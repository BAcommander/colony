# The Last Cable Station - animation v1

2026-10-03. First full twenty-second preview delivered following the user's render request. Motion is awaiting user review; original approved artwork and other scene renderers are unchanged.

- [20-second 720p preview](last-cable-station-v1-preview-20s.mp4)
- [Three loops, 60 seconds](last-cable-station-v1-three-loops-60s.mp4)
- [Delivery checks and fingerprints](delivery-v1.json)
- [Source-bound configuration](scene-plan-v1.json)
- [Original planning brief](../../final/06-last-cable-station/animation-plan-v1/README.md)

Valley clouds, upper sky, the bright left cloud bank and lower ravine use separately masked source-texture transport with slower distant motion. Three habitat window apertures have independent dim/off holds, including a wrapped hold at the join. Selected existing right-console status strokes update subtly; the left map and desk lamp stay steady. The parked cabin, camera, tower, cables, planet and room remain fixed. Two copies of each moving texture renew with staggered zero-opacity resets; this is a 2D approximation, not a fluid simulation.

Full-composition mask overlay and temporal stills, decoded isolated frames and a decoded combined frame were inspected. No continuous assistant playback or user artistic acceptance is claimed. Check the movement at normal speed, especially cloud travel, cliff/cable edges and the three-loop joins. The existing audio/transition approval does not approve these visuals.

## Verification

Four isolated eight-second clips fully decoded at 720p/30 fps. The full preview has 600 frames and the repeat review 1,800, with sequential timestamps. Each source frame asserts unchanged pixels outside permitted masks and exact cable/planet protection. Every layer has matching periodic endpoints and passes the last-to-first step comparison; the encoded preview passes separate region/composite seam checks. All three decoded repetitions match exactly. See isolated-validation.json, analytic-validation.json and preview-validation.json. Numeric checks do not establish artistic quality.

## Reproduce and continue

Use the local Python runtime with PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. Run render_cable.py --stage samples, then --stage isolated, then --stage preview. Media destinations refuse overwrite; choose a new version for changed timing or masks. setup_scene.py preserves the initial config and refuses an existing destination. masks/*.png are inspection exports; the renderer rebuilds full-precision masks from config geometry. Dependency hashes are recorded for ambient_effects.py, render_floodplain.py and water_surface.py under the repository scripts folder.

The original source is 1672x941. This delivery is a 1280x720 silent review preview. After visual acceptance, export and validate the upscaled 4K master with the same source/config and motion timing. The final music-video duration remains unconfirmed; no long assembly or new audio work occurred here. All files are local; no commit or push performed.
