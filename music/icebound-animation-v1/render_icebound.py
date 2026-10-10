"""Icebound adapter: source-coordinate masks and reused accepted transport logic."""
from pathlib import Path
import sys,json,hashlib,argparse,subprocess
import cv2,numpy as np
from PIL import Image
H=Path(__file__).resolve().parent;ROOT=H.parents[1]
sys.path.insert(0,str(H.parent/'cable-animation-v1'))
sys.path.insert(0,str(H.parent/'saltline-animation-v1'))
from render_cable import Cable
from periodic_transport import PeriodicDust
from ambient_effects import smoothstep,event_amount
from render_floodplain import encode,verify,digest

class Icebound(Cable):
 def __init__(self):
  super().__init__(str(H/'scene-plan-v1.json'));self.masks.pop('screen');self.haze=[]
  y,x=np.mgrid[:self.h,:self.w].astype(np.float32)
  for c in self.config['haze']:
   binary=self.poly(c['polygons']);binary[self.protected]=0
   mask=smoothstep(cv2.distanceTransform(binary,cv2.DIST_L2,5)/c['feather']).astype(np.float32)
   self.masks[c['name']]=mask;yy,xx=np.where(mask>0);roi=(xx.min(),yy.min(),xx.max()+1,yy.max()+1)
   x0,y0,x1,y1=roi
   self.haze.append((c['name'],roi,mask[y0:y1,x0:x1],PeriodicDust(x[y0:y1,x0:x1],y[y0:y1,x0:x1],c,self.duration)))
  ec=self.config['entrance'];ap=self.poly([ec['aperture']]).astype(np.float32)
  halo=cv2.GaussianBlur(ap,(0,0),2)*.2;halo[halo<.002]=0
  self.entrance=np.clip(ap+halo,0,1)
  spill=smoothstep(cv2.distanceTransform(self.poly(ec['spill_polygons']),cv2.DIST_L2,5)/12)*.13
  self.entrance=np.maximum(self.entrance,spill);self.masks['entrance']=self.entrance
  rc=self.config['room_spill'];self.room_spill=smoothstep(cv2.distanceTransform(self.poly(rc['polygons']),cv2.DIST_L2,5)/14)*rc['strength']
  self.masks['room_spill']=self.room_spill
  self.layer_masks={k:v>0 for k,v in self.masks.items()};self.active=np.logical_or.reduce(list(self.layer_masks.values()))

 def frame(self,t,only=None,prototype=False):
  t=float(t)%self.duration;f=super().frame(t,only,prototype).astype(np.float32)
  for name,(x0,y0,x1,y1),mask,field in self.haze:
   if only not in (None,name,'atmosphere'):continue
   alpha,color=field.density(t);alpha*=mask
   f[y0:y1,x0:x1]=f[y0:y1,x0:x1]*(1-alpha[...,None])+color*alpha[...,None]
  if only in (None,'entrance'):
   amount=max(event_amount(t,self.duration,e['start'],e['hold'],e['transition'])*e['depth'] for e in self.config['entrance']['events'])
   f*=1-self.entrance[...,None]*amount*np.array([1,.92,.72])
  if only in (None,'room_spill'):
   c=self.config['lights'][0];amount=event_amount(t,self.duration,c['start'],c['hold'],c['transition'])
   f*=1-self.room_spill[...,None]*amount*np.array([1,.88,.65])
  assert np.isfinite(f).all();f=np.uint8(np.rint(np.clip(f,0,255)))
  mask=self.active if only in (None,'atmosphere') else self.layer_masks[only]
  assert np.array_equal(f[~mask],self.base[~mask]);assert np.array_equal(f[self.protected],self.base[self.protected])
  return f

 def fingerprint(self):
  files=[H.parent/'cable-animation-v1/render_cable.py',H.parent/'saltline-animation-v1/periodic_transport.py',H.parent/'saltline-animation-v1/dust_transport.py',ROOT/'scripts/ambient_effects.py',ROOT/'scripts/render_floodplain.py',ROOT/'scripts/water_surface.py']
  return {'source_sha256':self.config['source']['sha256'],'config_sha256':digest(self.path),'renderer_sha256':digest(__file__),'dependencies':{str(p.relative_to(ROOT)):digest(p) for p in files},'effective_masks':{k:hashlib.sha256(v.tobytes()).hexdigest() for k,v in self.masks.items()}}

def samples(s):
 out=H/'masks';out.mkdir(exist_ok=True);overlay=s.base.astype(float)
 for (name,m),color in zip(s.masks.items(),[[80,180,255],[255,190,50],[120,240,160],[220,90,210],[255,120,30],[240,230,80]]):
  cv2.imwrite(str(out/(name+'.png')),np.uint8(np.rint(m*255)))
  alpha=np.minimum(m*2,.4)[...,None];overlay=overlay*(1-alpha)+np.array(color)*alpha
 Image.fromarray(np.uint8(overlay)).save(H/'mask-review.png')
 for t in [0,4.6,8,12,16,19+29/30]:Image.fromarray(s.frame(t)).save(H/f'sample-{t:.3f}s.png')
 checks={}
 for name,mask in s.layer_masks.items():
  assert mask.any();assert np.array_equal(s.frame(0,name),s.frame(20,name))
  seam=float(abs(s.frame(-1/30,name)[mask].astype(float)-s.frame(0,name)[mask]).mean())
  ordinary=[float(abs(s.frame(t+1/30,name)[mask].astype(float)-s.frame(t,name)[mask]).mean()) for t in np.arange(0,20,.5)]
  assert seam<=max(ordinary)*1.1+.01,(name,seam,max(ordinary))
  checks[name]={'periodic_endpoint_exact':True,'seam_mae':seam,'ordinary_max_sampled':max(ordinary),'pass':True}
 assert not np.array_equal(s.frame(0),s.frame(10))
 (H/'analytic-validation.json').write_text(json.dumps({'fingerprint':s.fingerprint(),'layers':checks,'source_protection':'asserted every generated frame','user_motion_approved':False},indent=2)+'\n')
 print('Masks, samples and analytic layer seams ready',flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['samples','isolated','preview'],required=True);p.add_argument('--layer',default=None);a=p.parse_args();s=Icebound();clips=[]
 if a.stage=='samples':samples(s);return
 if a.stage=='isolated':
  for name in ([a.layer] if a.layer else ['sky','far_spindrift','basin_spindrift']):
   suffix=s.config.get('test_revision','a');out=H/f'{name}-isolated-v1-{suffix}-8s.mp4';item=encode(s,out,8,name);item['validation']=verify(s,out,240);clips.append(item)
 else:
  out=H/'icebound-weather-post-v1-preview-20s.mp4';item=encode(s,out,20);item['validation']=verify(s,out,600,True);clips.append(item)
  repeat=H/'icebound-weather-post-v1-three-loops-60s.mp4';assert not repeat.exists()
  subprocess.run([s.config['ffmpeg'],'-v','error','-n','-stream_loop','2','-i',str(out),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
  validation=verify(s,repeat,1800,True);cap=cv2.VideoCapture(str(repeat));hashes=[]
  while True:
   ok,f=cap.read()
   if not ok:break
   hashes.append(hashlib.sha256(f.tobytes()).hexdigest())
  cap.release();assert hashes[:600]==hashes[600:1200]==hashes[1200:]
  clips.append({'path':repeat.relative_to(ROOT).as_posix(),'sha256':digest(repeat),'validation':validation,'three_repeated_decoded_payloads_identical':True})
  cap=cv2.VideoCapture(str(out));cap.set(cv2.CAP_PROP_POS_MSEC,8000);ok,f=cap.read();cap.release();assert ok;cv2.imwrite(str(H/'decoded-preview-8s.png'),f)
 name='isolated-'+a.layer if a.layer else a.stage
 (H/(name+'-validation.json')).write_text(json.dumps({'fingerprint':s.fingerprint(),'clips':clips,'user_motion_approved':False,'inspection':'Mask and temporal/decoded still inspection; continuous playback not claimed','silent':True},indent=2)+'\n')
 print(a.stage+' checks passed',flush=True)
if __name__=='__main__':main()
