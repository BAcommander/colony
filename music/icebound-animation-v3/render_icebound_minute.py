"""Minute-long independent lighting, preserving accepted local weather cycles."""
from pathlib import Path
import sys,json,hashlib,argparse,subprocess
import cv2,numpy as np
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(H.parent/'icebound-animation-v2'))
from render_icebound_v2 import IceboundV2
from ambient_effects import event_amount
from render_floodplain import encode,verify,digest

class IceboundMinute:
 def __init__(self):
  self.old=IceboundV2();self.parent=self.old.parent;self.path=H/'scene-plan-v3.json';self.config=json.loads(self.path.read_text());self.duration=60
  accepted=json.loads((R/self.config['baseline']).read_text());assert self.old.fingerprint()==accepted['fingerprint']
  self.base=self.old.base;self.h,self.w=self.base.shape[:2];self.masks=dict(self.old.masks);self.layer_masks=dict(self.old.layer_masks);self.active=self.old.active
  self.weather_cache={};self.snow_cache={};self.cache_enabled=False

 def weather(self,t):
  local=float(t)%20;index=round(local*30)%600
  grid=abs(local*30-round(local*30))<1e-7
  if self.cache_enabled and grid and index in self.weather_cache:return self.weather_cache[index]
  f=self.parent.frame(local,'atmosphere')
  if self.cache_enabled and grid:self.weather_cache[index]=f
  return f

 def snow(self,t):
  local=float(t)%20;index=round(local*30)%600;grid=abs(local*30-round(local*30))<1e-7
  if self.cache_enabled and grid and index in self.snow_cache:return self.snow_cache[index]
  a=self.old.snow_alpha(local).ravel();idx=np.flatnonzero(a).astype(np.int32);pair=(idx,a[idx])
  if self.cache_enabled and grid:self.snow_cache[index]=pair
  return pair

 def amount(self,t,name):
  c=next(c for c,roi,mask in self.parent.lights if c['name']==name)
  return max(event_amount(t,60,start,hold,c['transition']) for start,hold in self.config['windows'][name])

 def frame(self,t,only=None,prototype=False):
  t=float(t)%60
  if only in ['sky','far_spindrift','basin_spindrift','snowfall']:return self.old.frame(t%20,only)
  f=(self.weather(t) if only is None else self.base).astype(np.float32)
  if only in (None,'lights','lighting'):
   for c,(x0,y0,x1,y1),mask in self.parent.lights:
    f[y0:y1,x0:x1]*=1-mask[...,None]*self.amount(t,c['name'])*(1-c['floor'])
  if only in (None,'entrance','lighting'):
   amount=max(event_amount(t,60,e['start'],e['hold'],e['transition'])*e['depth'] for e in self.config['entrance_events'])
   f*=1-self.parent.entrance[...,None]*amount*np.array([1,.92,.72])
  if only in (None,'room_spill','lighting'):
   f*=1-self.parent.room_spill[...,None]*self.amount(t,'main_room_right')*np.array([1,.88,.65])
  f=np.uint8(np.rint(np.clip(f,0,255))).astype(np.float32)
  if only in (None,'beacons','lighting'):
   for b,(x0,y0,x1,y1),core,halo in self.old.beacons:
    strength=max(event_amount(t,60,start,hold,b['transition']) for start,hold in self.config['beacon_events'][b['name']])
    alpha=core*strength;patch=f[y0:y1,x0:x1]
    patch[:]=patch*(1-alpha[...,None])+np.array([255,110,75])*alpha[...,None]
    patch+=halo[...,None]*strength*np.array([200,23,9])
  if only is None:
   idx,a=self.snow(t);flat=f.reshape(-1,3)
   flat[idx]=flat[idx]*(1-a[:,None])+np.array(self.old.config['snow']['color'])*a[:,None]
  assert np.isfinite(f).all();f=np.uint8(np.rint(np.clip(f,0,255)))
  if only in self.layer_masks:assert np.array_equal(f[~self.layer_masks[only]],self.base[~self.layer_masks[only]])
  return f

 def fingerprint(self):
  p=self.old.fingerprint();deps=dict(p['dependencies']);deps['music/icebound-animation-v2/render_icebound_v2.py']=p['renderer_sha256'];deps['music/icebound-animation-v2/scene-plan-v2.json']=p['config_sha256']
  return {'source_sha256':p['source_sha256'],'config_sha256':digest(self.path),'renderer_sha256':digest(__file__),'dependencies':deps,'effective_masks':p['effective_masks']}

def samples(s):
 for t in [0,.7,8,20,28,40,48,59+29/30]:Image.fromarray(s.frame(t)).save(H/f'sample-{t:.3f}s.png')
 preserved={}
 for name in ['sky','far_spindrift','basin_spindrift','snowfall']:
  for t in [0,8,19+29/30,28,40,59+29/30]:assert np.array_equal(s.frame(t,name),s.old.frame(t%20,name))
  assert np.array_equal(s.frame(0,name),s.frame(60,name));preserved[name]='Exact v2 source frames at six sampled times; unchanged 20-second local clock'
 checks={}
 for name in ['lights','entrance','room_spill','beacons']:
  mask=s.layer_masks[name];assert np.array_equal(s.frame(0,name),s.frame(60,name))
  seam=float(abs(s.frame(-1/30,name)[mask].astype(float)-s.frame(0,name)[mask]).mean())
  ordinary=[float(abs(s.frame(t+1/30,name)[mask].astype(float)-s.frame(t,name)[mask]).mean()) for t in np.arange(0,60,.5)]
  assert seam<=max(ordinary)*1.1+.01,(name,seam,max(ordinary));checks[name]={'exact_endpoint':True,'seam_mae':seam,'ordinary_max_sampled':max(ordinary),'pass':True}
 first=s.frame(0);assert np.array_equal(first,s.frame(60));assert not np.array_equal(first,s.frame(20));assert not np.array_equal(first,s.frame(40))
 (H/'analytic-validation.json').write_text(json.dumps({'fingerprint':s.fingerprint(),'preserved_weather':preserved,'new_light_schedule_seams':checks,'full_composite_endpoint_exact':True,'distinct_at_0_20_40_seconds':True,'weather_speed_change_percent':0,'user_new_schedule_approved':False},indent=2)+'\n')
 print('Minute samples, preserved weather and new schedule seams passed',flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['samples','preview'],required=True);a=p.parse_args();s=IceboundMinute()
 if a.stage=='samples':samples(s);return
 s.cache_enabled=True;out=H/'icebound-weather-post-v3-minute-720p.mp4';item=encode(s,out,60)
 print('Minute rendered; validating encoded frames and joins',flush=True)
 s.weather_cache.clear();s.snow_cache.clear();item['validation']=verify(s,out,1800,True)
 repeat=H/'icebound-weather-post-v3-three-minutes-720p.mp4';assert not repeat.exists()
 subprocess.run([s.config['ffmpeg'],'-v','error','-n','-stream_loop','2','-i',str(out),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
 print('Checking three complete minute repetitions',flush=True)
 validation=verify(s,repeat,5400,True);cap=cv2.VideoCapture(str(repeat));hashes=[]
 while True:
  ok,f=cap.read()
  if not ok:break
  hashes.append(hashlib.sha256(f.tobytes()).hexdigest())
 cap.release();assert hashes[:1800]==hashes[1800:3600]==hashes[3600:]
 assert hashes[0]!=hashes[600] and hashes[0]!=hashes[1200]
 cap=cv2.VideoCapture(str(out));cap.set(cv2.CAP_PROP_POS_MSEC,28700);ok,f=cap.read();cap.release();assert ok;cv2.imwrite(str(H/'decoded-preview-28.7s.png'),f)
 record={'fingerprint':s.fingerprint(),'clips':[item,{'path':repeat.relative_to(R).as_posix(),'sha256':digest(repeat),'validation':validation,'three_repeated_decoded_payloads_identical':True}],'distinct_at_0_20_40_seconds':True,'silent':True,'user_new_schedule_approved':False,'inspection':'Temporal and decoded stills; no continuous playback claim'}
 (H/'preview-validation.json').write_text(json.dumps(record,indent=2)+'\n');print('Sixty-second preview and repeat checks passed',flush=True)
if __name__=='__main__':main()
