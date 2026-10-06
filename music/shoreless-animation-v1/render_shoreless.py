"""Shoreless source-bound compositor; reusable reflection/timing/encoding primitives."""
from pathlib import Path
import sys,json,hashlib,argparse,subprocess
import cv2,numpy as np
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(R/'scripts'))
from render_floodplain import ChannelSurface,encode,digest
from ambient_effects import smoothstep,event_amount
cv2.setNumThreads(4)

class Shoreless:
 def __init__(self,path=None):
  self.path=Path(path) if path else H/'scene-plan-v1.json';self.config=json.loads(self.path.read_text(encoding='utf-8'));c=self.config
  assert digest(R/c['source']['path'])==c['source']['sha256']
  self.base=np.array(Image.open(R/c['source']['path']).convert('RGB'));self.h,self.w=self.base.shape[:2];self.duration=c['duration']
  assert [self.w,self.h]==c['source']['dimensions']
  self.y,self.x=np.mgrid[:self.h,:self.w].astype(np.float32)
  window=self.poly([c['window']]);water=self.poly([c['water_polygon']]);water[self.poly(c['water_exclusions'])>0]=0
  structures=self.poly(c.get('protected_polygons',[]))
  for a,b,width in c.get('protected_lines',[]):cv2.line(structures,tuple(a),tuple(b),1,width)
  water[structures>0]=0
  self.masks={'water':self.feather(water,4)}
  wc=c['water'];x0,y0,x1,y1=wc['roi'];self.water=ChannelSurface(self.base[y0:y1,x0:x1],self.masks['water'][y0:y1,x0:x1],wc,(x0,y0))
  sky=self.poly([c['sky_polygon']]);protected=structures.copy()
  for x,y,radius in c['moons']:cv2.circle(protected,(x,y),radius,1,-1)
  for tc in c['turbines']:cv2.circle(protected,tuple(tc['hub']),tc['radius']+3,1,-1)
  sky[protected>0]=0
  self.clouds=[];cloud_union=np.zeros_like(self.x)
  for cc in c['clouds']:
   y0,y1=cc['y_range'];pm=sky.copy();pm[:y0]=0;pm[y1:]=0
   m=self.feather(pm,17);cloud_union=np.maximum(cloud_union,m)
   xslice=(80,max(0,y0-16),1221,min(self.h,y1+16));a,b,z,d=xslice
   invalid=np.uint8(sky[b:d,a:z]==0)*255
   clean=cv2.inpaint(self.base[b:d,a:z],invalid,7,cv2.INPAINT_TELEA).astype(np.float32)
   clean=cv2.GaussianBlur(clean,(0,0),.55)
   yy,xx=np.mgrid[:d-b,:z-a].astype(np.float32);offset=(yy+b)/700+(xx+a)/2600+cc['phase']
   self.clouds.append((cc,xslice,m[b:d,a:z],clean,xx,yy,offset))
  self.masks['sky']=cloud_union
  self.lights=[];lm=np.zeros_like(self.x)
  for lc in c['lights']:
   m=self.aperture(lc['polygons']);lm=np.maximum(lm,m);self.lights.append((lc,m))
  self.masks['lights']=lm
  lum=self.base.astype(np.float32).mean(2);warm=np.clip((self.base[:,:,0].astype(float)-self.base[:,:,2]-12)/100,0,1)
  lc=c['lamp'];core=self.aperture([lc['aperture']])*np.clip((lum-125)/65,0,1)
  x,y=lc['wall_center'];rx,ry=lc['wall_radius'];wall=np.exp(-((self.x-x)/rx)**2-((self.y-y)/ry)**2)*self.feather(self.poly([lc['wall_polygon']]),15)*warm*.65
  x,y=lc['desk_center'];rx,ry=lc['desk_radius'];desk=np.exp(-((self.x-x)/rx)**2-((self.y-y)/ry)**2)*self.feather(self.poly([lc['desk_polygon']]),20)*warm*.38
  self.masks['lamp']=np.maximum.reduce([core,wall,desk]).astype(np.float32);self.masks['lamp'][self.masks['lamp']<.002]=0
  ui=c['computers'];self.masks['computers']=self.feather(self.poly([ui['left_aperture'],ui['right_aperture']]),1.7)
  self.ui_roi=(1344,481,1645,614);a,b,z,d=self.ui_roi
  self.ui_mask=self.masks['computers'][b:d,a:z];self.ui_y,self.ui_x=np.mgrid[b:d,a:z].astype(np.float32)
  q=np.float32(ui['log_quad']);iw,ih=ui['log_size'];rect=np.float32([[0,0],[iw-1,0],[iw-1,ih-1],[0,ih-1]])
  self.log_tex=cv2.warpPerspective(self.base,cv2.getPerspectiveTransform(q,rect),(iw,ih))
  self.log_back=cv2.getPerspectiveTransform(rect,q-np.float32([a,b]));self.log_orig=cv2.warpPerspective(self.log_tex,self.log_back,(z-a,d-b)).astype(np.float32)
  self.log_mask=self.feather(self.poly([ui['log_quad']]),2)[b:d,a:z]
  self.log_y,self.log_x=np.mgrid[:ih,:iw].astype(np.float32)
  mw,mh=ui['meter_size'];quad=np.float32(ui['meter_quad']);rect=np.float32([[0,0],[mw-1,0],[mw-1,mh-1],[0,mh-1]])
  self.meter_back=cv2.getPerspectiveTransform(rect,quad-np.float32([a,b]))
  self.masks['room']=np.maximum(self.masks['lamp'],self.masks['computers'])
  self.rotors=[];rm=np.zeros_like(self.x)
  for tc in c['turbines']:
   cx,cy=tc['hub'];rad=tc['radius']+3;a,b,z,d=cx-rad,cy-rad,cx+rad+1,cy+rad+1
   patch=self.base[b:d,a:z];bm=np.zeros(patch.shape[:2],np.uint8)
   for end in tc['blade_ends']:cv2.line(bm,(rad,rad),(end[0]-a,end[1]-b),255,tc['width']+2,cv2.LINE_AA)
   # The fixed nacelle/mast will be restored over the rotating blade residual.
   clean=cv2.inpaint(patch,bm,4,cv2.INPAINT_TELEA).astype(np.float32)
   alpha=cv2.GaussianBlur(bm.astype(np.float32)/255,(0,0),.45)
   residual=(patch.astype(np.float32)-clean)*alpha[...,None]
   cleanplate=patch.astype(np.float32)*(1-alpha[...,None])+clean*alpha[...,None]
   yy,xx=np.mgrid[:2*rad+1,:2*rad+1];static=((abs(xx-rad)<=1)&(yy>=rad))|((xx-rad)**2+(yy-rad)**2<=2.5**2)
   rm[b:d,a:z]=np.maximum(rm[b:d,a:z],np.float32((xx-rad)**2+(yy-rad)**2<=(rad-1)**2))
   self.rotors.append((tc,(a,b,z,d),rad,residual,cleanplate,static))
  self.masks['turbines']=rm*window
  bm=np.zeros_like(self.x);self.beacons=[]
  for bc in c['beacons']:
   x,y=bc['center'];m=np.exp(-((self.x-x)**2+(self.y-y)**2)/2)*.8+.08*np.exp(-((self.x-x)**2+(self.y-y)**2)/18)
   m[m<.003]=0;bm=np.maximum(bm,m);self.beacons.append((bc,m))
  self.masks['beacons']=bm
  self.layer_masks={k:v>0 for k,v in self.masks.items()};self.active=np.logical_or.reduce(list(self.layer_masks.values()))

 def poly(self,polys):
  m=np.zeros((self.h,self.w),np.uint8)
  for p in polys:cv2.fillPoly(m,[np.array(p,np.int32)],1)
  return m
 def feather(self,m,n):return smoothstep(cv2.distanceTransform(m,cv2.DIST_L2,5)/n).astype(np.float32)
 def aperture(self,polys):
  m=np.zeros((self.h,self.w),np.float32)
  for points in polys:
   p=np.float32(points);a,b=np.floor(p.min(0)).astype(int)-2;z,d=np.ceil(p.max(0)).astype(int)+3;a=max(a,0);b=max(b,0);z=min(z,self.w);d=min(d,self.h)
   hi=np.zeros(((d-b)*4,(z-a)*4),np.uint8);cv2.fillPoly(hi,[np.rint((p-[a,b])*4).astype(np.int32)],255)
   lo=cv2.resize(cv2.GaussianBlur(hi.astype(np.float32)/255,(0,0),1),(z-a,d-b),interpolation=cv2.INTER_AREA);lo[lo<.015]=0
   m[b:d,a:z]=np.maximum(m[b:d,a:z],lo)
  return m
 def draw_computers(self,f,t):
  c=self.config['computers'];a,b,z,d=self.ui_roi;patch=f[b:d,a:z].copy();x=self.ui_x;y=self.ui_y
  points=np.float32(c['route']);phase=t/self.duration;steps=np.linalg.norm(np.diff(points,axis=0),axis=1);distance=phase*steps.sum();point=points[-1]
  for k,length in enumerate(steps):
   if distance<=length:point=points[k]+(points[k+1]-points[k])*distance/length;break
   distance-=length
  fade=smoothstep(t/.8)*smoothstep((self.duration-t)/.8);cx,cy=point
  marker=np.exp(-((x-cx)**2+(y-cy)**2)/(2*c['marker_radius']**2))*fade
  patch+=marker[...,None]*np.array(c['route_color'],np.float32)
  iw,ih=c['log_size'];shift=t/self.duration*ih
  moving=cv2.remap(self.log_tex,self.log_x,(self.log_y+shift).astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_WRAP)
  projected=cv2.warpPerspective(moving,self.log_back,(z-a,d-b)).astype(np.float32)
  patch+=(projected-self.log_orig)*self.log_mask[...,None]
  mw,mh=c['meter_size'];alpha=np.zeros((mh,mw),np.float32);rgb=np.zeros((mh,mw,3),np.float32);rgb[:]=[41,103,121]
  for row in range(3):
   level=.5+.24*np.sin(2*np.pi*t*(row+2)/20+row)+.12*np.sin(2*np.pi*t*7/20)
   for j in range(9):alpha[4+row*8:8+row*8,3+j*4:6+j*4]=np.clip(level*9-j,0,1)*.7
  projected=cv2.warpPerspective(rgb*alpha[...,None],self.meter_back,(z-a,d-b));wa=cv2.warpPerspective(alpha,self.meter_back,(z-a,d-b))
  patch=patch*(1-wa[...,None])+projected
  f[b:d,a:z]+=self.ui_mask[...,None]*(patch-f[b:d,a:z])
 def frame(self,t,only=None,prototype=False):
  t=float(t)%self.duration;f=self.base.astype(np.float32)
  if only in (None,'water'):
   a,b,z,d=self.config['water']['roi'];f[b:d,a:z]=self.water.frame(t)
  if only in (None,'sky'):
   for cc,(a,b,z,d),m,clean,x,y,offset in self.clouds:
    moving=np.zeros_like(clean)
    for phase in (0,.5):
     age=(t/self.duration+offset+phase)%1;weight=np.sin(np.pi*age)**2
     transported=cv2.remap(clean,(x-cc['speed']*self.duration*(age-.5)).astype(np.float32),y,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
     moving+=transported*weight[...,None]
    f[b:d,a:z]+=m[...,None]*(moving-clean)*cc['gain']
  if only in (None,'lights'):
   for lc,m in self.lights:f*=1-m[...,None]*event_amount(t,self.duration,lc['start'],lc['hold'],lc['transition'])*(1-lc['floor'])
  if only in (None,'lamp','room'):
   amount=max(event_amount(t,self.duration,e['start'],e['hold'],e['transition'])*e['depth'] for e in self.config['lamp']['events'])
   f*=1-self.masks['lamp'][...,None]*amount
  if only in (None,'computers','room'):self.draw_computers(f,t)
  if only in (None,'turbines'):
   for tc,(a,b,z,d),rad,residual,clean,static in self.rotors:
    matrix=cv2.getRotationMatrix2D((rad,rad),tc['direction']*360*t/tc['period'],1)
    moving=cv2.warpAffine(residual,matrix,(z-a,d-b),flags=cv2.INTER_LINEAR)
    patch=clean+moving;patch[static]=self.base[b:d,a:z][static]
    m=self.masks['turbines'][b:d,a:z,None];f[b:d,a:z]=f[b:d,a:z]*(1-m)+patch*m
  if only in (None,'beacons'):
   for bc,m in self.beacons:
    age=(t-bc['phase'])%bc['period'];pulse=float(smoothstep(age/.12)*smoothstep((.65-age)/.18))
    f+=m[...,None]*pulse*np.array([84,15,8],np.float32)
  assert np.isfinite(f).all();f=np.uint8(np.rint(np.clip(f,0,255)))
  mask=self.active if only is None else self.layer_masks[only]
  assert np.array_equal(f[~mask],self.base[~mask]),'Protected source pixels changed'
  return f
 def fingerprint(self):
  return {'source_sha256':self.config['source']['sha256'],'config_sha256':digest(self.path),'renderer_sha256':digest(__file__),'dependencies':{n:digest(R/'scripts'/n) for n in ['ambient_effects.py','render_floodplain.py','water_surface.py']},'masks':{k:hashlib.sha256(v.tobytes()).hexdigest() for k,v in self.masks.items()}}

def verify(s,path,count,loop):
 cap=cv2.VideoCapture(str(path));assert cap.get(cv2.CAP_PROP_FPS)==30
 masks={k:cv2.resize(m.astype(np.uint8),(1280,720),interpolation=cv2.INTER_NEAREST) for k,m in {**s.layer_masks,'combined':s.active}.items()}
 first=prev=None;maximum={k:0. for k in masks};hashes=[];i=0
 while True:
  ok,f=cap.read()
  if not ok:break
  assert f.shape==(720,1280,3) and abs(cap.get(cv2.CAP_PROP_POS_MSEC)/1000-i/30)<.0001
  hashes.append(hashlib.sha256(f.tobytes()).hexdigest())
  if first is None:first=f.copy()
  else:
   diff=cv2.absdiff(f,prev)
   for k,m in masks.items():maximum[k]=max(maximum[k],sum(cv2.mean(diff,mask=m)[:3])/3)
  prev=f;i+=1
 cap.release();assert i==count;checks={}
 if loop:
  assert hashes[0]!=hashes[-1]
  diff=cv2.absdiff(prev,first)
  for k,m in masks.items():
   value=sum(cv2.mean(diff,mask=m)[:3])/3;assert value<=maximum[k]*1.1+.01,(k,value,maximum[k])
   checks[k]={'seam_mae':value,'ordinary_max_mae':maximum[k],'pass':True}
 return {'frames':i,'fps':30,'full_decode':True,'sequential_timestamps':True,'encoded_seam':checks},hashes

def samples(s):
 (H/'masks').mkdir(exist_ok=True);overlay=s.base.astype(np.float32)
 for k,m in s.masks.items():cv2.imwrite(str(H/'masks'/f'{k}.png'),np.uint8(np.rint(m*255)))
 for k,col in [('water',[35,140,255]),('sky',[110,240,190]),('lights',[255,65,30]),('room',[255,200,20]),('turbines',[230,30,210])]:
  alpha=s.masks[k][...,None]*.42;overlay=overlay*(1-alpha)+np.float32(col)*alpha
 Image.fromarray(np.uint8(overlay)).save(H/'mask-review.png')
 for t in [0,4.35,8,12,16,19+29/30]:Image.fromarray(s.frame(t)).save(H/f'sample-{t:.3f}s.png')
 report={}
 for name,m in s.layer_masks.items():
  assert np.array_equal(s.frame(0,name),s.frame(s.duration,name))
  values=[]
  for t in [-1/30,0,3,7,12,16]:values.append(float(abs(s.frame(t+1/30,name)[m].astype(float)-s.frame(t,name)[m]).mean()))
  assert values[0]<=max(values[1:])*1.1+.01,(name,values)
  report[name]={'endpoint_exact':True,'seam_mae':values[0],'ordinary_max_sampled':max(values[1:]),'pass':True}
 deviations=np.abs(s.water.speed_deviations)*100
 (H/'analytic-validation.json').write_text(json.dumps({'fingerprint':s.fingerprint(),'layers':report,'water_frequency_quantization_deviation_percent':{'mean':float(deviations.mean()),'max':float(deviations.max())},'protected_source_pixels':'Asserted for every source frame','user_motion_approved':False},indent=2)+'\n',encoding='utf-8')
 print('Source, mask, temporal samples and analytic seams passed',flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['samples','isolated','preview'],required=True);a=p.parse_args();s=Shoreless()
 if a.stage=='samples':samples(s);return
 clips=[]
 if a.stage=='isolated':
  for layer in s.config['isolated_layers']:
   out=H/f'{layer}-isolated-v1-8s.mp4';item=encode(s,out,8,layer);item['validation'],_=verify(s,out,240,False);clips.append(item)
   print(layer,'isolated checks passed',flush=True)
 else:
  out=H/'shoreless-colony-v1-preview-20s.mp4';item=encode(s,out,20);item['validation'],hashes=verify(s,out,600,True);clips.append(item)
  repeat=H/'shoreless-colony-v1-three-loops-60s.mp4';assert not repeat.exists()
  subprocess.run([s.config['ffmpeg'],'-v','error','-n','-stream_loop','2','-i',str(out),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
  validation,repeated=verify(s,repeat,1800,True);assert repeated==hashes*3
  clips.append({'path':repeat.relative_to(R).as_posix(),'sha256':digest(repeat),'validation':validation,'three_repeated_decoded_payloads_identical':True})
  cap=cv2.VideoCapture(str(out));cap.set(cv2.CAP_PROP_POS_MSEC,8000);ok,f=cap.read();cap.release();assert ok;cv2.imwrite(str(H/'decoded-preview-8s.png'),f)
 (H/(a.stage+'-validation.json')).write_text(json.dumps({'fingerprint':s.fingerprint(),'clips':clips,'silent':True,'user_motion_approved':False,'inspection':'Source/mask/temporal/decoded stills; no continuous playback claim'},indent=2)+'\n',encoding='utf-8')
 print(a.stage,'checks passed',flush=True)
if __name__=='__main__':main()
