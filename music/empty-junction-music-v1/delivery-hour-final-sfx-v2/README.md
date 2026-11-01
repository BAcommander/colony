# The Empty Junction — final SFX mix v2, grit reduced 6 dB

User feedback, 2026-10-31: "grit is probably too loud, what levels did we use". Assistant proposed reducing grit by 6 dB, from +4.2 dB to −1.8 dB source gain, and the user replied "ok try it". V2 applies that reduction to all nineteen existing grit events in the combined one-hour mix and separate SFX stem. This authorizes the trial change, not listening approval.

## Check the change

- [Revised 60-second grit check](../review/Empty-Junction-check-03-grit-and-wind-60s-v2.mp3).
- [Previous, louder version of the same passage](../review/Empty-Junction-check-03-grit-and-wind-60s-v1.mp3).

Both are full-hour 3:05–4:05, at their actual final gains with no audition boost. Grit appears at excerpt 0:13–0:25 and 0:41–0:53. Music and wind levels are unchanged. The wind-only and train checks are also retained as V2 excerpts at unchanged levels in [example-sections.json](example-sections.json).

## Full delivery

- [Combined one-hour MP3 v2](media/The-Empty-Junction-1-Hour-final-SFX-v2.mp3).
- [Combined one-hour 24-bit FLAC v2](media/The-Empty-Junction-1-Hour-final-SFX-v2.flac).
- [Separate one-hour SFX-only 24-bit FLAC v2](media/The-Empty-Junction-1-Hour-SFX-only-v2.flac).

Grit is now nominally −43 LUFS in isolation before fades (source measured −41.2 LUFS, gain −1.8 dB). Music remains nominally −23 LUFS, wind −35 LUFS and train −35 LUFS before their respective fades. These are source-level descriptions, not the integrated loudness of the complete mix. Actual full-mix and stem measurements are in [validation](delivery-validation.json).

Music arrangement, nineteen grit timings, all fades, twenty one-minute wind windows, two-minute wind gaps and seven train timings remain as V1. Original and V1 delivery files are preserved. No radio, compressor, new generation, processing effects, video assembly or publishing is added.

[Recipe](mix-recipe.json), [example records](example-sections.json), [validation](delivery-validation.json) and [revision comparison](revision-comparison.json) document the result. V2 completed local validation, but the user requested another small reduction; [V3](../delivery-hour-final-sfx-v3/README.md) is the current requested delivery. V2 media remain locally in this package and were not copied into standard exports, so there is no V2 export-path receipt. Full files are decoded and compared with deterministic PCM, with exact hour duration, finite samples, no clipping and true-peak/loudness checks. The shared [builder](../delivery-hour-final-sfx-v1/build-final.cjs) accepts `--version=v2 --grit-db=-1.8`; the pre-parameter version is preserved in ../history/.

Assistant review is technical, not listening; user balance and full-session acceptance remain pending. Large media and PCM are ignored local files, not remote backups. No commit or push is performed.
