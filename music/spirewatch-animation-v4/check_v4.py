from pathlib import Path
import sys,json,hashlib,subprocess,time
import numpy as np,cv2
from PIL import Image,ImageDraw
from render_spirewatch import Spirewatch,H,save,sha,byte,old
s=Spirewatch();times=[0,7,20,40,54]
retained=['clouds','mist','depth_mist','falls','spray','water','walkway','lamp']
code="""import json,hashlib
from render_spirewatch import Spirewatch
s=Spirewatch();layers=%r;times=%r
print(json.dumps({k:[hashlib.sha256(s.frame(t,k).tobytes()).hexdigest() for t in times] for k in layers}))
"""%(retained,times)
reference=json.loads(subprocess.check_output([sys.executable,'-c',code],cwd=H.parent/'spirewatch-animation-v3'))
for k in retained:
 assert [hashlib.sha256(s.frame(t,k).tobytes()).hexdigest() for t in times]==reference[k],k
print('Eight retained layers match v3 at five times',flush=True)
checks={}
for k,m in s.layer_masks.items():
 first=s.frame(0,k);assert np.array_equal(first,s.frame(60,k)),k
 seam=float(np.abs(s.frame(-1/30,k)[m].astype(float)-first[m]).mean())
 steps=[float(np.abs(s.frame(t+1/30,k)[m].astype(float)-s.frame(t,k)[m]).mean()) for t in [0,7,18,29,40,54,59.9]]
 assert seam<=max(steps)*1.1+.012,(k,seam,steps)
 checks[k]={'periodic_endpoint':True,'seam':seam,'sampled_max_step':max(steps),'pass':True}
 print('Layer checked',k,flush=True)
(H/'masks').mkdir(exist_ok=True)
for k,m in s.masks.items():cv2.imwrite(str(H/'masks'/f'{k}.png'),byte(m*255))
stills=[0,7,12,18,24,28.6,36,47,54.6,59+29/30]
for t in stills:Image.fromarray(s.frame(t)).save(H/f'review-{t:05.2f}.png')
# Native-resolution detail contact sheets for inspection, never animation inputs.
for label,box,tt in [('tower',(1190,20,1340,435),[3,7,12,18,39,47]),('monitor',(135,550,325,700),[4,10,18,28,38,50]),('bridge',(1000,530,1640,664),[10,13,28,31])]:
 w=box[2]-box[0];h=box[3]-box[1];sheet=Image.new('RGB',(w*len(tt),h+24));draw=ImageDraw.Draw(sheet)
 for i,t in enumerate(tt):sheet.paste(Image.fromarray(s.frame(t)).crop(box),(i*w,24));draw.text((i*w+5,5),f'{t}s',fill='white')
 sheet.save(H/f'{label}-temporal.png')
save('analytic-validation.json',{'pass':True,'fingerprint':s.fingerprint(),'layers':checks,'retained_v3_layers':retained,'retained_times':times,'retained_exact':True,'warm_groups':len(s.window_records),'warm_apertures':sum(len(x['apertures']) for x in s.window_records),'protected_pixels':'Asserted on every generated native frame','assistant_continuous_playback':False})
save('mapped-window-apertures.json',s.window_records)
print('Analytic checks and inspection stills complete',flush=True)
