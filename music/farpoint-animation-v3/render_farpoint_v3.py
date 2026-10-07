"""V3 atmospheric and instrument additions over the reviewed v2 travel."""
from pathlib import Path
import sys,json,hashlib,argparse
import cv2,numpy as np
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(H.parent/'farpoint-animation-v2'))
from render_farpoint_v2 import ForwardFarpoint,Farpoint,byte_image,encode,digest,smoothstep,verify


class FarpointV3(ForwardFarpoint):
 def __init__(self):
  super().__init__()
  self.path=H/'scene-plan-v3.json';self.config=json.loads(self.path.read_text())
  assert digest(H.parent/'farpoint-animation-v2'/'render_farpoint_v2.py')==self.config['parent_v2_renderer_sha256']
  self.prepare_additions()
  self.layer_masks={k:v>0 for k,v in self.masks.items()}
  self.layer_masks['new_atmosphere']=self.layer_masks['lower_cloud']|self.layer_masks['cloud_shadows']
  self.layer_masks['planet_activity']=np.logical_or.reduce([self.layer_masks[k] for k in ['clouds','veil','lower_cloud','cloud_shadows']])
  self.layer_masks['habitation']=np.logical_or.reduce([self.layer_masks[k] for k in ['windows','screen','lamp','instrument_lights']])
  self.active=np.logical_or.reduce(list(self.layer_masks.values()))

 def prepare_additions(self):
  c=self.config['new_atmosphere']['lower_cloud'];a,b,z,d=c['roi'];self.lower_roi=(a,b,z,d)
  plate=self.base[b:d,a:z].astype(np.float32)
  m=self.poly([c['polygon']],8)[b:d,a:z]
  cx,cy,rad=c['protected_crater'];xx=self.x[b:d,a:z];yy=self.y[b:d,a:z]
  m*=smoothstep((np.hypot(xx-cx,yy-cy)-rad)/7)
  red,blue=plate[...,0],plate[...,2]
  gate=smoothstep((blue-c['blue_red_ratio']*red-c['blue_offset'])/25)*smoothstep((red-c['red_floor'])/c['red_range'])*m
  holes=cv2.dilate(np.uint8(gate>.13)*255,np.ones((3,3),np.uint8))
  terrain=cv2.inpaint(plate.astype(np.uint8),holes,6,cv2.INPAINT_TELEA).astype(np.float32)
  cloud=np.maximum(plate-terrain,0)*cv2.GaussianBlur(np.float32(holes>0),(0,0),.65)[...,None]*m[...,None]
  self.lower_clean=plate-cloud;self.lower_original=cloud
  alpha=np.clip(np.max(cloud/np.maximum(245-self.lower_clean,12),axis=2),0,.96)
  self.lower_optical=np.dstack([cloud+alpha[...,None]*self.lower_clean,alpha]).astype(np.float32)
  support=cv2.dilate(np.uint8(alpha>.002),np.ones((81,81),np.uint8))
  self.lower_mask=smoothstep(cv2.distanceTransform(support,cv2.DIST_L2,5)/10)
  self.lower_mask*=smoothstep((np.hypot(xx-cx,yy-cy)-rad)/7)
  self.lower_mask*=smoothstep((xx-a)/8)*smoothstep((z-1-xx)/8)*smoothstep((yy-b)/8)*smoothstep((d-1-yy)/8)
  self.lower_mask[self.lower_mask<.002]=0
  m=np.zeros(self.shape,np.float32);m[b:d,a:z]=self.lower_mask;self.masks['lower_cloud']=m
  pcx,pcy=self.config['planet']['center'];self.lower_rad=np.hypot(xx-pcx,yy-pcy);self.lower_angle=np.arctan2(yy-pcy,xx-pcx)
  sc=self.config['new_atmosphere']['cloud_shadows'];dx,dy=sc['offset']
  self.shadow_x=(self.px-self.planet_roi[0]-dx).astype(np.float32)
  self.shadow_y=(self.py-self.planet_roi[1]-dy).astype(np.float32)
  self.shadow_base=self.shadow_field(self.optical_cloud[...,3])
  self.masks['cloud_shadows']=self.masks['clouds'].copy()
  self.instrument_lights=[];union=np.zeros(self.shape,np.float32)
  rgb=self.base.astype(np.float32)
  for lc in self.config['instrument_lights']:
   core=self.poly(lc['core_polygons'],.8)
   x,y=lc['halo_center'];rx,ry=lc['halo_radius']
   if lc['color']=='blue':color=smoothstep((rgb[...,2]-rgb[...,0]-4)/32)
   elif lc['color']=='pink':color=smoothstep((rgb[...,0]+rgb[...,2]-2*rgb[...,1]-10)/55)
   else:color=smoothstep((rgb[...,0]-rgb[...,2]-8)/42)
   halo=np.exp(-((self.x-x)/rx)**2-((self.y-y)/ry)**2)*color*.58
   halo[(abs(self.x-x)>rx*1.5)|(abs(self.y-y)>ry*1.5)]=0
   mask=np.maximum(core,halo).astype(np.float32);mask[mask<.004]=0
   self.instrument_lights.append((lc,self.crop(mask)));union=np.maximum(union,mask)
  self.masks['instrument_lights']=union

 def shadow_field(self,alpha):
  sigma=self.config['new_atmosphere']['cloud_shadows']['blur_sigma']
  blurred=cv2.GaussianBlur(alpha,(0,0),sigma)
  return cv2.remap(blurred,self.shadow_x,self.shadow_y,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)

 def lower_cloud(self,t):
  c=self.config['new_atmosphere']['lower_cloud'];a,b,z,d=self.lower_roi
  cx,cy=self.config['planet']['center'];theta=self.lower_angle-c['speed_pixels_per_second']*t/self.lower_rad
  mx=(cx+self.lower_rad*np.cos(theta)-a).astype(np.float32);my=(cy+self.lower_rad*np.sin(theta)-b).astype(np.float32)
  moved=cv2.remap(self.lower_optical,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
  return (moved[...,:3]-moved[...,3,None]*self.lower_clean-self.lower_original)*self.lower_mask[...,None]*c['gain']

 def screen(self,f,t):
  super().screen(f,t)
  sc=self.config['screen'];c=self.config['screen_additions'];sw,sh=sc['size'];ink=np.zeros((sh,sw,3),np.float32)
  yy,xx=np.mgrid[:sh,:sw].astype(np.float32)
  cx,cy=c['radar_center'];rad=c['radar_radius'];angle=2*np.pi*t/c['radar_period']-np.pi/2
  polar=np.arctan2(yy-cy,xx-cx);r=np.hypot(xx-cx,yy-cy)
  behind=(angle-polar)%(2*np.pi)
  sweep=np.exp(-behind/.24)*smoothstep((rad-r)/2)*smoothstep(r/3)
  ink+=sweep[...,None]*np.float32([43,133,116])
  route=np.float32(sc['route'])
  for j in range(len(route)-1):
   phase=(t/2.7-j*.52)%5
   amount=float(smoothstep(phase/.22)*smoothstep((1.25-phase)/.3))
   if not amount:continue
   line=np.zeros((sh,sw),np.uint8)
   cv2.line(line,tuple(np.rint(route[j]*256).astype(int)),tuple(np.rint(route[j+1]*256).astype(int)),255,c['route_width'],cv2.LINE_AA,8)
   ink+=(line.astype(np.float32)/255)[...,None]*amount*np.float32(c['route_color'])
  for j,(x,y) in enumerate(c['meter_origins']):
   level=2.6+1.8*np.sin(t*1.05+j*1.8)+.5*np.sin(t*2.1+j)
   for k in range(c['meter_segments']):
    amount=float(smoothstep((level-k)/.7))
    # Small native-panel segments, not a replacement display or waveform.
    ink[y:y+3,x+k*5:x+k*5+3]+=amount*np.float32(c['meter_color'])
  a,b,z,d=self.screen_box;mat=self.screen_matrix.copy();mat[0]-=a*mat[2];mat[1]-=b*mat[2]
  warp=cv2.warpPerspective(ink,mat,(z-a,d-b),flags=cv2.INTER_LINEAR)
  f[b:d,a:z]+=warp*self.screen_mask[...,None]

 def frame_float(self,t,only=None):
  extras=['cloud_shadows','lower_cloud','new_atmosphere','instrument_lights']
  if only in extras:f=self.base.astype(np.float32)
  elif only=='planet_activity':
   f=super().frame_float(t,'clouds')+super().frame_float(t,'veil')-self.base
  else:f=super().frame_float(t,only)
  if only in (None,'cloud_shadows','new_atmosphere','planet_activity'):
   a,b,z,d=self.planet_roi;moved=self.forward_cloud(t);alpha=moved[...,3]
   strength=self.config['new_atmosphere']['cloud_shadows']['strength']
   shadow_delta=self.shadow_field(alpha)-self.shadow_base
   delta=self.clean*(np.exp(-strength*shadow_delta)[...,None]-1)*(1-alpha[...,None])
   f[b:d,a:z]+=delta*self.pm[...,None]
  if only in (None,'lower_cloud','new_atmosphere','planet_activity'):
   a,b,z,d=self.lower_roi;f[b:d,a:z]+=self.lower_cloud(t)
  if only in (None,'instrument_lights','habitation'):
   for lc,mask in self.instrument_lights:self.dim(f,mask,self.amount(t,lc['events']))
  assert np.isfinite(f).all()
  return f

 def fingerprint(self):
  result=super().fingerprint();result['files']['music/farpoint-animation-v3/render_farpoint_v3.py']=digest(__file__)
  result['prototype']={'duration_seconds':12,'seamless':False,'loop_boundary_checked':False}
  return result


def samples(s):
 old=ForwardFarpoint();reg={}
 for layer in ['clouds','veil','windows','lamp']:
  reg[layer]=all(np.array_equal(s.frame(t,layer),old.frame(t,layer)) for t in [0,3,7,8,11.5]);assert reg[layer],layer
 (H/'masks').mkdir(exist_ok=True)
 overlay=s.base.astype(np.float32)
 for layer in ['lower_cloud','cloud_shadows','instrument_lights','screen']:
  m=s.masks[layer];cv2.imwrite(str(H/'masks'/f'{layer}.png'),byte_image(m*255))
  color=[70,200,255] if layer in ['lower_cloud','cloud_shadows'] else [255,100,80]
  a=m[...,None]*.35;overlay=overlay*(1-a)+np.float32(color)*a
 Image.fromarray(byte_image(overlay)).save(H/'new-mask-review.png')
 for t in [0,2.2,3.5,4.65,6,7.25,9.25,11.5]:Image.fromarray(s.frame(t)).save(H/f'sample-{t:05.2f}s.png')
 for name,box,times in [('monitor',(237,471,390,591),[0,2,4,6]),('leds-left',(25,42,239,279),[0,1,2.2,6]),('pink',(344,750,717,824),[0,4.65,7.25,9.85]),('lower-planet',(1260,460,1484,591),[0,4,8,11.5])]:
  ims=[Image.fromarray(s.frame(t)).crop(box) for t in times];w,h=ims[0].size;sheet=Image.new('RGB',(w*2,h*2))
  for i,im in enumerate(ims):sheet.paste(im,((i%2)*w,(i//2)*h))
  sheet.save(H/f'{name}-temporal.png')
 force=s.base.astype(np.float32)
 for lc,m in s.instrument_lights:s.dim(force,m,.9)
 Image.fromarray(byte_image(force)).save(H/'forced-dark-leds.png')
 (H/'sample-validation.json').write_text(json.dumps({'fingerprint':s.fingerprint(),'retained_v2_sampled_exact':reg,'user_feedback':s.config['review'],'scope':'Source protection every frame; regression sampled. No loop or user visual approval claimed.'},indent=2)+'\n')


def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['samples','isolated','preview'],required=True);args=p.parse_args();s=FarpointV3()
 if args.stage=='samples':samples(s);return
 clips=[]
 layers=['new_atmosphere','habitation'] if args.stage=='isolated' else [None]
 seconds=8 if args.stage=='isolated' else 12
 for layer in layers:
  filename=f'{layer}-v3-isolated-8s.mp4' if layer else 'farpoint-v3-detail-preview-12s.mp4'
  item=encode(s,H/filename,seconds,layer,prototype=True);item['validation'],_=verify(s,H/filename,round(seconds*30),False);item['seamless']=False;clips.append(item)
  cap=cv2.VideoCapture(str(H/filename))
  for n in [0,105,210]:
   cap.set(cv2.CAP_PROP_POS_FRAMES,n);ok,f=cap.read();assert ok;cv2.imwrite(str(H/f'decoded-{layer or "combined"}-{n:03d}.png'),f)
  cap.release()
 (H/f'{args.stage}-validation.json').write_text(json.dumps({'fingerprint':s.fingerprint(),'clips':clips,'stage':'forward detail preview, not a seamless loop','user_approved':False,'inspection':'Mask/temporal/decoded stills, not continuous playback'},indent=2)+'\n')
 print(args.stage,'full decode and timestamps passed',flush=True)


if __name__=='__main__':main()
