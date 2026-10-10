from pathlib import Path
import json
H=Path(__file__).resolve().parent
c=json.loads((H.parent/'cable-animation-v1/scene-plan-v1.json').read_text())
c['version']='v2';c['feedback']='the movement seems ok, but clouds in the distance could do a lot more; room light flickering and sky light variations requested'
for cloud in c['clouds']:
 if cloud['name']=='sky':cloud['speed']=1.9
 if cloud['name']=='valley':cloud['speed']=3.7;cloud['feather']=7
c['distance_fog']={'polygons':[
 [[602,224],[636,219],[678,224],[717,224],[758,218],[795,225],[841,240],[865,264],[886,279],[887,317],[872,343],[846,365],[828,389],[792,416],[767,442],[741,461],[714,486],[695,482],[699,458],[718,431],[740,402],[737,378],[705,351],[680,327],[660,300],[639,281],[623,262]],
 [[944,350],[967,350],[1005,335],[1026,340],[1033,360],[1007,376],[985,394],[962,410],[948,443],[939,438]]],
 'exclude':[[[888,314],[955,314],[971,522],[953,536],[885,528]]],
 'feather':18,'speed':5.1,'lifetime':20,'seed':6203,'optical_depth':.18,'max_opacity':.22,'color':[205,191,186],
 'gusts':[{'x':680,'y':274,'width':101,'height':20,'route_slope':.09,'phase':0,'strength':1.0},{'x':765,'y':332,'width':103,'height':26,'route_slope':.04,'phase':.4,'strength':.85},{'x':823,'y':402,'width':89,'height':25,'route_slope':-.04,'phase':.7,'strength':.72}],
 'loop_schedule':[]}
for i,g in enumerate(c['distance_fog']['gusts']):
 for age in [i*3.3,(i*3.3+10)%20]:c['distance_fog']['loop_schedule'].append({'gust_index':i,'birth_x':g['x']-51,'age_at_zero':age,'fade_in':5,'fade_out':5})
c['lamp']={'aperture':[[125,443],[153,432],[182,425],[189,426],[189,429],[168,438],[141,446],[125,448]],'spill_regions':[
 {'polygon':[[113,449],[130,447],[211,477],[222,531],[201,552],[136,552],[114,534]],'center':[150,494],'radii':[70,68],'strength':.13},
 {'polygon':[[90,652],[149,630],[248,639],[354,655],[331,689],[174,716],[88,701]],'center':[202,672],'radii':[150,49],'strength':.13}],
 'events':[{'start':4.2,'hold':.64,'transition':.14,'depth':.70},{'start':5.03,'hold':.26,'transition':.065,'depth':.46},{'start':14.6,'hold':1.4,'transition':.24,'depth':.48}]}
c['daylight']={'start':5.8,'hold':11.7,'transition':3.6,'sky_depth':.09,'room_depth':.095,
 'room_polygons':[[[5,674],[100,635],[190,635],[290,641],[406,645],[514,650],[484,685],[294,722],[130,741],[5,745]],[[94,453],[114,453],[114,600],[91,603]]],
 'room_center':[236,688],'room_radii':[410,132],'sky_center':[350,200],'sky_radii':[570,280]}
c['implementation_note']='V2 extends immutable v1 adapter with spatially distributed periodic distant fog, lamp aperture/spill flickers and local daylight attenuation. Existing foreground cloud speeds, habitat schedule and console behavior preserved.'
p=H/'scene-plan-v2.json';assert not p.exists();p.write_text(json.dumps(c,indent=2)+'\n')
