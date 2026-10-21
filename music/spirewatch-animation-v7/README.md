# Spirewatch v7 — tower fix and passing weather

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
