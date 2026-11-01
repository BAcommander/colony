"""V3 adds scene-mapped directed weather and an anchored cabin plume to v2."""
from pathlib import Path
import sys,json,hashlib,argparse,subprocess
import cv2,numpy as np
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(H.parent/'empty-junction-animation-v2'))
import render_junction_v2 as v2
from render_junction_v2 import previous,EvolvingField,smoothstep,byte,digest,encode,verify
def save(name,data):(H/name).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')

def route(points,widths,count=150):
 # Catmull-Rom interpolation retains fixed anchors with smooth tangent changes.
 p=np.float32(points);p=np.vstack([p[0],p,p[-1]])
 out=[];ws=[]
 for u in np.linspace(0,len(points)-1,count):
  i=min(int(u),len(points)-2);q=u-i;a,b,c,d=p[i:i+4]
  out.append(.5*((2*b)+(-a+c)*q+(2*a-5*b+4*c-d)*q*q+(-a+3*b-3*c+d)*q*q*q))
  ws.append(np.interp(u,np.arange(len(widths)),widths))
 out=np.float32(out);arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(out,axis=0),axis=1))]
 return out,np.float32(ws),arc

class RouteField:
 def __init__(self,x,y,c):
  self.c=c;points,widths,arc=route(c['path'],c['widths'])
  dist=np.full(x.shape,1e9,np.float32);self.s=np.zeros_like(x);self.cross=np.zeros_like(x);self.width=np.zeros_like(x)
  for i,(px,py) in enumerate(points):
   d=(x-px)**2+(y-py)**2;take=d<dist
   tangent=points[min(i+1,len(points)-1)]-points[max(0,i-1)]
   normal=np.float32([-tangent[1],tangent[0]])/max(float(np.linalg.norm(tangent)),1e-5)
   self.cross[take]=((x-px)*normal[0]+(y-py)*normal[1])[take];self.s[take]=arc[i];self.width[take]=widths[i];dist[take]=d[take]
  self.env=smoothstep(self.s/14)*smoothstep((arc[-1]-self.s)/27)
  rng=np.random.default_rng(c['seed']);self.phases=rng.uniform(0,2*np.pi,7)
 def density(self,t):
  c=self.c;phase=2*np.pi*(self.s/(c['speed']*60)-t/60)
  n=np.zeros_like(self.s)
  for i,(k,weight) in enumerate([(3,.26),(5,.22),(9,.18),(14,.14),(23,.10),(37,.06),(59,.04)]):
   n+=weight*np.sin(k*phase+self.cross/(3+i*1.3)+self.phases[i])
  # Advected streaks curve and break apart along the mapped terrain.
  sway=self.width*.20*np.sin(phase*7+self.phases[0])
  cross=(self.cross-sway)/np.maximum(self.width,1)
  envelope=np.exp(-cross*cross*.9)*self.env
  alpha=np.clip((n+.21)*1.7,0,1)*envelope*c['opacity']
  return alpha,np.float32(c['color'])

class Plume:
 def __init__(self,x,y,c):
  self.x=x;self.y=y;self.c=c;self.points,self.widths,self.arc=route(c['path'],c['widths'],240)
  rng=np.random.default_rng(c['seed'])
  self.phases=(np.arange(c['particles'])+rng.uniform(0,.7,c['particles']))/c['particles']
  self.jitter=rng.uniform(0,2*np.pi,c['particles'])
 def density(self,t):
  c=self.c;tau=np.zeros_like(self.x)
  for phase,jitter in zip(self.phases,self.jitter):
   u=(t/c['lifetime']+phase)%1
   x=np.interp(u,np.linspace(0,1,240),self.points[:,0]);y=np.interp(u,np.linspace(0,1,240),self.points[:,1])
   w=np.interp(u,np.linspace(0,1,240),self.widths)
   birth=(t-u*c['lifetime'])%60
   pulse=.25+1.10*(.5+.5*np.sin(2*np.pi*birth/60*7))**2
   pulse*=.72+.28*np.cos(2*np.pi*birth/60*3)
   y+=w*.35*np.sin(15*u+jitter+2*np.pi*birth/60*3)
   rx=3+.85*w;ry=2+.60*w
   r=((self.x-x)/rx)**2+((self.y-y)/ry)**2
   fade=float(smoothstep(u/.08)*smoothstep((1-u)/.28))
   puff=np.exp(-r*1.4);puff[r>7]=0
   tau+=puff*fade*c['opacity']*pulse
  return np.minimum(1-np.exp(-tau),.48),np.float32(c['color'])

class Junction(v2.Junction):
 def __init__(self):
  self.path=H/'scene-plan-v3.json';self.config=json.loads(self.path.read_text(encoding='utf-8'))
  c=self.config;p=R/c['source']['path'];assert digest(p)==c['source']['sha256']
  self.base=np.array(Image.open(p).convert('RGB'));self.h,self.w=self.base.shape[:2]
  self.shape=(self.h,self.w);self.y,self.x=np.mgrid[:self.h,:self.w].astype(np.float32)
  self.duration=c['duration'];self.masks={};self.prepare_sky();self.prepare_mist();self.prepare_lights()
  a,b,z,d=self.sky_roi;self.bank=EvolvingField(self.x[b:d,a:z],self.y[b:d,a:z],c['cloud_bank'])
  self.extra=[]
  for name,c in self.config['new_motion'].items():
   m=self.poly(c.get('polygons',[c.get('polygon')]),c['feather'])
   if c.get('blockers'):m*=1-self.poly(c['blockers'],2)
   if name=='terrain_flow':m*=1-self.poly(self.config['weather_blockers'],1)
   m[m<.002]=0;(a,b,z,d),mask=self.crop(m);x=self.x[b:d,a:z];y=self.y[b:d,a:z]
   if name=='cabin_exhaust':fields=[Plume(x,y,c)]
   elif name=='yard_powder':fields=[RouteField(x,y,{**c,**r,'seed':c['seed']+i}) for i,r in enumerate(c['routes'])]
   else:fields=[RouteField(x,y,c)]
   self.masks[name]=m;self.extra.append((name,(a,b,z,d),mask,fields))
  self.layer_masks={k:m>0 for k,m in self.masks.items()}
  self.layer_masks['pass_weather']=self.layer_masks['far_mist']|self.layer_masks['middle_mist']|self.layer_masks['terrain_flow']
  self.layer_masks['habitation']=np.logical_or.reduce([m for k,m in self.layer_masks.items() if k.startswith('light_')])
  self.active=np.logical_or.reduce(list(self.layer_masks.values()))
 def frame_float(self,t,only=None):
  t=float(t)%60
  f=super().frame_float(t,only)
  for name,(a,b,z,d),mask,fields in self.extra:
   if only is not None and only!=name and not(only=='pass_weather' and name=='terrain_flow'):continue
   for field in fields:
    alpha,color=field.density(t);alpha*=mask
    if name=='yard_powder':
     # Existing warm pools tint airborne mineral powder; lamp state modulates this light.
     src=f[b:d,a:z]
     warmth=smoothstep((src[:,:,0]-src[:,:,2]-10)/45)*.42
     color=color+(np.float32([207,160,100])-color)*warmth[...,None]
    if name=='cabin_exhaust':
     c=next(c for c,_,_ in self.lights if c['name']=='door_lamp')
     warm=np.exp(-((self.x[b:d,a:z]-520)/48)**2)*.25*(1-self.amount(t,c['events']))
     color=color+(np.float32([209,176,128])-color)*warm[...,None]
    f[b:d,a:z]=f[b:d,a:z]*(1-alpha[...,None])+color*alpha[...,None]
  assert np.isfinite(f).all()
  return f
 def fingerprint(self):
  f=super().fingerprint()
  for p in [Path(__file__),H/'build_plan.py']:f['files'][p.relative_to(R).as_posix()]=digest(p)
  return f

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['samples','isolated','preview'],required=True);args=p.parse_args();s=Junction()
 if args.stage=='samples':
  previous.H=H;previous.samples(s)
  for layer in s.config['new_motion']:
   for t in [0,2,4,8,20,40,50,58]:
    Image.fromarray(cv2.resize(s.frame(t,layer),(1280,720),interpolation=cv2.INTER_AREA)).save(H/f'{layer}-{t:02d}s.png')
  return
 clips=[]
 if args.stage=='isolated':
  for layer in s.config['new_motion']:
   path=H/f'{layer}-v3-isolated-10s.mp4';item=encode(s,path,10,layer,True);item['validation'],_=verify(s,path,300,False);clips.append(item)
 else:
  path=H/'empty-junction-v3-preview-60s.mp4';item=encode(s,path,60);item['validation'],hashes=verify(s,path,1800,True);clips.append(item)
  repeat=H/'empty-junction-v3-three-loops-180s.mp4';assert not repeat.exists()
  subprocess.run([s.config['ffmpeg'],'-v','error','-n','-stream_loop','2','-i',str(path),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
  validation,repeated=verify(s,repeat,5400,True);assert repeated==hashes*3
  clips.append({'path':repeat.relative_to(R).as_posix(),'sha256':digest(repeat),'validation':validation,'exact_three_decoded_repetitions':True})
  save('decoded-frame-hashes.json',hashes)
  cap=cv2.VideoCapture(str(path))
  for n in [0,240,600,1200,1500,1799]:
   cap.set(cv2.CAP_PROP_POS_FRAMES,n);ok,f=cap.read();assert ok;cv2.imwrite(str(H/f'decoded-{n:04d}.png'),f)
  cap.release()
 save(args.stage+'-validation.json',{'fingerprint':s.fingerprint(),'clips':clips,'silent':True,'user_approved':False,'inspection':'Temporal/decoded stills; continuous playback unavailable'})
 print(args.stage,'complete decode and validation passed',flush=True)
if __name__=='__main__':main()
