"""Checks for sustained weather, protected structures and encoded local light states."""
from pathlib import Path
import json,subprocess,sys
import cv2,numpy as np
from render_junction_v2 import Junction,H,R,save,digest

def main():
 s=Junction();regions={'far_pass':('far_mist',[875,290,1090,358]),'left_cutting':('middle_mist',[610,324,850,379]),'right_cutting':('middle_mist',[1220,240,1460,320]),'horizon_clouds':('sky_clouds',[900,175,1125,242]),'upper_clouds':('sky_clouds',[690,105,1130,176])}
 coverage={}
 for name,(layer,(a,b,z,d)) in regions.items():
  mask=s.masks[layer][b:d,a:z]>.35;assert mask.sum()>100
  rows=[]
  for t in [0,8,20,30,40,48,55]:
   f=s.frame(t,layer)[b:d,a:z];g=s.frame(t+4,layer)[b:d,a:z]
   delta=abs(g.astype(float)-f.astype(float)).mean(2)[mask]
   rows.append({'time':t,'four_second_mean_change':float(delta.mean()),'fraction_over_one_level':float((delta>1).mean())})
  assert min(row['four_second_mean_change'] for row in rows)>.10,(name,rows)
  coverage[name]=rows
 fixed={'foreground_rails':[870,600,1660,935],'left_rock':[40,20,145,230],'cabin_wall':[40,320,155,510],'track_signal':[817,603,844,634],'parked_wagon_body':[776,485,809,524]}
 for t in [0,8.2,20,40,50,59+29/30]:
  f=s.frame(t)
  for name,(a,b,z,d) in fixed.items():
   assert np.array_equal(f[b:d,a:z],s.base[b:d,a:z]),(name,t)
 # Encoded full-scene cloud transport diagnostic at the horizon, not visual acceptance.
 p=H/'sky_clouds-v2-isolated-10s.mp4';cap=cv2.VideoCapture(str(p));ok,f=cap.read();assert ok
 cap.set(cv2.CAP_PROP_POS_FRAMES,240);ok,g=cap.read();assert ok;cap.release()
 crop=(int(910*1280/1672),int(170*720/941),int(1135*1280/1672),int(216*720/941))
 a,b,z,d=crop;gray=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY);other=cv2.cvtColor(g,cv2.COLOR_BGR2GRAY)
 patch=gray[b+4:d-4,a+12:z-28]
 area=other[b:d,a:z]
 match=cv2.matchTemplate(area,patch,cv2.TM_CCOEFF_NORMED)
 _,peak,_,pos=cv2.minMaxLoc(match)
 dx=pos[0]-12;dy=pos[1]-4
 assert dx>5 and abs(dy)<=4,(dx,dy,peak)
 lightstats={}
 cap=cv2.VideoCapture(str(H/'habitation-v2-isolated-10s.mp4'))
 data=[]
 for n in [0,99,174,248,264]:
  cap.set(cv2.CAP_PROP_POS_FRAMES,n);ok,f=cap.read();assert ok;data.append(f)
 cap.release()
 for name,xy in [('door_lamp',(405,348)),('yard_bay',(1156,431)),('hall_left',(937,396))]:
  x,y=xy;x=round(x*1280/1672);y=round(y*720/941)
  values=[float(f[y-1:y+2,x-1:x+2].mean()) for f in data]
  assert max(values)-min(values)>8,(name,values)
  lightstats[name]={'frame_indices':[0,99,174,248,264],'mean_levels':values}
 if '--preflight' in sys.argv:
  print('Coverage/structure/encoded isolated preflight passed; full delivery streams still pending',flush=True)
  return
 streams={}
 for name in ['empty-junction-v2-preview-60s.mp4','empty-junction-v2-three-loops-180s.mp4']:
  path=H/name;result=subprocess.run([s.config['ffmpeg'],'-hide_banner','-i',str(path)],capture_output=True,text=True)
  info=result.stderr
  assert 'Audio:' not in info and '1280x720' in info and '30 fps' in info and 'Video: h264' in info
  (H/(path.stem+'-streams.txt')).write_text(info,encoding='utf-8')
  streams[name]={'sha256':digest(path),'bytes':path.stat().st_size,'silent':True}
 save('coverage-delivery-validation.json',{'fingerprint':s.fingerprint(),'regions':coverage,'protected_regions':fixed,'protected_regions_sampled_exact':True,'encoded_cloud_translation_8s':{'dx':dx,'dy':dy,'match_correlation':peak,'scope':'Diagnostic only, not proof of visual readability'},'encoded_light_levels':lightstats,'streams':streams,'user_approved':False})
 print('Minute-wide coverage, protected structure, encoded transport/lights and streams passed',flush=True)
if __name__=='__main__':main()
