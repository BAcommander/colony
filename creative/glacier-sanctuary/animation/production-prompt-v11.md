# Glacier Sanctuary v11 - sixty-second 4K delivery

The user accepted v10 and requested a 60-second loop in 4K. Preserve its calm water, distant snow, fog, smoke, exterior flickers and upper lantern. Foreground snow remains absent. The source is 1672x941, so 3840x2160 is an upscale, without newly generated 4K detail.

## Loop construction

Water: retain 24 seeded directions, wavelengths, reflection settings, sampling filter and boundary damping. Quantize each angular frequency to the nearest positive integer cycle per 60 seconds. This matches positions and velocities at the boundary without a dissolve. Mean speed adjustment is about 5.15%, maximum 12.11% relative to accepted v10; do not slow global playback.

Snow: quantize each fall duration to a divisor of 60, follow its existing diagonal direction, and reset the trajectory only while opacity fades at the top/bottom of its field. Preserve count, size/opacity ranges and deterministic seed. Keep it beyond the foreground arch.

Fog: use paired advected banks with twenty-second staggered lifetimes; local sine-squared appearance/dissipation hides resets. Retain existing velocities and density settings. Supporting smoke and event schedules repeat on twenty seconds; exterior halos on ten seconds. The combined water/snow scene differs at 0/20/30 seconds and has a genuine sixty-second overall timeline.

## Delivery and checks

Render exactly 1,800 frames at 30 fps, silent, with no duplicate endpoint. Produce 720p review and 4K master from the same source-frame pass. Use H.264 QP0 after YUV420 conversion to avoid previously encountered temporal quantization seam drift. Decode every frame; compare encoded last-to-first change with ordinary adjacent-frame changes and confirm dimensions/duration. Verify a two-repeat preview across sixty seconds without a player restart. No global fade, reverse motion or camera movement.

Reproduce from repository root:

```powershell
python scripts/render_glacier_delivery.py --config creative/glacier-sanctuary/animation/scene-plan-v11.json
python scripts/check_glacier_repeat.py
```

Existing video destinations are protected from overwrite. Read final-v11/delivery-validation.json, analytic-loop-checks.json and repeat-validation.json. Acceptance applies to the user's v10 look and explicit request to finish it; no assistant continuous-playback judgment is claimed. Keep source/code/config hashes and exact feedback together. The approved final master uses narrow Git LFS tracking and independently verified remote restore; drafts stay local.
