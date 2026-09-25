# Glacier Sanctuary - sixty-second 4K delivery

The user accepted v10's look on 2026-09-25 and requested a sixty-second 4K loop. V11 keeps the slow water, distant snow/fog, vent smoke and facility lighting. Foreground snow remains absent. Loop timing is adjusted without globally slowing the scene.

## Media

- 4K master: final-v11/glacier-sanctuary-v11-60s-4k.mp4
- 720p preview: final-v11/glacier-sanctuary-v11-60s-720p.mp4
- Two-repeat join preview: final-v11/glacier-sanctuary-v11-two-loop-check-720p.mp4 (two minutes, join at 1:00).

The master is 3840x2160, 30 fps, 1,800 frames, silent. Source art is 1672x941, so 4K is upscaled. The overall timeline is sixty seconds, not a repeated twenty-second export; individual supporting effects can repeat sooner.

## Verification and acceptance

Read final-v11/delivery-validation.json for full decode, duration, frame count, encoded seam and output hashes. Individual layer endpoints and speed deviations are in analytic-loop-checks.json. repeat-validation.json verifies every decoded frame against two copies of the source loop. Sampled decoded images are saved alongside. These are technical checks and still inspection, not a claim of assistant continuous playback or user review of the full sixty-second export.

User acceptance: "ok i think we can go with this, extend it out into the 60 second loop ij 4k?" This approves the v10 look and finishing request.

## Restore or reproduce

The exact 4K master is tracked with Git LFS. Restore with `git lfs pull`, then compare SHA-256 with delivery-validation.json. Remote verification status is recorded separately in remote-backup.json; settings being pushed alone does not prove the video is backed up. Drafts and repeated previews stay local.

Production configuration: scene-plan-v11.json. Brief: production-prompt-v11.md. From the repository root:

```powershell
python scripts/render_glacier_delivery.py
python scripts/check_glacier_repeat.py
```

Both commands refuse existing video destinations. Pull the master instead of rerendering it unnecessarily. Dependencies: Python, NumPy, Pillow, OpenCV, imageio-ffmpeg; render_glacier.py, water_surface.py and ambient_effects.py. Source image and its hash are in the configuration. No paid service or separate credits are needed.

## Carry forward

The accepted water method is a 24-wave perspective reflection surface, calmed in v9 and slowed/filtered in v10. Keep its strengths; use sixty-second integer wave cycles and locally faded particle resets for delivery. Failed methods and exact feedback remain in water-method-status.json. Research and the 2D approximation's limits are documented in production-prompt-v10.md. Earlier motion studies are history, not current pending reviews.
