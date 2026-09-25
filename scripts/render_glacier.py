"""Glacier Sanctuary source-mapped motion study; preserves accepted older renderers."""
import argparse,json,hashlib,subprocess
from pathlib import Path
import cv2,numpy as np,imageio_ffmpeg
from PIL import Image,ImageDraw
from ambient_effects import polygon_mask,blend,vent_density,TAU,event_amount
ROOT=Path(__file__).resolve().parents[1]
class Glacier:
 def __init__(self,path):
  self.config=json.loads(Path(path).read_text());c=self.config
  self.base=np.array(Image.open(ROOT/c['source']['path']).convert('RGB'));self.h,self.w=self.base.shape[:2]
  assert hashlib.sha256((ROOT/c['source']['path']).read_bytes()).hexdigest()==c['source']['sha256']
  self.opening=polygon_mask((self.h,self.w),[c['opening']],feather=9)
  e=c['effects'];self.mist=e['mist'];x0,y0,x1,y1=self.mist['roi'];self.my,self.mx=np.mgrid[y0:y1,x0:x1].astype(np.float32)
  self.mmask=self.opening[y0:y1,x0:x1].copy();self.mmask*=np.sin(np.pi*np.linspace(0,1,y1-y0))[:,None]**.4
  self.water=e['water'];x0,y0,x1,y1=self.water['roi'];self.wy,self.wx=np.mgrid[0:y1-y0,0:x1-x0].astype(np.float32)
  self.wmask=polygon_mask(self.wx.shape,[self.water['polygon']],(x0,y0),12)
  blockers=polygon_mask(self.wx.shape,self.water['ice_blockers'],(x0,y0),1)
  clear=cv2.distanceTransform(np.uint8(blockers==0),cv2.DIST_L2,5);self.wmask*=np.clip((clear-5)/8,0,1)
  self.wbase=self.base[y0:y1,x0:x1].copy()
  self.reflection_surface=None
  if self.water.get('mode')=='reconstructed_surface':
   from water_surface import ReflectionSurface
   self.reflection_surface=ReflectionSurface(self.wbase,self.wmask,self.water['surface'])
  rng_water=np.random.default_rng(613)
  self.glints=[(rng_water.uniform(0,x1-x0),rng_water.uniform(0,y1-y0),rng_water.uniform(*self.water.get('glint_width',[9,28])),rng_water.uniform(*self.water.get('glint_height',[.6,1.4])),rng_water.uniform(0,1)) for _ in range(self.water.get('glint_count',0))]
  self.vent=e['vent'];sx,sy=self.vent['anchor'];self.vroi=[sx-2*self.vent['width'],sy-self.vent['height']-3,sx+2*self.vent['width']+self.vent['drift'],sy+1];x0,y0,x1,y1=self.vroi;self.vy,self.vx=np.mgrid[y0:y1,x0:x1].astype(float)
  rng=np.random.default_rng(e['snow']['seed']);s=e['snow'];n=s['count']
  self.flakes=np.column_stack([rng.uniform(660,1672,n),rng.uniform(160,780,n),rng.uniform(*s['speed_x'],n),rng.uniform(*s['speed_y'],n),rng.uniform(*s['opacity'],n),rng.uniform(*s['radius'],n)])
  self.masks={'atmosphere':self.opening>0,'water':np.zeros((self.h,self.w),bool),'combined':self.opening>0}
  x0,y0,x1,y1=self.water['roi'];self.masks['water'][y0:y1,x0:x1]=self.wmask>0
  self.masks['combined']|=self.masks['water'];x0,y0,x1,y1=self.vroi;self.masks['combined'][y0:y1,x0:x1]=True
  self.lights=[];self.masks['roof_lights']=np.zeros((self.h,self.w),bool);self.masks['roof_lights'][y0:y1,x0:x1]=True
  for light in e.get('lights',[]):
   mask=polygon_mask((self.h,self.w),light['polygons'],feather=1.5)
   self.lights.append((light,mask));self.masks['roof_lights']|=mask>0
  self.masks['combined']|=self.masks['roof_lights']
  self.masks['mist']=np.zeros((self.h,self.w),bool);x0,y0,x1,y1=self.mist['roi'];self.masks['mist'][y0:y1,x0:x1]=self.mmask>0
  self.masks['snow']=self.opening>0
  self.front_snow=c['effects'].get('foreground_snow');self.masks['foreground_snow']=np.zeros((self.h,self.w),bool)
  if self.front_snow:
   snow_rng=np.random.default_rng(self.front_snow['seed']);n=self.front_snow['count'];bottom=self.front_snow['top_y']
   self.front_flakes=np.column_stack([snow_rng.uniform(-80,self.w,n),snow_rng.uniform(bottom,self.h,n),snow_rng.uniform(7,16,n),snow_rng.uniform(25,44,n),snow_rng.uniform(.3,.65,n),snow_rng.uniform(2,4,n)])
   yy=np.arange(self.h)[:,None];self.front_mask=np.broadcast_to(np.minimum(np.clip((yy-bottom)/30,0,1),np.clip((self.h-yy)/20,0,1)),(self.h,self.w))
   self.masks['foreground_snow']=self.front_mask>0;self.masks['combined']|=self.masks['foreground_snow']
  self.halos=[];self.masks['exterior_lights']=np.zeros((self.h,self.w),bool)
  for lamp in e.get('exterior_lights',[])+e.get('light_spill',[]):
   sx,sy=lamp['anchor'];radius=lamp['radius'];rx,ry=radius if isinstance(radius,list) else (radius,radius);roi=[sx-rx*3,sy-ry*3,sx+rx*3+1,sy+ry*3+1]
   x0,y0,x1,y1=roi;yy,xx=np.mgrid[y0:y1,x0:x1].astype(float)
   d=((xx-sx)/rx)**2+((yy-sy)/ry)**2
   halo=np.exp(-d*.5)*np.clip((9-d)/2,0,1)
   if lamp.get('polygon'):halo*=polygon_mask(halo.shape,[lamp['polygon']],(x0,y0),6)
   self.halos.append((lamp,roi,halo));self.masks['exterior_lights'][y0:y1,x0:x1]|=halo>0
  self.masks['combined']|=self.masks['exterior_lights']
  self.tower=c['effects'].get('dome_lantern');self.masks['dome_light']=np.zeros((self.h,self.w),bool)
  if self.tower:
   self.tmask=polygon_mask((self.h,self.w),self.tower['polygons'],feather=1.2)
   sx,sy=self.tower['anchor'];yy,xx=np.mgrid[0:self.h,0:self.w];d=((xx-sx)/self.tower['radius'])**2+((yy-sy)/self.tower['radius'])**2
   self.tglow=np.exp(-d*.5)*np.clip((9-d)/2,0,1)
   self.masks['dome_light']=(self.tmask>0)|(self.tglow>0);self.masks['combined']|=self.masks['dome_light']
 def frame(self,t,layer='combined'):
  f=self.base.copy()
  if layer in ('water','combined'):
   phase=TAU*t/20;x=self.wx;y=self.wy
   mx=x+self.water['amplitude']*np.sin(y*.22-phase*2)*self.wmask
   my=y+self.water.get('vertical_amplitude',.45)*np.sin(x*.04+y*.13-phase)*self.wmask
   if self.water.get('mode')=='directional_reflection':
    # Perspective-compressed wave field; slopes disturb existing photographed reflections.
    depth=np.clip(y/190,0,1);u=x;v=100*np.log1p(y/55)
    nx=np.zeros_like(x);ny=np.zeros_like(y)
    for wave in self.water['waves']:
     angle,wavelength,weight,cycles,offset=wave
     k=TAU/wavelength;dx=np.cos(angle);dy=np.sin(angle)
     q=k*(dx*u+dy*v)-phase*cycles+offset
     nx+=weight*dx*np.cos(q);ny+=weight*dy*np.cos(q)
    mx=x+(1+depth)*nx*self.wmask
    my=y+(.45+.7*depth)*ny*self.wmask
   moved=cv2.remap(self.wbase,mx.astype(np.float32),my.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
   x0,y0,x1,y1=self.water['roi'];a=self.wmask[...,None]
   surface=self.wbase*(1-a)+moved*a
   if self.water.get('mode')=='directional_reflection':
    # Small slope-dependent response, biased toward existing reflected light.
    luminance=self.wbase.astype(float).mean(axis=2)/255
    response=np.clip((luminance-.20)*3,0,1)
    surface+=np.tanh(nx*.6+ny*.4)[...,None]*a*response[...,None]*4*np.array([.85,.94,1])
   if self.water.get('reflection_strength'):
    # Broken, traveling glints distributed over open water, never over ice.
    if self.water.get('broad_reflections'):
     q=y*.19-phase*self.water.get('reflection_speed',12)+.7*np.sin(x*.012)
     waves=1.8*(.5+.5*np.sin(q))**5-.32
     breakup=(.4+.6*(.5+.5*np.sin(x*.036+y*.02-phase)))
    else:
     waves=np.sin(y*.37-phase*4+.7*np.sin(x*.014))+ .45*np.sin(y*.61-phase*6+x*.008)
     breakup=.35+.65*(.5+.5*np.sin(x*.048+y*.017))
    surface+=waves[...,None]*breakup[...,None]*a*self.water['reflection_strength']*np.array([.8,.93,1.0])
   if self.water.get('mode')=='still_glints':
    # Keep the photographed water intact: only sparse small surface glints move.
    density=np.zeros_like(x)
    for sx,sy,width,height,offset in self.glints:
     age=(t/10+offset)%1;cx=sx+self.water['glint_speed']*(age-.5)*10
     density+=np.exp(-.5*(((x-cx)/width)**2+((y-sy)/height)**2))*np.sin(np.pi*age)**2
    alpha=np.clip(density*self.water['glint_opacity'],0,self.water.get('glint_cap',.12))*self.wmask
    surface=self.wbase*(1-alpha[...,None])+np.array(self.water.get('glint_color',[158,181,205]))*alpha[...,None]
   if self.reflection_surface is not None:surface=self.reflection_surface.frame(t)
   f[y0:y1,x0:x1]=np.uint8(np.rint(np.clip(surface,0,255)))
  if layer in ('mist','atmosphere','combined'):
   density=np.zeros_like(self.mx)
   for s in self.mist['sheets']:
    dx=self.mx-s['x']-s['speed']*t;dy=self.my-s['y']-s['slope']*dx
    shape=np.exp(-.5*((dx/s['width'])**2+(dy/s['height'])**2))
    texture=np.clip(.72+.18*np.sin(dx*.035+dy*.12)+.10*np.cos(dx*.065-dy*.17),0,1)
    density+=shape*texture
   blend(f,self.mist['roi'],self.mist['color'],np.clip(density*self.mist['opacity'],0,self.mist.get('max_opacity',.36))*self.mmask)
  if layer in ('snow','atmosphere','combined'):
   snow=np.zeros((self.h,self.w),np.float32)
   for sx,sy,vx,vy,opacity,radius in self.flakes:
    x=int(sx+vx*t);y=int(160+(sy-160+vy*t)%620)
    if 0<=x<self.w and 0<=y<self.h:cv2.circle(snow,(x,y),max(1,round(radius)),float(opacity),-1,lineType=cv2.LINE_AA)
   snow=cv2.GaussianBlur(snow,(0,0),.55)*self.opening
   blend(f,[0,0,self.w,self.h],[222,233,244],snow)
  if layer in ('roof_lights','combined'):blend(f,self.vroi,self.vent['color'],vent_density(self.vx,self.vy,self.vent,TAU*t/20))
  if layer in ('roof_lights','combined'):
   for light,mask in self.lights:
    amount=event_amount(t,20,light['start'],light['hold'],light['transition'])*light['strength']
    a=mask[...,None]*amount
    f=np.uint8(np.rint(np.clip(f*(1-a)+(f*.18+np.array([10,10,12]))*a,0,255)))
  if layer in ('exterior_lights','combined'):
   for lamp,roi,halo in self.halos:
    floor=lamp.get('floor',.45)
    brightness=lamp['strength']*(floor+(1-floor)*(.5+.5*np.sin(TAU*t/lamp['period']+lamp['phase'])))
    dip=0
    if lamp.get('flicker'):
     local=t+lamp['phase']*.6
     dip=max(event_amount(local,20,start,hold,transition) for start,hold,transition in [(1.3,.20,.06),(1.68,.28,.08),(3.8,.65,.14),(6.2,.24,.07)])*lamp.get('flicker_depth',.82)
     brightness*=1-dip
    x0,y0,x1,y1=roi;patch=f[y0:y1,x0:x1].astype(float)
    if lamp.get('flicker') and not isinstance(lamp['radius'],list):
     sx,sy=lamp['anchor'];yy,xx=np.mgrid[y0:y1,x0:x1];core=np.exp(-((xx-sx)**2+(yy-sy)**2)/18)
     patch*=1-core[...,None]*dip*.8
    f[y0:y1,x0:x1]=np.uint8(np.rint(np.clip(patch+halo[...,None]*brightness*np.array([1,.66,.30]),0,255)))
  if self.tower and layer in ('dome_light','combined'):
   off=event_amount(t,20,self.tower['start'],self.tower['hold'],self.tower['transition'])
   a=self.tmask[...,None]*off*.97
   f=np.uint8(np.rint(np.clip(f*(1-a)+(f*.12+np.array([8,10,13]))*a,0,255)))
   glow=(self.tglow*self.tower['strength']+self.tmask*24)*(1-off)
   f=np.uint8(np.rint(np.clip(f.astype(float)+glow[...,None]*np.array([1,.68,.30]),0,255)))
  if self.front_snow and layer in ('foreground_snow','combined'):
   snow=np.zeros((self.h,self.w),np.float32);top=self.front_snow['top_y']
   for sx,sy,vx,vy,opacity,radius in self.front_flakes:
    x=int((sx+vx*t+80)%(self.w+160)-80);y=int(top+(sy-top+vy*t)%(self.h-top))
    cv2.line(snow,(x,y),(x+1,y+3),float(opacity),max(2,round(radius)),lineType=cv2.LINE_AA)
   snow=cv2.GaussianBlur(snow,(0,0),1.1)*self.front_mask
   blend(f,[0,0,self.w,self.h],[224,235,246],snow)
  return f

def main():
 p=argparse.ArgumentParser();p.add_argument('--config',default='creative/glacier-sanctuary/animation/scene-plan-v1.json');p.add_argument('--output',default='creative/glacier-sanctuary/animation/review-v1');p.add_argument('--layers',nargs='+');p.add_argument('--compare-config');a=p.parse_args()
 out=ROOT/a.output;out.mkdir(parents=True,exist_ok=True);b=Glacier(ROOT/a.config);report={'status':'pending','duration_seconds':8,'fps':30,'seamless':False,'source':b.config['source'],'config_sha256':hashlib.sha256((ROOT/a.config).read_bytes()).hexdigest(),'renderer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'water_surface_sha256':hashlib.sha256((ROOT/'scripts/water_surface.py').read_bytes()).hexdigest() if (ROOT/'scripts/water_surface.py').exists() else None,'clips':[],'inspection':'Sampled stills and decoded-frame checks; user playback review pending'}
 overlay=b.base.copy();overlay[b.masks['atmosphere']]=np.uint8(overlay[b.masks['atmosphere']]*.65+np.array([65,120,190])*.35);Image.fromarray(overlay).save(out/'atmosphere-mask.jpg')
 Image.fromarray(np.uint8(b.masks['water'])*255).save(out/'water-mask.png')
 for layer in (a.layers or b.config.get('review_layers',['atmosphere','water','combined'])):
  dst=out/(layer+'.mp4');assert not dst.exists(),dst
  compare=Glacier(ROOT/a.compare_config) if a.compare_config else None
  size='1280x1440' if compare else '1280x720'
  cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-n','-f','rawvideo','-pix_fmt','rgb24','-s',size,'-r','30','-i','-','-an','-c:v','libx264','-preset','veryfast','-qp','0','-pix_fmt','yuv420p','-movflags','+faststart',str(dst)]
  proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
  try:
   for i in range(240):
    f=b.frame(i/30,layer);assert np.array_equal(f[~b.masks[layer]],b.base[~b.masks[layer]])
    frame=cv2.resize(f,(1280,720),interpolation=cv2.INTER_AREA)
    if compare:
     old=cv2.resize(compare.frame(i/30,layer),(1280,720),interpolation=cv2.INTER_AREA)
     frame=np.vstack([old,frame])
    proc.stdin.write(frame.tobytes())
  finally:proc.stdin.close()
  assert proc.wait()==0
  cap=cv2.VideoCapture(str(dst));count=0
  while True:
   ok,f=cap.read()
   if not ok:break
   assert f.shape[:2]==((1440,1280) if compare else (720,1280));count+=1
  cap.release();assert count==240
  report['clips'].append({'layer':layer,'path':dst.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'decoded_frames':count,'outside_mask_static':True});print('Finished '+layer,flush=True)
 sheet=Image.new('RGB',(1280,720))
 for i,t in enumerate([0,2,4,7.9667]):
  im=Image.fromarray(b.frame(t)).resize((640,360));ImageDraw.Draw(im).text((12,12),str(t)+'s',fill='white');sheet.paste(im,((i%2)*640,(i//2)*360))
 sheet.save(out/'temporal-samples.jpg');(out/'review.json').write_text(json.dumps(report,indent=2))
if __name__=='__main__':main()
