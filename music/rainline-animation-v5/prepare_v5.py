from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;M=H.parent;V4=M/'rainline-animation-v4';renderer=M/'rainline-renderer/render_rainline.py'
old=renderer.read_bytes();expected=json.loads((V4/'delivery-v4.json').read_text())['fingerprint']['renderer_sha256']
assert hashlib.sha256(old).hexdigest()==expected
snapshot=V4/'renderer-v4-snapshot.py'
if snapshot.exists():assert snapshot.read_bytes()==old
else:snapshot.write_bytes(old)
c=json.loads((V4/'scene-plan-v4.json').read_text(encoding='utf-8'));c['version']='v5'
c['room'].update(slow_depth=.018,desk_gain=.9,lamp_events=[dict(start=3.8,hold=.28,transition=.08,depth=.88),dict(start=13.5,hold=.4,transition=.1,depth=.82)])
c['room']['lamp_halo']={'center':[202,460],'radius':[70,32],'gain':.65}
c['glass_rain']={'refraction':2.6,'tail_darkening':.12,'tail_highlight':15,'head_highlight':52,'drops':[]}
routes=[(213,36,20,16,3.2),(353,160,10,22,6.1),(410,62,20,19,11.3),(553,55,20,17,8.2),(670,232,10,18,1.4),(793,68,20,16,14.5),(948,25,20,21,4.2),(1135,118,20,18,12.3),(1245,327,10,22,5.2),(1464,70,20,22,16.4),(1624,389,20,18,7.1),(1332,646,10,15,2.4)]
for i,(x,y,life,speed,phase) in enumerate(routes):
 c['glass_rain']['drops'].append(dict(x=x,y=y,life=life,speed=speed,phase=phase,width=1.6+.18*(i%4),head_radius=2.9+.2*(i%3),trail=75+11*(i%5),wiggle=.8+.25*(i%3)))
c['isolated_layers']=['glass','room']
c['notes']=[
'User: about there; requested foreground light blink and rain on windows for one final creative pass. This does not mark v5 reviewed or request a Git push.',
'Two brief desk-lamp dropouts replace the v4 gentle dips; same lamp core/desk-spill mask, no full-frame exposure effect.',
'Twelve sparse refractive beads travel downward on the glass with short wet trails. Glass clips exclude cabin frames and equipment; exterior objects are seen through local refraction, not deformed geometrically.',
'Deterministic ten/twenty-second droplet lives divide the loop; individual smooth birth/death fades hide resets.',
'Water, exterior rain, habitat masks/schedules, radio/screen and red/green beacons retain v4 settings.',
'Exact v4 renderer snapshot preserved. Existing art and all previous exports remain unchanged.'
]
(H/'scene-plan-v5.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
(H/'feedback-v4.txt').write_text("2026-10-05. User: i think we're about there, can we have the light in the foreground room blink? is there anything more we can do like raid on the windows at all? can we push one last time?\nRain on windows interpreted from context. 'Push one last time' is treated as a final creative refinement, not a Git push. Positive v4 feedback with requested refinement; v5 motion review pending.\n",encoding='utf-8')
print('V5 configuration prepared; exact v4 renderer preserved')
