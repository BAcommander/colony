"""Delivery checks targeted to v6 feedback; numbers do not establish artistic acceptance."""
import json,subprocess
import cv2,numpy as np
from PIL import Image
from render_farpoint_v6 import FarpointV6,FarpointV5,H,R,save,digest

def decoded(path,index):
 cap=cv2.VideoCapture(str(path));cap.set(cv2.CAP_PROP_POS_FRAMES,index)
 ok,f=cap.read();cap.release();assert ok,(path,index)
 return f

def main():
 s=FarpointV6();old=FarpointV5()
 original=np.array(Image.open(R/s.config['original_source']['path']).convert('RGB'))
 m=np.load(H/'reflection-cleanup-mask.npy')
 assert np.array_equal(s.base[m==0],original[m==0])
 cleanup=[]
 for x,y in [(433,497),(434,551),(434,560)]:
  before=original[y-2:y+3,x-3:x+4].mean(2)
  after=s.base[y-2:y+3,x-3:x+4].mean(2)
  assert after.max()<before.max()*.65
  cleanup.append({'center':[x,y],'original_peak':float(before.max()),'clean_peak':float(after.max())})
 assert np.array_equal(original[600:720,320:520],s.base[600:720,320:520])
 planet=old.layer_masks['planet_activity']
 retained={}
 for t in [0,7,20,40,54]:
  retained[str(t)]=np.array_equal(s.frame(t)[planet],old.frame(t)[planet])
  assert retained[str(t)],t
 # Motion tracking is an encode/transport diagnostic, not a readability verdict.
 p=H/'stars-v6-isolated-10s.mp4'
 f0=decoded(p,0);f8=decoded(p,240)
 g0=cv2.cvtColor(f0,cv2.COLOR_BGR2GRAY);g8=cv2.cvtColor(f8,cv2.COLOR_BGR2GRAY)
 safe=cv2.resize(s.masks['stars'],(1280,720),interpolation=cv2.INTER_AREA)
 safe=np.uint8(safe>.999)*255
 safe=cv2.erode(safe,np.ones((31,31),np.uint8))
 points=cv2.goodFeaturesToTrack(g0,300,.015,8,mask=safe,blockSize=3)
 assert points is not None
 q,status,err=cv2.calcOpticalFlowPyrLK(g0,g8,points,None,winSize=(17,17),maxLevel=3)
 back,bs,be=cv2.calcOpticalFlowPyrLK(g8,g0,q,None,winSize=(17,17),maxLevel=3)
 good=(status[:,0]>0)&(bs[:,0]>0)&(np.linalg.norm(back[:,0]-points[:,0],axis=1)<.75)
 flow=q[:,0]-points[:,0];good&=(err[:,0]<12)
 flows=flow[good]
 expected=np.float32([1.25*8*1280/1672,-.13*8*720/941])
 matching=np.linalg.norm(flows-expected,axis=1)<1
 assert matching.sum()>=20,(len(flows),matching.sum(),np.median(flows,axis=0))
 tracked={'tested_frame_indices':[0,240],'reliable_points':len(flows),'matching_expected_translation':int(matching.sum()),'median_matching_displacement':np.median(flows[matching],axis=0).tolist(),'expected_displacement':expected.tolist(),'scope':'Encoded transport diagnostic only; does not establish visual acceptance'}
 # Actual minute positions and velocities through the join, before quantization.
 analytic=[]
 for x,y,sprite,phase in s.star_sprites:
  def state(t):
   c=s.config['drifting_stars'];age=(t+phase+30)%60-30
   return np.array([x+1.25*age,y-.13*age]),float(np.clip((30-abs(age))/5,0,1))
  a,fa=state(60-1/30);b,fb=state(60);c,fc=state(1/30)
  if min(fa,fb,fc)>.1:
   assert np.allclose(b-a,c-b,atol=1e-8)
   analytic.append(float(np.linalg.norm(b-a)))
 assert len(analytic)>200
 leds={}
 for lc,((a,b,z,d),mask) in s.cabinet_lights:
  x,y=map(lambda v:int(round(v)),lc['center'])
  vals=[s.frame(t,'cabinet_leds')[y,x].astype(float) for t in [0,5.5,13,20,37,57]]
  spread=float(np.ptp(np.array(vals),axis=0).max())
  assert (spread==0) if lc['steady'] else (spread>80),(lc['name'],spread)
  leds[lc['name']]={'core_rgb_at_0_5p5_13_20_37_57s':[v.tolist() for v in vals],'maximum_channel_range':spread,'steady':lc['steady']}
 streams={}
 for path in [H/'farpoint-station-v6-preview-60s.mp4',H/'farpoint-station-v6-three-loops-180s.mp4']:
  result=subprocess.run([s.config['ffmpeg'],'-hide_banner','-i',str(path)],capture_output=True,text=True)
  text=result.stderr
  assert 'Audio:' not in text and 'Video: h264' in text and '1280x720' in text and '30 fps' in text
  (H/(path.stem+'-streams.txt')).write_text(text,encoding='utf-8')
  streams[path.name]={'video_only':True,'bytes':path.stat().st_size,'sha256':digest(path)}
 save('targeted-validation.json',{'fingerprint':s.fingerprint(),'original_pixels_exact_outside_cleanup':True,'lamp_and_desk_source_unchanged':True,'removed_bar_cores':cleanup,'full_planet_composite_exact_vs_v5':retained,'encoded_star_transport':tracked,'stars_with_continuous_forward_velocity_at_join':len(analytic),'cabinet_lights':leds,'streams':streams,'artistic_acceptance':False})
 print('Cleanup, retained planet, encoded star transport, cabinet and stream checks passed',flush=True)
if __name__=='__main__':main()
