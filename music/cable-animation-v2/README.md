# The Last Cable Station - animation v2

2026-10-03. User found v1 movement okay but requested substantially more distant cloud activity, room-light flickering and sky-light variation, then explicitly requested the render. V2 is a new review candidate, not yet accepted.

- [Twenty-second 720p preview](last-cable-station-v2-preview-20s.mp4)
- [Three-loop review, sixty seconds](last-cable-station-v2-three-loops-60s.mp4)
- [Delivery record](delivery-v2.json)
- [Configuration](scene-plan-v2.json)
- [Preserved v1](../cable-animation-v1/README.md)

## Visible changes

The upper clouds travel at 1.9 source pixels/second and the distant valley banks at 3.7 (v1: 1.15/2.3). Three independently seeded haze formations cross the central distant valley at different heights, with overlapping local lifetimes and protected tower/cable geometry. This spreads activity through the distance instead of only changing a narrow cloud bank. The closer ravine and left cloud bank retain their v1 transport rates.

The desk lamp has a brief dip at 4.2-4.84 seconds, a shorter follow-up at 5.03-5.29 and a gentler hold at 14.6-16.0. The complete aperture and its bright core dim together; small matching spill changes occur nearby. A soft 5.8-17.5-second daylight event reduces warm light over the left sky and sunlit desk with 3.6-second eased transitions. This is local illumination shading; the full image does not change exposure. The planet, camera, parked cabin and architecture remain geometrically fixed.

The foreground cloud layers, habitat light schedules and console behaviour remain pixel-identical to v1 in isolated sampled source frames. render_cable_v2.py extends the unchanged v1 class; PeriodicDust/DustTransport supply the existing deterministic transport method. New parameters are in a separate source-hash-bound configuration. No v1 art, code, configuration, masks or media were overwritten.

## Checks and review scope

Four isolated eight-second tests cover the changed valley motion, added haze, daylight and lamp. Full v2 preview and three-repeat review fully decode at 720p/30 fps with exact counts and timestamps. Source protection assertions run on every generated frame; analytical layer endpoints/seams and encoded region/composite seams passed. All three decoded repetitions match exactly. Hashes and checks are in analytic-validation.json, isolated-validation.json and preview-validation.json.

Mask overlays, full-composition temporal stills and decoded stills were inspected; continuous playback and user artistic acceptance are not claimed. Watch at normal speed for cloud visibility, haze density, lamp timing, local lighting and the repeated join. V1 movement feedback does not approve the new effects.

## Reproduce

Use the existing local Python runtime with PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. render_cable_v2.py supports --stage samples, --stage isolated and --stage preview. Encoded destinations refuse overwrite. Dependencies and effective mask hashes are recorded; setup_scene.py preserves the initial v2 configuration. Diagnostic mask PNGs show only newly added effect masks; original cloud masks remain source-config-derived.

Review render only: 20 seconds, 1280x720, silent. Native source remains 1672x941; 4K export awaits visual review. Audio/transition acceptance remains separate, and final long-video duration remains unconfirmed. No credits, commit, push or long assembly occurred.
