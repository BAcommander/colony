"""Screen-only extension of immutable Cable Station v2; native source coordinates."""
from pathlib import Path
import sys,json,hashlib,argparse,subprocess
import cv2,numpy as np
from PIL import Image
H=Path(__file__).resolve().parent;ROOT=H.parents[1]
sys.path.insert(0,str(H.parent/'cable-animation-v2'))
from render_cable_v2 import CableV2
from ambient_effects import smoothstep,event_amount
from render_floodplain import encode,verify,digest

class CableV3(CableV2):
 def __init__(self,config='scene-plan-v3.json'):
  super().__init__(str(H/config));c=self.config['computer_activity']
  self.computer_config=c
  self.computer_aperture=self.poly([c['left_aperture'],c['right_aperture']]).astype(np.float32)
  self.computer_aperture=smoothstep(cv2.distanceTransform(np.uint8(self.computer_aperture),cv2.DIST_L2,5)/2)
  self.masks['computers']=self.computer_aperture
  self.layer_masks={k:v>0 for k,v in self.masks.items()};self.active=np.logical_or.reduce(list(self.layer_masks.values()))
  self.roi=(267,467,626,593);x0,y0,x1,y1=self.roi
  self.ui_y,self.ui_x=np.mgrid[y0:y1,x0:x1].astype(np.float32)
  self.ui_mask=self.computer_aperture[y0:y1,x0:x1]
  points=np.array(c['route'],np.float32);self.route_points=points
  self.route_lengths=np.linalg.norm(np.diff(points,axis=0),axis=1);self.route_total=self.route_lengths.sum()
  w,h=c['log_size'];src=np.float32(c['log_quad']);dest=np.float32([[0,0],[w-1,0],[w-1,h-1],[0,h-1]])
  self.log_transform=cv2.getPerspectiveTransform(src,dest)
  self.log_texture=cv2.warpPerspective(self.base,self.log_transform,(w,h),flags=cv2.INTER_LINEAR)
  self.log_y,self.log_x=np.mgrid[:h,:w].astype(np.float32)
  points_local=src-np.array([x0,y0],np.float32)
  self.log_to_roi=cv2.getPerspectiveTransform(dest,points_local)
  log_mask=self.poly([c['log_quad']])[y0:y1,x0:x1]
  self.log_mask=smoothstep(cv2.distanceTransform(log_mask,cv2.DIST_L2,5)/2.2)
  self.log_original=self.base[y0:y1,x0:x1].astype(np.float32)
  self.log_reprojected=cv2.warpPerspective(self.log_texture,self.log_to_roi,(x1-x0,y1-y0),flags=cv2.INTER_LINEAR).astype(np.float32)

 def route_xy(self,fraction):
  distance=float(fraction)*float(self.route_total)
  for i,length in enumerate(self.route_lengths):
   if distance<=length:return self.route_points[i]+(self.route_points[i+1]-self.route_points[i])*(distance/length)
   distance-=float(length)
  return self.route_points[-1]

 def frame(self,t,only=None,prototype=False):
  t=float(t)%self.duration;f=super().frame(t,only,prototype)
  if only not in (None,'computers'):return f
  c=self.computer_config;x0,y0,x1,y1=self.roi;patch=f[y0:y1,x0:x1].astype(np.float32)
  x=self.ui_x;y=self.ui_y
  fraction=(t/c['route_duration_seconds'])%1;cx,cy=self.route_xy(fraction)
  env=smoothstep(t/c['route_fade_seconds'])*smoothstep((self.duration-t)/c['route_fade_seconds'])
  core=np.exp(-.5*((x-cx)**2+(y-cy)**2)/c['marker_radius']**2)
  glow=np.exp(-.5*((x-cx)**2+(y-cy)**2)/3.1**2)*.22
  patch+=(core+glow)[...,None]*np.array(c['route_color'])*env
  for node in c['nodes']:
   nx,ny=node['xy'];amount=event_amount(t,self.duration,node['start'],node['hold'],.6)
   radius=np.sqrt((x-nx)**2+(y-ny)**2)
   ring=np.exp(-.5*((radius-3.4)/.65)**2)*amount
   patch+=ring[...,None]*np.array([28,55,58])
  # Translate the actual source log within its existing perspective viewport.
  w,h=c['log_size'];shift=(t/c['log_scroll_seconds']*h)%h
  moving=cv2.remap(self.log_texture,self.log_x,(self.log_y+shift).astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_WRAP)
  projected=cv2.warpPerspective(moving,self.log_to_roi,(x1-x0,y1-y0),flags=cv2.INTER_LINEAR).astype(np.float32)
  patch+=self.log_mask[...,None]*(projected-self.log_reprojected)
  for indicator in c['indicators']:
   ax,ay,bx,by=indicator['roi'];amount=event_amount(t,self.duration,indicator['start'],indicator['hold'],.5)
   select=(x>=ax)&(x<bx)&(y>=ay)&(y<by)
   # Light existing data strokes more clearly instead of painting a bright row across the pane.
   blue=self.log_original[:,:,2]>self.log_original[:,:,0]*1.08
   active=select&blue&(self.log_original[:,:,1]>40)
   patch[active]+=np.array([11,30,32])*amount
  cursor=c['cursor'];ax,ay,bx,by=cursor['roi'];blink=event_amount(t,cursor['period_seconds'],.4,1.6,.15)
  cursor_mask=((x>=ax)&(x<bx)&(y>=ay)&(y<by)).astype(np.float32)
  patch+=cursor_mask[...,None]*np.array(cursor['color'])*blink
  meter=c['meter'];ax,ay=meter['start_xy'];phase=2*np.pi*t/self.duration
  level=(np.sin(phase+.6)+.35*np.sin(2*phase-1)+1.35)/2.7
  width=meter['width']*(meter['minimum_fraction']+(meter['maximum_fraction']-meter['minimum_fraction'])*level)
  bar=smoothstep((ax+width-x)/1.5)*((x>=ax)&(x<ax+meter['width'])&(y>=ay)&(y<ay+meter['height']))
  patch+=bar[...,None]*np.array(meter['color'])
  prior=f[y0:y1,x0:x1].astype(np.float32)
  patch=prior+self.ui_mask[...,None]*(patch-prior)
  assert np.isfinite(patch).all()
  f[y0:y1,x0:x1]=np.uint8(np.rint(np.clip(patch,0,255)))
  mask=self.active if only is None else self.layer_masks['computers']
  assert np.array_equal(f[~mask],self.base[~mask])
  return f

 def fingerprint(self):
  parent=super().fingerprint();parent['dependencies']['music/cable-animation-v2/render_cable_v2.py']=parent.pop('renderer_sha256')
  parent['renderer_sha256']=digest(__file__);return parent

def samples(s):
 mask=s.layer_masks['computers'];v2=CableV2();retained=[]
 for t in [0,4,8,12,16,19+29/30]:
  frame=s.frame(t);old=v2.frame(t);assert np.array_equal(frame[~mask],old[~mask]),'V2 outside screens changed'
  retained.append(t);Image.fromarray(frame).save(H/f'sample-{t:.3f}s.png')
  Image.fromarray(frame[449:611,227:643]).resize((1248,486)).save(H/f'screen-sample-{t:.3f}s.png')
 assert np.array_equal(s.frame(0,'computers'),s.frame(20,'computers'))
 seam=float(abs(s.frame(-1/30,'computers')[mask].astype(float)-s.frame(0,'computers')[mask]).mean())
 ordinary=[float(abs(s.frame(t+1/30,'computers')[mask].astype(float)-s.frame(t,'computers')[mask]).mean()) for t in np.arange(0,20,.5)]
 assert seam<=max(ordinary)*1.1+.01,(seam,max(ordinary))
 cv2.imwrite(str(H/'screen-mask.png'),np.uint8(s.masks['computers']*255))
 (H/'analytic-validation.json').write_text(json.dumps({'fingerprint':s.fingerprint(),'computers':{'endpoint_exact':True,'seam_mae':seam,'ordinary_max_sampled':max(ordinary),'pass':True},'v2_outside_screens_exact_at_seconds':retained,'user_motion_approved':False},indent=2)+'\n')
 print('Computer samples, seams and unchanged-v2 checks passed',flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['samples','isolated','preview'],required=True);a=p.parse_args();s=CableV3();clips=[]
 if a.stage=='samples':samples(s);return
 if a.stage=='isolated':
  out=H/'computers-isolated-v3-8s.mp4';item=encode(s,out,8,'computers');item['validation']=verify(s,out,240);clips.append(item)
 else:
  out=H/'last-cable-station-v3-preview-20s.mp4';item=encode(s,out,20);item['validation']=verify(s,out,600,True);clips.append(item)
  repeat=H/'last-cable-station-v3-three-loops-60s.mp4';assert not repeat.exists()
  subprocess.run([s.config['ffmpeg'],'-v','error','-n','-stream_loop','2','-i',str(out),'-map','0:v:0','-c','copy','-an','-movflags','+faststart',str(repeat)],check=True)
  validation=verify(s,repeat,1800,True)
  cap=cv2.VideoCapture(str(repeat));hs=[]
  while True:
   ok,f=cap.read()
   if not ok:break
   hs.append(hashlib.sha256(f.tobytes()).hexdigest())
  cap.release();assert hs[:600]==hs[600:1200]==hs[1200:]
  clips.append({'path':repeat.relative_to(ROOT).as_posix(),'sha256':digest(repeat),'validation':validation,'three_repeated_decoded_payloads_identical':True})
  cap=cv2.VideoCapture(str(out));cap.set(cv2.CAP_PROP_POS_MSEC,8000);ok,f=cap.read();cap.release();assert ok;cv2.imwrite(str(H/'decoded-v3-8s.png'),f)
 (H/(a.stage+'-validation.json')).write_text(json.dumps({'fingerprint':s.fingerprint(),'clips':clips,'user_motion_approved':False,'prior_feedback':s.config['feedback'],'inspection':'Temporal/decoded still inspection; continuous playback not claimed','silent':True},indent=2)+'\n')
 print(a.stage+' passed',flush=True)
if __name__=='__main__':main()
