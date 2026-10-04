from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;M=H.parent;V3=M/'rainline-animation-v3';renderer=M/'rainline-renderer/render_rainline.py'
old=renderer.read_bytes();expected=json.loads((V3/'delivery-v3.json').read_text())['fingerprint']['renderer_sha256']
assert hashlib.sha256(old).hexdigest()==expected,'Snapshot the actual v3 renderer before changing it'
snapshot=V3/'renderer-v3-snapshot.py'
if snapshot.exists():assert snapshot.read_bytes()==old
else:snapshot.write_bytes(old)
c=json.loads((V3/'scene-plan-v3.json').read_text(encoding='utf-8'));c['version']='v4'
for key in ['displacement_scale','reflection_contrast','specular_strength']:c['water'][key]*=.75
c['impacts']['strength']*=.75
c['lights'][1].update(polygons=[[[1280,360],[1298,360],[1299,362],[1299,382],[1297,385],[1279,385],[1278,382],[1278,363]],[[1373,364],[1375,362],[1393,362],[1393,385],[1375,386],[1373,383]],[[1396,362],[1410,362],[1412,364],[1412,382],[1410,385],[1396,386]]],glow_gain=0,spill_gain=0,reflection_gain=0,chromatic_gate=True,floor=.60)
c['room'].update(instruments_v2=True,slow_depth=.055,desk_gain=.9,lamp_events=[dict(start=2.2,hold=.65,transition=.25,depth=.18),dict(start=12.2,hold=.85,transition=.3,depth=.16)])
c['radio_meter']['strength']=.13
c['instruments']={
 'screen':{'quad':[[403,524],[445,522],[447,556],[404,557]],'size':[84,56]},
 'radio':{'quad':[[224,562],[272,558],[273,575],[225,579]],'size':[90,34]}}
c['notes']=[
'V4 user feedback: cannot see room/radio activity, rear-building mask needs improvement, reduce water another 25%.',
'Water displacement, reflection contrast, specular response and impact strength multiplied by .75. Speed and wave family retained from v3.',
'Rear glass traced to include three visible panes and outer edge; divider and cool metal are excluded with a source-color gate that preserves white light cores. Arbitrary rear spill/reflection rectangles removed.',
'Foreground instrumentation uses readable animated chart and dual level bars confined to perspective-mapped existing display areas. Source equipment/bezel/text outside those areas stays fixed.',
'Desk lamp has two clearly held gentle dips coupled to warm desk spill. Weather and antenna schedules otherwise unchanged.',
'V3 renderer byte-for-byte snapshot saved alongside v3; shared renderer extended with optional configuration controls.'
]
(H/'scene-plan-v4.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
(H/'feedback-v3.txt').write_text("User: can't see anything in the room or with the raid, can rear building mask be made better too, water still seems a bit too strong, maybe tone down another 25%\nInterpreted raid as radio in the established foreground-equipment context. V3 needs revision; v4 remains pending review.\n",encoding='utf-8')
print('V4 configuration prepared; exact v3 renderer snapshot preserved')
