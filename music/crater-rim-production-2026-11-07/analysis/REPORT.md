# Crater Rim original music measurements — 2026-11-07

Both original MP4 audio streams decode completely to exactly 14,400,000 stereo sample frames: 300 seconds at 48 kHz. FFmpeg reports no decode errors; every decoded sample is finite. The container/video duration must not be used as the musical duration. This is numerical analysis, not listening or artistic approval.

| Original | Full integrated loudness | Full true peak | Full LRA | Interior 20–280s loudness / LRA | Recommended fixed gain |
| --- | --- | --- | --- | --- | --- |
| Survey Room at First Light | −16.91 LUFS | −4.57 dBTP | 3.20 LU | −16.73 LUFS / 2.90 LU | −6.3 dB |
| First Light Basin | −17.25 LUFS | −6.00 dBTP | 1.90 LU | −17.09 LUFS / 1.80 LU | −5.9 dB |

These gains put the interior music at approximately −23.03 and −22.99 LUFS, respectively, while preserving its dynamics. Expected standalone true peaks become approximately −10.87 and −11.90 dBTP, leaving headroom for quiet scene effects. Meter the assembled music/SFX mix again; the final level depends on crossfades and the chosen effects. The loudnorm filters in the analysis script wrote their processed output only to null: `input_*` measurements are the source readings; their `output_*` fields are not a processing recommendation. No normalized music file was created.

## Source boundaries and candidate arrangement

Both tracks have exact silence during their first second and a gradual entrance that reaches near-normal density around 14 seconds. Survey Room's outgoing level begins falling more strongly after about 286 seconds; Basin's outgoing fall starts earlier, around 280 seconds. Their final seconds are very quiet. Repeating all of those fades end to end would introduce recurring gaps.

Retain **4.000–294.000 seconds of each original** as the first arrangement candidate. These are overlap handles, not intended hard-cut playback boundaries. Use a **24-second equal-power Survey Room → Basin overlap** and a **30-second equal-power Basin → Survey Room overlap**. Exact source windows:

| Handoff | Outgoing source window | Incoming source window |
| --- | --- | --- |
| Survey Room → Basin | Room 270–294s | Basin 4–28s |
| Basin → Survey Room | Basin 264–294s | Room 4–34s |

The two retained passages are 290 seconds each; the repeated A/B arrangement interval is **526 seconds (8:46)** once both overlaps are accounted for. The finite first A/B pair lasts 556 seconds before its return transition. Use the 526-second interval only with proper circular/alternating boundary construction; do not repeat a finite A/B pair with a naked cut.

Actual decoded PCM was evaluated in memory at the fixed gains, with cosine/sine equal-power weights, for 20/24/30/36-second overlaps in both directions. No audio output was written by this analysis. The 24-second Room→Basin candidate's quietest one-second window was 0.75 dB below the median of its surrounding ten-second handles. Basin→Room at 20 seconds dipped 4.88 dB below its surrounding median; the 30-second overlap reduced this to 2.31 dB. Extending to 36 seconds did not improve that minimum. These are level-envelope comparisons, not proof of harmonic compatibility or a listening verdict. The recommended overlap correlations were +0.065 and −0.060, so broad waveform cancellation was not dominant.

Keep both short join auditions for user review, including roughly 10–15 seconds on each side. Preserve separate effects controls. Do not apply extra repeated entrance/exit fades, loudness normalization, compression, time stretch or pitch changes merely to meet the target. Apply only the chosen once-only programme opening and closing treatment later. Interior LRA is modest, especially in Basin; these readings do not establish that either composition avoids audible melodic repetition.

## Evidence and reproducibility

- `analyze_originals.py`: complete original-file decode, metadata, SHA-256, full/interior loudness and quarter/one-second envelopes.
- `original-source-analysis.json`: both complete analysis records and source fingerprints.
- `survey-room-analysis.json` / `first-light-basin-analysis.json`: individual records.
- `*-one-second-levels.json` / `*-quarter-second-levels.json`: complete source envelopes, including fade tails.
- `*-probe.json`, `*-decode.log`, `*-full-loudness.log`, `*-interior-loudness.log`: raw evidence; empty decode logs mean no FFmpeg errors.
- `measure_join_candidates.py` and `join-candidate-measurements.json`: in-memory equal-power comparisons and one-second levels.
- `recommended-arrangement.json`: exact candidate gains/cuts/overlaps for the production agent.

Source and proposed join PCM stayed in process memory. There are no decoded PCM caches or generated audition files in this analysis folder. Run the scripts with the existing ComfyUI Python interpreter and FFmpeg/FFprobe on PATH; this host currently needs elevated tool execution to access the interpreter's base installation, despite normal source-file access.
