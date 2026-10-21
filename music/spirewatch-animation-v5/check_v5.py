import json,hashlib,subprocess,sys
import numpy as np,cv2
from PIL import Image,ImageDraw
from render_spirewatch import Spirewatch,H,save,sha,byte
s=Spirewatch();checks={}
for k,m in s.layer_masks.items():
 a=s.frame(0,k);assert np.array_equal(a,s.frame(60,k)),k
 seam=float(np.abs(s.frame(-1/30,k)[m].astype(float)-a[m]).mean())
 tt=[0,7,18,28.5,32.15,40,54.5,59.9]
 steps=[float(np.abs(s.frame(t+1/30,k)[m].astype(float)-s.frame(t,k)[m]).mean()) for t in tt]
 assert seam<=max(steps)*1.1+.012,(k,seam,steps)
 checks[k]={'periodic':True,'seam_mae':seam,'sampled_step_max':max(steps),'pass':True}
 print('Checked',k,flush=True)
assert len({sha_bytes for sha_bytes in [hashlib.sha256(s.frame(t).tobytes()).hexdigest() for t in [0,20,40]]})==3
(H/'masks').mkdir(exist_ok=True)
for k,m in s.masks.items():cv2.imwrite(str(H/'masks'/f'{k}.png'),byte(m*255))
for t in [0,7,12,18,24,28.6,32.2,40,47,54.6,59+29/30]:Image.fromarray(s.frame(t)).save(H/f'review-{t:05.2f}.png')
for label,box,tt in [('tower',(1220,25,1340,460),[3,8,13,19,40,48]),('screen',(130,550,320,704),[4,10,18,28,38,50]),('bridge',(1000,610,1650,748),[12,16,28,32])]:
 w,h=box[2]-box[0],box[3]-box[1];sheet=Image.new('RGB',(w*len(tt),h+24));draw=ImageDraw.Draw(sheet)
 for i,t in enumerate(tt):sheet.paste(Image.fromarray(s.frame(t)).crop(box),(i*w,24));draw.text((i*w+4,5),f'{t}s',fill='white')
 sheet.save(H/f'{label}-temporal.png')
thumb=np.array(Image.open(H.parent/'spirewatch-animation-v4/thumbnail-v1.png').convert('RGB'))
old=np.array(Image.open(H.parent/'digital-city-concepts-v1/01-spirewatch-v2-cleanup.png').convert('RGB'))
regions={'city_and_bridge':[650,450,1660,750],'room':[0,530,480,790],'main_spire':[1245,245,1335,450]}
brightness={}
for name,(a,b,z,d) in regions.items():
 calc=lambda ar:float((ar[b:d,a:z].astype(float)*np.array([.2126,.7152,.0722])).sum(2).mean())
 brightness[name]={'thumbnail_mean_luma':calc(thumb),'new_source_mean_luma':calc(s.base),'old_source_mean_luma':calc(old),'sampled_animation_mean_luma':[calc(s.frame(t)) for t in [0,12,24,40,56]]}
 assert .85<calc(s.base)/calc(thumb)<1.2,(name,brightness[name])
save('source-comparison.json',{'same_coordinate_regions':regions,'luma_values':brightness,'interpretation':'Descriptive brightness comparison, not a quality score. Source/artwork geometry differs from the older plate. Text regions excluded.','thumbnail_sha256':sha(H.parent/'spirewatch-animation-v4/thumbnail-v1.png'),'new_source_sha256':sha(H/'artwork-v5.png'),'visual_review':'Assistant inspected same-size clean plate and thumbnail; new plate retains bright city, bridge, water and room. Fine generated details may differ. User approval not inferred.'})
save('mapped-window-apertures.json',s.window_records)
save('analytic-validation.json',{'pass':True,'fingerprint':s.fingerprint(),'layers':checks,'distinct_0_20_40':True,'protected_pixels':'Every native output asserts unchanged source outside its active masks','warm_groups':len(s.window_records),'warm_apertures':sum(len(x['apertures']) for x in s.window_records),'masks_newly_mapped':True,'assistant_continuous_playback':False})
print('V5 analytical checks, source comparison and samples complete',flush=True)
