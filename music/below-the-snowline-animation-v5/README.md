# Below the Snowline — V5 stronger charge, fiery flight and continuous sky

User feedback: V4 cannon charging was too subtle, the sky still ripped inside the clouds, and the shuttle needed brighter fiery engines and an exit through the frame rather than a fade. V5 is a new two-minute review candidate, preserving V4 and the original landscape.

## Changes

- **Sky rebuilt:** one continuous bounded cloud deformation replaces the two shifted images, near-binary source-validity gate and changing normalization that created internal bands. The fixed conservative cloud mask still protects terrain/frost/equipment. There are no phase resets or per-pixel switches between source images. Original cloud detail gently deforms; no landscape pixels move with it.
- **Cannon:** much brighter blue-white cores, nearly full-strength barrel strips, brighter amber power nodes and broad additive bloom/reflected light. Charge cycles remain0:31–0:56 and1:28–1:53. No discharge or additional sound effect.
- **Shuttle:** original detailed RGBA asset retained, slightly larger passes, orange-white exhaust from both engines, and hot nozzle/bloom detail. Full-opacity flight crosses native x=-120 to1780 (and reverses on the second pass), beyond the1672px scene. Entry/exit is physical window/ice occlusion and viewport cropping, never a time-based opacity fade. The first crossing occupies-0:05–1:10; the second1:10–1:58. Those include the periods outside the visible window.
- Original textured console lights, radar beacons, bridge activity, wind/snow and the V6 soundtrack excerpt are retained.

## Review and reproduction

`Below-the-Snowline-v5-with-V6-audio-2min.mp4`:120seconds,1280×720,30fps, QP0 H.264/BT.709 and stereo48kHz AAC. The audio excerpt is byte-identical to V4:3:00–5:00 of V6 with its existing+0.4dB listening gain and short review-only fades.

Run `audit_sky.py` for independent map/Jacobian/source-footprint checks and diagnostic cloud crops, `render_v5.py samples` for full-scene stills, `render_v5.py render` for six contiguous sections, then `finish_review.py` for assembly/full decode/joins/source-picture/audio checks. Existing video files are protected against overwrite. `cache/` contains regenerable/intermediate review data.

A good native-to-decoded comparison does not prove the original renderer is artifact-free: V4 passed those checks while reproducing its faulty cloud gate. V5 adds independent cloud mapping checks and visual inspection of the upper cloud bank.

The shuttle master and exact prompt are preserved under `assets/` from the prior built-in imagegen call; no new image generation was needed for V5. The master alpha is unchanged; fiery engines are procedural animation layers.

Assistant checks are technical plus source/temporal/decoded-still inspection, not continuous playback or listening approval. V5 is pending user review, not a final seamless loop or full4K/two-hour export. Work remains on main; no upload or commit/push requested in this turn.
