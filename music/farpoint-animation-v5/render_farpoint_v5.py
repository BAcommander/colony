"""Expand planetary weather coverage; remove rejected aurora; readable fixed-star glints."""
from pathlib import Path
import sys,json,hashlib,argparse,subprocess
import cv2,numpy as np
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(H.parent/'farpoint-animation-v4'))
from render_farpoint_v4 import FarpointMinute,Farpoint,byte_image,encode,digest,smoothstep,verify
def save(name,data):(H/name).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')

def build_plan():
 c=json.loads((H.parent/'farpoint-animation-v4/scene-plan-v4.json').read_text(encoding='utf-8'))
 c.update(version='v5',status='V4 rejected for sparse coverage, implausible blue glow and imperceptible stars; revised candidate')
 c['parent_v4_renderer_sha256']=digest(H.parent/'farpoint-animation-v4/render_farpoint_v4.py')
 c['aurora']['enabled']=False
 c['stars'].update(depth=0,cycles=[5,4,6,3,5,4],brightness_range=[.45,2.15])
 c['expanded_weather']={'roi':[620,205,1612,647],'seed':105,'texture_size':512,'angular_scale':980,'period_lengths':[330,510],'radial_texture_scale':1.55,'threshold':.47,'transition':.18,'max_opacity':.74,'cloud_color':[240,235,219],'shadow_strength':.18,'shadow_offset':[-12,16],'bands':[[162,62,32],[290,66,30],[418,69,25]],'window_polygon':[[617,575],[650,512],[752,407],[871,319],[1030,242],[1210,201],[1450,174],[1609,181],[1608,580],[1583,617],[1546,645],[720,593]],'crater_detail':'Terrain coordinates stay fixed; moving cloud opacity may veil crater interiors. No displaced geology.'}
 c['review']={'approved':False,'feedback':'huge parts of the planet still have no clouds or movement, ahd the wierd blue glow over the planet doesn’t seem to make sense, i see no movement in the stars etc','inspection':'pending'}
 c['layer_order']=['retained_v4_weather','expanded_cloud_shadows','expanded_clouds','station_activity','stars']
 c['knowledge_reuse']['v4_correction']='Readability requires spatial coverage, not just nonzero activity within old masks. Remove rejected aurora. Add advected broken fronts over bare regions and strengthen selected original star light changes.'
 save('scene-plan-v5.json',c)

def periodic_noise(seed,size):
 rng=np.random.default_rng(seed);out=np.zeros((size,size),np.float32)
 for cells,weight in [(6,.43),(12,.27),(24,.16),(48,.09),(96,.05)]:
  grid=rng.random((cells,cells),dtype=np.float32)
  # Tiled interpolation makes value and slope continuous at both texture edges.
  tile=cv2.resize(np.tile(grid,(3,3)),(size*3,size*3),interpolation=cv2.INTER_CUBIC)
  out+=tile[size:size*2,size:size*2]*weight
 return out

class FarpointV5(FarpointMinute):
 def __init__(self):
  super().__init__()
  self.path=H/'scene-plan-v5.json';self.config=json.loads(self.path.read_text(encoding='utf-8'))
  assert digest(H.parent/'farpoint-animation-v4/render_farpoint_v4.py')==self.config['parent_v4_renderer_sha256']
  self.masks.pop('aurora');self.prepare_weather()
  self.layer_masks={k:m>0 for k,m in self.masks.items()}
  self.layer_masks['planet_activity']=np.logical_or.reduce([self.layer_masks[k] for k in ['clouds','veil','lower_cloud','cloud_shadows','lightning','expanded_weather']])
  self.layer_masks['habitation']=np.logical_or.reduce([self.layer_masks[k] for k in ['windows','screen','lamp','instrument_lights','reflections']])
  self.active=np.logical_or.reduce(list(self.layer_masks.values()))

 def aurora(self,t):return np.zeros((*self.aurora_mask.shape,3),np.float32)

 def prepare_weather(self):
  c=self.config['expanded_weather'];a,b,z,d=c['roi'];self.weather_roi=(a,b,z,d)
  xx=self.x[b:d,a:z];yy=self.y[b:d,a:z];cx,cy=self.config['planet']['center']
  radius=np.hypot(xx-cx,yy-cy);angle=np.arctan2(yy-cy,xx-cx)
  self.depth=self.config['planet']['radius']-radius;self.flow=angle*c['angular_scale']
  m=self.poly([c['window_polygon']],14)[b:d,a:z]
  m*=smoothstep((self.depth-52)/48)*smoothstep((yy-b)/12)*smoothstep((d-1-yy)/18)*smoothstep((xx-a)/16)*smoothstep((z-1-xx)/16)
  # Fade new fronts where the photographed upper-cloud layer already dominates.
  m*=.55+.45*smoothstep((self.depth-115)/70)
  m[m<.002]=0;self.weather_mask=m
  mask=np.zeros(self.shape,np.float32);mask[b:d,a:z]=m;self.masks['expanded_weather']=mask
  self.noises=[periodic_noise(c['seed']+i,c['texture_size']) for i in range(3)]
  self.wy=((self.depth*c['radial_texture_scale'])%c['texture_size']).astype(np.float32)
  self.lighting=(.67+.26*smoothstep((xx-750)/750)+.07*smoothstep((300-self.depth)/250))[...,None]
  yy0,xx0=np.mgrid[:d-b,:z-a].astype(np.float32);dx,dy=c['shadow_offset']
  self.wx_shadow=xx0-dx;self.wy_shadow=yy0-dy

 def weather_alpha(self,t):
  c=self.config['expanded_weather'];size=c['texture_size'];q=2*np.pi*t/self.duration
  fields=[]
  for noise,length in zip(self.noises,c['period_lengths']):
   mx=((self.flow/length-t/self.duration)*size).astype(np.float32)
   fields.append(cv2.remap(noise,mx,self.wy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_WRAP))
  n=fields[0]*.75+fields[1]*.25
  bands=np.zeros_like(self.depth)
  for i,(center,width,swing) in enumerate(c['bands']):
   front=center+swing*np.sin(self.flow/113-q*(i%2+1)+i*2.1)+12*np.sin(self.flow/47-2*q+i)
   bands=np.maximum(bands,np.exp(-((self.depth-front)/width)**2))
  density=smoothstep((n-c['threshold'])/c['transition'])
  alpha=density*bands*self.weather_mask*c['max_opacity']
  return alpha.astype(np.float32)

 def apply_weather(self,f,t):
  a,b,z,d=self.weather_roi;c=self.config['expanded_weather'];alpha=self.weather_alpha(t)
  shadow=cv2.remap(cv2.GaussianBlur(alpha,(0,0),4),self.wx_shadow,self.wy_shadow,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
  shadow*=self.weather_mask*c['shadow_strength']
  region=f[b:d,a:z]*(1-shadow[...,None])
  cloud=np.float32(c['cloud_color'])*self.lighting
  f[b:d,a:z]=region*(1-alpha[...,None])+cloud*alpha[...,None]

 def frame_float(self,t,only=None):
  t=float(t)%self.duration
  f=super().frame_float(t,only)
  if only in (None,'expanded_weather','planet_activity'):self.apply_weather(f,t)
  if only in (None,'stars'):
   low,high=self.config['stars']['brightness_range']
   for j,((a,b,z,d),m,_,phase) in enumerate(self.star_parts):
    cycles=self.config['stars']['cycles'][j]
    peak=(.5+.5*np.sin(2*np.pi*cycles*t/self.duration+phase))**2
    value=low+(high-low)*peak
    f[b:d,a:z]*=1+m[...,None]*(value-1)
  assert np.isfinite(f).all();return f

 def fingerprint(self):
  fp=super().fingerprint()
  for p in [Path(__file__),H.parent/'farpoint-animation-v4/scene-plan-v4.json']:
   fp['files'][p.relative_to(R).as_posix()]=digest(p)
  return fp

def samples(s):
 (H/'masks').mkdir(exist_ok=True)
 for k,m in s.masks.items():cv2.imwrite(str(H/'masks'/f'{k}.png'),byte_image(m*255))
 for t in [0,2,5,8,12.95,20,30,40,50,59+29/30]:
  Image.fromarray(cv2.resize(s.frame(t),(1280,720),interpolation=cv2.INTER_AREA)).save(H/f'sample-{t:06.2f}s.png')
 overlay=s.base.astype(np.float32);m=s.masks['expanded_weather'][...,None]*.45
 Image.fromarray(byte_image(overlay*(1-m)+np.float32([50,190,255])*m)).save(H/'weather-mask-review.png')
 old=FarpointMinute();reg={}
 for k in ['clouds','veil','lower_cloud','cloud_shadows','lightning','windows','screen','lamp','instrument_lights','reflections']:
  reg[k]=all(np.array_equal(s.frame(t,k),old.frame(t,k)) for t in [0,7,20,40,54])
  assert reg[k],k
 checks={}
 for key in s.layer_masks:
  m=s.layer_masks[key];assert np.array_equal(s.frame(0,key),s.frame(60,key))
  vals=[]
  for t in [-1/30,0,3,8,11.2,12.8,20,30,36.5,40,44.4,50,52.8,58]:
   vals.append(float(np.abs(s.frame(t+1/30,key)[m].astype(float)-s.frame(t,key)[m]).mean()))
  assert vals[0]<=max(vals[1:])*1.1+.01,(key,vals)
  checks[key]={'seam_mae':vals[0],'ordinary_sample_max':max(vals[1:]),'pass':True}
 assert len({hashlib.sha256(s.frame(t).tobytes()).hexdigest() for t in [0,20,40]})==3
 save('analytic-validation.json',{'fingerprint':s.fingerprint(),'retained_v4_layers_sampled_exact':reg,'layer_checks':checks,'distinct_0_20_40':True,'source_protection':'Asserted every rendered frame','visual_acceptance':False})
 print('samples and analytic/regression checks passed',flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['plan','samples','isolated','preview'],required=True);args=p.parse_args()
 if args.stage=='plan':build_plan();return
 s=FarpointV5()
 if args.stage=='samples':samples(s);return
 clips=[]
 if args.stage=='isolated':
  for layer in ['expanded_weather','stars']:
   path=H/f'{layer}-v5-isolated-10s.mp4';item=encode(s,path,10,layer,True);item['validation'],_=verify(s,path,300,False);clips.append(item)
 else:
  path=H/'farpoint-station-v5-preview-60s.mp4';item=encode(s,path,60);item['validation'],hashes=verify(s,path,1800,True);clips.append(item)
  repeat=H/'farpoint-station-v5-three-loops-180s.mp4';assert not repeat.exists()
  subprocess.run([s.config['ffmpeg'],'-v','error','-n','-stream_loop','2','-i',str(path),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
  validation,repeated=verify(s,repeat,5400,True);assert repeated==hashes*3
  clips.append({'path':repeat.relative_to(R).as_posix(),'sha256':digest(repeat),'validation':validation,'exact_three_decoded_repetitions':True})
  save('decoded-frame-hashes.json',hashes)
  cap=cv2.VideoCapture(str(path))
  for n in [0,150,600,1200,1500,1799]:
   cap.set(cv2.CAP_PROP_POS_FRAMES,n);ok,f=cap.read();assert ok;cv2.imwrite(str(H/f'decoded-{n:04d}.png'),f)
  cap.release()
 save(args.stage+'-validation.json',{'fingerprint':s.fingerprint(),'clips':clips,'silent':True,'user_approved':False,'inspection':'Actual-strength source/temporal/decoded stills; continuous playback unavailable'})
 print(args.stage,'full decode and validation passed',flush=True)
if __name__=='__main__':main()
