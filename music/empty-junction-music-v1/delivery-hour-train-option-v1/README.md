# The Empty Junction — optional distant-train mix v1

2026-10-31. User supplies `Distant_freight_trai_#4-1793489393057.mp3` and asks to add it as an option to the existing mix. The original one-hour music/wind version remains the baseline. No radio or compressor is added, and no new sound generation is performed.

## Listen

- [90-second audition](../review/Empty-Junction-train-option-audition-90s-v1.mp3): full mix 1:35–3:05; the train enters at excerpt 0:30 and lasts approximately 25 seconds.
- [Optional full-hour MP3](media/The-Empty-Junction-1-Hour-train-option-v1.mp3) and [24-bit FLAC](media/The-Empty-Junction-1-Hour-train-option-v1.flac).
- [Baseline hour and delivery paths](../delivery-hour-v1/README.md).

The train appears at **2:05, 10:22, 19:24, 28:17, 37:31, 46:22 and 55:20**. Each complete event is inside a wind-free interval. Seven irregular appearances across the hour avoid treating it as a frequent short loop. Wind retains the existing one-minute-on/two-minute-off schedule. The music arrangement, gains and closing fade are inherited unchanged.

The supplied MP3 actually has approximately 25 seconds of audio, despite the earlier suggested 12-second test setting. Actual generation controls and exact prompt used are unknown. Source analysis gives −39.5 LUFS, 9.7 LU LRA and −20.3 dBTP. A fixed +4.5 dB trial gain places the isolated source at nominally −35 LUFS before three-second entrance and six-second exit fades. This is a proposed balance for user listening, not an accepted mix or universal level. No EQ, compressor, limiter, stretch or pitch change is used.

## Verification and records

[Recipe](mix-recipe.json) records hashes, actual decoded source duration, gain and every event. [Validation](delivery-validation.json) covers full output decode, exact 3,600-second duration, finite samples, no clipping, true peak/loudness and full sample comparison against the recipe PCM for both formats. While rendering, all samples outside train events are compared with the verified lossless baseline and must match exactly. [Delivery paths](delivery-paths.json) records export copies only after SHA-256 verification.

[build-train-option.cjs](build-train-option.cjs) uses Node built-ins and FFmpeg, and refuses existing output files. Original source bytes are hash-verified under ../sources/; Downloads and baseline exports are unchanged. The export script is the existing one-hour copy/check script, reused without modifying it. Large media and PCM caches remain ignored and local. No upload, video assembly, commit, push or remote backup is performed. Assistant checks are technical; the supplied source has not been independently listened to by the assistant and user approval remains pending.

## One further SFX proposal

[Soft mineral-grit rustle](../mineral-grit-sfx-prompt-v1.txt) is a proposed lighter texture tied to the ground powder already animated in the original Junction scene. Later audition it only with selected wind passages, at low level, rather than filling every quiet gap. This is fictional scene sound, not a field recording or proof of materials. It is ungenerated and not included in either mix.
