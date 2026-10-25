"""Freeze the built-in image edit as a local, confined sky patch; map this source."""
from pathlib import Path
import sys,json,hashlib,shutil
sys.dont_write_bytecode=True
sys.path.insert(0,r'C:\AI\ComfyUI\venv\Lib\site-packages')
import cv2,numpy as np
from PIL import Image
H=Path(__file__).resolve().parent
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,a):Image.fromarray(a).save(H/p)
def smooth(v):v=np.clip(v,0,1);return v*v*(3-2*v)
def main():
 if (H/'scene-plan-v1.json').exists():raise RuntimeError('Preparation is already frozen. Preserve this package; make a new version for another artwork edit.')
 original=Path(r'G:\AI\colony\final\12-deepwell-station\artwork-v2.png')
 generated=Path(r'C:\Users\jazzs\.codex\generated_images\01a15eed-ec00-7593-8e11-a0c451e74a5e\exec-b8a2c0ae-7430-412e-9461-455d1a95dc38.png')
 for p,n in [(original,'artwork-original-v2.png'),(generated,'planet-imagegen-original.png')]:
  if not (H/n).exists():shutil.copy2(p,H/n)
 base=np.array(Image.open(original).convert('RGB'));gen=np.array(Image.open(generated).convert('RGB'))
 assert base.shape==gen.shape==(941,1672,3)
 yy,xx=np.mgrid[:941,:1672];box=(1010,41,1284,237);a,b,z,d=box
 mask=smooth(np.minimum.reduce([(xx-a)/23,(z-xx)/23,(yy-b)/20,(d-yy)/20]))
 # Fit only an additive low-order sky difference on the perimeter. The planet
 # and its veiling clouds do not contribute to this colour match.
 ring=(mask>0)&(mask<.7);X=np.stack([np.ones(ring.sum()),(xx[ring]-1147)/140,(yy[ring]-139)/100],axis=1)
 plane=np.stack([np.ones_like(xx),(xx-1147)/140,(yy-139)/100],axis=2)
 coeff=np.linalg.lstsq(X,(base.astype(float)-gen)[ring],rcond=None)[0]
 correction=np.clip(plane@coeff,-10,10)
 matched=np.clip(gen.astype(float)+correction,0,255)
 result=np.uint8(np.rint(base*(1-mask[...,None])+matched*mask[...,None]))
 assert np.array_equal(result[mask==0],base[mask==0])
 save('artwork-planet-v1.png',result);save('planet-edit-mask.png',np.uint8(np.rint(mask*255)))
 report={'tool':'built-in image_gen edit','original_source':str(original),'original_sha256':digest(original),'generated_original_sha256':digest(H/'planet-imagegen-original.png'),'final_sha256':digest(H/'artwork-planet-v1.png'),'dimensions':[1672,941],'local_sky_bbox':box,'feather_pixels':[23,20],'perimeter_colour_match_additive_plane':coeff.tolist(),'outside_sky_edit_mask_byte_identical':True,'changed_pixels':int(np.any(result!=base,axis=2).sum()),'user_art_approval':False}
 (H/'artwork-provenance.json').write_text(json.dumps(report,indent=2)+'\n')
 deps=H/'dependency-snapshot';deps.mkdir(exist_ok=True)
 paths={}
 for name in ['water_surface.py','render_floodplain.py','ambient_effects.py']:
  p=Path(r'G:\AI\colony\scripts')/name;shutil.copy2(p,deps/name);paths[name]={'original':str(p),'sha256':digest(p)}
 (deps/'manifest.json').write_text(json.dumps(paths,indent=2)+'\n')
 c={'scene':'Deepwell Station','catalog':'12','version':'v1','duration':20,'fps':30,'preview_size':[1280,720],
 'source':{'path':'artwork-planet-v1.png','sha256':report['final_sha256'],'dimensions':[1672,941]},
 'water':{'roi':[402,375,1672,704],'seed':12025,'components':24,'time_scale':.09,'specular_strength':13,'wavelength_range':[.65,5],'reflection_sigma_x':3,'reflection_sigma_y':1.5,'displacement_scale':.55,'reflection_contrast':.105,'highlight_roughness':.32,'sampling_filter_pixels':.8,'edge_damping_pixels':12,'loop_seconds':20,'perspective_distance_scale':2600,'perspective_horizon_y':315,'perspective_center_x':1060,'perspective_lateral_scale':330},
 'water_polygons':[
 [[756,443],[790,438],[846,430],[923,428],[991,433],[1098,447],[1175,457],[1268,473],[1383,495],[1487,510],[1594,528],[1592,538],[1531,540],[1528,550],[1600,553],[1671,561],[1671,690],[1610,675],[1580,659],[1480,647],[1410,634],[1350,620],[1300,617],[1264,602],[1265,588],[1210,573],[1166,564],[1090,559],[1040,551],[981,552],[995,536],[1007,526],[1004,517],[968,505],[920,497],[859,489],[875,485],[877,476],[837,467],[794,463],[783,453],[756,450]],
 [[605,561],[668,552],[725,552],[750,544],[833,549],[920,549],[950,557],[963,567],[930,582],[899,588],[810,584],[720,578]],
 [[405,392],[600,383],[835,386],[915,384],[921,395],[803,405],[638,402],[627,398],[405,402]],
 [[970,418],[1100,416],[1137,421],[1240,423],[1268,430],[1315,431],[1330,437],[1671,454],[1671,473],[1500,457],[1400,450],[1300,445],[1180,434],[1050,428]]],
 'sky':{'roi':[402,0,1590,237],'speed':3.6,'gain':1.0,'source_clean_sigma':.6,'feather':8,'planet_protection_ellipse':[1145,157,105,104],
 'polygon':[[407,104],[1284,0],[1578,0],[1570,30],[1476,42],[1387,66],[1316,100],[1304,142],[1312,184],[1294,212],[1242,213],[1196,212],[1160,222],[1040,225],[954,218],[882,212],[850,210],[850,202],[780,196],[713,185],[636,179],[573,166],[510,160],[475,160],[458,153],[405,152]]},
 'lights':[
 {'polygon':[[1641,179],[1653,178],[1653,192],[1641,195]],'start':3.4,'hold':4.8,'transition':1.4,'floor':.57},
 {'polygon':[[1612,183],[1624,182],[1624,198],[1612,200]],'start':10.8,'hold':5.7,'transition':1.8,'floor':.63},
 {'polygon':[[1549,194],[1559,192],[1559,212],[1549,215]],'start':7.5,'hold':6.4,'transition':1.6,'floor':.6},
 {'polygon':[[1470,233],[1489,232],[1489,239],[1470,241]],'start':14.4,'hold':4.2,'transition':1.2,'floor':.58}],
 'lamp':{'core':[[44,274],[67,271],[70,305],[46,309]],'wall_polygon':[[0,210],[108,220],[121,341],[0,365]],'spill_center':[52,286],'spill_radius':[60,60],'events':[{'start':5.6,'hold':.65,'transition':.16,'depth':.33},{'start':15.8,'hold':1.1,'transition':.26,'depth':.23}]},
 'screen':{'quad':[[268,356],[316,355],[326,404],[277,406]],'size':[96,96],'log_quad':[[306,365],[317,365],[320,385],[310,385]]},
 'isolated_layers':['water','sky','screen'],'inspection':'Initial source/temporal/decoded still review, continuous playback not claimed','user_approved':False}
 (H/'scene-plan-v1.json').write_text(json.dumps(c,indent=2)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
