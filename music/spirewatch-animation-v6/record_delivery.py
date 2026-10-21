from pathlib import Path
import json
from render_spirewatch import H,Spirewatch,save,sha
s=Spirewatch();fp=s.fingerprint();root=H.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
a=read(H/'analytic-validation.json');v=read(H/'preview-validation.json');r=read(H/'repeat-validation.json');c=read(H/'chunk-join-validation.json');q=read(H/'short-tests.json')
assert a['pass'] and a['fingerprint']==fp
assert v['fingerprint']==fp and v['frames']==1800 and v['full_decode']
assert r['frames']==5400 and r['three_exact_decoded_repetitions']
assert c['pass'] and c['fingerprint']==fp
assert q['fingerprint']==fp and len(q['clips'])==4
save('delivery-v6.json',{'date':'2026-10-21','status':'Technically verified; user playback review pending','preview':'spirewatch-v6-preview-60s.mp4','repeat':'spirewatch-v6-three-loops-180s.mp4','fingerprint':fp,'preview_sha256':sha(H/'spirewatch-v6-preview-60s.mp4'),'verification':{'analytic':'analytic-validation.json','short_tests':'short-tests.json','minute':'preview-validation.json','three_repeats':'repeat-validation.json','chunk_joins':'chunk-join-validation.json'},'assistant_review':'Native and decoded temporal stills inspected; no continuous playback','user_approved':False,'music_received':False,'four_k':False,'committed':False,'pushed':False})
(H/'README.md').write_text('''# Spirewatch v6 — readable city motion

2026-10-21. User rejected v5: "this isn't looking good at all, i can barely see any movement appart from the pc screen and the clouds". V5 remains preserved; v6 is a new candidate awaiting playback review.

- [Full 60-second preview](spirewatch-v6-preview-60s.mp4)
- [Three consecutive repeats](spirewatch-v6-three-loops-180s.mp4)
- [Eight-second full-scene test](combined-v6-test-8s.mp4)

Same bright 1672x941 artwork as v5. The main failure was additive light over already bright source emissions: visible source streaks stayed static. V6 modulates complete emitters, including white cores, from a dimmer standby state into travelling light. Main tower rises 1–15s, descends 20–34s, rises again 39–53s. Six tightly mapped city/support light regions have staggered travelling bands. Cyan and amber bridge lanes use visible moving sections with opposite travel directions and corresponding broken water reflections. Original monitor timing remains unchanged.

The waterfalls now carry larger downward-travelling filaments instead of relying on low-contrast source residual. Basin reflection motion is stronger and edge-damped. 183 complete warm apertures form 55 independent groups with local spill and two separated holds per minute. Whole-frame exposure is unchanged; the local emitting strips have dimmer quiet states to make movement distinguishable. No bright/dark percentage is claimed as an artistic improvement.

Initial strengthened district masks caught blue sky; replaced box bounds with tight emitter polygons. Initial traffic dimming had hard edges; source-lane masks now have smooth falloff. Initial district restart failed the analytical seam gate; local entrance/exit envelopes corrected the reset. Early stills remain local as history.

Clouds, screen, lamp, screen spill, lightning and storm response match v5 exactly at six sampled times. All layer endpoints/protected source checks, full 1800/5400-frame decoding/timestamps, regional and quiet-neighbour seams, exact repetitions and six chunk-boundary pictures passed. Four isolated/composite eight-second tests also passed. Assistant inspected native/decoded still sequences, not continuous playback. Technical success does not establish the user's artistic acceptance.

Silent 1280x720/30fps review. No eight-minute music received, 4K or final assembly. Source is native 1672x941; eventual 4K is an upscale. Preserve clean loops; Colony intro applies once during final assembly. New files local, uncommitted and unpushed.

Reproduce with the established Python runtime and PYTHONPATH=G:/AI/youtube/.runtime/scene-tools: check_v6.py, short_tests.py, render_parallel.py, render_spirewatch.py, check_chunk_joins.py. Outputs refuse overwrite. Use scene-plan-v6.json and delivery-v6.json for exact fingerprints.
''',encoding='utf-8')
# Preserve previous states before scoped current-status updates.
old=H.parent/'spirewatch-animation-v5/visual-review.json';d=read(old);save('previous-v5-review.json',d);d.update(status='Rejected by user for motion visibility',latest_user_feedback=read(H/'feedback-and-plan.json'));old.write_text(json.dumps(d,indent=2)+'\n')
direction=H.parent/'digital-city-concepts-v1/current-direction.json';d=read(direction);save('previous-direction.json',d)
d.update(date='2026-10-21',source='../spirewatch-animation-v6/artwork-v5.png',source_sha256=s.config['source']['sha256'],status='V6 city-motion correction delivered; user playback review pending',animation_record='music/spirewatch-animation-v6/delivery-v6.json',animation_preview='music/spirewatch-animation-v6/spirewatch-v6-preview-60s.mp4',user_motion_approved=False,latest_feedback='V5 rejected: movement only obvious on screen and clouds. V6 uses complete emitter contrast, travelling traffic, falling filaments and wider warm-window coverage.',backup_request='No new commit/push requested for v6')
direction.write_text(json.dumps(d,indent=2)+'\n')
pipeline=root/'PRODUCTION_PIPELINE.md';text=pipeline.read_text(encoding='utf-8');start=text.index('## Unnumbered city concept — Spirewatch');end=text.index('\n## ',start+4);save('previous-tracker-section.json',{'text':text[start:end]})
section='''## Unnumbered city concept — Spirewatch

2026-10-21: [V6 visibility correction](music/spirewatch-animation-v6/README.md) delivered after user rejected v5 as nearly static apart from clouds/screen. Same bright source, complete emitter dim-to-bright travel on tower and six city regions, opposed bridge traffic with water response, stronger falling filaments and 183 warm apertures in 55 groups. Clouds/screen and four other layers retained at six sampled times. Genuine sixty-second silent 720p/30fps preview and exact three-repeat review; full technical checks passed. Assistant inspected temporal/decoded stills, not continuous playback. User playback review pending. V5/v4 preserved with rejection history. Eight-minute Vast Unfamiliar World not yet received; music/4K/final assembly pending. Unnumbered, local/uncommitted/unpushed.
'''
pipeline.write_text(text[:start]+section+text[end:],encoding='utf-8')
agents=root/'AGENTS.md';text=agents.read_text(encoding='utf-8');heading='# Ambient Colony — working instructions';note='Current Spirewatch v6 (2026-10-21): user rejected v5 because movement was only apparent on PC/clouds. music/spirewatch-animation-v6/ delivers the same bright native plate with complete emitter dim-to-bright travel, three tower sweeps, six tight district regions, opposed cyan/amber traffic and broken reflections, larger downward waterfall features, stronger bounded water and 183 apertures/55 warm groups. Six unchanged layers match v5 at sampled times. Full minute/repeat/region/seam/chunk checks passed. Assistant inspected temporal/decoded stills, not continuous playback. User playback review pending; no music/4K/long assembly/commit/push. See README.md, delivery-v6.json and exact feedback. V5 is rejected for motion visibility, v4 for thumbnail mismatch; both preserved.'
assert 'Current Spirewatch v6 (2026-10-21):' not in text
text=text.replace('Current Spirewatch v5 (2026-10-21):','Historical Spirewatch v5 (2026-10-21; subsequently rejected for motion visibility):',1)
agents.write_text(text.replace(heading,heading+'\n\n'+note,1),encoding='utf-8')
bank=root/'creative/ANIMATION_KNOWLEDGE_BANK.md';text=bank.read_text(encoding='utf-8');heading='## Spirewatch animation candidate — latest 2026-10-21'
note='**V5 rejected for motion visibility; v6 is a candidate, not accepted.** The user could only readily see PC/cloud movement. Matching thumbnail brightness solved a different problem. Add-only cyan/traffic light over already bright source strips failed again: animate complete emitters including white cores, creating visible local contrast and spatial travel. [V6](../music/spirewatch-animation-v6/README.md) changes shape/coverage before increasing light: moving traffic sections, stronger falling material, 183 warm apertures/55 groups. Stronger modulation exposed cyan sky accidentally included in district boxes; use tightly mapped emitter polygons. Smooth traffic masks avoid hard dark contours. Local envelopes remove district reset discontinuities. Preserve cloud/screen behaviour with sampled exact comparisons. Full technical gates passed but temporal still inspection is not playback approval.'
assert note not in text
bank.write_text(text.replace(heading,heading+'\n\n'+note,1),encoding='utf-8')
print('V6 delivery, rejection history and project learnings saved')
