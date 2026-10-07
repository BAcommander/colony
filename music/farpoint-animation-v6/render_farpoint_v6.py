"""Farpoint v6: confined generated reflection repair, drifting source stars, cabinet LEDs."""
from pathlib import Path
import sys,json,hashlib,argparse,subprocess
import cv2,numpy as np
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(H.parent/'farpoint-animation-v5'))
from render_farpoint_v5 import FarpointV5,Farpoint,byte_image,encode,digest,smoothstep,verify
def save(n,d):(H/n).write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
PROMPT="Precise object removal edit. This is a narrow crop of a space-station observation window. Remove the three floating horizontal amber/white light streaks in the middle of the dark glass: one upper bright dash and the two lower smaller dashes. Remove their local amber reflected haze too, restoring quiet dark nearly black glass/space with sparse tiny background specks matching the surrounding image. Keep the left silver window/bezel edge, curved bottom sill, and lower-right exterior hardware completely unchanged in position, shape, lighting and material. Keep framing and aspect ratio exactly. Do not add any light, star, object, symbol, colour glow, text or decoration. The result is a clean local background repair patch for an existing animation, not a redesign."

def assets():
 old=R/'final/10-nightward-station/artwork-v3-close-world-leds.png'
 source=np.array(Image.open(old).convert('RGB'));x0,y0,x1,y1=397,471,466,581
 patch=np.array(Image.open(H/'reflection-cleanup-generated.png').convert('RGB').resize((x1-x0,y1-y0),Image.Resampling.LANCZOS))
 yy,xx=np.mgrid[y0:y1,x0:x1].astype(np.float32)
 # Keep all geometry outside the bar/haze region byte-identical, including the sill.
 m=np.zeros(xx.shape,np.float32)
 for x,y,rx,ry in [(433,497,22,12),(434,551,20,10),(434,560,20,10)]:
  r=np.sqrt(((xx-x)/rx)**2+((yy-y)/ry)**2)
  m=np.maximum(m,1-smoothstep((r-.66)/.34))
 m[(xx<410)|(xx>456)|(yy>573)]=0
 target_crop=source[y0:y1,x0:x1].copy()
 matched=cv2.seamlessClone(patch,target_crop,np.uint8(m>0)*255,((x1-x0)//2,(y1-y0)//2),cv2.NORMAL_CLONE)
 out=source.copy();out[y0:y1,x0:x1]=byte_image(target_crop*(1-m[...,None])+matched*m[...,None])
 target=R/'final/10-nightward-station/artwork-v4b-reflection-cleanup.png';assert not target.exists()
 Image.fromarray(out).save(target)
 full=np.zeros(source.shape[:2],np.float32);full[y0:y1,x0:x1]=m
 np.save(H/'reflection-cleanup-mask.npy',full);cv2.imwrite(str(H/'reflection-cleanup-mask.png'),byte_image(full*255))
 assert np.array_equal(source[full==0],out[full==0])
 (H/'reflection-cleanup-prompt.txt').write_text(PROMPT+'\n',encoding='utf-8')
 save('asset-provenance.json',{'method':'Built-in image_gen edit; Poisson colour/gradient matching into surrounding glass, then source-coordinate feathered compositing in the user-authorized local pipeline','prompt':'reflection-cleanup-prompt.txt','generated_patch':'reflection-cleanup-generated.png','generated_patch_sha256':digest(H/'reflection-cleanup-generated.png'),'crop_source_rectangle':[x0,y0,x1,y1],'original_source':old.relative_to(R).as_posix(),'original_sha256':digest(old),'clean_source':target.relative_to(R).as_posix(),'clean_sha256':digest(target),'source_size':[1672,941],'outside_cleanup_mask_byte_identical':True,'scope':'Floating bars and their nearby haze only; lamp and desk spill unchanged','approval':'User authorized removal; new composite preview still needs review','initial_fix':'Direct blending produced dark oval patches. Gradient matching corrects that local mismatch; initial candidate preserved.'})
 c=json.loads((H.parent/'farpoint-animation-v5/scene-plan-v5.json').read_text(encoding='utf-8'))
 c['version']='v6';c['status']='New positional star motion, bar cleanup and cabinet LEDs; review pending'
 c['original_source']=c['source'].copy();c['source']={'path':target.relative_to(R).as_posix(),'sha256':digest(target),'dimensions':[1672,941]}
 c['parent_v5_renderer_sha256']=digest(H.parent/'farpoint-animation-v5/render_farpoint_v5.py')
 c['stars']['brightness_range']=[1,1]
 c['drifting_stars']={'roi':[596,32,1607,577],'polygon':[[600,54],[1490,33],[1566,39],[1604,79],[1604,576],[599,574]],'planet_margin':19,'speed_xy':[1.25,-.13],'lifetime':60,'fade':5,'seed':606,'minimum_peak':15,'maximum_blob_area':26,'maximum_blob_width':9,'maximum_blob_height':9,'method':'Extract existing compact star sprites over stationary sky background; common forward velocity with independently phased zero-opacity renewals. Cinematic loop approximation, not physical celestial mechanics.'}
 c['cabinet']={'quad':[[1460,855],[1528,863],[1528,877],[1460,869]],'lights':[{'name':'power','center':[1472,864],'color':[58,175,215],'steady':True,'events':[]},{'name':'activity','center':[1492,866.5],'color':[90,200,141],'steady':False,'events':[[5,1.2],[12.5,.65],[13.6,.7],[28.2,1.4],[43.3,.7],[44.4,.8],[53.5,1.2]]},{'name':'status','center':[1512,869],'color':[240,147,48],'steady':False,'events':[[18,3.2],[36.5,4.1],[56.2,2.4]]}]}
 c['review']={'approved':False,'feedback':'Remove floating bars; star brightness changes still invisible, rethink movement; add bottom-right LEDs','prior_cloud_acceptance':'No new verdict; preserve v5 planet exactly'}
 save('scene-plan-v6.json',c)

class FarpointV6(FarpointV5):
 def __init__(self):
  super().__init__()
  self.path=H/'scene-plan-v6.json';self.config=json.loads(self.path.read_text(encoding='utf-8'))
  assert digest(H.parent/'farpoint-animation-v5/render_farpoint_v5.py')==self.config['parent_v5_renderer_sha256']
  p=R/self.config['source']['path'];assert digest(p)==self.config['source']['sha256']
  self.base=np.array(Image.open(p).convert('RGB'));self.masks.pop('reflections')
  box,mask=self.reflections;self.reflections=(box,np.zeros_like(mask))
  self.prepare_star_drift();self.prepare_cabinet()
  self.layer_masks={k:v>0 for k,v in self.masks.items()}
  self.layer_masks['planet_activity']=np.logical_or.reduce([self.layer_masks[k] for k in ['clouds','veil','lower_cloud','cloud_shadows','lightning','expanded_weather']])
  self.layer_masks['habitation']=np.logical_or.reduce([self.layer_masks[k] for k in ['windows','screen','lamp','instrument_lights','cabinet_leds']])
  self.active=np.logical_or.reduce(list(self.layer_masks.values()))

 def prepare_star_drift(self):
  c=self.config['drifting_stars'];a,b,z,d=c['roi'];self.star_roi=(a,b,z,d)
  xx=self.x[b:d,a:z];yy=self.y[b:d,a:z];cx,cy=self.config['planet']['center']
  sky=self.poly([c['polygon']],8)[b:d,a:z]
  sky*=smoothstep((np.hypot(xx-cx,yy-cy)-self.config['planet']['radius']-c['planet_margin'])/14)
  sky[sky<.002]=0;self.sky_mask=sky
  source=self.base[b:d,a:z];median=cv2.medianBlur(source,9)
  residual=np.maximum(source.astype(np.float32)-median.astype(np.float32),0)
  peaks=(residual.max(2)>c['minimum_peak'])&(sky>.98)
  count,labels,stats,centers=cv2.connectedComponentsWithStats(np.uint8(peaks),8)
  chosen=np.zeros(peaks.shape,np.uint8)
  for i in range(1,count):
   x,y,w,h,area=stats[i]
   if area<=c['maximum_blob_area'] and w<=c['maximum_blob_width'] and h<=c['maximum_blob_height']:
    chosen[labels==i]=255
  holes=cv2.dilate(chosen,np.ones((5,5),np.uint8))
  holes[sky<.99]=0
  self.clean_sky=cv2.inpaint(source,holes,3,cv2.INPAINT_TELEA).astype(np.float32)
  delta=np.maximum(source.astype(np.float32)-self.clean_sky,0)
  count,labels,stats,centers=cv2.connectedComponentsWithStats(holes,8)
  rng=np.random.default_rng(c['seed']);self.star_sprites=[]
  for i in range(1,count):
   x,y,w,h,area=map(int,stats[i])
   sprite=delta[y:y+h,x:x+w].copy()*(labels[y:y+h,x:x+w]==i)[...,None]
   if sprite.max()<c['minimum_peak']:continue
   phase=float(rng.uniform(0,self.duration));self.star_sprites.append((x,y,sprite,phase))
  self.star_removal=self.clean_sky-source.astype(np.float32)
  m=np.zeros(self.shape,np.float32);m[b:d,a:z]=sky;self.masks['stars']=m
  assert len(self.star_sprites)>60,len(self.star_sprites)

 def star_field(self,t):
  c=self.config['drifting_stars'];a,b,z,d=self.star_roi;field=np.zeros_like(self.clean_sky)
  vx,vy=c['speed_xy'];life=c['lifetime']
  for x,y,sprite,phase in self.star_sprites:
   age=(t+phase+life/2)%life-life/2;fade=float(smoothstep((life/2-abs(age))/c['fade']))
   if fade==0:continue
   tx=x+vx*age;ty=y+vy*age;ix=int(np.floor(tx));iy=int(np.floor(ty));h,w=sprite.shape[:2]
   shifted=cv2.warpAffine(sprite,np.float32([[1,0,tx-ix+1],[0,1,ty-iy+1]]),(w+3,h+3),flags=cv2.INTER_LINEAR)
   xa,ya=max(0,ix-1),max(0,iy-1);xb,yb=min(z-a,ix+w+2),min(d-b,iy+h+2)
   if xb>xa and yb>ya:field[ya:yb,xa:xb]+=shifted[ya-(iy-1):yb-(iy-1),xa-(ix-1):xb-(ix-1)]*fade
  return self.star_removal+field*self.sky_mask[...,None]

 def prepare_cabinet(self):
  c=self.config['cabinet'];self.cabinet_housing=self.poly([c['quad']],.6)
  edge=self.cabinet_housing-cv2.erode(self.cabinet_housing,np.ones((3,3),np.uint8))
  self.cabinet_edge=edge
  union=self.cabinet_housing.copy();self.cabinet_lights=[]
  for lc in c['lights']:
   x,y=lc['center'];r=np.hypot(self.x-x,(self.y-y)*1.1)
   core=1-smoothstep((r-1.3)/1.3)
   halo=np.exp(-.5*(((self.x-x)/5.2)**2+((self.y-y)/4.3)**2))*.20
   halo[halo<.004]=0
   self.cabinet_lights.append((lc,self.crop(np.maximum(core,halo))))
   union=np.maximum(union,np.maximum(core,halo))
  self.masks['cabinet_leds']=union

 def cabinet(self,f,t):
  m=self.cabinet_housing[...,None]
  f[:]=f*(1-m)+np.float32([17,17,17])*m
  f+=self.cabinet_edge[...,None]*np.float32([21,19,17])
  for lc,((a,b,z,d),mask) in self.cabinet_lights:
   events=[{'start':start,'hold':hold,'transition':.18,'depth':1} for start,hold in lc['events']]
   level=.82 if lc['steady'] else .14+.86*self.amount(t,events)
   f[b:d,a:z]+=mask[...,None]*np.float32(lc['color'])*level

 def frame_float(self,t,only=None):
  t=float(t)%self.duration;f=super().frame_float(t,only)
  # V5 brightness cycling is neutralized in config. Replace extracted original
  # points by translated native-profile sprites over the stationary sky.
  if only in (None,'stars'):
   a,b,z,d=self.star_roi;f[b:d,a:z]+=self.star_field(t)
  if only in (None,'cabinet_leds','habitation'):self.cabinet(f,t)
  assert np.isfinite(f).all();return f

 def fingerprint(self):
  fp=super().fingerprint()
  for p in [Path(__file__),H.parent/'farpoint-animation-v5/scene-plan-v5.json',H/'reflection-cleanup-generated.png',H/'reflection-cleanup-mask.npy']:
   fp['files'][p.relative_to(R).as_posix()]=digest(p)
  return fp

def samples(s):
 (H/'masks').mkdir(exist_ok=True)
 for k,m in s.masks.items():cv2.imwrite(str(H/'masks'/f'{k}.png'),byte_image(m*255))
 for t in [0,5,8,13,20,30,40,50,57,59+29/30]:
  Image.fromarray(cv2.resize(s.frame(t),(1280,720),interpolation=cv2.INTER_AREA)).save(H/f'sample-{t:06.2f}s.png')
 old=FarpointV5();retained={}
 for k in ['clouds','veil','lower_cloud','cloud_shadows','lightning','expanded_weather','screen','lamp','instrument_lights','windows']:
  m=old.layer_masks[k]
  retained[k]=all(np.array_equal(s.frame(t,k)[m],old.frame(t,k)[m]) for t in [0,7,20,40,54]);assert retained[k],k
 checks={}
 for k,m in s.layer_masks.items():
  assert np.array_equal(s.frame(0,k),s.frame(60,k)),k
  vals=[]
  for t in [-1/30,0,5,8,13,20,30,40,50,57]:
   vals.append(float(abs(s.frame(t+1/30,k)[m].astype(float)-s.frame(t,k)[m]).mean()))
  assert vals[0]<=max(vals[1:])*1.1+.01,(k,vals)
  checks[k]={'seam_mae':vals[0],'ordinary_max':max(vals[1:]),'pass':True}
 save('analytic-validation.json',{'fingerprint':s.fingerprint(),'retained_v5_regions_exact':retained,'layer_checks':checks,'star_sprite_count':len(s.star_sprites),'star_travel_preview_pixels_per_8_seconds':[v*8*1280/1672 for v in s.config['drifting_stars']['speed_xy']],'source_protection':'Asserted every frame relative to narrowly corrected clean plate','visual_approval':False})
 print('Samples, source protection, layer retention and seams passed',flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['assets','samples','isolated','preview'],required=True);args=p.parse_args()
 if args.stage=='assets':assets();return
 s=FarpointV6()
 if args.stage=='samples':samples(s);return
 clips=[]
 if args.stage=='isolated':
  for layer in ['stars','cabinet_leds']:
   out=H/f'{layer}-v6-isolated-10s.mp4';item=encode(s,out,10,layer,True);item['validation'],_=verify(s,out,300,False);clips.append(item)
 else:
  out=H/'farpoint-station-v6-preview-60s.mp4';item=encode(s,out,60);item['validation'],hashes=verify(s,out,1800,True);clips.append(item)
  repeat=H/'farpoint-station-v6-three-loops-180s.mp4';assert not repeat.exists()
  subprocess.run([s.config['ffmpeg'],'-v','error','-n','-stream_loop','2','-i',str(out),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
  validation,repeated=verify(s,repeat,5400,True);assert repeated==hashes*3
  clips.append({'path':repeat.relative_to(R).as_posix(),'sha256':digest(repeat),'validation':validation,'exact_three_decoded_repetitions':True})
  cap=cv2.VideoCapture(str(out))
  for n in [0,150,600,1200,1710,1799]:
   cap.set(cv2.CAP_PROP_POS_FRAMES,n);ok,f=cap.read();assert ok;cv2.imwrite(str(H/f'decoded-{n:04d}.png'),f)
  cap.release()
 save(args.stage+'-validation.json',{'fingerprint':s.fingerprint(),'clips':clips,'silent':True,'user_approved':False,'inspection':'Source/mask/actual-strength temporal and decoded stills; continuous playback unavailable'})
 print(args.stage,'full decode and validation passed',flush=True)
if __name__=='__main__':main()
