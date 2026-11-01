"""Deepwell: native fixed plate, source-bound water, clouds, apertures and UI.

The water/cloud methods are the frozen Floodplain/Shoreless methods. All source
coordinates and masks in this adapter belong to Deepwell. No optical-flow model,
camera movement, duplicated endpoint, full-frame fade or reversed sequence.
"""
from pathlib import Path
import sys,argparse,hashlib,json,subprocess,time,platform
sys.dont_write_bytecode=True
sys.path.insert(0,r'C:\AI\ComfyUI\venv\Lib\site-packages')
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H/'dependency-snapshot'))
import cv2,numpy as np
from PIL import Image,ImageDraw
from render_floodplain import ChannelSurface
from ambient_effects import smoothstep,event_amount
cv2.setNumThreads(4)
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_json(name,data):(H/name).write_text(json.dumps(data,indent=2)+'\n')
class Deepwell:
 def __init__(self):
  self.config=json.loads((H/'scene-plan-v1.json').read_text());c=self.config
  assert digest(H/c['source']['path'])==c['source']['sha256']
  self.base=np.array(Image.open(H/c['source']['path']).convert('RGB'));self.h,self.w=self.base.shape[:2]
  self.duration=c['duration'];self.y,self.x=np.mgrid[:self.h,:self.w].astype(np.float32)
  water=self.poly(c['water_polygons'])
  # Restrict the traced polygons to blue-grey brine. Limestone, white terrace
  # lips, islands and their pale submerged margins stay completely protected.
  rgb=self.base.astype(np.float32);brine=(rgb[:,:,2]-rgb[:,:,0]>5)&(rgb.mean(2)<204)
  distance=cv2.distanceTransform(water,cv2.DIST_L2,5)
  water*=np.uint8((distance>7)|brine)
  wm=self.feather(water,3.5)
  sc=c['sky'];sm=self.poly([sc['polygon']]);px,py,rx,ry=sc['planet_protection_ellipse']
  planet=((self.x-px)/rx)**2+((self.y-py)/ry)**2<=1
  sky_source=sm.copy();sm[planet]=0;sm=self.feather(sm,sc['feather'])
  a,b,z,d=sc['roi'];original=np.array(Image.open(H/'artwork-original-v2.png').convert('RGB'))
  clean=cv2.inpaint(original[b:d,a:z],np.uint8(sky_source[b:d,a:z]==0)*255,7,cv2.INPAINT_TELEA)
  self.clean=cv2.GaussianBlur(clean.astype(np.float32),(0,0),sc['source_clean_sigma'])
  self.cy,self.cx=np.mgrid[:d-b,:z-a].astype(np.float32);self.offset=(self.cy+b)/740+(self.cx+a)/2700+.17
  self.masks={'water':wm,'sky':sm};self.lights=[];lm=np.zeros_like(wm)
  for light in c['lights']:
   m=self.aperture([light['polygon']]);self.lights.append((light,m));lm=np.maximum(lm,m)
  self.masks['lights']=lm
  lc=c['lamp'];core=self.aperture([lc['core']]);warm=np.clip((rgb[:,:,0]-rgb[:,:,2]-10)/90,0,1)
  x,y=lc['spill_center'];rx,ry=lc['spill_radius']
  spill=np.exp(-((self.x-x)/rx)**2-((self.y-y)/ry)**2)*self.feather(self.poly([lc['wall_polygon']]),9)*warm*.48
  self.masks['lamp']=np.maximum(core,spill).astype(np.float32);self.masks['lamp'][self.masks['lamp']<.002]=0
  ui=c['screen'];self.masks['screen']=self.aperture([ui['quad']]);self.ui_roi=(263,350,333,413)
  a,b,z,d=self.ui_roi;iw,ih=ui['size'];quad=np.float32(ui['quad']);rect=np.float32([[0,0],[iw-1,0],[iw-1,ih-1],[0,ih-1]])
  self.ui_tex=cv2.warpPerspective(self.base,cv2.getPerspectiveTransform(quad,rect),(iw,ih))
  self.ui_back=cv2.getPerspectiveTransform(rect,quad-np.float32([a,b]));self.ui_mask=self.masks['screen'][b:d,a:z]
  self.ui_original=cv2.warpPerspective(self.ui_tex,self.ui_back,(z-a,d-b)).astype(np.float32)
  self.layer_masks={k:v>0 for k,v in self.masks.items()};self.active=np.logical_or.reduce(list(self.layer_masks.values()))
  wc=c['water'];a,b,z,d=wc['roi'];self.water=ChannelSurface(self.base[b:d,a:z],wm[b:d,a:z],wc,(a,b))
  self.protected_planet=planet
 def poly(self,polygons):
  m=np.zeros((self.h,self.w),np.uint8)
  for p in polygons:cv2.fillPoly(m,[np.asarray(p,np.int32)],1)
  return m
 def feather(self,m,n):return smoothstep(cv2.distanceTransform(m,cv2.DIST_L2,5)/n).astype(np.float32)
 def aperture(self,polys):
  m=np.zeros((self.h,self.w),np.float32)
  for p in polys:
   p=np.float32(p);a,b=np.maximum(np.floor(p.min(0)).astype(int)-2,0);z,d=np.minimum(np.ceil(p.max(0)).astype(int)+3,[self.w,self.h])
   hi=np.zeros(((d-b)*4,(z-a)*4),np.uint8);cv2.fillPoly(hi,[np.rint((p-[a,b])*4).astype(np.int32)],255)
   lo=cv2.resize(cv2.GaussianBlur(hi.astype(np.float32)/255,(0,0),.8),(z-a,d-b),interpolation=cv2.INTER_AREA);lo[lo<.01]=0;m[b:d,a:z]=np.maximum(m[b:d,a:z],lo)
  return m
 def screen(self,f,t):
  a,b,z,d=self.ui_roi;tex=self.ui_tex.astype(np.float32).copy();phase=2*np.pi*t/self.duration
  # Existing gauge receives a bounded pressure marker; the rest of the screen
  # keeps its existing panel structure. The log shifts within its own panel.
  angle=np.pi*(.70+.13*np.sin(phase)+.05*np.sin(3*phase+1))
  uy,ux=np.mgrid[:96,:96].astype(np.float32);dx=20*np.cos(angle);dy=-20*np.sin(angle)
  along=np.clip(((ux-31)*dx+(uy-42)*dy)/400,0,1)
  needle=np.exp(-((ux-31-along*dx)**2+(uy-42-along*dy)**2)/.65)
  marker=np.exp(-((ux-31-dx)**2+(uy-42-dy)**2)/2)
  tex+=needle[...,None]*np.float32([30,65,74])+marker[...,None]*np.float32([26,51,56])
  log=self.ui_tex[20:57,66:91];yy,xx=np.mgrid[:37,:25].astype(np.float32)
  moving=cv2.remap(log,xx,(yy+t/20*37).astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_WRAP)
  tex[20:57,66:91]=tex[20:57,66:91]*.40+moving*.60
  for row in range(3):
   level=.5+.22*np.sin((row+1)*phase+row)
   coverage=np.clip(28*level-np.arange(28),0,1)
   tex[72+row*4:74+row*4,9:37]+=coverage[None,:,None]*np.float32([18,36,40])
  projected=cv2.warpPerspective(tex,self.ui_back,(z-a,d-b));f[b:d,a:z]+=(projected-self.ui_original)*self.ui_mask[...,None]
 def frame(self,t,only=None):
  t=float(t)%self.duration;f=self.base.astype(np.float32)
  if only in (None,'water'):
   a,b,z,d=self.config['water']['roi'];f[b:d,a:z]=self.water.frame(t)
  if only in (None,'sky'):
   c=self.config['sky'];a,b,z,d=c['roi'];moving=np.zeros_like(self.clean)
   # Complementary local age windows renew only at zero contribution. Features
   # travel right continuously; there is no whole-sky crossfade or reversal.
   for phase in (0,.5):
    age=(t/self.duration+self.offset+phase)%1;weight=np.sin(np.pi*age)**2
    mx=self.cx-c['speed']*self.duration*(age-.5)
    transported=cv2.remap(self.clean,mx.astype(np.float32),self.cy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
    moving+=transported*weight[...,None]
   f[b:d,a:z]+=(moving-self.clean)*self.masks['sky'][b:d,a:z,None]*c['gain']
  if only in (None,'lights'):
   for c,m in self.lights:f*=1-m[...,None]*event_amount(t,self.duration,c['start'],c['hold'],c['transition'])*(1-c['floor'])
  if only in (None,'lamp'):
   amount=max(event_amount(t,self.duration,e['start'],e['hold'],e['transition'])*e['depth'] for e in self.config['lamp']['events'])
   f*=1-self.masks['lamp'][...,None]*amount
  if only in (None,'screen'):self.screen(f,t)
  assert np.isfinite(f).all();f=np.uint8(np.rint(np.clip(f,0,255)))
  mask=self.active if only is None else self.layer_masks[only]
  assert np.array_equal(f[~mask],self.base[~mask]),'Protected geometry changed'
  assert np.array_equal(f[self.protected_planet],self.base[self.protected_planet]),'Planet moved'
  return f
 def fingerprint(self):
  paths=['scene-plan-v1.json','render_deepwell.py','artwork-planet-v1.png','artwork-original-v2.png']
  paths+=['dependency-snapshot/'+x for x in ['ambient_effects.py','water_surface.py','render_floodplain.py']]
  return {'files':{p:digest(H/p) for p in paths},'masks_float32_sha256':{k:hashlib.sha256(v.tobytes()).hexdigest() for k,v in self.masks.items()},'runtime':{'python':sys.version,'numpy':np.__version__,'opencv':cv2.__version__,'platform':platform.platform(),'ffmpeg':subprocess.check_output(['ffmpeg','-version'],text=True).splitlines()[0]}}

def encode(s,out,seconds,only=None):
 assert not out.exists(),f'Preserve existing {out}'
 vf='scale=1280:720:flags=lanczos:in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p'
 command=['ffmpeg','-v','error','-n','-f','rawvideo','-pix_fmt','rgb24','-s','1672x941','-r','30','-i','pipe:0','-an','-vf',vf,'-c:v','libx264','-preset','veryfast','-qp','0','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-movflags','+faststart',str(out)]
 p=subprocess.Popen(command,stdin=subprocess.PIPE);started=time.time();count=round(seconds*30)
 try:
  for i in range(count):
   p.stdin.write(s.frame(i/30,only).tobytes())
   if i%120==0:print(out.name,i,'/',count,round(time.time()-started,1),'s',flush=True)
 finally:p.stdin.close()
 assert p.wait()==0
 return {'path':out.name,'sha256':digest(out),'seconds':seconds,'frames':count,'layer':only or 'combined','command':command}

def samples(s):
 (H/'masks').mkdir(exist_ok=True);overlay=s.base.astype(np.float32)
 for name,m in s.masks.items():Image.fromarray(np.uint8(np.rint(m*255))).save(H/'masks'/f'{name}.png')
 for name,color in [('water',[25,160,255]),('sky',[40,230,100]),('lights',[255,30,30]),('lamp',[255,200,0]),('screen',[220,50,255])]:
  alpha=s.masks[name][...,None]*.52;overlay=overlay*(1-alpha)+np.float32(color)*alpha
 Image.fromarray(np.uint8(overlay)).save(H/'mask-review.png')
 times=[0,4,8,12,16,19+29/30]
 for t in times:Image.fromarray(s.frame(t)).save(H/f'sample-{t:.3f}s.png')
 result={}
 for name,m in s.layer_masks.items():
  assert np.array_equal(s.frame(0,name),s.frame(20,name))
  pairs=[]
  for t in [-1/30,0,.0333333,.3,1,3,7,12,16,19.5]:
   pairs.append(float(np.abs(s.frame(t+1/30,name)[m].astype(float)-s.frame(t,name)[m]).mean()))
  assert pairs[0]<=max(pairs[1:])*1.15+.02,(name,pairs)
  spans=[]
  for t in [0,4,8,12,16]:spans.append(float(np.abs(s.frame(t+1,name)[m].astype(float)-s.frame(t,name)[m]).mean()))
  result[name]={'endpoint_exact':True,'seam_step_mae':pairs[0],'ordinary_sampled_max':max(pairs[1:]),'one_second_motion_at_0_4_8_12_16':spans,'protected_pixels_exact':True}
 write_json('analytic-validation.json',{'fingerprint':s.fingerprint(),'layers':result,'planet_static_exact':True,'outside_active_masks_exact':True,'water_loop_frequency_deviation_percent':{'mean':float(np.mean(np.abs(s.water.speed_deviations))*100),'max':float(np.max(np.abs(s.water.speed_deviations))*100)},'artistic_approval':False})
 print('Masks, native samples, analytic continuity and protection passed',flush=True)

def decode_verify(s,path,expected,loop=False,reference_hashes=None):
 # FFmpeg explicit BT.709 conversion: OpenCV's implicit colour conversion is
 # intentionally not used to judge source colour or decode the delivered clip.
 p=subprocess.Popen(['ffmpeg','-v','error','-i',str(path),'-map','0:v:0','-vf','scale=in_color_matrix=bt709:out_range=pc,format=rgb24','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE)
 size=1280*720*3;hashes=[];first=prev=None;i=0
 masks={k:cv2.resize(v.astype(np.uint8),(1280,720),interpolation=cv2.INTER_NEAREST)>0 for k,v in {**s.layer_masks,'combined':s.active}.items()}
 positions={k:np.flatnonzero(m) for k,m in masks.items()};steps={k:[] for k in masks};first_parts={};prev_parts={}
 while True:
  raw=p.stdout.read(size)
  if not raw:break
  assert len(raw)==size
  hashes.append(hashlib.sha256(raw).hexdigest());f=np.frombuffer(raw,np.uint8).reshape(720,1280,3)
  if i in [0,120,240,360,480,599] and expected==600:Image.fromarray(f).save(H/f'decoded-{i:04d}.png')
  flat=f.reshape(-1,3).astype(np.int16)
  for name,idx in positions.items():
   current=flat[idx]
   if i==0:first_parts[name]=current.copy()
   else:steps[name].append(float(np.abs(current-prev_parts[name]).mean()))
   prev_parts[name]=current
  i+=1
 assert p.wait()==0 and i==expected,(i,expected)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_frames','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,color_space,color_transfer,color_primaries:frame=best_effort_timestamp_time','-of','json',str(path)],text=True))
 stamps=np.array([float(f['best_effort_timestamp_time']) for f in probe['frames']]);assert len(stamps)==expected and np.max(np.abs(stamps-np.arange(expected)/30))<.00001
 streams=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(path)],text=True))['streams'];assert len(streams)==1 and streams[0]['codec_type']=='video'
 checks={}
 if loop:
  assert hashes[0]!=hashes[-1]
  for name in positions:
   seam=float(np.abs(prev_parts[name]-first_parts[name]).mean());v=steps[name]
   near=max(v[:15]+v[-15:]);ordinary=max(v)
   assert seam<=ordinary*1.15+.02,(name,seam,ordinary)
   assert seam<=near*1.3+.03,(name,'quiet neighbour',seam,near)
   checks[name]={'seam_mae':seam,'ordinary_max_mae':ordinary,'quiet_neighbour_max_mae':near,'pass':True}
 if reference_hashes is not None:assert hashes==reference_hashes*3,'Repeated decoded pictures differ'
 return {'decoded_frames':i,'all_frames_decode':True,'timestamps_sequential':True,'silent':True,'bt709':probe['streams'][0],'seam_checks':checks,'three_exact_decoded_repeats':reference_hashes is not None},hashes

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['samples','isolated','preview'],required=True);a=p.parse_args();s=Deepwell()
 if a.stage=='samples':samples(s);return
 clips=[]
 if a.stage=='isolated':
  for layer in s.config['isolated_layers']:
   out=H/f'deepwell-{layer}-isolated-8s.mp4';item=encode(s,out,8,layer);item['validation'],_=decode_verify(s,out,240);clips.append(item)
   print(layer,'isolated verified',flush=True)
 else:
  out=H/'Deepwell-v1-preview-20s.mp4';item=encode(s,out,20);item['validation'],hashes=decode_verify(s,out,600,True);clips.append(item)
  repeat=H/'Deepwell-v1-three-loops-60s.mp4';assert not repeat.exists()
  subprocess.run(['ffmpeg','-v','error','-n','-stream_loop','2','-i',str(out),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
  item={'path':repeat.name,'sha256':digest(repeat)};item['validation'],_=decode_verify(s,repeat,1800,True,hashes);clips.append(item)
  # Verify encoded packet payloads as well as every decoded RGB picture.
  def packets(p):return [x['data_hash'] for x in json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v','-show_packets','-show_data_hash','sha256','-show_entries','packet=data_hash','-of','json',str(p)],text=True))['packets']]
  assert packets(repeat)==packets(out)*3;item['three_identical_encoded_packet_sequences']=True
 write_json(a.stage+'-validation.json',{'fingerprint':s.fingerprint(),'clips':clips,'user_approved':False,'inspection':'Assistant inspects source, masks and temporal/decoded stills; no continuous playback claim'})
 print(a.stage,'complete and verified',flush=True)
if __name__=='__main__':main()
