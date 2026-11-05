# Below the Snowline — final two-hour 4K video

[Open the final video](../../exports/13-below-the-snowline/Below-the-Snowline-2-Hours-4K-v1.mp4)

Exact runtime **2:00:00**, 3840×2160 at 30 fps, 216,000 frames. H.264 YUV420p BT.709/TV with stereo 48 kHz AAC. Size 40,270,588,234 bytes (40.27 GB). SHA-256 `e1fd2b2c93dd993e84e06cea480f8daaf605f11207bca10d3022237fd0bc470a`.

The user approved the V6 scene with its corrected cliff masking, blue-white shuttle engines and stronger cannon charge, then requested this full export. The production renderer preserves that treatment and renders at the original 1672×941 artwork dimensions before Lanczos scaling to 4K. Continuous sky, weather and equipment phases are adjusted to whole cycles within 120 seconds. Snow and fog keep moving forward; shuttle/bridge/cannon events retain their scheduled passes and reach hidden/off states at the boundary. There is no whole-scene dissolve or reversed footage. The 120-second visual cycle repeats independently of the full audio event schedule; all audio event timings remain untouched. The native/source, cloud-map, cliff-occlusion and seam checks are recorded under `visual/`.

The existing two-hour V6 soundtrack contains all six layers. The original unfaded FLAC was hash-verified, then given +0.4 dB once and one 20-second linear closing fade. Every preparation sample was checked independently. Actual Colony v3 adds its opening once: AMBIENT COLONY/logo/PRESENTS, BELOW THE SNOWLINE and “Stay a while and listen”; graphics clear by 22 seconds. Sound is silent through 5 seconds and rises to the supplied level at 20 seconds. No extra SFX, music joins, stretching or loudness matching are added.

The first 120-second unit carries the opening; the following 59 clean units retain identical compressed picture payloads. Colony decoded the entire finished file. Independent validation checked all 216,000 timestamps, the copied units, all decoded pictures of the first clean unit, exact source pictures after the opening clears, and every AAC sample against the original master plus the intended gain/fades. Audio correlation 0.999983816; gain difference -0.007207 dB. Opening and closing diagnostic windows also passed individual checks.

## Files and reproduction

- `production-plan.json`: user authority and exact source audio.
- `visual/`: frozen source snapshot, native periodic renderer, render/audit/encoded-master checks and 4K master.
- `prepare_audio.py` and `audio-preparation-validation.json`: exact assembly FLAC recipe and sample checks.
- `assemble_with_colony.py`: verified preserved intro engine, 120-second Prepared master and final assembly; no installed application modifications.
- `verify_final.py`: `--video`, `--audio`, `--stills`, `--hash`, then `--finish`.
- `delivery-validation.json`, `video-validation.json`, `audio-validation.json`, `colony-export.json`: final evidence.
- `final-contact-sheet.jpg`: decoded opening, shuttle/cannon and repeat-boundary stills.

Original V6 preview, artwork, music and SFX are preserved. The complete long-form video is technically checked; user combined-playback review and YouTube upload/checks remain separate. Assistant inspection covers decoded temporal stills, not continuous playback or full listening. No paid generation, upload, commit or push was performed for this export. Long media and regenerable caches remain local under project policy. A Git push of records does not archive the full upload file.

## Backup checkpoint — November 5, 2026

The user subsequently requested commit and push of the completed work. The exact 120-second 4K visual master and 135-second opening/loop preview are selected for Git LFS, together with this package, frozen sources, audit evidence and current upload records. See `../production-backup-2026-11-05-snowline/` for the exact selection and local remote verification receipt. The two-hour upload video remains local under `EXPORTS.md`; its fingerprint does not represent a remote backup of that file. The earlier no-commit/push statement describes delivery before this subsequent request.
