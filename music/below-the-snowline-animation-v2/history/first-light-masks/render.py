from pathlib import Path
import sys,copy,json,hashlib,argparse,subprocess,time
sys.dont_write_bytecode=True
import baseline
from baseline import np,cv2,Image,smooth,H
from review_tools import encode,decode_verify
def save(n,d):(H/n).write_text(json.dumps(d,indent=2)+'\n')
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bounds(m,pad=0):
 y,x=np.where(m>0);return max(0,int(x.min())-pad),max(0,int(y.min())-pad),min(1672,int(x.max())+1+pad),min(941,int(y.max())+1+pad)
class Scene:
 def __init__(self):
  self.parent=baseline.Scene();s=self.parent;self.base=s.base;self.c=s.c;self.h,self.w=s.h,s.w;self.masks=dict(s.masks);self.views={}
  for name,m in s.masks.items():
   r=(0,0,s.w,s.h) if name=='snow' else bounds(m,55 if name=='sky' else 2)
   a,b,z,d=r;v=copy.copy(s);v.origin=(a,b);v.h=d-b;v.w=z-a
   for key in ['base','x','y','sky','skyvalid','sky_distance','glass','bridge','radar','readout','steam_mask']:setattr(v,key,getattr(s,key)[b:d,a:z].copy())
   v.masks={k:value[b:d,a:z] for k,value in s.masks.items()};v.layer_masks={k:value>0 for k,value in v.masks.items()}
   v.windows=[(c,m[b:d,a:z]) for c,m in s.windows];v.fog=[(c,m[b:d,a:z],n) for c,m,n in s.fog];self.views[name]=(r,v)
  self.additions={};self.buttons=[];self.keys=[];self.bridge=[];self.screens=[]
  for c in self.c['button_groups']:
   x,y=c['xy'];rx,ry=c['size'];m=self.poly([[x-rx/2,y-ry/2],[x+rx/2,y-ry/2],[x+rx/2,y+ry/2],[x-rx/2,y+ry/2]],.9)
   self.buttons.append((c,m))
  self.masks['buttons']=np.maximum.reduce([m for c,m in self.buttons])
  for i,p in enumerate(self.c['keys']):self.keys.append((i,self.poly(p,.8)))
  self.masks['keys']=np.maximum.reduce([m for i,m in self.keys])
  for c in self.c['bridge_lights']:
   m=self.poly(c['poly'],.8);self.bridge.append((c,m))
  self.masks['bridge_lights']=np.maximum.reduce([m for c,m in self.bridge])
  for c in self.c['habitat_screens']:self.screens.append((c,self.poly(c['poly'],.8)))
  self.masks['habitat_activity']=np.maximum.reduce([m for c,m in self.screens])
  self.lamp=self.poly(self.c['lamp_poly'],1.8);self.spill=self.poly(self.c['spill_poly'],24)*.13
  # Keep instrument glass/keys out of broad reflected practical light.
  self.spill*=1-np.maximum.reduce([self.masks[n] for n in ['terminals','buttons','keys']])
  self.masks['room_practical']=np.maximum(self.lamp,self.spill)
  self.layer_masks={n:m>0 for n,m in self.masks.items()};self.active=np.logical_or.reduce(list(self.layer_masks.values()))
  self.groups={'weather':['sky','far_powder','ravine_mist','ledge_spindrift','snow'],'controls':['terminals','buttons','keys','coffee_steam','room_practical'],'base_activity':['windows','bridge_lights','habitat_activity']}
  self.guard=self.poly(self.c['dish_guard'],0)>0
 def poly(self,p,feather):return self.parent.poly(p,feather)
 def apply(self,f,m,fn):
  a,b,z,d=bounds(m);f[b:d,a:z]=fn(f[b:d,a:z],m[b:d,a:z],a,b)
 def frame(self,t,only=None):
  t=float(t)%20;enabled=set(self.masks) if only is None else set(self.groups.get(only,[only]));f=self.base.copy()
  # Original layer order, region-local evaluation, quantized only at isolated
  # layer boundaries. The native source remains the same for every frame.
  for name in ['sky','far_powder','ravine_mist','ledge_spindrift','windows','terminals','coffee_steam']:
   if name not in enabled:continue
   r,v=self.views[name];a,b,z,d=r;v.base=f[b:d,a:z].copy();f[b:d,a:z]=v.frame(t,name)
  f=f.astype(np.float32)
  if 'buttons' in enabled:
   for c,m in self.buttons:
    age=(t-c['phase'])%20;level=.08+.92*float(smooth(age/.4)*smooth((5.1-age)/.8))
    self.apply(f,m,lambda p,q,a,b:p*(1-q[...,None]*.85)+np.float32(c['color'])*q[...,None]*level*.85)
  if 'keys' in enabled:
   for i,m in self.keys:
    phase=(t-i*1.3)%10;dip=float(smooth(phase/.55)*smooth((2.8-phase)/.7))
    self.apply(f,m,lambda p,q,a,b:p*(1-q[...,None]*dip*.70))
  if 'bridge_lights' in enabled:
   for c,m in self.bridge:
    age=(t-c['phase'])%20;dip=float(smooth(age/.8)*smooth((4-age)/1.1))
    self.apply(f,m,lambda p,q,a,b:p*(1-q[...,None]*dip*.62))
  if 'habitat_activity' in enabled:
   for c,m in self.screens:
    def display(p,q,a,b):
     yy,xx=np.mgrid[b:b+p.shape[0],a:a+p.shape[1]];scan=.35+.65*(.5+.5*np.sin(yy*.9-2*np.pi*t/5+c['phase']))
     alpha=q*(.42+.32*np.sin(2*np.pi*t/20+c['phase'])**2)
     return p*(1-alpha[...,None])+np.float32(c['color'])*scan[...,None]*alpha[...,None]
    self.apply(f,m,display)
  if 'room_practical' in enabled:
   age=(t-11.3)%20;dip=float(smooth(age/1.1)*smooth((4.2-age)/1.8))*.19
   self.apply(f,self.masks['room_practical'],lambda p,q,a,b:p*(1-q[...,None]*dip))
  f=np.uint8(np.rint(np.clip(f,0,255)))
  if 'snow' in enabled:
   r,v=self.views['snow'];v.base=f;f=v.frame(t,'snow')
  allowed=np.logical_or.reduce([self.layer_masks[n] for n in enabled]);assert np.array_equal(f[~allowed],self.base[~allowed])
  if only=='sky':assert np.array_equal(f[self.guard],self.base[self.guard]),'Dish geometry transported'
  return f
 def fingerprint(self):return {n:digest(H/n) for n in ['source.png','scene.json','baseline.py','render.py','review_tools.py']}
def samples(s):
 (H/'masks').mkdir(exist_ok=True)
 for n,m in s.masks.items():Image.fromarray(np.uint8(m*255)).save(H/'masks'/f'{n}.png')
 for t in [0,2,4,8,12,16,19+29/30]:Image.fromarray(s.frame(t)).save(H/f'sample-{t:.3f}.png')
 checks={}
 for n,m in s.layer_masks.items():
  first=s.frame(0,n);assert np.array_equal(first,s.frame(20,n))
  seam=float(np.abs(s.frame(-1/30,n)[m].astype(float)-first[m]).mean());steps=[float(np.abs(s.frame(t+1/30,n)[m].astype(float)-s.frame(t,n)[m]).mean()) for t in [0,.1,1,3,7,11,16,19.5]]
  assert seam<=max(steps)*1.15+.02,(n,seam,max(steps))
  checks[n]={'endpoint_exact':True,'seam_mae':seam,'ordinary_max':max(steps)}
 save('analytic-validation.json',{'fingerprint':s.fingerprint(),'layers':checks,'dish_guard_exact_in_sky_layer':True,'motion_user_approved':False})
 print('Samples and analytic checks passed',flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['samples','isolated','preview']);a=p.parse_args();s=Scene();results=[]
 if a.stage=='samples':samples(s);return
 if a.stage=='isolated':
  for name in ['sky','controls','base_activity']:
   out=H/f'{name}-isolated-8s.mp4';item=encode(s,out,8,name);item['validation']=decode_verify(s,out,240)[0];results.append(item)
 else:
  out=H/'Below-the-Snowline-v2-preview-20s.mp4';item=encode(s,out,20);item['validation'],hashes=decode_verify(s,out,600,True);results.append(item)
  rep=H/'Below-the-Snowline-v2-three-loops-60s.mp4';subprocess.run(['ffmpeg','-v','error','-n','-stream_loop','2','-i',str(out),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(rep)],check=True)
  val,_=decode_verify(s,rep,1800,True,hashes);results.append({'path':rep.name,'sha256':digest(rep),'validation':val})
 save(a.stage+'-validation.json',{'fingerprint':s.fingerprint(),'clips':results,'review':'Temporal and decoded still inspection; continuous playback not claimed'})
if __name__=='__main__':main()
