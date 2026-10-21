# Spirewatch v6 — readable city motion

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
