"""Retained-effect regression and actual-strength lighting review frames."""
import json
import cv2,numpy as np
from PIL import Image
from render_junction_v2 import Junction,previous,H,R,save,digest,byte

def main():
 s=Junction();old=previous.Junction()
 old_record=json.loads((H.parent/'empty-junction-animation-v1/delivery-v1.json').read_text(encoding='utf-8'))
 for path,value in old_record['fingerprint']['files'].items():assert digest(R/path)==value,path
 assert np.array_equal(s.masks['sky_clouds'],old.masks['sky_clouds'])
 retained=['cabin_window','roof_amber','yard_left','yard_bay','path_lamp']
 for name in retained:
  key='light_'+name
  for t in [0,3.8,7,14.4,20,24,30,40.8,50,54.2,59.9]:
   assert np.array_equal(s.frame(t,key),old.frame(t,key)),(name,t)
 rows=[]
 for t in [0,8.34,8.81,47.62]:
  f=s.frame(t,'habitation')
  Image.fromarray(cv2.resize(f,(1280,720),interpolation=cv2.INTER_AREA)).save(H/f'light-state-{t:05.2f}s.png')
  def level(x,y):return float(f[y-2:y+3,x-2:x+3].mean())
  # y=735 is the illuminated tread; y=725 is an unlit dark riser.
  rows.append({'time':t,'core':level(405,348),'door_spill':level(406,378),'step_spill':level(418,735)})
 assert all(rows[0][k]>rows[1][k] for k in ['core','door_spill','step_spill'])
 # A restrained optional shading study. It is deliberately absent from the renderer.
 f=s.frame(20).astype(np.float32);x,y=s.x,s.y
 mask=np.exp(-.5*((x-878)/65)**2-.5*((y-282)/38)**2)
 mask*=s.poly([[[803,254],[845,224],[887,256],[921,285],[906,318],[856,312]]],8)
 f*=1-mask[...,None]*.045
 Image.fromarray(cv2.resize(byte(f),(1280,720),interpolation=cv2.INTER_AREA)).save(H/'twilight-shading-study-maximum.png')
 save('retained-and-light-validation.json',{'fingerprint':s.fingerprint(),'v1_dependencies_unchanged':True,'retained_light_layers_exact':retained,'sample_times':[0,3.8,7,14.4,20,24,30,40.8,50,54.2,59.9],'sky_occlusion_mask_exact_v1':True,'actual_light_states':rows,'twilight_study':'Optional 4.5-percent local shade study; not part of delivered renderer. Visual review decides inclusion, not numeric checks.','user_approved':False})
 print('V1 provenance, retained light regressions and core/spill states passed',flush=True)
if __name__=='__main__':main()
