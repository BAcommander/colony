"""Configurable Rainline compositor, including precise glass, room activity and alternating beacons."""
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
 def __init__(self,path=None):
  self.path=Path(path) if path else H/'scene-plan-v2.json';self.config=json.loads(self.path.read_text(encoding='utf-8'));c=self.config
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
  # Apply color protection only around actual vegetation, not every green reflection.
  foliage_zone=self.poly([[[970,700],[1120,680],[1255,728],[1320,830],[1290,910],[1135,858],[1010,780]]])
  water[(cv2.dilate(green,np.ones((3,3),np.uint8))>0)&(foliage_zone>0)]=0
  self.masks['water']=self.feather(water,c['water_feather'])
  x0,y0,x1,y1=c['water']['roi'];self.water=ChannelSurface(self.base[y0:y1,x0:x1],self.masks['water'][y0:y1,x0:x1],c['water'],(x0,y0))
  self.haze=[]
  for mc in c['mist']:
   binary=self.poly(mc['polygons']);binary[(win==0)|(ex>0)]=0
   m=self.feather(binary,mc['feather']);self.masks[mc['name']]=m
   yy,xx=np.where(m>0);roi=(int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1));ax,ay,bx,by=roi
   y,x=np.mgrid[ay:by,ax:bx].astype(np.float32)
   self.haze.append((mc['name'],roi,m[ay:by,ax:bx],PeriodicDust(x,y,mc,self.duration)))
  self.lights=[];light_union=np.zeros((self.h,self.w),np.float32)
  luminosity=self.base.astype(np.float32).mean(axis=2)
  for lc in c['lights']:
   ap=self.aperture(lc['polygons'])
   emission=ap*(.25+.75*np.clip((luminosity-30)/135,0,1))
   if lc.get('chromatic_gate'):
    warm=np.clip((r-b-3)/24,0,1);white=np.clip((luminosity-160)/45,0,1)
    emission*=np.maximum(warm,white).astype(np.float32)
   glow=cv2.GaussianBlur(ap,(0,0),1.5)*lc.get('glow_gain',.055);glow[glow<.003]=0
   spill=self.feather(self.poly([lc['spill']]),10)*lc.get('spill_gain',.055)
   reflection=self.feather(self.poly([lc['reflection']]),8)*self.masks['water']*lc.get('reflection_gain',.17)
   m=np.maximum.reduce([emission,glow,spill,reflection])*self.window_mask
   light_union=np.maximum(light_union,m);self.lights.append((lc,m))
  yy,xx=np.mgrid[:self.h,:self.w].astype(np.float32)
  pc=c['practical_flicker'];cx,cy=pc['center'];rx,ry=pc['radius'];sx,sy=pc['spill_radius']
  practical=np.exp(-((xx-cx)/rx)**4-((yy-cy)/ry)**4)+.10*np.exp(-((xx-cx)/sx)**2-((yy-cy)/sy)**2)
  practical=np.minimum(practical,1)*self.window_mask;practical[practical<.003]=0
  self.practical=practical;light_union=np.maximum(light_union,practical)
  self.masks['lights']=light_union
  self.beacons=[];beacon_union=np.zeros_like(light_union)
  for bc in c['beacons']:
   cx,cy=bc['center'];r2=(xx-cx)**2+(yy-cy)**2
   bm=np.minimum(np.exp(-r2/(2*bc['radius']**2))+.11*np.exp(-r2/(2*bc['halo']**2)),1)*self.window_mask
   bm[bm<.002]=0;self.beacons.append((bc,bm));beacon_union=np.maximum(beacon_union,bm)
  self.masks['beacons']=beacon_union
  self.masks['screen']=self.feather(self.poly([c['screen']['polygon']]),1.5)
  self.masks['radio']=self.feather(self.poly([c['radio_meter']['polygon']]),1)
  self.instruments={}
  for name,ic in c.get('instruments',{}).items():
   quad=np.array(ic['quad'],np.float32);iw,ih=ic['size']
   x0=max(0,int(quad[:,0].min())-2);x1=min(self.w,int(quad[:,0].max())+3)
   y0=max(0,int(quad[:,1].min())-2);y1=min(self.h,int(quad[:,1].max())+3)
   transform=cv2.getPerspectiveTransform(np.array([[0,0],[iw-1,0],[iw-1,ih-1],[0,ih-1]],np.float32),quad-np.array([x0,y0],np.float32))
   coverage=cv2.warpPerspective(np.ones((ih,iw),np.float32),transform,(x1-x0,y1-y0))
   self.masks[name][y0:y1,x0:x1]=np.maximum(self.masks[name][y0:y1,x0:x1],coverage)
   self.instruments[name]=(ic,(x0,y0,x1,y1),transform)
  rc=c.get('room')
  if rc:
   aperture=self.poly([rc['lamp_bounds']]).astype(np.float32)
   # Include saturated white core; bound the luminosity matte to the lamp mouth.
   core=aperture*np.clip((luminosity-145)/70,0,1)
   core=cv2.GaussianBlur(core,(0,0),.55)*aperture
   cx,cy=rc['desk_center'];rx,ry=rc['desk_radius']
   warm=np.clip((r-b-12)/90,0,1).astype(np.float32)
   desk=np.exp(-((xx-cx)/rx)**2-((yy-cy)/ry)**2)*warm*self.feather(self.poly([rc['desk_polygon']]),18)*rc.get('desk_gain',.45)
   self.room_lamp=np.maximum(core,desk);self.room_lamp[self.room_lamp<.002]=0
   self.masks['room']=self.room_lamp.copy()
   mx0,my0,mx1,my1=rc['meter_roi'];self.masks['room'][my0:my1,mx0:mx1]=1
   self.masks['room']=np.maximum.reduce([self.masks['room'],self.masks['screen'],self.masks['radio']])
  self.masks['rain']=np.maximum(self.masks['rain_near'],self.masks['rain_far'])
  self.layer_masks={k:v>0 for k,v in self.masks.items() if k not in ['rain_near','rain_far']}
  self.active=np.logical_or.reduce(list(self.layer_masks.values()))
  self.regions={}
  for name,m in self.masks.items():
   ys,xs=np.where(m>0)
   if len(xs):self.regions[name]=(int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1)
  rng=np.random.default_rng(c['rain']['seed']);self.rain=[]
  for group in c['rain']['groups']:
   n=group['count'];life=group['life']
   particles=np.stack([rng.uniform(100,self.w+80,n),rng.uniform(-100,self.h+100,n),rng.uniform(0,life,n),rng.uniform(*group['vx'],n),rng.uniform(*group['vy'],n),rng.uniform(*group['length'],n),rng.uniform(*group['opacity'],n)],axis=1)
   self.rain.append((group,particles))
  rng=np.random.default_rng(c['impacts']['seed']);ys,xs=np.where(self.masks['water']>.8);self.impacts=[]
  for i in range(c['impacts']['count']):
   j=rng.integers(len(xs));self.impacts.append((int(xs[j]),int(ys[j]),rng.uniform(0,c['impacts']['life'])))
 def aperture(self,shapes):
  # Supersampling preserves curved corners without carving a rectangular dim patch.
  out=np.zeros((self.h,self.w),np.float32)
  for points in shapes:
   p=np.asarray(points,np.float32);x0=max(0,int(p[:,0].min())-2);y0=max(0,int(p[:,1].min())-2)
   x1=min(self.w,int(p[:,0].max())+3);y1=min(self.h,int(p[:,1].max())+3)
   high=np.zeros(((y1-y0)*4,(x1-x0)*4),np.uint8)
   cv2.fillPoly(high,[np.rint((p-[x0,y0])*4).astype(np.int32)],255)
   soft=cv2.GaussianBlur(high.astype(np.float32)/255,(0,0),1.4)
   low=cv2.resize(soft,(x1-x0,y1-y0),interpolation=cv2.INTER_AREA);low[low<.01]=0
   out[y0:y1,x0:x1]=np.maximum(out[y0:y1,x0:x1],low)
  return out
 def poly(self,shapes):
  m=np.zeros((self.h,self.w),np.uint8)
  for p in shapes:cv2.fillPoly(m,[np.array(p,np.int32)],1)
  return m
 def feather(self,m,n):return smoothstep(cv2.distanceTransform(m,cv2.DIST_L2,5)/n).astype(np.float32)
 def rain_alpha(self,t):
  result=np.zeros((self.h,self.w),np.float32)
  for group,particles in self.rain:
   layer=np.zeros((self.h,self.w),np.uint8);life=group['life']
   x,y,phase,vx,vy,length,strength=particles.T
   age=(t+phase)%life;fade=smoothstep(age/.18)*smoothstep((life-age)/.18)
   px=x+vx*(age-life/2);py=y+vy*(age-life/2);dx=vx/vy*length
   inside=(px>-35)&(px<self.w+35)&(py>-35)&(py<self.h+35)&(fade>.001)
   for ax,ay,bx,ln,val in zip(px[inside],py[inside],dx[inside],length[inside],strength[inside]*fade[inside]):
    # Three overlapping trail sections give a soft tail rather than uniform white sticks.
    for low,high,weight in [(0,1,.4),(.25,.9,.72),(.5,.82,1)]:
     cv2.line(layer,(round((ax+bx*low)*256),round((ay+ln*low)*256)),(round((ax+bx*high)*256),round((ay+ln*high)*256)),round(255*val*weight),1,cv2.LINE_AA,8)
   alpha=cv2.GaussianBlur(layer.astype(np.float32)/255,(0,0),.38)*self.masks[group['mask']]
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
 def draw_instrument(self,f,t,name):
  ic,(x0,y0,x1,y1),transform=self.instruments[name];w,h=ic['size']
  rgb=np.zeros((h,w,3),np.float32);alpha=np.zeros((h,w),np.float32)
  if name=='screen':
   rgb[:]=[22,31,36]
   for x in range(8,w,12):rgb[:,x]=[32,48,56]
   for y in range(8,h,10):rgb[y,:]=[32,48,56]
   phase=2*np.pi*t/10;x=np.arange(w,dtype=np.float32)
   curve=h*.53+7*np.sin(x*.105-phase)+3*np.sin(x*.29+2*phase)
   line=np.zeros((h,w),np.uint8)
   points=np.stack([x,curve],axis=1)*256
   cv2.polylines(line,[np.rint(points).astype(np.int32)],False,255,2,cv2.LINE_AA,8)
   glow=cv2.GaussianBlur(line.astype(np.float32)/255,(0,0),1.8)
   rgb+=glow[...,None]*np.array([18,47,60],np.float32)
   ink=line.astype(np.float32)/255
   rgb=rgb*(1-ink[...,None])+np.array([109,209,228],np.float32)*ink[...,None]
   sweep=(t%10)/10;center=sweep*(w-1)
   rgb+=np.exp(-((x-center)/3)**2)[None,:,None]*np.sin(np.pi*sweep)**2*np.array([6,20,24],np.float32)
   yy,xx=np.mgrid[:h,:w];edge=np.minimum.reduce([xx+1,w-xx,yy+1,h-yy]).astype(np.float32)
   alpha=.90*np.clip(edge/3,0,1)
  else:
   rgb[:]=[51,27,9]
   for row,y in enumerate([11,23]):
    level=.48+.26*np.sin(2*np.pi*t*(3+row)/20+.8*row)+.16*np.sin(2*np.pi*t*(7+row*2)/20+.7)
    for j in range(15):
     strength=np.clip(level*15-j,0,1)
     alpha[y:y+5,6+j*5:10+j*5]=.12+.78*strength
   # Small existing-display activity marker; no text or external UI.
   pulse=.5-.5*np.cos(2*np.pi*t/5)
   rgb[3:7,80:84]=[255,230,151];alpha[3:7,80:84]=.75*pulse
  shape=(x1-x0,y1-y0)
  wa=cv2.warpPerspective(alpha,transform,shape)
  premult=cv2.warpPerspective(rgb*alpha[...,None],transform,shape)
  f[y0:y1,x0:x1]=f[y0:y1,x0:x1]*(1-wa[...,None])+premult
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
    held=event_amount(t,self.duration,lc['start'],lc['hold'],lc['transition'])*(1-lc['floor'])
    flicker=max((event_amount(t,self.duration,e['start'],e['hold'],e['transition'])*e['depth'] for e in lc['flickers']),default=0)
    amount=1-(1-held)*(1-flicker)
    f*=1-m[...,None]*amount
   amount=max(event_amount(t,self.duration,e['start'],e['hold'],e['transition'])*e['depth'] for e in self.config['practical_flicker']['events'])
   f*=1-self.practical[...,None]*amount
  if only in (None,'beacons'):
   for bc,bm in self.beacons:
    age=(t-bc['phase'])%self.duration;phase=age%bc['period']
    pulse=float(smoothstep(phase/.16)*smoothstep((.85-phase)/.25))
    if pulse>0:
     color=bc.get('alternate_color',bc['color']) if int(age//bc['period'])%2 else bc['color']
     cx,cy=bc['center'];radius=int(bc['halo']*4)+2;x0=max(0,cx-radius);x1=min(self.w,cx+radius+1);y0=max(0,cy-radius);y1=min(self.h,cy+radius+1)
     alpha=bm[y0:y1,x0:x1,None]*(.90*pulse)
     f[y0:y1,x0:x1]=f[y0:y1,x0:x1]*(1-alpha)+np.array(color,np.float32)*alpha
  if only in (None,'room') and 'room' in self.config:
   rc=self.config['room'];slow=rc.get('slow_depth',.025)*(.5-.5*np.cos(2*np.pi*t/20))
   brief=max(event_amount(t,self.duration,e['start'],e['hold'],e['transition'])*e['depth'] for e in rc['lamp_events'])
   x0,y0,x1,y1=self.regions['room'];f[y0:y1,x0:x1]*=1-self.room_lamp[y0:y1,x0:x1,None]*(slow+brief)
   x0,y0,x1,y1=rc['meter_roi'];x=np.arange(x1-x0,dtype=np.float32)
   level=.48+.16*np.sin(2*np.pi*t*3/20)+.12*np.sin(2*np.pi*t*7/20+.7)+.06*np.sin(2*np.pi*t*13/20)
   bar=np.clip((level*(x1-x0)-x)/1.5,0,1)*(.65+.35*np.cos(x*np.pi/2)**2)
   stripe=np.array([.22,.8,.8,.22],np.float32)[:,None]*bar[None,:]
   if not rc.get('instruments_v2'):f[y0:y1,x0:x1]+=stripe[...,None]*np.array([19,13,3],np.float32)
  if only in (None,'screen','room'):
   c=self.config['screen'];x0,y0,x1,y1=c['roi'];y,x=np.mgrid[y0:y1,x0:x1]
   phase=(t%c['period'])/c['period'];center=x0+5+phase*(x1-x0-10)
   trace=y0+33+3*np.sin((x-x0)*.29+2*np.pi*phase)+1.3*np.sin((x-x0)*.69-4*np.pi*phase)
   line=np.exp(-((y-trace)/.8)**2)*np.exp(-((x-center)/13)**2)*np.sin(np.pi*phase)**2
   scan=np.exp(-((x-center)/1.2)**2)*.12*np.sin(np.pi*phase)**2
   alpha=(line+scan)*self.masks['screen'][y0:y1,x0:x1]
   if 'screen' in self.instruments:self.draw_instrument(f,t,'screen')
   else:f[y0:y1,x0:x1]+=alpha[...,None]*np.array([.2,.75,1])*c['strength']
  if only in (None,'radio','room'):
   c=self.config['radio_meter'];amount=c['strength']*(.5-.5*np.cos(2*np.pi*t/c['period']))
   f*=1-self.masks['radio'][...,None]*amount
   if 'radio' in self.instruments:self.draw_instrument(f,t,'radio')
  if only in (None,'rain'):
   alpha=self.rain_alpha(t);f=f*(1-alpha[...,None])+np.array(self.config['rain']['color'],np.float32)*alpha[...,None]
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
 for k,color in [('water',[30,160,255]),('mist_far',[200,50,200]),('mist_near',[60,230,130]),('lights',[255,70,30]),('screen',[255,255,0]),('beacons',[255,0,0]),('room',[255,190,0])]:
  alpha=s.masks[k][...,None]*.4;overlay=overlay*(1-alpha)+np.array(color)*alpha
 Image.fromarray(np.uint8(overlay)).save(H/'mask-review.png')
 for t in [0,4,8,12,16,19+29/30]:Image.fromarray(s.frame(t)).save(H/f'sample-{t:.3f}s.png')
 for k in ['water','lights','room','beacons']:Image.fromarray(s.frame(8,k)).save(H/f'{k}-sample-8s.png')
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
 global H
 p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--stage',choices=['samples','isolated','preview'],required=True);a=p.parse_args()
 if a.config:H=Path(a.config).resolve().parent
 s=Rainline(a.config)
 if a.stage=='samples':samples(s);return
 clips=[]
 if a.stage=='isolated':
  for layer in ['water','lights','room','beacons']:
   out=H/f"{layer}-isolated-{s.config['version']}-8s.mp4";item=encode(s,out,8,layer);item['validation'],_=verify(s,out,240,False);clips.append(item)
   print(layer+' isolated checks passed',flush=True)
 else:
  out=H/f"rainline-relay-{s.config['version']}-preview-20s.mp4";item=encode(s,out,20);item['validation'],hashes=verify(s,out,600,True);clips.append(item)
  assert hashes[0]!=hashes[-1]
  repeat=H/f"rainline-relay-{s.config['version']}-three-loops-60s.mp4";assert not repeat.exists()
  subprocess.run([s.config['ffmpeg'],'-v','error','-n','-stream_loop','2','-i',str(out),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
  validation,repeated=verify(s,repeat,1800,True);assert repeated==hashes*3
  clips.append({'path':repeat.relative_to(R).as_posix(),'sha256':digest(repeat),'validation':validation,'three_repeated_decoded_payloads_identical':True})
  cap=cv2.VideoCapture(str(out));cap.set(cv2.CAP_PROP_POS_MSEC,8000);ok,f=cap.read();cap.release();assert ok;cv2.imwrite(str(H/'decoded-preview-8s.png'),f)
 (H/(a.stage+'-validation.json')).write_text(json.dumps({'fingerprint':s.fingerprint(),'clips':clips,'silent':True,'user_motion_approved':False,'inspection':'Source/mask and temporal stills; no continuous playback claim'},indent=2)+'\n')
 print(a.stage+' checks passed',flush=True)
if __name__=='__main__':main()
