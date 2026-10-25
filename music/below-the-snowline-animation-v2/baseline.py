from pathlib import Path
import sys, json, hashlib, argparse, subprocess
sys.dont_write_bytecode=True
sys.path.insert(0,r'C:/AI/ComfyUI/venv/Lib/site-packages')
import cv2, numpy as np
from PIL import Image
from review_tools import encode, decode_verify
cv2.setNumThreads(4)
H=Path(__file__).resolve().parent
def smooth(v):
 v=np.clip(v,0,1);return v*v*(3-2*v)
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,d):(H/n).write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
class Scene:
 def __init__(self):
  self.c=json.loads((H/'scene.json').read_text());c=self.c
  self.base=np.array(Image.open(H/c['source']).convert('RGB'));self.h,self.w=self.base.shape[:2]
  self.y,self.x=np.mgrid[:self.h,:self.w].astype(np.float32)
  self.glass=self.poly(c['glass'],7);self.bridge=self.poly(c['bridge_guard'],0)
  self.sky=self.poly(c['sky'],8)*(1-self.poly(c['dish_guard'],0));self.sky*=self.glass
  self.skyvalid=self.sky>.99
  self.sky_distance=cv2.distanceTransform(self.skyvalid.astype(np.uint8),cv2.DIST_L2,5)
  self.masks={'sky':self.sky}
  self.fog=[]
  for fc in c['fog']:
   mask=self.poly(fc['poly'],fc['feather'])*self.glass*(1-self.bridge)
   rng=np.random.default_rng(fc['seed']);ny,nx=np.mgrid[:256,:512].astype(np.float32);noise=np.zeros_like(nx)
   for _ in range(22):
    cx,cy=rng.uniform(0,512),rng.uniform(0,256);dx=(nx-cx+256)%512-256;dy=(ny-cy+128)%256-128
    noise+=rng.uniform(.25,.8)*np.exp(-.5*((dx/rng.uniform(24,65))**2+(dy/rng.uniform(16,42))**2))
   noise=np.clip((noise-.20)*.65,0,1)
   self.fog.append((fc,mask,noise));self.masks[fc['name']]=mask
  self.windows=[(wc,self.poly(wc['poly'],.8)) for wc in c['windows']]
  self.masks['windows']=np.maximum.reduce([m for wc,m in self.windows])
  self.radar=self.poly(c['radar'],1.5);self.readout=self.poly(c['readout'],1.2)
  self.masks['terminals']=np.maximum(self.radar,self.readout)
  sc=c['steam'];u=(sc['anchor'][1]-self.y)/sc['height'];center=sc['anchor'][0]+sc['drift']*u
  self.steam_mask=((u>0)&(u<1)&(abs(self.x-center)<24)).astype(np.float32)
  self.steam_mask*=smooth((24-abs(self.x-center))/5);self.masks['coffee_steam']=self.steam_mask
  self.flakes=[];rng=np.random.default_rng(913)
  for lc in c['snow']:
   for _ in range(lc['count']):
    self.flakes.append((rng.uniform(330,1710),rng.uniform(-80,760),rng.uniform(*lc['vx']),rng.uniform(*lc['vy']),rng.uniform(*lc['radius']),rng.uniform(*lc['opacity']),rng.uniform(0,lc['life']),lc['life'],lc['depth']))
  self.masks['snow']=self.glass
  self.layer_masks={k:v>0 for k,v in self.masks.items()};self.active=np.logical_or.reduce(list(self.layer_masks.values()))
  self.groups={'weather':['sky','far_powder','ravine_mist','ledge_spindrift','snow'],'interior':['terminals','coffee_steam'],'lighting':['windows']}
 def poly(self,points,feather):
  b=np.zeros((self.h,self.w),np.uint8);cv2.fillPoly(b,[np.array(points,np.int32)],1)
  return smooth(cv2.distanceTransform(b,cv2.DIST_L2,5)/feather).astype(np.float32) if feather else b.astype(np.float32)
 def frame(self,t,only=None):
  t=float(t)%20;enabled=set(self.masks) if only is None else set(self.groups.get(only,[only]));f=self.base.astype(np.float32)
  if 'sky' in enabled:
   # Forward source transport; both sample validity and destination silhouettes
   # exclude the antenna, cannon, mountains and window rim.
   moving=np.zeros_like(f);weights=np.zeros((self.h,self.w),np.float32)
   for shift in [0,.37,.71]:
    age=(t/20+shift)%1;weight=np.sin(np.pi*age)**4
    dx=self.c['cloud_speed']*20*(age-.5);mx=self.x-dx-getattr(self,'origin',(0,0))[0]
    local_y=self.y-getattr(self,'origin',(0,0))[1]
    valid=cv2.remap(self.skyvalid.astype(np.float32),mx,local_y,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
    valid=smooth((valid-.98)/.02)*weight
    moved=cv2.remap(self.base.astype(np.float32),mx,local_y,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
    moving+=moved*valid[...,None];weights+=valid
   mask=self.sky*smooth(self.sky_distance/18)*smooth(weights/.12)
   moving/=np.maximum(weights[...,None],.00001)
   f+=mask[...,None]*(moving-f)
  for fc,m,noise in self.fog:
   if fc['name'] not in enabled:continue
   sx,sy=fc['scale'];mx=(self.x/sx*512-t/20*512).astype(np.float32);my=(self.y/sy*256).astype(np.float32)
   density=cv2.remap(noise,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_WRAP)
   a=m*density*fc['opacity'];f=f*(1-a[...,None])+np.float32([212,226,239])*a[...,None]
  if 'windows' in enabled:
   for wc,m in self.windows:
    phase=(t-wc['phase'])%20;amount=smooth(phase/1.5)*smooth((5-phase)/1.6)
    f*=1-m[...,None]*amount*.42
  if 'terminals' in enabled:
   # Sweep on original etched radar graphics; no screen or bezel deformation.
   angle=np.arctan2((self.y-330)/.96,self.x-119)
   delta=(angle-2*np.pi*t/10)%(2*np.pi)
   trail=np.exp(-delta/.38);radius=np.sqrt((self.x-119)**2+((self.y-330)/.96)**2)
   a=self.radar*trail*smooth((64-radius)/8)*.20
   f=f*(1-a[...,None])+np.float32([100,210,242])*a[...,None]
   for bx,by,phase in [(94,304,0),(143,351,3.7),(105,363,6.4)]:
    age=(t-phase)%10;strength=float(smooth(age/.24))*np.exp(-age/1.1)*float(smooth((10-age)/.4))
    spot=np.exp(-.5*(((self.x-bx)/1.8)**2+((self.y-by)/1.5)**2))*self.radar*strength*.65
    f+=spot[...,None]*np.float32([60,145,175])
   for i,(x0,x1,y0,y1) in enumerate([(44,62,471,522),(65,82,471,520),(91,105,471,521),(44,61,528,564),(91,97,526,561),(106,122,525,558)]):
    m=self.readout*(self.x>=x0)*(self.x<x1)*(self.y>=y0)*(self.y<y1)
    gain=.52+.48*(.5+.5*np.sin(2*np.pi*t/(10 if i%2 else 20)+i*1.7))
    f*=1-m[...,None]*(1-gain)
  if 'coffee_steam' in enabled:
   sc=self.c['steam'];sx,sy=sc['anchor'];u=np.clip((sy-self.y)/sc['height'],0,1);flow=2*np.pi*(u-t/5)
   tau=np.zeros_like(u)
   for ph in [0,2.3,4.6]:
    center=sx+sc['drift']*u+u*(3*np.sin(flow+ph)+2*np.sin(2*flow+ph))
    ribbon=np.exp(-.5*((self.x-center)/(.8+sc['width']*u*.5))**2)
    detail=np.clip(.45+.35*np.sin(flow*3+ph)+.2*np.sin(flow*5-ph),0,1)
    tau+=ribbon*detail
   a=tau*sc['opacity']*smooth(u/.08)*smooth((1-u)/.4)*(1-u)**.4*self.steam_mask
   f=f*(1-a[...,None])+np.float32([196,192,179])*a[...,None]
  if 'snow' in enabled:
   a=np.zeros((self.h,self.w),np.float32)
   for sx,sy,vx,vy,r,opacity,offset,life,depth in self.flakes:
    age=(t+offset)%life;fade=float(smooth(age/.7)*smooth((life-age)/.7))
    x=sx+vx*(age-life/2);y=sy+vy*(age-life/2)
    rr=int(np.ceil(r*3+3));x0=max(0,int(x)-rr);x1=min(self.w,int(x)+rr+2);y0=max(0,int(y)-rr);y1=min(self.h,int(y)+rr+2)
    if x1<=x0 or y1<=y0:continue
    xx=self.x[y0:y1,x0:x1];yy=self.y[y0:y1,x0:x1];p=np.zeros_like(xx)
    for dt,w in [(-.012,.25),(0,.5),(.012,.25)]:p+=w*np.exp(-.5*(((xx-x-vx*dt)/r)**2+((yy-y-vy*dt)/r)**2))
    p*=opacity*fade
    if depth=='far':p*=1-self.bridge[y0:y1,x0:x1]
    a[y0:y1,x0:x1]=1-(1-a[y0:y1,x0:x1])*(1-p)
   a*=self.glass;f=f*(1-a[...,None])+np.float32([228,238,247])*a[...,None]
  f=np.uint8(np.rint(np.clip(f,0,255)))
  allowed=np.logical_or.reduce([self.layer_masks[n] for n in enabled])
  assert np.array_equal(f[~allowed],self.base[~allowed]),'Protected pixels changed'
  return f
 def fingerprint(self):return {p:digest(H/p) for p in ['source.png','scene.json','render.py','review_tools.py']}
def samples(s):
 (H/'masks').mkdir(exist_ok=True)
 for n,m in s.masks.items():Image.fromarray(np.uint8(m*255)).save(H/'masks'/f'{n}.png')
 for t in [0,2,4,8,12,16,19+29/30]:Image.fromarray(s.frame(t)).save(H/f'sample-{t:.3f}.png')
 checks={}
 for n,m in s.layer_masks.items():
  first=s.frame(0,n);assert np.array_equal(first,s.frame(20,n))
  seam=float(np.abs(s.frame(-1/30,n)[m].astype(float)-first[m]).mean())
  steps=[float(np.abs(s.frame(t+1/30,n)[m].astype(float)-s.frame(t,n)[m]).mean()) for t in [0,.1,1,3,7,11,16,19.5]]
  assert seam<=max(steps)*1.15+.02,(n,seam,max(steps))
  checks[n]={'endpoint_exact':True,'seam_mae':seam,'normal_max':max(steps)}
 save('analytic-validation.json',{'fingerprint':s.fingerprint(),'layers':checks,'protected_pixels':'asserted every frame','artwork_selected':True,'animation_user_approved':False})
 print('Samples and analytical checks passed',flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['samples','isolated','preview']);a=p.parse_args();s=Scene()
 if a.stage=='samples':samples(s);return
 results=[]
 if a.stage=='isolated':
  for name in ['sky','weather','interior','lighting']:
   out=H/f'{name}-isolated-8s.mp4';item=encode(s,out,8,name);item['validation']=decode_verify(s,out,240)[0];results.append(item)
 else:
  out=H/'Below-the-Snowline-v1-preview-20s.mp4';item=encode(s,out,20);item['validation'],hashes=decode_verify(s,out,600,True);results.append(item)
  rep=H/'Below-the-Snowline-v1-three-loops-60s.mp4'
  subprocess.run(['ffmpeg','-v','error','-n','-stream_loop','2','-i',str(out),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(rep)],check=True)
  validation,_=decode_verify(s,rep,1800,True,hashes);results.append({'path':rep.name,'sha256':digest(rep),'validation':validation})
 save(a.stage+'-validation.json',{'fingerprint':s.fingerprint(),'clips':results,'review':'Temporal still inspection only; user playback review pending'})
if __name__=='__main__':main()
