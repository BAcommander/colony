"""Verify v2 retention, new motion coverage, masks and complete silent delivery."""
import sys,json,subprocess
import cv2,numpy as np
from PIL import Image
from render_junction_v3 import Junction,v2,H,R,save,digest,byte
def main():
 s=Junction();old=v2.Junction()
 prior=json.loads((H.parent/'empty-junction-animation-v2/delivery-v2.json').read_text(encoding='utf-8'))
 for p,h in prior['fingerprint']['files'].items():assert digest(R/p)==h,p
 new=np.logical_or.reduce([s.layer_masks[n] for n in s.config['new_motion']])
 times=[0,4,8.34,20,40,50,59+29/30]
 for t in times:
  assert np.array_equal(s.frame(t)[~new],old.frame(t)[~new]),t
  for layer in ['sky_clouds','far_mist','middle_mist','habitation']:
   assert np.array_equal(s.frame(t,layer),old.frame(t,layer)),(layer,t)
 coverage={}
 for name in s.config['new_motion']:
  mask=s.masks[name]>.30;rows=[]
  for t in [0,8,20,30,40,48,55]:
   a=s.frame(t,name);b=s.frame(t+2,name)
   value=float(np.abs(a.astype(float)-b.astype(float))[mask].mean())
   assert value>.10,(name,t,value)
   rows.append({'time':t,'two_second_mean_delta':value})
  coverage[name]=rows
 overlay=s.base.astype(np.float32)
 for name,color in [('terrain_flow',[80,220,200]),('yard_powder',[230,160,70]),('cabin_exhaust',[180,100,255])]:
  a=s.masks[name][...,None]*.5;overlay=overlay*(1-a)+np.float32(color)*a
 Image.fromarray(byte(overlay)).save(H/'new-motion-mask-overlay.png')
 encoded={}
 for name in s.config['new_motion']:
  path=H/f'{name}-v3-isolated-10s.mp4';cap=cv2.VideoCapture(str(path));frames=[]
  for n in [0,60,120,240]:
   cap.set(cv2.CAP_PROP_POS_FRAMES,n);ok,f=cap.read();assert ok;frames.append(f)
   cv2.imwrite(str(H/f'{name}-decoded-{n:03d}.png'),f)
  cap.release();mask=cv2.resize(np.uint8(s.layer_masks[name]),(1280,720),interpolation=cv2.INTER_NEAREST)
  changes=[sum(cv2.mean(cv2.absdiff(frames[0],f),mask=mask)[:3])/3 for f in frames[1:]]
  assert min(changes)>.10,(name,changes)
  encoded[name]={'frame0_to_2_4_8_second_mae':changes,'scope':'Implementation evidence, not artistic acceptance'}
 if '--preflight' in sys.argv:
  print('V2 retention, new motion coverage and isolated encoded checks passed',flush=True);return
 streams={}
 for name in ['empty-junction-v3-preview-60s.mp4','empty-junction-v3-three-loops-180s.mp4']:
  p=H/name;r=subprocess.run([s.config['ffmpeg'],'-hide_banner','-i',str(p)],capture_output=True,text=True)
  assert 'Audio:' not in r.stderr and '1280x720' in r.stderr and '30 fps' in r.stderr
  (H/(p.stem+'-streams.txt')).write_text(r.stderr,encoding='utf-8')
  streams[name]={'sha256':digest(p),'bytes':p.stat().st_size,'silent':True}
 save('coverage-delivery-validation.json',{'fingerprint':s.fingerprint(),'retained_v2_layers':['sky_clouds','far_mist','middle_mist','habitation'],'sample_times':times,'outside_new_masks_exact_v2':True,'v2_dependencies_unchanged':True,'coverage':coverage,'encoded_isolated':encoded,'streams':streams,'user_approved':False})
 print('V2 retention, minute coverage, encoded new motion and streams passed',flush=True)
if __name__=='__main__':main()
