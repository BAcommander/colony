from pathlib import Path
import json,hashlib
from PIL import Image
R=Path('G:/AI/colony');H=Path(__file__).resolve().parent
src=R/'final/07-icebound-weather-post/artwork-v3-final.png'
c={'scene_name':'Icebound Weather Post','version':'v1','status':'draft implementation',
'source':{'path':src.relative_to(R).as_posix(),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'dimensions':list(Image.open(src).size)},
'duration':20,'fps':30,'preview_size':[1280,720],'ffmpeg':'C:/Program Files/ShareX/ffmpeg.exe',
'feedback_applied':['Readable broad background motion from first draft','Independent far and nearer haze rather than one strong fog patch','Independent complete-aperture light holds and small local spill','Existing source geometry and frozen sea preserved','No foreground snow particles or global exposure modulation'],
'protected_geometry':['Ice cliffs and frozen sea topology','All structures, mast, equipment and camera','Ringed moon excluded from moving texture source and output'],
'protected_lines':[[[274,53],[274,373],13],[[311,114],[349,119],17],[[328,103],[328,155],12]],
'protected_ellipses':[[1501,228,65,40]],
'clouds':[{'name':'sky','speed':2.6,'feather':14,'phase':.18,'polygons':[[[0,0],[1671,0],[1671,430],[1575,423],[1550,411],[1460,411],[1443,394],[1390,390],[1375,382],[1240,375],[1220,360],[1188,356],[1180,340],[1090,334],[1080,319],[934,308],[918,285],[884,267],[851,250],[760,235],[741,216],[707,207],[690,181],[658,172],[652,160],[558,146],[473,129],[396,108],[345,103],[280,89],[240,68],[188,57],[127,48],[85,40],[0,32]]]}],
'lights':[
 {'name':'main_room_right','polygon':[[295,453],[364,454],[365,503],[296,504]],'start':2.8,'hold':6.6,'transition':.55,'floor':.30},
 {'name':'habitat_one_window','polygon':[[853,472],[863,473],[863,486],[853,486]],'start':10.4,'hold':7.3,'transition':.35,'floor':.20},
 {'name':'habitat_two_window','polygon':[[1003,507],[1010,508],[1010,519],[1003,518]],'start':17.3,'hold':6.7,'transition':.4,'floor':.25}],
'screen':{'polygon':[[0,0],[1,0],[1,1]],'bands':[],'starts':[],'holds':[],'depths':[]},
'entrance':{'aperture':[[491,451],[514,452],[514,458],[491,457]],'events':[{'start':4.3,'hold':.65,'transition':.16,'depth':.58},{'start':5.2,'hold':.3,'transition':.08,'depth':.35},{'start':14.1,'hold':1.7,'transition':.45,'depth':.25}],
'spill_polygons':[[[456,463],[518,463],[528,550],[482,552],[460,534]],[[463,608],[535,602],[592,623],[576,644],[482,640],[441,626]]]},
'room_spill':{'polygons':[[[272,514],[370,513],[383,551],[273,555]],[[259,622],[354,621],[409,645],[360,662],[260,651]]],'strength':.10},
'haze':[]}
def haze(name,poly,speed,height,width,centers,seed,opacity):
    gusts=[{'x':x,'y':y,'width':width,'height':height,'route_slope':0,'phase':0,'strength':1} for x,y in centers]
    return {'name':name,'polygons':[poly],'feather':12,'speed':speed,'lifetime':20,'seed':seed,'optical_depth':opacity,'max_opacity':.24,'color':[180,198,218],'gusts':gusts,
      'loop_schedule':[{'gust_index':i,'birth_x':g['x']-speed*10,'age_at_zero':(i*3.7+p)%20,'fade_in':5,'fade_out':5} for i,g in enumerate(gusts) for p in [0,10]]}
c['haze'].append(haze('far_spindrift',[[1117,501],[1671,493],[1671,584],[1592,576],[1560,561],[1490,557],[1450,565],[1363,563],[1324,548],[1280,542],[1230,556],[1124,546]],4.8,10,150,[(1240,516),(1515,536)],7101,.17))
c['haze'].append(haze('basin_spindrift',[[1185,583],[1260,579],[1300,586],[1383,581],[1420,565],[1470,572],[1518,578],[1570,610],[1671,620],[1671,683],[1580,676],[1514,665],[1460,650],[1370,669],[1306,649],[1253,639],[1198,632],[1154,620]],8.5,16,160,[(1260,606),(1545,644)],7102,.23))
c['layer_order']=['sky','far_spindrift','basin_spindrift','lights','entrance','room_spill']
c['loop_method']='Periodic forward cloud transport and staggered local haze lifetimes, zero-weight resets; independent eased periodic lighting events'
out=H/'scene-plan-v1.json';assert not out.exists();out.write_text(json.dumps(c,indent=2)+'\n')
print('Icebound source configuration saved')
