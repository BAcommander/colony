from pathlib import Path
import json,hashlib
H=Path(__file__).parent;R=H.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
d=read(H/'delivery-v2.json');reports=[read(H/n) for n in ['analytic-validation.json','isolated-validation.json','targeted-validation.json','preview-validation.json']]
assert all(r['fingerprint']==d['fingerprint'] for r in reports)
assert d['preview_validation']['frames']==1800 and d['repeat_validation']['frames']==5400
assert d['repeat_validation']['three_exact_decoded_repetitions']
assert all(v['pass'] for v in d['preview_validation']['encoded_seams'].values())
assert (H/'encoded-inspection.json').exists()
assert read(H/'chunk-join-validation.json')['pass']
d['date']='2026-10-11';d['started']='2026-10-10';d['sky_correction_regression']='sky-correction-regression.json';d['parallel_render']='parallel-render.json';write(H/'delivery-v2.json',d)
iso=read(H/'isolated-validation.json');iso['retained_media_provenance']=read(H/'sky-correction-regression.json');write(H/'isolated-validation.json',iso)
write(H/'visual-review.json',{'status':'Candidate for user playback review','user_motion_approved':False,'assistant_continuous_playback':False,'inspection_notes':'inspection-notes.txt','encoded_inspection':'encoded-inspection.json','fingerprint':d['fingerprint'],'earlier_v1_verdict':'User said substantial improvements needed','current_authorization':'Implement all improvements, add lightning, foreground monitor movement, city motion/glows and up/down glow on the main tower','scope':'User authorized implementation, not artistic acceptance of the result'})
(H/'README.md').write_text('''# Spirewatch — animation v2

2026-10-11 (work begun 2026-10-10): requested rebuild with lightning, monitor movement, city activity and a travelling tower glow. Silent sixty-second 1280x720/30 fps preview; user visual review pending.

- [Complete minute](spirewatch-v2-preview-60s.mp4)
- [Three identical minute repetitions](spirewatch-v2-three-loops-180s.mp4)
- [Delivery record and hashes](delivery-v2.json), [scene configuration](scene-plan-v2.json), [inspection notes](inspection-notes.txt)

## Changes

Rebuilt the three waterfall materials using transported source texture, restrained falling threads and local spray; retained their fixed channels. Replaced the softened reconstructed water with detailed source ripples across ten bounded basin patches, damping edges and the far right. Clearer source-cloud travel is supported by separate valley/city mist moving behind structures.

Three lighted transit passages follow the existing elevated corridor. Six existing cyan-light regions have independent travelling glows; sixteen actual window apertures have staggered occupancy holds. Main-spire glow runs upward at 2–13 seconds, downward at 26–40 and upward again at 45–57, confined to eleven mapped existing light-strip regions. The tower and other structures do not move.

The original foreground map has a brighter travelling marker linked to transit progress, restrained node acknowledgements and data-panel updates, with small desk spill. Existing walkway and coupled desk-lamp dips are retained. No large waveform replaces the display.

Three local cloud-lightning events peak around 9.6, 34.6 and 52.6 seconds, with partially hidden short branches, cloud afterglow and faint exterior/water response. Room exposure stays stable. This is a cinematic optical approximation, not a physical simulation.

## Validation and review scope

Five isolated full-composition clips were fully decoded. Analytical periodicity/protected geometry, transported waterfall direction, tower up/down direction, transit direction, water-detail retention and final-third environmental activity were checked. Full combined/repeat decoding covers all 1,800/5,400 frames and sequential timestamps. Encoded per-layer/composite seams, quiet-neighbour seam checks, distinct 0/20/40 states, no duplicate endpoint and exact repeated minutes passed. Reports are linked in delivery-v2.json and the validation JSON files.

Assistant inspected source, masks, native temporal crops and colour-aware decoded stills, not continuous playback. These technical and sampled-image checks do not establish user artistic approval. Check waterfall character, lightning intensity, tower glow, transit attachment and monitor visibility during playback. Initial tower sky spill was corrected by separately tracing emitter strips; its first-study code/config/stills remain in history/first-study.

Final encoded inspection also caught a cloud-source reconstruction edge beside the tower. Normalized surrounding-sky reconstruction with a smooth transition fixed it in inspected samples. The earlier full encode and reports are preserved in history/pre-sky-correction. All fourteen non-sky layers match at six sampled times; unchanged isolated clips retain provenance. The corrected minute uses four contiguous locally rendered chunks at absolute scene time, not repeated footage; full decode and boundary checks cover the assembled file.

## Source and reproduction

Same immutable 1672x941 source at ../digital-city-concepts-v1/01-spirewatch-v2-cleanup.png, SHA-256 22553e407a8aac902a7eb55ddf52d544752a642856b3265ef2368741a0eadcba. V1 and other scenes are preserved. A future 4K delivery would upscale this native source.

render_spirewatch.py uses the scene-bound baseline.py and hash-verified dependencies snapshots; it does not modify shared approved renderers. Run --stage samples, check_motion.py, --stage isolated, then render_parallel.py and --stage verify with the bundled Python and PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. Existing preview videos are protected from overwrite. setup_scene.py is initial scaffolding, not a revision command; the checked scene-plan-v2.json is authoritative. record_delivery.py updates current project records only after evidence exists.

No music, 4K master, long assembly, upload, paid service, new model, commit or push in this delivery. New media remain local. The concept remains unnumbered; Vast Unfamiliar World is only its short musical direction.
''',encoding='utf-8')
manifest=[]
for p in sorted(H.rglob('*')):
 if not p.is_file() or '__pycache__' in p.parts or p.name=='package-manifest.json':continue
 with p.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
 manifest.append({'path':p.relative_to(H).as_posix(),'bytes':p.stat().st_size,'sha256':digest})
write(H/'package-manifest.json',{'date':'2026-10-11','files':manifest,'remote_backup':False,'user_motion_approved':False})
p=R/'music/digital-city-concepts-v1/current-direction.json';s=read(p)
s.update(status='V2 complete minute and repeat review delivered; user visual review pending',animation_record='music/spirewatch-animation-v2/delivery-v2.json',animation_preview='music/spirewatch-animation-v2/spirewatch-v2-preview-60s.mp4',user_motion_approved=False,latest_feedback='User authorized the complete improvement plan plus lightning, monitor movement, city activity/glows and a travelling main-tower glow')
write(p,s)
p=R/'PRODUCTION_PIPELINE.md';s=p.read_text(encoding='utf-8');a=s.index('## Unnumbered city concept — Spirewatch');b=s.index('## Next concept exploration',a)
s=s[:a]+'''## Unnumbered city concept — Spirewatch

2026-10-11: user requested the improvement plan plus lightning, foreground monitor movement, city activity/glows and a travelling main-tower glow. [V2 minute and three-repeat review](music/spirewatch-animation-v2/README.md) delivered: rebuilt flowing waterfall texture, crisp calm basin ripples, layered clouds/mist, three transit passages, six district glows, sixteen window holds, synchronized map activity and up/down tower pulses. Three local lightning events include exterior response. Source geometry and room exposure remain fixed. Tower mask sky spill was corrected using mapped light strips; a later cloud-source edge was fixed with surrounding-sky reconstruction and smooth mast transitions. Full isolated/analytic/targeted and 1,800/5,400-frame decode/timestamp/seam/repeat checks passed, including exact picture checks on each side of the three parallel-render chunk joins. Assistant inspected native/decoded stills, not continuous playback. User visual review is next; v1 remains an unapproved historical checkpoint. Same cleaned 1672x941 source; 4K, long music and assembly are separate. No catalog number, commit, push or remote media backup; other releases unchanged.

'''+s[b:];p.write_text(s,encoding='utf-8')
p=R/'AGENTS.md';s=p.read_text(encoding='utf-8');a=s.index('Current Spirewatch animation (2026-10-10):');b=s.index('\n\n',a)
s=s[:a]+'''Current Spirewatch animation (2026-10-11): user authorized the improvement plan plus lightning, monitor movement, city glows/activity and up/down main-tower glow. Silent sixty-second 720p/30 fps v2 and exact three-repeat 180-second review delivered in music/spirewatch-animation-v2/; see README.md, scene-plan-v2.json and delivery-v2.json. Same cleaned 1672x941 source SHA-256 22553e407a8aac902a7eb55ddf52d544752a642856b3265ef2368741a0eadcba. Rebuilt transported waterfall material/spray, detailed bounded basin ripples, clearer clouds and depth-specific mist, three route-bound transit passages, six city strip glows, sixteen window holds, readable transit-linked map activity and retained coupled lamp/walkway dips. Main-spire pulses use eleven mapped emitter regions; three local cloud lightning events peak near 9.6/34.6/52.6 seconds with faint exterior response. Initial broad cyan tower mask caught sky; individually mapped strip regions corrected it, first study preserved. A later transported cloud-source edge was corrected with normalized valid-sky reconstruction and soft mast-fringe transitions; prior full encode preserved in history/pre-sky-correction. All fourteen non-sky layers match at six times; four contiguous parallel chunks pass exact native/decoded picture checks on both sides of joins. Five isolated clips, analytic protection/periodicity, targeted material/tower/transit direction/detail/late coverage and full 1,800/5,400-frame colour-aware decoding/timestamps, regional/composite/quiet-neighbour seams and exact repeat checks passed. Assistant inspected masks/temporal/decoded stills, not continuous playback. V2 awaits user visual verdict; implementation authorization is not acceptance. V1 preserved as the user's needs-improvement checkpoint. No 4K, new music, long assembly, commit, push, paid service or remote media backup. Unnumbered concept; other releases unchanged.'''+s[b:];p.write_text(s,encoding='utf-8')
p=R/'creative/ANIMATION_KNOWLEDGE_BANK.md';s=p.read_text(encoding='utf-8')
heading='## Spirewatch waterfall candidate — 2026-10-10';a=s.index(heading);b=s.find('\n## ',a+len(heading));b=len(s) if b<0 else b
s=s[:a]+'''## Spirewatch animation candidate — 2026-10-11

**V1 needs substantial improvement; v2 delivered for user review.** [V2 package](../music/spirewatch-animation-v2/README.md), [v1 audit](../music/spirewatch-animation-v1/improvement-audit/v2-improvement-brief.txt). User authorized the rebuild plus lightning, foreground monitor movement, city glows/activity and travelling main-tower glow. No v2 artistic verdict yet.

- Moving brightness over photographed static waterfall streaks did not provide enough material change. V2 transports normalized source water texture within fixed channel masks, preserving slow channel shading, with restrained threads and local spray. Early material contrast was excessive and reduced before rendering. Native feature tracking after removing stationary channel shading measures nine pixels down in 0.2 seconds; direction evidence does not establish natural playback.
- Reconstructing basin reflections blurred fine source detail. V2 uses bounded source ripple transport with edge damping and quieter far-right water. A five-state high-frequency measure retains about 99% of source detail; this verifies spatial detail, not artistic water acceptance. Depth-specific mist and stronger coherent cloud phases address motion coverage while preserving source/destination geometry exclusion.
- Cyan thresholding inside a broad tower rectangle included blue clouds. An approximate building silhouette still caught edge pockets. Map actual emitter-strip regions first, then select complete cores and narrow local spill. Eleven mapped main-spire regions now carry up/down pulses. First-study code/config/stills preserved in the v2 history. Do not treat blue-pixel selection as an architecture mask.
- A dominant elevated route can support sparse, perspective-mapped transit with explicit occluders. V2 links three transit passages to readable original-map monitor markers, adds restrained node/panel updates, six city glow regions and sixteen window holds. This is a candidate cinematic interpretation, not an accepted vehicle preset. Avoid floating dots, synchronization across all buildings and the prominent waveform rejected on Shoreless.
- Local lightning should be partly cloud-obscured and illuminate a coherent region with weaker exterior response. Three staggered events preserve room exposure. V2 branches/intensity require user playback feedback; source/encoded stills cannot establish their temporal character.
- Final encoded inspection exposed a vertical cloud-source reconstruction strip beside the tower, separate from the corrected light mask. Wide-hole inpainting can produce smooth-looking static fills that become obvious transported rectangles. Normalize nearby valid-sky radiance across missing regions and use a broad smooth transition; taper cloud contrast near thin protected mast fringes. Preserve both sampled-source and output exclusions. All fourteen non-sky layers matched at six sampled times after correction. History retains the previous complete encode and reports. Four contiguous local render chunks retain absolute scene time; compare native/decoded YUV at both sides of all chunk joins as well as timestamps and loop seams.
- Five isolated tests, analytical seams/protection, direction/detail/coverage and all combined/repeat frames/timestamps/encoded seams passed. Assistant inspected stills, not continuous playback. Technical passes do not promote this version to an accepted preset. V1 and the exact rejected first-study masks remain history. "500%" expresses ambition, never a measured result.
'''+s[b:];p.write_text(s,encoding='utf-8')
print('V2 delivery, current project state and knowledge bank recorded; no commit/push.')
