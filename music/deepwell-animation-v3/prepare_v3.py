"""Freeze v2 dependencies and source; map whole glass panes, vapor and pipe lights."""
from pathlib import Path
import json,shutil,hashlib
H=Path(__file__).resolve().parent;V2=H.parent/'deepwell-animation-v2';S=H/'v2-snapshot'
assert not (H/'scene-plan-v3.json').exists(),'Preserve this candidate; use a new revision'
S.mkdir(exist_ok=True)
for name in ['render_deepwell_v2.py','review_tools.py','weather_refinement.py','scene-plan-v2.json','baseline-snapshot-manifest.json']:
 shutil.copy2(V2/name,S/name)
shutil.copytree(V2/'baseline-snapshot',S/'baseline-snapshot',dirs_exist_ok=False)
files={str(p.relative_to(S)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(S.rglob('*')) if p.is_file()}
(H/'v2-snapshot-manifest.json').write_text(json.dumps(files,indent=2)+'\n')
shutil.copy2(V2/'review_tools.py',H/'review_tools.py')
c=json.loads((V2/'scene-plan-v2.json').read_text());c['version']='v3';c['source']['path']='v2-snapshot/baseline-snapshot/artwork-planet-v1.png'
panes=[
 {'id':'R1','group':'right-left-room','polygon':[[1603.8,181.1],[1607.7,178.6],[1613.1,177.0],[1613.1,203.8],[1603.8,205.3]]},
 {'id':'R2-steady','group':None,'polygon':[[1616.6,177.0],[1628.8,174.2],[1628.8,201.5],[1616.6,203.6]]},
 {'id':'R3','group':'right-bright-room','polygon':[[1640.7,173.5],[1658.5,171.9],[1658.5,199.1],[1640.7,201.0]]},
 {'id':'R4','group':'right-bright-room','polygon':[[1662.1,171.5],[1671.6,170.9],[1671.6,197.8],[1662.1,198.9]]},
 {'id':'M1','group':'middle-left-room','polygon':[[1550.5,198.6],[1553.1,195.2],[1556.1,193.8],[1556.1,215.9],[1550.5,217.5]]},
 {'id':'M2','group':'middle-left-room','polygon':[[1559.2,193.5],[1562.8,192.0],[1562.8,215.0],[1559.2,216.2]]},
 {'id':'M3','group':'middle-bright-room','polygon':[[1566.7,191.3],[1571.5,189.6],[1571.5,213.5],[1566.7,214.8]]},
 {'id':'M4','group':'middle-bright-room','polygon':[[1574.2,189.4],[1576.4,188.5],[1576.4,212.0],[1574.2,212.8]]},
 {'id':'L1','group':'lower-left-room','polygon':[[1464.7,232.1],[1477.6,230.5],[1477.6,242.0],[1464.7,242.9]]},
 {'id':'L2','group':'lower-bright-room','polygon':[[1480.3,230.1],[1492.1,229.0],[1492.1,240.9],[1480.3,241.9]]},
 {'id':'L3','group':'lower-bright-room','polygon':[[1494.6,228.8],[1497.7,228.3],[1497.7,238.5],[1494.6,239.4]]}]
events=[('right-left-room',1.7,5.1,.9,.57),('right-bright-room',8.1,5.9,1.4,.48),('middle-left-room',15.2,6.3,1.3,.57),('middle-bright-room',3.7,5.4,1.0,.51),('lower-left-room',10.7,5.2,1.0,.62),('lower-bright-room',17.3,5.9,1.2,.53)]
c['lights']=[{'name':name,'polygons':[p['polygon'] for p in panes if p['group']==name],'start':start,'hold':hold,'transition':transition,'floor':floor} for name,start,hold,transition,floor in events]
c['window_panes']={'panes':panes,'supersampling':16,'inward_feather_pixels':.38,'facade_regions':[[1595,165,1672,211],[1538,179,1581,222],[1438,218,1505,249]],'fixed_mullion_lines':[[1614,177,1614,205],[1634,174,1634,202],[1660,172,1660,200],[1557,195,1557,215],[1564,192,1564,215],[1573,191,1573,213],[1478,230,1478,242],[1493,229,1493,240]]}
c['steam']=[
 {'name':'coffee_steam','anchor':[250.5,748.7],'roi':[221,646,288,751],'height':96,'width':5.6,'drift':3.8,'lifetime':5,'opacity':.16,'seed':303,'color':[218,220,215],'kind':'coffee','baseline':.65},
 {'name':'tank_steam_near','anchor':[1196.6,234.1],'roi':[1184,183,1230,238],'height':47,'width':5.2,'drift':13,'lifetime':5,'opacity':.24,'seed':311,'color':[221,229,234],'kind':'vent','baseline':.28,'events':[{'start':.7,'hold':7.0,'transition':1.2},{'start':12.0,'hold':5.5,'transition':1.0}]},
 {'name':'tank_steam_middle','anchor':[1169.0,238.2],'roi':[1159,198,1192,242],'height':36,'width':3.8,'drift':10,'lifetime':4,'opacity':.21,'seed':313,'color':[217,226,232],'kind':'vent','baseline':.30,'events':[{'start':5.1,'hold':8.2,'transition':1.6}]},
 {'name':'tank_steam_far','anchor':[1291.0,228.5],'roi':[1281,187,1318,232],'height':37,'width':4.1,'drift':12,'lifetime':5,'opacity':.23,'seed':317,'color':[218,226,232],'kind':'vent','baseline':.28,'events':[{'start':14.4,'hold':8.4,'transition':1.6}]}]
c['steam_occluders']={
 'cup_front':[[215.5,751.5],[227,755.6],[249.5,756.3],[271.8,752.8],[290.6,747.6],[290.6,826],[214.5,827]],
 'tank_shells':[
 [[1127,254.0],[1145,246.4],[1159.0,249.1],[1159,245.2],[1170,240.0],[1180.7,244.3],[1181.2,241.2],[1196.8,237.0],[1214.5,243.1],[1214.5,282],[1126.2,291.5]],
 [[1245.0,243.0],[1260.2,236.1],[1272,240.6],[1274.1,237.6],[1291.2,232.6],[1308.0,238.6],[1308,265],[1244.5,278]]]},
c['steam_occluders']=c['steam_occluders'][0] if isinstance(c['steam_occluders'],tuple) else c['steam_occluders']
c['pipeline_lights']={'route':[[858,331.6],[900,323.5],[950,317.0],[1000,310.1],[1050,304.2],[1100,298.3],[1150,292.5],[1200,288.0],[1250,282.0],[1300,276.0],[1350,270.0],[1390,266.5]],'marker_x':[899,940,981,1021,1062,1107,1152,1200,1250,1302,1358,1386],'roi':[887,260,1394,332],'period':10,'phases':[0,.5],'floor':.12,'color':[132,222,229],'halo_color':[28,76,83],'fixture_darkening':.18,'pulse_width':.10,'core_sigma':[.95,.60],'halo_sigma':[2.1,1.1]}
c['isolated_groups']={'windows':['lights'],'coffee':['coffee_steam'],'tank_steam':['tank_steam_near','tank_steam_middle','tank_steam_far'],'pipeline':['pipeline_lights'],'water':['water'],'sky':['sky','planet_veil'],'atmosphere':['far_drift','basin_haze','brine_wisps','salt_far','salt_middle'],'habitation':['screen','lights','lamp','status','daylight']}
c['user_approved']=False;c['revision_scope']='Whole-pane masks replace v2 small rectangles; coffee and three actual roof-outlet steam sources; restrained mounted pipeline indicator chase. V2 remaining layers/timings retained.'
(H/'scene-plan-v3.json').write_text(json.dumps(c,indent=2)+'\n')
feedback={'date':'2026-10-25','exact_user_feedback':"window masking needs to be alot better, can we add steam in the forgroune to the coffee or pipes and to the containers in the distance? maybe some lights running along the pipeline?",'interpretation':'Replace window masks with actual full glass panes and preserve mullions/stone. Choose coffee for foreground steam, plus three existing tank roof outlets; do not invent a leaking foreground pipe. Add restrained fixed marker lights with travelling acknowledgement along the visible pipe, ending at the actual plant inlet.'}
(H/'user-feedback.json').write_text(json.dumps(feedback,indent=2)+'\n')
print('V2 frozen; whole panes, four steam anchors and actual visible-pipe route mapped.')
