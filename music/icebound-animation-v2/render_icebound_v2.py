"""Add periodic subpixel snow and two antenna beacons over the preserved v1 scene."""
from pathlib import Path
import sys,json,hashlib,argparse,subprocess
import cv2,numpy as np
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(H.parent/'icebound-animation-v1'))
from render_icebound import Icebound
from ambient_effects import smoothstep,event_amount
from render_floodplain import encode,verify,digest

class IceboundV2:
 def __init__(self):
  self.parent=Icebound();self.path=H/'scene-plan-v2.json';self.config=json.loads(self.path.read_text());self.duration=self.config['duration']
  prior=json.loads((H.parent/'icebound-animation-v1/preview-validation.json').read_text())
  assert self.parent.fingerprint()==prior['fingerprint'],'Delivered v1 dependencies changed'
  self.base=self.parent.base;self.h,self.w=self.base.shape[:2]
  self.masks=dict(self.parent.masks);self.masks['snowfall']=np.ones((self.h,self.w),np.float32)
  self.beacons=[];bm=np.zeros((self.h,self.w),np.float32)
  for b in self.config['beacons']:
   cx,cy=b['xy'];r=16;x0,y0,x1,y1=cx-r,cy-r,cx+r+1,cy+r+1
   yy,xx=np.mgrid[y0:y1,x0:x1];dist=(xx-cx)**2+(yy-cy)**2
   core=np.exp(-.5*dist/b['radius']**2);halo=np.exp(-.5*dist/b['halo_radius']**2)*b['halo_strength'];halo[halo<.003]=0
   self.beacons.append((b,(x0,y0,x1,y1),core.astype(np.float32),halo.astype(np.float32)))
   bm[y0:y1,x0:x1]=np.maximum(core,halo)>0.0001
  self.masks['beacons']=bm;self.layer_masks={k:v>0 for k,v in self.masks.items()};self.active=np.logical_or.reduce(list(self.layer_masks.values()))
  rng=np.random.default_rng(self.config['snow']['seed']);self.flakes=[]
  for c in self.config['snow']['layers']:
   assert abs(self.duration/c['life']-round(self.duration/c['life']))<1e-9
   for i in range(c['count']):
    self.flakes.append((rng.uniform(-100,self.w+100),rng.uniform(-80,self.h+80),rng.uniform(*c['vx']),rng.uniform(*c['vy']),rng.uniform(*c['radius']),rng.uniform(*c['opacity']),rng.uniform(0,c['life']),c['life'],rng.uniform(0,2*np.pi)))

 def snow_alpha(self,t):
  out=np.zeros((self.h,self.w),np.float32)
  for sx,sy,vx,vy,r,opacity,offset,life,phase in self.flakes:
   age=(float(t)+offset)%life
   fade=float(smoothstep(age/.65)*smoothstep((life-age)/.8))
   if fade==0:continue
   x=sx+vx*(age-life*.5)+1.8*np.sin(2*np.pi*age/life+phase);y=sy+vy*(age-life*.5)
   radius=int(np.ceil(r*3.3));x0=max(0,int(np.floor(x))-radius);x1=min(self.w,int(np.floor(x))+radius+2)
   y0=max(0,int(np.floor(y))-radius-1);y1=min(self.h,int(np.floor(y))+radius+3)
   if x0>=x1 or y0>=y1:continue
   yy,xx=np.mgrid[y0:y1,x0:x1]
   # Subpixel Gaussian footprints avoid integer-position stepping; small motion blur follows fall direction.
   footprint=np.zeros_like(xx,dtype=np.float32)
   for dt,weight in [(-.012,.25),(0,.5),(.012,.25)]:
    footprint+=np.exp(-.5*(((xx-x-vx*dt)/r)**2+((yy-y-vy*dt)/(r*1.1))**2)).astype(np.float32)*weight
   a=footprint*opacity*fade
   out[y0:y1,x0:x1]=1-(1-out[y0:y1,x0:x1])*(1-a)
  return out

 def frame(self,t,only=None,prototype=False):
  t=float(t)%self.duration
  if only in ('snowfall','beacons','additions'):f=self.base.copy()
  else:f=self.parent.frame(t,only,prototype)
  if only not in (None,'snowfall','beacons','additions'):return f
  f=f.astype(np.float32)
  if only in (None,'beacons','additions'):
   for b,(x0,y0,x1,y1),core,halo in self.beacons:
    strength=max(event_amount(t,b['period'],start,hold,b['transition']) for start,hold in b['pulses'])
    alpha=core*strength;patch=f[y0:y1,x0:x1]
    patch[:]=patch*(1-alpha[...,None])+np.array([255,110,75])*alpha[...,None]
    patch+=halo[...,None]*strength*np.array([200,23,9])
  if only in (None,'snowfall','additions'):
   a=self.snow_alpha(t);f=f*(1-a[...,None])+np.array(self.config['snow']['color'])*a[...,None]
  assert np.isfinite(f).all();f=np.uint8(np.rint(np.clip(f,0,255)))
  if only=='beacons':assert np.array_equal(f[~self.layer_masks['beacons']],self.base[~self.layer_masks['beacons']])
  return f

 def fingerprint(self):
  p=self.parent.fingerprint();deps=dict(p['dependencies'])
  deps['music/icebound-animation-v1/render_icebound.py']=p['renderer_sha256'];deps[self.config['baseline']]=p['config_sha256']
  return {'source_sha256':p['source_sha256'],'config_sha256':digest(self.path),'renderer_sha256':digest(__file__),'dependencies':deps,'effective_masks':{k:hashlib.sha256(v.tobytes()).hexdigest() for k,v in self.masks.items()}}

def samples(s):
 for t in [0,.7,1.3,2.3,4.7,8,12,16,19+29/30]:
  f=s.frame(t);Image.fromarray(f).save(H/f'sample-{t:.3f}s.png')
  if t in [.7,2.3]:Image.fromarray(f[25:160,205:310]).resize((420,540)).save(H/f'beacon-detail-{t:.1f}s.png')
 checks={}
 for name in ['snowfall','beacons']:
  mask=s.layer_masks[name];assert np.array_equal(s.frame(0,name),s.frame(20,name))
  seam=float(abs(s.frame(-1/30,name)[mask].astype(float)-s.frame(0,name)[mask]).mean())
  normal=[float(abs(s.frame(t+1/30,name)[mask].astype(float)-s.frame(t,name)[mask]).mean()) for t in np.arange(0,20,.5)]
  assert seam<=max(normal)*1.1+.01,(name,seam,max(normal))
  checks[name]={'periodic_endpoint_exact':True,'seam_mae':seam,'ordinary_max_sampled':max(normal),'pass':True}
 assert np.array_equal(s.snow_alpha(0),s.snow_alpha(20))
 for name in s.parent.layer_masks:
  for t in [0,8,16]:assert np.array_equal(s.frame(t,name),s.parent.frame(t,name))
 (H/'analytic-validation.json').write_text(json.dumps({'fingerprint':s.fingerprint(),'new_layers':checks,'v1_isolated_layers':'Exact at 0,8,16 seconds for every original layer','snow_lifetime_divides_loop':True,'snow_alpha_endpoint_exact':True,'user_motion_approved':False},indent=2)+'\n')
 print('V2 samples and new-layer analytic checks passed',flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['samples','isolated','preview'],required=True);a=p.parse_args();s=IceboundV2();clips=[]
 if a.stage=='samples':samples(s);return
 if a.stage=='isolated':
  out=H/'snow-and-beacons-isolated-v2-8s.mp4';item=encode(s,out,8,'additions');item['validation']=verify(s,out,240);clips.append(item)
 else:
  out=H/'icebound-weather-post-v2-preview-20s.mp4';item=encode(s,out,20);item['validation']=verify(s,out,600,True);clips.append(item)
  repeat=H/'icebound-weather-post-v2-three-loops-60s.mp4';assert not repeat.exists()
  subprocess.run([s.config['ffmpeg'],'-v','error','-n','-stream_loop','2','-i',str(out),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
  v=verify(s,repeat,1800,True);cap=cv2.VideoCapture(str(repeat));hashes=[]
  while True:
   ok,f=cap.read()
   if not ok:break
   hashes.append(hashlib.sha256(f.tobytes()).hexdigest())
  cap.release();assert hashes[:600]==hashes[600:1200]==hashes[1200:]
  clips.append({'path':repeat.relative_to(R).as_posix(),'sha256':digest(repeat),'validation':v,'three_repeated_decoded_payloads_identical':True})
  cap=cv2.VideoCapture(str(out));cap.set(cv2.CAP_PROP_POS_MSEC,4700);ok,f=cap.read();cap.release();assert ok;cv2.imwrite(str(H/'decoded-preview-4.7s.png'),f)
 (H/(a.stage+'-validation.json')).write_text(json.dumps({'fingerprint':s.fingerprint(),'clips':clips,'silent':True,'user_motion_approved':False,'inspection':'Temporal/decoded stills inspected; continuous playback not claimed'},indent=2)+'\n')
 print(a.stage+' checks passed',flush=True)
if __name__=='__main__':main()
