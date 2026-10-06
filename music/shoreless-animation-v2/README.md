# The Shoreless Colony animation v2

2026-10-06. Requested revision to the first catalog 09 draft. User visual review is pending.

- [Twenty-second silent 720p preview](shoreless-colony-v2-preview-20s.mp4)
- [Sixty-second review: three identical repetitions](shoreless-colony-v2-three-loops-60s.mp4)
- [Delivery evidence](delivery-v2.json)
- [Configuration](scene-plan-v2.json)
- [Renderer](render_shoreless_v2.py)
- [Mask review](mask-review.png)

## Changes from v1

Complete source-space aperture masks replace the three selected cabin-pane masks. Close-up forced dim checks revealed a few-pixel error on the middle and far cabins; the final masks remove the remaining bright strips while retaining dark frames and neighboring windows. The initial v2 mask review is retained under initial-mask-review/ as diagnostic history. Whole-aperture coverage includes bright cores and warm internal reflections; color gating alone is insufficient.

Sea foam follows bright photographed moving crests with advecting broken coverage and stronger wash near the three caisson bases. The underlying v1 sea displacement and speed are unchanged. It is a restrained photographic approximation, not physical wave breaking or foam simulation.

Three actual rooftop antenna tips now pulse independently and alternate red/green. A five-second pulse interval gives a ten-second complete color cycle within the twenty-second loop. The two original red turbine-hub beacons remain independent.

The left monitor has brighter route highlights, a moving marker and staggered node pulses. The right monitor has a cyan telemetry trace and meters inside its existing lower panel. Existing main imagery, screen perspective, bezels and room geometry remain fixed.

Additional brief window, exterior-practical and foreground shelf-light flickers are staggered. The shelf light dims its nearby warm wall and desk spill together. Other lighting stays steady.

A slow cloud opening introduces soft localized sun shafts and a warm reflection across the moving sea. The effect avoids buildings, islands and the room. It is a composited lighting approximation; it does not change global exposure.

## Preservation and verification

The immutable clean artwork-v1.png remains native 1672x941, SHA-256 f042d109358089f0e89b11c99a84505fba9a825dca3428ed7109055d29253f69. The v2 adapter imports the unchanged hash-bound v1 renderer. Water, sky, turbine rotation and original beacons match v1 exactly in isolated source frames at 0 and 7 seconds. V1 files and prior scenes remain preserved.

Five eight-second isolated tests cover lights, foam, antennas, room and sunlight. Analytic layer endpoints/seams and protected pixels passed. Full 600/1800-frame decodes and sequential timestamps passed, as did regional/composite encoded seams and three identical decoded repetitions. No duplicate endpoint is added. See analytic-validation.json, isolated-validation.json and preview-validation.json.

Assistant inspected mask crops, full-scene temporal samples and decoded stills, not continuous playback. Technical verification does not establish artistic approval. Review window edges, foam strength, antenna visibility, monitor readability and sunlight timing at normal speed. No soundtrack, 4K master or long assembly produced. Future 4K would upscale the 1672x941 artwork.

Reproduce with render_shoreless_v2.py --stage samples, then isolated, then preview, using the existing Python runtime and PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. prepare_v2.py refuses an existing config and the renderer refuses existing MP4 outputs. Draft media remain local and ignored; no credits, commit or push.
