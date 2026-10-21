from pathlib import Path
import json
from render_spirewatch import H,Spirewatch,save,sha
s=Spirewatch();R=H.parents[1]
analytic=json.loads((H/'analytic-validation.json').read_text());preview=json.loads((H/'preview-validation.json').read_text());repeat=json.loads((H/'repeat-validation.json').read_text());chunks=json.loads((H/'chunk-join-validation.json').read_text());tests=json.loads((H/'short-tests.json').read_text())
assert analytic['pass'] and analytic['fingerprint']==s.fingerprint()
assert preview['fingerprint']==s.fingerprint() and preview['frames']==1800
assert repeat['frames']==5400 and repeat['three_exact_decoded_repetitions']
assert chunks['pass'] and chunks['fingerprint']==s.fingerprint()
assert tests['fingerprint']==s.fingerprint() and len(tests['clips'])==4
save('artwork-generation.json',{'date':'2026-10-21','tool':'Built-in image_gen','mode':'edit','reference':'music/spirewatch-animation-v4/thumbnail-v1.png','reference_sha256':sha(H.parent/'spirewatch-animation-v4/thumbnail-v1.png'),'exact_prompt':'artwork-generation-prompt.txt','output':s.config['source'],'dimensions':[1672,941],'upscaled':False,'purpose':'Clean thumbnail-faithful animation plate','assistant_inspection':'Clean plate compared at same display size to thumbnail; city, spire, reflections and room retain brightness/colour hierarchy. Small generated geometry/material details may differ.','user_approved':False})
save('visual-review.json',{'date':'2026-10-21','status':'User playback review pending','previous_verdict':'V4 rejected: thumbnail much brighter/more exciting than animation','response':'Rebuilt clean plate directly from thumbnail and redrew masks. Main city/room/spire brightness compares closely to thumbnail; see source-comparison.json.','assistant_inspected':['clean source and reference at full composition','native composite states','tower/screen/bridge temporal crops','decoded preview stills'],'continuous_playback':False,'internal_fix':'Initial cloud mask included a few roof/antenna edges. Expanded skyline/mast exclusions and added source-distance-bounded transport. First mask-pass stills/config preserved in history/.','user_artwork_approved':False,'user_motion_approved':False,'known_limits':['60-second silent 720p review; no 4K or long assembly','No new eight-minute music received; no sync claim','Cloud motion tapers near solid boundaries to protect geometry','Existing thumbnail is a marketing reference; generated clean plate fine details may differ']})
save('delivery-v5.json',{'date':'2026-10-21','status':'Technically verified preview; user visual review pending','source':s.config['source'],'fingerprint':s.fingerprint(),'preview':str(H/'spirewatch-v5-preview-60s.mp4'),'repeat':str(H/'spirewatch-v5-three-loops-180s.mp4'),'preview_validation':preview,'repeat_validation':repeat,'chunk_checks':chunks,'artwork':str(H/'artwork-v5.png'),'user_motion_approved':False,'assistant_continuous_playback':False,'four_k':None,'audio':None,'committed':False,'pushed':False})
(H/'README.md').write_text('''# Spirewatch v5 — bright thumbnail-derived rebuild

Delivered 2026-10-21. Technically verified; user playback review pending. V4 was rejected because its older dark plate did not match its much brighter thumbnail. V5 uses a new clean plate edited directly from that thumbnail.

- [Complete sixty-second preview](spirewatch-v5-preview-60s.mp4)
- [Three exact repeats, 180-second review](spirewatch-v5-three-loops-180s.mp4)
- [New clean artwork](artwork-v5.png)
- [Thumbnail reference](../spirewatch-animation-v4/thumbnail-v1.png)
- [Exact built-in imagegen prompt](artwork-generation-prompt.txt)

The cyan spire, warm city/room, bright bridge and reflective water are present in the source itself. The animation does not dim them toward the old plate. Normal frame brightness in sampled city/room/spire regions closely matches the thumbnail (source-comparison.json); these are descriptive measurements, not a percentage quality claim.

All coordinates/masks were redrawn for the new 1672x941 plate. V4 masks were not reused. Upper clouds move faster than lower sky haze, with source-distance bounds protecting structures. Source waterfall material travels downward; water has calm bounded ripples. The tower sends light upward at 3–18s, holds at its crown, then returns downward at 37–54s. District channels acknowledge with delays. Cyan/amber/cyan bridge traffic occurs at 4–21 / 25–43 / 46–59s, with broken water responses. Warm windows have independent long holds. The original monitor map has tracking markers and a restrained scan. Lamp dips are around 32s; local intracloud light peaks around 28.6/54.6s. No detached lightning graphic or global exposure pulse.

First cloud-mask samples revealed pulled roof/antenna details; those were corrected before encoded previews. The rejected mask-pass stills/config are retained under history/first-mask-pass/. Assistant inspected source, native temporal samples and decoded stills, not continuous playback.

All layer endpoints/protected source checks, every 1800/5400 decoded frame/timestamp, regional/composite and quiet-neighbour seams, exact repeats and six contiguous-render boundary pictures passed. Four eight-second full-frame tests cover clouds, tower, transit and composite. Records: analytic-validation.json, short-tests.json, preview-validation.json, repeat-validation.json, chunk-join-validation.json and delivery-v5.json.

No new music received, so eight-minute music synchronization remains pending. Preview is silent 1280x720/30fps, not a 4K or long final. Earlier versions remain preserved. New media/records are local, uncommitted and unpushed.

Reproduce with existing Python runtime plus PYTHONPATH=G:/AI/youtube/.runtime/scene-tools: check_v5.py, render_parallel.py, render_spirewatch.py, check_chunk_joins.py. Config is scene-plan-v5.json. Rendering refuses existing destinations. Native artwork is 1672x941; any eventual 4K delivery is an upscale. Preserve clean scene loops and apply the established Colony opening once during final assembly.
''',encoding='utf-8')
direction=H.parent/'digital-city-concepts-v1/current-direction.json';d=json.loads(direction.read_text(encoding='utf-8-sig'));save('previous-direction.json',d)
d.update(date='2026-10-21',source='../spirewatch-animation-v5/artwork-v5.png',source_sha256=s.config['source']['sha256'],status='V5 thumbnail-derived clean plate and remapped animation delivered; user playback review pending',animation_record='music/spirewatch-animation-v5/delivery-v5.json',animation_preview='music/spirewatch-animation-v5/spirewatch-v5-preview-60s.mp4',user_motion_approved=False,latest_feedback='V4 was rejected for being darker than thumbnail. User authorized execution of the clean-plate animation rebuild.',backup_request='No new commit/push requested for v5; older backups remain separate')
direction.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
pipeline=R/'PRODUCTION_PIPELINE.md';text=pipeline.read_text(encoding='utf-8');a=text.index('## Unnumbered city concept — Spirewatch');b=text.index('\n## ',a+4);save('previous-tracker-section.json',{'text':text[a:b]})
section='''## Unnumbered city concept — Spirewatch

2026-10-21: [V5 bright rebuild](music/spirewatch-animation-v5/README.md) delivered: clean artwork derived directly from the thumbnail, new source-bound masks and genuine sixty-second 720p/30fps animation with three-repeat review. Source city/room/spire illumination closely matches the thumbnail. Moving clouds/waterfalls/water, tower/district sequences, transit/reflections, warm windows and monitor/lamp activity are remapped. Full technical checks passed; assistant inspected stills, not continuous playback. User playback review pending. V4 was rejected for its darker scene and remains preserved. Eight-minute Vast Unfamiliar World generation is in progress but audio has not been supplied; music sync, 4K and final assembly remain pending. Unnumbered. New v5 files are local/uncommitted/unpushed.
'''
pipeline.write_text(text[:a]+section+text[b:],encoding='utf-8')
agents=R/'AGENTS.md';text=agents.read_text(encoding='utf-8');heading='# Ambient Colony — working instructions'
note='Current Spirewatch v5 (2026-10-21): user authorized the thumbnail-faithful rebuild after rejecting darker v4. Delivered music/spirewatch-animation-v5/ with clean artwork-v5.png (1672x941, SHA-256 '+s.config['source']['sha256']+'), newly mapped masks, genuine sixty-second silent 720p/30fps preview and exact three-repeat review. Source city/room/spire brightness closely matches thumbnail; no return to old dark plate. First sky mask pulled some roof/antenna edges; corrected before encoding, first samples/config retained. Full analytical/decode/timestamp/regional/quiet-neighbour/chunk-boundary checks passed. Assistant inspected stills, not continuous playback. User artwork/motion review pending. No new eight-minute music received, no sync/4K/long assembly yet. Earlier versions and unrelated work preserved. New v5 local/uncommitted/unpushed. See README.md, delivery-v5.json and visual-review.json.'
assert 'Current Spirewatch v5 (2026-10-21):' not in text
agents.write_text(text.replace(heading,heading+'\n\n'+note,1),encoding='utf-8')
bank=R/'creative/ANIMATION_KNOWLEDGE_BANK.md';text=bank.read_text(encoding='utf-8');heading='## Spirewatch animation candidate — latest 2026-10-21'
note='**V5 rebuild executed; user review pending.** [New source and delivery](../music/spirewatch-animation-v5/README.md) use the bright thumbnail itself as the clean-plate edit reference. Matched-region city/room/spire luma stays close to the thumbnail through sampled animation states, resolving the measured baseline exposure gap without a global animated gain. Fine geometry changed, so all masks were redrawn. First sky masks accidentally moved roof/mast fragments: conservative skyline/mast exclusions plus distance-bounded source transport corrected sampled edges before video. Source brightness is independent of occasional lightning. Full technical gates passed; decoded/native still inspection does not imply artistic acceptance. Preserve rejected v4 and its feedback below as history.'
assert note not in text;bank.write_text(text.replace(heading,heading+'\n\n'+note,1),encoding='utf-8')
print('V5 delivery and current project records saved',flush=True)
