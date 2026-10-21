"""V4 connected-city choreography; exact source geometry and minute phase."""
import numpy as np
import cv2
from lighting_layers import LightingV3
from baseline import smoothstep,event_amount
TAU=2*np.pi

class LightingV4(LightingV3):
 def make_lightning(self):
  super().make_lightning()
  # Keep broad cloud response; obscure the thin branches more deeply in cloud.
  self.flashes=[(c,roi,m,bolt*.32) for c,roi,m,bolt in self.flashes]

 def make_city(self):
  super().make_city()
  cfg=self.config['lighting_v4'];self.activity=float(cfg['music_activity'])
  # Existing cyan material, not invented full-facade illumination.
  core=self.masks['tower'].copy()
  corona=cv2.GaussianBlur(core,(0,0),5)*1.8
  corona*=self.poly([[[1195,24],[1340,24],[1340,435],[1195,435]]],6)
  self.corona=self.install('tower_corona',corona)
  crown=core*np.exp(-((self.y-105)/62)**2)
  self.crown=self.install('tower_crown',np.maximum(crown,cv2.GaussianBlur(crown,(0,0),3)*.45))
  self.reflection=self.install('light_reflections',self.masks['water'].copy())
  # Faint defocused lamp-shaped reflection within lower-left glazing only.
  glass=self.poly([[[270,495],[390,500],[440,675],[276,658]]],18)
  bar=np.exp(-((self.x-314)/26)**4-((self.y-553)/3.8)**2)
  halo=np.exp(-((self.x-314)/35)**2-((self.y-556)/17)**2)*.11
  self.glass=self.install('glass_reflection',(bar*.25+halo)*glass)
  (a,b,z,d),m,x,y=self.transit
  self.route_y=np.interp(x,self.route[:,0],self.route[:,1]).astype(np.float32)
  self.route_distance=np.interp(x,self.route[:,0],self.lengths).astype(np.float32)
  self.water_data=[]
  for roi,m,x,y,*_ in self.ripples:
   a,b,z,d=roi
   # Static source texture modulates moving light; no smooth painted columns.
   l=self.base[b:d,a:z].astype(np.float32).mean(2)
   details=.3+.7*np.clip(l/55,0,1)
   self.water_data.append((roi,m,x+a,y+b,details))
  self.screen_path=np.float32(self.config['screen']['route'])
  self.screen_lengths=np.r_[0,np.cumsum(np.linalg.norm(np.diff(self.screen_path,axis=0),axis=1))]

 def tower_state(self,t):
  charge=event_amount(t,60,.5,5,1.4)+.65*event_amount(t,60,33,5,1.2)
  crown=event_amount(t,60,self.config['lighting_v4']['crown_start'],self.config['lighting_v4']['crown_hold'],self.config['lighting_v4']['crown_transition'])
  return charge,crown

 def render_tower(self,f,t):
  cfg=self.config['lighting_v4'];(a,b,z,d),m,x,y=self.tower
  band=np.zeros_like(m);head=band.copy();charge,crown=self.tower_state(t)
  for start,end,direction in self.config['tower']['events']:
   # Small phase offsets separate real channels while maintaining one cycle.
   age=(t-start-(x-1277)*.018)/(end-start)
   env=smoothstep(age/.12)*smoothstep((1-age)/.12)
   center=410-365*age if direction=='up' else 45+365*age
   band+=np.exp(-((y-center-(30 if direction=='up' else -30))/cfg['tower_band_height'])**2)*env
   head+=np.exp(-((y-center)/14)**2)*env
  basecharge=charge*np.exp(-((y-392)/42)**2)
  level=(.18+band*.95+head*.40+basecharge*.55)*self.activity
  f[b:d,a:z]*=1-m[...,None]*(1-cfg['tower_floor'])*(1-np.clip(band,0,1))[...,None]
  f[b:d,a:z]+=m[...,None]*level[...,None]*np.float32(cfg['tower_color'])

 def district_amount(self,t,i):
  cfg=self.config['lighting_v4'];delay=cfg['district_delays'][i]
  return max(event_amount(t,60,(s+delay)%60,cfg['district_hold'],cfg['district_transition']) for s in cfg['district_starts'])*self.activity

 def render_districts(self,f,t):
  cfg=self.config['lighting_v4']
  for i,(a,b,z,d),m,x,y in self.districts:
   amount=self.district_amount(t,i)
   start=(cfg['district_starts'][0]+cfg['district_delays'][i])%60
   second=(cfg['district_starts'][1]+cfg['district_delays'][i])%60
   dt=min((t-start)%60,(t-second)%60)
   age=np.clip(dt/(cfg['district_hold']+2*cfg['district_transition']),0,1)
   center=d-(d-b)*age
   band=np.exp(-((y-center)/48)**2)*amount
   f[b:d,a:z]*=1-m[...,None]*.12*(1-amount)
   f[b:d,a:z]+=m[...,None]*(.10+amount*.3+band*.75)[...,None]*np.float32(cfg['district_color'])

 def vehicle(self,t):
  progress,env,direction=self.travel(t)
  distance=progress*self.lengths[-1]
  px=float(np.interp(distance,self.lengths,self.route[:,0]))
  py=float(np.interp(distance,self.lengths,self.route[:,1]))
  color=np.float32([185,104,30] if direction<0 else [55,154,192])
  return progress,env*self.activity,direction,distance,px,py,color

 def render_transit_v4(self,f,t):
  progress,env,direction,distance,px,py,color=self.vehicle(t)
  if env<1e-5:return
  (a,b,z,d),m,x,y=self.transit
  perspective=np.clip(.45+.55*(x-688)/983,.4,1)
  cross=y-self.route_y-(1.6 if direction<0 else -1.1)
  behind=(distance-self.route_distance)*direction
  trail=np.exp(-np.maximum(behind,0)/(34*perspective))*smoothstep((behind+2)/4)*smoothstep((105*perspective-behind)/20)
  line=np.exp(-(cross/(.85*perspective+.25))**2)
  head=np.exp(-((self.route_distance-distance)/(4.8*perspective))**2-(cross/(1.4*perspective+.3))**2)
  # Tail stays attached to the moving source and follows the mapped track.
  light=(trail*line*.72+head*.95)*env*m
  glow=cv2.GaussianBlur(light,(0,0),1.7)*.36*m
  f[b:d,a:z]+=(light+glow)[...,None]*color

 def render_screen_v4(self,f,t):
  (a,b,z,d),m,x,y=self.display
  progress,env,direction,*_=self.vehicle(t)
  # Source map path remains intact. One tiny marker moves with each real passage.
  dist=progress*self.screen_lengths[-1]
  px=np.interp(dist,self.screen_lengths,self.screen_path[:,0]);py=np.interp(dist,self.screen_lengths,self.screen_path[:,1])
  marker=np.exp(-((x-px)**2+(y-py)**2)/4.5)*env
  details=np.clip((self.base[b:d,a:z,2].astype(float)-self.base[b:d,a:z,0].astype(float)-5)/35,0,1)
  sweep=.5+.5*np.cos(TAU*(t/20-(x-146)/170))
  scan=np.maximum(sweep-.92,0)/.08
  light=marker[...,None]*np.float32([46,136,170])+details[...,None]*scan[...,None]*np.float32([3,12,17])
  for j,(px,py) in enumerate(self.screen_path[[1,3,5]]):
   amount=self.district_amount(t,j+1)
   point=np.exp(-((x-px)**2+(y-py)**2)/2.2)
   light+=point[...,None]*amount*np.float32([46,104,122])
  # Retain the source's small right-hand panel; grouped acknowledgements only.
  pa,pb,pz,pd=self.config['screen']['panel']
  panel=(x>=pa)&(x<pz)&(y>=pb)&(y<pd)
  scanrow=np.exp(-((y-(pb+(pd-pb)*(t%15)/15))/5)**2)*np.sin(np.pi*(t%15)/15)**2
  light+=(panel*details*scanrow)[...,None]*np.float32([8,28,33])
  f[b:d,a:z]+=light*m[...,None]

 def render_new_layers(self,f,t,enabled):
  cfg=self.config['lighting_v4'];charge,crown=self.tower_state(t)
  if enabled('tower_corona'):
   (a,b,z,d),m,x,y=self.corona
   band=np.zeros_like(m)
   for start,end,direction in self.config['tower']['events']:
    age=(t-start)/(end-start)
    if 0<=age<=1:
     center=410-365*age if direction=='up' else 45+365*age
     band+=np.exp(-((y-center)/55)**2)*float(smoothstep(age/.12)*smoothstep((1-age)/.12))
   f[b:d,a:z]+=m[...,None]*(.10+.6*band[...,None])*np.float32([8,40,55])*self.activity
  if enabled('tower_crown'):
   (a,b,z,d),m,x,y=self.crown
   f[b:d,a:z]+=m[...,None]*crown*np.float32([42,115,145])*self.activity
  if enabled('light_reflections'):
   progress,env,direction,distance,px,py,color=self.vehicle(t)
   for (a,b,z,d),m,x,y,details in self.water_data:
    ripple=(.5+.5*np.sin(y*.78+x*.018-TAU*t/5))**3
    ripple*=.65+.35*np.sin(y*.19-x*.045+TAU*t/12)**2
    dx=x-px-2.2*np.sin(y*.27+TAU*t/10)
    spread=12+np.maximum(y-py,0)*.12
    trail=np.exp(-(dx/spread)**2)*np.exp(-np.maximum(y-py,0)/180)*env
    tower=np.exp(-((x-1280)/105)**2)*(.16*charge+.35*crown)*self.activity
    f[b:d,a:z]+=(m*details*ripple*cfg['reflection_strength'])[...,None]*(trail[...,None]*color*.46+tower[...,None]*np.float32([16,55,70]))
  if enabled('glass_reflection'):
   (a,b,z,d),m,x,y=self.glass;c=self.config['lamp']
   lamp=1-event_amount(t,60,c['start'],c['hold'],c['transition'])*c['depth']
   f[b:d,a:z]+=m[...,None]*lamp*cfg['glass_strength']*np.float32([28,17,7])
