import json,hashlib,importlib.util
import numpy as np,cv2
from PIL import Image,ImageDraw
from render_spirewatch import Spirewatch,H,save,sha,byte,old
s=Spirewatch();checks={}
for k,m in s.layer_masks.items():
 a=s.frame(0,k);assert np.array_equal(a,s.frame(60,k)),k
 seam=float(np.abs(s.frame(-1/30,k)[m].astype(float)-a[m]).mean())
 tt=[0,1,4,6.6,12,18.4,24,30.6,32.15,40,43.2,48,55,59.9]
 steps=[float(np.abs(s.frame(t+1/30,k)[m].astype(float)-s.frame(t,k)[m]).mean()) for t in tt]
 assert seam<=max(steps)*1.1+.012,(k,seam,steps)
 checks[k]={'periodic':True,'seam_mae':seam,'sampled_step_max':max(steps),'pass':True};print('Checked',k,flush=True)
assert not s.masks['tower'][425:].any() and not s.masks['tower_glow'][425:].any()
assert len({hashlib.sha256(s.frame(t).tobytes()).hexdigest() for t in [0,20,40]})==3
spec=importlib.util.spec_from_file_location('prior_v6',H.parent/'spirewatch-animation-v6/render_spirewatch.py');previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous);p=previous.Spirewatch()
retained={}
for k in ['clouds','water','falls','districts','windows','transit','reflections','screen','lamp','screen_spill']:
 for t in [0,7,20,32.2,40,54.6]:assert np.array_equal(s.frame(t,k),p.frame(t,k)),(k,t)
 retained[k]={'exact_match_to_v6_at':[0,7,20,32.2,40,54.6]}
old.H=H
(H/'masks').mkdir(exist_ok=True)
for k,m in s.masks.items():cv2.imwrite(str(H/'masks'/f'{k}.png'),byte(m*255))
for t in [0,4,8,12,24,28.6,32.2,40,48,54.6,59+29/30]:Image.fromarray(s.frame(t)).save(H/f'review-{t:05.2f}.png')
save('mapped-window-apertures.json',s.window_records)
save('analytic-validation.json',{'pass':True,'fingerprint':s.fingerprint(),'layers':checks,'retained_layers':retained,'distinct_0_20_40':True,'protected_pixels':'Every native output asserts unchanged source outside active masks','warm_groups':len(s.window_records),'warm_apertures':sum(len(x['apertures']) for x in s.window_records),'tower_and_glow_zero_below_source_y425':True,'assistant_continuous_playback':False})
print('V7 analytical and retained layer checks passed',flush=True)
