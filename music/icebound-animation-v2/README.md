# Icebound Weather Post - snowfall and beacons v2

2026-10-03. User requested visible snowfall and blinking radar-style lights at the antenna top. This supersedes the v1 choice to omit snow particles. The original still and v1 draft remain preserved. V2 is a twenty-second 720p/30 fps silent preview. User accepted the look with "i think it's good" and asked about possible refinements; see approved-v2-preview.json. Longer timing changes remain proposals only.

- [Twenty-second preview](icebound-weather-post-v2-preview-20s.mp4)
- [Three-loop review, sixty seconds](icebound-weather-post-v2-three-loops-60s.mp4)
- [Eight-second isolated additions](snow-and-beacons-isolated-v2-8s.mp4)
- [Delivery record](delivery-v2.json)
- [Configuration](scene-plan-v2.json)
- [Preserved v1](../icebound-animation-v1/README.md)

Fine snow falls diagonally down and right, with three size/speed groups and a sparse nearer group for depth. Seeded paths use ten/twenty-second lifetimes, subpixel Gaussian footprints and slight directional blur. Flakes fade to zero before path renewal; no reversed motion or full-frame dissolve. The snowfall can pass in front of the scenery as an optical overlay. It does not warp the underlying landscape or station and is not a physical accumulation simulation.

Two small red beacons are anchored at source coordinates (274,55) and (240,107), on the existing upper mast and side antenna tips. Separate four/five-second schedules create staggered double flashes. Each includes a compact bright core and restrained red halo. No beam or new antenna geometry is added.

The unchanged v1 renderer supplies the original clouds, basin spindrift, window schedules and lamp/spill activity. Its delivered dependency fingerprint is checked on initialization. Every original isolated layer matches v1 exactly at 0,8,16 seconds. The new renderer is a composition wrapper, so the base source-protection checks still run before the requested snow/beacon overlays.

## Verification and review

An eight-second isolated additions test, complete 600-frame preview and 1800-frame repeated review fully decode with sequential timestamps. Analytic snow/beacon endpoints and seam checks pass; snow opacity fields repeat exactly and lifetimes divide the loop. The complete encoded regional/composite seams pass the existing gate. All three decoded repetitions match exactly. See analytic-validation.json, isolated-validation.json and preview-validation.json for hashes and evidence.

Full-scene temporal stills, antenna close-ups and decoded stills were inspected. Continuous assistant playback is not claimed. User acceptance of the v2 look is recorded separately. Review snow density/speed, beacon timing and the repeated join at normal size. 4K delivery, soundtrack and long assembly remain pending; native artwork is 1672x941.

Reproduce using render_icebound_v2.py --stage samples, --stage isolated and --stage preview with the existing Python runtime and PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. Existing encoded destinations refuse overwrite. No paid generation, model installation, commit or push occurred.
