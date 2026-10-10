"""Source-bound Spirewatch v1. Fixed city with independent local motion layers."""
from pathlib import Path
import sys,json,hashlib,subprocess,time,argparse
import cv2,numpy as np
from PIL import Image,ImageDraw
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(H/'dependencies'))
from ambient_effects import smoothstep,event_amount
from render_floodplain import ChannelSurface
cv2.setNumThreads(4)
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(n,v):(H/n).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def byte(a):return np.uint8(np.rint(np.clip(a,0,255)))
def bounds(m,pad=0):
 y,x=np.where(m>0);return max(0,int(x.min())-pad),max(0,int(y.min())-pad),min(m.shape[1],int(x.max())+1+pad),min(m.shape[0],int(y.max())+1+pad)

class Spirewatch:
 def __init__(self):
  self.path=H/'scene-plan-v2.json';self.config=json.loads(self.path.read_text());c=self.config
  src=R/c['source']['path'];assert sha(src)==c['source']['sha256']
  for n,h in c['dependencies'].items():assert sha(H/'dependencies'/n)==h
  self.base=np.array(Image.open(src).convert('RGB'));self.h,self.w=self.base.shape[:2];self.shape=(self.h,self.w);self.duration=c['duration']
  assert [self.w,self.h]==c['source']['dimensions'];self.y,self.x=np.mgrid[:self.h,:self.w].astype(np.float32)
  self.masks={};self.clouds=[];self.falls=[];self.waters=[];self.windows=[];self.walkway=[]
  self.make_atmosphere();self.make_falls();self.make_water();self.make_lights();self.make_screen()
  self.layer_masks={k:v>0 for k,v in self.masks.items()};self.active=np.logical_or.reduce(list(self.layer_masks.values()))
 def poly(self,polys,feather=0):
  m=np.zeros(self.shape,np.uint8)
  for p in polys:cv2.fillPoly(m,[np.int32(p)],1)
  return smoothstep(cv2.distanceTransform(m,cv2.DIST_L2,5)/feather).astype(np.float32) if feather else m
 def make_atmosphere(self):
  c=self.config['sky'];binary=self.poly([c['polygon']]);excluded=self.poly(c['exclusions']+[c['mountain']])
  for a,b,w in c['protected_lines']:cv2.line(excluded,tuple(a),tuple(b),1,w)
  excluded=cv2.dilate(excluded,np.ones((5,5),np.uint8))
  self.protected_silhouettes=excluded>0;binary[excluded>0]=0
  # Keep every distant roof/light out of both transport source and destination.
  boundary=np.interp(np.arange(self.w),[0,600,650,700,750,800,855,900,960,1030,1100,1150,1200,1350,1420,1500,1600,1671],[370,382,385,393,401,413,402,415,429,421,415,390,376,380,374,385,373,350])
  binary[self.y>boundary[None,:]]=0
  # The wider extraction exclusion prevents structure pixels bleeding into weather.
  invalid=cv2.dilate(np.uint8(binary==0),np.ones((19,19),np.uint8))
  a,b,z,d=260,0,self.w,480
  patch=self.base[b:d,a:z];hole=invalid[b:d,a:z]*255
  clean=cv2.inpaint(patch,hole,5,cv2.INPAINT_TELEA).astype(np.float32)
  clean=cv2.GaussianBlur(clean,(0,0),.45)
  mask=smoothstep(np.maximum(cv2.distanceTransform(binary,cv2.DIST_L2,5)-1,0)/c['feather']).astype(np.float32)
  split=smoothstep((self.y-295)/95)
  for name,m,settings in [('clouds',mask*(1-split),c),('mist',mask*split,self.config['mist'])]:
   m[m<.002]=0;self.masks[name]=m
   yy,xx=np.mgrid[b:d,a:z].astype(np.float32);xx-=a;yy-=b
   offset=(xx+a)/3100+(yy+b)/1200+.13
   self.clouds.append((name,settings,(a,b,z,d),m[b:d,a:z],clean,xx,yy,offset))
 def make_falls(self):
  mask=np.zeros(self.shape,np.float32)
  for c in self.config['falls']:
   m=self.poly([c['polygon']],2);a,b,z,d=bounds(m,3);local=m[b:d,a:z];mask=np.maximum(mask,m)
   yy,xx=np.mgrid[:d-b,:z-a].astype(np.float32);rng=np.random.default_rng(c['seed'])
   # Periodic vertical texture with elongated streaks; only the density travels.
   height=int(c['speed']*c['period']);width=z-a
   grid=rng.random((max(8,height//14),max(4,width//3)),dtype=np.float32)
   tile=cv2.resize(np.tile(grid,(3,1)),(width,height*3),interpolation=cv2.INTER_CUBIC)
   tex=tile[height:height*2];tex=(tex-tex.mean())/(tex.std()+1e-6)
   self.falls.append((c,(a,b,z,d),local,xx,yy,tex))
  self.masks['falls']=mask
 def make_water(self):
  c=self.config['water'];mask=np.zeros(self.shape,np.float32)
  for i,p in enumerate(c['polygons']):
   m=self.poly([p],5);m[m<.002]=0;mask=np.maximum(mask,m);a,b,z,d=bounds(m,5)
   settings=dict(c);settings['seed']+=i;settings['displacement_scale']*=c['far_right_multiplier'] if a>1300 else 1
   obj=ChannelSurface(self.base[b:d,a:z],m[b:d,a:z],settings,(a,b))
   self.waters.append(((a,b,z,d),obj))
  self.masks['water']=mask
 def make_lights(self):
  c=self.config['windows'];rgb=self.base.astype(np.float32);wm=np.zeros(self.shape,np.float32);choices=[]
  for ri,(a,b,z,d) in enumerate(c['facade_regions']):
   p=rgb[b:d,a:z];on=np.uint8((p.max(2)>65)&(p[:,:,0]>p[:,:,2]*1.03))
   count,lab,stats,centers=cv2.connectedComponentsWithStats(on,8)
   groups=[]
   for j in range(1,count):
    x,y,w,h,area=map(int,stats[j])
    if 2<=area<=30 and w<=9 and h<=9:groups.append((area,x+a,y+b,w,h))
   groups.sort(reverse=True)
   choices.extend(groups[:2])
  self.window_records=[]
  for i,(_,x,y,w,h) in enumerate(choices[:c['count']]):
   # Complete compact aperture with a narrowly bounded glow, not the facade bbox.
   m=self.poly([[[x,y],[x+w-1,y],[x+w-1,y+h-1],[x,y+h-1]]]).astype(np.float32)
   m=np.maximum(m,cv2.GaussianBlur(m,(0,0),1.0)*.13);m[m<.003]=0;wm=np.maximum(wm,m)
   a,b,z,d=bounds(m);self.windows.append((i,(a,b,z,d),m[b:d,a:z]))
   self.window_records.append({'index':i,'aperture':[x,y,w,h],'start':c['starts'][i],'hold':c['holds'][i]})
  self.masks['windows']=wm
  wc=self.config['walkway'];mask=np.zeros(self.shape,np.float32)
  warm=np.clip((rgb[:,:,0]-rgb[:,:,2])/45,0,1)
  for i,(x,y) in enumerate(wc['lights']):
   core=np.exp(-((self.x-x)/2.5)**4-((self.y-y)/2.0)**4)
   halo=np.exp(-((self.x-x)/8)**2-((self.y-y)/5)**2)*warm*.16
   m=np.maximum(core,halo).astype(np.float32);m[m<.004]=0;mask=np.maximum(mask,m)
   a,b,z,d=bounds(m);self.walkway.append((i,(a,b,z,d),m[b:d,a:z]))
  self.masks['walkway']=mask
  lc=self.config['lamp'];aperture=self.poly([lc['polygon']]).astype(np.float32)
  core=np.maximum(aperture,cv2.GaussianBlur(aperture,(0,0),2)*.22)
  wall=self.poly([lc['wall_polygon']],14)*np.exp(-((self.x-78)/80)**2-((self.y-570)/100)**2)*.43
  desk=self.poly([lc['desk_polygon']],12)*np.exp(-((self.x-130)/235)**2-((self.y-730)/90)**2)*.65
  cup=self.poly([lc['cup_polygon']],2)*.32
  m=np.maximum.reduce([core,wall,desk,cup]).astype(np.float32);m[m<.002]=0
  self.masks['lamp']=m;a,b,z,d=bounds(m);self.lamp=((a,b,z,d),m[b:d,a:z])
 def make_screen(self):
  c=self.config['screen'];m=self.poly([c['polygon']],1.7);self.masks['screen']=m
  a,b,z,d=bounds(m);self.screen=((a,b,z,d),m[b:d,a:z]);self.route=np.float32(c['route'])
  self.route_lengths=np.r_[0,np.cumsum(np.linalg.norm(np.diff(self.route,axis=0),axis=1))]
 def frame(self,t,only=None,force_dark=False):
  t=float(t)%self.duration;f=self.base.astype(np.float32)
  for name,c,(a,b,z,d),m,clean,x,y,offset in self.clouds:
   if only not in (None,name,'atmosphere'):continue
   moving=np.zeros_like(clean)
   for shift in (0,.5):
    age=(t/self.duration+offset+shift)%1;weight=np.sin(np.pi*age)**2
    mx=x-c['speed']*self.duration*(age-.5)
    v=cv2.remap(clean,mx.astype(np.float32),y,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
    moving+=v*weight[...,None]
   f[b:d,a:z]+=m[...,None]*c['strength']*(moving-clean)
  if only in (None,'falls'):
   for c,(a,b,z,d),m,x,y,tex in self.falls:
    sy=(y-t*c['speed'])%tex.shape[0]
    density=cv2.remap(tex,x,sy.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_WRAP)
    density=np.tanh(density*.85)*c['depth']
    f[b:d,a:z]*=1+density[...,None]*m[...,None]
  if only in (None,'water'):
   for (a,b,z,d),obj in self.waters:f[b:d,a:z]+=obj.frame(t)-self.base[b:d,a:z]
  if only in (None,'windows'):
   c=self.config['windows']
   for i,(a,b,z,d),m in self.windows:
    amount=1 if force_dark else event_amount(t,self.duration,c['starts'][i],c['holds'][i],c['transition'])
    f[b:d,a:z]*=1-m[...,None]*amount*(1-c['floor'])
  if only in (None,'walkway'):
   c=self.config['walkway']
   for i,(a,b,z,d),m in self.walkway:
    amt=event_amount(t,self.duration,c['starts'][i],c['hold'],.10)
    f[b:d,a:z]*=1-m[...,None]*amt*c['depth']
  if only in (None,'lamp'):
   c=self.config['lamp'];(a,b,z,d),m=self.lamp
   amt=event_amount(t,self.duration,c['start'],c['hold'],c['transition'])
   f[b:d,a:z]*=1-m[...,None]*amt*c['depth']
  if only in (None,'screen'):
   c=self.config['screen'];(a,b,z,d),m=self.screen;xx=self.x[b:d,a:z];yy=self.y[b:d,a:z]
   age=(t% c['period'])/c['period'];distance=age*self.route_lengths[-1]
   idx=min(np.searchsorted(self.route_lengths,distance,side='right')-1,len(self.route)-2)
   u=(distance-self.route_lengths[idx])/(self.route_lengths[idx+1]-self.route_lengths[idx]);pos=self.route[idx]*(1-u)+self.route[idx+1]*u
   envelope=float(smoothstep(age/.07)*smoothstep((1-age)/.07))
   marker=np.exp(-((xx-pos[0])**2+(yy-pos[1])**2)/3.8)*envelope
   added=marker[...,None]*np.float32([.6,.88,1])*c['marker_strength']
   for i,(px,py) in enumerate([c['route'][2],c['route'][4],c['route'][-1]]):
    amt=event_amount(t,60,9+i*17,2.4,.6)
    added+=np.exp(-((xx-px)**2+(yy-py)**2)/3.2)[...,None]*np.float32([10,21,27])*amt
   pa,pb,pz,pd=c['panel'];panel=(xx>=pa)&(xx<pz)&(yy>=pb)&(yy<pd)
   source=self.base[b:d,a:z];gate=np.float32((source[:,:,2]>source[:,:,0]*1.15)&(source[:,:,2]>30))*panel
   scan=np.exp(-((yy-(pb+(t%20)/20*(pd-pb))) / 5)**2)*float(smoothstep((t%20)/1)*smoothstep((20-t%20)/1))
   added+=scan[...,None]*gate[...,None]*np.float32([3,6,8])
   f[b:d,a:z]+=added*m[...,None]
  assert np.isfinite(f).all();out=byte(f)
  active=self.active if only is None else (self.layer_masks['clouds']|self.layer_masks['mist'] if only=='atmosphere' else self.layer_masks[only])
  assert np.array_equal(out[~active],self.base[~active]),'Protected pixels changed'
  return out
 def fingerprint(self):
  return {'source':self.config['source'],'config_sha256':sha(self.path),'renderer_sha256':sha(__file__),'dependencies':self.config['dependencies'],'masks':{k:hashlib.sha256(m.tobytes()).hexdigest() for k,m in self.masks.items()},'runtime':{'numpy':np.__version__,'opencv':cv2.__version__}}

def samples(s):
 (H/'masks').mkdir(exist_ok=True);out=s.base.astype(np.float32)
 colors=[[45,150,255],[60,230,175],[255,180,40],[20,200,220],[255,80,80],[250,60,220],[255,220,60],[90,255,80]]
 for (name,m),color in zip(s.masks.items(),colors):
  cv2.imwrite(str(H/'masks'/f'{name}.png'),byte(m*255));out=out*(1-m[...,None]*.42)+np.float32(color)*m[...,None]*.42
 Image.fromarray(byte(out)).save(H/'mask-review.png')
 for t in [0,4,8,20,32.1,40,52,59+29/30]:Image.fromarray(s.frame(t)).save(H/f'sample-{t:06.2f}s.png')
 Image.fromarray(s.frame(0,'windows',True)).save(H/'windows-forced-dim.png')
 Image.fromarray(s.frame(32.1,'lamp')).save(H/'lamp-dip.png')
 save('mapped-window-apertures.json',s.window_records)
 report={}
 for name,m in s.layer_masks.items():
  assert np.array_equal(s.frame(0,name),s.frame(60,name))
  seam=np.abs(s.frame(-1/30,name)[m].astype(float)-s.frame(0,name)[m]).mean()
  ordinary=[float(np.abs(s.frame(t+1/30,name)[m].astype(float)-s.frame(t,name)[m]).mean()) for t in [0,1,4,8,14.3,19.5,31.8,32.1,38.7,40,51.2,57,59.9]]
  assert seam<=max(ordinary)*1.1+.01,(name,seam,max(ordinary))
  report[name]={'periodic_endpoint':True,'seam_mae':float(seam),'ordinary_max_sampled':max(ordinary),'pass':True}
 assert len({hashlib.sha256(s.frame(t)).hexdigest() for t in [0,20,40]})==3
 save('analytic-validation.json',{'fingerprint':s.fingerprint(),'layers':report,'distinct_0_20_40':True,'protected_pixels':'Asserted on every source frame','inspection':'Sampled stills pending; no continuous playback claim'})
 print('Samples, masks and analytic checks ready',flush=True)

def encode(s,path,seconds,only=None):
 assert not path.exists();n=int(seconds*30);ff=s.config['ffmpeg'];w,h=s.config['preview_size']
 command=[ff,'-v','error','-n','-f','rawvideo','-pix_fmt','rgb24','-s',f'{s.w}x{s.h}','-r','30','-i','pipe:0','-vf',f'scale={w}:{h}:flags=lanczos:out_color_matrix=bt709:out_range=tv','-an','-c:v','libx264','-preset','veryfast','-qp','0','-pix_fmt','yuv420p','-bf','0','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-color_range','tv','-movflags','+faststart',str(path)]
 p=subprocess.Popen(command,stdin=subprocess.PIPE);start=time.monotonic()
 try:
  for i in range(n):
   p.stdin.write(s.frame(i/30,only).tobytes())
   if (i+1)%120==0:print(f'{path.name}: {i+1}/{n}, {time.monotonic()-start:.0f}s',flush=True)
 finally:p.stdin.close()
 assert p.wait()==0

def verify(s,path,count,seam=True,repeat=False):
 w,h=s.config['preview_size'];size=w*h*3
 cmd=[s.config['ffmpeg'],'-v','error','-i',str(path),'-map','0:v:0','-vf','scale=in_color_matrix=bt709:out_range=full','-pix_fmt','rgb24','-f','rawvideo','-']
 proc=subprocess.Popen(cmd,stdout=subprocess.PIPE)
 masks={k:cv2.resize(m.astype(np.uint8),(w,h),interpolation=cv2.INTER_NEAREST) for k,m in {**s.layer_masks,'combined':s.active}.items()}
 mx={k:0. for k in masks};hs=[];first=prev=None;near=[];region_steps={k:[] for k in masks}
 i=0
 while True:
  raw=proc.stdout.read(size)
  if not raw:break
  assert len(raw)==size
  frame=np.frombuffer(raw,np.uint8).reshape(h,w,3)
  hs.append(hashlib.sha256(raw).hexdigest())
  if first is None:first=frame.copy()
  if prev is not None and (not repeat or i<1800):
   diff=cv2.absdiff(frame,prev)
   for k,m in masks.items():
    value=sum(cv2.mean(diff,mask=m)[:3])/3;mx[k]=max(mx[k],value)
    if i<15 or 1785<=i<1800:region_steps[k].append(value)
  if i in [0,240,600,1200] and not repeat:Image.fromarray(frame).save(H/f'{path.stem}-decoded-{i:04d}.png')
  prev=frame.copy();i+=1
  if i%600==0:print(f'{path.name}: decoded {i}/{count}',flush=True)
 assert proc.wait()==0 and i==count
 # Decode timestamps independently of RGB conversion.
 cap=cv2.VideoCapture(str(path));j=0
 while True:
  ok,_=cap.read()
  if not ok:break
  assert abs(cap.get(cv2.CAP_PROP_POS_MSEC)/1000-j/30)<.0001;j+=1
 cap.release();assert j==count
 report={'frames':i,'full_decode':True,'sequential_timestamps':True,'dimensions':[w,h],'fps':30,'sha256':sha(path),'colour_aware_decode':True}
 if seam and not repeat:
  diff=cv2.absdiff(prev,first);checks={}
  for k,m in masks.items():
   value=sum(cv2.mean(diff,mask=m)[:3])/3;local=max(region_steps[k]) if region_steps[k] else mx[k]
   assert value<=mx[k]*1.1+.012,(k,value,mx[k])
   assert value<=local*1.25+.012,(k,'quiet seam',value,local)
   checks[k]={'seam_mae':value,'ordinary_max':mx[k],'neighbor_max':local,'pass':True}
  assert hs[0]!=hs[-1] and len({hs[0],hs[600],hs[1200]})==3
  report.update(encoded_seams=checks,no_duplicate_endpoint=True,distinct_0_20_40=True)
 if repeat:assert hs[:1800]==hs[1800:3600]==hs[3600:];report['three_exact_decoded_repetitions']=True
 return report

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['samples','isolated','preview','verify'],required=True);args=p.parse_args();s=Spirewatch()
 if args.stage=='samples':samples(s);return
 if args.stage=='isolated':
  records=[]
  for layer in ['atmosphere','falls','water']:
   path=H/f'{layer}-isolated-8s.mp4';encode(s,path,8,layer);records.append({'layer':layer,**verify(s,path,240,False)})
  save('isolated-validation.json',{'fingerprint':s.fingerprint(),'clips':records});return
 out=H/'spirewatch-v1-preview-60s.mp4';review=H/'spirewatch-v1-three-loops-180s.mp4'
 if args.stage=='preview':encode(s,out,60)
 report=verify(s,out,1800)
 save('preview-validation.json',{'fingerprint':s.fingerprint(),**report})
 if not review.exists():subprocess.run([s.config['ffmpeg'],'-v','error','-n','-stream_loop','2','-i',str(out),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(review)],check=True)
 repeated=verify(s,review,5400,True,True)
 save('repeat-validation.json',repeated)
 save('delivery-v1.json',{'date':'2026-10-10','status':'Technically verified draft; user motion review pending','source':s.config['source'],'fingerprint':s.fingerprint(),'preview':str(out),'preview_validation':report,'repeat':str(review),'repeat_validation':repeated,'user_motion_approved':False,'assistant_continuous_playback':False,'four_k':None,'audio':None})
 print('Minute preview and three-repeat review fully verified',flush=True)
if __name__=='__main__':main()
