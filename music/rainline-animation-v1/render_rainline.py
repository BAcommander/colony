"""Rainline first draft: fixed source, water, layered rain/mist and practical lights."""
from pathlib import Path
import sys,json,hashlib,subprocess,argparse,time
import cv2,numpy as np
from PIL import Image,ImageDraw
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(R/'scripts'));sys.path.insert(0,str(H.parent/'saltline-animation-v1'))
from render_floodplain import ChannelSurface,encode,digest
from ambient_effects import smoothstep,event_amount
from periodic_transport import PeriodicDust
cv2.setNumThreads(4)

class Rainline:
 def __init__(self):
  self.path=H/'scene-plan-v1.json';self.config=json.loads(self.path.read_text(encoding='utf-8'));c=self.config
  assert digest(R/c['source']['path'])==c['source']['sha256']
  self.base=np.array(Image.open(R/c['source']['path']).convert('RGB'));self.h,self.w=self.base.shape[:2];self.duration=c['duration']
  assert [self.w,self.h]==c['source']['dimensions']
  win=self.poly(c['windows']);ex=self.poly(c['protected_exterior'])
  win[self.poly(c.get('interior_occluders',[]))>0]=0
  self.window_mask=self.feather(win,2);far=win.copy();far[ex>0]=0
  self.masks={'rain_near':self.window_mask,'rain_far':self.feather(far,2)}
  water=self.poly(c['water_polygons']);water[(win==0)|(ex>0)|(self.poly(c['water_exclusions'])>0)]=0
  # Freeze green vegetation protruding into the flooded plane; retain amber reflections.
  r,g,b=self.base.astype(float).transpose(2,0,1)
  green=((g>r*1.08)&(g>b*1.035)).astype(np.uint8)
  water[cv2.dilate(green,np.ones((3,3),np.uint8))>0]=0
  self.masks['water']=self.feather(water,7)
  x0,y0,x1,y1=c['water']['roi'];self.water=ChannelSurface(self.base[y0:y1,x0:x1],self.masks['water'][y0:y1,x0:x1],c['water'],(x0,y0))
  self.haze=[]
  for mc in c['mist']:
   binary=self.poly(mc['polygons']);binary[(win==0)|(ex>0)]=0
   m=self.feather(binary,mc['feather']);self.masks[mc['name']]=m
   yy,xx=np.where(m>0);roi=(int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1));ax,ay,bx,by=roi
   y,x=np.mgrid[ay:by,ax:bx].astype(np.float32)
   self.haze.append((mc['name'],roi,m[ay:by,ax:bx],PeriodicDust(x,y,mc,self.duration)))
  self.lights=[];light_union=np.zeros((self.h,self.w),np.float32)
  for lc in c['lights']:
   ap=self.poly([lc['polygon']]).astype(np.float32)
   glow=cv2.GaussianBlur(ap,(0,0),2)*.15;glow[glow<.002]=0
   spill=self.feather(self.poly([lc['spill']]),8)*.10
   reflection=self.feather(self.poly([lc['reflection']]),8)*self.masks['water']*.20
   m=np.maximum.reduce([ap,glow,spill,reflection])*self.window_mask
   light_union=np.maximum(light_union,m);self.lights.append((lc,m))
  self.masks['lights']=light_union
  self.masks['screen']=self.feather(self.poly([c['screen']['polygon']]),1.5)
  self.masks['radio']=self.feather(self.poly([c['radio_meter']['polygon']]),1)
  self.masks['rain']=np.maximum(self.masks['rain_near'],self.masks['rain_far'])
  self.layer_masks={k:v>0 for k,v in self.masks.items() if k not in ['rain_near','rain_far']}
  self.active=np.logical_or.reduce(list(self.layer_masks.values()))
  rng=np.random.default_rng(c['rain']['seed']);self.rain=[]
  for group in c['rain']['groups']:
   particles=[]
   for i in range(group['count']):
    life=group['life'];vx=rng.uniform(*group['vx']);vy=rng.uniform(*group['vy'])
    particles.append((rng.uniform(100,self.w+80),rng.uniform(-100,self.h+100),rng.uniform(0,life),vx,vy,rng.uniform(*group['length']),rng.uniform(*group['opacity'])))
   self.rain.append((group,particles))
  rng=np.random.default_rng(c['impacts']['seed']);ys,xs=np.where(self.masks['water']>.8);self.impacts=[]
  for i in range(c['impacts']['count']):
   j=rng.integers(len(xs));self.impacts.append((int(xs[j]),int(ys[j]),rng.uniform(0,c['impacts']['life'])))
 def poly(self,shapes):
  m=np.zeros((self.h,self.w),np.uint8)
  for p in shapes:cv2.fillPoly(m,[np.array(p,np.int32)],1)
  return m
 def feather(self,m,n):return smoothstep(cv2.distanceTransform(m,cv2.DIST_L2,5)/n).astype(np.float32)
 def rain_alpha(self,t):
  result=np.zeros((self.h,self.w),np.float32)
  for group,particles in self.rain:
   layer=np.zeros((self.h,self.w),np.uint8);life=group['life']
   for x,y,phase,vx,vy,length,strength in particles:
    age=(t+phase)%life;fade=float(smoothstep(age/.3)*smoothstep((life-age)/.3))
    if fade==0:continue
    px=x+vx*(age-life/2);py=y+vy*(age-life/2)
    if px<-20 or px>self.w+20 or py<-20 or py>self.h+20:continue
    dx=vx/vy*length
    cv2.line(layer,(round(px*256),round(py*256)),(round((px+dx)*256),round((py+length)*256)),round(255*strength*fade),1,cv2.LINE_AA,8)
   alpha=cv2.GaussianBlur(layer.astype(np.float32)/255,(0,0),.45)*self.masks[group['mask']]
   result=1-(1-result)*(1-alpha)
  return result
 def impacts_layer(self,t):
  out=np.zeros((self.h,self.w),np.float32);life=self.config['impacts']['life']
  for x,y,phase in self.impacts:
   age=(t+phase)%life;strength=np.sin(np.pi*age/life)**2
   rx=1+age/life*(5+(y-460)*.023);ry=rx*.26
   x0=max(0,int(x-rx-3));x1=min(self.w,int(x+rx+4));y0=max(0,int(y-ry-2));y1=min(self.h,int(y+ry+3))
   yy,xx=np.mgrid[y0:y1,x0:x1]
   distance=np.sqrt(((xx-x)/rx)**2+((yy-y)/ry)**2)
   out[y0:y1,x0:x1]+=np.exp(-((distance-1)*rx/1.1)**2)*strength
  return out*self.masks['water']*self.config['impacts']['strength']
 def frame(self,t,only=None,prototype=False):
  t=float(t)%self.duration;f=self.base.astype(np.float32)
  if only in (None,'water'):
   x0,y0,x1,y1=self.config['water']['roi'];f[y0:y1,x0:x1]=self.water.frame(t)
   f+=self.impacts_layer(t)[...,None]*np.array([.65,.8,.9],np.float32)
  for name,(x0,y0,x1,y1),mask,field in self.haze:
   if only not in (None,name):continue
   alpha,color=field.density(t);alpha*=mask
   f[y0:y1,x0:x1]=f[y0:y1,x0:x1]*(1-alpha[...,None])+color*alpha[...,None]
  if only in (None,'lights'):
   for lc,m in self.lights:
    amount=event_amount(t,self.duration,lc['start'],lc['hold'],lc['transition'])*(1-lc['floor'])
    f*=1-m[...,None]*amount
  if only in (None,'screen'):
   c=self.config['screen'];x0,y0,x1,y1=c['roi'];y,x=np.mgrid[y0:y1,x0:x1]
   phase=(t%c['period'])/c['period'];center=x0+5+phase*(x1-x0-10)
   trace=y0+33+3*np.sin((x-x0)*.29+2*np.pi*phase)+1.3*np.sin((x-x0)*.69-4*np.pi*phase)
   line=np.exp(-((y-trace)/.8)**2)*np.exp(-((x-center)/13)**2)*np.sin(np.pi*phase)**2
   scan=np.exp(-((x-center)/1.2)**2)*.12*np.sin(np.pi*phase)**2
   alpha=(line+scan)*self.masks['screen'][y0:y1,x0:x1]
   f[y0:y1,x0:x1]+=alpha[...,None]*np.array([.2,.75,1])*c['strength']
  if only in (None,'radio'):
   c=self.config['radio_meter'];amount=c['strength']*(.5-.5*np.cos(2*np.pi*t/c['period']))
   f*=1-self.masks['radio'][...,None]*amount
  if only in (None,'rain'):
   alpha=self.rain_alpha(t);f=f*(1-alpha[...,None])+np.array(self.config['rain']['color'])*alpha[...,None]
  assert np.isfinite(f).all();f=np.uint8(np.rint(np.clip(f,0,255)))
  m=self.active if only is None else self.layer_masks[only]
  assert np.array_equal(f[~m],self.base[~m]),'Protected pixels changed'
  return f
 def fingerprint(self):
  deps=['scripts/render_floodplain.py','scripts/water_surface.py','scripts/ambient_effects.py','music/saltline-animation-v1/periodic_transport.py','music/saltline-animation-v1/dust_transport.py']
  return {'source_sha256':self.config['source']['sha256'],'config_sha256':digest(self.path),'renderer_sha256':digest(__file__),'dependencies':{p:digest(R/p) for p in deps},'masks':{k:hashlib.sha256(v.tobytes()).hexdigest() for k,v in self.masks.items()}}

def verify(s,path,count,loop):
 cap=cv2.VideoCapture(str(path));assert cap.get(cv2.CAP_PROP_FPS)==30
 masks={k:cv2.resize(m.astype(np.uint8),(1280,720),interpolation=cv2.INTER_NEAREST) for k,m in {**s.layer_masks,'combined':s.active}.items()}
 first=prev=None;maximum={k:0. for k in masks};hashes=[];i=0
 while True:
  ok,f=cap.read()
  if not ok:break
  assert f.shape==(720,1280,3) and abs(cap.get(cv2.CAP_PROP_POS_MSEC)/1000-i/30)<.0001
  hashes.append(hashlib.sha256(f.tobytes()).hexdigest())
  if first is None:first=f.copy()
  else:
   diff=cv2.absdiff(f,prev)
   for k,m in masks.items():maximum[k]=max(maximum[k],sum(cv2.mean(diff,mask=m)[:3])/3)
  prev=f;i+=1
 cap.release();assert i==count
 checks={}
 if loop:
  diff=cv2.absdiff(prev,first)
  for k,m in masks.items():
   value=sum(cv2.mean(diff,mask=m)[:3])/3;assert value<=maximum[k]*1.1+.01,(k,value,maximum[k])
   checks[k]={'seam_mae':value,'ordinary_max_mae':maximum[k],'pass':True}
 return {'frames':i,'fps':30,'full_decode':True,'sequential_timestamps':True,'encoded_seam':checks},hashes

def samples(s):
 (H/'masks').mkdir(exist_ok=True)
 for k,m in s.masks.items():cv2.imwrite(str(H/'masks'/f'{k}.png'),np.uint8(np.rint(m*255)))
 overlay=s.base.astype(float)
 for k,color in [('water',[30,160,255]),('mist_far',[200,50,200]),('mist_near',[60,230,130]),('lights',[255,70,30]),('screen',[255,255,0])]:
  alpha=s.masks[k][...,None]*.4;overlay=overlay*(1-alpha)+np.array(color)*alpha
 Image.fromarray(np.uint8(overlay)).save(H/'mask-review.png')
 for t in [0,4,8,12,16,19+29/30]:Image.fromarray(s.frame(t)).save(H/f'sample-{t:.3f}s.png')
 for k in ['water','rain','mist_far','mist_near']:Image.fromarray(s.frame(8,k)).save(H/f'{k}-sample-8s.png')
 # Endpoint equality and local seam checks; video checks cover every ordinary step.
 checks={}
 for k,m in s.layer_masks.items():
  assert np.array_equal(s.frame(0,k),s.frame(20,k))
  values=[]
  for t in [-1/30,0,3,8,12,16]:
   values.append(float(np.abs(s.frame(t+1/30,k)[m].astype(float)-s.frame(t,k)[m]).mean()))
  assert values[0]<=max(values[1:])*1.1+.01,(k,values)
  checks[k]={'endpoint_exact':True,'seam_mae':values[0],'ordinary_max_sampled':max(values[1:]),'pass':True}
 assert not np.array_equal(s.frame(0),s.frame(10))
 (H/'analytic-validation.json').write_text(json.dumps({'fingerprint':s.fingerprint(),'layers':checks,'source_protection':'Asserted on every generated source frame','user_motion_approved':False},indent=2)+'\n')
 print('Masks, samples and analytic checks passed',flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['samples','isolated','preview'],required=True);a=p.parse_args();s=Rainline()
 if a.stage=='samples':samples(s);return
 clips=[]
 if a.stage=='isolated':
  for layer in ['rain','water','mist_far','mist_near']:
   out=H/f'{layer}-isolated-v1-8s.mp4';item=encode(s,out,8,layer);item['validation'],_=verify(s,out,240,False);clips.append(item)
   print(layer+' isolated checks passed',flush=True)
 else:
  out=H/'rainline-relay-v1-preview-20s.mp4';item=encode(s,out,20);item['validation'],hashes=verify(s,out,600,True);clips.append(item)
  assert hashes[0]!=hashes[-1]
  repeat=H/'rainline-relay-v1-three-loops-60s.mp4';assert not repeat.exists()
  subprocess.run([s.config['ffmpeg'],'-v','error','-n','-stream_loop','2','-i',str(out),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
  validation,repeated=verify(s,repeat,1800,True);assert repeated==hashes*3
  clips.append({'path':repeat.relative_to(R).as_posix(),'sha256':digest(repeat),'validation':validation,'three_repeated_decoded_payloads_identical':True})
  cap=cv2.VideoCapture(str(out));cap.set(cv2.CAP_PROP_POS_MSEC,8000);ok,f=cap.read();cap.release();assert ok;cv2.imwrite(str(H/'decoded-preview-8s.png'),f)
 (H/(a.stage+'-validation.json')).write_text(json.dumps({'fingerprint':s.fingerprint(),'clips':clips,'silent':True,'user_motion_approved':False,'inspection':'Source/mask and temporal stills; no continuous playback claim'},indent=2)+'\n')
 print(a.stage+' checks passed',flush=True)
if __name__=='__main__':main()
