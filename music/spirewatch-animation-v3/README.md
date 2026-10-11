# Spirewatch — lighting revision v3

The user could not see the v2 lightning or tower movement and found the warm city lights static. This version responds with stronger local storm illumination and broader, independently timed city lighting. “250%” is creative ambition, not a measured quality claim. V2 remains preserved and remotely backed up at 4f008e9; this new candidate needs user playback review.

- [Full minute](spirewatch-v3-preview-60s.mp4)
- [Three-repeat review](spirewatch-v3-three-loops-180s.mp4)
- [Delivery record](delivery-v3.json), [configuration](scene-plan-v3.json), [revision checks](analytic-validation.json)

## What to look for

Lightning begins at 9.4, 34.4 and 52.4 seconds, with first peaks near 9.6, 34.6 and 52.6 seconds. Broader cloud illumination, a weaker second pulse and a fading glow last roughly 1.8 seconds per event. Thin partly obscured branches support the illumination. A horizontally related response affects mapped exterior structures and water; interior surfaces retain their exposure.

The main spire's travelling band rises at 2–13 seconds, descends at 26–40 and rises at 45–57. A dimmer emitter state around the wider bright band gives it readable contrast. Existing source-bound strip masks keep the change on the structure. Six other cyan light regions have independent 20/30-second travelling glows.

157 warm apertures are organized into 36 local groups. Each group has two independent off/dim holds per minute, complete aperture cores, coupled small spill and a slight warm recovery. Other lights remain steady. Group masks are extracted only within mapped facade boxes; they do not dim rectangular building regions. Existing three walkway lamps have deeper, slightly longer dips and the desk lamp has a stronger coupled dip near 32 seconds. The foreground map/transit relationship is retained.

## Retained environment and inspection

Same cleaned 1672×941 source SHA-256 22553e407a8aac902a7eb55ddf52d544752a642856b3265ef2368741a0eadcba. The cloud reconstruction, layered mist, waterfalls, calm basin water, transit and monitor are retained from v2. Nine isolated retained layers are compared byte-for-byte at five source times in check_revision.py.

The first lighting study had an overly graphic thick lightning zigzag. Its code/configuration/sample are preserved in history/first-lighting-study. The current branches are thinner, more irregular and partly cloud-obscured. Current cloud illumination also follows the transported cloud brightness instead of painting a flat glow over dark cloud detail.

The first complete render exposed dark antenna fringes during brighter lightning. A transport mask needs a safety margin, but static illumination should reach the sky beside the actual thin silhouette. V3 now uses a separate tighter upper-sky illumination mask; cloud transport itself remains unchanged. The first complete render and reports are preserved in history/pre-lightning-mask-refinement.

Assistant inspection uses full-composition native and decoded samples, temporal crops and masks, not continuous playback. Encoded full-minute/repeat, timing, local/composite seam and exact contiguous-render join checks are recorded in the delivery reports when completed. Technical checks do not establish artistic acceptance.

## Reproduction

Use the bundled Python with PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. Run check_revision.py, the isolated lighting studies, render_parallel.py, render_spirewatch.py --stage verify, check_chunk_joins.py and inspect_encoded.py. Four contiguous 15-second render chunks preserve absolute scene time; this is a genuine minute, not a repeated short segment. Existing video outputs are protected against overwrite. lighting_layers.py holds new effects; render_spirewatch.py retains the v2 environmental algorithms, with hashes bound in the delivery record.

Silent 1280×720 at 30 fps; no new audio, 4K delivery or long assembly. A future 4K version would upscale the native source. No credits or paid services used. User explicitly requested commit/push on 2026-10-11. Current v3 minute preview, source/config/masks, diagnostics/history records and learnings selected for Git backup. Repeated/older/isolated/intermediate videos remain local. See backup-manifest.json and subsequent local remote-backup-verification.json for actual remote evidence. Backup authorization does not imply artistic approval.
