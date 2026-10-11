"""Source-bound v3 lighting; fixed architecture, visible contrast and local response."""
import numpy as np
import cv2
from baseline import smoothstep,event_amount

class LightingV3:
 def make_lights(self):
  super().make_lights()
  cfg=self.config['lighting_v3'];rng=np.random.default_rng(cfg['seed'])
  rgb=self.base.astype(np.float32);used=np.zeros(self.shape,np.uint8)
  total=np.zeros(self.shape,np.float32);self.window_groups=[];self.window_records=[]
  for ri,(a,b,z,d) in enumerate(self.config['windows']['facade_regions']):
   p=rgb[b:d,a:z];warm=(p[:,:,0]>p[:,:,2]*1.10)&(p[:,:,0]>68)&(p[:,:,1]>40)
   # Identify small real apertures, then include every pixel of their bounding box,
   # including pale cores. Keep large facade/water regions out of this extraction.
   n,labels,stats,centers=cv2.connectedComponentsWithStats(warm.astype(np.uint8),8)
   candidates=[]
   for j in range(1,n):
    x,y,w,h,area=map(int,stats[j]);x+=a;y+=b
    if 2<=area<=55 and 1<=w<=12 and 1<=h<=10 and not used[y:y+h,x:x+w].any():
     candidates.append((x,y,w,h,area))
   candidates.sort(key=lambda q:q[4],reverse=True)
   for cluster in range(cfg['window_clusters_per_facade']):
    if not candidates:break
    anchor=candidates[0];ax,ay=anchor[:2]
    near=[q for q in candidates if abs(q[0]-ax)<38 and abs(q[1]-ay)<19][:cfg['window_max_per_cluster']]
    candidates=[q for q in candidates if q not in near]
    if not near:continue
    core=np.zeros(self.shape,np.float32)
    for x,y,w,h,_ in near:core[y:y+h,x:x+w]=1;used[y:y+h,x:x+w]=1
    spill=cv2.GaussianBlur(core,(0,0),1.5)*.24
    m=np.maximum(core,spill);m[m<.004]=0
    roi,mask,x,y=self.crop(m,2)
    start=float(rng.uniform(0,60));hold=float(rng.uniform(*cfg['window_hold_range']))
    second=(start+27+float(rng.uniform(-4,4)))%60
    self.window_groups.append((roi,mask,start,second,hold))
    self.window_records.append({'facade':ri,'apertures':[list(q[:4]) for q in near],'dim_start':start,'second_dim_start':second,'hold':hold,'floor':cfg['window_floor'],'spill_coupled':True})
    total=np.maximum(total,m)
  self.masks['windows']=total

 def make_city(self):
  super().make_city()
  # Source-mapped cyan masks remain unchanged; dynamic contrast replaces add-only
  # modulation, whose signal disappeared against already-bright emitters in v2.

 def render_windows(self,f,t,force_dark=False):
  cfg=self.config['lighting_v3']
  for (a,b,z,d),m,start,second,hold in self.window_groups:
   amount=1. if force_dark else max(event_amount(t,60,start,hold,cfg['window_transition']),event_amount(t,60,second,hold*.68,cfg['window_transition']))
   f[b:d,a:z]*=1-m[...,None]*amount*(1-cfg['window_floor'])
   # A slower warm recovery after each hold; no frame-wide exposure pulse.
   recovery=0. if force_dark else event_amount(t,60,(start+hold+.8)%60,2.4,.7)
   source=self.base[b:d,a:z].astype(np.float32)
   f[b:d,a:z]+=source*m[...,None]*recovery*.18

 def render_tower(self,f,t):
  cfg=self.config['lighting_v3'];(a,b,z,d),m,x,y=self.tower
  band=np.zeros(m.shape,np.float32);head=band.copy()
  for start,end,direction in self.config['tower']['events']:
   age=(t-start)/(end-start)
   if 0<=age<=1:
    center=410-365*age if direction=='up' else 45+365*age
    env=float(smoothstep(age/.08)*smoothstep((1-age)/.08))
    trail=center+(35 if direction=='up' else -35)
    band+=np.exp(-((y-trail)/cfg['tower_band_height'])**2)*env
    head+=np.exp(-((y-center)/20)**2)*env
  f[b:d,a:z]*=1-m[...,None]*(1-cfg['tower_floor'])*(1-np.clip(band,0,1))[...,None]
  f[b:d,a:z]+=m[...,None]*(band*.7+head*.6)[...,None]*np.float32(cfg['tower_color'])

 def render_districts(self,f,t):
  cfg=self.config['lighting_v3']
  for i,(a,b,z,d),m,x,y in self.districts:
   age=(t/(20 if i%2==0 else 30)+i*.187)%1
   direction=age if i%2==0 else 1-age
   env=float(np.sin(np.pi*age)**2)
   center=b+(d-b)*direction
   band=np.exp(-((y-center)/cfg['district_band_height'])**2)*env
   f[b:d,a:z]*=1-m[...,None]*(1-cfg['district_floor'])*(1-band)[...,None]
   f[b:d,a:z]+=m[...,None]*band[...,None]*np.float32(cfg['district_color'])

 def make_lightning(self):
  self.flashes=[];self.responses=[];total=np.zeros(self.shape,np.float32);rtotal=total.copy()
  sky=np.clip(self.masks['clouds']+self.masks['mist'],0,1)
  lum=self.base.astype(np.float32).mean(2)
  shape=.3+.7*np.clip((cv2.GaussianBlur(lum,(0,0),5)-6)/48,0,1)
  exterior=self.poly(self.config['sky']['exclusions']).astype(np.float32)
  exterior[:,:600]=0;exterior[510:]=0
  structure=exterior*np.clip(lum/80,.10,.75)
  for c in self.config['lightning']['events']:
   px,py=c['center'];rx,ry=c['radius']
   g=np.exp(-((self.x-px)/rx)**2-((self.y-py)/ry)**2)
   cloud=g*sky*shape
   raw=np.zeros(self.shape,np.uint8);rng=np.random.default_rng(c['seed']);points=[]
   drift=0.
   for j in range(30):
    drift=.72*drift+rng.normal(0,3.3)
    points.append([int(px-70+j*5+rng.normal(0,1.7)),int(py-29+j*2+drift)])
   cv2.polylines(raw,[np.int32(points)],False,235,1,cv2.LINE_AA)
   for j,sign in [(6,-1),(12,1),(20,-1)]:
    x,y=points[j];branch=[[x,y]]
    for k in range(1,8):branch.append([int(x+sign*k*4+rng.normal(0,1.8)),int(y-k*2+rng.normal(0,2.4))])
    cv2.polylines(raw,[np.int32(branch)],False,155,1,cv2.LINE_AA)
   conceal=np.clip((cv2.GaussianBlur(lum,(0,0),2)-10)/35,0,1)
   conceal*=.50+.32*np.sin(self.x*.063+self.y*.045)**2
   bolt=cv2.GaussianBlur(raw.astype(np.float32)/255,(0,0),.55)*sky*conceal
   cloud=np.maximum(cloud,cv2.GaussianBlur(bolt,(0,0),12)*2.5*sky)
   m=np.maximum(cloud,bolt);m[m<.002]=0
   roi,mask,x,y=self.crop(m,2);a,b,z,d=roi
   self.flashes.append((c,roi,mask,bolt[b:d,a:z]));total=np.maximum(total,m)
   local=np.exp(-((self.x-px)/(rx*1.35))**2)
   response=np.maximum(structure,self.masks['water']*.30)*local
   response[response<.002]=0
   self.responses.append((c,*self.crop(response,2)));rtotal=np.maximum(rtotal,response)
  self.masks['lightning']=total;self.masks['storm_response']=rtotal

 def flash_value(self,t,c):
  dt=(t-c['time'])%60
  if dt>1.8:return 0.
  lead=np.exp(-((dt-.20)/.14)**2)
  pulses=lead+.62*np.exp(-((dt-.51)/.16)**2)+.25*np.exp(-((dt-.95)/.36)**2)
  return c['strength']*float(pulses)*float(smoothstep(dt/.07)*smoothstep((1.8-dt)/.25))

 def render_storm_response(self,f,t):
  color=np.float32(self.config['lighting_v3']['storm_response_color'])
  for c,(a,b,z,d),m,x,y in self.responses:
   amp=self.flash_value(t,c)
   if amp>.0001:f[b:d,a:z]+=m[...,None]*amp*color
