"""Record only verified delivery; preserve unrelated shared-document content."""
from pathlib import Path
import json,hashlib,shutil
from PIL import Image
from render_spirewatch import H,Spirewatch,save,sha
R=H.parents[1];s=Spirewatch()
analytic=json.loads((H/'analytic-validation.json').read_text())
preview=json.loads((H/'preview-validation.json').read_text())
repeat=json.loads((H/'repeat-validation.json').read_text())
chunks=json.loads((H/'chunk-join-validation.json').read_text())
assert analytic['pass'] and analytic['fingerprint']==s.fingerprint()
assert preview['fingerprint']==s.fingerprint() and preview['frames']==1800
assert repeat['frames']==5400 and repeat['three_exact_decoded_repetitions']
assert chunks['pass'] and chunks['fingerprint']==s.fingerprint()
assert (H/'principal-layer-tests.json').exists() and (H/'isolated-test-validation.json').exists()
save('visual-review.json',{'date':'2026-10-21','status':'User review pending','assistant_inspection':'Full-composition native and decoded stills; native temporal crops for tower, bridge and screen. No continuous playback or listening claim.','observed':['Main spire brightness band changes vertical position in temporal samples','Original architecture and monitor layout preserved','Source-mapped cyan/amber route light follows bridge','Thumbnail text is correctly spelled and main spire remains unobstructed'],'internal_revision':'First still lightning branches reduced to 32% of v3 branch contribution; broad cloud illumination retained. First review stills were replaced by final-state samples before encoding; earlier v3 remains intact.','limitations':['Thumbnail is generated marketing adaptation with fine geometry/lighting differences','No eight-minute audio supplied; music-aligned envelope remains future work','Lamp reflection intentionally faint; user should judge in playback','720p review, not 4K or long final assembly'],'user_motion_approved':False,'user_thumbnail_approved':False})
save('thumbnail-generation.json',{'date':'2026-10-21','tool':'Built-in image_gen','mode':'edit','reference':s.config['source'],'exact_prompt_file':'thumbnail-prompt-v1.txt','png':{'path':'thumbnail-v1.png','sha256':sha(H/'thumbnail-v1.png'),'dimensions':list(Image.open(H/'thumbnail-v1.png').size)},'jpeg':{'path':'thumbnail-v1.jpg','sha256':sha(H/'thumbnail-v1.jpg'),'dimensions':list(Image.open(H/'thumbnail-v1.jpg').size)},'conversion':'FFmpeg Lanczos 1280x720 JPEG q2','role':'Marketing adaptation, not animation source','user_approved':False})
save('delivery-v4.json',{'date':'2026-10-21','status':'Technically verified; artistic review pending','source':s.config['source'],'fingerprint':s.fingerprint(),'preview':str(H/'spirewatch-v4-preview-60s.mp4'),'preview_validation':preview,'repeat':str(H/'spirewatch-v4-three-loops-180s.mp4'),'repeat_validation':repeat,'chunk_checks':chunks,'thumbnail':str(H/'thumbnail-v1.jpg'),'user_motion_approved':False,'assistant_continuous_playback':False,'audio':None,'four_k':None,'committed':False,'pushed':False})
(H/'README.md').write_text('''# Spirewatch v4 — connected digital city

Delivered 2026-10-21. Technically verified; user animation and thumbnail review pending. Earlier versions preserved.

- **Watch:** [complete sixty-second preview](spirewatch-v4-preview-60s.mp4).
- **Join review:** [three exact repetitions, 180 seconds](spirewatch-v4-three-loops-180s.mp4).
- **Thumbnail:** [1280x720 JPEG](thumbnail-v1.jpg), [native generated PNG](thumbnail-v1.png), [exact generation prompt](thumbnail-prompt-v1.txt).
- **Music:** [eight-minute prompt](music-prompt-eight-minutes.txt). User is generating the track; no new audio was received or evaluated in this pass.

The main spire charges near its base, sends staggered light up existing channels (3–17s), holds near its crown, then sends a later return downward (37–53s). Six cyan districts respond with delays. Three bridge passages (4–20s cyan, 25–42s amber, 45–59s cyan) have attached trails and broken water reflections. The original monitor map has transit tracking and small acknowledgements; warm windows have slower independent holds. Two local cloud storms peak around 28.6 and 54.6 seconds. A faint lamp reflection follows its local lighting state.

The exact same 1672x941 source is retained. Eight weather/water/lamp layers match v3 exactly at five sampled times. New light reflections do not increase water displacement. Geometry stays fixed; thumbnail pixels never enter animation. The generated thumbnail has brighter marketing lighting and some fine-geometry differences from the clean scene.

Validated all native layer endpoints/source protection, all 1800/5400 decoded frames and timestamps, regional/composite and quiet-neighbour seams, exact three-cycle identity, and all six contiguous-render boundary pictures. Details: analytic-validation.json, preview-validation.json, repeat-validation.json, chunk-join-validation.json, delivery-v4.json. The assistant inspected native/decoded stills and temporal crops, not continuous playback.

No 4K, long combined video or music sync yet. Lighting has an activity control for the eventual eight-minute energy arc; actual timings await the supplied music. No commit/push in this session; new files are local.

Reproduction: use the existing Python runtime and PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. The versioned package already contains its source/config/dependency snapshot; do not rerun setup_v4.py. Check with check_v4.py; render with render_parallel.py; verify with render_spirewatch.py --stage verify and check_chunk_joins.py. Render destinations must be absent; preserve previous outputs before any deliberate revision.
''',encoding='utf-8')
# Shared records: read current versions immediately before scoped changes.
direction=H.parent/'digital-city-concepts-v1/current-direction.json'
previous=json.loads(direction.read_text());save('previous-direction.json',previous)
previous.update(date='2026-10-21',status='V4 connected-city minute and thumbnail delivered; user review pending',animation_record='music/spirewatch-animation-v4/delivery-v4.json',animation_preview='music/spirewatch-animation-v4/spirewatch-v4-preview-60s.mp4',user_motion_approved=False,latest_feedback='User requested implementing as much of the proposed TRON-inspired improvements as possible; eight-minute music generation in progress.',long_audio_selected=False,thumbnail='music/spirewatch-animation-v4/thumbnail-v1.jpg',backup_request='No new commit/push requested for v4; prior v3 backup preserved')
direction.write_text(json.dumps(previous,indent=2)+'\n',encoding='utf-8')
pipeline=R/'PRODUCTION_PIPELINE.md';text=pipeline.read_text(encoding='utf-8');start=text.index('## Unnumbered city concept — Spirewatch');end=text.index('\n## ',start+4)
save('previous-tracker-section.json',{'text':text[start:end]})
section='''## Unnumbered city concept — Spirewatch

2026-10-21: [V4 minute, three-repeat review and thumbnail](music/spirewatch-animation-v4/README.md) delivered. Connected main-spire charge/up/crown/down sequence, delayed district responses, cyan/amber transit trails and mapped water light reflections, subtle monitor tracking, slower warm-window schedules and two localized cloud storms. Same 1672x941 clean plate; eight weather/water/lamp layers match v3 at five sampled states. Full technical checks passed; assistant inspected stills, not continuous playback. User animation/thumbnail review pending. User is generating an eight-minute Vast Unfamiliar World development (pulse to ambient middle and back); audio not yet supplied. Music sync, 4K and final assembly remain pending. Unnumbered; v1–v3 preserved and v3 backup remains separate. New v4 files are local, uncommitted and unpushed.
'''
pipeline.write_text(text[:start]+section+text[end:],encoding='utf-8')
agents=R/'AGENTS.md';text=agents.read_text(encoding='utf-8');marker='Current Spirewatch v4 (2026-10-21):'
assert marker not in text
text=text.replace('# Ambient Colony — working instructions','# Ambient Colony — working instructions\n\n'+marker+' Connected-city revision and TRON-inspired thumbnail delivered in music/spirewatch-animation-v4/. Genuine sixty-second 720p/30fps preview and exact three-repeat review; full technical gates passed. Same source as v3, eight retained layers sampled byte-identically. Main-spire charge/up/crown/down cycle, delayed cyan district responses, perspective cyan/amber transit with water reflections, original monitor-map tracking, slower warm windows, faint lamp-linked glass reflection and two local storms. User playback/thumbnail review pending; assistant inspected stills only. Eight-minute Vast Unfamiliar World music generation in progress, no new audio received; musical envelope timing, 4K and final assembly pending. Thumbnail is a separate generated marketing adaptation, never a clean animation source. Earlier versions and unrelated work preserved. New v4 files local/uncommitted/unpushed. See README.md, delivery-v4.json, visual-review.json and creative-brief.txt.',1)
agents.write_text(text,encoding='utf-8')
bank=R/'creative/ANIMATION_KNOWLEDGE_BANK.md';text=bank.read_text(encoding='utf-8');marker='## Spirewatch animation candidate — 2026-10-11';assert marker in text
text=text.replace(marker,'''## Spirewatch animation candidate — latest 2026-10-21

**V4 implemented, technically verified, user review pending.** [V4 package](../music/spirewatch-animation-v4/README.md). Coordinate emissive systems with delays rather than simply raising every light: one source-bound tower cycle, independent district acknowledgements, perspective transit trails and corresponding broken water response. Keep water displacement independent of reflection brightness. Preserve monitor-map detail with small markers instead of replacing it with a large graph. Longer window holds keep human habitation distinct from equipment pulses. Faint lamp reflection is an artistic approximation pending review. First branch still was too explicit; reduce branch contribution while retaining cloud illumination. Eight retained layers match v3 at five sampled times. The forthcoming eight-minute music is not yet received: expose a lighting-activity control without inventing synchronization or changing environmental velocity. Generated thumbnail may differ in fine geometry and must not become the motion plate. Native/decoded still inspection is separate from playback approval. Earlier v3 status below is historical.
''',1)
bank.write_text(text,encoding='utf-8')
print('Verified delivery, provenance and scoped current records saved')
