from pathlib import Path
import json,hashlib,shutil
R=Path('G:/AI/colony/music');src=R/'spirewatch-animation-v2';dst=R/'spirewatch-animation-v3'
dst.mkdir(exist_ok=True)
assert not (dst/'scene-plan-v3.json').exists()
shutil.copytree(src/'dependencies',dst/'dependencies',dirs_exist_ok=True)
baseline=(src/'baseline.py').read_text().replace("scene-plan-v2.json","scene-plan-v3.json")
(dst/'baseline.py').write_text(baseline,encoding='utf-8')
c=json.loads((src/'scene-plan-v2.json').read_text())
c['version']='v3';c['baseline_sha256']=hashlib.sha256((dst/'baseline.py').read_bytes()).hexdigest()
c['status']='V3 lighting rebuild candidate; playback review pending'
c['revision']={'feedback':'Lightning missed, big tower activity invisible, warm lights seem static. User requested stronger lightning and more lighting activity; 250% is ambition, not a quality measurement.', 'retained':'Identical v2 source/cloud reconstruction/falls/water/mist/transit/monitor', 'knowledge_reuse':'Complete aperture masks and coupled spill; independent room holds; source-bound cyan masks; calm water; real minute scheduling; quiet-neighbor seam checks.', 'prior_checkpoint':'4f008e92dfeed7788f504cb28d76dcae8efcf9c7'}
c['lighting_v3']={'tower_floor':0.40,'tower_band_height':64,'tower_color':[68,184,225],'district_floor':0.58,'district_band_height':50,'district_color':[38,132,169], 'window_floor':0.12,'window_transition':0.32,'window_hold_range':[3.5,8.0], 'window_clusters_per_facade':3,'window_max_per_cluster':7,'seed':31011,'lightning_cloud_color':[76,100,126],'lightning_bolt_color':[122,161,189],'storm_response_color':[20,30,40]}
c['windows']['facade_regions'] += [[212,380,269,463],[728,670,809,739],[715,598,788,643],[832,585,881,630],[863,370,901,420],[1122,470,1182,497],[1275,419,1365,445],[1380,457,1460,480],[1490,477,1575,502],[1195,683,1270,732],[1600,665,1660,724],[371,87,422,215]]
c['lamp']['depth']=.54
c['walkway']['depth']=.76;c['walkway']['hold']=.65
for e in c['lightning']['events']:
 e['radius']=[round(e['radius'][0]*1.32),round(e['radius'][1]*1.2)]
c['lightning']['duration']=1.8
c['lightning']['style']='Broader local intracloud flash with two uneven pulses, longer fading glow, partial branches and spatially related exterior/water response; stable room exposure.'
(dst/'scene-plan-v3.json').write_text(json.dumps(c,indent=2)+'\n')
s=(src/'render_spirewatch.py').read_text()
start=s.index("  if enabled('windows'):\n",s.index(' def frame('));end=s.index("  if enabled('walkway'):",start)
s=s[:start]+"  if enabled('windows'):self.render_windows(f,t,force_dark)\n"+s[end:]
start=s.index("  if enabled('tower'):\n",s.index(' def frame('));end=s.index('  progress,env,direction=',start)
s=s[:start]+"  if enabled('tower'):self.render_tower(f,t)\n  if enabled('city_glow'):self.render_districts(f,t)\n"+s[end:]
s=s.replace("np.float32([25,33,42])+bolt[...,None]*amp*np.float32([19,25,30])", "np.float32(self.config['lighting_v3']['lightning_cloud_color'])+bolt[...,None]*amp*np.float32(self.config['lighting_v3']['lightning_bolt_color'])")
start=s.index("  if enabled('storm_response') and flash>.0001:");end=s.index('  assert np.isfinite(f)',start)
s=s[:start]+"  if enabled('storm_response'):self.render_storm_response(f,t)\n"+s[end:]
s=s.replace('\ndef samples(s):', '\nfrom lighting_layers import LightingV3\nclass Spirewatch(LightingV3,Spirewatch):\n pass\n\ndef samples(s):')
s=s.replace("fp['baseline_sha256']=sha(H/'baseline.py');return fp", "fp['baseline_sha256']=sha(H/'baseline.py');fp['lighting_layers_sha256']=sha(H/'lighting_layers.py');return fp")
s=s.replace('spirewatch-v2-','spirewatch-v3-').replace('delivery-v2.json','delivery-v3.json').replace('V2 minute','V3 minute')
s=s.replace("'2026-10-10'","'2026-10-11'")
(dst/'render_spirewatch.py').write_text(s,encoding='utf-8')
for name in ['render_parallel.py','check_chunk_joins.py','inspect_encoded.py']:
 s=(src/name).read_text().replace('spirewatch-v2-','spirewatch-v3-').replace('scene-plan-v2','scene-plan-v3')
 (dst/name).write_text(s,encoding='utf-8')
print(dst)
