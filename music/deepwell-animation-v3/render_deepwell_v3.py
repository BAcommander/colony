"""Deepwell v3: exact whole-pane glazing, anchored vapor and mounted pipe indicators."""
from pathlib import Path
import sys,json,hashlib,argparse,subprocess,time,platform
sys.dont_write_bytecode=True
sys.path.insert(0,r'C:\AI\ComfyUI\venv\Lib\site-packages')
H=Path(__file__).resolve().parent;S=H/'v2-snapshot'
# Load the current output helper before importing the frozen renderer, so media
# diagnostics go to v3, never into the immutable v2 snapshot.
from review_tools import encode,decode_verify
sys.path.insert(0,str(S))
import render_deepwell_v2 as previous
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
from ambient_effects import smoothstep,event_amount
cv2.setNumThreads(4)
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,value):(H/name).write_text(json.dumps(value,indent=2)+'\n')
def cut(a,r):x0,y0,x1,y1=r;return a[y0:y1,x0:x1]
def bounds(m):
 y,x=np.nonzero(m>0);return (int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1))

class Steam:
 def __init__(self,c,occlusion):
  self.c=c;self.r=tuple(c['roi']);a,b,z,d=self.r;self.y,self.x=np.mgrid[b:d,a:z].astype(np.float32)
  sx,sy=c['anchor'];u=(sy-self.y)/c['height'];self.u=np.clip(u,0,1).astype(np.float32)
  rng=np.random.default_rng(c['seed']);self.phases=rng.uniform(0,2*np.pi,3).astype(np.float32)
  center=sx+c['drift']*self.u
  corridor=2.7+c['width']*self.u*2.0
  self.mask=np.float32((u>0)&(u<1)&(abs(self.x-center)<corridor+5))
  self.mask*=1-cut(occlusion,self.r).astype(np.float32)
  self.mask*=smoothstep((self.x-a)/3)*smoothstep((z-1-self.x)/3)*smoothstep((self.y-b)/3)*smoothstep((d-1-self.y)/2)
  self.mask[self.mask<.001]=0
 def density(self,t):
  c=self.c;u=self.u;sx,sy=c['anchor'];flow=np.float32(2*np.pi)*(u-np.float32(t/c['lifetime']))
  tau=np.zeros_like(u);width=.70+c['width']*u*.62
  for i,ph in enumerate(self.phases):
   curl=u*(2.3*np.sin(flow*1.0+ph)+1.15*np.sin(flow*2.0+ph*.7))
   if c['kind']=='vent':curl*=.85
   center=sx+c['drift']*u+curl+(i-1)*(.7+u*c['width']*.33)
   ribbon=np.exp(-.5*((self.x-center)/np.maximum(width*(.65+i*.09),.5))**2)
   detail=np.clip(.36+.40*np.sin(flow*3.0+ph+(self.x-sx)*.25)+.24*np.sin(flow*5.0-ph*.6),0,1)
   tau+=ribbon*detail*(.75 if i==1 else .52)
  # Material features travel upward with u=t/lifetime+constant. Birth-time
  # variation travels with them, instead of fading the whole plume at once.
  birth=t-u*c['lifetime']
  if c['kind']=='coffee':emission=c['baseline']+(1-c['baseline'])*(.5+.5*np.sin(2*np.pi*birth/20+.6))
  else:
   emission=np.zeros_like(u)+c['baseline']
   for e in c['events']:emission=np.maximum(emission,c['baseline']+(1-c['baseline'])*event_amount(birth,20,e['start'],e['hold'],e['transition']))
  envelope=smoothstep(u/.065)*smoothstep((1-u)/.30)*np.maximum(1-u,0)**.45
  tau*=envelope*emission*c['opacity']
  alpha=(1-np.exp(-tau))*self.mask
  return np.clip(alpha,0,.42).astype(np.float32)

class DeepwellV3(previous.DeepwellV2):
 def __init__(self):
  started=time.time();super().__init__();self.v2_config=self.config;self.old_window_mask=self.masks['lights'].copy()
  self.config=json.loads((H/'scene-plan-v3.json').read_text());c=self.config;assert digest(H/c['source']['path'])==c['source']['sha256']
  self.make_windows();self.make_steam();self.make_pipeline()
  self.layer_masks={k:v>0 for k,v in self.masks.items()};self.active=np.logical_or.reduce(list(self.layer_masks.values()))
  self.groups=c['isolated_groups'];self.group_masks={k:np.logical_or.reduce([self.layer_masks[n] for n in names]) for k,names in self.groups.items()}
  print('Deepwell v3 ready',round(time.time()-started,2),'s;',len(self.layer_masks),'layers;',len(self.panes),'mapped panes',flush=True)
 def glazing(self,poly):
  c=self.config['window_panes'];ss=c['supersampling'];p=np.asarray(poly,np.float32);a,b=np.maximum(np.floor(p.min(0)).astype(int)-1,0);z,d=np.minimum(np.ceil(p.max(0)).astype(int)+2,[self.w,self.h])
  hi=np.zeros(((d-b)*ss,(z-a)*ss),np.uint8);cv2.fillPoly(hi,[np.rint((p-[a,b])*ss).astype(np.int32)],1)
  # Feather inward at supersampled resolution. No Gaussian blur can leak onto
  # an adjacent mullion, stone reveal or the large centre pillar.
  dist=cv2.distanceTransform(hi,cv2.DIST_L2,5);alpha=smoothstep(dist/(ss*c['inward_feather_pixels'])).astype(np.float32)
  lo=cv2.resize(alpha,(z-a,d-b),interpolation=cv2.INTER_AREA);lo[lo<.001]=0
  full=np.zeros((self.h,self.w),np.float32);full[b:d,a:z]=lo;return full
 def make_windows(self):
  c=self.config['window_panes'];self.panes=[];self.windows=[];all_glass=np.zeros((self.h,self.w),np.float32);active=all_glass.copy()
  stiles=np.zeros((self.h,self.w),np.uint8)
  for x0,y0,x1,y1 in c['fixed_mullion_lines']:cv2.line(stiles,(x0,y0),(x1,y1),1,1)
  for pane in c['panes']:
   m=self.glazing(pane['polygon']);m[stiles>0]=0;self.panes.append((pane,m));all_glass=np.maximum(all_glass,m)
  for light in self.config['lights']:
   m=np.maximum.reduce([pm for pane,pm in self.panes if pane['group']==light['name']]);r=bounds(m);self.windows.append((light,r,cut(m,r)));active=np.maximum(active,m)
  self.masks['lights']=active;self.all_glass=all_glass;facades=np.zeros((self.h,self.w),bool)
  for a,b,z,d in c['facade_regions']:facades[b:d,a:z]=True
  self.window_frame_guard=facades&(active==0);self.mullion_guard=stiles>0
  assert not np.any(active[self.mullion_guard]),'Glazing touches a fixed mullion'
  self.steady_glass=np.maximum.reduce([m for p,m in self.panes if p['group'] is None])>0
 def make_steam(self):
  c=self.config['steam_occluders'];cup=self.poly([c['cup_front']])>0;tanks=self.poly(c['tank_shells'])>0
  self.cup_guard=cup;self.tank_guard=tanks;self.steam=[]
  for sc in self.config['steam']:
   occluder=cup if sc['kind']=='coffee' else tanks|self.pipeline
   plume=Steam(sc,occluder);full=np.zeros((self.h,self.w),np.float32);a,b,z,d=plume.r;full[b:d,a:z]=plume.mask
   self.masks[sc['name']]=full;self.steam.append(plume)
   assert not np.any(full[occluder]),'Vapor overlaps its solid occluder'
 def make_pipeline(self):
  c=self.config['pipeline_lights'];self.pipe_roi=tuple(c['roi']);a,b,z,d=self.pipe_roi;y,x=np.mgrid[b:d,a:z].astype(np.float32);route=np.float32(c['route']);self.pipe_markers=[]
  route_y=np.interp(x,route[:,0],route[:,1]).astype(np.float32);depth=np.clip((x-route[0,0])/(route[-1,0]-route[0,0]),0,1)
  metal=smoothstep((1.8+depth*2.5-abs(y-route_y))/.55).astype(np.float32)
  # The route stops at the real plant inlet near x1390; it does not continue
  # onto the right cliff. Light and tiny housing remain on the pipe face.
  photo=cut(self.base,self.pipe_roi).astype(np.float32);material=np.float32((photo[:,:,2]-photo[:,:,0]>-4)&(photo.mean(2)<218));metal*=material
  arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(route,axis=0),axis=1))];self.pipe_total=float(arc[-1])
  full=np.zeros((self.h,self.w),np.float32);combined=np.zeros_like(x);housing=np.zeros_like(x)
  for mx in c['marker_x']:
   my=float(np.interp(mx,route[:,0],route[:,1]));q=float(np.interp(mx,route[:,0],arc)/arc[-1]);scale=.75+.40*q
   sx,sy=c['core_sigma'];hx,hy=c['halo_sigma']
   core=np.exp(-.5*(((x-mx)/(sx*scale))**2+((y-my)/(sy*scale))**2))*metal
   halo=np.exp(-.5*(((x-mx)/(hx*scale))**2+((y-my)/(hy*scale))**2))*metal
   fixture=np.exp(-.5*(((x-mx)/(1.45*sx*scale))**4+((y-my)/(.9*scale))**4))*metal
   for m in [core,halo,fixture]:m[m<.004]=0
   combined=np.maximum(combined,np.maximum(core,halo));housing=np.maximum(housing,fixture);self.pipe_markers.append((q,core,halo))
  self.pipe_housing=housing;allowed=np.maximum(combined,housing);full[b:d,a:z]=allowed;self.masks['pipeline_lights']=full;self.pipe_allowed=full>0
 def pipeline_frame(self,f,t):
  c=self.config['pipeline_lights'];a,b,z,d=self.pipe_roi;patch=f[b:d,a:z];patch*=1-self.pipe_housing[...,None]*c['fixture_darkening']
  for q,core,halo in self.pipe_markers:
   pulse=0
   for ph in c['phases']:
    age=(t/c['period']+ph)%1;fade=float(smoothstep(age/.085)*smoothstep((1-age)/.085));pulse=max(pulse,float(np.exp(-((q-age)/c['pulse_width'])**4))*fade)
   gain=c['floor']+(1-c['floor'])*pulse;alpha=core*gain
   patch=patch*(1-alpha[...,None])+np.float32(c['color'])*alpha[...,None]
   patch+=halo[...,None]*gain*.10*np.float32(c['halo_color'])
  f[b:d,a:z]=patch
 def frame(self,t,only=None):
  t=float(t)%20;enabled=set(self.masks) if only is None else set(self.groups.get(only,[only]))
  f=super().frame(t,only).astype(np.float32)
  for plume in self.steam:
   if plume.c['name'] not in enabled:continue
   a,b,z,d=plume.r;alpha=plume.density(t);f[b:d,a:z]=f[b:d,a:z]*(1-alpha[...,None])+np.float32(plume.c['color'])*alpha[...,None]
  if 'pipeline_lights' in enabled:self.pipeline_frame(f,t)
  assert np.isfinite(f).all();f=np.uint8(np.rint(np.clip(f,0,255)))
  mask=self.active if only is None else self.group_masks[only] if only in self.group_masks else self.layer_masks[only]
  assert np.array_equal(f[~mask],self.base[~mask]),'Protected source pixels changed'
  assert np.array_equal(f[self.window_frame_guard],self.base[self.window_frame_guard]),'Window frame/stone/steady pane changed'
  assert np.array_equal(f[self.mullion_guard],self.base[self.mullion_guard]),'Fixed mullion changed'
  guard=(self.pipeline|self.tank_guard|self.cup_guard)&~self.pipe_allowed
  assert np.array_equal(f[guard],self.base[guard]),'Protected pipe/support/tank/cup body changed'
  return f
 def fingerprint(self):
  paths=['scene-plan-v3.json','render_deepwell_v3.py','review_tools.py','v2-snapshot-manifest.json']
  paths+=[str(p.relative_to(H)).replace('\\','/') for p in sorted(S.rglob('*')) if p.is_file()]
  return {'files':{n:digest(H/n) for n in paths},'masks_float32_sha256':{k:hashlib.sha256(v.tobytes()).hexdigest() for k,v in self.masks.items()},'runtime':{'python':sys.version,'numpy':np.__version__,'opencv':cv2.__version__,'platform':platform.platform(),'ffmpeg':subprocess.check_output(['ffmpeg','-version'],text=True).splitlines()[0]}}

def sample_review(s):
 (H/'masks').mkdir(exist_ok=True)
 for name,m in s.masks.items():Image.fromarray(np.uint8(np.rint(np.clip(m,0,1)*255))).save(H/'masks'/f'{name}.png')
 overlay=s.base.astype(np.float32)
 colors={'lights':[240,70,40],'coffee_steam':[110,220,255],'tank_steam_near':[70,220,255],'tank_steam_middle':[70,220,255],'tank_steam_far':[70,220,255],'pipeline_lights':[50,245,160]}
 for name,color in colors.items():
  m=s.masks[name][...,None]*.48;overlay=overlay*(1-m)+np.float32(color)*m
 Image.fromarray(np.uint8(overlay)).save(H/'changed-mask-review.png')
 for t in [0,2,4,6,8,12,16,19+29/30]:Image.fromarray(s.frame(t)).save(H/f'sample-{t:.3f}s.png')
 # A deliberately all-dim diagnostic exposes incomplete pane masks immediately.
 dark=s.base.astype(np.float32).copy()
 for light,r,m in s.windows:
  a,b,z,d=r;dark[b:d,a:z]*=1-m[...,None]*(1-light['floor'])
 dark=np.uint8(np.rint(np.clip(dark,0,255)));Image.fromarray(dark).save(H/'window-all-dim-diagnostic.png')
 core_checks=[]
 for x,y in s.config['window_panes']['bright_core_controls']:
  coverage=float(s.masks['lights'][y,x]);ratio=float(dark[y,x].mean()/s.base[y,x].mean())
  assert coverage>.72 and ratio<.72,('Incomplete bright-core mask',x,y,coverage,ratio)
  core_checks.append({'xy':[x,y],'mask_coverage':coverage,'all_dim_to_source_luminance_ratio':ratio})
 a,b,z,d=(1437,163,1672,250);original=Image.fromarray(s.base).crop((a,b,z,d));dim=Image.fromarray(dark).crop((a,b,z,d));mask=Image.fromarray(np.uint8(overlay)).crop((a,b,z,d));out=Image.new('RGB',(1410,3*522))
 for i,im in enumerate([original,mask,dim]):out.paste(im.resize((1410,522),resample=Image.Resampling.NEAREST),(0,i*522))
 out.save(H/'window-source-mask-dim-comparison.png')
 checks={}
 for name in ['lights','coffee_steam','tank_steam_near','tank_steam_middle','tank_steam_far','pipeline_lights']:
  m=s.layer_masks[name];first=s.frame(0,name);assert np.array_equal(first,s.frame(20,name))
  seam=float(np.abs(s.frame(-1/30,name)[m].astype(float)-first[m]).mean());steps=[]
  for t in [0,.033333,.3,1,3,7,12,16,19.5]:steps.append(float(np.abs(s.frame(t+1/30,name)[m].astype(float)-s.frame(t,name)[m]).mean()))
  assert seam<=max(steps)*1.15+.02,(name,seam,steps)
  movement=[float(np.abs(s.frame(t+1,name)[m].astype(float)-s.frame(t,name)[m]).mean()) for t in [0,4,8,12,16]]
  checks[name]={'endpoint_exact':True,'seam_step_mae':seam,'ordinary_sampled_max':max(steps),'one_second_motion_at_0_4_8_12_16':movement}
 save('analytic-validation.json',{'fingerprint':s.fingerprint(),'changed_layers':checks,'bright_core_controls':core_checks,'mullions_stone_steady_pane_exact':True,'steam_occluders_exact':True,'pipeline_exact_except_explicit_indicator_mask':True,'old_window_mask_pixels_outside_corrected_glass':int(np.count_nonzero((s.old_window_mask>0)&~s.layer_masks['lights'])),'panes':len(s.panes),'animated_panes':sum(p['group'] is not None for p,m in s.panes),'room_groups':len(s.windows),'user_approved':False})
 print('Pane boundaries, guards, native samples and changed-layer continuity passed',flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['samples','isolated','preview'],required=True);p.add_argument('--group',choices=['windows','coffee','tank_steam','pipeline']);a=p.parse_args();s=DeepwellV3()
 if a.stage=='samples':sample_review(s);return
 clips=[]
 if a.stage=='isolated':
  for group in ([a.group] if a.group else ['windows','coffee','tank_steam','pipeline']):
   out=H/f'deepwell-v3-{group}-isolated-8s.mp4';item=encode(s,out,8,group);item['validation'],_=decode_verify(s,out,240);clips.append(item);print(group,'isolated verified',flush=True)
 else:
  out=H/'Deepwell-v3-preview-20s.mp4';item=encode(s,out,20);item['validation'],hashes=decode_verify(s,out,600,True);clips.append(item)
  repeat=H/'Deepwell-v3-three-loops-60s.mp4';assert not repeat.exists();subprocess.run(['ffmpeg','-v','error','-n','-stream_loop','2','-i',str(out),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
  item={'path':repeat.name,'sha256':digest(repeat)};item['validation'],_=decode_verify(s,repeat,1800,True,hashes)
  def packets(path):return [v['data_hash'] for v in json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v','-show_packets','-show_data_hash','sha256','-show_entries','packet=data_hash','-of','json',str(path)],text=True))['packets']]
  assert packets(repeat)==packets(out)*3;item['three_identical_encoded_packet_sequences']=True;clips.append(item)
 save(a.stage+('-'+a.group if a.group else '')+'-validation.json',{'fingerprint':s.fingerprint(),'clips':clips,'user_approved':False,'inspection':'Source/mask/native temporal/decoded stills; continuous playback not claimed'})
 print(a.stage,'complete and verified',flush=True)
if __name__=='__main__':main()
