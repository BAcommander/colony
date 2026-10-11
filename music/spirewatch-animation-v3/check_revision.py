"""Bounded checks for this lighting revision and retained v2 environmental fields."""
import json,hashlib,subprocess,sys
import numpy as np,cv2
from PIL import Image
from render_spirewatch import Spirewatch,H,save,sha,byte
s=Spirewatch();times=[0,8,20,40,52]
retained=['clouds','mist','depth_mist','falls','spray','water','transit','screen','screen_spill']
code="""import json,hashlib
from render_spirewatch import Spirewatch
s=Spirewatch();layers=%r;times=%r
print(json.dumps({k:[hashlib.sha256(s.frame(t,k).tobytes()).hexdigest() for t in times] for k in layers}))
"""%(retained,times)
reference=json.loads(subprocess.check_output([sys.executable,'-c',code],cwd=H.parent/'spirewatch-animation-v2'))
for layer in retained:
 hashes=[hashlib.sha256(s.frame(t,layer).tobytes()).hexdigest() for t in times]
 assert hashes==reference[layer],layer
print('Nine retained layers match v2 at five times',flush=True)
checks={}
for layer in s.layer_masks:
 m=s.layer_masks[layer];a=s.frame(0,layer);b=s.frame(60,layer)
 assert np.array_equal(a,b),layer
 seam=float(np.abs(s.frame(-1/30,layer)[m].astype(float)-a[m]).mean())
 tt=[0,4,9.55,14.3,31.8,34.55,51.2,59.9]
 ordinary=[float(np.abs(s.frame(t+1/30,layer)[m].astype(float)-s.frame(t,layer)[m]).mean()) for t in tt]
 assert seam<=max(ordinary)*1.1+.012,(layer,seam,ordinary)
 checks[layer]={'periodic':True,'seam':seam,'ordinary_max_sampled':max(ordinary),'pass':True}
(H/'masks').mkdir(exist_ok=True)
for name,m in s.masks.items():cv2.imwrite(str(H/'masks'/f'{name}.png'),byte(m*255))
for t in [0,4,8,9.62,20,28,32,34.62,40,48,52.62,56,59+29/30]:Image.fromarray(s.frame(t)).save(H/f'sample-{t:06.2f}s.png')
Image.fromarray(s.frame(0,'windows',True)).save(H/'windows-forced-dim.png')
save('mapped-window-apertures.json',s.window_records)
# A rectangular lower-left crop contains exterior water through the window.
# Test mapped interior surfaces and the opaque bottom foreground instead.
room=(s.masks['lamp']>0)|(s.masks['screen']>0)
room[880:,:]=True
assert np.array_equal(s.frame(9.62,'storm')[room],s.base[room])
save('analytic-validation.json',{'fingerprint':s.fingerprint(),'layers':checks,'retained_v2_layers':retained,'retained_times':times,'retained_layers_exact':True,'warm_groups':len(s.window_records),'warm_apertures':sum(len(x['apertures']) for x in s.window_records),'storm_room_protected':True,'native_source_protection':'Asserted on every generated frame','continuous_playback':False,'pass':True})
print('Revision checks and current samples passed',flush=True)
