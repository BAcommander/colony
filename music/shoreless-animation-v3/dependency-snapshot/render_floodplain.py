"""Source-bound Floodplain adapter. Existing approved renderers are unchanged."""
from pathlib import Path
import argparse,hashlib,json,subprocess,time
import cv2,numpy as np
from PIL import Image
from ambient_effects import smoothstep,event_amount
from water_surface import ReflectionSurface
ROOT=Path(__file__).resolve().parents[1]
cv2.setNumThreads(4)
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

class ChannelSurface(ReflectionSurface):
 def __init__(self,plate,mask,c,origin):
  super().__init__(plate,mask,c)
  # Remap the reusable wave normals onto this channel's perspective, not Glacier's.
  gx=self.x+origin[0];gy=self.y+origin[1]
  distance=c['perspective_distance_scale']/np.maximum(gy-c['perspective_horizon_y'],10)
  self.world_x=(gx-c['perspective_center_x'])*distance/c['perspective_lateral_scale'];self.world_z=distance
  rng=np.random.default_rng(c['seed']);self.waves=[];self.wave_filters=[];self.speed_deviations=[]
  for i in range(c['components']):
   theta=rng.normal(1.10,.55);length=rng.uniform(*c['wavelength_range']);k=2*np.pi/length
   direction=np.array([np.cos(theta),np.sin(theta)])
   phase=k*(direction[0]*self.world_x+direction[1]*self.world_z)+rng.uniform(0,2*np.pi)
   natural=np.sqrt(9.81*k)*c['time_scale'];omega=2*np.pi*max(1,round(natural*c['loop_seconds']/(2*np.pi)))/c['loop_seconds']
   amp=(length/c['wavelength_range'][1])**.4;self.waves.append((phase.astype(np.float32),omega,amp,direction))
   py,px=np.gradient(phase);self.wave_filters.append(np.exp(-.5*c['sampling_filter_pixels']**2*(px*px+py*py)).astype(np.float32))
   self.speed_deviations.append(float(omega/natural-1))
  self.norm=sum(w[2]**2 for w in self.waves)**.5

class Floodplain:
 def __init__(self,path):
  self.path=Path(path);self.config=json.loads(self.path.read_text());c=self.config
  src=ROOT/c['source']['path'];assert digest(src)==c['source']['sha256']
  self.base=np.array(Image.open(src).convert('RGB'));self.duration=c['duration'];self.h,self.w=self.base.shape[:2]
  assert [self.w,self.h]==c['source']['dimensions']
  self.masks={k:cv2.imread(str(self.path.parent/v),0).astype(np.float32)/255 for k,v in c['masks'].items()}
  self.layer_masks={k:v>0 for k,v in self.masks.items() if k!='active'};self.active=self.masks['active']>0
  self.clouds=[]
  for roi in c['sky']['regions']:
   x0,y0,x1,y1=roi;patch=self.base[y0:y1,x0:x1];m=self.masks['sky'][y0:y1,x0:x1]
   invalid=np.uint8(m<.05)*255
   for shape in c['sky']['exclusions']:
    if 'ellipse' in shape:
     sx,sy,rx,ry=shape['ellipse'];cv2.ellipse(invalid,(sx-x0,sy-y0),(rx,ry),0,0,360,255,-1)
    else:
     ax,ay,bx,by=shape['rectangle'];cv2.rectangle(invalid,(ax-x0,ay-y0),(bx-x0,by-y0),255,-1)
   clean=cv2.inpaint(patch,invalid,7,cv2.INPAINT_TELEA)
   clean=cv2.GaussianBlur(clean.astype(np.float32),(0,0),c['sky']['source_clean_sigma'])
   y,x=np.mgrid[:y1-y0,:x1-x0].astype(np.float32)
   self.clouds.append((roi,m,clean,x,y,(y+y0)/500+(x+x0)/2200))
  wc=c['water'];x0,y0,x1,y1=wc['roi'];self.water=ChannelSurface(self.base[y0:y1,x0:x1],self.masks['water'][y0:y1,x0:x1],wc,(x0,y0))
 def frame(self,t,only=None,prototype=False):
  t=float(t)%self.duration;f=self.base.astype(np.float32)
  if only in (None,'sky'):
   for (x0,y0,x1,y1),mask,clean,x,y,offset in self.clouds:
    if prototype:
     moving=cv2.remap(clean,x-self.config['sky']['speed']*t,y,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
    else:
     moving=np.zeros_like(clean)
     for shift in (0,.5):
      age=(t/self.duration+offset+shift)%1;weight=np.sin(np.pi*age)**2
      mx=x-self.config['sky']['speed']*self.duration*(age-.5)
      layer=cv2.remap(clean,mx.astype(np.float32),y,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
      moving+=layer*weight[...,None]
    f[y0:y1,x0:x1]+=mask[...,None]*(moving-clean)
  if only in (None,'water'):
   x0,y0,x1,y1=self.config['water']['roi'];f[y0:y1,x0:x1]=self.water.frame(t)
  if only in (None,'lights'):
   for light in self.config['lights']:
    x0,y0,x1,y1=light['roi'];m=self.masks['lights'][y0:y1,x0:x1]
    amount=event_amount(t,self.duration,light['start'],light['hold'],light['transition'])
    f[y0:y1,x0:x1]*=1-m[...,None]*amount*(1-light['floor'])
    flicker=max((event_amount(t,self.duration,e['start'],e['hold'],e['transition'])*e['depth'] for e in light.get('flickers',[])),default=0)
    f[y0:y1,x0:x1]*=1-m[...,None]*flicker
  if only in (None,'lamp') and 'lamp' in self.config:
   flicker=max((event_amount(t,self.duration,e['start'],e['hold'],e['transition'])*e['depth'] for e in self.config['lamp']['flickers']),default=0)
   f*=1-self.masks['lamp'][...,None]*flicker
  if only in (None,'screen'):
   c=self.config['screen'];x0,y0,x1,y1=c['roi'];y,x=np.mgrid[y0:y1,x0:x1]
   # A small chart marker traveling right and fading locally at the wrap.
   phase=t/c['period'];center=x0+4+phase*(x1-x0-8);height=y0+35+3*np.sin(2*np.pi*phase)
   alpha=np.exp(-((x-center)**2/3+(y-height)**2/2))*np.sin(np.pi*phase)**2*self.masks['screen'][y0:y1,x0:x1]
   f[y0:y1,x0:x1]+=alpha[...,None]*np.array([.35,.8,1])*c['strength']
  if only in (None,'beacon'):
   c=self.config['beacon'];x0,y0,x1,y1=c['roi'];m=self.masks['beacon'][y0:y1,x0:x1]
   dim=.65*(.5-.5*np.cos(2*np.pi*t/c['period']))
   f[y0:y1,x0:x1]*=1-m[...,None]*dim
  f=np.uint8(np.rint(np.clip(f,0,255)))
  mask=self.active if only is None else self.layer_masks[only]
  assert np.array_equal(f[~mask],self.base[~mask]),'Protected pixels changed'
  return f
 def fingerprint(self):
  paths=[self.config['source']['path'],'scripts/render_floodplain.py','scripts/water_surface.py','scripts/ambient_effects.py']
  return {'config_sha256':digest(self.path),'files':{p:digest(ROOT/p) for p in paths},'masks':{k:digest(self.path.parent/v) for k,v in self.config['masks'].items()}}

def encode(scene,out,seconds,only=None,prototype=False):
 assert not out.exists(),f'Preserve existing {out}'
 fps=scene.config['fps'];w,h=scene.config['preview_size'];count=round(seconds*fps)
 proc=subprocess.Popen([scene.config['ffmpeg'],'-v','error','-n','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(fps),'-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-qp','0','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],stdin=subprocess.PIPE)
 started=time.time()
 try:
  for i in range(count):
   f=scene.frame(i/fps,only,prototype);f=cv2.resize(f,(w,h),interpolation=cv2.INTER_AREA)
   proc.stdin.write(f.tobytes())
   if i and i%150==0:print(out.name,i,'/',count,round(time.time()-started,1),'s',flush=True)
 finally:proc.stdin.close()
 assert proc.wait()==0
 return {'path':out.relative_to(ROOT).as_posix(),'sha256':digest(out),'frames':count,'seconds':seconds,'layer':only or 'combined','prototype':prototype}

def verify(scene,path,expected,loop=False):
 cap=cv2.VideoCapture(str(path));fps=cap.get(cv2.CAP_PROP_FPS);first=None;prev=None;deltas={};timestamps=[];count=0
 masks={k:cv2.resize(v.astype(np.uint8),(1280,720),interpolation=cv2.INTER_NEAREST)>0 for k,v in {**scene.layer_masks,'combined':scene.active}.items()}
 values={k:[] for k in masks};first_samples={};last_samples={}
 while True:
  ok,f=cap.read()
  if not ok:break
  assert f.shape==(720,1280,3);timestamps.append(cap.get(cv2.CAP_PROP_POS_MSEC)/1000)
  if first is None:first=f.copy()
  for name,mask in masks.items():
   current=f[mask].astype(np.float32)
   if count==0:first_samples[name]=current
   else:values[name].append(float(np.abs(current-last_samples[name]).mean()))
   last_samples[name]=current
  prev=f;count+=1
 cap.release();assert count==expected and fps==30,(count,expected,fps)
 assert np.max(np.abs(np.array(timestamps)-np.arange(count)/30))<.0001,'Non-sequential timestamps'
 if loop:
  for name in masks:
   seam=float(np.abs(last_samples[name]-first_samples[name]).mean());ordinary=max(values[name]);med=float(np.median(values[name]))
   assert seam<=ordinary*1.1+.01,(name,seam,ordinary)
   deltas[name]={'seam_mae':seam,'ordinary_max_mae':ordinary,'ordinary_median_mae':med,'pass':True}
 return {'decoded_frames':count,'fps':fps,'sequential_timestamps':True,'seam_checks':deltas}

def main():
 p=argparse.ArgumentParser();p.add_argument('--config',default='final/04-floodplain-keeper/animation-v1/scene-plan-v1.json');p.add_argument('--stage',choices=['samples','isolated','preview'],required=True);a=p.parse_args()
 scene=Floodplain(ROOT/a.config);out=ROOT/scene.config['output_dir'];out.mkdir(parents=True,exist_ok=True);reportdir=scene.path.parent
 if a.stage=='samples':
  for t in [0,4,8,12,16]:
   f=scene.frame(t);Image.fromarray(f).save(out/f'sample-{t:02d}.png')
  frames=[cv2.resize(scene.frame(t),(640,360)) for t in [0,4,8,12]]
  Image.fromarray(np.concatenate([np.concatenate(frames[:2],axis=1),np.concatenate(frames[2:],axis=1)],axis=0)).save(out/'temporal-sheet.png')
  endpoint={}
  for layer in scene.layer_masks:
   f0=scene.frame(0,layer);fend=scene.frame(scene.duration,layer);assert np.array_equal(f0,fend)
   m=scene.layer_masks[layer];near=[scene.frame(t,layer)[m].astype(float) for t in [-1/30,0,1/30]]
   endpoint[layer]={'periodic_endpoint_exact':True,'left_step_mae':float(abs(near[1]-near[0]).mean()),'right_step_mae':float(abs(near[2]-near[1]).mean())}
  deviations=np.array(scene.water.speed_deviations)
  (reportdir/'analytic-validation.json').write_text(json.dumps({'fingerprint':scene.fingerprint(),'layer_periodicity':endpoint,'water_speed_deviation_mean_absolute_percent':float(np.abs(deviations).mean()*100),'water_speed_deviation_max_absolute_percent':float(np.abs(deviations).max()*100),'water_speed_deviations_percent':(deviations*100).tolist(),'water_active_source_pixels':int(scene.layer_masks['water'].sum()),'protected_pixels':'Exact for every generated source frame; encoding/resizing may alter pixels.','visual_approval':False},indent=2)+'\n')
  print('Samples and analytic checks saved',flush=True)
 elif a.stage=='isolated':
  clips=[]
  for layer in ['water','sky']:
   item=encode(scene,out/f'{layer}-isolated-8s.mp4',8,layer)
   item['validation']=verify(scene,ROOT/item['path'],240);clips.append(item)
  (reportdir/'isolated-review.json').write_text(json.dumps({'fingerprint':scene.fingerprint(),'clips':clips,'status':'awaiting normal-speed user review; samples only inspected by assistant'},indent=2)+'\n')
 else:
  version=scene.config['version']
  item=encode(scene,out/f'floodplain-keeper-{version}-preview-20s.mp4',20)
  item['validation']=verify(scene,ROOT/item['path'],600,True)
  repeat=out/f'floodplain-keeper-{version}-three-loops-60s.mp4';assert not repeat.exists()
  subprocess.run([scene.config['ffmpeg'],'-v','error','-n','-stream_loop','2','-i',str(ROOT/item['path']),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
  repeat_validation=verify(scene,repeat,1800,True)
  # Verify each repeated decoded pixel payload, not only metadata duration.
  cap=cv2.VideoCapture(str(repeat));hashes=[]
  while True:
   ok,f=cap.read()
   if not ok:break
   hashes.append(hashlib.sha256(f.tobytes()).digest())
  cap.release();assert hashes[:600]==hashes[600:1200]==hashes[1200:1800]
  cap=cv2.VideoCapture(str(ROOT/item['path']));ok,decoded=cap.read();cap.release();assert ok;cv2.imwrite(str(out/'decoded-frame.png'),decoded)
  report={'fingerprint':scene.fingerprint(),'preview':item,'repeated_preview':{'path':repeat.relative_to(ROOT).as_posix(),'sha256':digest(repeat),'validation':repeat_validation,'three_decoded_payloads_identical':True},'user_approval':False,'inspection':'Source/mask and temporal still samples inspected; no continuous playback claim.','source_detail':'1672x941 native; 720p review. No 4K export during first-version review.'}
  (reportdir/'delivery-validation.json').write_text(json.dumps(report,indent=2)+'\n');print('Complete preview and repeated payload checks passed',flush=True)
if __name__=='__main__':main()
