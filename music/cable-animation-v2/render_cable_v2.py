"""V2 effect extension; imports the immutable v1 renderer and accepted transport primitives."""
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

class CableV2(Cable):
 def __init__(self,config='scene-plan-v2.json'):
  super().__init__(str(H/config));c=self.config
  y,x=np.mgrid[:self.h,:self.w].astype(np.float32);self.xx=x;self.yy=y
  fc=c['distance_fog'];binary=self.poly(fc['polygons'])
  for poly in fc['exclude']:binary[self.poly([poly])>0]=0
  binary[self.protected]=0
  fog=smoothstep(cv2.distanceTransform(binary,cv2.DIST_L2,5)/fc['feather']).astype(np.float32)
  self.masks['distance_fog']=fog
  yy,xx=np.where(fog>0);self.fog_roi=(xx.min(),yy.min(),xx.max()+1,yy.max()+1)
  x0,y0,x1,y1=self.fog_roi;self.fog=PeriodicDust(x[y0:y1,x0:x1],y[y0:y1,x0:x1],fc,self.duration)
  lamp=c['lamp'];aperture=self.poly([lamp['aperture']]).astype(np.float32)
  halo=cv2.GaussianBlur(aperture,(0,0),1.7)*.20;halo[halo<.003]=0
  self.lamp_aperture=np.clip(aperture+halo,0,1);self.lamp_spill=np.zeros_like(x)
  for region in lamp['spill_regions']:
   boundary=smoothstep(cv2.distanceTransform(self.poly([region['polygon']]),cv2.DIST_L2,5)/9)
   cx,cy=region['center'];rx,ry=region['radii'];shape=np.exp(-.5*(((x-cx)/rx)**2+((y-cy)/ry)**2))
   self.lamp_spill=np.maximum(self.lamp_spill,boundary*shape*region['strength'])
  self.masks['room_lamp']=np.maximum(self.lamp_aperture,self.lamp_spill)
  dc=c['daylight'];cx,cy=dc['sky_center'];rx,ry=dc['sky_radii']
  sky_shape=np.exp(-.5*(((x-cx)/rx)**2+((y-cy)/ry)**2))
  # Local left-sky/sunward illumination only; preserve the fixed planet and cables.
  self.day_sky=np.maximum(self.masks['sky'],self.masks['left_fog'])*sky_shape*dc['sky_depth']
  binary=self.poly(dc['room_polygons']);boundary=smoothstep(cv2.distanceTransform(binary,cv2.DIST_L2,5)/16)
  cx,cy=dc['room_center'];rx,ry=dc['room_radii'];room_shape=np.exp(-.5*(((x-cx)/rx)**2+((y-cy)/ry)**2))
  self.day_room=boundary*room_shape*dc['room_depth']
  self.masks['daylight']=np.maximum(self.day_sky,self.day_room)
  for name in ['room_lamp','daylight']:self.masks[name][self.protected]=0
  self.layer_masks={k:v>0 for k,v in self.masks.items()};self.active=np.logical_or.reduce(list(self.layer_masks.values()))

 def frame(self,t,only=None,prototype=False):
  t=float(t)%self.duration;f=super().frame(t,only,prototype).astype(np.float32)
  if only in (None,'distance_fog','atmosphere'):
   x0,y0,x1,y1=self.fog_roi;alpha,color=self.fog.density(t)
   alpha*=self.masks['distance_fog'][y0:y1,x0:x1]
   f[y0:y1,x0:x1]=f[y0:y1,x0:x1]*(1-alpha[...,None])+color*alpha[...,None]
  if only in (None,'room_lamp'):
   amount=max(event_amount(t,self.duration,e['start'],e['hold'],e['transition'])*e['depth'] for e in self.config['lamp']['events'])
   dim=np.clip(self.lamp_aperture+self.lamp_spill,0,1)*amount
   f*=1-dim[...,None]*np.array([1,.96,.87])
  if only in (None,'daylight'):
   dc=self.config['daylight'];amount=event_amount(t,self.duration,dc['start'],dc['hold'],dc['transition'])
   dim=(self.day_sky+self.day_room)*amount
   f*=1-dim[...,None]*np.array([1,.86,.65])
  assert np.isfinite(f).all();f=np.uint8(np.rint(np.clip(f,0,255)))
  mask=self.active if only in (None,'atmosphere') else self.layer_masks[only]
  assert np.array_equal(f[~mask],self.base[~mask])
  assert np.array_equal(f[self.protected],self.base[self.protected])
  return f

 def fingerprint(self):
  return {'source_sha256':self.config['source']['sha256'],'config_sha256':digest(self.path),'renderer_sha256':digest(__file__),'dependencies':{str(p.relative_to(ROOT)):digest(p) for p in [H.parent/'cable-animation-v1/render_cable.py',H.parent/'saltline-animation-v1/periodic_transport.py',H.parent/'saltline-animation-v1/dust_transport.py',ROOT/'scripts/ambient_effects.py',ROOT/'scripts/render_floodplain.py',ROOT/'scripts/water_surface.py']},'effective_masks':{k:hashlib.sha256(v.tobytes()).hexdigest() for k,v in self.masks.items()}}

def samples(s):
 out=H/'masks';out.mkdir(exist_ok=True);overlay=s.base.astype(float)
 for name,color in [('distance_fog',[120,240,180]),('room_lamp',[255,160,35]),('daylight',[120,170,255])]:
  m=s.masks[name];cv2.imwrite(str(out/(name+'.png')),np.uint8(np.rint(m*255)))
  a=np.minimum(m*3,.5)[...,None];overlay=overlay*(1-a)+np.array(color)*a
 Image.fromarray(np.uint8(overlay)).save(H/'new-masks-review.png')
 for t in [0,4.55,8,12,15.2,19+29/30]:Image.fromarray(s.frame(t)).save(H/f'sample-{t:.3f}s.png')
 checks={}
 for name,mask in s.layer_masks.items():
  assert np.array_equal(s.frame(0,name),s.frame(20,name))
  seam=float(abs(s.frame(-1/30,name)[mask].astype(float)-s.frame(0,name)[mask]).mean())
  ordinary=[float(abs(s.frame(t+1/30,name)[mask].astype(float)-s.frame(t,name)[mask]).mean()) for t in np.arange(0,20,.5)]
  assert seam<=max(ordinary)*1.1+.01,(name,seam,max(ordinary))
  checks[name]={'periodic_endpoint_exact':True,'seam_mae':seam,'ordinary_max_sampled':max(ordinary),'pass':True}
 # The requested revision leaves these v1 supporting layers pixel-identical at representative times.
 v1=Cable();preserved={}
 for name in ['ravine','left_fog','lights','screen']:
  for t in [0,4,8,12,16]:assert np.array_equal(s.frame(t,name),v1.frame(t,name)),name
  preserved[name]='source frames identical at 0,4,8,12,16 seconds'
 (H/'analytic-validation.json').write_text(json.dumps({'fingerprint':s.fingerprint(),'layers':checks,'preserved_v1_layers':preserved,'user_motion_approved':False},indent=2)+'\n')
 print('V2 samples and layer seams ready; v1 supporting layers preserved',flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['samples','isolated','preview'],required=True);a=p.parse_args();s=CableV2();clips=[]
 if a.stage=='samples':samples(s);return
 if a.stage=='isolated':
  for name in ['valley','distance_fog','daylight','room_lamp']:
   out=H/f'{name}-isolated-v2-8s.mp4';item=encode(s,out,8,name);item['validation']=verify(s,out,240);clips.append(item)
 else:
  out=H/'last-cable-station-v2-preview-20s.mp4';item=encode(s,out,20);item['validation']=verify(s,out,600,True);clips.append(item)
  repeat=H/'last-cable-station-v2-three-loops-60s.mp4';assert not repeat.exists()
  subprocess.run([s.config['ffmpeg'],'-v','error','-n','-stream_loop','2','-i',str(out),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
  validation=verify(s,repeat,1800,True)
  cap=cv2.VideoCapture(str(repeat));hs=[]
  while True:
   ok,f=cap.read()
   if not ok:break
   hs.append(hashlib.sha256(f.tobytes()).hexdigest())
  cap.release();assert hs[:600]==hs[600:1200]==hs[1200:]
  clips.append({'path':repeat.relative_to(ROOT).as_posix(),'sha256':digest(repeat),'validation':validation,'three_repeated_decoded_payloads_identical':True})
  cap=cv2.VideoCapture(str(out));cap.set(cv2.CAP_PROP_POS_MSEC,8000);ok,f=cap.read();cap.release();assert ok;cv2.imwrite(str(H/'decoded-v2-8s.png'),f)
 (H/(a.stage+'-validation.json')).write_text(json.dumps({'fingerprint':s.fingerprint(),'clips':clips,'user_motion_approved':False,'prior_feedback':s.config['feedback'],'inspection':'Temporal/decoded still inspection; continuous playback not claimed','silent':True},indent=2)+'\n')
 print(a.stage+' passed',flush=True)
if __name__=='__main__':main()
