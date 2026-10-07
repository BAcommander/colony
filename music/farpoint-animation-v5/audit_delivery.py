"""Check the actual complaints: central/lower weather coverage and encoded star visibility."""
import json,subprocess
import cv2,numpy as np
from render_farpoint_v5 import FarpointV5,H,R,save,digest
def main():
 s=FarpointV5()
 assert 'aurora' not in s.masks and 'aurora' not in s.layer_masks
 regions={'central_plain':[1040,370,1280,490],'lower_left':[760,490,1000,570],'lower_middle':[1050,505,1310,594],'lower_right':[1380,465,1575,600],'upper_middle':[1010,270,1300,365],'right_atmosphere':[1440,270,1590,460]}
 coverage={k:[] for k in regions}
 for t in [0,8,20,30,40,50,56]:
  f=s.frame(t,'expanded_weather').astype(np.float32);g=s.frame(t+4,'expanded_weather').astype(np.float32)
  for name,(a,b,z,d) in regions.items():
   change=np.abs(g[b:d,a:z]-f[b:d,a:z]).mean(2)
   coverage[name].append({'time':t,'mean_change_over_four_seconds':float(change.mean()),'fraction_over_two_levels':float((change>2).mean())})
 for name,rows in coverage.items():
  assert all(x['mean_change_over_four_seconds']>.2 for x in rows),(name,rows)
 # Measure encoded original stars at 720p, not only float masks or enlarged diagnostics.
 cap=cv2.VideoCapture(str(H/'stars-v5-isolated-10s.mp4'));values=[[] for _ in s.star_parts]
 while True:
  ok,f=cap.read()
  if not ok:break
  for j,(x,y) in enumerate(s.config['stars']['centers']):
   px,py=round(x*1280/s.w),round(y*720/s.h)
   values[j].append(float(f[py-2:py+3,px-2:px+3].mean(2).max()))
 cap.release()
 stars=[]
 for center,v in zip(s.config['stars']['centers'],values):
  assert len(v)==300
  spread=max(v)-min(v);assert spread>20,(center,spread)
  stars.append({'source_center':center,'decoded_peak_min':min(v),'decoded_peak_max':max(v),'range':spread,'position_fixed':True})
 streams={}
 for path in [H/'farpoint-station-v5-preview-60s.mp4',H/'farpoint-station-v5-three-loops-180s.mp4']:
  result=subprocess.run([s.config['ffmpeg'],'-hide_banner','-i',str(path)],capture_output=True,text=True)
  text=result.stderr
  assert 'Audio:' not in text and 'Video: h264' in text and '1280x720' in text and '30 fps' in text
  (H/(path.stem+'-streams.txt')).write_text(text,encoding='utf-8')
  streams[path.name]={'video_only':True,'bytes':path.stat().st_size,'sha256':digest(path)}
 save('coverage-star-validation.json',{'fingerprint':s.fingerprint(),'aurora_removed_from_active_layers':True,'regional_weather_changes':coverage,'encoded_star_ranges':stars,'streams':streams,'scope':'Coverage, quantization and stream checks, not artistic acceptance. Full-size temporal/decoded stills inspected; continuous playback unavailable.'})
 print('Coverage, encoded-star range and stream checks passed',flush=True)
if __name__=='__main__':main()
