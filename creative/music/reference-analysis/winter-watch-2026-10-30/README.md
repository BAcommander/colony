# WINTER WATCH reference — 2026-10-30

User reference: [Ambient Outpost / WINTER WATCH — Remote Forest Outpost](https://www.youtube.com/watch?v=dDYH-75RJWA). User says they have listened to it for almost the whole day. This is their positive listening report; it does not identify which musical property caused that preference.

The URL was a live broadcast when inspected. The reusable tool acquired an audio-only 30-minute excerpt from the public one-hour HLS DVR window, starting approximately 1,815 seconds behind the live edge at metadata retrieval. The decoded recording is **1,800.0109 seconds**. A separate five-minute initial sample and earlier reports are retained. No whole-broadcast or all-day analysis is claimed. The stream's title timestamp changed during inspection.

## Measurements from the thirty-minute excerpt

| Measure | Result |
| --- | --- |
| Integrated loudness | −22.6 LUFS |
| Loudness range | 5.0 LU |
| True peak | −5.7 dBTP |
| One-second RMS, 5th / 50th / 95th percentile | −26.83 / −24.50 / −21.11 dBFS |
| Stereo correlation | 0.263 |
| Side energy | 36.86% |
| Spectral energy below 80 Hz | 33.25% |
| 80–250 Hz | 35.94% |
| 250 Hz–1 kHz | 26.70% |
| 1–4 kHz | 4.09% |
| 4–12 kHz | 0.0255% |
| 12–24 kHz | 0.000162% |

These measurements support describing the signal as weighted toward bass/lower mids, with very little high-frequency energy and substantially different stereo channels. Spectral percentages are not perceived loudness. LUFS describes the recording, not the user's playback volume. A positive amount of loudness movement does not automatically make a recording comfortable or interesting.

The highest multiband recurrence candidate is 628 seconds (10:28), score 0.495. Three ±3-second waveform searches returned only 0.267 / 0.226 / 0.197 correlations, with inconsistent offsets. Candidates at 620 and 608 seconds also have weak waveform matches. **Do not call this a confirmed ten-minute loop.** The tool checks selected short windows, not every possible offset or time stretch. Lack of a confirmed repeat here does not establish that the broadcast contains no repeated material.

## Practical next comparison

Use this as one positive listening reference. Compare a chosen Ambient Colony track with the same analyser, then audition both at matched listening levels. Investigate bass weight, how much upper-mid/treble activity attracts attention, stereo movement and the size/frequency of swells separately. A darker spectrum and moderate level movement are hypotheses to test in original music, not a recipe to copy or a measured explanation of user enjoyment. Instrument identity, harmony, phrase quality, reverb and absence of vocals have not been established by assistant listening.

## Files and verification

- [Compact measurement and provenance record](measurements.json), without third-party audio.
- Full [interactive thirty-minute report](../../../../exports/reference-analysis/winter-watch-30min-v2/report.html) and JSON/timeline remain local under ignored exports.
- Source recording: `exports/reference-analysis/winter-watch-30min-v1/reference-sample.m4a`; the v2 analysis reuses that exact recording. Report playback references that file.
- Reusable [tool instructions](../README.md), including file-picker/drag-and-drop launcher and CLI commands.
- Four tests pass: opposite-polarity stereo/spectrum; known feature recurrence; partial-tail/mono/silence/CLI preservation; actual repeated versus unrelated waveform offsets. A real YouTube DVR acquisition and full thirty-minute analysis completed. Report charts were visually inspected in the local browser and audio controls were available; no continuous assistant listening is claimed.

New tool/results are local work. No commit, push, paid generation, model installation, or upload of reference audio was performed for this request.
