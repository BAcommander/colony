"""V5: complete apertures, source cloud transport and ridge-occluded turbulent mist."""
from pathlib import Path
import sys,json,hashlib,subprocess,time,argparse
import cv2,numpy as np
from PIL import Image,ImageDraw
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'empty-junction-animation-v4'))
import render_junction_v4 as old
cv2.setNumThreads(4)
def write(name,obj): (H/name).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')
def smooth(x): return np.clip(x,0,1)**2*(3-2*np.clip(x,0,1))
def byte(x): return np.uint8(np.clip(np.rint(x),0,255))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

class Scene:
 def __init__(self):
  self.previous=old.Junction();p=self.previous
  self.base=p.base;self.src=self.base.astype(np.float32);self.h,self.w=self.base.shape[:2]
  self.x,self.y=p.x,p.y;self.masks={};self.prepare_sky();self.prepare_lights();self.prepare_mist()
  self.retained=[v for v in p.extra if v[0] in ('cabin_exhaust','yard_powder')]
  for name,roi,mask,fields in self.retained:self.masks[name]=p.masks[name]
  self.active=np.maximum.reduce(list(self.masks.values()))>0

 def polygon(self,points,feather=1): return self.previous.poly([points],feather)

 def prepare_sky(self):
  # Refine a hand-traced silhouette using local colour evidence. No image generation.
  p=self.previous;raw=self.polygon(p.config['sky']['polygon'],.5)[:350]
  hard=np.uint8(raw>.5);inside=cv2.distanceTransform(hard,cv2.DIST_L2,5)
  outside=cv2.distanceTransform(1-hard,cv2.DIST_L2,5)
  labels=np.full(hard.shape,cv2.GC_PR_BGD,np.uint8)
  labels[hard>0]=cv2.GC_PR_FGD;labels[inside>35]=cv2.GC_FGD;labels[outside>6]=cv2.GC_BGD
  cv2.setRNGSeed(44105)
  cv2.grabCut(cv2.cvtColor(self.base[:350],cv2.COLOR_RGB2BGR),labels,None,np.zeros((1,65)),np.zeros((1,65)),4,cv2.GC_INIT_WITH_MASK)
  safe=np.uint8((labels==cv2.GC_FGD)|(labels==cv2.GC_PR_FGD))
  # Conservative one-pixel protection, without the previous 32-pixel stationary fringe.
  edge=smooth((cv2.distanceTransform(safe,cv2.DIST_L2,5)-.5)/1.5)
  mask=np.zeros((self.h,self.w),np.float32);mask[:350]=edge
  # Keep weather entirely out of the lowest ambiguous skyline; fade in open sky only.
  mask*=smooth((330-self.y)/30);mask[mask<.002]=0
  self.masks['clouds']=mask
  # A cloud-free, slowly varying sky gradient, fitted only to sky samples.
  src=self.src[:350];bg=np.empty_like(src);filled=np.empty_like(src)
  xx=np.arange(self.w)
  support=p.masks['sky_clouds'][:350]>.995
  for y in range(350):
   valid=np.where(support[y])[0]
   if len(valid)<2: valid=np.array([800,1000])
   for c in range(3):
    filled[y,:,c]=np.interp(xx,valid,src[y,valid,c])
    # Upper radiance quantile avoids fitting the darker cloud body as sky.
    xs=[];ys=[]
    for a in range(0,self.w,170):
     take=valid[(valid>=a)&(valid<a+250)]
     if len(take)>15:xs.append(float(take.mean()));ys.append(float(np.percentile(src[y,take,c],85)))
    bg[y,:,c]=np.interp(xx,xs,ys) if xs else filled[y,:,c]
  bg=cv2.GaussianBlur(bg,(0,0),45,sigmaY=9)
  self.sky_bg=bg
  # Tight graph-cut matte supplies visible sky detail; conservative support above fits
  # the slow illumination gradient only. Fill hidden residual in 2D, not scanline stripes.
  source_safe=cv2.erode(safe,np.ones((7,7),np.uint8))
  residual=src-bg
  coded=byte(residual+128)
  filled_residual=cv2.inpaint(coded,np.uint8(source_safe==0)*255,5,cv2.INPAINT_TELEA).astype(np.float32)-128
  residual=residual*source_safe[...,None]+filled_residual*(1-source_safe[...,None])
  # Interpolation across hidden areas uses atmospheric samples only, never rock fragments.
  self.sky_texture=residual.astype(np.float32)
  self.sky_original=src-bg
  self.sky_x,self.sky_y=np.meshgrid(np.arange(self.w,dtype=np.float32),np.arange(350,dtype=np.float32))
  Image.fromarray(byte(bg+self.sky_texture)).save(H/'cloud-texture-reconstructed.png')

 def clouds(self,t):
  field=np.zeros_like(self.sky_texture);y=self.sky_y
  # Long uninterrupted forward transport; a brief zero-weight renewal at the end.
  # Equal continuously crossfaded copies merely blurred around a fixed centre.
  age=t%60;renew=float(smooth((age-50)/10))
  for local_age,weight in [(age,1-renew),(age-60,renew)]:
   if weight==0:continue
   speed=1.05-.35*smooth((y-140)/150)
   mx=self.sky_x-speed*(local_age-25)
   my=y+1.1*np.sin(self.sky_x/170+local_age*.018)*smooth((y-70)/80)
   field+=cv2.remap(self.sky_texture,mx.astype(np.float32),my.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)*weight
  return field-self.sky_original

 def prepare_lights(self):
  self.lights=[];r,g,b=cv2.split(self.src)
  # Complete pane geometry in source perspective, then emission selection protects mullions.
  galleries=[(1224,1243),(1246,1264),(1267,1286),(1290,1309),(1312,1332),(1336,1357),(1360,1383),(1387,1409),(1413,1435)]
  halls=[(932,945),(948,964),(967,991),(996,1013),(1017,1032),(1036,1056),(1061,1080),(1085,1110),(1115,1135)]
  specs=[]
  for i,(a,z) in enumerate(galleries):
   a-=.7;z+=.7
   top=lambda x:413.4-(x-1224)*.100
   bottom=lambda x:440-(x-1224)*.078
   specs.append((f'gallery_{i}',[[a,top(a)],[z,top(z)],[z,bottom(z)],[a,bottom(a)]],[9,37,4,46,23,54,16,41,30][i],[13,8,17,11,9,14,10,12,8][i],.64))
  for i,(a,z) in enumerate(halls):
   a-=.7;z+=.7
   top=lambda x:442.5-(x-932)*.059
   bottom=lambda x:459.5-(x-932)*.058
   specs.append((f'hall_{i}',[[a,top(a)],[z,top(z)],[z,bottom(z)],[a,bottom(a)]],[31,6,48,19,40,12,55,26,2][i],[9,12,7,13,8,10,9,14,11][i],.58))
  specs.extend([
   ('upper_left',[[1552,313],[1566,308],[1566,331],[1552,337]],8,15,.62),
   ('upper_right',[[1573,306],[1589,301],[1589,325],[1573,331]],37,15,.64),
   ('cabin',[[392,573],[408,573],[408,629],[392,630]],28,8,.23)])
  for name,poly,start,hold,depth in specs:
   geom=self.polygon(poly,.6)
   warm=smooth((r-b-14)/24)*smooth((r-58)/48)
   white_core=smooth((np.minimum(np.minimum(r,g),b)-145)/65)
   emission=np.maximum(warm,white_core)
   m=geom*emission;m[m<.002]=0
   self.masks['window_'+name]=m
   self.lights.append((name,m,start,hold,depth,1.8))
  # Retain the separately mapped practical lamps; discard all earlier partial window masks.
  for c,roi,m in self.previous.lights:
   if c['name'] in ('door_lamp','roof_amber','yard_signal','hall_practical','upper_door_lamp'):
    whole=self.previous.masks['light_'+c['name']];self.masks['practical_'+c['name']]=whole
    self.lights.append((c,whole,0,0,0,0))
  self.light_regions=[(name,*self.previous.crop(m),start,hold,depth,transition) for name,m,start,hold,depth,transition in self.lights]
  write('apertures.json',{'panes':[{'name':n,'polygon':poly,'start':s,'hold':h,'depth':d} for n,poly,s,h,d in specs],
    'method':'Complete perspective apertures, including white light cores; source emission gate protects dark mullions. No broad rectangular wall dimming.'})

 def prepare_mist(self):
  # Explicit ridge silhouettes bound each depth, separate from the soft atmospheric envelope.
  far=[[817,297],[888,300],[944,315],[1004,310],[1068,295],[1114,300],[1112,349],[1095,352],[1078,348],[1066,354],[1047,352],[1034,361],[1018,366],[1001,366],[991,363],[972,361],[956,350],[942,348],[927,344],[911,345],[900,337],[882,339],[871,332],[855,332],[843,320],[828,319]]
  middle=[[561,342],[658,327],[745,333],[827,351],[905,354],[973,367],[1052,372],[1081,383],[1061,414],[1006,418],[960,420],[940,414],[921,412],[903,410],[885,414],[865,413],[850,404],[828,405],[805,401],[789,392],[770,390],[749,392],[733,385],[710,387],[688,380],[666,379],[644,370],[621,370],[600,359],[581,361],[562,351]]
  self.fogs=[]
  for idx,(name,poly,center,height,speed,opacity,col) in enumerate([
   ('far_mist',far,333,23,1.05,.37,[153,160,181]),
   ('middle_mist',middle,371,23,2.5,.29,[137,148,169])]):
   mask=self.polygon(poly,2.2)
   # The hall's two foreground utility uprights and cross-arm stand in front of valley fog.
   mast_bounds=self.polygon([[954,385],[975,385],[975,433],[954,433]],.5)
   mast_detail=smooth((100-self.src.mean(2))/28)*mast_bounds
   mask*=1-mast_detail
   # Soft entrance/dissipation at path ends; crisp ridge occlusion at the lower edge.
   points=np.float32(poly);lo,hi=points[:,0].min(),points[:,0].max()
   mask*=smooth((self.x-lo)/65)*smooth((hi-self.x)/70)
   mask[mask<.002]=0;self.masks[name]=mask
   a,b,z,d=self.previous.crop(mask)[0];xx=self.x[b:d,a:z];yy=self.y[b:d,a:z]
   rng=np.random.default_rng(5510+idx);tex=np.zeros((384,2048),np.float32)
   for rows,cols,w in [(9,25,.50),(22,61,.28),(50,130,.15),(110,280,.07)]:
    tex+=cv2.resize(rng.random((rows,cols),dtype=np.float32),(2048,384),interpolation=cv2.INTER_CUBIC)*w
   self.fogs.append((name,(a,b,z,d),xx,yy,mask[b:d,a:z],tex,center,height,speed,opacity,np.float32(col)))

 def mist(self,t,item):
  name,roi,x,y,mask,tex,center,height,speed,opacity,col=item
  field=np.zeros_like(x)
  age=(t+(17 if name=='far_mist' else 39))%60;renew=float(smooth((age-48)/12))
  for local_age,w in [(age,1-renew),(age-60,renew)]:
   if w==0:continue
   u=x-speed*(local_age-30)+130
   # Spatial curl travels with the field: breakup changes shape while flowing downstream.
   v=(y-center)*1.8+180+8*np.sin(u/41+local_age*.03)+4*np.sin(u/19-local_age*.02)
   noise=cv2.remap(tex,u.astype(np.float32),v.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
   field+=noise*w
  envelope=np.exp(-.5*((y-center-6*np.sin(x/93))/height)**2)
  density=smooth((field-.31)/.38)*envelope
  alpha=(1-np.exp(-density*opacity*1.65))*mask
  return alpha,col

 def frame(self,t,only=None):
  t=float(t)%60;f=self.src.copy()
  if only in (None,'clouds'): f[:350]+=self.clouds(t)*self.masks['clouds'][:350,:,None]
  for item in self.fogs:
   if only not in (None,'mist'): continue
   a,b,z,d=item[1];alpha,col=self.mist(t,item)
   f[b:d,a:z]=f[b:d,a:z]*(1-alpha[...,None])+col*alpha[...,None]
  if only in (None,'windows'):
   for name,roi,m,start,hold,depth,transition in self.light_regions:
    if isinstance(name,dict):amount=self.previous.amount(t,name['events'])
    else:amount=self.previous.amount(t,[{'start':start,'hold':hold,'depth':depth,'transition':transition}])
    # Subtract the emissive contribution, keeping cool ambient reflected light in glass.
    a,b,z,d=roi;local=f[b:d,a:z]
    emission=np.maximum(local-np.float32([27,31,40]),0)
    f[b:d,a:z]-=emission*m[...,None]*amount
  if only is None:
   for name,roi,mask,fields in self.retained:
    f=self.previous.apply_extra(f,t,name,roi,mask,fields,self.previous.wind_envelope(t) if name=='yard_powder' else 1)
  f=byte(f);assert np.array_equal(f[~self.active],self.base[~self.active]);return f

def samples(s):
 (H/'masks').mkdir(exist_ok=True)
 for name,m in s.masks.items():Image.fromarray(byte(m*255)).save(H/'masks'/f'{name}.png')
 union=np.maximum.reduce([m for k,m in s.masks.items() if k.startswith('window')])
 overlay=s.src*(1-union[...,None]*.7)+np.float32([20,240,160])*union[...,None]*.7
 Image.fromarray(byte(overlay)).save(H/'window-mask-overlay.png')
 for t in [0,6,12,20,32,44,56]:Image.fromarray(s.frame(t)).save(H/f'sample-{t:02d}.png')
 for name in ['clouds','mist','windows']:
  for t in [6,20,44]:Image.fromarray(s.frame(t,name)).save(H/f'{name}-{t:02d}.png')
 for name,box in [('gallery',(1210,387,1440,443)),('hall',(925,428,1140,466)),('valley',(760,280,1150,430))]:
  crops=[Image.fromarray(s.frame(t)).crop(box).resize(((box[2]-box[0])*3,(box[3]-box[1])*3)) for t in [0,12,32,44]]
  sheet=Image.new('RGB',(crops[0].width,crops[0].height*4))
  for i,c in enumerate(crops):sheet.paste(c,(0,i*c.height))
  sheet.save(H/f'{name}-temporal.png')
 checks={}
 for layer in ['clouds','mist','windows',None]:
  assert np.array_equal(s.frame(0,layer),s.frame(60,layer))
  vals=[float(np.abs(s.frame(t+1/30,layer).astype(float)-s.frame(t,layer)).mean()) for t in [-1/30,0,8,20,32,44,56]]
  assert vals[0]<=max(vals[1:])*1.3+.002
  checks[str(layer)]={'periodic':True,'seam_mae':vals[0],'sample_max_mae':max(vals[1:])}
 write('analytic-validation.json',{'checks':checks,'source_sha256':sha(s.previous.source_path),'protected_pixels':'Asserted every native rendered frame','user_approved':False})

def encoder(path,w=1280,h=720):
 assert not path.exists(),path
 return subprocess.Popen(['ffmpeg','-v','error','-n','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r','30','-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-qp','0','-pix_fmt','yuv420p','-movflags','+faststart',str(path)],stdin=subprocess.PIPE)

def render(s,seconds):
 out=H/f'Empty-Junction-v5-{seconds}s-720p.mp4';proc=encoder(out)
 started=time.time()
 try:
  for i in range(seconds*30):
   frame=cv2.resize(s.frame(i/30),(1280,720),interpolation=cv2.INTER_AREA);proc.stdin.write(frame.tobytes())
   if i%150==0: print('v5',i,'/',seconds*30,'elapsed',round(time.time()-started),flush=True)
 finally:proc.stdin.close()
 assert proc.wait()==0
 write('render-record.json',{'path':out.name,'sha256':sha(out),'seconds':seconds,'frames':seconds*30,'renderer_sha256':sha(__file__),'source_sha256':sha(s.previous.source_path),'user_approved':False})

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['samples','render'],required=True);p.add_argument('--seconds',type=int,default=60);args=p.parse_args();s=Scene()
 if args.stage=='samples':samples(s)
 else:render(s,args.seconds)
