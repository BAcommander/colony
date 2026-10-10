# Spirewatch — animation v2

2026-10-11 (work begun 2026-10-10): requested rebuild with lightning, monitor movement, city activity and a travelling tower glow. Silent sixty-second 1280x720/30 fps preview. User says “it's getting better”; saved as a positive progress checkpoint, with further refinement open.

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

No music, 4K master, long assembly, upload, paid service or new model in this delivery. User requested commit/push on 2026-10-11. Source art, code/configuration, masks, inspection/history records and the exact v2 minute preview are selected for Git backup; repeated reviews and intermediate videos remain local. See backup-manifest.json and the subsequent local remote-backup-verification.json for actual remote evidence. package-manifest.json preserves the earlier delivery inventory; backup-manifest.json records this checkpoint. The concept remains unnumbered; Vast Unfamiliar World is only its short musical direction.
