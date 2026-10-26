# Illuminated Horizon + Illuminated Stillness — two-hour alternating soundtrack

User accepted both transition previews (“yeah those transitions sound good”) and requested two hours alternating the two tracks. This delivery uses complete original Horizon (8:30) and the supplied long Stillness (3:00), with the accepted eight-second equal-power overlaps and unchanged fixed gains of -7.74 / -7.08 dB. It does not use the earlier rejected slowdown, spectral drone or source-separation experiments.

The sequence starts with Horizon. Track A restarts every 11:14; Stillness starts 8:22 into each cycle. There are eleven Horizon occurrences (the final one uses 7:40) and ten complete Stillness occurrences, with twenty alternating joins. Exact total duration is 2:00:00. One twenty-second half-cosine closing fade ends the final Horizon passage. Source pitch/tempo and existing source fades are retained. No extra opening fade is baked into the master: apply the once-only current opening in Colony during later video assembly. No SFX, EQ, separation or dynamic normalization.

The 320 kb/s MP3 is for convenient playback. The stereo 48 kHz/24-bit FLAC is the lossless master for later assembly. Both are local outputs; no video assembly, paid generation, commit, push or remote media backup is included. Original files and previously approved auditions remain preserved.

See mix-recipe.json and track-timeline.tsv for exact placement and source hashes. Encoding alone is not verification: delivery-validation.json must report passed. Validation decodes every sample of both complete files, checks exact 345,600,000 frames per channel, finite values, no clipping, integrated loudness and true peak. Every decoded FLAC sample is additionally compared with the complete streaming recipe within 24-bit quantization tolerance, covering all twenty joins and repetitions. Assistant has not listened; approval covers the short transitions and the requested extension, not full two-hour listening.

## Verified final locations

- [Illuminated-Horizon-and-Stillness-2-Hours-v1.flac](G:/AI/colony/exports/spirewatch/Illuminated-Horizon-and-Stillness-2-Hours-v1.flac)
- [Illuminated-Horizon-and-Stillness-2-Hours-v1.mp3](G:/AI/colony/exports/spirewatch/Illuminated-Horizon-and-Stillness-2-Hours-v1.mp3)

Long media are stored in the standard Git-ignored exports/spirewatch/ directory. delivery-paths.json records exact hashes and locations. Build script output paths describe the temporary encode staging; finalize_delivery.py moves only the two fully verified files. No remote backup is implied.
