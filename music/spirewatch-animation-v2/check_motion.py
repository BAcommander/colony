"""Targeted supporting evidence; none of these tests establish artistic acceptance."""
import json,sys
from pathlib import Path
import numpy as np,cv2
from PIL import Image,ImageDraw
from render_spirewatch import Spirewatch,H,save
s=Spirewatch();report={'fingerprint':s.fingerprint(),'continuous_playback':False}

# Track an actual waterfall-material patch, rather than the old random brightness field.
roi,mask,texture,level,x,y,c,speed=s.flow[0];a,b,z,d=roi
norm=[]
for t in [0,.2]:
 f=s.frame(t,'falls')[b:d,a:z].astype(np.float32);blend=mask[...,None]*.94
 # Divide out the fixed channel shading and feathered source contribution.
 f=(f-s.base[b:d,a:z]*(1-blend))/np.maximum(blend*level,.1)
 f=f[221-b:339-b,264-a:295-a].mean(2)
 norm.append(f)
corr=[]
for shift in range(1,21):
 a=norm[0][:-shift].ravel();b=norm[1][shift:].ravel();corr.append(float(np.corrcoef(a,b)[0,1]))
best=int(np.argmax(corr))+1
assert 4<=best<=15,(best,max(corr))
report['fall_texture']={'measured_downward_pixels_in_point_two_seconds':best,'correlation':max(corr),'scope':'material feature direction, not realism'}

# The light band must travel in both directions within mapped emitter strips.
def centroid(t,layer):
 d=np.maximum(s.frame(t,layer).astype(float)-s.base,0).mean(2)
 return [float((s.x*d).sum()/d.sum()),float((s.y*d).sum()/d.sum())]
up=[centroid(t,'tower')[1] for t in [4,7,10]];down=[centroid(t,'tower')[1] for t in [28,32,37]]
assert up[0]>up[1]>up[2] and down[0]<down[1]<down[2]
report['tower']={'up_centroid_y':up,'down_centroid_y':down,'emission_regions':s.config['tower']['emitter_regions'],'direction_checks':True}
transit=[centroid(t,'transit')[0] for t in [5,8,11,14]]
assert all(a<b for a,b in zip(transit,transit[1:]))
report['transit']={'centroid_x':transit,'times':[5,8,11,14],'direction_check':True}

# Check source-detail retention on representative basin interiors.
m=cv2.erode(np.uint8(s.masks['water']>.8),np.ones((5,5),np.uint8))>0
def detail(im):
 g=im.mean(2).astype(np.float32);return float(np.abs(g-cv2.GaussianBlur(g,(0,0),1.1))[m].mean())
base=detail(s.base);ratios=[detail(s.frame(t,'water'))/base for t in [0,7,20,40,56]]
assert min(ratios)>.85,ratios
report['water_detail']={'source_relative_high_frequency_ratios':ratios,'times':[0,7,20,40,56],'minimum_gate':.85,'scope':'retained fine detail, not perceptual water quality'}

coverage={}
for layer in ['clouds','mist','depth_mist','falls','water','screen','city_glow']:
 mask=s.layer_masks[layer];vals=[]
 for t in [0,20,40,52]:
  d=np.abs(s.frame(t+2,layer).astype(float)-s.frame(t,layer).astype(float))[mask]
  vals.append(float(d.mean()))
 assert all(v>0 for v in vals),(layer,vals)
 coverage[layer]=vals
report['two_second_motion_at_0_20_40_52']=coverage
report['lightning_events']=[{'time':c['time'],'peak_effect':float(s.flash_value(c['time']+.22,c))} for c in s.config['lightning']['events']]
report['protection']='Asserted for every sampled and encoded native frame; compression/resizing can change pixels.'
report['user_motion_approved']=False
save('targeted-validation.json',report)
print(json.dumps({k:v for k,v in report.items() if k in ('fall_texture','tower','water_detail')},indent=2),flush=True)
