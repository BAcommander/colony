# Icebound Weather Post - first animation draft

2026-10-03. User requested a draft incorporating recent animation feedback from the start. This is a twenty-second 720p/30 fps silent candidate, not yet user-approved. The approved v3 still is preserved and hash-bound.

- [Twenty-second preview](icebound-weather-post-v1-preview-20s.mp4)
- [Three-loop review, sixty seconds](icebound-weather-post-v1-three-loops-60s.mp4)
- [Delivery record](delivery-v1.json)
- [Source-coordinate configuration](scene-plan-v1.json)
- [Mask review](mask-review.png)

## Changes informed by recent feedback

Cloud texture moves coherently to the right across the broad sky above the stepped ice cliffs, at 2.6 source pixels/second. The mast and ringed moon are excluded from both the sampled moving texture and its output. There is no global exposure pulse or movement of cliff/ice geometry.

Two independent wind layers cross the frozen basin: farther haze at 4.8 source pixels/second and nearer spindrift at 8.5. Each has two staggered formations and local twenty-second lifetimes, expanding the active landscape beyond one small patch. These are textured optical overlays, not a fluid/snow simulation; terrain shapes remain fixed. There are no foreground snow particles.

Initial isolated test A used a snow colour too close to the ice in inspected full-scene stills. Test B uses paler snow at unchanged opacity, speed and coverage. Initial clips, configuration, renderer and validation are preserved as test-A history; the current draft uses scene-plan-v1.json and the matching B isolated tests.

The main right-hand room window dims independently for 6.6 seconds; two distant windows have separate 7.3/6.7-second holds, including a wrapped hold across the loop. The left room and other lights stay steady. The entrance lamp has a short double dip and a separate gentle longer dip, coupled to restrained doorway/snow spill. A little main-room spill follows its window state. Complete lit apertures include their white cores. No prominent computer screens are visible in this source, so no invented display is added.

The camera, weather mast, station, connections, ice cliffs, frozen sea and ringed moon stay geometrically fixed. New masks and anchors are mapped specifically to this image. render_icebound.py imports unchanged Cable cloud/light primitives and Saltline periodic transport; it does not copy their scene coordinates or modify their accepted renderers.

## Checks and review scope

Three eight-second full-composition isolated clips test the sky and each wind depth. Individual analytic endpoints/seams, protected-source assertions and finite frame values pass. The complete preview and repeated review fully decode with exact frame counts, sequential timestamps and regional/composite encoded seams within the existing gate. All three decoded repetitions are identical. See analytic-validation.json, isolated-validation.json and preview-validation.json for hashes and evidence.

Source/mask details, temporal stills and decoded frames were inspected. Continuous assistant playback and artistic acceptance are not claimed. Review normal-speed visibility, haze density, light scheduling and the repeated join. This draft does not establish 4K delivery, soundtrack generation or long-video duration. Native source is 1672x941.

## Reproduce

Use render_icebound.py --stage samples, --stage isolated and --stage preview with the existing local Python runtime and PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. Encoded destinations refuse overwrite. setup_scene.py records the initial configuration; source, effective masks and dependency hashes are stored in validation reports. No paid generation, model install, Git commit/push or long assembly occurred.
