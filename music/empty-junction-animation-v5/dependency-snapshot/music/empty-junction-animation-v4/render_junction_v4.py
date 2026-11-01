"""Revised scene adapter; reuse Junction effects with a fully fresh source map."""
from pathlib import Path
import sys,json,hashlib,argparse,subprocess,time
import cv2,numpy as np
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(H.parent/'empty-junction-animation-v3'))
import render_junction_v3 as v3
from render_junction_v3 import RouteField,Plume,EvolvingField,smoothstep,byte,digest
cv2.setNumThreads(4)
def save(name,value):(H/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
class Junction(v3.Junction):
 def __init__(self):
  self.path=H/'scene-plan-v4.json';self.config=json.loads(self.path.read_text(encoding='utf-8'));c=self.config
  self.source_path=R/c['source']['path'];assert digest(self.source_path)==c['source']['sha256']
  self.base=np.array(Image.open(self.source_path).convert('RGB'));self.h,self.w=self.base.shape[:2];assert [self.w,self.h]==c['source']['dimensions']
  self.shape=(self.h,self.w);self.y,self.x=np.mgrid[:self.h,:self.w].astype(np.float32);self.duration=60;self.masks={}
  self.prepare_sky();self.prepare_mist();self.prepare_lights();a,b,z,d=self.sky_roi
  self.bank=EvolvingField(self.x[b:d,a:z],self.y[b:d,a:z],c['cloud_bank']);self.extra=[]
  self.sky_reference_field=self.cloud_field(0);self.bank_reference=self.bank.density(0)[0]
  for name,cc in c['new_motion'].items():
   m=self.poly(cc.get('polygons',[cc.get('polygon')]),cc['feather'])
   if cc.get('blockers'):m*=1-self.poly(cc['blockers'],2)
   if name=='terrain_flow':m*=1-self.poly(c['weather_blockers'],1)
   m[m<.002]=0;(a,b,z,d),mask=self.crop(m);x=self.x[b:d,a:z];y=self.y[b:d,a:z]
   fields=[Plume(x,y,cc)] if name=='cabin_exhaust' else [RouteField(x,y,{**cc,**r,'seed':cc['seed']+i}) for i,r in enumerate(cc['routes'])] if name=='yard_powder' else [RouteField(x,y,cc)]
   self.masks[name]=m;self.extra.append((name,(a,b,z,d),mask,fields))
  self.layer_masks={k:m>0 for k,m in self.masks.items()}
  self.layer_masks['pass_weather']=self.layer_masks['far_mist']|self.layer_masks['middle_mist']|self.layer_masks['terrain_flow']
  self.layer_masks['habitation']=np.logical_or.reduce([m for k,m in self.layer_masks.items() if k.startswith('light_')])
  self.active=np.logical_or.reduce(list(self.layer_masks.values()))
 def cloud_field(self,t):
  c=self.config['sky'];a,b,z,d=self.sky_roi;field=np.zeros_like(self.sky_background)
  for x,y,sprite,phase,speed in self.clouds:
   age=(t+phase+30)%60-30;fade=float(smoothstep((30-abs(age))/c['fade']))
   tx=x+speed*age;ix=int(np.floor(tx));hh,ww=sprite.shape[:2]
   shifted=cv2.warpAffine(sprite,np.float32([[1,0,tx-ix+1],[0,1,0]]),(ww+3,hh),flags=cv2.INTER_LINEAR)
   xa=max(0,ix-1);xb=min(z-a,ix+ww+2)
   if xb>xa:field[y:y+hh,xa:xb]+=shifted[:,xa-(ix-1):xb-(ix-1)]*fade
  return field
 def sky(self,f,t):
  # Apply transport differences around the photographed sky, rather than
  # replacing it with a normalized reconstruction at a coarse skyline edge.
  a,b,z,d=self.sky_roi
  f[b:d,a:z]+=(self.cloud_field(t)-self.sky_reference_field)*self.sky_mask[...,None]
  alpha,color=self.bank.density(t)
  f[b:d,a:z]+=(alpha-self.bank_reference)[...,None]*(color-self.base[b:d,a:z])*self.sky_mask[...,None]*.35
 def wind_envelope(self,t):
  age=float(t)%60
  return float(smoothstep(age/5)*smoothstep((60-age)/8))
 def apply_extra(self,f,t,name,roi,mask,fields,strength=1):
  a,b,z,d=roi
  for field in fields:
   alpha,color=field.density(t);alpha*=mask*strength
   if name=='yard_powder':
    src=f[b:d,a:z];warmth=smoothstep((src[:,:,0]-src[:,:,2]-10)/45)*.42
    color=color+(np.float32([207,160,100])-color)*warmth[...,None]
   elif name=='cabin_exhaust':
    cc=self.config['new_motion'][name];ax,ay=cc['anchor'];warm=np.exp(-((self.x[b:d,a:z]-ax)/45)**2-((self.y[b:d,a:z]-ay)/35)**2)*.12
    color=color+(np.float32([209,176,128])-color)*warm[...,None]
   f[b:d,a:z]=f[b:d,a:z]*(1-alpha[...,None])+color*alpha[...,None]
  return f
 def frame_float(self,t,only=None,include_powder=True):
  t=float(t)%60;f=v3.v2.Junction.frame_float(self,t,only)
  for name,roi,mask,fields in self.extra:
   if name=='yard_powder' and not include_powder:continue
   if only is not None and only!=name and not(only=='pass_weather' and name=='terrain_flow'):continue
   f=self.apply_extra(f,t,name,roi,mask,fields,self.wind_envelope(t) if name=='yard_powder' else 1)
  assert np.isfinite(f).all();return f
 def frame(self,t,only=None,prototype=False):
  f=byte(self.frame_float(t,only));m=self.active if only is None else self.layer_masks[only]
  assert np.array_equal(f[~m],self.base[~m]),'Protected pixels changed';return f
 def variants(self,t):
  quiet=self.frame_float(t,include_powder=False);wind=quiet.copy()
  for name,roi,mask,fields in self.extra:
   if name=='yard_powder':wind=self.apply_extra(wind,t,name,roi,mask,fields,self.wind_envelope(t))
  q,w=byte(quiet),byte(wind)
  assert np.array_equal(q[~self.active],self.base[~self.active]);assert np.array_equal(w[~self.active],self.base[~self.active])
  assert np.array_equal(q[~self.layer_masks['yard_powder']],w[~self.layer_masks['yard_powder']])
  return w,q
 def fingerprint(self):
  dependencies=['music/empty-junction-animation-v1/render_junction.py','music/empty-junction-animation-v2/render_junction_v2.py','music/empty-junction-animation-v3/render_junction_v3.py','scripts/ambient_effects.py','scripts/render_floodplain.py','scripts/water_surface.py','music/saltline-animation-v1/dust_transport.py','music/saltline-animation-v1/periodic_transport.py','music/farpoint-animation-v1/render_farpoint.py']
  paths=[self.source_path,self.path,Path(__file__),H/'build_plan.py']+[R/p for p in dependencies]
  return {'files':{p.relative_to(R).as_posix():digest(p) for p in paths},'masks':{k:hashlib.sha256(m.tobytes()).hexdigest() for k,m in self.masks.items()},
   'runtime':{'python':sys.version,'numpy':np.__version__,'opencv':cv2.__version__},'duration':60,'source':self.config['source']}
def encoder(s,out):
 assert not out.exists(),out
 return subprocess.Popen([s.config['ffmpeg'],'-v','error','-n','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r','30','-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-qp','0','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],stdin=subprocess.PIPE)
def encode(s,out,seconds,only=None):
 proc=encoder(s,out)
 try:
  for i in range(round(seconds*30)):
   f=cv2.resize(s.frame(i/30,only),(1280,720),interpolation=cv2.INTER_AREA);proc.stdin.write(f.tobytes())
   if i and i%150==0:print(out.name,i,'/',round(seconds*30),flush=True)
 finally:proc.stdin.close()
 assert proc.wait()==0
def samples(s):
 (H/'masks').mkdir(exist_ok=True)
 for name,m in s.masks.items():Image.fromarray(byte(m*255)).save(H/'masks'/f'{name}.png')
 overlay=s.base.astype(np.float32)
 for name,col in [('sky_clouds',[70,180,255]),('pass_weather',[100,230,190]),('yard_powder',[230,170,70]),('cabin_exhaust',[210,100,250]),('habitation',[255,100,90])]:
  a=s.layer_masks[name][...,None]*.35;overlay=overlay*(1-a)+np.float32(col)*a
 Image.fromarray(byte(overlay)).save(H/'mask-overlay.png')
 for t in [0,4,8,16,24,36,48,56,59+29/30]:
  Image.fromarray(cv2.resize(s.frame(t),(1280,720),interpolation=cv2.INTER_AREA)).save(H/f'sample-{t:05.2f}s.png')
 for layer in ['yard_powder','cabin_exhaust','pass_weather','habitation','sky_clouds']:
  for t in [4,8,16,36,48]:Image.fromarray(cv2.resize(s.frame(t,layer),(1280,720),interpolation=cv2.INTER_AREA)).save(H/f'{layer}-{t:02d}s.png')
 checks={}
 for layer in ['yard_powder','cabin_exhaust','pass_weather','habitation','sky_clouds']:
  m=s.layer_masks[layer];assert np.array_equal(s.frame(0,layer),s.frame(60,layer))
  times=[-1/30,0,4.1,8.3,16.4,24.2,36,48,56,58];changes=[]
  for t in times:changes.append(float(np.abs(s.frame(t+1/30,layer).astype(np.float32)-s.frame(t,layer)).mean(axis=2)[m].mean()))
  assert changes[0]<=max(changes[1:])*1.1+.01,(layer,changes)
  checks[layer]={'periodic_state':True,'seam_mae':changes[0],'ordinary_max_sample_mae':max(changes[1:]),'pass':True}
 assert len({hashlib.sha256(s.frame(t).tobytes()).hexdigest() for t in [0,20,40]})==3
 save('analytic-validation.json',{'fingerprint':s.fingerprint(),'layer_checks':checks,'distinct_0_20_40':True,'protected_pixels':'Asserted for every native frame','user_approved':False})
 print('Fresh masks, temporal samples and analytical checks ready',flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['samples','isolated','preview'],required=True);a=p.parse_args();s=Junction()
 if a.stage=='samples':samples(s);return
 if a.stage=='isolated':
  for layer in ['yard_powder','cabin_exhaust']:encode(s,H/f'{layer}-v4-isolated-8s.mp4',8,layer)
  print('Two principal full-composition tests ready',flush=True);return
 out=H/'Empty-Junction-v4-wind-minute-720p.mp4';quiet=H/'Empty-Junction-v4-quiet-minute-720p.mp4';pw,pq=encoder(s,out),encoder(s,quiet)
 started=time.time()
 try:
  for i in range(1800):
   w,q=s.variants(i/30)
   for frame,proc in [(w,pw),(q,pq)]:proc.stdin.write(cv2.resize(frame,(1280,720),interpolation=cv2.INTER_AREA).tobytes())
   if i and i%150==0:print('paired minute',i,'/ 1800,',round(time.time()-started,1),'seconds',flush=True)
 finally:pw.stdin.close();pq.stdin.close()
 assert pw.wait()==pq.wait()==0
 save('render-record.json',{'fingerprint':s.fingerprint(),'files':[{'file':p.name,'sha256':digest(p),'frames':1800,'fps':30,'silent':True} for p in [out,quiet]],
  'quiet_difference':'Only yard powder omitted; all other rendered native pixels equal outside its mask for all 1800 frames.',
  'wind_timing':'Powder fades inside the active minute; schedule wind, quiet, quiet for the requested one-minute-on/two-minute-off cycle.'})
 print('Paired genuine sixty-second units rendered',flush=True)
if __name__=='__main__':main()
