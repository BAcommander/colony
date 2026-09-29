from pathlib import Path
import json,hashlib,sys
import cv2,numpy as np
from PIL import Image,ImageDraw

ROOT=Path('G:/AI/colony');OUT=ROOT/'final/04-floodplain-keeper/animation-v1'
OUT.mkdir(exist_ok=True);(OUT/'masks').mkdir(exist_ok=True)
source=ROOT/'final/04-floodplain-keeper/artwork-v2-animation.png'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='1e9c4da5a9c01393c9e2f8105ed7023b5bbbaa58f83d613b70a32184fa676c26'
base=np.array(Image.open(source).convert('RGB'));h,w=base.shape[:2]
def masks(name,polygons,exclusions=(),feather=4):
 m=np.zeros((h,w),np.uint8)
 for points in polygons:cv2.fillPoly(m,[np.array(points,np.int32)],255)
 for points in exclusions:cv2.fillPoly(m,[np.array(points,np.int32)],0)
 dist=cv2.distanceTransform(m,cv2.DIST_L2,5)
 v=np.clip((dist-1)/feather,0,1);v=v*v*(3-2*v)
 cv2.imwrite(str(OUT/'masks'/f'{name}.png'),np.uint8(np.rint(v*255)))
 return v
sky=masks('sky',[
 [[469,24],[1286,43],[1285,179],[1197,184],[1165,193],[1110,194],[1080,201],[1068,215],[1039,220],[1028,233],[970,235],[950,239],[893,238],[877,227],[835,226],[819,230],[802,245],[789,246],[777,237],[763,230],[750,223],[744,211],[696,206],[628,207],[578,205],[526,207],[469,207]],
 [[30,3],[178,20],[178,195],[133,197],[105,197],[75,202],[30,200]]
 ],[
 [[662,135],[697,135],[697,250],[662,250]],
 [[1116,177],[1126,177],[1126,245],[1116,245]]
 ],7)
yy,xx=np.mgrid[:h,:w];radius=np.sqrt(((xx-1081)/1.0)**2+((yy-111)/1.0)**2)
v=np.clip((radius-37)/9,0,1);sky*=v*v*(3-2*v)
cv2.imwrite(str(OUT/'masks/sky.png'),np.uint8(np.rint(sky*255)))
water_polygons=[
 [[838,399],[895,400],[948,403],[979,412],[1025,420],[1100,428],[1150,439],[1199,453],[1213,457],[1207,462],[1086,470],[965,475],[942,472],[930,459],[918,443],[910,435],[889,429],[850,427],[838,421]],
 [[775,387],[800,386],[828,388],[828,396],[813,403],[785,401]],
 [[497,350],[551,349],[580,351],[591,355],[579,361],[550,361],[529,357],[499,358]],
 [[735,349],[772,349],[782,354],[782,364],[773,371],[751,370],[739,365]],
 [[948,447],[951,470],[945,471],[941,453]],
 [[42,356],[74,359],[88,361],[101,359],[104,367],[91,378],[62,375],[42,372]]
]
water=masks('water',water_polygons,feather=4)
screen=masks('screen',[[[942,518],[989,515],[992,562],[945,565]]],feather=2)
lights=masks('lights',[[[583,290],[594,290],[594,302],[583,302]],[[766,294],[773,294],[773,304],[766,304]]],feather=1)
beacon=np.exp(-((xx-679)**2+(yy-147)**2)/5)*np.clip((base[:,:,0].astype(float)-base[:,:,1]*1.12)/40,0,1)
beacon[((xx-679)**2+(yy-147)**2)>12]=0
cv2.imwrite(str(OUT/'masks/beacon.png'),np.uint8(np.rint(beacon*255)))
active=(sky+water+screen+lights+beacon)>0
cv2.imwrite(str(OUT/'masks/active.png'),np.uint8(active)*255)
overlay=base.astype(float)
for mask,col in [(sky,[70,130,255]),(water,[0,255,180]),(screen,[255,0,255]),(lights,[255,200,0]),(beacon,[255,60,60])]:
 overlay=overlay*(1-mask[...,None]*.4)+np.array(col)*mask[...,None]*.4
Image.fromarray(np.uint8(overlay)).save(OUT/'mask-review.png')
config={
 'scene_name':'Floodplain Keeper','version':'v1','status':'first motion candidate; user approval pending',
 'source':{'path':source.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'dimensions':[w,h],'selection':'Prepared v2 chosen for first animation trial under user instruction to try v1; no standalone art approval inferred.'},
 'duration':20,'fps':30,'preview_size':[1280,720],'final_size':[3840,2160],
 'output_dir':'exports/04-floodplain-keeper/animation-v1','ffmpeg':'C:/Program Files/ShareX/ffmpeg.exe',
 'sky':{'speed':2.0,'regions':[[28,0,185,215],[465,18,1295,250]],'feather':7,'source_clean_sigma':1.2,'exclusions':[{'ellipse':[1081,111,40,40]},{'rectangle':[663,136,696,249]},{'rectangle':[1117,178,1125,249]}]},
 'water':{'roi':[28,345,1220,478],'seed':814,'components':24,'time_scale':.09,'specular_strength':9,'wavelength_range':[.65,5.0],'reflection_sigma_x':1.2,'reflection_sigma_y':.6,'displacement_scale':.23,'reflection_contrast':.08,'highlight_roughness':.32,'sampling_filter_pixels':.85,'edge_damping_pixels':9,'loop_seconds':20,'perspective_horizon_y':305,'perspective_distance_scale':1500,'perspective_center_x':840,'perspective_lateral_scale':400},
 'lights':[{'roi':[581,288,596,304],'start':3,'hold':5,'transition':1,'floor':.2},{'roi':[764,292,775,306],'start':12,'hold':5,'transition':1.2,'floor':.25}],
 'screen':{'roi':[939,513,995,568],'period':20,'strength':13},
 'beacon':{'roi':[674,143,684,151],'period':10},
 'masks':{name:f'masks/{name}.png' for name in ['sky','water','screen','lights','beacon','active']},
 'protection':'Camera, furniture, glass residual detail, geometry, reeds, waterline, moon and fixed terrain. No foreground rain, steam or added objects.',
 'inspection':'Source still and coordinate-grid crops inspected; masks revised against this exact plate; motion pending.',
 'method':'Shared ReflectionSurface with scene-specific perspective and recalculated wave phases; Basalt-style overlapping local source-cloud lifetimes. No full-frame dissolve or reversed motion.',
}
(OUT/'scene-plan-v1.json').write_text(json.dumps(config,indent=2)+'\n')
print('Prepared',OUT,'active pixels',int(active.sum()))
