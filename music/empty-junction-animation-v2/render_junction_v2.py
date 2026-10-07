"""V2: broader cloud banks and evolving mist; reuse v1 geometry, lights and validation."""
from pathlib import Path
import sys,json,argparse,subprocess,hashlib
import cv2,numpy as np
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(H.parent/'empty-junction-animation-v1'))
import render_junction as previous
from render_junction import smoothstep,byte,digest,encode,verify

def save(name,data): (H/name).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')

class EvolvingField:
 """Advected multiscale density with evolving billows and independent invisible renewal."""
 def __init__(self,x,y,c):
  self.x=x;self.y=y;self.c=c
  rng=np.random.default_rng(c['seed']);shape=(384,2048)
  self.texture=np.zeros(shape,np.float32)
  for rows,cols,weight in [(10,30,.53),(25,82,.29),(65,210,.13),(150,450,.05)]:
   n=rng.random((rows,cols),dtype=np.float32)
   self.texture+=cv2.resize(n,(shape[1],shape[0]),interpolation=cv2.INTER_CUBIC)*weight
 def density(self,t):
  c=self.c;tau=np.zeros_like(self.x)
  for i,(gx,gy,w,h,phase) in enumerate(c['parcels']):
   age=(t+phase*60)%60;elapsed=age-30
   fade=float(smoothstep(age/c['fade'])*smoothstep((60-age)/c['fade']))
   if fade<1e-7:continue
   travel=c['speed']*elapsed;dx=self.x-gx-travel
   # Different frequencies alter the parcel internally, not just its opacity.
   center=gy+h*.18*np.sin(dx/w*4+age*.105+i)
   thickness=h*(.88+.18*np.sin(dx/w*3-age*.13+i*2))
   dy=self.y-center
   env=np.exp(-.5*(dx/w)**2-.5*(dy/thickness)**2)
   env*=smoothstep((3-np.abs(dx/w))/.8)*smoothstep((3-np.abs(dy/thickness))/.8)
   u=(self.x-travel*1.13+i*173+400).astype(np.float32)
   v=(self.y+60+i*37+h*.16*np.sin(dx/w*5+age*.14)).astype(np.float32)
   n=cv2.remap(self.texture,u,v,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
   density=np.maximum(n*env-c['threshold'],0)*c['contrast']
   tau+=density*c['optical_depth']*fade
  alpha=np.minimum(1-np.exp(-tau),c['max_opacity'])
  return alpha,np.float32(c['color'])

class Junction(previous.Junction):
 def __init__(self):
  self.path=H/'scene-plan-v2.json';self.config=json.loads(self.path.read_text(encoding='utf-8'))
  c=self.config;p=R/c['source']['path'];assert digest(p)==c['source']['sha256']
  self.base=np.array(Image.open(p).convert('RGB'));self.h,self.w=self.base.shape[:2]
  assert [self.w,self.h]==c['source']['dimensions']
  self.shape=(self.h,self.w);self.y,self.x=np.mgrid[:self.h,:self.w].astype(np.float32)
  self.duration=c['duration'];self.masks={};self.prepare_sky();self.prepare_mist();self.prepare_lights()
  a,b,z,d=self.sky_roi;self.bank=EvolvingField(self.x[b:d,a:z],self.y[b:d,a:z],c['cloud_bank'])
  self.layer_masks={k:m>0 for k,m in self.masks.items()}
  self.layer_masks['pass_weather']=self.layer_masks['far_mist']|self.layer_masks['middle_mist']
  self.layer_masks['habitation']=np.logical_or.reduce([m for k,m in self.layer_masks.items() if k.startswith('light_')])
  self.active=np.logical_or.reduce(list(self.layer_masks.values()))
 def sky(self,f,t):
  super().sky(f,t);a,b,z,d=self.sky_roi
  alpha,color=self.bank.density(t);alpha*=self.sky_mask
  f[b:d,a:z]=f[b:d,a:z]*(1-alpha[...,None])+color*alpha[...,None]
 def prepare_mist(self):
  self.mists=[];blocker=self.poly(self.config['weather_blockers'],1)
  for c in self.config['weather']:
   m=self.poly(c['polygons'],c['feather'])*(1-blocker);m[m<.002]=0
   (a,b,z,d),local=self.crop(m)
   self.mists.append((c['name'],(a,b,z,d),local,EvolvingField(self.x[b:d,a:z],self.y[b:d,a:z],c)))
   self.masks[c['name']]=m
 def fingerprint(self):
  f=super().fingerprint()
  for p in [Path(__file__),H/'build_plan.py']:
   f['files'][p.relative_to(R).as_posix()]=digest(p)
  return f

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['samples','isolated','preview'],required=True);args=p.parse_args();s=Junction()
 if args.stage=='samples':
  previous.H=H;previous.samples(s);return
 clips=[]
 if args.stage=='isolated':
  for layer in ['sky_clouds','pass_weather','habitation']:
   path=H/f'{layer}-v2-isolated-10s.mp4';item=encode(s,path,10,layer,True);item['validation'],_=verify(s,path,300,False);clips.append(item)
 else:
  path=H/'empty-junction-v2-preview-60s.mp4';item=encode(s,path,60);item['validation'],hashes=verify(s,path,1800,True);clips.append(item)
  repeat=H/'empty-junction-v2-three-loops-180s.mp4';assert not repeat.exists()
  subprocess.run([s.config['ffmpeg'],'-v','error','-n','-stream_loop','2','-i',str(path),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
  validation,repeated=verify(s,repeat,5400,True);assert repeated==hashes*3
  clips.append({'path':repeat.relative_to(R).as_posix(),'sha256':digest(repeat),'validation':validation,'exact_three_decoded_repetitions':True})
  save('decoded-frame-hashes.json',hashes)
  cap=cv2.VideoCapture(str(path))
  for n in [0,246,600,900,1200,1500,1710,1799]:
   cap.set(cv2.CAP_PROP_POS_FRAMES,n);ok,f=cap.read();assert ok;cv2.imwrite(str(H/f'decoded-{n:04d}.png'),f)
  cap.release()
 save(args.stage+'-validation.json',{'fingerprint':s.fingerprint(),'clips':clips,'silent':True,'user_approved':False,'inspection':'Source, masks and temporal/decoded stills; continuous playback unavailable'})
 print(args.stage,'complete decode and validation passed',flush=True)
if __name__=='__main__':main()
