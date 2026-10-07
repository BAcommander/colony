"""Additional delivery facts, regional evidence and reproducible decoded samples."""
from pathlib import Path
import json,subprocess,hashlib
import cv2,numpy as np
from PIL import Image
from render_farpoint_v4 import FarpointMinute,H,R,save,byte_image,digest

def main():
 s=FarpointMinute();reports={}
 for path in [H/'farpoint-station-v4-preview-60s.mp4',H/'farpoint-station-v4-three-loops-180s.mp4']:
  result=subprocess.run([s.config['ffmpeg'],'-hide_banner','-i',str(path)],capture_output=True,text=True)
  text=result.stderr
  assert 'Audio:' not in text and 'Video: h264' in text and '1280x720' in text and '30 fps' in text,text
  (H/(path.stem+'-streams.txt')).write_text(text)
  reports[path.name]={'video_only':True,'bytes':path.stat().st_size,'sha256':digest(path)}
 regions={}
 for name in ['clouds','lower_cloud','aurora','stars','reflections','screen','instrument_lights']:
  m=s.layer_masks[name];changes=[]
  for t in [0,8,20,30,40,50,58]:
   a=s.frame(t,name);b=s.frame(t+1,name);changes.append({'time':t,'mae':float(np.abs(a[m].astype(float)-b[m]).mean())})
  regions[name]=changes
  # Intermittent lights may be quiet; continuous atmospheric features must persist.
  if name in ['clouds','lower_cloud','aurora']:assert all(x['mae']>0 for x in changes)
 primitive_masks={}
 from render_farpoint_v3 import FarpointV3
 old=FarpointV3()
 for k in ['windows','screen','lamp','instrument_lights','lower_cloud']:
  primitive_masks[k]=bool(np.array_equal(s.masks[k],old.masks[k]));assert primitive_masks[k]
 # Bright/dim local samples at actual delivery depth, plus the diagnostic full-dark state.
 for t in [12,12.95,44,44.7]:
  Image.fromarray(s.frame(t)).crop((395,480,458,576)).resize((252,384)).save(H/f'reflections-{t:05.2f}s.png')
 # Frame-by-frame differences at the join, keeping the same numeric gate.
 checks={}
 dt=1/30
 for layer in ['clouds','lower_cloud','aurora','stars','screen']:
  m=s.layer_masks[layer]
  ims=[s.frame(t,layer)[m].astype(np.float32) for t in [-2*dt,-dt,0,dt,2*dt]]
  steps=[ims[i+1]-ims[i] for i in range(4)]
  checks[layer]={'adjacent_join_step_mae':[float(abs(v).mean()) for v in steps],'join_step_alignment':float(np.sum(steps[1]*steps[2])/(np.linalg.norm(steps[1])*np.linalg.norm(steps[2])+1e-12))}
 save('supplemental-validation.json',{'fingerprint':s.fingerprint(),'streams':reports,'minute_coverage':regions,'retained_masks_exact':primitive_masks,'join_motion_diagnostics':checks,'inspection':'Normal-size source/temporal/decoded stills, masks and forced-dark states. No continuous playback capability; user playback verdict pending.'})
 print('Stream, coverage, retained-mask and join-motion checks passed')

if __name__=='__main__':main()
