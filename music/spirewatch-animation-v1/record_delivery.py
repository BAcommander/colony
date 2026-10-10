from pathlib import Path
import json
H=Path(__file__).parent;R=H.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
d=read(H/'delivery-v1.json');a=read(H/'analytic-validation.json');i=read(H/'isolated-validation.json');target=read(H/'targeted-validation.json')
assert d['fingerprint']==a['fingerprint']==i['fingerprint']==target['fingerprint']
assert d['preview_validation']['frames']==1800 and d['repeat_validation']['three_exact_decoded_repetitions']
assert all(v['pass'] for v in d['preview_validation']['encoded_seams'].values())
assert (H/'visual-review.json').exists()
text='''# Spirewatch — animation draft v1

Delivered 2026-10-10 in response to the user's “do it” instruction invoking the saved animation production prompt. New unnumbered concept; Farpoint and numbered releases remain unchanged.

- [Complete minute preview](spirewatch-v1-preview-60s.mp4): silent, 1280x720, 30 fps, 1800 frames.
- [Three-repeat join review](spirewatch-v1-three-loops-180s.mp4): silent, 180 seconds; repeats the exact minute three times.
- [Delivery and hashes](delivery-v1.json), [scene plan](scene-plan-v1.json), [visual inspection](visual-review.json).

## Implemented

Broad source-cloud travel to the right and independent lower mist; downward density/streak travel within three photographed waterfall channels; seven carefully bounded water patches with low-strength filtered 24-wave reflections and additional right-side calming. Ten independently held windows, three brief existing walkway-lamp dips, a small monitor route marker and node/panel updates, and one desk-lamp dip at 31.8–32.65 seconds with its warm local illumination.

Cloud renewal and local habitation states span the full sixty seconds. Waterfall fields have independent 6/5/4-second local cycles, the route marker 30 seconds and panel scan 20 seconds. It is not three copies of a twenty-second scene. Local cycles are retained at their own speeds. Cyan architectural routes stay steady. Optional beacons were omitted because the source does not establish clear emitting tip apertures; transit accents were deferred to preserve the motion hierarchy. No new rain, lightning, sunbeams, objects, audio or camera motion.

Source: ../digital-city-concepts-v1/01-spirewatch-v2-cleanup.png, native 1672x941, SHA-256 22553e407a8aac902a7eb55ddf52d544752a642856b3265ef2368741a0eadcba. The corrected cup, furniture, city structures and source plate remain fixed. Only explicitly masked local lighting/optical effects change pixels. This is optical animation of a still, not a physical waterfall or atmospheric simulation.

## Checks and limits

Three eight-second full-composition isolated tests (atmosphere, falls, water) passed full decoding and timestamps. Forced-dim window sheet and lamp/screen/fall temporal crops inspected. Initial weather masks sampled some distant structure details; exclusions were expanded and a conservative lower skyline boundary added. The initial study is retained under history/initial-mask-study/.

The tracked waterfall density moves eight native pixels down in 0.2 seconds (40 px/s); four weather regions have nonzero four-second motion at 0, 20, 40 and 52 seconds. Those numbers support direction/coverage, not artistic approval. Native analytic seams, protected source pixels, every encoded minute/review frame and timestamp, regional/composite seam gates, quiet-neighbor seam checks, no duplicate endpoint, distinct 0/20/40 states and three exact decoded minute repetitions passed.

Assistant inspected native and colour-aware decoded stills, masks and temporal crops; continuous playback was not performed. User motion review remains pending. In particular, waterfall texture, cloud renewal, water calmness and small-screen visibility need a real-time user verdict. No 4K, music mix, long assembly, upload, commit or push produced in this request. Future 4K would be upscaled from the 1672x941 source.

## Reproduction

Use render_spirewatch.py with --stage samples, --stage isolated, then --stage preview. Existing videos are protected from overwrite; use a new version directory for changed deliveries. Keep scene-plan-v1.json, renderer, masks and the hash-verified dependencies/ snapshot together. The current environment uses the bundled Python with PYTHONPATH=G:/AI/youtube/.runtime/scene-tools for OpenCV. inspect_motion.py creates the targeted diagnostics. build_plan.py records the initial source-coordinate configuration; do not run it over a later revised configuration without deliberate review.
'''
(H/'README.md').write_text(text,encoding='utf-8')
p=R/'music/digital-city-concepts-v1/current-direction.json';state=read(p);state.update(status='Spirewatch v1 minute animation and three-repeat review delivered; user motion review pending',animation_rendered=True,animation_record='music/spirewatch-animation-v1/delivery-v1.json',animation_preview='music/spirewatch-animation-v1/spirewatch-v1-preview-60s.mp4',user_motion_approved=False);save(p,state)
p=R/'PRODUCTION_PIPELINE.md';s=p.read_text(encoding='utf-8');heading='## Unnumbered city concept — Spirewatch'
paragraph='''## Unnumbered city concept — Spirewatch

2026-10-10: user preferred Spirewatch among three digital-city concepts, requested the cup cleanup and invoked its saved animation prompt with “do it”. [V1 minute preview and three-repeat review](music/spirewatch-animation-v1/README.md) are delivered: readable cloud transport, downward waterfall texture, calm basin reflections, independent windows/walkway lights, restrained monitor map activity and coupled desk-lamp dip. Technical gates passed; assistant inspected sampled stills, not continuous playback. User motion review pending. Source is the cleaned 1672x941 artwork; 4K, long music and assembly are separate. Vast Unfamiliar World is the associated short musical direction. No catalog number assigned; Farpoint and releases 11–14 are unchanged.

'''
if heading in s:
 start=s.index(heading);end=s.find('\n## ',start+len(heading));s=s[:start]+paragraph+(s[end+1:] if end!=-1 else '')
else:
 pos=s.index('## Next concept exploration');s=s[:pos]+paragraph+s[pos:]
p.write_text(s,encoding='utf-8')
p=R/'AGENTS.md';s=p.read_text(encoding='utf-8');para='Current Spirewatch animation (2026-10-10): New unnumbered digital-city concept; user invoked music/digital-city-concepts-v1/spirewatch-animation-prompt-v1.txt with “do it”. Silent sixty-second 720p/30 fps v1 and exact three-repeat 180-second review delivered in music/spirewatch-animation-v1/. Cleaned source 1672x941 SHA-256 22553e407a8aac902a7eb55ddf52d544752a642856b3265ef2368741a0eadcba. Broad cloud transport/lower mist, downward texture in three existing falls, seven calm water patches, ten independent windows, three walkway dips, restrained monitor route/nodes/panel and one coupled desk-lamp dip. Waterfall fields repeat locally at 6/5/4 seconds; cloud renewal and lighting span sixty seconds. Optional beacons/transit accents omitted. Initial source-sampling roof artifacts fixed by wider exclusion and conservative skyline; study preserved. Three isolated tests, analytic/source protection, tracked downward flow, minute-wide weather coverage, full 1800/5400-frame colour-aware decoding and timestamps, regional/composite/quiet-neighbor seams and exact repetitions passed. Assistant inspected masks/temporal/decoded stills, not continuous playback. User motion review, 4K and extended music/assembly pending. Vast Unfamiliar World remains a short musical direction; no audio mixed. No paid tools, commit, push or upload. See README.md, scene-plan-v1.json and delivery-v1.json. Numbered releases unchanged.'
marker='Current Spirewatch animation ('
if marker in s:
 start=s.index(marker);end=s.index('\n\n',start);s=s[:start]+para+s[end:]
else:
 pos=s.index('\n\n');s=s[:pos+2]+para+'\n\n'+s[pos+2:]
p.write_text(s,encoding='utf-8')
p=R/'creative/ANIMATION_KNOWLEDGE_BANK.md';s=p.read_text(encoding='utf-8');heading='## Spirewatch waterfall candidate'
if heading not in s:
 s+='\n## Spirewatch waterfall candidate — 2026-10-10\n\n[Unnumbered v1 draft](../music/spirewatch-animation-v1/README.md), user review pending. The photographed falls use downward-advected periodic density within fixed channel masks, retaining the background architecture. Three independent 6/5/4-second fields preserve their speeds inside a minute-wide scene. Source-normalized tracking measured eight pixels of downward travel in 0.2 seconds; this distinguishes positional flow from pure brightness pulsing but does not establish natural-looking playback. Calm basin ripples are a separate cropped layer.\n\nThe first weather extraction included small distant roof/light details, despite masking the major towers. Expand source exclusions beyond traced edges and keep the lower transport boundary above unresolved rooflines. The fixed source detail remains visible beneath narrowly feathered edges. Inspect tower sides and distant city silhouettes as well as the main spire; numerically valid seams alone do not catch sampled architecture. Earlier study preserved; current full-frame isolated and minute-loop checks passed. Candidate methods are not accepted visual presets.\n'
p.write_text(s,encoding='utf-8')
print('Spirewatch records and live tracker updated')
