# The Empty Junction — final SFX mix v3, grit softened further

Current decision, 2026-10-31: user says "ok i tihnk i'm good with it" and asks whether the audio is ready. V3 is the chosen audio mix; current balance is accepted and further SFX changes stop unless requested. [Exact approval and scope](user-approval-2026-10-31.json). A continuous full-hour listening session has not been reported; this does not withhold the user's approval of the current version. The pending-review statements below describe delivery-time state before this feedback.

2026-10-31. User heard the six-decibel quieter V2 example and said "yeah much better, but down a tiny bit more please". V3 lowers grit by another 1.5 dB: **−3.3 dB source gain**, nominally **−44.5 LUFS before fades**, 7.5 dB below original V1. Music, wind, train, all timings and all fades remain unchanged.

## Listen

- [Latest 60-second grit check](../review/Empty-Junction-check-03-grit-and-wind-60s-v3.mp3).
- [Previous V2 check, 1.5 dB louder grit](../review/Empty-Junction-check-03-grit-and-wind-60s-v2.mp3).
- [Original V1 check, 7.5 dB louder grit](../review/Empty-Junction-check-03-grit-and-wind-60s-v1.mp3).

Same full-hour section 3:05–4:05; grit appears at excerpt 0:13–0:25 and 0:41–0:53. These are the actual mix levels, without audition boosts. V2 received provisional positive feedback, followed by this requested further reduction; no V3 or full-session approval is inferred.

## Full files

- [Combined one-hour MP3 v3](media/The-Empty-Junction-1-Hour-final-SFX-v3.mp3).
- [Combined one-hour 24-bit FLAC v3](media/The-Empty-Junction-1-Hour-final-SFX-v3.flac).
- [Separate one-hour SFX-only FLAC v3](media/The-Empty-Junction-1-Hour-SFX-only-v3.flac).

[Recipe](mix-recipe.json), [three example records](example-sections.json), [full delivery validation](delivery-validation.json), [revision comparison](revision-comparison.json) and [verified export paths](delivery-paths.json) record actual outputs. Full mixes and the separate stem must decode to exactly 3,600 seconds, have finite unclipped samples, pass true-peak/loudness checks and match the deterministic PCM recipe. Samples outside grit events retain the previous verified music/wind/train mix exactly during rendering. The three check clips are compared with their corresponding full-mix regions.

Same existing music arrangement, twenty one-minute wind windows separated by two-minute gaps, seven train passages in wind-free gaps, nineteen grit events during selected wind minutes, and one twenty-second closing fade. SFX-only stem contains wind/train/grit without music; do not add it to the combined file. No new generation, EQ, compression, limiter, time stretch or pitch change. Source audio and prior complete versions/check clips are preserved.

The shared builder is [build-final.cjs](../delivery-hour-final-sfx-v1/build-final.cjs), invoked with `--version=v3 --grit-db=-3.3`. The earlier unparameterized renderer remains archived in ../history/. V2 completed full local validation after the request for V3; its media and audition are preserved locally as history, without copying V2 into the standard exports folder. V3 is the current requested delivery.

Assistant verification is technical, not listening. User V3 balance and full-session verdict are pending. Large media/cache remain ignored local files; no video assembly, publication, commit, push or remote backup is performed.
