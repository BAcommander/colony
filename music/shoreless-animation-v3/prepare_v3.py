from pathlib import Path
import json, hashlib
H=Path(__file__).resolve().parent
V2=H.parent/'shoreless-animation-v2'
c=json.loads((V2/'scene-plan-v2.json').read_text())
c.update(version='v3',duration=60,environment_period=20)
c['feedback']='the sea on the far right is moving a tiny bit too much (only to the far right of the viewable area to the right of hte 3rd tower), the graph on the right monitor is too much, i prefer what you did on the left monitor, can any of the lights on the walk way flicker? can you built it out into a 1 minute loop?'
c['far_right_water']={'transition_x':[1085,1145],'displacement_multiplier':.75,'other_water_unchanged':True}
c.pop('telemetry')
c['right_screen']={'tracking_center':[1589,534],'tracking_half_size':[6,4],'travel_pixels':2,'period':12,'color':[17,51,59],'nodes':[[1552,581],[1578,584]]}
starts=[[2.4,24.6,48.2],[10.3,31.2,55.0],[17.7,40.4,58.1]]
holds=[[5.4,4.1,6.0],[6.2,4.8,3.7],[4.7,5.2,4.7]]
for j,lc in enumerate(c['lights']):
 lc['holds']=[{'start':a,'hold':b,'transition':lc['transition'],'depth':1-lc['floor']} for a,b in zip(starts[j],holds[j])]
 lc['flickers'] += [{'start':28.2+j*7.1,'hold':.22,'transition':.06,'depth':.48},{'start':51.7+j*2.5,'hold':.25,'transition':.07,'depth':.5}]
c['lamp']['events'] += [{'start':27.3,'hold':.2,'transition':.05,'depth':.5},{'start':27.76,'hold':.16,'transition':.05,'depth':.35},{'start':43.1,'hold':.36,'transition':.09,'depth':.42},{'start':54.5,'hold':.18,'transition':.05,'depth':.55}]
for j,lc in enumerate(c['exterior_flickers']):
 lc['events'] += [{'start':25.1+j*6.3,'hold':.24,'transition':.06,'depth':.55},{'start':46.5+j*4.2,'hold':.3,'transition':.08,'depth':.46}]
c['walkway_lights']=[]
for center,events in [([479,419],[(5.0,.25,.65),(5.47,.16,.4),(32.7,.38,.55)]),([826,415],[(13.5,.3,.6),(39.4,.22,.65),(39.87,.15,.35)]),([893,414],[(22.6,.24,.6),(51.2,.32,.5)])]:
 c['walkway_lights'].append({'center':center,'radius':[3.4,4.0],'spill_radius':[13,18],'events':[{'start':a,'hold':b,'depth':d,'transition':.06} for a,b,d in events]})
c['sunlight']['events']=[{'start':3,'hold':13,'transition':3,'depth':1},{'start':27,'hold':10,'transition':3,'depth':.82},{'start':44,'hold':12,'transition':3,'depth':.92}]
c['knowledge_reuse']['revision_v3']=['Preserve environment speeds: existing 20-second periodic fields divide a 60-second timeline with no speed requantization.','Unique minute-wide window, room, exterior and walkway events; sunlight uses three distinct openings.','Local water displacement reduction only beyond third caisson; do not weaken whole water layer.','Restore source screen imagery; left route style preferred over conspicuous waveform.','Cache native periodic background pixels once and compose unique minute-wide lighting at source resolution.']
c['isolated_layers']=['water','computers','walkway']
c['v2_renderer_sha256']=hashlib.sha256((V2/'render_shoreless_v2.py').read_bytes()).hexdigest()
p=H/'scene-plan-v3.json';assert not p.exists();p.write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
(H/'feedback-v2.txt').write_text(c['feedback']+'\n',encoding='utf-8')
print('V3 minute configuration prepared')
