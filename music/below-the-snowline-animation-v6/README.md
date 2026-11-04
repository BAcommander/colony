# Below the Snowline — V6 cliff occlusion and blue engines

User feedback: the shuttle crossed the left rock wall incorrectly; its engines should have blue flame similar to the cannon charge. This revision preserves V5 and delivers a new two-minute review using the same soundtrack.

## Changes

- The left flight boundary is manually traced against the original 1672×941 cliff silhouette. The old diagonal both exposed rock pixels and hid clear sky prematurely. A one-native-pixel inset protects the snowy lip, with four-times supersampling for subpixel edge coverage.
- The same occlusion mask covers the hull, exhaust, nozzle cores and glow. The right-hand frosted frame is also traced so the flight exits against the actual frame. Flight paths, sizes, timings and constant opacity remain unchanged.
- The engines now use blue/cyan tails and blue-white cores matching the cannon charge. Mirrored nozzle positioning is corrected by one output pixel. The generated shuttle master, its original alpha and the landscape remain unchanged.

## Approved review — 2026-11-04

The user accepted this V6 preview ("perfect") and explicitly requested commit/push. See `user-approval.json`.

`Below-the-Snowline-v6-with-V6-audio-2min.mp4` is the 120-second, 1280×720, 30fps review. Inspect the left cliff around 0:27–0:30 and 1:36–1:39; 0:39–0:50 shows the blue exhaust with the charged cannon. The unchanged two-minute V6 audio excerpt already contains all six sound layers.

`audit_flight.py` independently checks cliff masking against manually traced source geometry, includes the previous V5 mask as a positive control, and compares unaffected animation layers. `repair-validation.json` records those results. `finish_review.py` assembles the six rendered sections and checks every decoded frame/timestamp, section joins, native-picture controls and the complete AAC soundtrack against the existing FLAC. The assistant inspects temporal and decoded stills; assistant continuous playback/listening are not claimed. User acceptance is recorded separately above.

Reproduce with `audit_flight.py`, `render_v6.py samples`, `render_v6.py render`, then `finish_review.py`. Existing rendered files are protected against overwrite. `cache/` contains regenerable intermediates and diagnostics. `package-manifest.json` fingerprints the delivered review package.

This approved two-minute preview is not a final seamless loop or full-length 4K export. No new image generation, soundtrack revision or upload. The user authorized backup on main; exact scope and post-push evidence are recorded under `../production-backup-2026-11-04-v6/`.
