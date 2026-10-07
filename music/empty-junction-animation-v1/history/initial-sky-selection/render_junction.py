"""The Empty Junction: source-masked cloud transport, optical mist and practical lights."""
from pathlib import Path
import sys,json,hashlib,argparse,subprocess
import cv2,numpy as np
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(R/'scripts'))
from ambient_effects import smoothstep,event_amount
from render_floodplain import encode,digest
sys.path.insert(0,str(R/'music/saltline-animation-v1'))
from periodic_transport import PeriodicDust
sys.path.insert(0,str(R/'music/farpoint-animation-v1'))
from render_farpoint import verify
cv2.setNumThreads(4)
def save(name,data):(H/name).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
def byte(a):return np.uint8(np.rint(np.clip(a,0,255)))

class Junction:
 def __init__(self):
  self.path=H/'scene-plan-v1.json';self.config=json.loads(self.path.read_text(encoding='utf-8'))
  c=self.config;p=R/c['source']['path'];assert digest(p)==c['source']['sha256']
  self.base=np.array(Image.open(p).convert('RGB'));self.h,self.w=self.base.shape[:2]
  assert [self.w,self.h]==c['source']['dimensions']
  self.shape=(self.h,self.w);self.y,self.x=np.mgrid[:self.h,:self.w].astype(np.float32)
  self.duration=c['duration'];self.masks={};self.prepare_sky();self.prepare_mist();self.prepare_lights()
  self.layer_masks={k:m>0 for k,m in self.masks.items()}
  self.layer_masks['pass_weather']=self.layer_masks['far_mist']|self.layer_masks['middle_mist']
  self.layer_masks['habitation']=np.logical_or.reduce([m for k,m in self.layer_masks.items() if k.startswith('light_')])
  self.active=np.logical_or.reduce(list(self.layer_masks.values()))

 def poly(self,polygons,feather=2,inset=0):
  scale=3;mask=np.zeros((self.h*scale,self.w*scale),np.uint8)
  for p in polygons:cv2.fillPoly(mask,[np.rint(np.float32(p)*scale).astype(np.int32)],255)
  distance=cv2.distanceTransform(mask,cv2.DIST_L2,5)/scale
  m=smoothstep((distance-inset)/feather)
  return cv2.resize(m,(self.w,self.h),interpolation=cv2.INTER_AREA).astype(np.float32)
 def crop(self,m,pad=0):
  ys,xs=np.where(m>0);a=max(0,int(xs.min())-pad);b=max(0,int(ys.min())-pad)
  z=min(self.w,int(xs.max())+pad+1);d=min(self.h,int(ys.max())+pad+1)
  return (a,b,z,d),m[b:d,a:z].copy()

 def prepare_sky(self):
  c=self.config['sky'];m=self.poly([c['polygon']]+c['holes'],c['feather'],c['inset'])
  m*=1-self.poly(c['blockers'],1);m[m<.002]=0
  self.masks['sky_clouds']=m
  (a,b,z,d),self.sky_mask=self.crop(m)
  self.sky_roi=(a,b,z,d);src=self.base[b:d,a:z].astype(np.float32)
  support=np.float32(self.sky_mask>.995)
  sx,sy=c['background_sigma']
  den=cv2.GaussianBlur(support,(0,0),sx,sigmaY=sy)
  num=cv2.GaussianBlur(src*support[...,None],(0,0),sx,sigmaY=sy)
  bg=num/np.maximum(den[...,None],1e-6)
  # The normalized blur only samples true sky; it never brings rock pixels into clouds.
  bg[den<.0001]=src[den<.0001]
  self.sky_background=bg;self.sky_removal=(bg-src)*self.sky_mask[...,None]
  delta=np.minimum(src-bg,0)*support[...,None]
  xx=self.x[b:d,a:z];yy=self.y[b:d,a:z]
  weights=[]
  for x,y,wx,wy in c['groups']:
   r=((xx-x)/wx)**2+((yy-y)/wy)**2
   w=np.exp(-r*1.5);w[r>6]=0;weights.append(w)
  total=np.maximum(sum(weights),.015)
  rng=np.random.default_rng(c['seed']);self.clouds=[]
  for (x,y,wx,wy),weight in zip(c['groups'],weights):
   sprite=delta*(weight/total)[...,None]*c['strength']
   active=np.max(abs(sprite),axis=2)>.02
   ys,xs=np.where(active)
   if len(xs)==0:continue
   xa,xb=int(xs.min()),int(xs.max()+1);ya,yb=int(ys.min()),int(ys.max()+1)
   sprite=sprite[ya:yb,xa:xb].copy()
   self.clouds.append((xa,ya,sprite,float(rng.uniform(0,60)),c['speed_upper'] if y<175 else c['speed_horizon']))

 def sky(self,f,t):
  c=self.config['sky'];a,b,z,d=self.sky_roi
  field=np.zeros_like(self.sky_background)
  for x,y,sprite,phase,speed in self.clouds:
   age=(t+phase+30)%60-30;fade=float(smoothstep((30-abs(age))/c['fade']))
   tx=x+speed*age;ix=int(np.floor(tx));hh,ww=sprite.shape[:2]
   shifted=cv2.warpAffine(sprite,np.float32([[1,0,tx-ix+1],[0,1,0]]),(ww+3,hh),flags=cv2.INTER_LINEAR)
   xa=max(0,ix-1);xb=min(z-a,ix+ww+2)
   if xb>xa:field[y:y+hh,xa:xb]+=shifted[:,xa-(ix-1):xb-(ix-1)]*fade
  f[b:d,a:z]+=self.sky_removal+field*self.sky_mask[...,None]

 def prepare_mist(self):
  self.mists=[]
  blocker=self.poly(self.config['weather_blockers'],1)
  for c in self.config['weather']:
   m=self.poly(c['polygons'],c['feather'])*(1-blocker);m[m<.002]=0
   (a,b,z,d),local=self.crop(m);x=self.x[b:d,a:z];y=self.y[b:d,a:z]
   transport={k:c[k] for k in ['seed','speed','color','optical_depth','max_opacity']}
   transport['lifetime']=60
   transport['gusts']=[{'x':gx,'y':gy,'width':gw,'height':gh,'route_slope':-.025 if c['name']=='middle_mist' else .015,'strength':1,'phase':ph} for (gx,gy,gw,gh),ph in zip(c['gusts'],c['phases'])]
   transport['loop_schedule']=[{'gust_index':i,'birth_x':g['x']-c['speed']*30,'age_at_zero':ph*60,'fade_in':8,'fade_out':8} for i,(g,ph) in enumerate(zip(transport['gusts'],c['phases']))]
   self.mists.append((c['name'],(a,b,z,d),local,PeriodicDust(x,y,transport,60)))
   self.masks[c['name']]=m

 def prepare_lights(self):
  self.lights=[];src=self.base.astype(np.float32)
  lum=src.mean(2);warm=smoothstep((src[:,:,0]-src[:,:,2]-8)/65)
  for c in self.config['lights']:
   core=self.poly(c['polygons'],c['feather'])
   # Geometry owns the aperture. Brightness gating protects dark dividers within it.
   core*=smoothstep((lum-48)/55)
   spill=np.zeros(self.shape,np.float32)
   for x,y,rx,ry,strength in c.get('glows',[]):
    r=((self.x-x)/rx)**2+((self.y-y)/ry)**2
    glow=np.exp(-r*.5)*strength;glow[r>9]=0
    spill=np.maximum(spill,glow*warm)
   m=np.maximum(core,spill);m[m<.002]=0
   self.masks['light_'+c['name']]=m
   self.lights.append((c,*self.crop(m)))
 def amount(self,t,events):
  return max([float(event_amount(t,60,e['start'],e['hold'],e['transition']))*e['depth'] for e in events] or [0])
 def frame_float(self,t,only=None):
  t=float(t)%60;f=self.base.astype(np.float32)
  if only in (None,'sky_clouds'):self.sky(f,t)
  for name,(a,b,z,d),mask,weather in self.mists:
   if only in (None,name,'pass_weather'):
    alpha,color=weather.density(t);alpha*=mask
    f[b:d,a:z]=f[b:d,a:z]*(1-alpha[...,None])+color*alpha[...,None]
  for c,(a,b,z,d),mask in self.lights:
   if only in (None,'habitation','light_'+c['name']):
    amount=self.amount(t,c['events'])
    f[b:d,a:z]*=1-mask[...,None]*amount
  assert np.isfinite(f).all()
  return f
 def frame(self,t,only=None,prototype=False):
  f=byte(self.frame_float(t,only))
  m=self.active if only is None else self.layer_masks[only]
  assert np.array_equal(f[~m],self.base[~m]),'Protected pixels changed'
  return f
 def fingerprint(self):
  paths=[self.config['source']['path'],'music/empty-junction-animation-v1/render_junction.py','scripts/ambient_effects.py','scripts/render_floodplain.py','scripts/water_surface.py','music/saltline-animation-v1/dust_transport.py','music/saltline-animation-v1/periodic_transport.py','music/farpoint-animation-v1/render_farpoint.py']
  return {'config_sha256':digest(self.path),'files':{p:digest(R/p) for p in paths},'masks':{k:hashlib.sha256(v.tobytes()).hexdigest() for k,v in self.masks.items()},'versions':{'numpy':np.__version__,'opencv':cv2.__version__},'duration':60}

def samples(s):
 (H/'masks').mkdir(exist_ok=True)
 for name,m in s.masks.items():cv2.imwrite(str(H/'masks'/f'{name}.png'),byte(m*255))
 overlay=s.base.astype(np.float32)
 for k,color in [('sky_clouds',[70,180,255]),('far_mist',[230,170,255]),('middle_mist',[80,255,170])]:
  m=s.masks[k][...,None]*.48;overlay=overlay*(1-m)+np.float32(color)*m
 Image.fromarray(byte(overlay)).save(H/'weather-mask-overlay.png')
 overlay=s.base.astype(np.float32)
 for name,m in s.masks.items():
  if name.startswith('light_'):
   a=m[...,None]*.7;overlay=overlay*(1-a)+np.float32([255,60,60])*a
 Image.fromarray(byte(overlay)).save(H/'light-mask-overlay.png')
 forced=s.base.astype(np.float32)
 for c,(a,b,z,d),m in s.lights:forced[b:d,a:z]*=1-m[...,None]*.88
 Image.fromarray(byte(forced)).save(H/'forced-dim-lights.png')
 for t in [0,4,8,20,30,40,50,57,59+29/30]:
  Image.fromarray(cv2.resize(s.frame(t),(1280,720),interpolation=cv2.INTER_AREA)).save(H/f'sample-{t:06.2f}s.png')
 for k in ['sky_clouds','pass_weather','habitation']:
  for t in [0,8,20,40]:
   Image.fromarray(cv2.resize(s.frame(t,k),(1280,720),interpolation=cv2.INTER_AREA)).save(H/f'{k}-{t:02d}s.png')
 checks={}
 for name,m in s.layer_masks.items():
  assert np.array_equal(s.frame(0,name),s.frame(60,name))
  times=[-1/30,0,3.1,8.2,14.1,20,23.3,30,40,47.5,50,58]
  vals=[float(abs(s.frame(t+1/30,name)[m].astype(float)-s.frame(t,name)[m]).mean()) for t in times]
  assert vals[0]<=max(vals[1:])*1.1+.01,(name,vals)
  eps=1/300;left=(s.frame_float(0,name)-s.frame_float(-eps,name))[m]/eps;right=(s.frame_float(eps,name)-s.frame_float(0,name))[m]/eps
  checks[name]={'periodic_state':True,'seam_mae':vals[0],'ordinary_sample_max':max(vals[1:]),'velocity_boundary_difference_mae':float(abs(left-right).mean()),'pass':True}
 assert len({hashlib.sha256(s.frame(t).tobytes()).hexdigest() for t in [0,20,40]})==3
 save('analytic-validation.json',{'fingerprint':s.fingerprint(),'layer_checks':checks,'distinct_0_20_40':True,'source_protection':'Exact outside active native masks, asserted every rendered frame','user_approved':False})
 print('Samples and analytical checks passed',flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['samples','isolated','preview'],required=True);args=p.parse_args();s=Junction()
 if args.stage=='samples':samples(s);return
 clips=[]
 if args.stage=='isolated':
  for layer in ['sky_clouds','pass_weather','habitation']:
   path=H/f'{layer}-v1-isolated-10s.mp4';item=encode(s,path,10,layer,True);item['validation'],_=verify(s,path,300,False);clips.append(item)
 else:
  path=H/'empty-junction-v1-preview-60s.mp4';item=encode(s,path,60);item['validation'],hashes=verify(s,path,1800,True);clips.append(item)
  repeat=H/'empty-junction-v1-three-loops-180s.mp4';assert not repeat.exists()
  subprocess.run([s.config['ffmpeg'],'-v','error','-n','-stream_loop','2','-i',str(path),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
  validation,repeated=verify(s,repeat,5400,True);assert repeated==hashes*3
  clips.append({'path':repeat.relative_to(R).as_posix(),'sha256':digest(repeat),'validation':validation,'exact_three_decoded_repetitions':True})
  save('decoded-frame-hashes.json',hashes)
  cap=cv2.VideoCapture(str(path))
  for n in [0,246,600,900,1200,1500,1710,1799]:
   cap.set(cv2.CAP_PROP_POS_FRAMES,n);ok,f=cap.read();assert ok;cv2.imwrite(str(H/f'decoded-{n:04d}.png'),f)
  cap.release()
 save(args.stage+'-validation.json',{'fingerprint':s.fingerprint(),'clips':clips,'silent':True,'user_approved':False,'inspection':'Source/native crops, masks and temporal/decoded stills; continuous playback unavailable'})
 print(args.stage,'complete decode and validation passed',flush=True)
if __name__=='__main__':main()

