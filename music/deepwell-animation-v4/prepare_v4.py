"""Freeze v3 and configure a materially more readable vapor/purple-light pass."""
from pathlib import Path
import json,shutil,hashlib
H=Path(__file__).resolve().parent;V3=H.parent/'deepwell-animation-v3';S=H/'v3-snapshot'
assert not (H/'scene-plan-v4.json').exists(),'Preserve the selection; create a new revision'
S.mkdir(exist_ok=True)
for name in ['render_deepwell_v3.py','review_tools.py','scene-plan-v3.json','v2-snapshot-manifest.json']:
 shutil.copy2(V3/name,S/name)
shutil.copytree(V3/'v2-snapshot',S/'v2-snapshot')
(H/'v3-snapshot-manifest.json').write_text(json.dumps({q.relative_to(S).as_posix():hashlib.sha256(q.read_bytes()).hexdigest() for q in sorted(S.rglob('*')) if q.is_file()},indent=2)+'\n')
shutil.copy2(V3/'review_tools.py',H/'review_tools.py')
c=json.loads((V3/'scene-plan-v3.json').read_text());c['version']='v4';c['source']['path']='v3-snapshot/v2-snapshot/baseline-snapshot/artwork-planet-v1.png'
settings={
 'coffee_steam':{'roi':[198,617,316,751],'height':124,'width':12,'drift':5.0,'lifetime':10,'opacity':1.00,'color':[235,236,229],'baseline':.84,'curl':8.0,'alpha_cap':.56},
 'tank_steam_near':{'roi':[1165,157,1264,238],'height':70,'width':9.5,'drift':24,'lifetime':5,'opacity':1.30,'color':[243,246,249],'baseline':.67,'curl':11.0,'alpha_cap':.62},
 'tank_steam_middle':{'roi':[1147,174,1230,242],'height':58,'width':7.5,'drift':19,'lifetime':5,'opacity':1.15,'color':[239,244,248],'baseline':.68,'curl':9.0,'alpha_cap':.60},
 'tank_steam_far':{'roi':[1264,158,1359,232],'height':63,'width':8.8,'drift':25,'lifetime':5,'opacity':1.25,'color':[241,245,249],'baseline':.67,'curl':11.0,'alpha_cap':.62}}
for sc in c['steam']:sc.update(settings[sc['name']])
pc=c['pipeline_lights'];pc.update({'marker_x':sorted(set(pc['marker_x']+[879,960,1042,1128,1175,1225,1276,1330])),'roi':[868,257,1397,337],'period':20,'floor':.24,'color':[177,64,226],'peak_color':[242,164,255],'halo_color':[106,26,159],'halo_gain':.23,'fixture_darkening':.24,'pulse_width':.105,'core_sigma':[3.40,1.15],'halo_sigma':[5.4,2.0],'tail_length':.10,'tail_width':.16,'tail_strength':.44,'mode':'cosine round trip: far-left at 0/20, plant inlet at 10; continuous turnaround and directional tail'})
pc.pop('phases',None)
pc['tube_outline']=[[876,325.6],[900,320.7],[950,312.9],[1000,305.4],[1050,300.1],[1100,293.9],[1150,288.3],[1200,282.9],[1250,276.0],[1300,271.1],[1350,265.0],[1392,261.3],[1392,278.0],[1350,280.6],[1300,287.0],[1250,291.2],[1200,297.4],[1150,301.0],[1100,306.2],[1050,311.2],[1000,316.2],[950,321.2],[900,329.0],[876,333.6]]
c['revision_scope']='User reports all steam and cyan lights too faint. Replace thin vapor with wider, rolling, higher-contrast persistent steam; larger purple pipe-face segments with a continuous out-and-back pulse and coupled local metal halo. Retain v3 glazing and thirteen other layers.'
c['user_approved']=False
(H/'scene-plan-v4.json').write_text(json.dumps(c,indent=2)+'\n')
feedback={'date':'2026-10-25','exact_user_feedback':'steam in all places very hard to see, cyan lights too, can the be purple maybe and run aup and down the pipeline, then take another pass to make it MUCH better','interpretation':'V3 vapor and pipeline indicators failed visibility review. Change coverage, morphology, material contrast, source duty and emitter footprint, not only a small opacity increase. Purple is explicit; show a complete outward/return trip at normal speed. Preserve corrected glazing, source and v3. MUCH better is ambition, not a measured quality claim.'}
(H/'user-feedback.json').write_text(json.dumps(feedback,indent=2)+'\n')
print('V3 frozen; broad rolling vapor and a full purple pipeline round trip configured.')
