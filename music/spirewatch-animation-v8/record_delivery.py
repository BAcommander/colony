import json
from render_spirewatch import H,Spirewatch,save,sha
s=Spirewatch();fp=s.fingerprint();root=H.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
a=read(H/'analytic-validation.json');v=read(H/'preview-validation.json');r=read(H/'repeat-validation.json');c=read(H/'chunk-join-validation.json');q=read(H/'short-tests.json')
assert a['pass'] and a['fingerprint']==fp and a['tower_and_glow_zero_below_source_y425']
assert v['fingerprint']==fp and v['frames']==1800 and v['full_decode']
assert r['frames']==5400 and r['three_exact_decoded_repetitions']
assert c['pass'] and c['fingerprint']==fp and q['fingerprint']==fp and len(q['clips'])==4
save('delivery-v8.json',{'date':'2026-10-21','status':'Technically verified finishing preview; user playback review pending','preview':'spirewatch-v8-preview-60s.mp4','repeat':'spirewatch-v8-three-loops-180s.mp4','fingerprint':fp,'preview_sha256':sha(H/'spirewatch-v8-preview-60s.mp4'),'verification':['analytic-validation.json','short-tests.json','preview-validation.json','repeat-validation.json','chunk-join-validation.json'],'assistant_review':'Native and decoded temporal stills; not continuous playback','user_approved':False,'music_received':False,'four_k':False,'committed':False,'pushed':False})
(H/'README.md').write_text('''# Spirewatch v8 — finishing pass

2026-10-21. User authorized the four proposed finishing changes with "go". This is a review candidate; no final artistic acceptance is inferred.

- [60-second preview](spirewatch-v8-preview-60s.mp4)
- [Three-loop review](spirewatch-v8-three-loops-180s.mp4)
- [Eight-second combined test, scene 12–20s](combined-v8-test-8s.mp4)

Added anchored spray at the three waterfall outlets. Small overlapping wisps rise, expand, drift slightly right and dissolve inside mapped masks, with foreground roof/ledge exclusions. The first sampled placement was lost in bright water; the origins/drift were adjusted toward the darker adjacent stone, retaining modest opacity. This is a restrained finishing layer, not a new large fog bank.

Rain streaks now briefly catch the local lightning, with strength falling off spatially from each flash. Rain density, paths, shower timing and normal brightness remain unchanged. The two showers overlap flashes near 18.4 and 43.2 seconds. Lightning does not globally brighten the room.

Four independently timed red/amber beacons sit on existing antenna tips at native coordinates (343,232), (1277,29), (1157,382), (1647,380). Initial candidate coordinates left some cores detached from visible mast tips; source crops were used to remap them before the full minute. The initial short tests/config remain under history/. Soft cores/halos and 10/12/15/20-second periods keep them secondary to the city.

The main tower sweep eases into the crown, holds approximately 15–18s, then eases down through 34s. A second rise ends at 53s, holds to 56s and fades by 59s. Position has zero speed at the crown transition. The v7 narrow emitter mask and foundation protection remain: tower/glow are zero at and below native y425. No broad facade dimming or global exposure changes.

Thirteen existing isolated layers match v7 exactly at six sampled times: clouds, water, waterfalls, district lights, warm windows, transit, reflections, screen, lamp, screen spill, normal rain, lightning and storm response. Full source/endpoint checks, all 1800/5400 decoded frames/timestamps, regional and quiet-neighbour seams, exact three repeats and six contiguous-render boundary pictures passed. Four short tests cover spray, rain illumination, beacons and composite. Assistant inspected native/decoded temporal stills, not continuous playback.

Same native 1672x941 source (SHA-256 e93d08a99ac2bfd7a20e17f0a3ad07d9e406300ab67f3dc98237490ab09b5af0). Silent 1280x720/30fps review; no music, 4K or long assembly. Original versions preserved. New files local, uncommitted and unpushed. See scene-plan-v8.json, feedback-and-plan.json and delivery-v8.json.

Reproduce with the existing Python runtime and PYTHONPATH=G:/AI/youtube/.runtime/scene-tools: check_v8.py, short_tests.py, render_parallel.py, render_spirewatch.py, check_chunk_joins.py. Eventual 4K uses the same native source and disclosed upscaling. Apply the established Colony intro once during final assembly.
''',encoding='utf-8')
direction=H.parent/'digital-city-concepts-v1/current-direction.json';d=read(direction);save('previous-direction.json',d)
d.update(date='2026-10-21',source='../spirewatch-animation-v8/artwork-v5.png',source_sha256=s.config['source']['sha256'],status='V8 finishing pass delivered; user playback review pending',animation_record='music/spirewatch-animation-v8/delivery-v8.json',animation_preview='music/spirewatch-animation-v8/spirewatch-v8-preview-60s.mp4',user_motion_approved=False,latest_feedback='User authorized proposed waterfall spray, rain illumination, antenna beacons and gentler tower turnaround. V6 much improved; v7 fixed its tower-foot defect and added weather.',backup_request='No new commit/push requested for v8')
direction.write_text(json.dumps(d,indent=2)+'\n')
pipeline=root/'PRODUCTION_PIPELINE.md';text=pipeline.read_text(encoding='utf-8');start=text.index('## Unnumbered city concept — Spirewatch');end=text.index('\n## ',start+4);save('previous-tracker-section.json',{'text':text[start:end]})
section='''## Unnumbered city concept — Spirewatch

2026-10-21: [V8 finishing pass](music/spirewatch-animation-v8/README.md) delivered after user authorized waterfall spray, lightning-lit rain, antenna beacons and a gentler tower turnaround. Thirteen existing layers match v7 at six sampled times; tower foundation protection remains. Genuine sixty-second silent 720p/30fps preview and exact three-repeat review pass full technical checks. Native/decoded stills inspected, not continuous playback; user review pending. Same bright source, no new music/4K/long assembly. Earlier versions preserved. Unnumbered, local/uncommitted/unpushed.
'''
pipeline.write_text(text[:start]+section+text[end:],encoding='utf-8')
agents=root/'AGENTS.md';text=agents.read_text(encoding='utf-8');heading='# Ambient Colony — working instructions';note='Current Spirewatch v8 (2026-10-21): user authorized the four finishing suggestions with "go". music/spirewatch-animation-v8/ adds anchored, roof-occluded waterfall spray, rain illuminated locally during flashes, four independent red/amber antenna beacons and eased tower travel/crown holds (15–18 and 53–56s). Narrow tower emitter and y425 foundation protection retained. Thirteen other layers match v7 at six times. Genuine silent sixty-second 720p and three-repeat review passed full technical checks. Assistant inspected temporal/decoded stills, not continuous playback. User v8 review pending; no music/4K/long assembly/commit/push. See README.md and delivery-v8.json.'
assert 'Current Spirewatch v8 (2026-10-21):' not in text
text=text.replace('Current Spirewatch v7 (2026-10-21):','Historical Spirewatch v7 (2026-10-21):',1)
agents.write_text(text.replace(heading,heading+'\n\n'+note,1),encoding='utf-8')
bank=root/'creative/ANIMATION_KNOWLEDGE_BANK.md';text=bank.read_text(encoding='utf-8');heading='## Spirewatch animation candidate — latest 2026-10-21'
note='**V8 finishing candidate; user playback approval pending.** User authorized the proposed polish. [V8](../music/spirewatch-animation-v8/README.md) anchors small expanding/rising spray wisps at actual waterfall outlets and restores foreground ledge masks. A spray overlay lost against white water was shifted toward adjacent darker stone, rather than made globally opaque. Rain illumination affects the existing streak field only and uses each flash’s location; normal rain stays exact. Four small independent tip beacons and eased travel with crown holds complete the pass. Retain the narrow tower emitter/foundation fix. Thirteen prior isolated layers match at six times. These are technically checked candidates, not accepted universal presets.'
assert note not in text;bank.write_text(text.replace(heading,heading+'\n\n'+note,1),encoding='utf-8')
print('V8 delivery and project learnings saved')
