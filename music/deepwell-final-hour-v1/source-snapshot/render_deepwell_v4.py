"""Readable rolling steam and a purple pipe-face light pulse with a smooth return."""
from pathlib import Path
import sys,json,hashlib,argparse,subprocess,time,platform
sys.dont_write_bytecode=True
sys.path.insert(0,r'C:\AI\ComfyUI\venv\Lib\site-packages')
H=Path(__file__).resolve().parent;S=H/'v3-snapshot'
from review_tools import encode,decode_verify
sys.path.insert(0,str(S))
import render_deepwell_v3 as previous
import cv2,numpy as np
from PIL import Image,ImageDraw
from ambient_effects import smoothstep,event_amount
cv2.setNumThreads(4)
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,value):(H/name).write_text(json.dumps(value,indent=2)+'\n')
def cut(a,r):x0,y0,x1,y1=r;return a[y0:y1,x0:x1]

class RollingSteam:
 def __init__(self,c,occlusion):
  self.c=c;self.r=tuple(c['roi']);a,b,z,d=self.r;self.y,self.x=np.mgrid[b:d,a:z].astype(np.float32)
  sx,sy=c['anchor'];raw=(sy-self.y)/c['height'];self.u=np.clip(raw,0,1).astype(np.float32)
  rng=np.random.default_rng(c['seed']);self.phase=rng.uniform(0,2*np.pi,4).astype(np.float32)
  center=sx+c['drift']*self.u
  radius=3*(1.5+c['width']*self.u**.65*.9)+c['curl']*self.u**.7+6
  self.mask=smoothstep((radius-abs(self.x-center))/5)*np.float32((raw>0)&(raw<1))
  self.mask*=1-cut(occlusion,self.r).astype(np.float32)
  self.mask*=smoothstep((self.x-a)/4)*smoothstep((z-1-self.x)/4)*smoothstep((self.y-b)/3)*smoothstep((d-1-self.y)/2)
  self.mask[self.mask<.001]=0
 def density(self,t):
  c=self.c;u=self.u;sx,sy=c['anchor'];flow=np.float32(2*np.pi)*(u-np.float32(t/c['lifetime']));p=self.phase
  # Wider moving material and lateral curl replace the nearly stationary-looking
  # thin v3 strands. Every temporal harmonic is integral, so life divides 20s.
  curl=c['curl']*u**.7*(.66*np.sin(flow+p[0])+.34*np.sin(3*flow+p[1]))
  center=sx+c['drift']*u+curl
  width=1.5+c['width']*u**.65*(.66+.18*np.sin(2*flow+p[2]))
  cross=(self.x-center)/np.maximum(width,1)
  body=np.exp(-.5*cross*cross)
  material=.46+.22*np.sin(2*flow+cross*1.30+p[1])+.18*np.sin(5*flow-cross*1.8+p[2])+.10*np.sin(9*flow+cross*2.2+p[3])
  material=smoothstep((material-.10)/.82)
  tau=body*material*.82
  for sign,ph in [(-1,p[2]),(1,p[3])]:
   thread_center=center+sign*width*.48+u*np.sin(3*flow+ph)*1.2
   filament=np.exp(-.5*((self.x-thread_center)/(width*.29+.65))**2)
   broken=np.clip(.42+.38*np.sin(3*flow+ph)+.20*np.sin(7*flow-ph*.7),0,1)
   tau+=filament*broken*.25
  birth=t-u*c['lifetime']
  if c['kind']=='coffee':emission=c['baseline']+(1-c['baseline'])*(.5+.5*np.sin(2*np.pi*birth/20+.6))
  else:
   emission=np.zeros_like(u)+c['baseline']
   for e in c['events']:emission=np.maximum(emission,c['baseline']+(1-c['baseline'])*event_amount(birth,20,e['start'],e['hold'],e['transition']))
  height=smoothstep(u/.035)*smoothstep((1-u)/.32)*np.maximum(1-.40*u,0)
  alpha=(1-np.exp(-tau*height*emission*c['opacity']))*self.mask
  return np.clip(alpha,0,c['alpha_cap']).astype(np.float32)

class DeepwellV4(previous.DeepwellV3):
 def __init__(self):
  self.v4_config=json.loads((H/'scene-plan-v4.json').read_text());super().__init__();self.v3_config=self.config;self.config=self.v4_config
  assert digest(H/self.config['source']['path'])==self.config['source']['sha256']
  self.groups=self.config['isolated_groups'];self.group_masks={k:np.logical_or.reduce([self.layer_masks[n] for n in names]) for k,names in self.groups.items()}
  print('Deepwell v4 ready:',len(self.pipe_markers),'purple segments; rolling steam at',len(self.steam),'sources',flush=True)
 def make_steam(self):
  c=self.v4_config['steam_occluders'];cup=self.poly([c['cup_front']])>0;tanks=self.poly(c['tank_shells'])>0
  self.cup_guard=cup;self.tank_guard=tanks;self.steam=[]
  for sc in self.v4_config['steam']:
   occluder=cup if sc['kind']=='coffee' else tanks|self.pipeline;plume=RollingSteam(sc,occluder);a,b,z,d=plume.r
   full=np.zeros((self.h,self.w),np.float32);full[b:d,a:z]=plume.mask;self.masks[sc['name']]=full;self.steam.append(plume)
   assert not np.any(full[occluder]),'Vapor intersects its solid source/body'
 def make_pipeline(self):
  c=self.v4_config['pipeline_lights'];self.pipe_roi=tuple(c['roi']);a,b,z,d=self.pipe_roi;y,x=np.mgrid[b:d,a:z].astype(np.float32);route=np.float32(c['route'])
  # Geometric pipe-face coverage retains bright metal highlights. A luminance
  # gate must not erase a lamp core simply because its source texel is bright.
  metal=cut(self.glazing(c['tube_outline']),self.pipe_roi)
  arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(route,axis=0),axis=1))];self.pipe_total=float(arc[-1]);self.pipe_markers=[]
  combined=np.zeros_like(x);housing=np.zeros_like(x);slopes=np.gradient(route[:,1],route[:,0])
  for mx in c['marker_x']:
   my=float(np.interp(mx,route[:,0],route[:,1]));q=float(np.interp(mx,route[:,0],arc)/arc[-1]);scale=.75+.40*q
   slope=float(np.interp(mx,route[:,0],slopes));tx=1/np.sqrt(1+slope*slope);ty=slope*tx
   along=(x-mx)*tx+(y-my)*ty;cross=-(x-mx)*ty+(y-my)*tx;sx,sy=c['core_sigma'];hx,hy=c['halo_sigma']
   core=np.exp(-.5*((along/(sx*scale))**4+(cross/(sy*scale))**4))*metal
   halo=np.exp(-.5*((along/(hx*scale))**2+(cross/(hy*scale))**2))*metal
   fixture=np.exp(-.5*((along/(sx*scale*1.42))**4+(cross/(sy*scale*1.20))**4))*metal
   for m in [core,halo,fixture]:m[m<.004]=0
   combined=np.maximum(combined,np.maximum(core,halo));housing=np.maximum(housing,fixture);self.pipe_markers.append((q,core,halo))
  self.pipe_housing=housing;self.pipe_qmin=min(q for q,_,_ in self.pipe_markers);self.pipe_qmax=max(q for q,_,_ in self.pipe_markers)
  full=np.zeros((self.h,self.w),np.float32);full[b:d,a:z]=np.maximum(combined,housing);self.masks['pipeline_lights']=full;self.pipe_allowed=full>0
 def pipeline_head(self,t):
  p=2*np.pi*(t%20)/20;head=self.pipe_qmin+(self.pipe_qmax-self.pipe_qmin)*(.5-.5*np.cos(p))
  return float(head),float(np.sin(p))
 def pipeline_frame(self,f,t):
  c=self.config['pipeline_lights'];a,b,z,d=self.pipe_roi;patch=f[b:d,a:z];patch*=1-self.pipe_housing[...,None]*c['fixture_darkening']
  head,direction=self.pipeline_head(t);tail_center=head-c['tail_length']*direction
  for q,core,halo in self.pipe_markers:
   leading=float(np.exp(-((q-head)/c['pulse_width'])**4));tail=c['tail_strength']*float(np.exp(-.5*((q-tail_center)/c['tail_width'])**2))
   pulse=min(1,leading+tail);gain=c['floor']+(1-c['floor'])*pulse
   colour=np.float32(c['color'])+pulse*(np.float32(c['peak_color'])-np.float32(c['color']))
   alpha=core*gain;patch=patch*(1-alpha[...,None])+colour*alpha[...,None]
   patch+=halo[...,None]*gain*c['halo_gain']*np.float32(c['halo_color'])
  f[b:d,a:z]=patch
 def fingerprint(self):
  names=['scene-plan-v4.json','render_deepwell_v4.py','review_tools.py','v3-snapshot-manifest.json']
  names+=[q.relative_to(H).as_posix() for q in sorted(S.rglob('*')) if q.is_file()]
  return {'files':{n:digest(H/n) for n in names},'masks_float32_sha256':{k:hashlib.sha256(v.tobytes()).hexdigest() for k,v in self.masks.items()},'runtime':{'python':sys.version,'numpy':np.__version__,'opencv':cv2.__version__,'platform':platform.platform(),'ffmpeg':subprocess.check_output(['ffmpeg','-version'],text=True).splitlines()[0]}}

def samples(s):
 (H/'masks').mkdir(exist_ok=True);images=[];times=[0,2,4,6,8,10,12,15,16,19+29/30]
 for name,m in s.masks.items():Image.fromarray(np.uint8(np.rint(np.clip(m,0,1)*255))).save(H/'masks'/f'{name}.png')
 overlay=s.base.astype(np.float32)
 for name,colour in [('coffee_steam',[60,190,255]),('tank_steam_near',[60,190,255]),('tank_steam_middle',[60,190,255]),('tank_steam_far',[60,190,255]),('pipeline_lights',[210,60,255])]:
  m=s.masks[name][...,None]*.42;overlay=overlay*(1-m)+np.float32(colour)*m
 Image.fromarray(np.uint8(overlay)).save(H/'changed-mask-review.png')
 for t in times:
  frame=s.frame(t);Image.fromarray(frame).save(H/f'sample-{t:.3f}s.png');images.append(frame)
 # Full-composition preview-size samples use the actual delivery conversion,
 # including 4:2:0 chroma, rather than a brighter RGB-only resized approximation.
 vf='scale=1280:720:flags=lanczos:in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p,scale=in_color_matrix=bt709:in_range=tv:out_range=pc,format=rgb24'
 raw=subprocess.run(['ffmpeg','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1672x941','-r','30','-i','pipe:0','-vf',vf,'-f','rawvideo','-pix_fmt','rgb24','pipe:1'],input=b''.join(f.tobytes() for f in images),stdout=subprocess.PIPE,check=True).stdout
 size=1280*720*3;assert len(raw)==len(times)*size
 for i,t in enumerate(times):Image.fromarray(np.frombuffer(raw[i*size:(i+1)*size],np.uint8).reshape(720,1280,3)).save(H/f'preview-size-{t:.3f}s.png')
 checks={}
 for name in ['coffee_steam','tank_steam_near','tank_steam_middle','tank_steam_far','pipeline_lights']:
  m=s.layer_masks[name];first=s.frame(0,name);assert np.array_equal(first,s.frame(20,name))
  seam=float(np.abs(s.frame(-1/30,name)[m].astype(float)-first[m]).mean());steps=[]
  for t in [0,.033333,.3,1,3,7,12,16,19.5]:steps.append(float(np.abs(s.frame(t+1/30,name)[m].astype(float)-s.frame(t,name)[m]).mean()))
  assert seam<=max(steps)*1.15+.02,(name,seam,steps)
  movement=[float(np.abs(s.frame(t+1,name)[m].astype(float)-s.frame(t,name)[m]).mean()) for t in [0,4,8,12,16]]
  checks[name]={'endpoint_exact':True,'seam_step_mae':seam,'ordinary_sampled_max':max(steps),'one_second_motion_at_0_4_8_12_16':movement}
 path={str(t):s.pipeline_head(t)[0] for t in [0,2,5,8,10,12,15,18,20]}
 assert path['0']<path['5']<path['10'] and path['10']>path['15']>path['20'] and path['0']==path['20']
 core_checks=[]
 for x,y in s.config['window_panes']['bright_core_controls']:
  coverage=float(s.masks['lights'][y,x]);assert coverage>.72;core_checks.append({'xy':[x,y],'mask_coverage':coverage})
 save('analytic-validation.json',{'fingerprint':s.fingerprint(),'changed_layers':checks,'pipeline_head_normalized_arc':path,'head_zero_speed_at_0_10_20':'Analytic cosine derivative is zero','bright_core_controls_retained':core_checks,'source_guards':'Inherited unchanged v3 per-frame window/mullion/stone/steady glass/cup/tank/pipe checks, with explicit purple-indicator footprint','user_approved':False,'inspection':'Native and actual-conversion 720p temporal stills; continuous playback not claimed'})
 print('Native/720p samples, source guards, changed-layer seams and both pipeline directions passed',flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['samples','isolated','preview'],required=True);p.add_argument('--group',choices=['coffee','tank_steam','pipeline']);a=p.parse_args();s=DeepwellV4()
 if a.stage=='samples':samples(s);return
 clips=[]
 if a.stage=='isolated':
  for group in ([a.group] if a.group else ['coffee','tank_steam','pipeline']):
   seconds=20 if group=='pipeline' else 8;out=H/(f'deepwell-v4-{group}-roundtrip-20s.mp4' if group=='pipeline' else f'deepwell-v4-{group}-isolated-8s.mp4')
   item=encode(s,out,seconds,group);item['validation'],_=decode_verify(s,out,seconds*30,group=='pipeline');clips.append(item);print(group,'isolated verified',flush=True)
 else:
  out=H/'Deepwell-v4-preview-20s.mp4';item=encode(s,out,20);item['validation'],hashes=decode_verify(s,out,600,True);clips.append(item)
  repeat=H/'Deepwell-v4-three-loops-60s.mp4';assert not repeat.exists();subprocess.run(['ffmpeg','-v','error','-n','-stream_loop','2','-i',str(out),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
  item={'path':repeat.name,'sha256':digest(repeat)};item['validation'],_=decode_verify(s,repeat,1800,True,hashes)
  def packets(path):return [q['data_hash'] for q in json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v','-show_packets','-show_data_hash','sha256','-show_entries','packet=data_hash','-of','json',str(path)],text=True))['packets']]
  assert packets(repeat)==packets(out)*3;item['three_identical_encoded_packet_sequences']=True;clips.append(item)
 save(a.stage+('-'+a.group if a.group else '')+'-validation.json',{'fingerprint':s.fingerprint(),'clips':clips,'user_approved':False,'inspection':'Source/native/actual-720p/decoded temporal stills; no continuous playback claim'})
 print(a.stage,'complete and verified',flush=True)
if __name__=='__main__':main()
