# Gate Camp V2 water and light test

[Watch the V2 preview](Gate-Camp-water-and-light-v2-8s.mp4) and [compare the V1 preview](../gate-camp-animation-v1/Gate-Camp-portal-v1-8s.mp4). Both are eight seconds at 720p/30 fps. V2 reuses V1's mapped wave motion and reduces some fine sparkle. Wider pearl-blue highlights roll across the surface. A soft blue spill follows the same light fields on three traced areas of stone beneath the portal. [Production references](../../final/17-gate-camp/portal-research.md)

All 240 frames decoded in sequence. The portal samples stayed within the aperture, and protected pixels matched the clean art before resizing and encoding. The largest blue lift on the landing was 14 out of 255 RGB codes in the source composite. Sampled decoded comparisons were inspected. Motion and spill strength are pending playback review, followed by the periodic build. [Checks and hashes](delivery.json)

Reproduce with `python music/gate-camp-animation-v2/render_water_light.py` in the existing audio-analysis environment with the output path free. The [editable look settings](look-settings.json) sit on top of the [V1 source geometry](../gate-camp-animation-v1/scene-plan.json).
