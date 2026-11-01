"""V6: visible mountain fog, darker light-off states, mast beacons and a distant planet."""
from pathlib import Path
import sys,json,hashlib,time,subprocess,argparse
import cv2,numpy as np
from PIL import Image
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'empty-junction-animation-v5'))
import render_v5 as v5
# V5's init writes diagnostic assets. Route them into this version, preserving V5 bytes.
v5.H=H
cv2.setNumThreads(4)
def save(name,obj):(H/name).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
smooth=v5.smooth;byte=v5.byte

class Scene(v5.Scene):
 def __init__(self):
  super().__init__();self.prepare_planet();self.prepare_beacons()
  self.active=np.maximum.reduce(list(self.masks.values()))>0
 def prepare_lights(self):
  super().prepare_lights();updated=[]
  for name,m,start,hold,depth,transition in self.lights:
   if isinstance(name,dict):
    name=json.loads(json.dumps(name))
    for e in name['events']:e['depth']=.90 if name['name']!='door_lamp' else .85
   else:depth=.94 if name!='cabin' else .82
   updated.append((name,m,start,hold,depth,transition))
  self.lights=updated
  self.light_regions=[(n,*self.previous.crop(m),a,b,c,d) for n,m,a,b,c,d in self.lights]
 def prepare_mist(self):
  super().prepare_mist()
  # Keep the detailed lower ridgeline occluders; give fog more vertical and lateral body.
  far=[[710,282],[802,273],[878,282],[944,288],[1004,281],[1077,280],[1124,292],
       [1112,349],[1095,352],[1078,348],[1066,354],[1047,352],[1034,361],[1018,366],
       [1001,366],[991,363],[972,361],[956,350],[942,348],[927,344],[911,345],[900,337],
       [882,339],[871,332],[855,332],[843,320],[828,319],[802,321],[776,312],[754,315],[731,307],[713,309]]
  middle=[[508,319],[602,303],[686,307],[757,320],[832,329],[910,339],[982,350],[1055,360],[1081,383],
       [1061,414],[1006,418],[960,420],[940,414],[921,412],[903,410],[885,414],[865,413],
       [850,404],[828,405],[805,401],[789,392],[770,390],[749,392],[733,385],[710,387],
       [688,380],[666,379],[644,370],[621,370],[600,359],[581,361],[562,351],[536,347],[516,335]]
  new=[]
  for old,poly,center,height,opacity,col in zip(self.fogs,[far,middle],[325,357],[34,31],[.82,.67],[[183,193,209],[170,183,202]]):
   name,_,_,_,_,tex,_,_,speed,_,_=old
   mask=self.polygon(poly,3)
   points=np.float32(poly);lo,hi=points[:,0].min(),points[:,0].max()
   mask*=smooth((self.x-lo)/55)*smooth((hi-self.x)/55)
   # Upper fog silhouette dissolves into clear air, rather than tracing the support polygon.
   mask*=smooth((self.y-(center-height*1.5))/24)
   mast=self.polygon([[954,385],[975,385],[975,433],[954,433]],.5)*smooth((100-self.src.mean(2))/28)
   mask*=1-mast;mask[mask<.002]=0
   self.masks[name]=mask;a,b,z,d=self.previous.crop(mask)[0]
   new.append((name,(a,b,z,d),self.x[b:d,a:z],self.y[b:d,a:z],mask[b:d,a:z],tex,center,height,speed,opacity,np.float32(col)))
  self.fogs=new
 def mist(self,t,item):
  name,roi,x,y,mask,tex,center,height,speed,opacity,col=item
  age=(t+(17 if name=='far_mist' else 39))%60;renew=float(smooth((age-48)/12));field=np.zeros_like(x)
  for a,w in [(age,1-renew),(age-60,renew)]:
   if not w:continue
   u=x-speed*(a-30)+130
   # Rounder billows and small internal curls; still forward advected, not opacity-only breathing.
   v=(y-center)*1.15+180+7*np.sin(u/95+a*.018)+3*np.sin(u/46-a*.013)
   field+=cv2.remap(tex,(u*1.25).astype(np.float32),v.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)*w
  centerline=center+9*np.sin(x/107)+3*np.sin(x/43)
  envelope=np.exp(-.5*((y-centerline)/height)**2)
  density=smooth((field-.27)/.40)*envelope
  alpha=(1-np.exp(-density*opacity*1.9))*mask
  return alpha,col
 def prepare_planet(self):
  asset=Image.open(H/'ringed-planet-rgba.png').convert('RGBA')
  assert asset.getextrema()[3][0]==0 and asset.getextrema()[3][1]==255
  # The generated RGBA remains unchanged. Placement and haze are renderer parameters.
  bounds=Image.fromarray(np.uint8(np.array(asset.getchannel('A'))>4)*255).getbbox()
  asset=asset.crop(bounds);width=196;height=round(asset.height*width/asset.width)
  asset=asset.resize((width,height),Image.Resampling.LANCZOS)
  rgba=np.array(asset).astype(np.float32);cx,cy=1031,76;x0=round(cx-width/2);y0=round(cy-height/2)
  self.planet_roi=(x0,y0,x0+width,y0+height)
  self.planet_alpha=rgba[:,:,3]/255*.52
  # Blend celestial colour toward local atmospheric radiance, preserving faint ring readability.
  sky=self.src[y0:y0+height,x0:x0+width]
  self.planet_color=rgba[:,:,:3]*.80+sky*.20
  self.planet_alpha*=self.masks['clouds'][y0:y0+height,x0:x0+width]
  m=np.zeros((self.h,self.w),np.float32);m[y0:y0+height,x0:x0+width]=self.planet_alpha
  self.masks['planet']=m
 def prepare_beacons(self):
  self.beacons=[]
  for name,x,y,period,phase in [('cabin_tall',273,214.4,6,.65),('cabin_short',369,271.3,5,2.1),('hall_mast',968.1,386.5,4,1.2)]:
   r2=(self.x-x)**2+(self.y-y)**2
   core=np.exp(-r2/(2*1.22**2));halo=np.exp(-r2/(2*4.4**2))*.30
   core[r2>16]=0;halo[r2>150]=0
   m=np.maximum(core,halo);self.masks['beacon_'+name]=m
   roi,local=self.previous.crop(m);a,b,z,d=roi
   self.beacons.append((name,roi,core[b:d,a:z],halo[b:d,a:z],period,phase))
  save('beacon-plan.json',{'source_native_dimensions':[1672,941],'anchors':[{'name':n,'roi':list(roi),'period_seconds':p,'phase_seconds':phase} for n,roi,c,h,p,phase in self.beacons],'pulse':'Soft 0.18s rise, 0.28s hold, 0.25s fall; independent periods and phases'})
 def frame(self,t,only=None):
  t=float(t)%60;f=self.src.copy()
  if only in (None,'planet'):
   a,b,z,d=self.planet_roi;alpha=self.planet_alpha
   f[b:d,a:z]=f[b:d,a:z]*(1-alpha[...,None])+self.planet_color*alpha[...,None]
  if only in (None,'clouds'):
   # Atmospheric cloud texture remains in front of the distant planet.
   f[:350]+=self.clouds(t)*self.masks['clouds'][:350,:,None]
  for item in self.fogs:
   if only not in (None,'mist'):continue
   a,b,z,d=item[1];alpha,col=self.mist(t,item)
   f[b:d,a:z]=f[b:d,a:z]*(1-alpha[...,None])+col*alpha[...,None]
  if only in (None,'windows'):
   for name,roi,m,start,hold,depth,transition in self.light_regions:
    amount=self.previous.amount(t,name['events']) if isinstance(name,dict) else self.previous.amount(t,[{'start':start,'hold':hold,'depth':depth,'transition':transition}])
    a,b,z,d=roi;emission=np.maximum(f[b:d,a:z]-np.float32([14,19,28]),0)
    f[b:d,a:z]-=emission*m[...,None]*amount
  if only is None:
   for name,roi,mask,fields in self.retained:
    f=self.previous.apply_extra(f,t,name,roi,mask,fields,self.previous.wind_envelope(t) if name=='yard_powder' else 1)
  if only in (None,'beacons'):
   for name,roi,core,halo,period,phase in self.beacons:
    age=(t+phase)%period;pulse=float(smooth(age/.18)*smooth((.71-age)/.25))
    a,b,z,d=roi;local=f[b:d,a:z]
    alpha=core*pulse*.97
    local=local*(1-alpha[...,None])+np.float32([255,55,31])*alpha[...,None]
    local+=halo[...,None]*np.float32([130,12,5])*pulse
    f[b:d,a:z]=local
  result=byte(f);assert np.array_equal(result[~self.active],self.base[~self.active]);return result

def samples(s):
 (H/'masks').mkdir(exist_ok=True)
 for n,m in s.masks.items():Image.fromarray(byte(m*255)).save(H/'masks'/f'{n}.png')
 times=[0,1.6,3.1,5.7,10,12,20,32,44,56]
 for t in times:Image.fromarray(s.frame(t)).save(H/f'sample-{t:04.1f}.png')
 for layer in ['mist','windows','beacons','planet']:
  for t in [0,5.7,12,32]:Image.fromarray(s.frame(t,layer)).save(H/f'v6-{layer}-{t:04.1f}.png')
 checks={}
 for layer in ['clouds','mist','windows','beacons',None]:
  assert np.array_equal(s.frame(0,layer),s.frame(60,layer))
  vals=[float(np.abs(s.frame(t+1/30,layer).astype(float)-s.frame(t,layer)).mean()) for t in [-1/30,0,.1,.5,5.7,8,20,32,44,56]]
  assert vals[0]<=max(vals[1:])*1.3+.002,(layer,vals)
  checks[str(layer)]={'periodic':True,'seam_mae':vals[0],'ordinary_max':max(vals[1:])}
 # Show actual fog and off-state change at display size, with no gain amplification.
 save('analytic-validation.json',{'source_sha256':sha(s.previous.source_path),'planet_sha256':sha(H/'ringed-planet-rgba.png'),'layers':checks,'protected_pixels_asserted':True,'user_approved':False})
 save('scene-plan-v6.json',{'source':str(s.previous.source_path),'planet':{'asset':'ringed-planet-rgba.png','roi':list(s.planet_roi),'opacity':.52,'colour_haze_mix':.20},'fog':'Expanded far and middle banks, brighter atmospheric colour, stronger optical thickness, rolling forward-advection and terrain occlusion','light_off_depth':{'windows':.94,'cabin':.82,'practicals':.90,'door_lamp':.85},'ambient_floor_rgb':[14,19,28],'period_seconds':60,'retained':['source cloud transport','grille condensation','wind-timed near powder'],'beacons':'beacon-plan.json'})

def render(s,seconds=30):
 out=H/f'Empty-Junction-v6-{seconds}s-720p.mp4';p=v5.encoder(out);start=time.time()
 try:
  for i in range(seconds*30):
   p.stdin.write(cv2.resize(s.frame(i/30),(1280,720),interpolation=cv2.INTER_AREA).tobytes())
   if i%150==0:print('v6',i,'/',seconds*30,'elapsed',round(time.time()-start),flush=True)
 finally:p.stdin.close()
 assert p.wait()==0
 save('render-record.json',{'file':out.name,'sha256':sha(out),'frames':seconds*30,'seconds':seconds,'renderer_sha256':sha(__file__),'base_renderer_sha256':sha(Path(v5.__file__)),'qp':0})

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['samples','render'],required=True);p.add_argument('--seconds',type=int,default=30);a=p.parse_args();s=Scene()
 if a.stage=='samples':samples(s)
 else:render(s,a.seconds)
