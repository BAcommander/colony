# The Empty Junction — one-hour ambience v1

User requested the one-hour version on 2026-10-31, ending radio experimentation. This audio delivery alternates the two supplied four-minute music sources with the latest requested intermittent wind. No radio is included and no new generation is performed.

## Arrangement

- Exactly 3,600 seconds, stereo 48 kHz. Delivery formats: 192 kb/s MP3 and 24-bit FLAC.
- Signal Cabin Wait and Quiet Signal Cabin alternate, using fixed −9.13/−9.76 dB gains and twelve-second equal-power overlaps. Nine A occurrences and eight B occurrences; the last A is shortened by the one-hour endpoint. Sixteen handovers.
- First A uses source 0:00–3:44. Later A occurrences use 0:02–3:44; B occurrences use 0:02–3:50. The closing fades from the generated sources are excluded so the arrangement keeps playing through each handover. First A-to-B timing matches the preceding preview. The return B-to-A join is newly assembled for this extension.
- Wind retains the previous +7.85 dB source gain and crossfaded 24-second source period. Twenty one-minute wind windows begin at 0:00, 3:00, 6:00 and every three minutes through 57:00. Each window includes five-second fade-in and eight-second fade-out; the following two minutes have no added wind. Wind uses a separate global clock from the music handovers.
- One twenty-second closing fade. Only the first source's short generated entrance remains; no added production opening fade or branded intro. Apply the current once-only production intro later if assembling video.
- No EQ, compressor, limiter, time stretch or pitch change. Existing generated music and wind are retained.

## Verification and files

[Recipe](mix-recipe.json) contains every occurrence, gain, trim and wind window, plus original source hashes. [Render checks](render-checks.json) cover all rendered samples and the entire wind-off schedule. [Delivery validation](delivery-validation.json) records full-length decode, exact frame count, finite samples, clipping/headroom, loudness and full sample comparison against the deterministic recipe PCM for each export. The FLAC is compared within 24-bit quantization tolerance; the MP3 is also compared across its entire decoded duration. [Delivery paths](delivery-paths.json) is written only after hash-verifying copies in the project's ignored exports folder.

[One-minute B-to-A return-join excerpt](../review/Empty-Junction-B-to-A-return-join-60s-v1.mp3) covers the hour's 6:48–7:48, with the handover at excerpt 0:20–0:32. No separate listening approval of this new join or the complete hour is inferred. Assistant verification is technical, not listening.

[build-hour.cjs](build-hour.cjs) uses Node built-ins and FFmpeg. Originals and prior previews are unchanged. Fresh runs refuse existing media. `--resume` requires matching recipe fingerprint, source hashes and complete PCM size, then validates reused exports. [export-delivery.ps1](export-delivery.ps1) copies only the two validated exports, refuses differing existing destination bytes and checks SHA-256 after delivery. No files are deleted.

Large media and PCM caches remain ignored locally. This request does not perform a video render, upload, commit, push or remote backup. Final artistic/full-session listening remains with the user.
