from pathlib import Path
import json, cv2, numpy as np
from render_saltline import Saltline, HERE
a=Saltline('scene-plan-v3.json');b=Saltline('scene-plan-v4.json')
m=b.layer_masks['far_dust'];rows=[]
for t in (0,2,4,6,8,10,11.9666666667):
 f=b.frame(t,'far_dust',True)
 rows.append({'time_seconds':t,'source_far_dust_mean_absolute_delta':float(np.abs(f[m].astype(float)-b.base[m]).mean()),'source_far_dust_unchanged_from_v3':bool(np.array_equal(a.frame(t,'far_dust',True),f))})
mask=cv2.resize(m.astype(np.uint8),(1280,720),interpolation=cv2.INTER_NEAREST)>0
cap1=cv2.VideoCapture(str(HERE/'saltline-dust-v3-combined-8s.mp4'));cap2=cv2.VideoCapture(str(HERE/'saltline-v4-combined-12s.mp4'))
diff=[]
for i in range(240):
 ok1,f1=cap1.read();ok2,f2=cap2.read();assert ok1 and ok2
 diff.append(float(np.abs(f1[mask].astype(float)-f2[mask]).mean()))
cap1.release();cap2.release()
report={'settings_unchanged':a.config['far_dust']==b.config['far_dust'],'mask_unchanged':bool(np.array_equal(a.masks['far_dust'],b.masks['far_dust'])),'samples':rows,'encoded_first_eight_seconds_far_region_mae_max':max(diff),'encoded_first_eight_seconds_far_region_mae_mean':float(np.mean(diff)),'inspection_scope':'Numeric region comparisons; not artistic visibility proof'}
(HERE/'v4-far-visibility-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
