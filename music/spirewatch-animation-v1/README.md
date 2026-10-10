# Spirewatch — animation draft v1

Delivered 2026-10-10 in response to the user's “do it” instruction invoking the saved animation production prompt. New unnumbered concept; Farpoint and numbered releases remain unchanged.

- [Complete minute preview](spirewatch-v1-preview-60s.mp4): silent, 1280x720, 30 fps, 1800 frames.
- [Three-repeat join review](spirewatch-v1-three-loops-180s.mp4): silent, 180 seconds; repeats the exact minute three times.
- [Delivery and hashes](delivery-v1.json), [scene plan](scene-plan-v1.json), [visual inspection](visual-review.json).

## Current user verdict — 2026-10-10

User says the scene needs substantial improvement. V1 is an unapproved checkpoint. The [audit and proposed v2 rebuild](improvement-audit/v2-improvement-brief.txt) prioritizes flowing waterfall material, crisp basin detail, atmospheric depth, restrained city transit and readable room activity. Findings are based on code and twelve decoded-frame samples, not continuous playback. Proposed changes are not implemented.

## Implemented

Broad source-cloud travel to the right and independent lower mist; downward density/streak travel within three photographed waterfall channels; seven carefully bounded water patches with low-strength filtered 24-wave reflections and additional right-side calming. Ten independently held windows, three brief existing walkway-lamp dips, a small monitor route marker and node/panel updates, and one desk-lamp dip at 31.8–32.65 seconds with its warm local illumination.

Cloud renewal and local habitation states span the full sixty seconds. Waterfall fields have independent 6/5/4-second local cycles, the route marker 30 seconds and panel scan 20 seconds. It is not three copies of a twenty-second scene. Local cycles are retained at their own speeds. Cyan architectural routes stay steady. Optional beacons were omitted because the source does not establish clear emitting tip apertures; transit accents were deferred to preserve the motion hierarchy. No new rain, lightning, sunbeams, objects, audio or camera motion.

Source: ../digital-city-concepts-v1/01-spirewatch-v2-cleanup.png, native 1672x941, SHA-256 22553e407a8aac902a7eb55ddf52d544752a642856b3265ef2368741a0eadcba. The corrected cup, furniture, city structures and source plate remain fixed. Only explicitly masked local lighting/optical effects change pixels. This is optical animation of a still, not a physical waterfall or atmospheric simulation.

## Checks and limits

Three eight-second full-composition isolated tests (atmosphere, falls, water) passed full decoding and timestamps. Forced-dim window sheet and lamp/screen/fall temporal crops inspected. Initial weather masks sampled some distant structure details; exclusions were expanded and a conservative lower skyline boundary added. The initial study is retained under history/initial-mask-study/.

The tracked waterfall density moves eight native pixels down in 0.2 seconds (40 px/s); four weather regions have nonzero four-second motion at 0, 20, 40 and 52 seconds. Those numbers support direction/coverage, not artistic approval. Native analytic seams, protected source pixels, every encoded minute/review frame and timestamp, regional/composite seam gates, quiet-neighbor seam checks, no duplicate endpoint, distinct 0/20/40 states and three exact decoded minute repetitions passed.

Assistant inspected native and colour-aware decoded stills, masks and temporal crops; continuous playback was not performed. User has reviewed the scene and says substantial improvement is needed; no positive motion verdict is recorded. In particular, waterfall texture, cloud renewal, water calmness and small-screen visibility need a real-time user verdict. No 4K, music mix, long assembly, upload, commit or push produced in this request. Future 4K would be upscaled from the 1672x941 source.

## Reproduction

Use render_spirewatch.py with --stage samples, --stage isolated, then --stage preview. Existing videos are protected from overwrite; use a new version directory for changed deliveries. Keep scene-plan-v1.json, renderer, masks and the hash-verified dependencies/ snapshot together. The current environment uses the bundled Python with PYTHONPATH=G:/AI/youtube/.runtime/scene-tools for OpenCV. inspect_motion.py creates the targeted diagnostics. build_plan.py records the initial source-coordinate configuration; do not run it over a later revised configuration without deliberate review.
