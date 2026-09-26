# Basalt assembled export review

Source: G:/AI/colony/exports/02-basalt-transmission/basalt.mp4, 2,668,815,183 bytes. Reviewed 2026-09-26. Original unchanged.

Metadata: 02:00:00, H.264 3840x2160 30 fps, stereo AAC 48 kHz approximately 197 kb/s. Whole-file packet traversal and full audio decode/loudness completed without failure. Six stills and six two-second boundary windows decoded. This is not full video decode verification or continuous assistant playback.

## Findings

1. Audio is aligned with the supplied two-hour master in ten-second excerpts at 1:00, 59:50 and 1:59:50, with waveform correlation 0.996–0.999. It has been boosted about 1.7 dB: output -16.0 LUFS/-2.2 dBTP versus source -17.7 LUFS/-3.9 dBTP. No measured peak clipping. If preserving playlist loudness was intended, retain source gain rather than normalizing each export silently.
2. Overlay confirmed present at 15:04, 30:04 and 1:00:04, absent in samples 0:04, 2:04 and 1:59:59. Consistent with the configured 15-minute interval. User should decide if this is desirable for ambient viewing.
3. Background color changes during the overlay segment. At matching loop phase, decoded 640x360 frames at 0:04, 14:44 and 15:24 are identical; 15:04 differs even in the upper 240 rows, outside the graphic. Mean RGB difference against 14:44: +2.037, +1.334, -2.275 on 0–255 scale; mean absolute difference 2.208. Inspect color matrix/range/pixel-format handling between plain and composited segments, and ensure both use one consistent transform. The cause is not yet established from app code. Merely tagging metadata may not repair pixels already converted incorrectly.
4. Ordinary 20-second boundaries show small numeric outliers (about 0.278 MAE vs median adjacent 0.040 at 320x180), while overlay boundaries are larger (about 1.796). Numerical ratios alone do not establish visible flicker; inspect supplied short clip and compare encoded boundaries with the source. Original approved loop's seam was comparable to normal frame changes.

## Local review files

- report.json: sampled audio and boundary measurements.
- audio-loudness.txt: complete output audio EBU R128 summary.
- packet-check.txt: whole-file demux/packet traversal warnings (empty if none).
- export-contact-sheet.jpg: six sampled stills.
- overlay-transition-check.mp4: original source 14:55–15:15, 720p silent preview; overlay section starts around preview 0:05.

Recommendation: review/fix the overlay section's background color change before publication. Confirm intended overlay frequency and whether export normalization is enabled. Do not claim full video decode verification or final user visual approval.
