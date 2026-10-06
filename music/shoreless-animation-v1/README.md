# The Shoreless Colony animation v1

2026-10-06. First draft for catalog 09, built under the request to animate the next scene using accumulated feedback. Uses the clean artwork-v1.png, not the thumbnail adaptation. This is a review candidate.

- [Twenty-second silent 720p preview](shoreless-colony-v1-preview-20s.mp4)
- [Sixty-second review with three exact repetitions](shoreless-colony-v1-three-loops-60s.mp4)
- [Sea test](water-isolated-v1-8s.mp4)
- [Cloud test](sky-isolated-v1-8s.mp4)
- [Turbine test](turbines-isolated-v1-8s.mp4)
- [Room and monitors test](room-isolated-v1-8s.mp4)
- [Delivery record](delivery-v1.json)
- [Configuration](scene-plan-v1.json)
- [Mask review](mask-review.png)

## Visible actions

The original choppy sea moves through a filtered 24-wave perspective reflection surface. Displacement .40, contrast .045 and specular strength 3 retain the source water character at a restrained starting strength. Caissons, access platforms, connecting corridors and antenna masts are excluded from the output and sampled water texture. The treatment is a source-based 2D approximation; waves do not physically break around supports.

Upper and low cloud layers travel independently at 2.2 and 1.4 source pixels per second. Local overlapping lifetimes hide resets while preserving forward movement. Moons, island outlines, window frame and antenna silhouettes are excluded from the moving source and output. This can soften cloud texture; judge naturalness at normal speed.

The two existing turbine blade images are extracted over locally reconstructed sky and rotate once per twenty seconds. Fixed hubs and masts are restored over the blades. Small independently timed red hub lights support them. This optical reconstruction is new for Shoreless and awaits review, rather than inheriting acceptance from another scene.

Three small groups of cabin panes have independent dark holds of 5.4, 6.2 and 4.7 seconds; the last wraps across the join. Other windows and exterior practical lights remain steady. Source-space, supersampled masks preserve the visible frames and dividers. The foreground shelf light has a brief paired flicker near 4.2/4.8 seconds and a gentler dip near 14.1 seconds, with associated warm wall and desk illumination.

The left monitor has a moving marker along the existing platform diagram. An existing narrow log panel on the right monitor scrolls forward and its small status area carries changing segmented meters. Main monitor pictures, bezels, furniture and camera remain fixed.

## Reused lessons and checks

The configuration records the knowledge-bank choices: Glacier/Floodplain water and sampling protection, Cable cloud transport and monitor activity, Ringfall/Floodplain complete light apertures and local spill, and Saltline/Icebound circular light schedules. All coordinates are mapped afresh to this 1672x941 plate. Before rendering, sample inspection prompted additional protection for thin antenna masts in both sky and water regions.

Four eight-second isolated tests precede the complete draft. Analytic layer endpoints/seams, finite frames and protected source pixels passed. Every preview/review frame decoded with sequential timestamps; regional/composite encoded seam gates passed, with no duplicate endpoint. The sixty-second review has three identical decoded repetitions; it is not a unique one-minute animation. Water frequency quantization deviations are recorded in analytic-validation.json.

Assistant inspected source/crops/masks, temporal full-scene samples and decoded stills, not continuous playback. User review is pending, especially sea strength, turbine extraction, cloud travel, light masks and monitor readability. No 4K master, soundtrack or combined long video for scene 09 yet. Preview: 1280x720, 30 fps, silent. Future 4K will upscale the native 1672x941 source.

Use render_shoreless.py --stage samples, then isolated, then preview with the existing local Python runtime and PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. setup_scene.py refuses an existing config; renderer outputs refuse existing MP4 destinations. The shared Floodplain water/encoder and timing primitives are imported unchanged and fingerprinted. Draft videos remain local ignored files. No paid generation, new model, Git commit or push.
