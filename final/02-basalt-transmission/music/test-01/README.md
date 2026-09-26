# Basalt first generated tests — 2026-09-26

User supplied Basalt_Transmission_Outpost_2026-09-26T152953.mp3 and Copper_Dusk_Transmission_2026-09-26T152953.mp3 from Downloads. Both decode to 60 seconds. Screenshot shows Music v2.5, no finetune, one minute, two variants, displayed batch cost 1,800 credits. No user preference or listening approval supplied yet. No reliable assistant audition available.

Comparison uses stereo spectral power at 22.05 kHz; first/last 10 seconds excluded. Reference is the supplied PYRAMID track's 1:10–1:50 passage. These are representative measurements, not whole-track perceptual ratings.

| Energy band | Basalt Transmission Outpost | Copper Dusk Transmission | Reference |
|---|---:|---:|---:|
| Below 80 Hz | <0.01% | 78.92% | 19.12% |
| 80–250 Hz | 12.71% | 7.17% | 37.91% |
| 250–1000 Hz | 86.96% | 13.46% | 40.99% |
| 1–4 kHz | 0.32% | 0.46% | 1.98% |

Outpost's stereo correlation is -0.052; Copper's is 0.764; the reference excerpt's is -0.163. This suggests much more channel separation in Outpost, without proving aesthetic quality or mono compatibility. Typical one-second RMS ranges (10th–90th percentile) are 6.79 dB, 4.52 dB and 3.08 dB respectively. Both generated tests have movement in level; neither should be labelled flat from these measurements.

The two variants land at opposite tonal extremes: Outpost is predominantly midrange with very little deep bass; Copper is predominantly sub-bass. Outpost is a reasonable candidate if the user likes its atmosphere and wants more diffuse spatial character, but it may need a little supporting low-end. Copper may need less sub-bass if preferred. Do not choose a winner solely on these figures, and do not combine the files blindly: harmonic compatibility is unverified. Ask for user listening preference before revising or requesting a long generation. Match playback loudness before comparing.

Source files remain in Downloads; no audio was uploaded or added to Git. test-comparison.json and the local comparison script preserve the method/results. Approval status: awaiting user feedback.

## User feedback and finished-master volume comparison

User says either could work, with Basalt Transmission Outpost slightly preferred. Treat Outpost as the current preferred direction, not approval of a longer export. Full Ringfall one-hour MP3 measured at -17.7 LUFS integrated, 7.5 LU LRA, -4.6 dBTP. Basalt one-minute test is -17.4 LUFS, 12.6 LU LRA, -3.5 dBTP. Integrated difference is only 0.3 LU, so average levels are already close. Basalt has larger measured dynamics, but a one-minute intro/outro-heavy test and a full hour are not directly equivalent LRA samples. Recheck the longer generated Basalt export before gain matching. Copper Dusk is -11.6 LUFS, about 6.1 LU louder than the finished Ringfall file.
