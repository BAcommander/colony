# Crater Rim Survey — one-hour music and SFX audition

Prepared 7 November 2026 after the user supplied both five-minute music exports and requested an hour-long mix with SFX. The user accepted the presented mix on November 7 and requested commit/push: “ok i think that's decent commit and push it”. See [approval record](user-approval.json).

- [Full hour MP3](../../exports/14-crater-rim-survey/audio-1h-v1/Crater-Rim-Survey-1-Hour-music-and-SFX-v1.mp3) · [24-bit FLAC](../../exports/14-crater-rim-survey/audio-1h-v1/Crater-Rim-Survey-1-Hour-music-and-SFX-v1.flac).
- [Two-minute in-scene check](review/Crater-Rim-V5-with-music-and-SFX-2min-v1.mp4): audio from full mix 0:20–2:20, with short review fades. Wind enters at 0:25, reaches its plateau after a 12-second rise, and ends by 1:30. Room air is continuous. Existing V5 picture packets repeat twice unchanged; the longer visual schedule has not been built here.
- [First ten minutes with both tracks and SFX](review/Crater-Rim-full-pair-with-SFX-10min-v1.mp3).
- Dry joins: [Survey Room → Basin](review/Crater-Rim-Survey-Room-to-Basin-join-75s-v1.mp3) · [Basin → Survey Room](review/Crater-Rim-Basin-to-Survey-Room-join-75s-v1.mp3). Each join starts 15 seconds into its 75-second check. Review files share the full mix's playback gain; no separate normalization.

## Music

Both supplied MP4s contain exactly 300 seconds of stereo 48 kHz audio, despite 304.4-second video containers. Byte-exact originals and SHA-256 receipts are in `sources/` and `source-manifest.json`. They followed the V4 Survey Room / Across the Basin prompt handoff, but the actual executed text, settings and cost were not supplied.

Fixed music gains are −6.3 dB for Survey Room at First Light and −5.9 dB for First Light Basin. Interior programme levels are approximately −23 LUFS. Original dynamics, stereo, timing and pitch remain; no music EQ, compression, time stretching or added melody. The first Survey Room starts at its original zero; subsequent passages retain source 4–294 seconds. Equal-power overlaps are 24 seconds into Basin and 30 seconds back into Survey Room, selected from measured fade-tail comparisons. The first joins occur at 4:30–4:54 and 8:50–9:20. Subsequent A/B cycles recur every 526 seconds (8:46). Independent SFX timing does not eliminate repetition in the music.

## SFX and fades

Wind uses the original 30-second `music/sfx-library/assets/wind-soft-exterior-01.mp3`, never its boosted browsing preview. Source 1–29 seconds with a four-second equal-power overlap makes a 24-second cycle. A second-order 1800 Hz low-pass, applied in periodic context, gives a sheltered audition. The filtered cycle receives 5.48 dB fixed gain for nominal −38 LUFS before the event envelope. This is a new scene balance, not a copied approval from another video.

There are 18 wind passages, each roughly one minute, with 12-second rises and 18-second falls. Fully quiet wind gaps range from 110 to 147 seconds. Source phase and broad movement vary independently of the music joins. The first full-hour wind passage is 0:45–1:50. All exact events are in `mix-recipe.json` and `cue-sheet.txt`.

Room air is original procedural band-shaped noise at −45 dBFS stereo RMS, nominally 140–950 Hz, with narrow stereo and slow level variation. Its 197-second source period is independent of the music. It contains no recorded machinery, voices or tonal oscillator. The method adapts the established room-air generator with a new seed and scene-specific level. No paid generation was used. No radio, snow, train or grit was added.

The hour has one 20-second closing fade, applied equally to all stems. No Colony opening is baked; retain this closing fade and apply the current Colony opening once in later video assembly. Short auditions have separate 0.5-second entry and two-second exit fades that do not affect the hour. Dry music, combined SFX, wind-only and room-air-only FLACs are beside the full mix for later revisions.

## Checks and remaining review

Exact 3600 seconds, 172,800,000 stereo sample frames. All six full-hour files decoded completely and were compared sample by sample with their rendered references; lossless files agree within 24-bit quantization tolerance and MP3 correlation/SNR pass. Every decoded sample is finite and unclipped. Repeated dry joins match their first counterparts exactly. A separate audit checked all raw frames for exact mix = dry + SFX and SFX = wind + room; PCM stems end at zero. Source fingerprints are unchanged.

Combined measurements: **-22.98 LUFS, 2.3 LU LRA, -9.90 dBTP**. These are technical measurements, not a listening or harmonic-compatibility verdict. The user accepted the presented balance; uninterrupted full-hour listening is not asserted. The historical validation records retain their pre-review status. Long animation, final video and publication remain separate. [Backup and restore instructions](../production-backup-2026-11-07-crater-rim-audio/README.md).

`build_mix.py` reproduces the hour in a fresh output/cache version; `make_scene_review.py` creates the optional sound-in-scene check. See `analysis/`, `mix-recipe.json`, `delivery-validation.json`, `scene-review-validation.json` and `analysis/independent-stem-audit.json`. Large outputs remain under `exports/14-crater-rim-survey/audio-1h-v1/`; raw scratch is `.local/crater-rim-audio-2026-11-07-v1/`. Do not overwrite originals or approved earlier scenes.
