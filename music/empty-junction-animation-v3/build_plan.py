from pathlib import Path
import json
H=Path(__file__).resolve().parent
c=json.loads((H.parent/'empty-junction-animation-v2/scene-plan-v2.json').read_text(encoding='utf-8'))
c.update(version='v3',status='Near/middle/distant motion candidate; playback review pending')
c['feedback']['v2']="it's ok still overall feels kinda static"
c['feedback']['scope']='User authorized ground mineral streamers, cabin ventilation condensation and terrain-guided mist.'
c['new_motion']={
 'terrain_flow':{'path':[[920,286],[948,302],[972,325],[1015,336],[1080,336],[1120,327]],'widths':[3,8,14,17,13,3],'speed':8,'seed':11301,'opacity':.36,'color':[173,178,193],'feather':8,'polygon':[[899,279],[928,273],[957,285],[984,304],[1030,315],[1101,310],[1142,319],[1137,347],[1058,356],[979,351],[937,328],[914,306]]},
 'yard_powder':{'seed':11302,'opacity':.31,'color':[158,164,179],'feather':7,'routes':[{'path':[[1115,557],[1162,568],[1225,601],[1286,640],[1350,700],[1438,793]],'widths':[2,4,6,9,11,3],'speed':17},{'path':[[644,790],[705,775],[758,791],[822,815],[895,849]],'widths':[2,6,8,11,2],'speed':22}],'polygons':[[[1091,541],[1168,543],[1240,577],[1299,623],[1382,702],[1466,789],[1450,817],[1387,776],[1290,687],[1200,621],[1112,582]],[[621,782],[679,748],[722,749],[803,782],[928,855],[905,875],[827,850],[705,819],[627,811]]],'blockers':[[[775,610],[849,610],[849,774],[774,774]]]},
 'cabin_exhaust':{'anchor':[520,389],'path':[[520,389],[538,386],[568,374],[610,361],[666,348]],'widths':[2,4,8,13,0],'lifetime':10,'particles':26,'seed':11303,'opacity':.30,'color':[185,185,195],'feather':3,'polygon':[[519,380],[542,373],[572,355],[612,342],[654,330],[689,337],[690,363],[640,382],[586,394],[542,400],[519,395]]}
}
c['new_motion']['yard_powder']['blockers'].append([[1140,548],[1169,548],[1169,612],[1140,612]])
c['new_motion']['terrain_flow']['blockers']=[[[1069,350],[1107,331],[1143,319],[1152,359],[1069,368]]]
c['omitted']['vent']='Existing right-hand cabin louvred grille used as a plausible exhaust; capped roof pipe remains unused. No artwork edit.'
c['method_notes']+=['V3 explicitly authorizes localized near-ground powder; previous blanket foreground-weather exclusion is superseded for these mapped routes.', 'Use existing cabin grille at native x520/y389. Exhaust interpretation is artistic, not established engineering.', 'V2 sky, side mist and station lights retained. Add directed optical flow at three depths. No person or hanging hardware added.']
(H/'scene-plan-v3.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
