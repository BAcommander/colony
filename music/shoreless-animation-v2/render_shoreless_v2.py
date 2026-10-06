"""Scoped Shoreless revision: complete panes, foam, antenna signals, readable UI and sunlight."""
from pathlib import Path
import sys,json,hashlib,argparse,subprocess
import cv2,numpy as np
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parents[1];V1=H.parent/'shoreless-animation-v1'
sys.path.insert(0,str(V1))
from render_shoreless import Shoreless,verify
from render_floodplain import encode,digest
from ambient_effects import smoothstep,event_amount

class ShorelessV2(Shoreless):
 def __init__(self):
  super().__init__(H/'scene-plan-v2.json');c=self.config
  assert digest(V1/'render_shoreless.py')==c['v1_renderer_sha256']
  # Bound to complete glass shapes first; suppress dark/cool framing within them.
  rgb=self.base.astype(np.float32);lum=rgb.mean(2);warm=np.clip((rgb[:,:,0]-rgb[:,:,2]-2)/26,0,1);white=np.clip((lum-145)/50,0,1)
  gate=np.maximum(warm,white)*np.clip((lum-28)/38,0,1)
  self.lights=[];union=np.zeros_like(self.x)
  for lc in c['lights']:
   m=self.aperture(lc['polygons'])*gate;m[m<.003]=0
   union=np.maximum(union,m);self.lights.append((lc,m))
  self.practicals=[]
  for lc in c['exterior_flickers']:
   x,y=lc['center'];rx,ry=lc['radius'];sx,sy=lc['spill_radius']
   core=np.exp(-((self.x-x)/rx)**4-((self.y-y)/ry)**4)
   spill=np.exp(-((self.x-x)/sx)**2-((self.y-y)/sy)**2)*warm*.20
   m=np.maximum(core,spill).astype(np.float32);m[m<.003]=0
   self.practicals.append((lc,m));union=np.maximum(union,m)
  self.masks['lights']=union
  self.antennas=[];union=np.zeros_like(self.x)
  for ac in c['antenna_lights']:
   x,y=ac['center'];rr=(self.x-x)**2+(self.y-y)**2
   m=np.clip(np.exp(-rr/(2*ac['radius']**2))+.13*np.exp(-rr/(2*ac['halo']**2)),0,1).astype(np.float32);m[m<.003]=0
   union=np.maximum(union,m);self.antennas.append((ac,m))
  self.masks['antennas']=union
  a,b,z,d=c['water']['roi'];self.foam_roi=(a,b,z,d);self.foam_mask=self.masks['water'][b:d,a:z]
  self.foam_y,self.foam_x=np.mgrid[b:d,a:z].astype(np.float32);wash=np.zeros_like(self.foam_x)
  for x,y,rx,ry in c['foam']['wash_zones']:wash=np.maximum(wash,np.exp(-((self.foam_x-x)/rx)**2-((self.foam_y-y)/ry)**2))
  self.wash=wash;self.masks['foam']=self.masks['water'].copy()
  # Fixed multiscale texture advects through periodic local lifetimes.
  rng=np.random.default_rng(c['foam']['seed']);noise=rng.uniform(0,1,(128,384)).astype(np.float32)
  self.foam_noise=cv2.resize(noise,(z-a,d-b),interpolation=cv2.INTER_CUBIC)
  self.foam_noise=cv2.GaussianBlur(self.foam_noise,(0,0),.5)
  self.foam_yy,self.foam_xx=np.mgrid[:d-b,:z-a].astype(np.float32)
  sc=c['sunlight'];cx,cy=sc['opening'];rx,ry=sc['opening_radius'];opening=np.exp(-((self.x-cx)/rx)**2-((self.y-cy)/ry)**2)*self.masks['sky']
  self.sun_sky=opening.astype(np.float32);shaft=np.zeros_like(self.x)
  height=self.y-cy;vertical=smoothstep(height/20)*smoothstep((240-height)/80)
  for slope,width in sc['rays']:
   center=cx+slope*height
   shaft+=np.exp(-((self.x-center)/(width+height*.11))**2)*vertical
  self.sun_shafts=np.minimum(shaft,.85)*(np.maximum(self.masks['sky'],self.masks['water']))
  self.sun_water=np.exp(-((self.x-654)/240)**2)*self.masks['water']*np.clip((self.y-330)/190,0,1)
  for m in [self.sun_sky,self.sun_shafts,self.sun_water]:m[m<.002]=0
  self.masks['sunlight']=np.maximum.reduce([self.sun_sky,self.sun_shafts,self.sun_water])
  ic=c['telemetry'];iw,ih=ic['size'];a,b,z,d=self.ui_roi;q=np.float32(ic['quad'])-np.float32([a,b]);rect=np.float32([[0,0],[iw-1,0],[iw-1,ih-1],[0,ih-1]])
  self.telemetry_back=cv2.getPerspectiveTransform(rect,q)
  self.masks['room']=np.maximum(self.masks['lamp'],self.masks['computers'])
  self.layer_masks={k:v>0 for k,v in self.masks.items()};self.active=np.logical_or.reduce(list(self.layer_masks.values()))

 def draw_computers(self,f,t):
  super().draw_computers(f,t)
  if not hasattr(self,'telemetry_back'):return
  a,b,z,d=self.ui_roi;patch=f[b:d,a:z].copy();x=self.ui_x;y=self.ui_y
  route=np.float32(self.config['computers']['route'])
  # Sequential highlights follow existing platform links; retain diagram geometry.
  for j in range(len(route)-1):
   line=np.zeros(patch.shape[:2],np.uint8);p=route[j]-[a,b];q=route[j+1]-[a,b]
   cv2.line(line,tuple(np.rint(p*256).astype(int)),tuple(np.rint(q*256).astype(int)),255,2,cv2.LINE_AA,8)
   amount=event_amount(t,20,1+j*2.7,3.0,.6)
   patch+=(line.astype(np.float32)/255)[...,None]*amount*np.float32([20,69,81])
  for j,(cx,cy) in enumerate(route[[1,3,4]]):
   ring=np.exp(-((np.sqrt((x-cx)**2+(y-cy)**2)-4.0)/.8)**2)*event_amount(t,20,2+j*5,3.5,.7)
   patch+=ring[...,None]*np.float32([33,100,118])
  ic=self.config['telemetry'];iw,ih=ic['size'];panel=np.zeros((ih,iw,3),np.float32);panel[:]=[17,30,36]
  for xx in range(8,iw,14):panel[:,xx]=[29,48,55]
  for yy in range(8,ih,12):panel[yy,:]=[29,48,55]
  phase=2*np.pi*t/10;xx=np.arange(iw,dtype=np.float32);yy=ih*.49+9*np.sin(xx*.094-phase)+4*np.sin(xx*.23+phase*2)
  ink=np.zeros((ih,iw),np.uint8);cv2.polylines(ink,[np.rint(np.stack([xx,yy],axis=1)*256).astype(np.int32)],False,255,2,cv2.LINE_AA,8)
  line=ink.astype(np.float32)/255;panel=panel*(1-line[...,None])+np.float32([111,211,225])*line[...,None]
  for j in range(12):
   level=.5+.25*np.sin(phase*.5)+.18*np.sin(phase*1.5+.7)
   panel[ih-10:ih-5,5+j*8:10+j*8]+=np.float32([24,68,79])*np.clip(level*12-j,0,1)
  py,px=np.mgrid[:ih,:iw];alpha=np.minimum.reduce([px+1,iw-px,py+1,ih-py]).astype(np.float32);alpha=np.clip(alpha/3,0,1)*ic['opacity']
  wa=cv2.warpPerspective(alpha,self.telemetry_back,(z-a,d-b));color=cv2.warpPerspective(panel*alpha[...,None],self.telemetry_back,(z-a,d-b))
  patch=patch*(1-wa[...,None])+color
  f[b:d,a:z]+=self.ui_mask[...,None]*(patch-f[b:d,a:z])

 def add_foam(self,f,t):
  a,b,z,d=self.foam_roi;patch=f[b:d,a:z];lum=patch.mean(2)
  # Follow photographed moving crests, rather than drawing white ellipses.
  crest=np.clip((lum-cv2.GaussianBlur(lum,(0,0),5)-3)/23,0,1)
  cool=np.clip((patch[:,:,2]-patch[:,:,0]+15)/30,0,1)
  noise=np.zeros_like(lum)
  for phase in [0,.5]:
   age=(t/10+self.foam_x/1700+self.foam_y/1900+phase)%1;weight=np.sin(np.pi*age)**2
   moved=cv2.remap(self.foam_noise,(self.foam_xx-20*(age-.5)).astype(np.float32),(self.foam_yy-4*(age-.5)).astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
   noise+=moved*weight
  broken=np.clip((noise-.34)*2.7,0,1)
  wash_pulse=.68+.32*np.sin(2*np.pi*t/5+self.foam_x*.035+self.foam_y*.021)**2
  coverage=self.config['foam']['open_sea_strength']+.75*self.wash*wash_pulse
  alpha=crest*cool*broken*coverage*self.foam_mask*self.config['foam']['strength']
  f[b:d,a:z]=patch*(1-alpha[...,None])+np.float32(self.config['foam']['color'])*alpha[...,None]

 def frame(self,t,only=None,prototype=False):
  t=float(t)%self.duration;f=super().frame(t,only,prototype).astype(np.float32)
  if only in (None,'lights'):
   for lc,m in self.lights:
    amount=max((event_amount(t,20,e['start'],e['hold'],e['transition'])*e['depth'] for e in lc.get('flickers',[])),default=0)
    f*=1-m[...,None]*amount
   for lc,m in self.practicals:
    amount=max(event_amount(t,20,e['start'],e['hold'],e['transition'])*e['depth'] for e in lc['events']);f*=1-m[...,None]*amount
  if only in (None,'foam'):self.add_foam(f,t)
  if only in (None,'antennas'):
   for ac,m in self.antennas:
    age=(t-ac['phase'])%20;local=age%ac['period']
    pulse=float(smoothstep(local/.12)*smoothstep((.7-local)/.18))
    color=np.float32([242,48,29] if int(age/ac['period'])%2==0 else [54,225,126])
    alpha=m[...,None]*pulse*.88;f=f*(1-alpha)+color*alpha
  if only in (None,'sunlight'):
   sc=self.config['sunlight'];amount=event_amount(t,20,sc['start'],sc['hold'],sc['transition'])
   f+=amount*(self.sun_sky[...,None]*np.float32(sc['sky_gain'])+self.sun_shafts[...,None]*np.float32(sc['shaft_gain']))
   # Modulate existing crests to retain water texture in the warm reflection patch.
   lum=f.mean(2);response=.35+.65*np.clip((lum-35)/80,0,1)
   f+=self.sun_water[...,None]*response[...,None]*amount*np.float32(sc['water_gain'])
  assert np.isfinite(f).all();f=np.uint8(np.rint(np.clip(f,0,255)));mask=self.active if only is None else self.layer_masks[only]
  assert np.array_equal(f[~mask],self.base[~mask]),'Protected source changed'
  return f
 def fingerprint(self):
  d=super().fingerprint();d['dependencies']['music/shoreless-animation-v1/render_shoreless.py']=d['renderer_sha256'];d['renderer_sha256']=digest(__file__);return d

def samples(s):
 (H/'masks').mkdir(exist_ok=True);overlay=s.base.astype(np.float32)
 for k,m in s.masks.items():cv2.imwrite(str(H/'masks'/f'{k}.png'),np.uint8(np.rint(m*255)))
 for k,col in [('lights',[255,60,40]),('foam',[40,200,255]),('antennas',[60,255,150]),('room',[240,220,20]),('sunlight',[255,160,30])]:
  alpha=s.masks[k][...,None]*.35;overlay=overlay*(1-alpha)+np.float32(col)*alpha
 Image.fromarray(np.uint8(overlay)).save(H/'mask-review.png')
 for t in [0,4.35,6,8,12,16,19+29/30]:Image.fromarray(s.frame(t)).save(H/f'sample-{t:.3f}s.png')
 for name,box in [('near',(260,399,350,434)),('middle',(731,390,790,418)),('far',(975,400,1021,422))]:
  a,b,z,d=box
  mask=s.masks['lights'][b:d,a:z];crop=s.base[b:d,a:z].astype(np.float32)*(1-mask[...,None]*.8)
  Image.fromarray(np.uint8(crop)).resize(((z-a)*6,(d-b)*6)).save(H/f'{name}-dim-mask.png')
 report={}
 for name,m in s.layer_masks.items():
  assert np.array_equal(s.frame(0,name),s.frame(20,name));values=[]
  for t in [-1/30,0,3,7,12,16]:values.append(float(abs(s.frame(t+1/30,name)[m].astype(float)-s.frame(t,name)[m]).mean()))
  assert values[0]<=max(values[1:])*1.1+.01,(name,values)
  report[name]={'endpoint_exact':True,'seam_mae':values[0],'ordinary_max_sampled':max(values[1:]),'pass':True}
 old=Shoreless();retained={}
 for layer in ['water','sky','turbines','beacons']:
  retained[layer]=all(np.array_equal(s.frame(t,layer),old.frame(t,layer)) for t in [0,7]);assert retained[layer]
 (H/'analytic-validation.json').write_text(json.dumps({'fingerprint':s.fingerprint(),'layers':report,'v1_retained_layers_exact_at_0_and_7':retained,'user_motion_approved':False},indent=2)+'\n',encoding='utf-8')
 print('Masks, temporal samples, analytical seams and retained V1 layers passed',flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['samples','isolated','preview'],required=True);a=p.parse_args();s=ShorelessV2()
 if a.stage=='samples':samples(s);return
 clips=[]
 if a.stage=='isolated':
  for layer in s.config['isolated_layers']:
   out=H/f'{layer}-isolated-v2-8s.mp4';item=encode(s,out,8,layer);item['validation'],_=verify(s,out,240,False);clips.append(item);print(layer,'isolated checks passed',flush=True)
 else:
  out=H/'shoreless-colony-v2-preview-20s.mp4';item=encode(s,out,20);item['validation'],hashes=verify(s,out,600,True);clips.append(item)
  repeat=H/'shoreless-colony-v2-three-loops-60s.mp4';assert not repeat.exists();subprocess.run([s.config['ffmpeg'],'-v','error','-n','-stream_loop','2','-i',str(out),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
  v,hs=verify(s,repeat,1800,True);assert hs==hashes*3;clips.append({'path':repeat.relative_to(R).as_posix(),'sha256':digest(repeat),'validation':v,'three_repeated_decoded_payloads_identical':True})
  cap=cv2.VideoCapture(str(out));cap.set(cv2.CAP_PROP_POS_MSEC,8000);ok,f=cap.read();cap.release();assert ok;cv2.imwrite(str(H/'decoded-preview-8s.png'),f)
 (H/(a.stage+'-validation.json')).write_text(json.dumps({'fingerprint':s.fingerprint(),'clips':clips,'silent':True,'user_motion_approved':False,'inspection':'Source/mask/temporal/decoded stills; no continuous playback claim'},indent=2)+'\n',encoding='utf-8');print(a.stage,'checks passed',flush=True)
if __name__=='__main__':main()
