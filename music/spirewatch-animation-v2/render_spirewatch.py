"""Spirewatch v2: fixed architecture, transported materials and connected city activity."""
from pathlib import Path
import argparse,json,hashlib,subprocess,time
import numpy as np,cv2
from PIL import Image,ImageDraw
import baseline as old
from baseline import byte,bounds,sha,smoothstep,event_amount
H=Path(__file__).parent
TAU=2*np.pi
def save(name,obj): (H/name).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')

class Spirewatch(old.Spirewatch):
 def __init__(self):
  super().__init__()
  assert sha(H/'baseline.py')==self.config['baseline_sha256']
  self.make_depth();self.make_city();self.make_lightning();self.make_display()
  self.layer_masks={k:v>0 for k,v in self.masks.items()}
  self.active=np.logical_or.reduce(list(self.layer_masks.values()))
 def crop(self,m,pad=0):
  a,b,z,d=bounds(m,pad);y,x=np.mgrid[b:d,a:z].astype(np.float32)
  return (a,b,z,d),m[b:d,a:z],x,y
 def make_atmosphere(self):
  super().make_atmosphere()
  # Wide inpainted architecture holes made rectangular streaks when transported.
  # Reconstruct only missing sky with normalized surrounding sky radiance, then
  # transition over a broad valid-sky annulus; architecture never enters sampling.
  _,_,(a,b,z,d),_,_,_,_,_=self.clouds[0]
  known=np.uint8((self.masks['clouds']+self.masks['mist'])[b:d,a:z]>.02)
  known=cv2.erode(known,np.ones((19,19),np.uint8)).astype(np.float32)
  original=self.base[b:d,a:z].astype(np.float32)
  denominator=cv2.GaussianBlur(known,(0,0),48,11)
  estimate=cv2.GaussianBlur(original*known[...,None],(0,0),48,11)/np.maximum(denominator[...,None],1e-6)
  old_clean=self.clouds[0][4]
  estimate=np.where((denominator>1e-5)[...,None],estimate,old_clean)
  distance=cv2.distanceTransform(known.astype(np.uint8),cv2.DIST_L2,5)
  blend=1-smoothstep(distance/36)
  clean=original*(1-blend[...,None])+estimate*blend[...,None]
  guard=np.ones(known.shape,np.float32)
  yy,xx=np.mgrid[b:d,a:z].astype(np.float32)
  # Keep the narrow original sky fringe around real masts from standing out as
  # a bright stationary cylinder against a darker passing cloud formation.
  for p,q,width in self.config['sky']['protected_lines']:
   if p[0]!=q[0] or p[1]<200:continue
   center=(p[1]+q[1])/2
   guard*=1-.86*np.exp(-((xx-p[0])/19)**2-((yy-center)/30)**2)
  self.clouds=[(name,c,roi,m*guard,clean,x,y,offset) for name,c,roi,m,_,x,y,offset in self.clouds]
 def install(self,name,m):
  m=m.astype(np.float32);m[m<.002]=0;self.masks[name]=m
  return self.crop(m,2)
 def make_falls(self):
  self.flow=[];total=np.zeros(self.shape,np.float32)
  for c in self.config['falls']:
   m=self.poly([c['polygon']],1.5);roi,mask,x,y=self.crop(m,2);a,b,z,d=roi
   p=self.base[b:d,a:z].astype(np.float32);hh,ww=mask.shape
   clean=cv2.inpaint(p.astype(np.uint8),np.uint8(mask<.3)*255,3,cv2.INPAINT_TELEA).astype(np.float32)
   # Reflect-tiled actual material travels downward, independent of channel outline.
   trim=max(2,hh//9);section=clean[trim:-trim]
   tile=np.concatenate([section,section[::-1]],axis=0).copy()
   level=np.maximum(cv2.GaussianBlur(clean,(0,0),.8,28),5)
   column=np.maximum(np.mean(tile,axis=0,keepdims=True),5)
   normalized=tile/column
   rng=np.random.default_rng(c['seed'])
   noise=rng.random((max(8,tile.shape[0]//9),max(5,ww//2)),dtype=np.float32)
   noise=cv2.resize(np.tile(noise,(3,1)),(ww,tile.shape[0]*3),interpolation=cv2.INTER_CUBIC)[tile.shape[0]:tile.shape[0]*2]
   thread=np.clip((noise-.5)*1.0+.95,.45,1.5)
   normalized*=.8+.2*thread[...,None]
   normalized/=np.maximum(normalized.mean(axis=0,keepdims=True),.1)
   normalized=cv2.GaussianBlur(normalized,(0,0),.40,2.2)
   self.flow.append((roi,mask,normalized,level,x-a,y-b,c,tile.shape[0]/c['period']))
   total=np.maximum(total,m)
  self.masks['falls']=total
 def make_water(self):
  self.ripples=[];total=np.zeros(self.shape,np.float32)
  for i,p in enumerate(self.config['water']['polygons']):
   m=self.poly([p],4);roi,mask,x,y=self.crop(m,4);a,b,z,d=roi
   depth=np.clip((y-490)/260,.12,1)
   strength=.67 if a>1300 else 1.0
   phases=[]
   for j in range(5):
    phase=(y-490)*(.29+j*.087)+(x-800)*(.032+j*.014)+i+j*2.13
    phases.append((phase.astype(np.float32),TAU*(2+j)/60,1/(j+1)))
   self.ripples.append((roi,mask,x-a,y-b,depth,strength,phases,self.base[b:d,a:z].astype(np.float32)))
   total=np.maximum(total,m)
  self.masks['water']=total
 def make_depth(self):
  cfg=self.config['new_mist'];self.depth=[];total=np.zeros(self.shape,np.float32)
  occlude=self.poly(self.config['sky']['exclusions'])
  occlude=cv2.dilate(occlude,np.ones((3,3),np.uint8))
  for i,poly in enumerate(cfg['regions']):
   m=self.poly([poly],20)*(1-occlude);roi,mask,x,y=self.crop(m,2);a,b,z,d=roi
   speed=cfg['speeds'][i];ww=round(speed*60);hh=d-b
   rng=np.random.default_rng(744+i);field=np.zeros((hh,ww),np.float32)
   for sx,sy,amp in [(8,5,.65),(19,10,.25),(42,19,.1)]:
    small=rng.random((sy,sx),dtype=np.float32)
    tex=cv2.resize(np.tile(small,(1,3)),(ww*3,hh),interpolation=cv2.INTER_CUBIC)[:,ww:ww*2]
    field+=tex*amp
   field=np.clip((field-.25)*1.7,0,1)
   self.depth.append((roi,mask,x-a,y-b,field,speed,cfg['strengths'][i]))
   total=np.maximum(total,m)
  self.masks['depth_mist']=total
  # Confined spray at photographed falls' lower ends; no invented plunge pool.
  spray=np.zeros(self.shape,np.float32)
  for x,y,rx,ry in [(286,352,19,8),(551,559,14,7),(557,590,9,3)]:
   spray=np.maximum(spray,np.exp(-((self.x-x)/rx)**2-((self.y-y)/ry)**2)*self.masks['falls'])
  self.spray=self.install('spray',spray)
 def make_city(self):
  rgb=self.base.astype(np.float32)
  cyan=np.clip((rgb[:,:,2]-rgb[:,:,0]-12)/40,0,1)*np.clip((rgb[:,:,1]-rgb[:,:,0]-6)/35,0,1)*np.clip((rgb[:,:,2]-45)/55,0,1)
  region=np.zeros(self.shape,np.float32)
  for a,b,z,d in self.config['tower']['emitter_regions']:region[b:d,a:z]=1
  silhouette=self.poly(self.config['sky']['exclusions'])
  core=cyan*region*silhouette
  halo=cv2.GaussianBlur(core,(0,0),3)*.45*silhouette
  self.tower=self.install('tower',np.maximum(core,halo))
  self.districts=[];total=np.zeros(self.shape,np.float32)
  for i,box in enumerate([[418,98,461,365],[648,291,679,480],[899,377,923,521],[1045,513,1084,758],[1398,630,1444,815],[1349,387,1365,435]]):
   a,b,z,d=box;m=np.zeros(self.shape,np.float32);m[b:d,a:z]=cyan[b:d,a:z]
   m=np.maximum(m,cv2.GaussianBlur(m,(0,0),2)*.20*silhouette)
   self.districts.append((i,*self.crop(m,3)));total=np.maximum(total,m)
  self.masks['city_glow']=total
  c=self.config['transit'];self.route=np.float32(c['route']);self.lengths=np.r_[0,np.cumsum(np.linalg.norm(np.diff(self.route,axis=0),axis=1))]
  route=np.zeros(self.shape,np.uint8);cv2.polylines(route,[self.route.astype(np.int32)],False,255,16)
  rm=cv2.GaussianBlur(route.astype(np.float32)/255,(0,0),2)
  rm*=1-self.poly(c['occluders']);self.transit=self.install('transit',rm)
 def make_lightning(self):
  self.flashes=[];total=np.zeros(self.shape,np.float32)
  sky=np.clip(self.masks['clouds']+self.masks['mist'],0,1)
  rgb=self.base.astype(np.float32);lum=rgb.mean(2)
  for c in self.config['lightning']['events']:
   px,py=c['center'];rx,ry=c['radius']
   g=np.exp(-((self.x-px)/rx)**2-((self.y-py)/ry)**2)
   shape=np.clip((cv2.GaussianBlur(lum,(0,0),3)-5)/45,.15,1)
   m=g*sky*shape
   bolt=np.zeros(self.shape,np.uint8);rng=np.random.default_rng(c['seed']);points=[]
   for j in range(9):points.append([int(px-38+j*9+rng.normal(0,4)),int(py-33+j*7+rng.normal(0,6))])
   cv2.polylines(bolt,[np.int32(points)],False,255,1,cv2.LINE_AA)
   branch=np.int32([points[4],[points[4][0]+20,points[4][1]-5],[points[4][0]+31,points[4][1]+2]])
   cv2.polylines(bolt,[branch],False,150,1,cv2.LINE_AA)
   # Cloud obscuration breaks the line into irregular partly hidden filaments.
   conceal=np.clip((cv2.GaussianBlur(lum,(0,0),1)-12)/28,0,1)
   bolt=cv2.GaussianBlur(bolt.astype(np.float32)/255,(0,0),.75)*sky*conceal
   m=np.maximum(m,bolt);roi,mask,x,y=self.crop(m,2);a,b,z,d=roi
   self.flashes.append((c,roi,mask,bolt[b:d,a:z]))
   total=np.maximum(total,m)
  self.masks['lightning']=total
  # Faint exterior response, clipped to mapped structures/water, never the room.
  exterior=self.poly(self.config['sky']['exclusions']);exterior[:,:640]=0;exterior[480:]=0
  response=exterior*np.clip(lum/100,0,.55)
  response=np.maximum(response,self.masks['water']*.12)
  self.flash_response=self.install('storm_response',response)
 def make_display(self):
  # Screen coordinates remain from this exact source, not another scene.
  c=self.config['screen'];self.display=self.crop(self.masks['screen'],2)
  m=self.poly([self.config['lamp']['desk_polygon']],8)
  m*=np.exp(-((self.x-269)/100)**2-((self.y-729)/24)**2)
  self.display_spill=self.install('screen_spill',m)
 def travel(self,t):
  for start,end,direction in self.config['transit']['events']:
   age=(t-start)/(end-start)
   if 0<=age<=1:return (age if direction==1 else 1-age),float(smoothstep(age/.08)*smoothstep((1-age)/.08)),direction
  return 0.,0.,1
 def flash_value(self,t,c):
  dt=(t-c['time'])%60
  if dt>1.25:return 0.
  # Broad main discharge and weak delayed cloud afterglow, smooth and localized.
  return c['strength']*(float(np.exp(-((dt-.22)/.13)**2))+.23*float(np.exp(-((dt-.62)/.23)**2)))*float(smoothstep(dt/.07)*smoothstep((1.25-dt)/.15))
 def frame(self,t,only=None,force_dark=False):
  t=float(t)%60;f=self.base.astype(np.float32)
  enabled=lambda k:only is None or only==k or (only=='atmosphere' and k in ('clouds','mist','depth_mist')) or (only=='city' and k in ('tower','city_glow','transit','screen','screen_spill','windows','walkway','lamp')) or (only=='storm' and k in ('lightning','storm_response'))
  for name,c,(a,b,z,d),m,clean,x,y,offset in self.clouds:
   if not enabled(name):continue
   moving=np.zeros_like(clean);weight_sum=np.zeros(m.shape,np.float32)
   for shift in (0,.5):
    age=(t/60+offset+shift)%1
    # Dominant phase keeps a cloud edge more legible than equal broad blending.
    weight=np.maximum(np.sin(np.pi*age),0)**6
    v=cv2.remap(clean,(x-c['speed']*60*(age-.5)).astype(np.float32),y,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT_101)
    moving+=v*weight[...,None];weight_sum+=weight
   moving/=weight_sum[...,None]
   blend=(m*c['strength'])[...,None]
   f[b:d,a:z]=f[b:d,a:z]*(1-blend)+moving*blend
  if enabled('depth_mist'):
   for (a,b,z,d),mask,x,y,field,speed,strength in self.depth:
    n=cv2.remap(field,((x-t*speed)%field.shape[1]).astype(np.float32),y,cv2.INTER_LINEAR,borderMode=cv2.BORDER_WRAP)
    alpha=mask*n*strength
    f[b:d,a:z]=f[b:d,a:z]*(1-alpha[...,None])+np.float32([70,99,112])*alpha[...,None]
  if enabled('falls'):
   for (a,b,z,d),mask,texture,level,x,y,c,speed in self.flow:
    mx=x+.40*np.sin(y*.078-TAU*t/c['period'])
    my=(y-t*speed)%texture.shape[0]
    material=cv2.remap(texture,mx.astype(np.float32),my.astype(np.float32),cv2.INTER_CUBIC,borderMode=cv2.BORDER_WRAP)
    water=(1+(np.clip(material,.25,2.0)-1)*.65)*level
    blend=mask[...,None]*.94
    f[b:d,a:z]=f[b:d,a:z]*(1-blend)+water*blend
  if enabled('spray'):
   (a,b,z,d),mask,x,y=self.spray
   wisps=.5+.25*np.sin(x*.45-y*.37-TAU*t/4)+.25*np.sin(x*.21+y*.55-TAU*t/5)
   f[b:d,a:z]+=mask[...,None]*wisps[...,None]*np.float32([4,7,8])
  if enabled('water'):
   for (a,b,z,d),mask,x,y,depth,strength,phases,plate in self.ripples:
    dx=np.zeros(mask.shape,np.float32);dy=dx.copy()
    for phase,omega,amp in phases:
     dx+=np.sin(phase-omega*t)*amp;dy+=np.cos(phase*.72-omega*t)*amp*.24
    dx*=depth*strength*.75*mask;dy*=depth*strength*.50*mask
    moving=cv2.remap(plate,x+dx,y+dy,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT_101)
    f[b:d,a:z]+=(moving-plate)*mask[...,None]
  if enabled('windows'):
   c=self.config['windows']
   for i,(a,b,z,d),m in self.windows:
    amt=1 if force_dark else event_amount(t,60,c['starts'][i],c['holds'][i],c['transition'])
    f[b:d,a:z]*=1-m[...,None]*amt*(1-c['floor'])
  if enabled('walkway'):
   c=self.config['walkway']
   for i,(a,b,z,d),m in self.walkway:
    f[b:d,a:z]*=1-m[...,None]*event_amount(t,60,c['starts'][i],c['hold'],.1)*c['depth']
  if enabled('lamp'):
   c=self.config['lamp'];(a,b,z,d),m=self.lamp
   f[b:d,a:z]*=1-m[...,None]*event_amount(t,60,c['start'],c['hold'],c['transition'])*c['depth']
  if enabled('tower'):
   (a,b,z,d),m,x,y=self.tower;band=np.zeros(m.shape,np.float32)
   for start,end,direction in self.config['tower']['events']:
    age=(t-start)/(end-start)
    if 0<=age<=1:
     center=410-365*age if direction=='up' else 45+365*age
     env=float(smoothstep(age/.1)*smoothstep((1-age)/.1))
     band+=np.exp(-((y-center)/self.config['tower']['band_height'])**2)*env
   f[b:d,a:z]+=m[...,None]*band[...,None]*np.float32([30,97,128])
  if enabled('city_glow'):
   for i,(a,b,z,d),m,x,y in self.districts:
    age=(t/20+i*.187)%1
    band=np.exp(-((y-(b+(d-b)*age))/35)**2)*float(np.sin(np.pi*age)**2)
    f[b:d,a:z]+=m[...,None]*band[...,None]*np.float32([12,38,52])
  progress,env,direction=self.travel(t)
  if enabled('transit') and env>0:
   (a,b,z,d),m,x,y=self.transit;light=np.zeros(m.shape,np.float32)
   for j in range(self.config['transit']['carriages']):
    distance=np.clip(progress*self.lengths[-1]-direction*j*16,0,self.lengths[-1])
    idx=min(np.searchsorted(self.lengths,distance,side='right')-1,len(self.route)-2);idx=max(0,idx)
    u=(distance-self.lengths[idx])/(self.lengths[idx+1]-self.lengths[idx]);pos=self.route[idx]*(1-u)+self.route[idx+1]*u
    perspective=.45+.55*(pos[0]-688)/983
    along=x-pos[0];across=y-pos[1]-.16*along
    body=np.exp(-(along/(6*perspective))**6-(across/(1.5*perspective))**4)
    glow=np.exp(-(along/(9*perspective))**2-(across/(3*perspective))**2)*.18
    light+=body+glow
   f[b:d,a:z]+=light[...,None]*m[...,None]*env*np.float32([65,142,172])
  if enabled('screen'):
   (a,b,z,d),m,x,y=self.display
   # Map tracing connected to each city passage; quiet scanning continues between.
   age=progress
   route=np.float32(self.config['screen']['route']);length=np.r_[0,np.cumsum(np.linalg.norm(np.diff(route,axis=0),axis=1))]
   dist=age*length[-1];idx=min(max(np.searchsorted(length,dist,side='right')-1,0),len(route)-2)
   u=(dist-length[idx])/(length[idx+1]-length[idx]);pos=route[idx]*(1-u)+route[idx+1]*u
   visibility=env
   marker=np.exp(-((x-pos[0])**2+(y-pos[1])**2)/8)*visibility
   screen=marker[...,None]*np.float32([65,142,160])
   for j,(px,py) in enumerate(route[[1,3,5]]):
    amt=event_amount(t,60,7+j*17,4,.65)
    rr=np.sqrt((x-px)**2+(y-py)**2)
    ring=np.exp(-((rr-4.0)/1.2)**2)*amt
    screen+=ring[...,None]*np.float32([12,38,45])
   panel=self.config['screen']['panel'];pa,pb,pz,pd=panel
   panelmask=(x>=pa)&(x<pz)&(y>=pb)&(y<pd)
   lum=self.base[b:d,a:z].astype(np.float32)
   details=np.clip((lum[:,:,2]-lum[:,:,0]-12)/30,0,1)*panelmask
   scan=np.exp(-((y-(pb+(t%10)/10*(pd-pb)))/8)**2)*float(np.sin(np.pi*(t%10)/10)**2)
   screen+=details[...,None]*scan[...,None]*np.float32([12,40,51])
   f[b:d,a:z]+=screen*m[...,None]
  if enabled('screen_spill'):
   (a,b,z,d),m,x,y=self.display_spill
   f[b:d,a:z]+=m[...,None]*env*np.float32([.4,1.2,1.8])
  flash=0.
  for c,roi,m,bolt in self.flashes:
   amp=self.flash_value(t,c);flash=max(flash,amp)
   if enabled('lightning') and amp>.0001:
    a,b,z,d=roi
    f[b:d,a:z]+=m[...,None]*amp*np.float32([25,33,42])+bolt[...,None]*amp*np.float32([19,25,30])
  if enabled('storm_response') and flash>.0001:
   (a,b,z,d),m,x,y=self.flash_response
   f[b:d,a:z]+=m[...,None]*flash*np.float32([6,9,12])
  assert np.isfinite(f).all();result=byte(f)
  active=self.active if only is None else np.logical_or.reduce([v for k,v in self.layer_masks.items() if enabled(k)])
  assert np.array_equal(result[~active],self.base[~active]),f'Protected pixels: {only}'
  return result
 def fingerprint(self):
  fp=super().fingerprint();fp['renderer_sha256']=sha(__file__);fp['baseline_sha256']=sha(H/'baseline.py');return fp

def samples(s):
 (H/'masks').mkdir(exist_ok=True)
 for name,m in s.masks.items():cv2.imwrite(str(H/'masks'/f'{name}.png'),byte(m*255))
 times=[0,4,8,9.62,16,20,32.1,34.62,40,48,52.62,56,59+29/30]
 for t in times:Image.fromarray(s.frame(t)).save(H/f'sample-{t:06.2f}s.png')
 Image.fromarray(s.frame(0,'windows',True)).save(H/'windows-forced-dim.png')
 report={}
 for name,m in s.layer_masks.items():
  assert np.array_equal(s.frame(0,name),s.frame(60,name))
  seam=float(np.abs(s.frame(-1/30,name)[m].astype(float)-s.frame(0,name)[m]).mean())
  ordinary=[float(np.abs(s.frame(t+1/30,name)[m].astype(float)-s.frame(t,name)[m]).mean()) for t in [0,1,4,8,9.55,14.3,19.5,31.8,32.1,34.55,38.7,40,51.2,52.55,57,59.9]]
  assert seam<=max(ordinary)*1.1+.01,(name,seam,max(ordinary))
  report[name]={'periodic_endpoint':True,'seam_mae':seam,'ordinary_max_sampled':max(ordinary),'pass':True}
 assert len({hashlib.sha256(s.frame(t)).hexdigest() for t in [0,20,40]})==3
 save('analytic-validation.json',{'fingerprint':s.fingerprint(),'layers':report,'distinct_0_20_40':True,'protected_pixels':'Asserted on every native frame','continuous_playback':False})
 save('mapped-window-apertures.json',s.window_records)
 print('Samples and analytical checks ready',flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',required=True,choices=['samples','isolated','preview','verify']);a=p.parse_args();s=Spirewatch()
 if a.stage=='samples':samples(s);return
 if a.stage=='isolated':
  records=[]
  for layer,seconds in [('falls',8),('water',8),('atmosphere',8),('storm',12),('city',16)]:
   path=H/f'{layer}-isolated-{seconds}s.mp4'
   if not path.exists():old.encode(s,path,seconds,layer)
   records.append({'layer':layer,**old.verify(s,path,seconds*30,False)})
  save('isolated-validation.json',{'fingerprint':s.fingerprint(),'clips':records});return
 out=H/'spirewatch-v2-preview-60s.mp4';repeat=H/'spirewatch-v2-three-loops-180s.mp4'
 if a.stage=='preview':old.encode(s,out,60)
 report=old.verify(s,out,1800);save('preview-validation.json',{'fingerprint':s.fingerprint(),**report})
 if not repeat.exists():subprocess.run([s.config['ffmpeg'],'-v','error','-n','-stream_loop','2','-i',str(out),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
 rr=old.verify(s,repeat,5400,True,True);save('repeat-validation.json',rr)
 save('delivery-v2.json',{'date':'2026-10-10','status':'Technically verified preview; user visual review pending','source':s.config['source'],'fingerprint':s.fingerprint(),'preview':str(out),'preview_validation':report,'repeat':str(repeat),'repeat_validation':rr,'user_motion_approved':False,'assistant_continuous_playback':False,'four_k':None,'audio':None})
 print('V2 minute and three-repeat review fully verified',flush=True)
if __name__=='__main__':main()
