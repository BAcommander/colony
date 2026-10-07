"""Farpoint minute completion adapter. Historical v1/v2/v3 remain immutable."""
from pathlib import Path
import sys,json,hashlib,argparse,subprocess
import cv2,numpy as np
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(H.parent/'farpoint-animation-v3'))
from render_farpoint_v3 import FarpointV3,Farpoint,byte_image,encode,digest,smoothstep,verify

def save(name,data): (H/name).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')

class FarpointMinute(FarpointV3):
 def __init__(self):
  super().__init__()
  self.path=H/'scene-plan-v4.json';self.config=json.loads(self.path.read_text());self.duration=self.config['duration']
  assert digest(H.parent/'farpoint-animation-v3/render_farpoint_v3.py')==self.config['parent_v3_renderer_sha256']
  self.prepare_habitation();self.prepare_additions()
  c=self.config['cloud_lifetimes']
  weights=np.stack([np.exp(-.5*((self.px-x)/c['width'])**2) for x in c['centers_x']]);weights/=weights.sum(0)
  self.cloud_parts=[(self.optical_cloud*w[...,None]).astype(np.float32) for w in weights]
  self.pm=self.safe.copy();self.pm[self.pm<.002]=0
  a,b,z,d=self.planet_roi
  self.masks['clouds'][b:d,a:z]=self.pm;self.masks['cloud_shadows']=self.masks['clouds'].copy()
  # The supporting veil retains the historical 20-second field at its speed.
  # Its method is not used for the principal clouds.
  self.masks['veil'][b:d,a:z]=self.pm
  self.prepare_aurora();self.prepare_stars_reflections()
  self.masks['lightning']=self.masks['clouds'].copy()
  self.layer_masks={k:v>0 for k,v in self.masks.items()}
  for name,keys in {'planet_activity':['clouds','veil','lower_cloud','cloud_shadows','aurora','lightning'],'aurora_storms':['aurora','lightning'],'stars_reflections':['stars','reflections','lamp'],'habitation':['windows','screen','lamp','instrument_lights','reflections']}.items():
   self.layer_masks[name]=np.logical_or.reduce([self.layer_masks[k] for k in keys])
  self.active=np.logical_or.reduce(list(self.layer_masks.values()))

 def prepare_aurora(self):
  c=self.config['aurora'];a,b,z,d=c['roi'];xx=self.x[b:d,a:z];yy=self.y[b:d,a:z];cx,cy=self.config['planet']['center']
  self.ar=np.hypot(xx-cx,yy-cy);self.aa=np.arctan2(yy-cy,xx-cx);self.inward=self.config['planet']['radius']-self.ar
  lo,hi=c['angle_range'];self.arc=(self.aa-lo)/(hi-lo)
  m=smoothstep(self.arc/.1)*smoothstep((1-self.arc)/.14)*smoothstep((self.inward-8)/8)*smoothstep((c['inner_limit']-self.inward)/15)
  m*=smoothstep((yy-b)/10)*smoothstep((d-1-yy)/12)*smoothstep((xx-a)/10)*smoothstep((z-1-xx)/10)
  m[m<.002]=0;self.aurora_mask=m
  rng=np.random.default_rng(410)
  self.aurora_threads=[(float(pos),float(rng.uniform(.0025,.007)),float(rng.uniform(15,39)),float(rng.uniform(.3,1)),float(rng.uniform(0,6.28))) for pos in np.sort(rng.uniform(0,1.4,26))]
  mask=np.zeros(self.shape,np.float32);mask[b:d,a:z]=m;self.masks['aurora']=mask

 def prepare_stars_reflections(self):
  c=self.config['stars'];self.star_parts=[];union=np.zeros(self.shape,np.float32)
  for (x,y),cycles,phase in zip(c['centers'],c['cycles'],c['phases']):
   box=(x-3,y-3,x+4,y+4);a,b,z,d=box;patch=self.base[b:d,a:z].astype(np.float32)
   lum=patch.mean(2);background=float(np.percentile(lum,25));m=smoothstep((lum-background-3)/25)
   assert m.max()>.1,(x,y)
   union[b:d,a:z]=np.maximum(union[b:d,a:z],m)
   self.star_parts.append((box,m,cycles,phase))
  self.masks['stars']=union
  core=self.poly(self.config['reflections']['polygons'],.65)
  halo=np.zeros(self.shape,np.float32);rgb=self.base.astype(np.float32)
  # Include white-hot pixels, but never dim the dark glass as a polygonal tile.
  core*=smoothstep((rgb.max(2)-65)/90)
  warm=smoothstep((rgb[...,0]-rgb[...,2]-4)/40)
  for x,y,rx,ry in [(433,497,19,10),(434,550,15,7),(434,560,16,7)]:
   p=np.exp(-((self.x-x)/rx)**2-((self.y-y)/ry)**2)*warm*.45
   p[(abs(self.x-x)>rx*1.4)|(abs(self.y-y)>ry*1.4)]=0;halo=np.maximum(halo,p)
  m=np.maximum(core,halo);m[m<.003]=0;self.masks['reflections']=m;self.reflections=self.crop(m)

 def forward_cloud(self,t):
  c=self.config['cloud_lifetimes'];life=c['seconds'];cx,cy=self.config['planet']['center'];a,b,_,_=self.planet_roi
  out=np.zeros_like(self.optical_cloud)
  for texture,phase in zip(self.cloud_parts,c['phase_seconds']):
   age=(t+phase+life/2)%life-life/2
   opacity=float(smoothstep((life/2-abs(age))/c['fade_seconds']))
   if opacity==0:continue
   theta=self.angle-self.omega*age
   mx=(cx+self.rad*np.cos(theta)-a).astype(np.float32);my=(cy+self.rad*np.sin(theta)-b).astype(np.float32)
   p=cv2.remap(texture,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)*opacity
   # Premultiplied over, never additive cloud glare.
   out[...,:3]=p[...,:3]+out[...,:3]*(1-p[...,3,None]);out[...,3]=p[...,3]+out[...,3]*(1-p[...,3])
  return out

 def lower_cloud(self,t):
  c=self.config['lower_lifetimes'];a,b,z,d=self.lower_roi;cx,cy=self.config['planet']['center']
  xx=self.x[b:d,a:z];partition=smoothstep((xx-1360)/45);out=np.zeros_like(self.lower_optical)
  for w,phase in zip([1-partition,partition],c['phase_seconds']):
   life=c['seconds'];age=(t+phase+life/2)%life-life/2;fade=float(smoothstep((life/2-abs(age))/c['fade_seconds']))
   theta=self.lower_angle-self.config['new_atmosphere']['lower_cloud']['speed_pixels_per_second']*age/self.lower_rad
   mx=(cx+self.lower_rad*np.cos(theta)-a).astype(np.float32);my=(cy+self.lower_rad*np.sin(theta)-b).astype(np.float32)
   p=cv2.remap(self.lower_optical*w[...,None],mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)*fade
   out[...,:3]=p[...,:3]+out[...,:3]*(1-p[...,3,None]);out[...,3]=p[...,3]+out[...,3]*(1-p[...,3])
  return (out[...,:3]-out[...,3,None]*self.lower_clean-self.lower_original)*self.lower_mask[...,None]*self.config['new_atmosphere']['lower_cloud']['gain']

 def veil_at(self,t):
  cx,cy=self.config['planet']['center'];a,b,_,_=self.planet_roi;out=np.zeros_like(self.veil)
  for phase in [0.,.5]:
   age=(t/20+self.offset+.23+phase)%1;theta=self.angle-.8/self.rad*20*(age-.5)
   mx=(cx+self.rad*np.cos(theta)-a).astype(np.float32);my=(cy+self.rad*np.sin(theta)-b).astype(np.float32)
   out+=cv2.remap(self.veil,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)*(np.sin(np.pi*age)**2)[...,None]
  return (out-self.veil)*self.pm[...,None]*self.config['planet']['veil']['gain']

 def aurora(self,t):
  q=2*np.pi*t/self.duration;u=self.arc;v=self.inward
  base=25+8*np.sin(u*19-q)+4*np.sin(u*43+2*q)
  folds=(.5+.5*np.sin(u*24-q+1.1*np.sin(u*14+q)))**2
  curtain=np.exp(-((v-base)/15)**2)*folds
  filaments=np.zeros_like(u)
  for pos,width,height,strength,phase in self.aurora_threads:
   at=(pos+1.4*t/self.duration)%1.4
   bent=u+.004*np.sin(v/15+u*10-q+phase)+.002*np.sin(v/8+2*q+phase)
   distance=(bent-at+.7)%1.4-.7
   radial=np.exp(-((v-base-3)/(height*.62))**2)
   filaments+=np.exp(-(distance/width)**2)*radial*strength*(.72+.28*np.sin(q+phase))
  filaments=cv2.GaussianBlur(np.minimum(filaments,1.2),(0,0),.8)
  glow=np.exp(-((v-base-2)/23)**2)*folds*.15
  c=self.config['aurora']
  return ((curtain*.4+filaments*.72)[...,None]*np.float32(c['color'])+(filaments*.32)[...,None]*np.float32(c['filament_color'])+glow[...,None]*np.float32(c['color']))*self.aurora_mask[...,None]

 def storm(self,t,alpha):
  out=np.zeros((*alpha.shape,3),np.float32)
  for e in self.config['lightning']:
   dt=(t-e['time']+30)%60-30
   pulse=np.exp(-(dt/.16)**2)+.63*np.exp(-((dt-.38)/.22)**2)
   if pulse<.00001:continue
   cx,cy=e['center'];rx,ry=e['radius'];g=np.exp(-((self.px-cx)/rx)**2-((self.py-cy)/ry)**2)
   # Illuminate only the present optical cloud, including a soft internal halo.
   cloud=cv2.GaussianBlur(alpha,(0,0),2.2)
   out+=(g*cloud*pulse*e['strength'])[...,None]*np.float32([.85,.94,1.])
  return out*self.pm[...,None]

 def screen(self,f,t):
  # Keep the original route/log primitive on its original twenty-second cycle.
  Farpoint.screen(self,f,t%self.config['screen']['period'])
  sc=self.config['screen'];c=self.config['screen_additions'];sw,sh=sc['size'];ink=np.zeros((sh,sw,3),np.float32)
  yy,xx=np.mgrid[:sh,:sw].astype(np.float32);cx,cy=c['radar_center'];rad=c['radar_radius']
  angle=2*np.pi*t/c['radar_period']-np.pi/2;polar=np.arctan2(yy-cy,xx-cx);r=np.hypot(xx-cx,yy-cy)
  # Smooth angular lobe eliminates the hard reset edge of the draft sweep.
  sweep=np.exp((np.cos(angle-polar)-1)*20)*smoothstep((rad-r)/2)*smoothstep(r/3)
  ink+=sweep[...,None]*np.float32([43,133,116])
  route=np.float32(sc['route'])
  for j in range(len(route)-1):
   phase=(t/c['route_period']*5-j*.52)%5;amount=float(smoothstep(phase/.22)*smoothstep((1.25-phase)/.3))
   line=np.zeros((sh,sw),np.uint8);cv2.line(line,tuple(np.rint(route[j]*256).astype(int)),tuple(np.rint(route[j+1]*256).astype(int)),255,c['route_width'],cv2.LINE_AA,8)
   ink+=(line.astype(np.float32)/255)[...,None]*amount*np.float32(c['route_color'])
  for j,(x,y) in enumerate(c['meter_origins']):
   level=2.6+1.8*np.sin(2*np.pi*c['meter_cycles'][0]*t/60+j*1.8)+.5*np.sin(2*np.pi*c['meter_cycles'][1]*t/60+j)
   for k in range(c['meter_segments']):ink[y:y+3,x+k*5:x+k*5+3]+=float(smoothstep((level-k)/.7))*np.float32(c['meter_color'])
  a,b,z,d=self.screen_box;mat=self.screen_matrix.copy();mat[0]-=a*mat[2];mat[1]-=b*mat[2]
  f[b:d,a:z]+=cv2.warpPerspective(ink,mat,(z-a,d-b),flags=cv2.INTER_LINEAR)*self.screen_mask[...,None]

 def frame_float(self,t,only=None):
  t=float(t)%self.duration;f=self.base.astype(np.float32)
  groups={'planet_activity':['clouds','veil','lower_cloud','cloud_shadows','aurora','lightning'],'aurora_storms':['aurora','lightning'],'stars_reflections':['stars','reflections','lamp'],'habitation':['windows','screen','lamp','instrument_lights','reflections']}
  wanted=set(self.masks) if only is None else set(groups.get(only,[only]));a,b,z,d=self.planet_roi
  moved=self.forward_cloud(t) if wanted&{'clouds','cloud_shadows','lightning'} else None
  if 'clouds' in wanted:f[b:d,a:z]+=(moved[...,:3]-moved[...,3,None]*self.clean-self.cloud)*self.pm[...,None]*self.config['planet']['transport']['gain']
  if 'veil' in wanted:f[b:d,a:z]+=self.veil_at(t)
  if 'cloud_shadows' in wanted:
   delta=self.clean*(np.exp(-self.config['new_atmosphere']['cloud_shadows']['strength']*(self.shadow_field(moved[...,3])-self.shadow_base))[...,None]-1)*(1-moved[...,3,None])
   f[b:d,a:z]+=delta*self.pm[...,None]
  if 'lightning' in wanted:f[b:d,a:z]+=self.storm(t,moved[...,3])
  if 'lower_cloud' in wanted:
   a,b,z,d=self.lower_roi;f[b:d,a:z]+=self.lower_cloud(t)
  if 'aurora' in wanted:
   a,b,z,d=self.config['aurora']['roi'];f[b:d,a:z]+=self.aurora(t)
  if 'windows' in wanted:
   for lc,m in self.windows:self.dim(f,m,self.amount(t,lc['events']))
  if 'screen' in wanted:self.screen(f,t)
  if 'lamp' in wanted:self.dim(f,self.lamp,self.amount(t,self.config['lamp']['events']))
  if 'reflections' in wanted:self.dim(f,self.reflections,self.amount(t,self.config['lamp']['events']))
  if 'instrument_lights' in wanted:
   for lc,m in self.instrument_lights:self.dim(f,m,self.amount(t,lc['events']))
  if 'stars' in wanted:
   for (a,b,z,d),m,cycles,phase in self.star_parts:
    value=self.config['stars']['depth']*np.sin(2*np.pi*cycles*t/60+phase);f[b:d,a:z]*=1+m[...,None]*value
  assert np.isfinite(f).all();return f

 def fingerprint(self):
  result=Farpoint.fingerprint(self)
  for v in [2,3,4]:
   p=H.parent/f'farpoint-animation-v{v}'/f'render_farpoint_v{v}.py';result['files'][p.relative_to(R).as_posix()]=digest(p)
  for v in [1,2,3]:
   p=H.parent/f'farpoint-animation-v{v}'/f'scene-plan-v{v}.json';result['files'][p.relative_to(R).as_posix()]=digest(p)
  result['duration']=60;return result

def samples(s):
 (H/'masks').mkdir(exist_ok=True)
 for k,m in s.masks.items():cv2.imwrite(str(H/'masks'/f'{k}.png'),byte_image(m*255))
 for t in [0,4,8,11.2,12.95,20,30,36.5,40,44.7,50,52.8,59+29/30]:
  Image.fromarray(cv2.resize(s.frame(t),(1280,720),interpolation=cv2.INTER_AREA)).save(H/f'sample-{t:06.2f}s.png')
 forced=s.base.astype(np.float32)
 for lc,m in s.instrument_lights:s.dim(forced,m,.9)
 for lc,m in s.windows:s.dim(forced,m,.9)
 s.dim(forced,s.lamp,.9);s.dim(forced,s.reflections,.9)
 Image.fromarray(byte_image(forced)).save(H/'forced-dark.png')
 overlay=s.base.astype(np.float32)
 for k,color in [('aurora',[0,255,200]),('stars',[255,0,150]),('reflections',[255,150,0])]:
  m=s.masks[k][...,None]*.55;overlay=overlay*(1-m)+np.float32(color)*m
 Image.fromarray(byte_image(overlay)).save(H/'new-mask-review.png')
 checks={}
 for key,m in s.layer_masks.items():
  start=s.frame(0,key);assert np.array_equal(start,s.frame(60,key)),key
  vals=[]
  for t in [-1/30,0,3,8,11.2,12.8,20,27.9,30,36.5,40,44.4,50,52.8,58]:
   vals.append(float(np.abs(s.frame(t+1/30,key)[m].astype(float)-s.frame(t,key)[m]).mean()))
  assert vals[0]<=max(vals[1:])*1.1+.01,(key,vals)
  checks[key]={'periodic_endpoint':True,'seam_mae':vals[0],'ordinary_sample_max':max(vals[1:]),'pass':True}
 # Retained extraction and source geometry are compared independently of new timing.
 old=FarpointV3();retained={k:bool(np.array_equal(getattr(s,k),getattr(old,k))) for k in ['base','cloud','clean','optical_cloud','omega','lower_optical','lower_clean','screen_matrix','screen_mask']}
 assert all(retained.values()),retained
 assert len({hashlib.sha256(s.frame(t).tobytes()).hexdigest() for t in [0,20,40]})==3
 save('analytic-validation.json',{'fingerprint':s.fingerprint(),'layer_checks':checks,'retained_v3_arrays_exact':retained,'distinct_0_20_40':True,'source_protection':'Asserted for every rendered frame','visual_acceptance':False})
 print('Samples and analytical checks passed',flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['samples','isolated','preview'],required=True);args=p.parse_args();s=FarpointMinute()
 if args.stage=='samples':samples(s);return
 clips=[]
 if args.stage=='isolated':
  for layer,offset in [('aurora_storms',7.5),('stars_reflections',9),('habitation',0),('planet_activity',20)]:
   class Excerpt:
    config=s.config
    def frame(self,t,only=None,prototype=False):return s.frame(t+offset,only,prototype)
   path=H/f'{layer}-v4-isolated-8s.mp4';item=encode(Excerpt(),path,8,layer,True);item['source_start_seconds']=offset;item['validation'],_=verify(s,path,240,False);clips.append(item)
 else:
  path=H/'farpoint-station-v4-preview-60s.mp4';item=encode(s,path,60);item['validation'],hashes=verify(s,path,1800,True);clips.append(item)
  repeat=H/'farpoint-station-v4-three-loops-180s.mp4';assert not repeat.exists()
  subprocess.run([s.config['ffmpeg'],'-v','error','-n','-stream_loop','2','-i',str(path),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
  validation,repeated=verify(s,repeat,5400,True);assert repeated==hashes*3
  clips.append({'path':repeat.relative_to(R).as_posix(),'sha256':digest(repeat),'validation':validation,'exact_three_decoded_repetitions':True})
  save('decoded-frame-hashes.json',hashes)
  cap=cv2.VideoCapture(str(path))
  for n in [0,336,600,1095,1200,1584,1799]:
   cap.set(cv2.CAP_PROP_POS_FRAMES,n);ok,f=cap.read();assert ok;cv2.imwrite(str(H/f'decoded-{n:04d}.png'),f)
  cap.release()
 save(args.stage+'-validation.json',{'fingerprint':s.fingerprint(),'clips':clips,'silent':True,'user_approved':False,'inspection':'Masks, temporal and decoded stills; continuous playback not claimed'})
 print(args.stage,'full decoding and validation passed',flush=True)

if __name__=='__main__':main()
