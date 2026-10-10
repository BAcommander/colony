# Icebound Weather Post — Winter Colony Night auditions

2026-10-04. Original seven-minute export preserved byte-for-byte under exports/07-icebound-weather-post/source/. SHA-256 and decoded duration (420.010667 seconds at analysis rate) are in analysis.json. User supplied the longer file after choosing Colony Winter Night's musical direction and reporting unwanted lyrics in that earlier short test. No assistant listening or vocal-absence claim.

Candidate retains source 1:23–6:54 (331 seconds), using an eight-second equal-power sine/cosine crossfade and fixed -8 dB gain. The first search reached its boundary; the expanded search found this level/coarse-spectrum candidate. Original search records are preserved. These measurements cannot establish harmonic compatibility.

- Short audition: exports/07-icebound-weather-post/Icebound-Weather-Post-Winter-Colony-Night-join-v1.mp3 — 58 seconds; transition at 0:25–0:33.
- Three-repeat preview: exports/07-icebound-weather-post/Icebound-Weather-Post-Winter-Colony-Night-three-repeats-v1.mp3 — 16:17; transitions at 5:23–5:31 and 10:46–10:54.

Both MP3s fully decoded with exact sample counts and finite samples. Measured short/long levels are -20.3/-20.2 LUFS and true peaks -9.0/-8.9 dBFS. No clipping. Short audition uses 0.15/0.3-second edge fades; three-repeat preview uses one 5-second opening and 10-second closing fade. See audition-v1.json and loudness logs.

User accepted the short join and requested the hour on 2026-10-04. The [one-hour delivery](one-hour-delivery-v1.md) is now complete. Full-hour listening remains pending; absence of vocals is not independently verified. Animation status remains separate. Media are local ignored exports, not backed up by Git. No credits, commit or push.

Reproduce with analyze.py then make-auditions-v1.py using the existing Python/NumPy runtime and local FFmpeg. Encoding refuses to overwrite existing exports.
