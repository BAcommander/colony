from pathlib import Path
import json,hashlib
H=Path(__file__).parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
c=json.loads((H.parent/'spirewatch-animation-v3/scene-plan-v3.json').read_text())
c['version']='v4';c['date']='2026-10-21'
c['tower']['events']=[[3,17,'up'],[37,53,'down']]
c['transit']['events']=[[4,20,1],[25,42,-1],[45,59,1]]
c['lighting_v3']['window_transition']=1.1
c['lighting_v3']['window_hold_range']=[6,12]
c['lighting_v3']['window_floor']=.25
c['lightning']['events']=c['lightning']['events'][:2]
c['lightning']['events'][0]['time']=28.4
c['lightning']['events'][1]['time']=54.4
c['lighting_v4']={'tower_floor':.68,'tower_color':[46,145,180],'tower_band_height':38,'crown_start':16.5,'crown_hold':5.5,'crown_transition':1.4,'district_delays':[9,6,3,1,4,0], 'district_starts':[18,49], 'district_hold':6,'district_transition':1.3,'district_color':[20,86,114], 'reflection_strength':.62,'glass_strength':.65,'music_activity':1.0,'music_sync':'Not yet timed: eight-minute generation pending. Preview uses full activity; renderer accepts an activity multiplier without changing weather velocity.'}
c['reuse_notes']=['Immutable v3 source and exact source-coordinate masks retained.','V3 clouds, mist, falls, spray, water displacement, walkway and lamp retained.','Whole-aperture window masks retained; slower independent holds/recovery.','Source-bound city emitters, perspective transit and monitor traces revised; no broad facade rectangles.','New water light response clipped to water masks; no extra displacement.','Local window-glass reflection clipped away from frame and equipment.','Thumbnail is separate generated marketing adaptation, never animation input.']
for name in ['baseline.py','render_spirewatch.py','render_parallel.py']:
 p=H/name;s=p.read_text();s=s.replace('scene-plan-v3.json','scene-plan-v4.json').replace('spirewatch-v3','spirewatch-v4').replace('delivery-v3.json','delivery-v4.json')
 if name=='render_spirewatch.py':
  start=s.index("  if enabled('transit') and env>0:")
  end=s.index("  if enabled('screen_spill'):",start)
  s=s[:start]+"  if enabled('transit'):self.render_transit_v4(f,t)\n  if enabled('screen'):self.render_screen_v4(f,t)\n  self.render_new_layers(f,t,enabled)\n"+s[end:]
  s=s.replace('from lighting_layers import LightingV3\nclass Spirewatch(LightingV3,Spirewatch):','from digital_layers import LightingV4\nclass Spirewatch(LightingV4,Spirewatch):')
  s=s.replace("fp['lighting_layers_sha256']=sha(H/'lighting_layers.py');return fp", "fp['lighting_layers_sha256']=sha(H/'lighting_layers.py');fp['digital_layers_sha256']=sha(H/'digital_layers.py');return fp")
  s=s.replace("'2026-10-11'","'2026-10-21'")
 p.write_text(s,encoding='utf-8')
c['baseline_sha256']=sha(H/'baseline.py')
(H/'scene-plan-v4.json').write_text(json.dumps(c,indent=2)+'\n')
print('Versioned v4 package prepared')
