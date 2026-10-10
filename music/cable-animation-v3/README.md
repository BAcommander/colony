# The Last Cable Station - animation v3

2026-10-03. User described v2 as getting there and requested computer-screen activity. V3 adds only screen activity, preserving the v2 environment and lighting. The user accepted this v3 look with "ok perfect" on 2026-10-03. The matching 4K master and confirmed two-hour Colony assembly are delivered; see ../../final/06-last-cable-station/assembly-v1/README.md.

- [Twenty-second 720p preview](last-cable-station-v3-preview-20s.mp4)
- [Three-loop review, sixty seconds](last-cable-station-v3-three-loops-60s.mp4)
- [Isolated screen test, eight seconds](computers-isolated-v3-8s.mp4)
- [Delivery record](delivery-v3.json)
- [Configuration](scene-plan-v3.json)
- [Preserved v2](../cable-animation-v2/README.md)

The left monitor carries a small moving route marker and two timed node highlights along its existing map. The right monitor's original log texture scrolls upward inside a perspective-mapped viewport; existing status strokes brighten independently, with a small cursor and changing meter. Screen bezels and existing layouts stay fixed. All motion uses the common twenty-second period. The marker fades out before its return; log transport wraps forward through the join.

The v3 renderer extends the unchanged v2 renderer, which retains the v1 dependency. Source pixels outside the computer apertures match v2 exactly at 0, 4, 8, 12, 16 and 19.9667 seconds. The source plate remains the approved 1672x941 v3 artwork, bound by hash. Old versions are preserved.

The isolated test, full 600-frame preview and 1800-frame repeated review decode with correct counts and timestamps. Analytical screen endpoints/seams and encoded regional/composite seams pass. All three decoded repetitions match exactly; source-protection assertions run during rendering. See analytic-validation.json, isolated-validation.json and preview-validation.json for evidence and dependency hashes.

Full-scene temporal stills, enlarged screen crops and a decoded frame were inspected. Continuous assistant playback is not claimed. User acceptance is recorded separately in approved-v3-preview.json. Review at normal speed for screen activity and the join. The 720p preview is silent. The accepted look now has a verified 4K master and a two-hour combined export; full combined review remains pending. No credits, commit or push occurred.

Reproduce using render_cable_v3.py --stage samples, --stage isolated and --stage preview with the existing Python runtime and PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. Encoded outputs refuse overwrite. setup_scene.py records the initial config; effective masks and dependencies are fingerprinted in each validation report.
