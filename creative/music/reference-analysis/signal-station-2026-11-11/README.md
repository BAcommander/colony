# THE SIGNAL STATION reference — 2026-11-11

User reference: [Ambient Outpost / THE SIGNAL STATION — Dark Forest Rain Ambience, 24/7](https://www.youtube.com/watch?v=xWLPU_Ku3Kw). User's exact report: "i seem to be able to listen to this for like 10 hours no problem". This is a positive long-session listening report. It does not identify which property causes it.

The URL was a live broadcast (started 2026-11-10, Music category). A 30-minute audio excerpt was taken from the public DVR window, about 1,815 seconds behind the live edge at 10:20 UTC; decoded 1,800.01 s, SHA-256 `ca5b7d8e2566e7fa24e7d35fa4a9449fd87b8a67f41eca6f883d24541d0d67c7`. It is not the whole stream or necessarily the passage the user heard. Audio and the full interactive report stay under ignored `exports/reference-analysis/signal-station-2026-11-11-30min/`.

## Standard analyser

| Measure | SIGNAL STATION | WINTER WATCH (Oct 30) |
| --- | ---: | ---: |
| Integrated loudness | −25.7 LUFS | −22.6 LUFS |
| Loudness range | 3.8 LU | 5.0 LU |
| True peak | −5.6 dBTP | −5.7 dBTP |
| 1 s RMS p5 / p50 / p95 | −28.7 / −26.4 / −23.8 dBFS | −26.8 / −24.5 / −21.1 dBFS |
| Stereo correlation / side energy | 0.251 / 37.4% | 0.263 / 36.9% |
| Below 80 Hz | 44.8% | 33.3% |
| 80–250 Hz | 27.6% | 35.9% |
| 250 Hz–1 kHz | 24.7% | 26.7% |
| 1–4 kHz | 2.47% | 4.09% |
| 4–12 kHz | 0.42% | 0.026% |

Recurrence candidates at 608 / 402 / 615 s have sampled waveform correlations of only 0.13–0.53. No loop is confirmed; none is ruled out.

## Texture and pace comparison

[texture-pace-comparison.json](texture-pace-comparison.json), made by [scripts/compare_texture_pace.py](../../../../scripts/compare_texture_pace.py): the same 16 kHz method on eight 30-minute passages (both references, Snowline V6 02:00–32:00, and the five October published passages).

| Measure | SIGNAL STATION | WINTER WATCH | Snowline V6 | Rainline | Shoreless | Basalt | Ringfall | Spirewatch |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Noise-like share of energy | 30.6% | 28.8% | 17.3% | 4.8% | 16.3% | 9.5% | 4.5% | 14.6% |
| 2–8 kHz band relative to total | −18.5 dB | −21.5 dB | −34.4 dB | −41.9 dB | −39.2 dB | −47.4 dB | −47.4 dB | −31.2 dB |
| 2–8 kHz 1 s level spread (p5–p95) | 2.9 dB | 7.6 dB | 16.8 dB | 23.8 dB | 12.5 dB | 14.2 dB | 12.5 dB | 19.6 dB |
| Spectral flatness 500 Hz–2 kHz | 0.43 | 0.25 | 0.07 | 0.02 | 0.03 | 0.02 | 0.02 | 0.06 |
| 30 s level spread (p5–p95) | 1.9 dB | 3.1 dB | 4.0 dB | 2.1 dB | 1.4 dB | 2.5 dB | 5.1 dB | 1.2 dB |
| Mid-band events ≥6 dB above the last 10 s, per minute | 2.4 | 1.5 | 17.1 | 1.5 | 2.8 | 1.9 | 9.6 | 5.8 |
| Same, ≥10 dB | 0.16 | 0.00 | 5.25 | 0.00 | 0.00 | 0.00 | 0.77 | 0.13 |
| Pitch-profile change over 60 s (0 = identical) | 0.48 | 0.32 | 0.31 | 0.02 | 0.15 | 0.17 | 0.14 | 0.06 |
| Time the most common strongest pitch class leads | 48% | 33% | 48% | 89% | 48% | 71% | 82% | 73% |

## What the numbers support

1. **Both long-session references carry a constant noise-like bed.** About 30% of their energy is noise-like, and the upper band is present every second (2.9 dB spread here). Our published tracks are 80–95% sustained tone with an upper band 13–29 dB lower relative to the mix that comes and goes. Rainline's rain has the same flat upper-band character but sits about 23 dB lower and is intermittent.
2. **Very few moments stand out from the last ten seconds**, and almost none by 10 dB. Snowline V6 has roughly seven times as many 6 dB events and is the only passage with frequent 10 dB events. Its mid band is otherwise quiet, so radio, creaks and snow stand clear of it.
3. **Long-term level is flat** (1.9 dB over 30-second averages, 3.8 LU) and the stream is quiet at −25.7 LUFS.
4. **The pitch content is not a fixed drone.** Its profile changes more over a minute than any of our tracks, and no single pitch class leads for most of the time. The noise bed can inflate this measure, so treat it as "not static", not as a measured rate of harmonic change.

## Limits

Signal measurements only; no assistant listening. The noise/tone split is a spectral-structure allocation, not a rain stem or a fader level. "Rain" comes from the stream title, not from sound identification. Event counts depend on the chosen band (300 Hz–6 kHz), window and thresholds. One excerpt of one stream, compared against one user's report: this is a hypothesis about long-session comfort, not a demonstrated cause.

## Proposed test (not built)

Hold one accepted dry music bed fixed and compare: A as released; B with a continuous, steady broadband weather bed whose 2–8 kHz level sits about 18–22 dB below the full mix, never switching off; C the same as B with scheduled effects lowered so that nothing rises more than about 6 dB above the bed. Same playback gain, then a 30–60 minute work session. This follows the existing same-bed method in [LEARNINGS.md](../../../LEARNINGS.md).

Local work, uncommitted. No paid generation, model install or upload of reference audio.
