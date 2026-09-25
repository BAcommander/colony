"""Decode review clips and compare the actual seam with normal frame steps."""
import argparse,json
from pathlib import Path
import cv2,numpy as np
from render_basalt import Basalt

def main():
 p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--review',required=True);a=p.parse_args()
 b=Basalt(a.config);root=Path(__file__).resolve().parents[1];path=Path(a.review);r=json.loads(path.read_text());out={}
 for item in r['clips']:
  name=item['layer'];mask=b.active if name=='combined' else b.layer_masks[name]
  mask=cv2.resize(mask.astype(np.uint8),(1280,720),interpolation=cv2.INTER_NEAREST)>0
  cap=cv2.VideoCapture(str(root/item['path']));first=None;prev=None;deltas=[];count=0
  while True:
   ok,f=cap.read()
   if not ok:break
   f=f[mask].astype(np.float32)
   if first is None:first=f
   if prev is not None:deltas.append(float(np.abs(f-prev).mean()))
   prev=f;count+=1
  fps=cap.get(cv2.CAP_PROP_FPS);cap.release()
  assert count==600 and fps==30,(name,count,fps)
  seam=float(np.abs(prev-first).mean());maximum=max(deltas)
  assert seam<=maximum*1.1+.01,(name,seam,maximum)
  out[name]={'decoded_frames':count,'fps':fps,'seam_mae':seam,'ordinary_max_mae':maximum,'ordinary_median_mae':float(np.median(deltas)),'seam_within_ordinary_range_tolerance':True}
 out['inspection']='Decoded-frame and analytic checks plus sampled still inspection; user playback judgment pending. No continuous playback review claimed.'
 path.with_name('encoded-seam-checks.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
if __name__=='__main__':main()
