import json
from render_spirewatch import H,Spirewatch,save,sha
s=Spirewatch();fp=s.fingerprint();root=H.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
a=read(H/'analytic-validation.json');v=read(H/'preview-validation.json');r=read(H/'repeat-validation.json');c=read(H/'chunk-join-validation.json');q=read(H/'short-tests.json')
assert a['pass'] and a['fingerprint']==fp and a['tower_and_glow_zero_below_source_y425']
assert v['fingerprint']==fp and v['frames']==1800 and v['full_decode']
assert r['frames']==5400 and r['three_exact_decoded_repetitions']
assert c['pass'] and c['fingerprint']==fp and q['fingerprint']==fp and len(q['clips'])==4
save('delivery-v7.json',{'date':'2026-10-21','status':'Technically verified; user playback review pending','preview':'spirewatch-v7-preview-60s.mp4','repeat':'spirewatch-v7-three-loops-180s.mp4','fingerprint':fp,'preview_sha256':sha(H/'spirewatch-v7-preview-60s.mp4'),'verification':['analytic-validation.json','short-tests.json','preview-validation.json','repeat-validation.json','chunk-join-validation.json'],'assistant_review':'Native and decoded temporal stills, not continuous playback','user_approved':False,'music_received':False,'four_k':False,'committed':False,'pushed':False})
body='''# Spirewatch v7 — tower fix and passing weather

2026-10-21. V6 received positive feedback ("much improved") but the user identified an intermittent floating-looking tower and requested lightning across the sky, asking whether occasional rain would fit. V7 is a candidate for review, not user-approved.

- [60-second preview](spirewatch-v7-preview-60s.mp4)
- [Three-loop review](spirewatch-v7-three-loops-180s.mp4)
- [Tower correction](tower-fix-review.png)

The tower defect came from the colour mask selecting blue wall/fog as well as lights. Its lower boundary created a horizontal dark cut. V7 selects narrow, locally bright emitters, retains the travelling light schedule and smoothly protects the foundation: tower and glow masks are exactly zero at and below native y425. The source geometry and original base fog remain intact. Stronger lighting must not dim broad blue structure simply because it shares the emitter colour.

Five localized intracloud flashes peak around 6.6, 18.4, 30.6, 43.2 and 55 seconds, distributed left/centre/right across the sky. Fine irregular branches are partly veiled by source clouds. The first internal full render exposed dark rectangles above left roofs because the conservative motion exclusions were still too broad for illumination. Those rooflines were remapped tightly and reinspected at flash peaks; the first pass is preserved in history/first-lightning-silhouette/. Illumination uses a tighter silhouette than transported clouds. Each event has its own spatially related water response; no global room flash.

Two exterior rain showers run approximately 11–26 and 37–53 seconds, including smooth 3–4-second entrances/exits. Sparse three-depth streaks stay within the window view and outside the room/frame/monitor. No rain audio, glass streaks or music synchronization. This is an artistic rain trial, not an accepted preset.

Ten retained layers match v6 exactly at six sampled times: clouds, water, waterfalls, district lights, warm windows, transit, transit reflections, screen, lamp and screen spill. Full layer/endpoint/source checks, 1800/5400-frame decoding/timestamps, regional and quiet-neighbour seams, exact repetitions and six chunk-boundary comparisons passed. Four eight-second tests cover the tower, lightning, rain and combined scene, using actual timeline offsets. Assistant inspected native/decoded temporal stills, not continuous playback.

Same native 1672x941 bright artwork, SHA-256 e93d08a99ac2bfd7a20e17f0a3ad07d9e406300ab67f3dc98237490ab09b5af0. Silent 1280x720/30fps review, no 4K or long assembly. New music remains outstanding. Earlier versions preserved; new records/media local, uncommitted and unpushed. See scene-plan-v7.json, feedback-and-plan.json and delivery-v7.json.

Reproduce with the existing Python runtime and PYTHONPATH=G:/AI/youtube/.runtime/scene-tools: check_v7.py, short_tests.py, render_parallel.py, render_spirewatch.py, check_chunk_joins.py. Future 4K uses the same native source and disclosed upscaling; apply Colony intro once during final assembly.
'''
(H/'README.md').write_text(body,encoding='utf-8')
direction=H.parent/'digital-city-concepts-v1/current-direction.json';d=read(direction);save('previous-direction.json',d)
d.update(date='2026-10-21',source='../spirewatch-animation-v7/artwork-v5.png',source_sha256=s.config['source']['sha256'],status='V7 tower-foot correction and weather trial delivered; user playback review pending',animation_record='music/spirewatch-animation-v7/delivery-v7.json',animation_preview='music/spirewatch-animation-v7/spirewatch-v7-preview-60s.mp4',user_motion_approved=False,latest_feedback='V6 much improved; floating-looking tower mask defect. Broader lightning requested; occasional rain trial.',backup_request='No new commit/push requested for v7')
direction.write_text(json.dumps(d,indent=2)+'\n')
pipeline=root/'PRODUCTION_PIPELINE.md';text=pipeline.read_text(encoding='utf-8');start=text.index('## Unnumbered city concept — Spirewatch');end=text.index('\n## ',start+4);save('previous-tracker-section.json',{'text':text[start:end]})
section='''## Unnumbered city concept — Spirewatch

2026-10-21: [V7 tower/weather correction](music/spirewatch-animation-v7/README.md) delivered. User called v6 much improved but found a floating-looking tower mask. Narrow emitter selection and protected foundation remove its horizontal dimmed patch; five distributed intracloud flashes and two gentle exterior rain showers added. Ten retained layers match v6 at six sampled times. Genuine silent sixty-second 720p preview and exact three-repeat review pass full technical checks. Native/decoded stills inspected, not continuous playback; user review pending. Same bright source, no new music/4K/long assembly. Earlier versions preserved. Unnumbered, local/uncommitted/unpushed.
'''
pipeline.write_text(text[:start]+section+text[end:],encoding='utf-8')
agents=root/'AGENTS.md';text=agents.read_text(encoding='utf-8');heading='# Ambient Colony — working instructions';note='Current Spirewatch v7 (2026-10-21): v6 was "much improved" but user found a floating-looking tower, requested lightning across the sky and asked about occasional rain. V7 at music/spirewatch-animation-v7/ restricts the tower mask to narrow bright emitters and protects the foundation below y425, fixing broad blue wall/fog dimming with a flat boundary. Five distributed intracloud flashes (6.6/18.4/30.6/43.2/55s) and two exterior showers (11–26/37–53s) are a review candidate. Ten other layers match v6 at six times. Genuine sixty-second silent 720p and exact three-repeat review passed full technical checks. Assistant inspected temporal/decoded stills, not continuous playback. User v7 review pending, no music/4K/long assembly/commit/push. See README.md and delivery-v7.json.'
assert 'Current Spirewatch v7 (2026-10-21):' not in text
text=text.replace('Current Spirewatch v6 (2026-10-21):','Historical Spirewatch v6 (2026-10-21; subsequently much improved with tower-mask defect):',1)
agents.write_text(text.replace(heading,heading+'\n\n'+note,1),encoding='utf-8')
bank=root/'creative/ANIMATION_KNOWLEDGE_BANK.md';text=bank.read_text(encoding='utf-8');heading='## Spirewatch animation candidate — latest 2026-10-21'
note='**V6 positive checkpoint; v7 tower/weather candidate pending review.** User says v6 is "much improved", but the tower sometimes looks floating. Its cyan mask included broad blue structure/fog and ended in a horizontal cut. [V7](../music/spirewatch-animation-v7/README.md) selects narrow locally bright strips and smoothly protects the source foundation. A colour match alone does not identify an emitter. Five localized flashes span the sky using tighter illumination silhouettes and independent water responses; two sparse exterior rain showers have depth, smooth envelopes and protected interior/frame. Rain is a proposed trial, not an accepted universal addition. Ten retained layers match at six sampled times; technical checks do not imply playback approval.'
assert note not in text;bank.write_text(text.replace(heading,heading+'\n\n'+note,1),encoding='utf-8')
print('V7 delivery and current project learnings saved')
