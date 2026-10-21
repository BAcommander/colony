"""Spirewatch v7: bright thumbnail-derived plate, newly mapped motion."""
from pathlib import Path
import sys,json,hashlib,argparse,subprocess
import numpy as np,cv2
from PIL import Image
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H/'dependencies'))
from ambient_effects import smoothstep,event_amount
import validation_legacy as old
old.H=H
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
  self.path=H/'scene-plan-v7.json';self.config=json.loads(self.path.read_text());c=self.config
  assert sha(H/c['source']['path'])==c['source']['sha256']
  self.base=np.array(Image.open(H/c['source']['path']).convert('RGB'));self.h,self.w=self.base.shape[:2];self.shape=(self.h,self.w)
  assert [self.w,self.h]==c['source']['dimensions'];self.y,self.x=np.mgrid[:self.h,:self.w].astype(np.float32)
  self.duration=60;self.masks={};self.activity=c['music_activity'];self.v=c['visibility']
  self.make_sky();self.make_water();self.make_falls();self.make_lights();self.make_transit();self.make_room();self.make_storm();self.make_rain()
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
  # Saturated white cores belong to the same emitter, not static holes in a cyan mask.
  adjacent=cv2.dilate(np.float32(cyan>.4),np.ones((3,3),np.uint8))
  cyan=np.maximum(cyan,adjacent*np.float32((rgb[:,:,1]>145)&(rgb[:,:,2]>155)&(rgb[:,:,0]<rgb[:,:,2]*1.04)))
  # Only local bright strips are emissive. Broad blue wall/fog belongs to the
  # immutable structure; dimming it created a flat cut across the tower foot.
  local=rgb[:,:,1]-cv2.GaussianBlur(rgb[:,:,1],(0,0),4,.8)
  seeds=np.float32((cyan>.25)&(rgb[:,:,1]>105)&(local>23))
  emit=cv2.GaussianBlur(cv2.dilate(seeds,np.ones((1,3),np.uint8)),(0,0),.55)
  foundation=1-smoothstep((self.y-385)/40)
  self.tower=self.install('tower',emit*self.poly([self.config['tower_polygon']],1)*foundation)
  corona=cv2.GaussianBlur(self.masks['tower'],(0,0),4)*.7*foundation
  self.corona=self.install('tower_glow',corona)
  self.districts=[];total=np.zeros(self.shape,np.float32)
  for i,polys in enumerate(self.config['district_polygons']):
   m=cyan*self.poly(polys,1)
   m=np.maximum(m,cv2.GaussianBlur(m,(0,0),1.8)*.15);m[m<.002]=0
   roi=bounds(m);a,b,z,d=roi;y,x=np.mgrid[b:d,a:z].astype(np.float32)
   self.districts.append((i,roi,m[b:d,a:z],x,y));total=np.maximum(total,m)
  self.install('districts',total)
  self.windows=[];total=np.zeros(self.shape,np.float32);rng=np.random.default_rng(2110);used=np.zeros(self.shape,np.uint8);self.window_records=[]
  for ri,(a,b,z,d) in enumerate(self.config['window_regions']):
   p=rgb[b:d,a:z];seed=(p[:,:,0]>p[:,:,2]*1.22)&(p[:,:,0]>90)&(p[:,:,1]>55)
   near=cv2.dilate(np.float32(seed),np.ones((3,3),np.uint8))>0
   warm=seed|(near&(p[:,:,0]>160)&(p[:,:,1]>115)&(p[:,:,0]>p[:,:,2]*.98))
   n,lab,stats,_=cv2.connectedComponentsWithStats(warm.astype(np.uint8),8);candidates=[]
   for x,y,w,h,area in stats[1:]:
    x,y,w,h,area=map(int,[x+a,y+b,w,h,area])
    if 2<=area<=100 and w<=15 and h<=18 and not used[y:y+h,x:x+w].any():candidates.append((x,y,w,h))
   candidates.sort(key=lambda v:v[2]*v[3],reverse=True)
   for j in range(self.v['window_groups_per_region']):
    if not candidates:break
    ax,ay,*_=candidates[0];near=[q for q in candidates if abs(q[0]-ax)<24 and abs(q[1]-ay)<15][:7]
    candidates=[q for q in candidates if q not in near];m=np.zeros(self.shape,np.float32)
    for x,y,w,h in near:m[y:y+h,x:x+w]=1;used[y:y+h,x:x+w]=1
    m=np.maximum(m,cv2.GaussianBlur(m,(0,0),2.2)*.35);m[m<.002]=0;roi=bounds(m);a0,b0,z0,d0=roi
    start=float((ri*3.7+j*11.3)%60);hold=float(rng.uniform(4,9));depth=float(rng.uniform(.72,1-self.v['warm_window_floor']))
    self.windows.append((roi,m[b0:d0,a0:z0],start,hold,depth));total=np.maximum(total,m)
    self.window_records.append({'region':ri,'apertures':near,'start':start,'hold':hold,'depth':depth})
  self.install('windows',total)
 def make_transit(self):
  self.route=np.float32(self.config['route']);self.lengths=np.r_[0,np.cumsum(np.linalg.norm(np.diff(self.route,axis=0),axis=1))]
  # Read the actual source lanes. A single thin guessed centerline missed the rail
  # at the right of the picture and added almost nothing over white source streaks.
  rgb=self.base.astype(np.float32);guide=np.interp(self.x,self.route[:,0],self.route[:,1]);cross=self.y-guide
  inside=(self.x>=663)&(self.x<1672)
  warm=(rgb[:,:,0]>rgb[:,:,2]*1.12)&(rgb[:,:,0]>95)
  cool=(rgb[:,:,2]>rgb[:,:,0]*1.2)&(rgb[:,:,1]>95)
  masks=[]
  for seed,lo,hi in [(cool,-5,18),(warm,-24,4)]:
   seed=np.float32(seed&inside&(cross>lo)&(cross<hi))
   core=cv2.dilate(seed,np.ones((3,3),np.uint8))*np.float32((rgb[:,:,1]>45)&(cross>lo)&(cross<hi)&inside)
   m=cv2.GaussianBlur(cv2.dilate(core,np.ones((3,3),np.uint8)),(0,0),1.2)
   m*=1-self.poly(self.config['transit_occluders']);m[m<.002]=0;masks.append(m)
  m=np.maximum(*masks);self.transit=self.install('transit',m)
  (a,b,z,d),_,x,y=self.transit;self.lanes=[m[b:d,a:z] for m in masks]
  self.route_y=np.interp(x,self.route[:,0],self.route[:,1]);self.route_distance=np.interp(x,self.route[:,0],self.lengths)
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
  # Illumination does not transport source pixels, so it needs no broad sky
  # erosion halo. Keep actual building/mast silhouettes out of the flash.
  sky=self.poly([self.config['sky_polygon']])*(1-self.poly(self.config['lightning_exclusions']))
  for p,q,w in self.config['masts']:cv2.line(sky,tuple(p),tuple(q),0,w+1)
  sky=smoothstep(cv2.distanceTransform(sky.astype(np.uint8),cv2.DIST_L2,5)/2)
  for c in self.config['storms']:
   px,py=c['center'];rx,ry=c['radius'];g=np.exp(-((self.x-px)/rx)**2-((self.y-py)/ry)**2)
   lobes=.7+.16*np.sin(self.x*.021+self.y*.013)+.14*np.sin(self.x*.037-self.y*.026)
   m=g*sky*lobes*(.25+.75*np.clip(lum/100,0,1));m[m<.002]=0;roi=bounds(m);a,b,z,d=roi
   branch=np.zeros(self.shape,np.float32)
   pts=np.float32(c['branch'])
   # Supersampled fine fragments, mostly veiled by the source cloud texture.
   rng=np.random.default_rng(int(c['time']*100));jagged=[]
   for first,last in zip(pts[:-1],pts[1:]):
    delta=last-first;length=float(np.linalg.norm(delta));perp=np.float32([-delta[1],delta[0]])/length
    for u in np.linspace(0,1,max(3,int(length/5)),endpoint=False):jagged.append(first+delta*u+perp*rng.uniform(-3,3)*np.sin(np.pi*u))
   jagged.append(pts[-1]);jagged=np.float32(jagged)
   high=np.zeros((self.h*2,self.w*2),np.uint8);cv2.polylines(high,[np.int32(jagged*2)],False,255,1,cv2.LINE_AA)
   mid=pts[len(pts)//2];fork=np.float32([mid,mid+[18,-18],mid+[39,-29]])
   cv2.polylines(high,[np.int32(fork*2)],False,150,1,cv2.LINE_AA)
   branch=cv2.resize(high.astype(np.float32)/255,(self.w,self.h),interpolation=cv2.INTER_AREA)
   veil=np.clip((lum-42)/90,0,.65)*(.5+.5*np.sin(self.x*.083+self.y*.051)**2)
   branch=(branch+cv2.GaussianBlur(branch,(0,0),2)*1.3)*sky*veil
   branch*=m>0
   wr=self.masks['water']*np.exp(-((self.x-px)/(rx*1.3))**2)*.23;wr[wr<.002]=0;water_roi=bounds(wr);wa,wb,wz,wd=water_roi
   self.storm.append((c,roi,m[b:d,a:z],branch[b:d,a:z],water_roi,wr[wb:wd,wa:wz]));total=np.maximum(total,m);response=np.maximum(response,wr)
  self.install('lightning',total);self.response=self.install('storm_response',response)
 def make_rain(self):
  c=self.config['rain'];mask=self.poly([c['window_polygon']],4)*(1-self.poly(c['foreground_exclusions']))
  self.rain=self.install('rain',mask);rng=np.random.default_rng(c['seed']);self.drops=[]
  for i in range(c['count']):
   depth=c['depths'][0 if i<c['count']*.60 else 1 if i<c['count']*.88 else 2]
   self.drops.append((float(rng.uniform(180,1760)),float(rng.uniform(0,1)),float(rng.uniform(.65,1.)),depth))
 def rain_amount(self,t):
  return max(float(smoothstep(((t-start)%60)/fadein)*smoothstep((length-(t-start)%60)/fadeout)) for start,length,fadein,fadeout in self.config['rain']['events'])
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
    dx=(np.sin(y*.32+x*.019-TAU*t/12)+.35*np.sin(y*.61-x*.027-TAU*t/10))*depth*m*self.v['water_displacement']
    dy=np.sin(y*.34+x*.05-TAU*t/15)*depth*m*.32
    moving=cv2.remap(plate,(x-a+dx).astype(np.float32),(y-b+dy).astype(np.float32),cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT_101)
    f[b:d,a:z]+=(moving-plate)*m[...,None]
  if enabled('falls'):
   for (a,b,z,d),m,x,y,tile,level,period in self.falls:
    material=cv2.remap(tile,x,(y-t*tile.shape[0]/period).astype(np.float32)%tile.shape[0],cv2.INTER_CUBIC,borderMode=cv2.BORDER_WRAP)
    # Downward travelling foam filaments at different widths, not a near-static
    # vertical texture with only its tiny high-frequency residual changing.
    phase=TAU*(y/37-t/(period/5))+.9*np.sin(x*.31)+.45*np.sin(x*.83)
    front=.62*np.sin(phase)+.28*np.sin(TAU*(y/61-t/(period/3))+1.8*np.sin(x*.19))+.10*np.sin(TAU*(y/17-t/(period/7))+x*.63)
    foam=np.exp(-(np.sin(phase*.5)/.34)**2)
    moving=level*(1+(np.clip(material,.45,1.7)-1)*.55+front[...,None]*self.v['waterfall_texture_contrast'])
    moving+=foam[...,None]*np.float32([12,19,22])
    f[b:d,a:z]=f[b:d,a:z]*(1-m[...,None]*.96)+moving*m[...,None]*.96
  charge=event_amount(t,60,.5,5,1.5);crown=event_amount(t,60,17,5,1.3)
  if enabled('tower') or enabled('tower_glow'):
   for name,data,color,scale in [('tower',self.tower,[26,72,88],1.),('tower_glow',self.corona,[8,38,58],1.)]:
    if not enabled(name):continue
    (a,b,z,d),m,x,y=data;band=np.zeros_like(m)
    for start,end,direction in self.config['tower_events']:
     age=(t-start-(x-1280)*.014)/(end-start);env=smoothstep(age/.1)*smoothstep((1-age)/.1)
     center=450-385*age if direction=='up' else 65+385*age
     band+=np.exp(-((y-center)/self.v['tower_head_width'])**2)*env
    amount=(band+charge*.45*np.exp(-((y-440)/34)**2)+crown*.65*np.exp(-((y-93)/48)**2))*self.activity*scale
    if name=='tower':
     gain=self.v['tower_floor']+(1.3-self.v['tower_floor'])*np.clip(amount,0,1)
     f[b:d,a:z]*=1+m[...,None]*(gain[...,None]-1)
    f[b:d,a:z]+=m[...,None]*amount[...,None]*np.float32(color)
  if enabled('districts'):
   for i,(a,b,z,d),m,x,y in self.districts:
    age=(t/20-i*.13)%1
    center=b-65+age*(d-b+130)
    band=np.exp(-((y-center)/48)**2)*smoothstep(age/.12)*smoothstep((1-age)/.12)
    gain=.50+.75*band
    f[b:d,a:z]*=1+m[...,None]*(gain[...,None]-1)
    f[b:d,a:z]+=m[...,None]*band[...,None]*np.float32([12,48,65])
  if enabled('windows'):
   for (a,b,z,d),m,start,hold,depth in self.windows:
    amount=max(event_amount(t,60,start,hold,.45),event_amount(t,60,(start+29)%60,hold*.7,.6))
    f[b:d,a:z]*=1-m[...,None]*amount*depth
  progress,env,direction,distance,px,py,color=self.vehicle(t)
  if enabled('transit'):
   (a,b,z,d),m,x,y=self.transit
   for i,lane in enumerate(self.lanes):
    pulse=np.zeros_like(m)
    for phase in [0,.5]:
     age=(t/(20 if i==0 else 30)+phase+i*.17)%1
     pos=540+age*1280 if i==0 else 1820-age*1280
     length=65+60*np.clip((x-663)/1008,0,1)
     envelope=smoothstep(age/.09)*smoothstep((1-age)/.09)
     pulse=np.maximum(pulse,np.exp(-((x-pos)/length)**4)*envelope)
    gain=self.v['transit_floor']+(1.35-self.v['transit_floor'])*pulse
    f[b:d,a:z]*=1+lane[...,None]*(gain[...,None]-1)
    f[b:d,a:z]+=lane[...,None]*pulse[...,None]*np.float32([10,24,32] if i==0 else [32,19,5])
  if enabled('reflections'):
   for (a,b,z,d),m,x,y,plate,depth in self.water:
    ripple=(.5+.5*np.sin(y*.73+x*.023-TAU*t/5))**3*(.7+.3*np.sin(y*.21-x*.02+TAU*t/12)**2)
    details=.35+.65*np.clip(plate.mean(2)/90,0,1)
    reflected=np.zeros((*m.shape,3),np.float32)
    for i in range(2):
     for phase in [0,.5]:
      age=(t/(20 if i==0 else 30)+phase+i*.17)%1
      pos=540+age*1280 if i==0 else 1820-age*1280
      route_y=float(np.interp(pos,self.route[:,0],self.route[:,1]))
      spread=20+np.maximum(y-route_y,0)*.14
      envelope=smoothstep(age/.09)*smoothstep((1-age)/.09)
      trail=np.exp(-((x-pos-2*np.sin(y*.22+TAU*t/10))/spread)**2)*np.exp(-np.maximum(y-route_y,0)/180)*envelope
      reflected+=trail[...,None]*np.float32([16,49,65] if i==0 else [60,35,8])
    tower=np.exp(-((x-1290)/90)**2)*(.12*charge+.30*crown)*self.activity
    f[b:d,a:z]+=(m*ripple*details)[...,None]*(reflected+tower[...,None]*np.float32([15,55,70]))
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
  if enabled('rain'):
   strength=self.rain_amount(t)
   if strength>0:
    (a,b,z,d),m,x,y=self.rain;drops=np.zeros(m.shape,np.uint8);c=self.config['rain']
    for sx,phase,opacity,depth in self.drops:
     age=(t/depth['life']+phase)%1
     py=-45+age*(self.h+90);px=sx+c['wind_pixels_per_second']*age*depth['life']
     env=float(smoothstep(age/.08)*smoothstep((1-age)/.08))
     length=depth['length'];dx=-length*.11
     cv2.line(drops,(int(px-a),int(py-b)),(int(px-a+dx),int(py-b+length)),int(255*opacity*depth['strength']*env),depth['width'],cv2.LINE_AA)
    rain=drops.astype(np.float32)/255*m*strength*c['opacity']
    f[b:d,a:z]+=rain[...,None]*np.float32([91,132,156])
  for c,(a,b,z,d),m,branch,(wa,wb,wz,wd),wr in self.storm:
   amount=self.flash_value(t,c)
   if enabled('lightning') and amount>0:
    detail=.35+.65*np.clip(f[b:d,a:z].mean(2)/110,0,1)
    f[b:d,a:z]+=m[...,None]*detail[...,None]*amount*np.float32([78,105,130])
    f[b:d,a:z]+=branch[...,None]*amount*np.float32([100,130,158])
   if enabled('storm_response') and amount>0:
    f[wb:wd,wa:wz]+=wr[...,None]*amount*np.float32([15,30,45])
  assert np.isfinite(f).all();out=byte(f);active=self.active if only is None else self.layer_masks[only]
  assert np.array_equal(out[~active],self.base[~active]),'Protected source changed'
  return out
 def fingerprint(self):
  return {'source':self.config['source'],'config_sha256':sha(self.path),'renderer_sha256':sha(__file__),'validation_sha256':sha(H/'validation_legacy.py'),'dependencies':{p.name:sha(p) for p in sorted((H/'dependencies').glob('*.py'))},'masks':{k:hashlib.sha256(m.tobytes()).hexdigest() for k,m in self.masks.items()},'runtime':{'numpy':np.__version__,'opencv':cv2.__version__}}

def verify():
 s=Spirewatch();out=H/'spirewatch-v7-preview-60s.mp4';repeat=H/'spirewatch-v7-three-loops-180s.mp4'
 report=old.verify(s,out,1800);save('preview-validation.json',{'fingerprint':s.fingerprint(),**report})
 if not repeat.exists():subprocess.run([s.config['ffmpeg'],'-v','error','-n','-stream_loop','2','-i',str(out),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
 save('repeat-validation.json',old.verify(s,repeat,5400,True,True));print('V7 full minute and repeats verified',flush=True)
if __name__=='__main__':verify()
