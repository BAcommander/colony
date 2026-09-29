from pathlib import Path
import json, hashlib, shutil
import numpy as np, cv2
from PIL import Image
R=Path('G:/AI/colony'); p=R/'final/04-floodplain-keeper'; a=p/'animation-v2'; a.mkdir(exist_ok=False); (a/'masks').mkdir()
c=json.loads((p/'animation-v1/scene-plan-v1.json').read_text());c['version']='v2';c['status']='V1 water/clouds liked; added lighting flicker pending user review';c['output_dir']='exports/04-floodplain-keeper/animation-v2'
for k,v in c['masks'].items(): c['masks'][k]='../animation-v1/'+v
c['lights'][0]['flickers']=[{'start':1.2,'hold':.24,'transition':.07,'depth':.48},{'start':1.58,'hold':.32,'transition':.10,'depth':.32},{'start':10.4,'hold':.28,'transition':.08,'depth':.4}]
c['lights'][1]['flickers']=[{'start':5.1,'hold':.3,'transition':.09,'depth':.48},{'start':5.56,'hold':.22,'transition':.07,'depth':.3},{'start':18.3,'hold':.35,'transition':.10,'depth':.42}]
c['lamp']={'flickers':[{'start':6.2,'hold':.34,'transition':.10,'depth':.28},{'start':6.72,'hold':.24,'transition':.08,'depth':.19},{'start':15.25,'hold':.42,'transition':.12,'depth':.24}],'description':'Brief desk-lamp dips with coupled warm wall and desk spill; steady between events.'}
base=np.array(Image.open(p/'artwork-v2-animation.png').convert('RGB'));h,w=base.shape[:2]
def poly(points,feather):
 m=np.zeros((h,w),np.uint8);cv2.fillPoly(m,[np.array(points,np.int32)],255);d=cv2.distanceTransform(m,cv2.DIST_L2,5);v=np.clip(d/feather,0,1);return v*v*(3-2*v)
core=poly([[1355,380],[1368,383],[1430,399],[1434,405],[1418,404],[1360,387]],1.5)
wall=poly([[1373,393],[1423,405],[1492,475],[1505,505],[1450,509],[1394,520],[1369,508]],25)
desk=poly([[1235,579],[1388,551],[1468,574],[1548,594],[1539,612],[1494,618],[1455,613],[1380,600],[1288,611],[1201,614],[1198,596]],24)
warm=np.clip((base[:,:,0].astype(float)-base[:,:,2].astype(float))/75,0,1)
lamp=np.maximum(core,np.maximum(wall*.5,desk*.55)*warm)
cv2.imwrite(str(a/'masks/lamp.png'),np.uint8(np.rint(lamp*255)))
active=cv2.imread(str(p/'animation-v1/masks/active.png'),0)>0;active|=lamp>=.5/255
cv2.imwrite(str(a/'masks/active.png'),np.uint8(active)*255)
c['masks']['lamp']='masks/lamp.png';c['masks']['active']='masks/active.png';c['inspection']='V2 adds localized fixture flickers; unchanged v1 cloud/water settings and masks.'
(a/'scene-plan-v2.json').write_text(json.dumps(c,indent=2)+'\n')
Image.fromarray(np.uint8(base*(1-lamp[:,:,None]*.45)+np.array([0,255,150])*lamp[:,:,None]*.45)).save(a/'lamp-mask-review.png')
print('V2 lighting masks and config prepared; use scripts/render_floodplain.py')
