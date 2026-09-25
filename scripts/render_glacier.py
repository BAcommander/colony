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
 def frame(self,t,layer='combined'):
  f=self.base.copy()
  if layer in ('water','combined'):
   phase=TAU*t/20;x=self.wx;y=self.wy
   mx=x+self.water['amplitude']*np.sin(y*.22-phase*2)*self.wmask
   my=y+self.water.get('vertical_amplitude',.45)*np.sin(x*.04+y*.13-phase)*self.wmask
   moved=cv2.remap(self.wbase,mx.astype(np.float32),my.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
   x0,y0,x1,y1=self.water['roi'];a=self.wmask[...,None]
   surface=self.wbase*(1-a)+moved*a
   if self.water.get('reflection_strength'):
    # Broken, traveling glints distributed over open water, never over ice.
    waves=np.sin(y*.37-phase*4+.7*np.sin(x*.014))+ .45*np.sin(y*.61-phase*6+x*.008)
    breakup=.35+.65*(.5+.5*np.sin(x*.048+y*.017))
    surface+=waves[...,None]*breakup[...,None]*a*self.water['reflection_strength']*np.array([.8,.93,1.0])
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
  return f

def main():
 p=argparse.ArgumentParser();p.add_argument('--config',default='creative/glacier-sanctuary/animation/scene-plan-v1.json');p.add_argument('--output',default='creative/glacier-sanctuary/animation/review-v1');a=p.parse_args()
 out=ROOT/a.output;out.mkdir(parents=True,exist_ok=True);b=Glacier(ROOT/a.config);report={'status':'pending','duration_seconds':8,'fps':30,'seamless':False,'source':b.config['source'],'config_sha256':hashlib.sha256((ROOT/a.config).read_bytes()).hexdigest(),'renderer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'clips':[],'inspection':'Sampled stills and decoded-frame checks; user playback review pending'}
 overlay=b.base.copy();overlay[b.masks['atmosphere']]=np.uint8(overlay[b.masks['atmosphere']]*.65+np.array([65,120,190])*.35);Image.fromarray(overlay).save(out/'atmosphere-mask.jpg')
 Image.fromarray(np.uint8(b.masks['water'])*255).save(out/'water-mask.png')
 for layer in b.config.get('review_layers',['atmosphere','water','combined']):
  dst=out/(layer+'.mp4');assert not dst.exists(),dst
  cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-n','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r','30','-i','-','-an','-c:v','libx264','-preset','veryfast','-qp','0','-pix_fmt','yuv420p','-movflags','+faststart',str(dst)]
  proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
  try:
   for i in range(240):
    f=b.frame(i/30,layer);assert np.array_equal(f[~b.masks[layer]],b.base[~b.masks[layer]])
    proc.stdin.write(cv2.resize(f,(1280,720),interpolation=cv2.INTER_AREA).tobytes())
  finally:proc.stdin.close()
  assert proc.wait()==0
  cap=cv2.VideoCapture(str(dst));count=0
  while True:
   ok,f=cap.read()
   if not ok:break
   assert f.shape[:2]==(720,1280);count+=1
  cap.release();assert count==240
  report['clips'].append({'layer':layer,'path':dst.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'decoded_frames':count,'outside_mask_static':True});print('Finished '+layer,flush=True)
 sheet=Image.new('RGB',(1280,720))
 for i,t in enumerate([0,2,4,7.9667]):
  im=Image.fromarray(b.frame(t)).resize((640,360));ImageDraw.Draw(im).text((12,12),str(t)+'s',fill='white');sheet.paste(im,((i%2)*640,(i//2)*360))
 sheet.save(out/'temporal-samples.jpg');(out/'review.json').write_text(json.dumps(report,indent=2))
if __name__=='__main__':main()
