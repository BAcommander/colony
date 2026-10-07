"""Build the explicit minute configuration once; rendering reads the saved JSON."""
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent
c=json.loads((H.parent/'farpoint-animation-v3/scene-plan-v3.json').read_text())
c.update(version='v4',duration=60,status='Complete minute candidate; user playback review pending')
c['parent_v3_renderer_sha256']=hashlib.sha256((H.parent/'farpoint-animation-v3/render_farpoint_v3.py').read_bytes()).hexdigest()
c['completion_prompt']='final/10-nightward-station/animation-completion-prompt-v2.txt'
c['cloud_lifetimes']={'seconds':60,'fade_seconds':5,'centers_x':[780,960,1130,1300,1460,1600],'width':112,'phase_seconds':[0,11,23,35,46,55],'method':'Partition the extracted source into distinct feathered formations. Direct forward curved travel at v2 speeds. Each formation renews only at zero opacity; phases are staggered over the minute. No blend of nearby full weather-field copies.'}
c['lower_lifetimes']={'seconds':30,'fade_seconds':3,'phase_seconds':[5,20]}
c['aurora']={'roi':[620,285,1020,586],'angle_range':[-2.39,-2.055],'inner_limit':92,'color':[34,100,93],'filament_color':[53,87,90]}
c['lightning']=[{'time':11.2,'center':[1040,350],'radius':[64,24],'strength':36},{'time':36.5,'center':[1570,318],'radius':[40,26],'strength':42},{'time':52.8,'center':[1240,267],'radius':[57,23],'strength':34}]
c['stars']={'centers':[[788,69],[802,92],[808,257],[699,424],[1490,109],[1507,100]],'cycles':[1,2,1,3,2,1],'phases':[.3,2.1,4.2,1.4,5.6,3.3],'depth':.19}
c['reflections']={'polygons':[[[422,494],[444,491.5],[445,500],[422,502]],[[425,547],[442,544.8],[443,553.5],[425,556]],[[425,557],[443,553.8],[444,562.5],[425,565]]],'interpretation':'Existing source bars interpreted as warm practical-light reflections; original emitter uncertain. Linked to desk lamp state.'}
def event(start,hold,depth,transition=.12):return dict(start=start,hold=hold,depth=depth,transition=transition)
c['habitat_windows'][0]['events']=[event(3.4,5.8,.81,.45),event(31.2,8.7,.81,.65)]
c['habitat_windows'][1]['events']=[event(17.6,4.8,.77,.55),event(56.9,5.2,.77,.55)]
c['lamp']['events']=[event(12.7,.58,.48),event(44.2,1.15,.38,.24)]
extra=[[event(24.6,.3,.82,.06),event(25.12,.23,.8,.06),event(49.3,.65,.75)], [event(33.1,3.2,.72,.3)], [event(29.6,.25,.85,.06),event(30.04,.26,.85,.06),event(54.2,.8,.72)], [], [], []]
for i,lc in enumerate(c['instrument_lights']):
 if i<3:lc['events']+=extra[i]
 else:lc['events']=[event([27.8,41.2,18.5][i-3],[.75,1.1,.8][i-3],[.3,.25,.28][i-3],.3)]
c['screen_additions']['radar_period']=7.5
c['screen_additions']['route_period']=15
c['screen_additions']['meter_cycles']=[10,20]
c['loop_method']='Staggered local cloud renewal at zero opacity; periodic forward auroral fields; integer-cycle screen/star motion; independent wrapped held light schedules. One genuine minute, no duplicate endpoint.'
c['review']={'approved':False,'v2_cloud_visibility_confirmed':True,'v3_additions_not_accepted':True,'inspection':'To be recorded after rendering'}
c['knowledge_reuse']['scene_specific_exclusions']=['no exhaust without a mapped vent','no exterior weather in vacuum','no spacecraft','no whole-planet rotation','star brightness variation is cinematic, not atmospheric scintillation']
c['loop_speed_changes']={'principal_clouds':'v2 velocities unchanged','lower_cloud':'v3 velocity unchanged','radar':'8 to 7.5 seconds, +6.667% to close over minute','meter':'1.05/2.1 to 2*pi*10/60 and 2*pi*20/60, -0.267%','route_highlights':'13.5 to 15 seconds; main marker/log retain 20 seconds'}
(H/'scene-plan-v4.json').write_text(json.dumps(c,indent=2)+'\n')
