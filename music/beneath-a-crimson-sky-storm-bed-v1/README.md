# Beneath a Crimson Sky — continuous storm bed v1

Built 2026-11-11 as step 2 of the [standing plan](../../creative/IMPROVEMENT_LOG.md): a storm layer that never switches off, made before the music is chosen. Ten minutes, effects only, no music. User listening is pending; the assistant has not listened.

| File (in `exports/15-beneath-a-crimson-sky/storm-bed-v1/`) | Contents |
| --- | --- |
| `storm-bed-dark-10min.mp3` | Sheltered wind in two decorrelated layers plus a continuous low grit floor. |
| `storm-bed-open-10min.mp3` | The same, plus a steady fine-sand hiss (1.5–7 kHz) 14 dB below the wind. |
| `storm-bed-dark-with-thunder-10min.mp3`, `storm-bed-open-with-thunder-10min.mp3` | Each bed with four distant thunder rolls at 1:18, 3:09, 5:36 and 8:10. |
| `thunder-stem-10min.mp3` | Thunder alone. |

Each has a matching FLAC. Both beds share one constant gain (dark bed at −30 dBFS RMS), so the only difference between dark and open is the hiss layer.

## How it avoids repeating

Only two recordings exist: a 30-second wind and a 12-second grit take. Every layer is drawn as unequal overlapping sections from random positions in its source (86 and 66 wind sections, 206 grit, 184 hiss), so nothing recurs on a fixed period. A slow swell of ±2.5 dB follows three unequal cycles (47, 83 and 131 seconds). The underlying recordings are still short; new longer wind and sand takes would improve this.

## Measurements, bed with thunder, no music

| Measure | Dark | Open | SIGNAL STATION (full mix) | WINTER WATCH (full mix) |
| --- | ---: | ---: | ---: | ---: |
| 2–8 kHz band relative to total | −17.5 dB | −13.9 dB | −18.5 dB | −21.5 dB |
| 2–8 kHz 1 s level spread | 7.8 dB | 6.2 dB | 2.9 dB | 7.6 dB |
| Spectral flatness 2–8 kHz | 0.05 | 0.46 | 0.40 | 0.04 |
| 30 s level spread | 2.6 dB | 2.6 dB | 1.9 dB | 3.1 dB |
| 6 dB stand-out moments per minute | 0 | 0 | 2.4 | 1.5 |

The reference columns are full mixes with music, so the band levels are not comparable until music is added; music will lower the bed's share. The comparison that matters is the final mix. [Full figures](bed-measurements.json) · [Build report and settings](bed-report.json) · [Script](build_bed.py).

Rebuild: fetch the two library sources with `git lfs pull --include="music/sfx-library/assets/wind-soft-exterior-01.mp3,music/sfx-library/assets/grit-mineral-soft-01.mp3"`, then run `build_bed.py` in `.local/audio-analysis`. The output folder must not exist.

## Next

Audition both 60-second music tests under each bed. The two test files are not on this machine: they were kept local on the other PC and are not in Git.
