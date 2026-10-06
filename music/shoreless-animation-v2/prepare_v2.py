from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;V1=H.parent/'shoreless-animation-v1'
c=json.loads((V1/'scene-plan-v1.json').read_text());c['version']='v2'
c['feedback']='can we mask the windows better, can we add some froath on the sea, can we do the standard antenna stuff, can we have anytihng on the monitors in the room, can we have some more flickering light and some sunlight poking through the clouds'
c['lights']=[
 {'name':'near_left_window','polygons':[[[269,407],[272,405.5],[285.5,405.5],[285.5,426],[271,427],[269,424]],[[288,405.5],[301,405],[304,407],[304,424],[301,426],[288,426]]],'start':2.4,'hold':5.4,'transition':.3,'floor':.2,'flickers':[{'start':12.6,'hold':.22,'transition':.06,'depth':.55}]},
 {'name':'middle_right_window','polygons':[[[761,399],[763,397],[773,397],[773,412],[761,412]],[[776,397],[783,397],[784,399],[784,412],[776,412]]],'start':10.3,'hold':6.2,'transition':.32,'floor':.24,'flickers':[{'start':4.8,'hold':.3,'transition':.08,'depth':.45}]},
 {'name':'far_left_window','polygons':[[[981,407],[983,405.5],[988.5,405.5],[988.5,416],[981,416]],[[991,405.5],[997,405.5],[998,407],[998,416],[991,416]]],'start':17.7,'hold':4.7,'transition':.3,'floor':.24,'flickers':[{'start':9.2,'hold':.25,'transition':.06,'depth':.6}]}
]
c['lamp']['events'] += [{'start':8.4,'hold':.24,'transition':.06,'depth':.48},{'start':15.05,'hold':.18,'transition':.05,'depth':.6}]
c['computers']['marker_radius']=3.0;c['computers']['route_color']=[75,158,179]
c['telemetry']={'quad':[[1541,560],[1605,565],[1600,601],[1534,594]],'size':[112,62],'opacity':.84}
c['antenna_lights']=[{'center':[244,304],'phase':.4,'period':4,'radius':1.1,'halo':3.5},{'center':[682,338],'phase':1.4,'period':5,'radius':.95,'halo':3},{'center':[950,321],'phase':2.5,'period':4,'radius':.95,'halo':3}]
c['exterior_flickers']=[{'center':[98,378],'radius':[4.8,4],'spill_radius':[16,21],'events':[{'start':5.6,'hold':.3,'transition':.06,'depth':.7},{'start':6.08,'hold':.18,'transition':.05,'depth':.45}]},{'center':[604,399],'radius':[3,4],'spill_radius':[11,15],'events':[{'start':12.0,'hold':.25,'transition':.06,'depth':.58}]},{'center':[1052,395],'radius':[2.8,3],'spill_radius':[9,11],'events':[{'start':16.4,'hold':.3,'transition':.08,'depth':.6}]}]
c['foam']={'seed':921,'strength':.36,'color':[187,204,204],'wash_zones':[[220,691,210,25],[689,561,150,19],[1007,507,110,14]],'open_sea_strength':.58}
c['sunlight']={'start':3.0,'hold':13.0,'transition':3.0,'opening':[474,238],'opening_radius':[172,47],'sky_gain':[18,12,5],'shaft_gain':[15,11,6],'water_gain':[24,17,7],'rays':[[.34,23],[.77,33],[1.13,28]]}
c['isolated_layers']=['lights','foam','antennas','room','sunlight']
c['v1_renderer_sha256']=hashlib.sha256((V1/'render_shoreless.py').read_bytes()).hexdigest()
shapes=[[[269.5,408],[271,407],[302,407],[304,408],[304,424],[302,425.5],[270,425.5],[269.5,424]],[[759.2,401],[761,400.2],[774.5,400.2],[776,401],[776,411.2],[759.5,411.5]],[[980,406],[981,405.5],[994,405.5],[995.5,407],[995.5,414],[980,414.5]]]
for lc,shape in zip(c['lights'],shapes):lc['polygons']=[shape]
for ac in c['antenna_lights']:ac['period']=5
p=H/'scene-plan-v2.json';assert not p.exists();p.write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
(H/'feedback-v1.txt').write_text(c['feedback']+'\n',encoding='utf-8')
print('V2 configuration saved; V1 preserved')
