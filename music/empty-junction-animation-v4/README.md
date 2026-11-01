# The Empty Junction — revised-composition animation v4

**Subsequently rejected visually (2026-11-01):** the user found window masking, clouds and mist poor and requested a drastic improvement. The technical checks below remain historical evidence, not artistic approval. See the [V5 rebuild](../empty-junction-animation-v5/README.md) and [exact feedback](../empty-junction-animation-v5/user-feedback.json).

Current review candidate: the new complete-cabin artwork animated at native 1672×941 and downsampled to 1280×720/30 fps. User's "lets go" authorizes continuing animation after choosing the V3 audio balance. No detailed visual acceptance of this returned motion is inferred.

## Watch

- [Four-minute review with approved music and SFX](Empty-Junction-v4-with-approved-audio-4min-720p.mp4).
- [One scheduled silent cycle, three minutes](Empty-Junction-v4-scheduled-cycle-180s-720p.mp4).
- [Three exact scheduled cycles, nine minutes](Empty-Junction-v4-three-cycles-540s-720p.mp4).
- [Wind minute](Empty-Junction-v4-wind-minute-720p.mp4) and [quiet minute](Empty-Junction-v4-quiet-minute-720p.mp4).
- Principal full-composition tests: [ground powder](yard_powder-v4-isolated-8s.mp4), [cabin plume](cabin_exhaust-v4-isolated-8s.mp4).

The four-minute video is an excerpt for motion/balance review, without the once-only production intro. At 0:00–1:00 and 3:00–4:00, near-ground powder fades in/out with the wind passages. During the two intervening minutes, near powder is absent while the rest of the location continues moving. The train is heard at 2:05–2:30. Grit occurs at 3:18–3:30 and 3:46–3:58. Its V3 level is the user's chosen −3.3 dB source gain; no mix gain/EQ/fades are changed for the video, apart from normal AAC encoding for playback.

## Visible motion

- Two broken mineral-powder streams follow separate ground routes: across the cabin approach toward the turnout, and along the right yard margin toward the foreground. Small variations in shape and density travel forward along the routes. Ground-equipment occlusion is mapped to this new image.
- Condensation emerges at the existing louvred grille near source x315/y546, flows left/up along the cabin, expands and breaks apart. The antenna/pipe occluders preserve foreground fittings. This is an artistic interpretation of cabin ventilation, not a physical fluid simulation.
- Source-derived clouds move slowly through the open sky, with a restrained evolving sky layer and separately moving far/middle mist. A terrain-guided thread follows the central pass behind the freight buildings. Static mineral fins and building outlines remain protected.
- Nine selected hall/gallery/upper-room groups, the cabin's narrow door window and five practical/signal groups have independent holds or brief dim/recovery events. Other windows and lamps remain steady. Practical cores and nearby photographed spill vary together.

The camera, rails, buildings, freight wagons and landscape geometry remain fixed. The train sound is off-screen beyond the pass; no train animation or new vehicle is added. There are no added people, screens or other props.

## Source and remapping

[Frozen clean artwork](artwork-v3.png), SHA-256 `44bd1465510494ed91bc54c9461cb77da590179cb708c6dd21fcd6a6b51f8ba8`, is byte-identical to the revised scene-only composition. [Fresh plan](scene-plan-v4.json) contains new skyline, weather routes, aperture polygons, lamp spill and occluders. No old-coordinate transform or old masks are reused. Effect mathematics are reused from Junction v1–v3; this is a fresh scene adapter for a different composition. Old art, thumbnail candidates, prior animations and approved audio are preserved.

The first sky prototype created visible pale boundaries around rock silhouettes. Its diagnostic samples/config/masks remain under history/initial-sky-boundary/. The current adapter applies transported cloud differences around the actual photographed sky with a wider inward feather, preserving the reference sky at phase zero and removing that replacement-edge artifact. Corrected full-composition temporal samples were inspected before rendering the full minute.

The minute's weather and lighting states repeat after 60 seconds; it is not three copied twenty-second videos. Wind-enabled and quiet units are rendered from the same source/configuration in one native pass. They differ only inside the powder mask. The 180-second delivery cycle is wind / quiet / quiet, matching the requested audio's one-minute-on/two-minute-off timing. The silent nine-minute review contains exactly three copies of that scheduled cycle. No full-frame crossfade, reverse motion, duplicate endpoint or camera movement is used.

## Verification and review scope

[Analytical checks](analytic-validation.json) cover periodic layer states, seam changes, distinct 0/20/40-second states, finite pixels and exact unchanged source pixels outside active native masks. [Principal clip checks](isolated-validation.json) cover both eight-second clips and direct native RGB-to-decoded YUV controls. [Delivery record](delivery-v4.json) records full frame decoding, timestamps, regional and quiet-neighbour seam tests, exact scheduled/repeated decoded pictures and complete AAC-to-approved-source audio comparison.

[Renderer fingerprint](render-record.json) and [dependency snapshots](dependency-snapshot.json) preserve the exact source/config/code/masks/runtime identity. Preview is 720p from the native still, not a 4K delivery. No final hour-long video has been assembled.

Assistant visual review uses unamplified source-scale/720p temporal and decoded stills, not continuous playback. Pixel and seam passes are technical evidence; user playback determines whether the place feels alive enough. Motion and full combined playback verdict remain pending. The audio mix itself was accepted separately.

## Reproduce

Use existing local Python with NumPy/OpenCV/Pillow and FFmpeg. From the project music directory, run build_plan.py, render_junction_v4.py --stage samples, --stage isolated, validate_delivery.py --stage isolated, render_junction_v4.py --stage preview, then validate_delivery.py --stage delivery, under this directory. Existing media refuse overwrite. Reproduce in a fresh isolated copy, restoring the fingerprinted dependencies there if current shared files differ; do not overwrite newer shared code in the active project.

No model installation, external video service, paid generation, 4K render, upload, commit, push or remote backup is performed. Review media remain ignored local files. The next production step follows the user's visual verdict; the existing branded opening belongs once in a later final assembly.
