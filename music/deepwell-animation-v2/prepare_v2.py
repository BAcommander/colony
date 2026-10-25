"""Preserve the first pass and freeze a full Deepwell refinement brief/config."""
from pathlib import Path
import json,shutil,hashlib
H=Path(__file__).resolve().parent;V1=H.parent/'deepwell-animation-v1'
assert not (H/'scene-plan-v2.json').exists(),'Preserve this revision; use a new version'
B=H/'baseline-snapshot';(B/'dependency-snapshot').mkdir(parents=True,exist_ok=True)
paths=['render_deepwell.py','scene-plan-v1.json','artwork-planet-v1.png','artwork-original-v2.png','analytic-validation.json','preview-validation.json','artwork-provenance.json']
paths+=['dependency-snapshot/'+n for n in ['water_surface.py','render_floodplain.py','ambient_effects.py','manifest.json']]
for name in paths:shutil.copy2(V1/name,B/name)
(H/'baseline-snapshot-manifest.json').write_text(json.dumps({n:hashlib.sha256((B/n).read_bytes()).hexdigest() for n in paths},indent=2)+'\n')
feedback={'date':'2026-10-25','exact_user_feedback':"ok it's a decent first pass, but needs a good bit more, lets make it 300% better, revisit every park",'interpretation':'Revisit every part of the animation. Decent first pass is a checkpoint, not final acceptance. 300% expresses ambition, not a measured improvement. Preserve the artwork and v1; make a complete stronger v2 review candidate.','scope':'Twenty-second silent 720p/30fps loop plus three-repeat review. No soundtrack, new image generation, 4K, long assembly or commit/push requested.'}
(H/'user-feedback.json').write_text(json.dumps(feedback,indent=2)+'\n')
old=json.loads((B/'scene-plan-v1.json').read_text())
c={'scene':'Deepwell Station','catalog':'12','version':'v2','duration':20,'fps':30,'preview_size':[1280,720],
 'source':{'path':'baseline-snapshot/artwork-planet-v1.png','sha256':old['source']['sha256'],'dimensions':[1672,941]},
 'baseline_snapshot':'baseline-snapshot','seed':122026,
 'reuse':{'water':'Glacier/Floodplain filtered reflection normals, retuned for horizontal wind crests and channel depth; no sparse glint substitution','sky':'Basalt/Shoreless source cloud transport; original planet-free source excludes geometry; new foreground veil crosses fixed planet','weather':'Separate far/middle/near transport and terrain-guided flow from Basalt/Cable/Empty Junction lessons; exact masks are Deepwell-specific; candidate methods are not inherited approvals','instruments':'Cable Station perspective-confined functional display; continuous needle/bar fields retain v1 seam fix','lighting':'Complete apertures, independent held schedules, attached emitter/spill and retained steady windows from Rainline/Spirewatch'},
 'water':dict(old['water'],seed=122026,components=32,wavelength_range=[.09,.82],time_scale=.075,reflection_sigma_x=1.05,reflection_sigma_y=.55,displacement_scale=.43,reflection_contrast=.105,specular_strength=10.5,sampling_filter_pixels=1.0),
 'water_direction':{'main_theta':1.48,'main_spread':.24,'cross_theta':.35,'cross_spread':.28,'cross_count':8,'cross_strength':.38,'gust_time_offset_seconds':.24,'sun_glint_variation':.14},
 'sky':{'near_speed':4.8,'far_speed':2.7,'gain':1.10,'feather':6,'planet_ellipse':[1145,160,89,90],'veil_band_center_y':177,'veil_band_radius_y':48,'veil_opacity':.22,'veil_speed':7.0},
 'atmosphere':[
 {'name':'far_drift','roi':[410,280,1145,361],'polygon':[[418,304],[627,303],[805,309],[971,300],[1110,315],[1115,339],[967,347],[761,350],[540,345],[418,342]],'center_y':326,'height':12,'speed':4.2,'seed':124,'opacity':.12,'color':[196,207,214],'feather':12},
 {'name':'basin_haze','roi':[415,335,1320,431],'polygon':[[420,349],[669,345],[840,349],[938,342],[1083,354],[1276,382],[1255,398],[1123,390],[971,373],[841,376],[643,374],[420,372]],'center_y':361,'height':8,'speed':7.2,'seed':128,'opacity':.13,'color':[205,214,220],'feather':9},
 {'name':'brine_wisps','roi':[745,424,1510,561],'polygon':[[777,444],[933,434],[1087,448],[1230,471],[1380,498],[1490,520],[1482,533],[1359,514],[1202,488],[1065,467],[933,451],[789,460]],'center_y':459,'height':6,'slope':.115,'speed':8.5,'seed':130,'opacity':.105,'color':[202,214,221],'feather':8}],
 'surface_drift':[
 {'name':'salt_far','roi':[422,328,988,371],'route':[[429,347],[580,345],[760,349],[971,355]],'speed':14.0,'opacity':.15,'width':3.8,'seed':140,'color':[211,218,220]},
 {'name':'salt_middle','roi':[425,398,775,448],'route':[[433,422],[536,422],[650,418],[763,427]],'speed':20.0,'opacity':.16,'width':4.2,'seed':142,'color':[208,216,221]}],
 'lights':[
 {'polygon':[[1642,179],[1652,178],[1652,193],[1642,195]],'start':1.8,'hold':5.1,'transition':1.1,'floor':.43},
 {'polygon':[[1627,181],[1638,180],[1638,196],[1627,198]],'start':12.1,'hold':4.9,'transition':1.0,'floor':.58},
 {'polygon':[[1612,184],[1622,183],[1622,199],[1612,201]],'start':7.7,'hold':4.3,'transition':.9,'floor':.47},
 {'polygon':[[1549,195],[1558,193],[1558,212],[1549,215]],'start':16.3,'hold':5.8,'transition':1.4,'floor':.52},
 {'polygon':[[1565,193],[1574,191],[1574,209],[1565,211]],'start':4.1,'hold':5.1,'transition':1.4,'floor':.63},
 {'polygon':[[1470,233],[1482,232],[1482,239],[1470,241]],'start':9.5,'hold':4.0,'transition':.8,'floor':.45},
 {'polygon':[[1486,232],[1497,231],[1497,237],[1486,239]],'start':17.6,'hold':4.7,'transition':1.3,'floor':.62},
 {'polygon':[[1430,240],[1436,239],[1436,245],[1430,247]],'start':6.3,'hold':5.0,'transition':1.5,'floor':.57}],
 'lamp':{'events':[{'start':6.4,'hold':1.3,'transition':.32,'depth':.30},{'start':14.8,'hold':2.0,'transition':.6,'depth':.20},{'start':6.04,'hold':.18,'transition':.055,'depth':.18}],'spill_gain':1.20,'desk_polygon':[[296,745],[575,715],[747,773],[609,805],[493,817],[356,790]],'desk_strength':.045},
 'status':{'polygon':[[252,319],[258,319],[258,338],[252,339]],'events':[{'start':3.2,'hold':.42,'transition':.1,'depth':.72},{'start':3.88,'hold':.3,'transition':.08,'depth':.6},{'start':11.7,'hold':.7,'transition':.16,'depth':.60},{'start':18.0,'hold':.42,'transition':.1,'depth':.54}]},
 'daylight':{'table_polygon':[[300,742],[576,713],[747,774],[608,805],[493,817],[354,789]],'table_strength':.042,'ledge_polygon':[[435,584],[804,628],[1184,690],[1614,759],[1614,769],[1176,704],[797,644],[436,598]],'ledge_strength':.027},
 'screen':{'quad':old['screen']['quad'],'size':[128,128],'needle_strength':1.25,'log_cycles':2,'data_cycles':4},
 'isolated_groups':{'sky':['sky','planet_veil'],'water':['water'],'atmosphere':['far_drift','basin_haze','brine_wisps','salt_far','salt_middle'],'habitation':['screen','lights','lamp','status','daylight']},
 'user_approved':False,'inspection':'Native/temporal/decoded still inspection; continuous playback not claimed'}
(H/'scene-plan-v2.json').write_text(json.dumps(c,indent=2)+'\n')
print('V1 frozen locally; exact feedback and all-part v2 configuration saved.')
