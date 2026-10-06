"""Minute adapter: retained periodic environment plus unique minute-wide local lighting."""
from pathlib import Path
import sys,json,hashlib,argparse,subprocess,time
import cv2,numpy as np
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parents[1];V2=H.parent/'shoreless-animation-v2'
sys.path.insert(0,str(V2))
from render_shoreless_v2 import ShorelessV2
from render_shoreless import Shoreless,verify
from render_floodplain import encode,digest
from ambient_effects import smoothstep,event_amount

class ShorelessV3(ShorelessV2):
 def __init__(self):
  super().__init__()
  self.path=H/'scene-plan-v3.json';self.config=json.loads(self.path.read_text());c=self.config
  assert digest(V2/'render_shoreless_v2.py')==c['v2_renderer_sha256']
  self.loop_duration=c['duration'];self.duration=c['environment_period']
  # Inherited atmosphere/foam/left UI use their original periods and speeds.
  wc=dict(c['water']);a,b,z,d=wc['roi'];xx=self.x[b:d,a:z]
  start,end=c['far_right_water']['transition_x'];self.calm=smoothstep((xx-start)/(end-start))
  wc['displacement_scale']=wc['displacement_scale']*(1-self.calm*(1-c['far_right_water']['displacement_multiplier']))
  self.water.c=wc
  self.lights=[(lc,m) for lc,(_,m) in zip(c['lights'],self.lights)]
  self.practicals=[(lc,m) for lc,(_,m) in zip(c['exterior_flickers'],self.practicals)]
  self.walkway=[];wm=np.zeros_like(self.x)
  rgb=self.base.astype(np.float32);warm=np.clip((rgb[:,:,0]-rgb[:,:,2]-2)/26,0,1)
  for lc in c['walkway_lights']:
   x,y=lc['center'];rx,ry=lc['radius'];sx,sy=lc['spill_radius']
   core=np.exp(-((self.x-x)/rx)**4-((self.y-y)/ry)**4)
   spill=np.exp(-((self.x-x)/sx)**2-((self.y-y)/sy)**2)*warm*.24
   m=np.maximum(core,spill).astype(np.float32);m[m<.003]=0
   wm=np.maximum(wm,m);self.walkway.append((lc,m))
  self.masks['walkway']=wm
  self.layer_masks={k:v>0 for k,v in self.masks.items()};self.active=np.logical_or.reduce(list(self.layer_masks.values()))
  self.local_masks={}
  for key,m in self.masks.items():self.local_masks[key]=self.crop_mask(m)
  self.local_lights=[(lc,self.crop_mask(m)) for lc,m in self.lights]
  self.local_practicals=[(lc,self.crop_mask(m)) for lc,m in self.practicals]
  self.local_walkway=[(lc,self.crop_mask(m)) for lc,m in self.walkway]
  self.local_antennas=[(lc,self.crop_mask(m)) for lc,m in self.antennas]
  self.local_beacons=[(lc,self.crop_mask(m)) for lc,m in self.beacons]
  self.cache=None

 def crop_mask(self,m):
  yy,xx=np.where(m>0);a,b,z,d=int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1
  return (a,b,z,d),m[b:d,a:z]

 def amount(self,t,events):
  return max((event_amount(t,self.loop_duration,e['start'],e['hold'],e['transition'])*e['depth'] for e in events),default=0)

 def dim(self,f,local,amount):
  if not amount:return
  (a,b,z,d),m=local;f[b:d,a:z]*=1-m[...,None]*amount

 def draw_computers(self,f,t):
  # Preserve v2 left screen exactly; omit its oversized replacement waveform.
  Shoreless.draw_computers(self,f,t%self.duration)
  a,b,z,d=self.ui_roi;patch=f[b:d,a:z].copy();x=self.ui_x;y=self.ui_y
  route=np.float32(self.config['computers']['route'])
  for j in range(len(route)-1):
   line=np.zeros(patch.shape[:2],np.uint8);p=route[j]-[a,b];q=route[j+1]-[a,b]
   cv2.line(line,tuple(np.rint(p*256).astype(int)),tuple(np.rint(q*256).astype(int)),255,2,cv2.LINE_AA,8)
   patch+=(line.astype(np.float32)/255)[...,None]*event_amount(t,20,1+j*2.7,3,.6)*np.float32([20,69,81])
  for j,(cx,cy) in enumerate(route[[1,3,4]]):
   ring=np.exp(-((np.sqrt((x-cx)**2+(y-cy)**2)-4)/.8)**2)*event_amount(t,20,2+j*5,3.5,.7)
   patch+=ring[...,None]*np.float32([33,100,118])
  rc=self.config['right_screen'];phase=2*np.pi*t/rc['period'];cx,cy=rc['tracking_center'];rx,ry=rc['tracking_half_size']
  cx+=rc['travel_pixels']*np.sin(phase);cy+=np.sin(phase)
  ink=np.zeros(patch.shape[:2],np.uint8)
  for dx in [-1,1]:
   for dy in [-1,1]:
    p=(cx+dx*rx-a,cy+dy*ry-b)
    for q in [(p[0]-dx*3,p[1]),(p[0],p[1]-dy*2)]:
     cv2.line(ink,tuple(np.rint(np.array(p)*256).astype(int)),tuple(np.rint(np.array(q)*256).astype(int)),255,1,cv2.LINE_AA,8)
  patch+=(ink.astype(np.float32)/255)[...,None]*(.6+.4*np.sin(phase*.5)**2)*np.float32(rc['color'])
  for j,(cx,cy) in enumerate(rc['nodes']):
   glow=np.exp(-((x-cx)**2+(y-cy)**2)/3)*(.5-.5*np.cos(phase+j*np.pi))
   patch+=glow[...,None]*np.float32([12,35,43])
  f[b:d,a:z]+=self.ui_mask[...,None]*(patch-f[b:d,a:z])

 def environment(self,t,only=None):
  t=t%self.duration;f=self.base.astype(np.float32)
  if only in (None,'water'):
   a,b,z,d=self.config['water']['roi'];f[b:d,a:z]=self.water.frame(t)
  if only in (None,'sky'):
   for cc,(a,b,z,d),m,clean,x,y,offset in self.clouds:
    moving=np.zeros_like(clean)
    for phase in [0,.5]:
     age=(t/self.duration+offset+phase)%1;weight=np.sin(np.pi*age)**2
     moved=cv2.remap(clean,(x-cc['speed']*self.duration*(age-.5)).astype(np.float32),y,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
     moving+=moved*weight[...,None]
    f[b:d,a:z]+=m[...,None]*(moving-clean)*cc['gain']
  if only in (None,'turbines'):
   for tc,(a,b,z,d),rad,residual,clean,static in self.rotors:
    mat=cv2.getRotationMatrix2D((rad,rad),tc['direction']*360*t/tc['period'],1)
    patch=clean+cv2.warpAffine(residual,mat,(z-a,d-b),flags=cv2.INTER_LINEAR);patch[static]=self.base[b:d,a:z][static]
    m=self.masks['turbines'][b:d,a:z,None];f[b:d,a:z]=f[b:d,a:z]*(1-m)+patch*m
  if only in (None,'beacons'):
   for bc,((a,b,z,d),m) in self.local_beacons:
    age=(t-bc['phase'])%bc['period'];pulse=float(smoothstep(age/.12)*smoothstep((.65-age)/.18))
    f[b:d,a:z]+=m[...,None]*pulse*np.float32([84,15,8])
  f=np.rint(np.clip(f,0,255)).astype(np.float32)
  if only in (None,'foam'):self.add_foam(f,t)
  if only in (None,'antennas'):
   for ac,((a,b,z,d),m) in self.local_antennas:
    age=(t-ac['phase'])%20;local=age%ac['period'];pulse=float(smoothstep(local/.12)*smoothstep((.7-local)/.18))
    col=np.float32([242,48,29] if int(age/ac['period'])%2==0 else [54,225,126]);alpha=m[...,None]*pulse*.88
    f[b:d,a:z]=f[b:d,a:z]*(1-alpha)+col*alpha
  return f

 def frame(self,t,only=None,prototype=False):
  t=float(t)%self.loop_duration
  environment_layers=['water','sky','turbines','beacons','foam','antennas']
  if only in environment_layers:f=self.environment(t,only)
  elif only is None:
   # Float32 cache preserves exact source composites before local light changes.
   idx=round(t*30)%600
   if self.cache is not None and abs(t*30-round(t*30))<1e-6:
    p=self.cache/f'{idx:04d}.npy'
    if p.exists():f=np.load(p)
    else:
     f=self.environment(t);np.save(p,f)
   else:f=self.environment(t)
  else:f=self.base.astype(np.float32)
  if only in (None,'lights'):
   for lc,m in self.local_lights:
    self.dim(f,m,self.amount(t,lc['holds']));self.dim(f,m,self.amount(t,lc['flickers']))
   for lc,m in self.local_practicals:self.dim(f,m,self.amount(t,lc['events']))
  if only in (None,'walkway'):
   for lc,m in self.local_walkway:self.dim(f,m,self.amount(t,lc['events']))
  if only in (None,'lamp','room'):self.dim(f,self.local_masks['lamp'],self.amount(t,self.config['lamp']['events']))
  if only in (None,'computers','room'):self.draw_computers(f,t)
  if only in (None,'sunlight'):
   sc=self.config['sunlight'];amount=self.amount(t,sc['events'])
   if amount:
    (a,b,z,d),_=self.local_masks['sunlight'];patch=f[b:d,a:z]
    patch+=amount*(self.sun_sky[b:d,a:z,None]*np.float32(sc['sky_gain'])+self.sun_shafts[b:d,a:z,None]*np.float32(sc['shaft_gain']))
    response=.35+.65*np.clip((patch.mean(2)-35)/80,0,1)
    patch+=self.sun_water[b:d,a:z,None]*response[...,None]*amount*np.float32(sc['water_gain'])
  assert np.isfinite(f).all();f=np.uint8(np.rint(np.clip(f,0,255)))
  mask=self.active if only is None else self.layer_masks[only]
  assert np.array_equal(f[~mask],self.base[~mask]),'Protected pixels changed'
  return f

 def fingerprint(self):
  return {'source_sha256':self.config['source']['sha256'],'config_sha256':digest(self.path),'renderer_sha256':digest(__file__),'dependencies':{p:digest(R/p) for p in ['music/shoreless-animation-v2/render_shoreless_v2.py','music/shoreless-animation-v1/render_shoreless.py','scripts/render_floodplain.py','scripts/water_surface.py','scripts/ambient_effects.py']},'masks':{k:hashlib.sha256(v.tobytes()).hexdigest() for k,v in self.masks.items()}}

def samples(s):
 (H/'masks').mkdir(exist_ok=True)
 for k,m in s.masks.items():cv2.imwrite(str(H/'masks'/f'{k}.png'),np.uint8(np.rint(m*255)))
 a,b,z,d=s.config['water']['roi'];im=s.base.astype(np.float32);im[b:d,a:z]+=s.calm[...,None]*s.masks['water'][b:d,a:z,None]*np.float32([70,5,0]);Image.fromarray(np.uint8(np.clip(im,0,255))).save(H/'local-water-adjustment.png')
 for t in [0,5.12,8,13.64,20,32.85,40,51.35,59+29/30]:Image.fromarray(s.frame(t)).save(H/f'sample-{t:.3f}s.png')
 for k,box in [('walkway',(460,402,497,448)),('right-monitor',(1495,490,1648,614))]:
  Image.fromarray(s.frame(5.12)).crop(box).resize(((box[2]-box[0])*4,(box[3]-box[1])*4)).save(H/f'{k}-active.png')
 checks={}
 for key,m in s.layer_masks.items():
  assert np.array_equal(s.frame(0,key),s.frame(60,key))
  vals=[]
  for t in [-1/30,0,5.1,7,13.6,20,32.8,40,51.3]:vals.append(float(np.abs(s.frame(t+1/30,key)[m].astype(float)-s.frame(t,key)[m]).mean()))
  assert vals[0]<=max(vals[1:])*1.1+.01,(key,vals)
  checks[key]={'endpoint_exact':True,'seam_mae':vals[0],'ordinary_max_sampled':max(vals[1:]),'pass':True}
 old=ShorelessV2();reg={}
 for layer in ['sky','turbines','beacons','antennas']:
  reg[layer]=all(np.array_equal(s.frame(t,layer),old.frame(t,layer)) for t in [0,7]);assert reg[layer]
 keep=s.x<1085
 reg['water_left_of_1085']=all(np.array_equal(s.frame(t,'water')[keep],old.frame(t,'water')[keep]) for t in [0,7]);assert reg['water_left_of_1085']
 left=(s.x>=1350)&(s.x<1490)&(s.y>=480)&(s.y<610)
 reg['left_monitor']=all(np.array_equal(s.frame(t,'computers')[left],old.frame(t%20,'computers')[left]) for t in [0,7,27,47]);assert reg['left_monitor']
 distinct=len({hashlib.sha256(s.frame(t).tobytes()).hexdigest() for t in [0,20,40]})==3;assert distinct
 (H/'analytic-validation.json').write_text(json.dumps({'fingerprint':s.fingerprint(),'layers':checks,'retained_v2_sampled_exact':reg,'distinct_0_20_40':distinct,'environment_frequency_change_percent':0,'user_motion_approved':False},indent=2)+'\n')
 print('Analytic seams, source protection, local water/left screen regression and distinct minute states passed',flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['samples','isolated','preview'],required=True);args=p.parse_args();s=ShorelessV3()
 if args.stage=='samples':samples(s);return
 clips=[]
 if args.stage=='isolated':
  for layer in s.config['isolated_layers']:
   out=H/f'{layer}-isolated-v3-8s.mp4';item=encode(s,out,8,layer);item['validation'],_=verify(s,out,240,False);clips.append(item);print(layer,'isolated passed',flush=True)
 else:
  cache=H/'.environment-cache';cache.mkdir(exist_ok=True);(cache/'.gitignore').write_text('*\n')
  marker=cache/'fingerprint.json';finger=s.fingerprint()
  if marker.exists():assert json.loads(marker.read_text())==finger
  else:marker.write_text(json.dumps(finger,indent=2)+'\n')
  s.cache=cache
  out=H/'shoreless-colony-v3-preview-60s.mp4';item=encode(s,out,60);item['validation'],hs=verify(s,out,1800,True);assert hs[:600]!=hs[600:1200] and hs[600:1200]!=hs[1200:];item['three_distinct_twenty_second_sections']=True;clips.append(item)
  repeat=H/'shoreless-colony-v3-three-loops-180s.mp4';assert not repeat.exists()
  subprocess.run([s.config['ffmpeg'],'-v','error','-n','-stream_loop','2','-i',str(out),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
  val,rhs=verify(s,repeat,5400,True);assert rhs==hs*3;clips.append({'path':repeat.relative_to(R).as_posix(),'sha256':digest(repeat),'validation':val,'three_repeated_decoded_payloads_identical':True})
  cap=cv2.VideoCapture(str(out));cap.set(cv2.CAP_PROP_POS_MSEC,8000);ok,f=cap.read();cap.release();assert ok;cv2.imwrite(str(H/'decoded-preview-8s.png'),f)
 (H/f'{args.stage}-validation.json').write_text(json.dumps({'fingerprint':s.fingerprint(),'clips':clips,'silent':True,'user_motion_approved':False},indent=2)+'\n')
 print(args.stage,'checks passed',flush=True)
if __name__=='__main__':main()
