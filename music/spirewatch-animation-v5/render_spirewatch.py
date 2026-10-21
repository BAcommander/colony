"""Spirewatch v5: bright thumbnail-derived plate, newly mapped motion."""
from pathlib import Path
import sys,json,hashlib,argparse,subprocess
import numpy as np,cv2
from PIL import Image
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H/'dependencies'))
from ambient_effects import smoothstep,event_amount
import validation_legacy as old
cv2.setNumThreads(2)
TAU=2*np.pi
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def byte(a):return np.uint8(np.rint(np.clip(a,0,255)))
def save(n,obj):(H/n).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')
def bounds(m,pad=2):
 yy,xx=np.where(m>0);return max(0,int(xx.min())-pad),max(0,int(yy.min())-pad),min(m.shape[1],int(xx.max())+1+pad),min(m.shape[0],int(yy.max())+1+pad)

class Spirewatch:
 def __init__(self):
  self.path=H/'scene-plan-v5.json';self.config=json.loads(self.path.read_text());c=self.config
  assert sha(H/c['source']['path'])==c['source']['sha256']
  self.base=np.array(Image.open(H/c['source']['path']).convert('RGB'));self.h,self.w=self.base.shape[:2];self.shape=(self.h,self.w)
  assert [self.w,self.h]==c['source']['dimensions'];self.y,self.x=np.mgrid[:self.h,:self.w].astype(np.float32)
  self.duration=60;self.masks={};self.activity=c['music_activity']
  self.make_sky();self.make_water();self.make_falls();self.make_lights();self.make_transit();self.make_room();self.make_storm()
  self.layer_masks={k:m>0 for k,m in self.masks.items()};self.active=np.logical_or.reduce(list(self.layer_masks.values()))
 def poly(self,polys,feather=0):
  m=np.zeros(self.shape,np.uint8)
  for p in polys:cv2.fillPoly(m,[np.int32(p)],1)
  return smoothstep(cv2.distanceTransform(m,cv2.DIST_L2,5)/feather).astype(np.float32) if feather else m.astype(np.float32)
 def install(self,name,m):
  m=m.astype(np.float32);m[m<.002]=0;self.masks[name]=m
  a,b,z,d=bounds(m);y,x=np.mgrid[b:d,a:z].astype(np.float32)
  return (a,b,z,d),m[b:d,a:z],x,y
 def make_sky(self):
  c=self.config;binary=self.poly([c['sky_polygon']]);block=self.poly(c['sky_exclusions'])
  for p,q,w in c['masts']:cv2.line(block,tuple(p),tuple(q),1,w+2)
  binary*=1-block
  binary=cv2.erode(binary,np.ones((17,17),np.uint8))
  dist=cv2.distanceTransform(binary.astype(np.uint8),cv2.DIST_L2,5)
  # Mask allows local source transport without ever sampling architecture.
  m=smoothstep((dist-2)/5);self.sky=self.install('clouds',m)
  roi,mask,x,y=self.sky;a,b,z,d=roi
  self.sky_plate=self.base[b:d,a:z].astype(np.float32)
  self.sky_dist=dist[b:d,a:z]
  self.sky_xy=(x-a,y-b)
  self.sky_phase=(x/6800+y/4200+.1).astype(np.float32)
  self.sky_speed=c['cloud_speed']*(1-.52*smoothstep((y-270)/160))
 def make_water(self):
  self.water=[];total=np.zeros(self.shape,np.float32)
  for poly in self.config['water_polygons']:
   m=self.poly([poly],4);m[m<.002]=0;a,b,z,d=bounds(m);y,x=np.mgrid[b:d,a:z].astype(np.float32)
   depth=np.clip((y-560)/340,.15,.85)
   self.water.append(((a,b,z,d),m[b:d,a:z],x,y,self.base[b:d,a:z].astype(np.float32),depth))
   total=np.maximum(total,m)
  self.install('water',total);self.install('reflections',total.copy())
 def make_falls(self):
  self.falls=[];total=np.zeros(self.shape,np.float32)
  for c in self.config['falls']:
   m=self.poly([c['polygon']],2);m[m<.002]=0;a,b,z,d=bounds(m);p=self.base[b:d,a:z].astype(np.float32);hh,ww=p.shape[:2]
   # Use source material only, with a stable slowly varying vertical light field.
   level=np.maximum(cv2.GaussianBlur(p,(0,0),.65,22),5)
   section=p[max(2,hh//9):-max(2,hh//9)]
   tile=np.concatenate([section,section[::-1]],axis=0)
   tile=tile/np.maximum(cv2.GaussianBlur(tile,(0,0),.65,18),5)
   y,x=np.mgrid[:hh,:ww].astype(np.float32)
   self.falls.append(((a,b,z,d),m[b:d,a:z],x,y,tile,level,c['period']))
   total=np.maximum(total,m)
  self.install('falls',total)
 def make_lights(self):
  rgb=self.base.astype(np.float32)
  cyan=np.clip((rgb[:,:,2]-rgb[:,:,0]-15)/45,0,1)*np.clip((rgb[:,:,1]-rgb[:,:,0]-10)/40,0,1)*np.clip((rgb[:,:,1]-45)/75,0,1)
  self.tower=self.install('tower',cyan*self.poly([self.config['tower_polygon']],1))
  corona=cv2.GaussianBlur(self.masks['tower'],(0,0),4)*.7
  self.corona=self.install('tower_glow',corona)
  self.districts=[];total=np.zeros(self.shape,np.float32)
  for i,(a,b,z,d) in enumerate(self.config['district_boxes']):
   m=np.zeros(self.shape,np.float32);m[b:d,a:z]=cyan[b:d,a:z]
   m=np.maximum(m,cv2.GaussianBlur(m,(0,0),1.8)*.15);m[m<.002]=0
   roi=bounds(m);a,b,z,d=roi;y,x=np.mgrid[b:d,a:z].astype(np.float32)
   self.districts.append((i,roi,m[b:d,a:z],x,y));total=np.maximum(total,m)
  self.install('districts',total)
  self.windows=[];total=np.zeros(self.shape,np.float32);rng=np.random.default_rng(2110);used=np.zeros(self.shape,np.uint8);self.window_records=[]
  for ri,(a,b,z,d) in enumerate(self.config['window_regions']):
   p=rgb[b:d,a:z];warm=(p[:,:,0]>p[:,:,2]*1.22)&(p[:,:,0]>90)&(p[:,:,1]>55)
   n,lab,stats,_=cv2.connectedComponentsWithStats(warm.astype(np.uint8),8);candidates=[]
   for x,y,w,h,area in stats[1:]:
    x,y,w,h,area=map(int,[x+a,y+b,w,h,area])
    if 2<=area<=70 and w<=13 and h<=17 and not used[y:y+h,x:x+w].any():candidates.append((x,y,w,h))
   candidates.sort(key=lambda v:v[2]*v[3],reverse=True)
   for j in range(2):
    if not candidates:break
    ax,ay,*_=candidates[0];near=[q for q in candidates if abs(q[0]-ax)<30 and abs(q[1]-ay)<23][:5]
    candidates=[q for q in candidates if q not in near];m=np.zeros(self.shape,np.float32)
    for x,y,w,h in near:m[y:y+h,x:x+w]=1;used[y:y+h,x:x+w]=1
    m=np.maximum(m,cv2.GaussianBlur(m,(0,0),1.4)*.2);m[m<.002]=0;roi=bounds(m);a0,b0,z0,d0=roi
    start=float(rng.uniform(0,60));hold=float(rng.uniform(6,12));depth=float(rng.uniform(.35,.65))
    self.windows.append((roi,m[b0:d0,a0:z0],start,hold,depth));total=np.maximum(total,m)
    self.window_records.append({'region':ri,'apertures':near,'start':start,'hold':hold,'depth':depth})
  self.install('windows',total)
 def make_transit(self):
  self.route=np.float32(self.config['route']);self.lengths=np.r_[0,np.cumsum(np.linalg.norm(np.diff(self.route,axis=0),axis=1))]
  m=np.zeros(self.shape,np.uint8);cv2.polylines(m,[self.route.astype(np.int32)],False,255,14)
  m=cv2.GaussianBlur(m.astype(np.float32)/255,(0,0),1.3)*(1-self.poly(self.config['transit_occluders']))
  self.transit=self.install('transit',m)
  (a,b,z,d),m,x,y=self.transit;self.route_y=np.interp(x,self.route[:,0],self.route[:,1]);self.route_distance=np.interp(x,self.route[:,0],self.lengths)
 def make_room(self):
  self.screen=self.install('screen',self.poly([self.config['screen_polygon']],2))
  self.screen_route=np.float32(self.config['screen_route']);self.screen_lengths=np.r_[0,np.cumsum(np.linalg.norm(np.diff(self.screen_route,axis=0),axis=1))]
  core=self.poly([self.config['lamp_core']],1)
  spill=self.poly([self.config['lamp_spill']],12)*.5
  wall=self.poly([[[0,549],[119,551],[129,704],[0,709]]],10)*.2
  self.lamp=self.install('lamp',np.maximum(core,np.maximum(spill,wall)))
  screen_spill=self.poly([[[150,714],[280,725],[365,742],[325,754],[178,732]]],8)*.3
  self.screen_spill=self.install('screen_spill',screen_spill)
 def make_storm(self):
  self.storm=[];total=np.zeros(self.shape,np.float32);response=np.zeros(self.shape,np.float32)
  lum=self.base.astype(np.float32).mean(2)
  for c in self.config['storms']:
   px,py=c['center'];rx,ry=c['radius'];g=np.exp(-((self.x-px)/rx)**2-((self.y-py)/ry)**2)
   m=g*self.masks['clouds']*(.25+.75*np.clip(lum/100,0,1));roi=bounds(np.where(m>.002,m,0));a,b,z,d=roi
   m[m<.002]=0;self.storm.append((c,roi,m[b:d,a:z]));total=np.maximum(total,m)
   response=np.maximum(response,self.masks['water']*np.exp(-((self.x-px)/(rx*1.6))**2)*.25)
  self.install('lightning',total);self.response=self.install('storm_response',response)
 def vehicle(self,t):
  for start,end,direction in self.config['transit_events']:
   age=(t-start)/(end-start)
   if 0<=age<=1:
    progress=age if direction==1 else 1-age;env=float(smoothstep(age/.08)*smoothstep((1-age)/.08))*self.activity
    distance=progress*self.lengths[-1];x=float(np.interp(distance,self.lengths,self.route[:,0]));y=float(np.interp(distance,self.lengths,self.route[:,1]))
    return progress,env,direction,distance,x,y,np.float32([65,156,194] if direction==1 else [210,126,36])
  return 0.,0.,1,0.,663.,559.,np.float32([65,156,194])
 def district_amount(self,t,i):
  delay=self.config['district_delays'][i]
  return max(event_amount(t,60,(19+delay)%60,5,1.5),event_amount(t,60,(49+delay)%60,5,1.5))*self.activity
 def flash_value(self,t,c):
  dt=(t-c['time'])%60
  if dt>1.8:return 0.
  return float(c['strength']*(np.exp(-((dt-.20)/.14)**2)+.55*np.exp(-((dt-.52)/.17)**2)+.2*np.exp(-((dt-.95)/.34)**2)))*float(smoothstep(dt/.07)*smoothstep((1.8-dt)/.25))
 def frame(self,t,only=None):
  t=float(t)%60;f=self.base.astype(np.float32);enabled=lambda k:only is None or only==k
  if enabled('clouds'):
   (a,b,z,d),m,x,y=self.sky;xx,yy=self.sky_xy;plate=self.sky_plate
   moving=np.zeros_like(plate);weights=np.zeros_like(m)
   for shift in [0,.5]:
    age=(t/60+self.sky_phase+shift)%1;weight=np.sin(np.pi*age)**6
    requested=(age-.5)*60*self.sky_speed
    # Smooth bound guarantees source sampling remains on this side of every edge.
    limit=np.maximum(self.sky_dist-3,0)*.45
    dx=limit*np.tanh(requested/np.maximum(limit,1))
    patch=cv2.remap(plate,(xx-dx).astype(np.float32),yy,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT_101)
    moving+=patch*weight[...,None];weights+=weight
   moving/=np.maximum(weights[...,None],1e-6)
   f[b:d,a:z]+=(moving-plate)*m[...,None]*.90
  if enabled('water'):
   for (a,b,z,d),m,x,y,plate,depth in self.water:
    dx=(np.sin(y*.48+x*.019-TAU*t/12)+.35*np.sin(y*.87-x*.027-TAU*t/10))*depth*m*.65
    dy=np.sin(y*.34+x*.05-TAU*t/15)*depth*m*.12
    moving=cv2.remap(plate,(x-a+dx).astype(np.float32),(y-b+dy).astype(np.float32),cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT_101)
    f[b:d,a:z]+=(moving-plate)*m[...,None]
  if enabled('falls'):
   for (a,b,z,d),m,x,y,tile,level,period in self.falls:
    material=cv2.remap(tile,x,(y-t*tile.shape[0]/period).astype(np.float32)%tile.shape[0],cv2.INTER_CUBIC,borderMode=cv2.BORDER_WRAP)
    moving=level*(1+(np.clip(material,.45,1.7)-1)*.65)
    f[b:d,a:z]=f[b:d,a:z]*(1-m[...,None]*.85)+moving*m[...,None]*.85
  charge=event_amount(t,60,.5,5,1.5);crown=event_amount(t,60,17,5,1.3)
  if enabled('tower') or enabled('tower_glow'):
   for name,data,color,scale in [('tower',self.tower,[16,55,70],1.),('tower_glow',self.corona,[5,22,32],.7)]:
    if not enabled(name):continue
    (a,b,z,d),m,x,y=data;band=np.zeros_like(m)
    for start,end,direction in self.config['tower_events']:
     age=(t-start-(x-1280)*.014)/(end-start);env=smoothstep(age/.1)*smoothstep((1-age)/.1)
     center=450-385*age if direction=='up' else 65+385*age
     band+=np.exp(-((y-center)/37)**2)*env
    amount=(band+charge*.45*np.exp(-((y-440)/34)**2)+crown*.65*np.exp(-((y-93)/48)**2))*self.activity*scale
    f[b:d,a:z]+=m[...,None]*amount[...,None]*np.float32(color)
  if enabled('districts'):
   for i,(a,b,z,d),m,x,y in self.districts:
    amount=self.district_amount(t,i);band=.45+.55*np.sin((y-b)/(d-b)*np.pi-TAU*t/20)**2
    f[b:d,a:z]+=m[...,None]*(amount*band)[...,None]*np.float32([10,42,53])
  if enabled('windows'):
   for (a,b,z,d),m,start,hold,depth in self.windows:
    f[b:d,a:z]*=1-m[...,None]*event_amount(t,60,start,hold,1.2)*depth
  progress,env,direction,distance,px,py,color=self.vehicle(t)
  if enabled('transit') and env>0:
   (a,b,z,d),m,x,y=self.transit;perspective=np.clip(.45+.55*(x-663)/1008,.4,1)
   cross=y-self.route_y+(-1.2 if direction==1 else 1.2);behind=(distance-self.route_distance)*direction
   tail=np.exp(-np.maximum(behind,0)/(42*perspective))*smoothstep((behind+2)/4)*smoothstep((115*perspective-behind)/18)
   line=np.exp(-(cross/(1.15*perspective+.4))**2);head=np.exp(-((self.route_distance-distance)/(5*perspective))**2-(cross/(1.6*perspective+.4))**2)
   light=(tail*line*.9+head)*env*m
   f[b:d,a:z]+=(light+cv2.GaussianBlur(light,(0,0),1.7)*.25*m)[...,None]*color
  if enabled('reflections'):
   for (a,b,z,d),m,x,y,plate,depth in self.water:
    ripple=(.5+.5*np.sin(y*.73+x*.023-TAU*t/5))**3*(.7+.3*np.sin(y*.21-x*.02+TAU*t/12)**2)
    details=.35+.65*np.clip(plate.mean(2)/90,0,1)
    spread=12+np.maximum(y-py,0)*.12
    trail=np.exp(-((x-px-2*np.sin(y*.22+TAU*t/10))/spread)**2)*np.exp(-np.maximum(y-py,0)/160)*env
    tower=np.exp(-((x-1290)/90)**2)*(.12*charge+.30*crown)*self.activity
    f[b:d,a:z]+=(m*ripple*details)[...,None]*(trail[...,None]*color*.34+tower[...,None]*np.float32([15,55,70]))
  if enabled('screen'):
   (a,b,z,d),m,x,y=self.screen;dist=progress*self.screen_lengths[-1]
   sx=np.interp(dist,self.screen_lengths,self.screen_route[:,0]);sy=np.interp(dist,self.screen_lengths,self.screen_route[:,1])
   marker=np.exp(-((x-sx)**2+(y-sy)**2)/5)*env
   details=np.clip((self.base[b:d,a:z,2].astype(float)-self.base[b:d,a:z,0].astype(float)-8)/45,0,1)
   sweep=np.maximum((.5+.5*np.cos(TAU*(t/20-(x-145)/170)))-.92,0)/.08
   light=marker[...,None]*np.float32([38,110,137])+details[...,None]*sweep[...,None]*np.float32([3,13,19])
   for j,(sx,sy) in enumerate(self.screen_route[[1,3,5]]):
    light+=np.exp(-((x-sx)**2+(y-sy)**2)/3)[...,None]*self.district_amount(t,j)*np.float32([38,79,101])
   f[b:d,a:z]+=light*m[...,None]
  if enabled('lamp'):
   (a,b,z,d),m,x,y=self.lamp;amount=max(event_amount(t,60,32.1,.28,.10),event_amount(t,60,32.8,.16,.08))
   f[b:d,a:z]*=1-m[...,None]*amount*.60
  if enabled('screen_spill'):
   (a,b,z,d),m,x,y=self.screen_spill;f[b:d,a:z]+=m[...,None]*env*np.float32([1,4,6])
  flash=0.
  for c,(a,b,z,d),m in self.storm:
   amount=self.flash_value(t,c);flash=max(flash,amount)
   if enabled('lightning') and amount>0:
    detail=.35+.65*np.clip(f[b:d,a:z].mean(2)/110,0,1)
    f[b:d,a:z]+=m[...,None]*detail[...,None]*amount*np.float32([58,84,108])
  if enabled('storm_response'):
   (a,b,z,d),m,x,y=self.response;f[b:d,a:z]+=m[...,None]*flash*np.float32([15,30,45])
  assert np.isfinite(f).all();out=byte(f);active=self.active if only is None else self.layer_masks[only]
  assert np.array_equal(out[~active],self.base[~active]),'Protected source changed'
  return out
 def fingerprint(self):
  return {'source':self.config['source'],'config_sha256':sha(self.path),'renderer_sha256':sha(__file__),'validation_sha256':sha(H/'validation_legacy.py'),'dependencies':{p.name:sha(p) for p in sorted((H/'dependencies').glob('*.py'))},'masks':{k:hashlib.sha256(m.tobytes()).hexdigest() for k,m in self.masks.items()},'runtime':{'numpy':np.__version__,'opencv':cv2.__version__}}

def verify():
 s=Spirewatch();out=H/'spirewatch-v5-preview-60s.mp4';repeat=H/'spirewatch-v5-three-loops-180s.mp4'
 report=old.verify(s,out,1800);save('preview-validation.json',{'fingerprint':s.fingerprint(),**report})
 if not repeat.exists():subprocess.run([s.config['ffmpeg'],'-v','error','-n','-stream_loop','2','-i',str(out),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
 save('repeat-validation.json',old.verify(s,repeat,5400,True,True));print('V5 full minute and repeats verified',flush=True)
if __name__=='__main__':verify()
