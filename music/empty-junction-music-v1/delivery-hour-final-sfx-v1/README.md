# The Empty Junction — one-hour final SFX combination v1

2026-10-31. User asks to use the supplied wind, distant train and mineral grit in the final SFX mix and provide example sections for checks. This delivers the full music-plus-effects hour, a separate same-level SFX-only stem, and three one-minute in-context examples. Earlier rejected radio/compressor ideas are not included. No new generation is performed.

## Check examples

These are excerpts of the actual final full mix at its actual gains, without extra normalization or audition boosts.

| Example | Full-hour section | What to listen for |
| --- | --- | --- |
| [01 Wind](../review/Empty-Junction-check-01-wind-60s-v1.mp3) | 0:15–1:15 | Music + wind; wind fades out by excerpt 0:45, leaving music. No train or grit. |
| [02 Train](../review/Empty-Junction-check-02-train-60s-v1.mp3) | 1:45–2:45 | Music + train at excerpt 0:20–0:45. No wind or grit. |
| [03 Grit and wind](../review/Empty-Junction-check-03-grit-and-wind-60s-v1.mp3) | 3:05–4:05 | Grit at excerpt 0:13–0:25 and 0:41–0:53, with music and wind. Wind ends by 0:55. No train. |

Check whether each effect can be noticed without taking over, whether the grit is too scratchy or sharp, whether the train feels far enough away, and whether returns to music alone feel natural. User balance/full-session approval remains pending. Assistant checks are technical, not listening.

## Full delivery

- [Combined full-hour MP3](media/The-Empty-Junction-1-Hour-final-SFX-v1.mp3).
- [Combined full-hour 24-bit FLAC](media/The-Empty-Junction-1-Hour-final-SFX-v1.flac).
- [Separate one-hour SFX-only 24-bit FLAC](media/The-Empty-Junction-1-Hour-SFX-only-v1.flac): wind + train + grit, without music. Do not add this stem to the combined file; it already contains these effects.

The original two music sources and arrangement are retained from the verified train-option FLAC. Wind remains one minute on/two minutes off, with five-second fade-ins and eight-second fade-outs inside active minutes. Train remains seven appearances at 2:05, 10:22, 19:24, 28:17, 37:31, 46:22 and 55:20, entirely in wind-free gaps, at the previously proposed +4.5 dB source gain with three/six-second entrance/exit fades.

The new 12-second grit source appears nineteen times within selected wind minutes, sometimes in two separated bursts. It uses fixed +4.2 dB gain (source −41.2 LUFS, nominally −37 LUFS before fades), one-second entrance and 2.5-second exit fades, and also follows the wind envelope. No grit overlaps a train or occurs during a wind-off interval. This is a trial balance requiring user checks, not a universal gain rule. Every exact start/end is recorded in [mix-recipe.json](mix-recipe.json).

No EQ, limiter, compressor, pitch shift or time stretch is added. The original hour's twenty-second closing fade is retained without applying another. The SFX stem is silent outside the scheduled wind/train/grit windows and is already silent during the final two minutes.

## Validation and preservation

[Delivery validation](delivery-validation.json) records full-length decode of both full mixes and the SFX stem, exact 3,600 seconds/172,800,000 stereo frames, finite samples, no clipping, loudness/true peak and full sample comparison against deterministic PCM. The lossless outputs must agree within 24-bit quantization tolerance. Render checks compare all full-mix samples outside grit events with the previous lossless mix exactly, and test all SFX-stem quiet-gap samples for exact silence. All three excerpts are decoded and compared with the matching regions of the final mix; [example-sections.json](example-sections.json) contains the details.

[Delivery paths](delivery-paths.json) is written only after copying the three validated outputs into the standard ignored exports folder and confirming SHA-256. Original supplied source bytes are copied/hash-verified under ../sources/; Downloads, old mix variants, art and animation remain unchanged. Actual model, settings and prompt used for supplied generations are not verified. User-authorized combination does not imply final listening acceptance.

[build-final.cjs](build-final.cjs) and [shared verifier](../audio-verify.cjs) use Node built-ins and FFmpeg. Existing outputs refuse overwrite. Source audio, PCM caches and exported full-length media are local, not remotely backed up by these actions. No video assembly, upload, paid service, commit or push is performed.
