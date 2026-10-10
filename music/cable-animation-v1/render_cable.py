"""Source-bound Cable Station adapter; periodic cloud transport from Floodplain/Saltline."""
from pathlib import Path
import sys,json,hashlib,argparse,subprocess
import cv2,numpy as np
from PIL import Image
H=Path(__file__).resolve().parent;ROOT=H.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from ambient_effects import smoothstep,event_amount
from render_floodplain import encode,verify,digest
cv2.setNumThreads(4)

class Cable:
 def __init__(self,config='scene-plan-v1.json'):
  self.path=H/config;self.config=json.loads(self.path.read_text());c=self.config;self.duration=c['duration']
  src=ROOT/c['source']['path'];assert digest(src)==c['source']['sha256']
  self.base=np.array(Image.open(src).convert('RGB'));self.h,self.w=self.base.shape[:2];assert [self.w,self.h]==c['source']['dimensions']
  self.masks={};self.clouds=[];self.lights=[];self.screens=[]
  protected=np.zeros((self.h,self.w),np.uint8)
  for a,b,width in c['protected_lines']:cv2.line(protected,tuple(a),tuple(b),255,width,cv2.LINE_8)
  for x,y,rx,ry in c['protected_ellipses']:cv2.ellipse(protected,(x,y),(rx,ry),0,0,360,255,-1)
  self.protected=protected>0
  for cloud in c['clouds']:
   name=cloud['name'];full=self.poly(cloud['polygons']);full[self.protected]=0
   dist=cv2.distanceTransform(full,cv2.DIST_L2,5)
   m=smoothstep(np.maximum(dist-1,0)/cloud['feather']).astype(np.float32);self.masks[name]=m
   # Separate local regions prevent large empty interior areas entering texture preparation.
   for poly in cloud['polygons']:
    pm=self.poly([poly]);pm[self.protected]=0;yy,xx=np.where(pm>0)
    x0=max(0,int(xx.min())-40);y0=max(0,int(yy.min())-20);x1=min(self.w,int(xx.max())+41);y1=min(self.h,int(yy.max())+21)
    local=m[y0:y1,x0:x1]*np.float32(pm[y0:y1,x0:x1]>0)
    patch=self.base[y0:y1,x0:x1];invalid=np.uint8(pm[y0:y1,x0:x1]==0)*255
    clean=cv2.inpaint(patch,invalid,5,cv2.INPAINT_TELEA).astype(np.float32)
    clean=cv2.GaussianBlur(clean,(0,0),.5)
    y,x=np.mgrid[:y1-y0,:x1-x0].astype(np.float32)
    offset=(y+y0)/700+(x+x0)/2600+cloud['phase']
    self.clouds.append((name,cloud,(x0,y0,x1,y1),local,clean,x,y,offset))
  lights=np.zeros((self.h,self.w),np.float32)
  for light in c['lights']:
   aperture=self.poly([light['polygon']]).astype(np.float32)
   spill=cv2.GaussianBlur(aperture,(0,0),1.1)*.08
   spill[spill<.002]=0;mask=np.clip(aperture+spill,0,1)
   lights=np.maximum(lights,mask);yy,xx=np.where(mask>0);roi=(xx.min(),yy.min(),xx.max()+1,yy.max()+1)
   x0,y0,x1,y1=roi;self.lights.append((light,roi,mask[y0:y1,x0:x1]))
  self.masks['lights']=lights
  screen=np.zeros((self.h,self.w),np.float32);sc=c['screen'];aperture=self.poly([sc['polygon']])
  for i,(x0,y0,x1,y1) in enumerate(sc['bands']):
   patch=self.base[y0:y1,x0:x1].astype(float)
   # Restrict modulation to the original cool status strokes, not blank screen pixels.
   mask=np.float32((patch[:,:,2]>patch[:,:,0]*1.12)&(patch[:,:,1]>43))*aperture[y0:y1,x0:x1]
   screen[y0:y1,x0:x1]=np.maximum(screen[y0:y1,x0:x1],mask)
   self.screens.append(((x0,y0,x1,y1),mask,sc['starts'][i],sc['holds'][i],sc['depths'][i]))
  self.masks['screen']=screen
  self.layer_masks={k:v>0 for k,v in self.masks.items()};self.active=np.logical_or.reduce(list(self.layer_masks.values()))

 def poly(self,polygons):
  p=np.zeros((self.h,self.w),np.uint8)
  for points in polygons:cv2.fillPoly(p,[np.array(points,np.int32)],1)
  return p

 def frame(self,t,only=None,prototype=False):
  t=float(t)%self.duration;f=self.base.astype(np.float32)
  for name,c,(x0,y0,x1,y1),mask,clean,x,y,offset in self.clouds:
   if only not in (None,name,'atmosphere'):continue
   moving=np.zeros_like(clean)
   # Same periodic forward transport as accepted Floodplain/Saltline cloud layers.
   for shift in (0,.5):
    age=(t/self.duration+offset+shift)%1;weight=np.sin(np.pi*age)**2
    mx=x-c['speed']*self.duration*(age-.5)
    layer=cv2.remap(clean,mx.astype(np.float32),y,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
    moving+=layer*weight[...,None]
   f[y0:y1,x0:x1]+=mask[...,None]*(moving-clean)
  if only in (None,'lights'):
   for c,(x0,y0,x1,y1),mask in self.lights:
    amount=event_amount(t,self.duration,c['start'],c['hold'],c['transition'])
    f[y0:y1,x0:x1]*=1-mask[...,None]*amount*(1-c['floor'])
  if only in (None,'screen'):
   for (x0,y0,x1,y1),mask,start,hold,depth in self.screens:
    f[y0:y1,x0:x1]*=1-mask[...,None]*event_amount(t,self.duration,start,hold,.45)*depth
  assert np.isfinite(f).all()
  f=np.uint8(np.rint(np.clip(f,0,255)))
  mask=self.active if only in (None,'atmosphere') else self.layer_masks[only]
  assert np.array_equal(f[~mask],self.base[~mask]),'Protected source changed'
  assert np.array_equal(f[self.protected],self.base[self.protected]),'Cable or planet changed'
  return f

 def fingerprint(self):
  return {'source_sha256':self.config['source']['sha256'],'config_sha256':digest(self.path),'renderer_sha256':digest(__file__),'dependencies':{n:digest(ROOT/'scripts'/n) for n in ['ambient_effects.py','render_floodplain.py','water_surface.py']},'effective_masks':{k:hashlib.sha256(v.tobytes()).hexdigest() for k,v in self.masks.items()}}

def samples(s):
 masks=H/'masks';masks.mkdir(exist_ok=True)
 overlay=s.base.astype(float)
 colors=[[40,155,255],[50,235,160],[255,130,60],[230,100,220],[255,220,0],[30,250,240]]
 for (name,m),color in zip(s.masks.items(),colors):
  cv2.imwrite(str(masks/(name+'.png')),np.uint8(np.rint(m*255)))
  alpha=m[...,None]*.45;overlay=overlay*(1-alpha)+np.array(color)*alpha
 Image.fromarray(np.uint8(overlay)).save(H/'mask-review.png')
 for t in [0,4,8,12,16,19+29/30]:Image.fromarray(s.frame(t)).save(H/f'sample-{t:.3f}s.png')
 report={}
 for name,mask in s.layer_masks.items():
  assert np.array_equal(s.frame(0,name),s.frame(20,name))
  seam=float(abs(s.frame(-1/30,name)[mask].astype(float)-s.frame(0,name)[mask]).mean())
  ordinary=[float(abs(s.frame(t+1/30,name)[mask].astype(float)-s.frame(t,name)[mask]).mean()) for t in np.arange(0,20,1)]
  assert seam<=max(ordinary)*1.1+.01,(name,seam,max(ordinary))
  report[name]={'exact_periodic_endpoint':True,'seam_mae':seam,'ordinary_max_sampled':max(ordinary),'pass':True}
 assert not np.array_equal(s.frame(0),s.frame(10))
 (H/'analytic-validation.json').write_text(json.dumps({'fingerprint':s.fingerprint(),'layers':report,'protected_source_pixels':'asserted per generated frame','inspection':'not yet visually reviewed','user_motion_approved':False},indent=2)+'\n')
 print('Source/masks/samples and analytic seams ready',flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['samples','isolated','preview'],required=True);p.add_argument('--config',default='scene-plan-v1.json');a=p.parse_args()
 s=Cable(a.config);items=[]
 if a.stage=='samples':samples(s);return
 if a.stage=='isolated':
  for name in ['valley','sky','ravine','left_fog']:
   out=H/f'{name}-isolated-v1-8s.mp4';item=encode(s,out,8,name);item['validation']=verify(s,out,240);items.append(item)
 else:
  out=H/'last-cable-station-v1-preview-20s.mp4';item=encode(s,out,20);item['validation']=verify(s,out,600,True);items.append(item)
  repeat=H/'last-cable-station-v1-three-loops-60s.mp4';assert not repeat.exists()
  subprocess.run([s.config['ffmpeg'],'-v','error','-n','-stream_loop','2','-i',str(out),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
  v=verify(s,repeat,1800,True)
  cap=cv2.VideoCapture(str(repeat));hs=[]
  while True:
   ok,f=cap.read()
   if not ok:break
   hs.append(hashlib.sha256(f.tobytes()).hexdigest())
  cap.release();assert hs[:600]==hs[600:1200]==hs[1200:]
  items.append({'path':repeat.relative_to(ROOT).as_posix(),'sha256':digest(repeat),'validation':v,'three_repeated_decoded_payloads_identical':True})
  cap=cv2.VideoCapture(str(out));ok,f=cap.read();cap.release();assert ok;cv2.imwrite(str(H/'decoded-preview-frame.png'),f)
 (H/f'{a.stage}-validation.json').write_text(json.dumps({'fingerprint':s.fingerprint(),'clips':items,'user_motion_approved':False,'inspection':'Source masks and temporal stills inspected; continuous playback not claimed','silent':True},indent=2)+'\n')
 print(a.stage+' checks passed',flush=True)
if __name__=='__main__':main()
