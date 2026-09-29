"""Saltline source-bound motion trial; immutable source, independent masked layers."""
from pathlib import Path
import sys, json, hashlib, argparse
import cv2, numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from ambient_effects import smoothstep, event_amount
from render_floodplain import encode, verify
from dust_transport import DustTransport
cv2.setNumThreads(4)
HERE=Path(__file__).resolve().parent
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

class Saltline:
 def __init__(self,config='scene-plan-v1.json'):
  self.path=HERE/config
  self.config=json.loads(self.path.read_text()); c=self.config
  source=ROOT/c['source']['path']; assert digest(source)==c['source']['sha256']
  self.base=np.array(Image.open(source).convert('RGB')); self.h,self.w=self.base.shape[:2]
  assert [self.w,self.h]==c['source']['dimensions']; self.duration=c['duration']
  self.masks={}; self.rois={}; self.grids={}
  prep=ROOT/'final/05-saltline-receiver/animation-prep-v1/masks'
  for name in c.get('enabled_motion',['sky','far_dust','near_dust']):
   binary=cv2.imread(str(prep/(name+'.png')),0)>0
   if name in c.get('mask_geometry',{}):
    geometry=c['mask_geometry'][name]; binary=np.zeros((self.h,self.w),np.uint8)
    for pts in geometry['include']: cv2.fillPoly(binary,[np.array(pts,np.int32)],1)
    for pts in geometry['exclude']: cv2.fillPoly(binary,[np.array(pts,np.int32)],0)
    binary=binary>0
   # The draft sky boundary intersected the fine left-dish feed tip.
   # Keep the entire lower-sky equipment region fixed in this transport trial.
   if name=='sky': binary[275:]=False
   # Feather strictly inward: no motion enters solid geometry.
   distance=cv2.distanceTransform(binary.astype(np.uint8),cv2.DIST_L2,5)
   m=smoothstep(np.maximum(distance-2,0)/c['feather'][name]).astype(np.float32)
   self.masks[name]=m
   yy,xx=np.where(m>0); roi=(int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1))
   self.rois[name]=roi; x0,y0,x1,y1=roi
   y,x=np.mgrid[y0:y1,x0:x1].astype(np.float32); self.grids[name]=(x,y)
  self.lights=[]
  if c.get('lights'):
   light_union=np.zeros((self.h,self.w),np.float32)
   for light in c['lights']:
    full=np.zeros((self.h,self.w),np.uint8)
    for pts in light.get('polygons',[]):cv2.fillPoly(full,[np.array(pts,np.int32)],255)
    if 'ellipse' in light:
     sx,sy,rx,ry=light['ellipse'];cv2.ellipse(full,(sx,sy),(rx,ry),0,0,360,255,-1)
    yy,xx=np.where(full>0);pad=light.get('spill_pad',8)
    x0=max(0,int(xx.min())-pad);x1=min(self.w,int(xx.max())+pad+1);y0=max(0,int(yy.min())-pad);y1=min(self.h,int(yy.max())+pad+1)
    aperture=full[y0:y1,x0:x1].astype(np.float32)/255
    soft=smoothstep(cv2.distanceTransform(np.uint8(aperture>0),cv2.DIST_L2,5)/1.2)
    spill=cv2.GaussianBlur(aperture,(0,0),light.get('spill_sigma',2))*light.get('spill_strength',.10)
    mask=np.clip(soft+spill,0,1);self.lights.append((light,(x0,y0,x1,y1),mask))
    light_union[y0:y1,x0:x1]=np.maximum(light_union[y0:y1,x0:x1],mask)
   self.masks['lights']=light_union
  if c.get('sunlight'):
   full=np.zeros((self.h,self.w),np.uint8)
   for pts in c['sunlight']['polygons']:cv2.fillPoly(full,[np.array(pts,np.int32)],1)
   m=smoothstep(cv2.distanceTransform(full,cv2.DIST_L2,5)/c['sunlight']['feather']).astype(np.float32)
   self.masks['sunlight']=m;yy,xx=np.where(m>0)
   x0=int(xx.min());x1=int(xx.max()+1);y0=int(yy.min());y1=int(yy.max()+1)
   self.sun_roi=(x0,y0,x1,y1);self.sun_y,self.sun_x=np.mgrid[y0:y1,x0:x1].astype(np.float32)
  self.layer_masks={k:v>0 for k,v in self.masks.items()}; self.active=np.logical_or.reduce(list(self.layer_masks.values()))
  x0,y0,x1,y1=self.rois['sky']; self.clean=self.base[y0:y1,x0:x1].copy()
  invalid=(self.masks['sky'][y0:y1,x0:x1]==0).astype(np.uint8)*255
  cv2.ellipse(invalid,(62-x0,316-y0),(52,53),0,0,360,255,-1)
  self.clean=cv2.inpaint(self.clean,invalid,7,cv2.INPAINT_TELEA).astype(np.float32)
  x,y=self.grids['sky']; self.cx=x-x0; self.cy=y-y0
  self.dust={name:DustTransport(*self.grids[name],c[name],self.duration) for name in ('far_dust','near_dust') if name in self.grids and c[name].get('method')=='textured_gusts'}

 def frame(self,t,only=None,prototype=False):
  t=float(t)%self.duration; f=self.base.astype(np.float32)
  for name in self.masks:
   if name in ('lights','sunlight'):continue
   if only not in (None,name): continue
   x0,y0,x1,y1=self.rois[name]; x,y=self.grids[name]; m=self.masks[name][y0:y1,x0:x1]
   if name=='sky':
    speed=self.config['sky_speed']
    if prototype:
     moving=cv2.remap(self.clean,self.cx-speed*t,self.cy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
    else:
     moving=np.zeros_like(self.clean)
     offset=y/500+x/2200
     for shift in (0,.5):
      age=(t/self.duration+offset+shift)%1; weight=np.sin(np.pi*age)**2
      layer=cv2.remap(self.clean,(self.cx-speed*self.duration*(age-.5)).astype(np.float32),self.cy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
      moving+=layer*weight[...,None]
    f[y0:y1,x0:x1]+=m[...,None]*(moving-self.clean)
   else:
    if name in self.dust:
     alpha,color=self.dust[name].density(t,prototype);alpha*=m
     patch=f[y0:y1,x0:x1];f[y0:y1,x0:x1]=patch*(1-alpha[...,None])+color*alpha[...,None]
     continue
    c=self.config[name]; density=np.zeros_like(x)
    for s in c['sheets']:
     age=(t/c['lifetime']+s['phase'])%1
     elapsed=t if prototype else (age-.5)*c['lifetime']
     envelope=1 if prototype else np.sin(np.pi*age)**2
     dx=x-(s['x']+c['speed']*elapsed)
     bend=s.get('bend',0)*np.sin(dx*.028+s['phase']*6.28)
     dy=y-s['y']-s['slope']*dx-bend
     body=np.exp(-.5*((dx/s['width'])**2+(dy/s['height'])**2))
     structure=np.clip(.7+.2*np.sin(dx*.045+dy*.15)+.1*np.cos(dx*.087-dy*.23),0,1)
     density+=body*structure*envelope*s['strength']
    alpha=m*np.clip(density*c['opacity'],0,c['max_opacity'])
    patch=f[y0:y1,x0:x1]; f[y0:y1,x0:x1]=patch*(1-alpha[...,None])+np.array(c['color'])*alpha[...,None]
  if only in (None,'lights'):
   for light,(x0,y0,x1,y1),mask in self.lights:
    amount=max((event_amount(t,self.duration,e['start'],e['hold'],e['transition'])*e.get('depth',1) for e in light['events']),default=0)
    patch=f[y0:y1,x0:x1];dark=patch*light['floor']+np.array(light.get('dark_offset',[4,3,2]))
    alpha=mask*amount;f[y0:y1,x0:x1]=patch*(1-alpha[...,None])+dark*alpha[...,None]
  if 'sunlight' in self.masks and only in (None,'sunlight'):
   c=self.config['sunlight'];x0,y0,x1,y1=self.sun_roi
   # A single passing cloud shadow on sunlit dry crust, not changing global exposure.
   center=c['start_x']+c['speed']*t
   field=np.exp(-.5*(((self.sun_x-center)/c['width'])**2+((self.sun_y-c['center_y'])/c['height'])**2))
   alpha=self.masks['sunlight'][y0:y1,x0:x1]*field*c['attenuation']
   f[y0:y1,x0:x1]*=1-alpha[...,None]*np.array([.9,1,1.03])
  f=np.uint8(np.rint(np.clip(f,0,255))); mask=self.active if only is None else self.layer_masks[only]
  assert np.array_equal(f[~mask],self.base[~mask]),'Protected pixels changed'
  return f

def initialize():
 prep=json.loads((ROOT/'final/05-saltline-receiver/animation-prep-v1/scene-plan.json').read_text())
 c={'scene_name':'Saltline Receiver','version':'v1','source':prep['source'],'duration':20,'fps':30,'preview_size':[1280,720],'final_size':[3840,2160],'output_dir':HERE.relative_to(ROOT).as_posix(),'ffmpeg':'C:/Program Files/ShareX/ffmpeg.exe','sky_speed':2.5,'feather':{'sky':10,'far_dust':8,'near_dust':8},'source_selection':{'feedback':'yes lets animate, whats the plan?','date':'2026-09-29','scope':'v2 source selected for animation; motion not reviewed'},'status':'Principal motion prototypes; lights deferred until transport review','far_dust':{'speed':8,'lifetime':10,'opacity':.10,'max_opacity':.13,'color':[229,186,153],'sheets':[{'x':845,'y':432,'width':160,'height':9,'slope':.008,'phase':0,'strength':1},{'x':970,'y':439,'width':130,'height':7,'slope':-.015,'phase':.5,'strength':.7}]},'near_dust':{'speed':14,'lifetime':10,'opacity':.12,'max_opacity':.16,'color':[222,167,128],'sheets':[{'x':760,'y':514,'width':90,'height':11,'slope':-.035,'phase':0,'strength':1},{'x':818,'y':550,'width':90,'height':9,'slope':.03,'phase':.5,'strength':.8}]}}
 assert not (HERE/'scene-plan-v1.json').exists()
 (HERE/'scene-plan-v1.json').write_text(json.dumps(c,indent=2)+'\n')

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['init','samples','isolated','combined','preview'],required=True);p.add_argument('--config',default='scene-plan-v1.json');p.add_argument('--layers',nargs='+');a=p.parse_args()
 if a.stage=='init':initialize();return
 scene=Saltline(a.config); items=[]; version=scene.config.get('trial_version','v1b')
 if a.stage=='samples':
  for t in (0,2,4,6):Image.fromarray(scene.frame(t,prototype=True)).save(HERE/('prototype-'+version+'-sample-'+str(t)+'s.png'))
  overlay=scene.base.copy().astype(float)
  for name,col in [('far_dust',[60,170,255]),('near_dust',[255,170,50])]:
   if name not in scene.masks:continue
   m=scene.masks[name][...,None]*.5;overlay=overlay*(1-m)+np.array(col)*m
  Image.fromarray(np.uint8(overlay)).save(HERE/(version+'-mask-review.png'))
  return
 if a.stage=='isolated':
  for name in (a.layers or list(scene.masks)):
   item=encode(scene,HERE/(name+'-transport-'+version+'-8s.mp4'),8,name,True)
   item['validation']=verify(scene,ROOT/item['path'],240);items.append(item)
  for t in (0,4,7): Image.fromarray(scene.frame(t,prototype=True)).save(HERE/('prototype-'+version+'-sample-'+str(t)+'s.png'))
 elif a.stage=='combined':
  seconds=scene.config.get('trial_seconds',8)
  item=encode(scene,HERE/('saltline-'+version+'-combined-'+str(seconds)+'s.mp4'),seconds,None,True)
  item['validation']=verify(scene,ROOT/item['path'],round(seconds*30));items.append(item)
 else:
  item=encode(scene,HERE/'saltline-v1-preview-20s.mp4',20)
  item['validation']=verify(scene,ROOT/item['path'],600,True);items.append(item)
 report={'source_sha256':scene.config['source']['sha256'],'config_sha256':digest(scene.path),'renderer_sha256':digest(__file__),'dependencies_sha256':{'dust_transport.py':digest(HERE/'dust_transport.py'),'encoder':digest(ROOT/'scripts/render_floodplain.py'),'ambient_effects':digest(ROOT/'scripts/ambient_effects.py')},'draft_mask_sha256':{n:digest(ROOT/'final/05-saltline-receiver/animation-prep-v1/masks'/(n+'.png')) for n in scene.masks if n in ('sky','far_dust','near_dust')},'clips':items,'user_motion_approval':False,'inspection':'Full decode and per-source-frame protected-pixel assertions; normal-speed visual review pending','prototype_not_loop':a.stage in ('isolated','combined'),'supporting_lights':'implemented; visual review pending' if scene.lights else 'not implemented in principal-layer trial','sunlight':'localized passing cloud shadow; visual review pending' if 'sunlight' in scene.masks else 'unchanged'}
 report['mask_geometry']=scene.config.get('mask_geometry',{})
 report['previous_feedback']=scene.config.get('previous_feedback')
 report['effective_masks_sha256']={n:hashlib.sha256(m.tobytes()).hexdigest() for n,m in scene.masks.items()}
 (HERE/(a.stage+'-'+version+'-validation.json')).write_text(json.dumps(report,indent=2)+'\n')
 print('Saltline '+a.stage+' complete',flush=True)
if __name__=='__main__':main()
