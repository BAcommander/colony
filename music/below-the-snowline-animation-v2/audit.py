from pathlib import Path
import sys,importlib.util
from render import Scene,np,Image,H,save
p=H.parent/'snowline-animation-v1/render.py'
if not p.exists():p=H.parent/'below-the-snowline-animation-v1/render.py'
spec=importlib.util.spec_from_file_location('original_v1',p);old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
a=old.Scene();b=Scene();checks={}
for n in ['far_powder','ravine_mist','ledge_spindrift','windows','terminals','coffee_steam','snow']:
 for t in [0,4,8,12,16]:assert np.array_equal(a.frame(t,n),b.frame(t,n)),('Unintended change',n,t)
 checks[n]='Exact isolated match at five phases'
sheet=Image.new('RGB',(1040,520));r=(770,145,900,275)
for i,t in enumerate([0,4,8,12]):
 for row,s in enumerate([a,b]):sheet.paste(Image.fromarray(s.frame(t,'sky')).crop(r).resize((260,260)),(260*i,260*row))
sheet.save(H/'dish-before-after.png')
save('regression-validation.json',{'fingerprint':b.fingerprint(),'retained_layers':checks,'old_valid_cloud_source_pixels_now_excluded':int(np.count_nonzero(a.skyvalid & b.guard)),'same_source':np.array_equal(a.base,b.base),'before_after':'dish-before-after.png: v1 top, v2 bottom; 0/4/8/12 seconds','inspection':'Temporal still comparison, not continuous playback'})
print('Unchanged-layer comparisons and dish regression ready',flush=True)
