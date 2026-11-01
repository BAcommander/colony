"""Deepwell v2: source-bound refinement of all scene layers, fixed photographic plate."""
from pathlib import Path
import sys,json,hashlib,argparse,time,subprocess,platform
sys.dont_write_bytecode=True
sys.path.insert(0,r'C:\AI\ComfyUI\venv\Lib\site-packages')
H=Path(__file__).resolve().parent;B=H/'baseline-snapshot'
sys.path.insert(0,str(B))
import render_deepwell as baseline
import cv2,numpy as np
from PIL import Image,ImageDraw
from ambient_effects import smoothstep,event_amount
from render_floodplain import ChannelSurface
from review_tools import encode,decode_verify
from weather_refinement import render_weather
cv2.setNumThreads(4)
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_json(name,value):(H/name).write_text(json.dumps(value,indent=2)+'\n')
def box(mask):
 y,x=np.nonzero(mask>0)
 return (int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1))
def cut(a,r):x0,y0,x1,y1=r;return a[y0:y1,x0:x1]
def crop_blend(frame,r,colour,alpha):
 x0,y0,x1,y1=r;p=frame[y0:y1,x0:x1];frame[y0:y1,x0:x1]=p*(1-alpha[...,None])+np.asarray(colour,np.float32)*alpha[...,None]
def sun_state(t):return .5+.35*np.sin(2*np.pi*t/20-.8)+.15*np.sin(4*np.pi*t/20+.5)

class BrineSurface(ChannelSurface):
 def __init__(self,plate,mask,c,origin,dc):
  super().__init__(plate,mask,c,origin);rng=np.random.default_rng(c['seed']);self.waves=[];self.wave_filters=[];self.speed_deviations=[]
  for i in range(c['components']):
   cross=i<dc['cross_count'];theta=float(rng.normal(dc['cross_theta'] if cross else dc['main_theta'],dc['cross_spread'] if cross else dc['main_spread']))
   length=float(rng.uniform(*c['wavelength_range']));k=2*np.pi/length;dx=float(np.cos(theta));dy=float(np.sin(theta))
   phase=np.float32(k)*(np.float32(dx)*self.world_x+np.float32(dy)*self.world_z)+np.float32(rng.uniform(0,2*np.pi))
   natural=float(np.sqrt(9.81*k)*c['time_scale']);omega=2*np.pi*max(1,round(natural*20/(2*np.pi)))/20
   amp=float((length/c['wavelength_range'][1])**.4)*(dc['cross_strength'] if cross else 1)
   py,px=np.gradient(phase);filtered=np.exp(np.float32(-.5*c['sampling_filter_pixels']**2)*(px*px+py*py)).astype(np.float32)
   self.waves.append((phase.astype(np.float32),float(omega),amp,(dx,dy)));self.wave_filters.append(filtered);self.speed_deviations.append(omega/natural-1)
  self.norm=float(sum(q[2]**2 for q in self.waves)**.5);self.dc=dc
  self.depth=np.clip(self.y/max(float(self.y.max()),1),0,1)
 def frame(self,t):
  effective=t+self.dc['gust_time_offset_seconds']*np.sin(2*np.pi*t/20)
  nx=np.zeros_like(self.x);nz=np.zeros_like(self.x)
  for (phase,omega,amp,(dx,dy)),filtered in zip(self.waves,self.wave_filters):
   slope=np.cos(phase-np.float32(omega*effective))*np.float32(amp)*filtered;nx+=slope*np.float32(dx);nz+=slope*np.float32(dy)
  nx/=self.norm;nz/=self.norm;displacement=self.c['displacement_scale']*self.edge_damping
  mx=self.x+nx*(9+9*self.depth)*displacement;my=self.y+nz*(6+9*self.depth)*displacement
  reflected=cv2.remap(self.reflection,mx.astype(np.float32),my.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
  orientation=np.tanh(nz*.85+nx*.25);glint=np.exp(-((nx-.18)**2+(nz+.48)**2)/self.c['highlight_roughness'])
  sunlight=1+self.dc['sun_glint_variation']*(sun_state(t)-.5)
  surface=reflected*(1+orientation[...,None]*self.c['reflection_contrast'])+(glint-.16)[...,None]*self.c['specular_strength']*sunlight*np.float32([.82,.93,1])
  a=self.mask[...,None];return np.clip(self.plate*(1-a)+surface*a,0,255)

class DeepwellV2(baseline.Deepwell):
 def __init__(self):
  started=time.time();super().__init__();self.old_config=self.config;c=json.loads((H/'scene-plan-v2.json').read_text());self.config=c
  assert digest(H/c['source']['path'])==c['source']['sha256'];self.duration=c['duration']
  # All full-frame masks are built once. Repeated frame work is restricted to
  # small physical regions, particularly practical lights and instrument panes.
  self.masks={'water':self.masks['water']};self.water_roi=tuple(c['water']['roi']);a,b,z,d=self.water_roi
  self.water=BrineSurface(self.base[b:d,a:z],self.masks['water'][b:d,a:z],c['water'],(a,b),c['water_direction'])
  self.sky_roi=tuple(self.old_config['sky']['roi']);a,b,z,d=self.sky_roi
  sky=self.feather(self.poly([self.old_config['sky']['polygon']]),c['sky']['feather']);sx,sy,rx,ry=c['sky']['planet_ellipse']
  distance=np.sqrt(((self.x-sx)/rx)**2+((self.y-sy)/ry)**2)
  guard=1-smoothstep((distance-.985)/.045);self.planet_body=distance<=1
  self.sky_mask=cut(sky*(1-guard),self.sky_roi).astype(np.float32)
  self.masks['sky']=sky*(1-guard)
  cy,cx=self.cy,self.cx;global_y=cy+b
  self.near_weight=smoothstep((175-global_y)/95).astype(np.float32)
  self.cloud_base=self.clean.copy();self.cloud_original=self.clean.copy();self.offset=(cy+b)/860+(cx+a)/3000+.23
  lum=self.clean.mean(2);broad=cv2.GaussianBlur(lum,(0,0),22,sigmaY=12)
  self.front_texture=np.clip((cv2.GaussianBlur(lum,(0,0),3.5)-broad+2)/9,0,1).astype(np.float32)
  band=np.exp(-((global_y-c['sky']['veil_band_center_y'])/c['sky']['veil_band_radius_y'])**2)
  self.veil_mask=cut(sky,self.sky_roi)*band.astype(np.float32);self.masks['planet_veil']=np.zeros_like(sky);self.masks['planet_veil'][b:d,a:z]=self.veil_mask
  # Exclude the real pipeline and its supports from basin overlays. They remain
  # stable source objects in front of the moving distant air.
  pipeline=np.zeros((self.h,self.w),np.uint8)
  cv2.polylines(pipeline,[np.int32([[854,334],[1040,311],[1230,288],[1410,268],[1671,240]])],False,1,15)
  for x,y,fy in [(901,329,347),(959,322,342),(1022,314,339),(1087,306,333),(1154,298,328),(1223,290,320)]:cv2.line(pipeline,(x,y),(x,fy),1,9)
  pipeline=cv2.dilate(pipeline,np.ones((3,3),np.uint8));self.pipeline=pipeline>0
  self.weather=[]
  for ac in c['atmosphere']:
   r=tuple(ac['roi']);a,b,z,d=r;mask=self.feather(self.poly([ac['polygon']]),ac['feather']);mask[pipeline>0]=0
   m=cut(mask,r);yy,xx=np.mgrid[:d-b,:z-a].astype(np.float32);center=ac['center_y']+ac.get('slope',0)*(xx+a-(a+z)/2)
   envelope=np.exp(-((yy+b-center)/ac['height'])**2).astype(np.float32)
   m*=envelope;m[m<.001]=0;full=np.zeros_like(sky);full[b:d,a:z]=m;self.masks[ac['name']]=full
   texture=self.noise_texture((d-b,z-a),ac['seed'])
   self.weather.append((ac,r,m,texture,xx,yy))
  for ac in c['surface_drift']:
   r=tuple(ac['roi']);a,b,z,d=r;yy,xx=np.mgrid[:d-b,:z-a].astype(np.float32);route=np.float32(ac['route']);center=np.interp(xx+a,route[:,0],route[:,1]).astype(np.float32)
   envelope=np.exp(-((yy+b-center)/ac['width'])**2)*smoothstep((xx-5)/23)*smoothstep((z-a-5-xx)/23)
   envelope*=np.float32(pipeline[b:d,a:z]==0)
   envelope[envelope<.001]=0;full=np.zeros_like(sky);full[b:d,a:z]=envelope;self.masks[ac['name']]=full
   texture=self.noise_texture((d-b,z-a),ac['seed']);self.weather.append((ac,r,envelope.astype(np.float32),texture,xx,yy))
  self.windows=[];full=np.zeros_like(sky)
  for lc in c['lights']:
   m=self.aperture([lc['polygon']]);r=box(m);self.windows.append((lc,r,cut(m,r)));full=np.maximum(full,m)
  self.masks['lights']=full
  lc=self.old_config['lamp'];rgb=self.base.astype(np.float32);warm=np.clip((rgb[:,:,0]-rgb[:,:,2]-10)/90,0,1)
  core=self.aperture([lc['core']]);x,y=lc['spill_center'];rx,ry=lc['spill_radius']
  spill=np.exp(-((self.x-x)/rx)**2-((self.y-y)/ry)**2)*self.feather(self.poly([lc['wall_polygon']]),10)*warm*.55
  desk=self.feather(self.poly([c['lamp']['desk_polygon']]),22)*c['lamp']['desk_strength']
  lamp=np.maximum(core,spill*c['lamp']['spill_gain']);lamp=np.maximum(lamp,desk);lamp[lamp<.001]=0
  self.masks['lamp']=lamp;self.lamp_roi=box(lamp);self.lamp_mask=cut(lamp,self.lamp_roi)
  status=self.aperture([c['status']['polygon']]);spill=cv2.GaussianBlur(status,(0,0),2)*.14;status=np.maximum(status,spill);status[status<.002]=0
  self.masks['status']=status;self.status_roi=box(status);self.status_mask=cut(status,self.status_roi)
  dc=c['daylight'];dm=self.feather(self.poly([dc['table_polygon']]),24)*dc['table_strength']+self.feather(self.poly([dc['ledge_polygon']]),4)*dc['ledge_strength'];dm[dm<.0002]=0
  self.masks['daylight']=dm;self.day_roi=box(dm);self.day_mask=cut(dm,self.day_roi)
  self.masks['screen']=self.aperture([c['screen']['quad']]);self.ui_roi=(263,350,333,413);a,b,z,d=self.ui_roi;iw,ih=c['screen']['size']
  quad=np.float32(c['screen']['quad']);rect=np.float32([[0,0],[iw-1,0],[iw-1,ih-1],[0,ih-1]])
  self.ui_tex=cv2.warpPerspective(self.base,cv2.getPerspectiveTransform(quad,rect),(iw,ih))
  self.ui_back=cv2.getPerspectiveTransform(rect,quad-np.float32([a,b]));self.ui_original=cv2.warpPerspective(self.ui_tex,self.ui_back,(z-a,d-b)).astype(np.float32);self.ui_mask=cut(self.masks['screen'],self.ui_roi)
  self.uy,self.ux=np.mgrid[:ih,:iw].astype(np.float32)
  self.layer_masks={k:v>0 for k,v in self.masks.items()};self.active=np.logical_or.reduce(list(self.layer_masks.values()))
  self.groups=c['isolated_groups'];self.group_masks={k:np.logical_or.reduce([self.layer_masks[n] for n in names]) for k,names in self.groups.items()}
  print('Deepwell v2 initialized',round(time.time()-started,2),'s;',len(self.masks),'independent masks',flush=True)
 def noise_texture(self,shape,seed):
  h,w=shape;y,x=np.mgrid[:h,:w].astype(np.float32);rng=np.random.default_rng(seed);field=np.zeros(shape,np.float32)
  for i in range(18):
   kx=int(rng.integers(1,7));ky=int(rng.integers(1,6));ph=float(rng.uniform(0,2*np.pi));field+=np.cos(2*np.pi*(kx*x/w+ky*y/h)+ph).astype(np.float32)/np.float32(i+2)**.4
  field=(field-float(field.mean()))/max(float(field.std()),.01)
  return np.clip((field-.12)*.42,0,1).astype(np.float32)
 def transport(self,texture,t,speed,x,y,offset=0):
  out=np.zeros_like(texture,dtype=np.float32)
  for shift in (0,.5):
   age=(t/20+offset+shift)%1;weight=np.sin(np.pi*age)**2
   mx=(x-speed*20*(age-.5)).astype(np.float32)
   out+=cv2.remap(texture,mx,y,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)*(weight[...,None] if texture.ndim==3 and np.ndim(weight)>0 else weight)
  return out
 def weather_frame(self,f,t,enabled):
  render_weather(self,f,t,enabled)
 def screen_frame(self,f,t):
  tex=self.ui_tex.astype(np.float32).copy();x=self.ux;y=self.uy;p=2*np.pi*t/20
  pressure=.56+.24*np.sin(p-.3)+.1*np.sin(3*p+.7)
  angle=np.pi*(1.04-.72*pressure);dx=27*np.cos(angle);dy=-27*np.sin(angle);cx,cy=40,57
  along=np.clip(((x-cx)*dx+(y-cy)*dy)/(27*27),0,1);needle=np.exp(-((x-cx-along*dx)**2+(y-cy-along*dy)**2)/.8)
  tip=np.exp(-((x-cx-dx)**2+(y-cy-dy)**2)/3)
  tex+=(needle[...,None]*np.float32([34,70,79])+tip[...,None]*np.float32([35,66,73]))*self.config['screen']['needle_strength']
  # Retain source panel boundaries and data strokes; scroll only the log pane.
  log=self.ui_tex[26:76,88:121];ly,lx=np.mgrid[:50,:33].astype(np.float32)
  moved=cv2.remap(log,lx,(ly+t/20*100).astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_WRAP)
  tex[26:76,88:121]=tex[26:76,88:121]*.18+moved*.82
  for row in range(3):
   level=np.clip(pressure+(row-1)*.12+.09*np.sin((row+2)*p+row),.12,.93);coverage=np.clip(36*level-np.arange(36),0,1)
   tex[94+row*5:97+row*5,12:48]+=coverage[None,:,None]*np.float32([29,60,66])
  # Forward-moving acquisition cursor stays inside the existing upper-right plot.
  yy,xx=np.mgrid[30:70,90:120].astype(np.float32);q=(t/5)%1;fade=np.sin(np.pi*q)**2
  marker=np.exp(-((xx-(92+25*q))**2/2+(yy-(57-6*np.sin(2*np.pi*q)))**2/3))*fade
  tex[30:70,90:120]+=marker[...,None]*np.float32([44,81,92])
  a,b,z,d=self.ui_roi;projected=cv2.warpPerspective(tex,self.ui_back,(z-a,d-b));f[b:d,a:z]+=(projected-self.ui_original)*self.ui_mask[...,None]
 def frame(self,t,only=None):
  t=float(t)%20;enabled=set(self.masks) if only is None else set(self.groups.get(only,[only]));f=self.base.astype(np.float32)
  if 'water' in enabled:
   a,b,z,d=self.water_roi;f[b:d,a:z]=self.water.frame(t)
  if 'sky' in enabled or 'planet_veil' in enabled:
   c=self.config['sky'];a,b,z,d=self.sky_roi
   if 'sky' in enabled:
    near=self.transport(self.cloud_base,t,c['near_speed'],self.cx,self.cy,self.offset)
    far=self.transport(self.cloud_base,t,c['far_speed'],self.cx,self.cy,self.offset+.19)
    moving=near*self.near_weight[...,None]+far*(1-self.near_weight[...,None])
    f[b:d,a:z]+=(moving-self.cloud_original)*self.sky_mask[...,None]*c['gain']
   if 'planet_veil' in enabled:
    shifted_y=np.clip(self.cy-64,0,self.front_texture.shape[0]-1).astype(np.float32)
    density=self.transport(self.front_texture,t,c['veil_speed'],self.cx,shifted_y,self.offset+.29)
    alpha=density*self.veil_mask*c['veil_opacity'];crop_blend(f,self.sky_roi,[210,216,228],alpha)
  self.weather_frame(f,t,enabled)
  if 'lights' in enabled:
   for c,r,m in self.windows:
    a,b,z,d=r;amount=event_amount(t,20,c['start'],c['hold'],c['transition']);f[b:d,a:z]*=1-m[...,None]*amount*(1-c['floor'])
  if 'lamp' in enabled:
   amount=max(event_amount(t,20,e['start'],e['hold'],e['transition'])*e['depth'] for e in self.config['lamp']['events']);a,b,z,d=self.lamp_roi;f[b:d,a:z]*=1-self.lamp_mask[...,None]*amount
  if 'status' in enabled:
   amount=max(event_amount(t,20,e['start'],e['hold'],e['transition'])*e['depth'] for e in self.config['status']['events']);a,b,z,d=self.status_roi;f[b:d,a:z]*=1-self.status_mask[...,None]*amount
  if 'screen' in enabled:self.screen_frame(f,t)
  if 'daylight' in enabled:
   a,b,z,d=self.day_roi;f[b:d,a:z]*=1+self.day_mask[...,None]*(sun_state(t)-.5)*2
  assert np.isfinite(f).all();f=np.uint8(np.rint(np.clip(f,0,255)))
  mask=self.active if only is None else self.group_masks[only] if only in self.group_masks else self.layer_masks[only]
  assert np.array_equal(f[~mask],self.base[~mask]),'Protected source pixels changed'
  assert np.array_equal(f[self.pipeline],self.base[self.pipeline]),'Pipeline/support source pixels changed'
  return f
 def fingerprint(self):
  names=['scene-plan-v2.json','render_deepwell_v2.py','review_tools.py','weather_refinement.py','baseline-snapshot-manifest.json']
  names+=[str(p.relative_to(H)).replace('\\','/') for p in sorted(B.rglob('*.py'))]+[self.config['source']['path'],'baseline-snapshot/scene-plan-v1.json','baseline-snapshot/artwork-original-v2.png']
  return {'files':{n:digest(H/n) for n in names},'masks_float32_sha256':{k:hashlib.sha256(v.tobytes()).hexdigest() for k,v in self.masks.items()},'runtime':{'python':sys.version,'numpy':np.__version__,'opencv':cv2.__version__,'platform':platform.platform(),'ffmpeg':subprocess.check_output(['ffmpeg','-version'],text=True).splitlines()[0]}}

def samples(s):
 (H/'masks').mkdir(exist_ok=True);overlay=s.base.astype(np.float32)
 colours={'water':[35,150,255],'sky':[30,220,90],'planet_veil':[210,90,240],'far_drift':[255,120,20],'basin_haze':[255,210,20],'brine_wisps':[70,230,230],'salt_far':[220,60,70],'salt_middle':[240,100,90],'lights':[255,30,30],'lamp':[255,200,20],'status':[255,120,0],'screen':[190,50,255],'daylight':[220,220,20]}
 for k,m in s.masks.items():
  Image.fromarray(np.uint8(np.rint(np.clip(m,0,1)*255))).save(H/'masks'/f'{k}.png');alpha=np.clip(m[...,None],0,1)*.42;overlay=overlay*(1-alpha)+np.float32(colours[k])*alpha
 Image.fromarray(np.uint8(overlay)).save(H/'mask-review.png')
 for t in [0,2,4,6.7,8,12,16,19+29/30]:Image.fromarray(s.frame(t)).save(H/f'sample-{t:.3f}s.png')
 checks={}
 for name in s.layer_masks:
  m=s.layer_masks[name];zero=s.frame(0,name);assert np.array_equal(zero,s.frame(20,name))
  seam=float(np.abs(s.frame(-1/30,name)[m].astype(float)-zero[m]).mean());steps=[]
  for t in [0,.033333,.3,1,3,7,12,16,19.5]:steps.append(float(np.abs(s.frame(t+1/30,name)[m].astype(float)-s.frame(t,name)[m]).mean()))
  assert seam<=max(steps)*1.15+.02,(name,seam,steps)
  motion=[float(np.abs(s.frame(t+1,name)[m].astype(float)-s.frame(t,name)[m]).mean()) for t in [0,4,8,12,16]]
  checks[name]={'endpoint_exact':True,'protected_pixels_exact':True,'seam_step_mae':seam,'ordinary_sampled_max':max(steps),'one_second_motion_at_0_4_8_12_16':motion}
 write_json('analytic-validation.json',{'fingerprint':s.fingerprint(),'layers':checks,'source_protection':'Asserted on every native rendered frame outside the selected layer/group masks','planet':'Fixed source body and silhouette; only explicit foreground cloud opacity changes it. Planet-free cloud sampling prevents duplicates.','water_frequency_deviation_percent':{'mean':float(np.mean(np.abs(s.water.speed_deviations))*100),'max':float(np.max(np.abs(s.water.speed_deviations))*100)},'user_approved':False})
 print('Native samples, mask protection and per-layer analytic continuity passed',flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['samples','isolated','preview'],required=True);p.add_argument('--group',choices=['sky','water','atmosphere','habitation']);a=p.parse_args();s=DeepwellV2()
 if a.stage=='samples':samples(s);return
 clips=[]
 if a.stage=='isolated':
  for group in ([a.group] if a.group else s.groups):
   out=H/f'deepwell-v2-{group}-isolated-8s.mp4';item=encode(s,out,8,group);item['validation'],_=decode_verify(s,out,240);clips.append(item);print(group,'isolated verified',flush=True)
 else:
  out=H/'Deepwell-v2-preview-20s.mp4';item=encode(s,out,20);item['validation'],hashes=decode_verify(s,out,600,True);clips.append(item)
  repeat=H/'Deepwell-v2-three-loops-60s.mp4';assert not repeat.exists();subprocess.run(['ffmpeg','-v','error','-n','-stream_loop','2','-i',str(out),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
  item={'path':repeat.name,'sha256':digest(repeat)};item['validation'],_=decode_verify(s,repeat,1800,True,hashes)
  def packets(path):return [v['data_hash'] for v in json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v','-show_packets','-show_data_hash','sha256','-show_entries','packet=data_hash','-of','json',str(path)],text=True))['packets']]
  assert packets(repeat)==packets(out)*3;item['three_identical_encoded_packet_sequences']=True;clips.append(item)
 write_json(a.stage+('-'+a.group if a.group else '')+'-validation.json',{'fingerprint':s.fingerprint(),'clips':clips,'user_approved':False,'inspection':'Source/mask/temporal/decoded stills; continuous playback not claimed'})
 print(a.stage,'complete and verified',flush=True)
if __name__=='__main__':main()
