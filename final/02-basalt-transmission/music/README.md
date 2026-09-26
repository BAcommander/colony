# Basalt Transmission: soundtrack brief and reference analysis

Prepared 2026-09-26. Status: two one-minute tests received; comparison in test-01/README.md. User preference and approval pending; no final Basalt soundtrack yet.

## Reference and limits

User supplied THE GREAT PYRAMID OUTPOST MP3, YouTube ID G0-ZTBd6jyI. Full filename and SHA-256 are in measurements.json. All processing was local; source audio has not been uploaded or added to the repository. Analysis uses NumPy and FFmpeg. No reliable assistant audition was available: this report does not claim instrument identification or a subjective listening review.

## Measured findings

- Four-hour stereo MP3, 44.1 kHz, approximately 164 kb/s average (filename's 128k is not the detected average).
- Full-file integrated loudness -16.2 LUFS; loudness range 5.3 LU; reconstructed true peak -1.1 dBTP. DEAD WATER was -10.0 LUFS/4.9 LU, so the new reference is about 6.2 LU quieter in the measured masters, with comparable loudness variation. Match listening levels before comparing mood or quality.
- One-second RMS 5th/50th/95th percentiles approximately -20.43/-18.24/-15.38 dBFS. Distinct from loudness range and LUFS.
- First roughly 20 seconds are very quiet; level rises markedly from about 0:20 to 0:30. End fades sharply through the last roughly 10–15 seconds. Whole-file repetition would include these fades.
- Strong aligned waveform recurrence at 3568.8645 seconds (59:28.8645), with correlation 0.981–0.989 across four 20-second windows at 1:00, 5:00, 15:00 and 30:00. This supports repeated recorded material on an approximately one-hour scale. These offsets are not proven edit points; exact crossfade construction and a fully uniform loop length remain unknown.
- Spectral recurrence also has nearby peaks around 59:33 and 1:59:05, but selected waveform checks there reach only about 0.40–0.42. Do not report these as exact audio loop lengths. A smaller peak around 5:27 is unverified and may be a component or structural recurrence.
- Full-file stereo correlation at 8192 Hz is approximately -0.187. Strong channel differences support checking spatial presentation; this is not evidence that phase cancellation is desirable or that mono compatibility is good.

Five one-minute excerpts beginning at 1:00, 5:00, 15:00, 30:00 and 50:00 were analysed at 22.05 kHz by averaging left/right spectral power:

| Frequency band | Range of energy shares across samples |
|---|---:|
| Below 80 Hz | 14–19% |
| 80–250 Hz | 30–45% |
| 250–1000 Hz | 35–54% |
| 1–4 kHz | 1–3% |
| 4–11.025 kHz | About 0–0.01% |

These are signal energy shares within the analysis bandwidth, not perceived loudness fractions or full-file averages. The important balance is bass plus substantial midrange, with strongly subdued treble. This is not evidence for an almost pure sub-bass generation.

Persistent peaks near 65.27, 130.55 and 195.82 Hz are consistent with harmonics of a C-centered foundation; a recurring peak near 98.25 Hz is near G. Other prominent peaks change between excerpts (roughly 264, 293, 315, 349, 392 and 523 Hz among others). This supports sustained tonal material with variation above it, but neither a chord progression nor a major/minor key can be established from these peaks alone. No reliable BPM has been established.

## Translation into a Basalt soundtrack

Measured target: rounded low foundation, clearly present midrange layers, restrained treble, level movement, and spacious presentation. Prompt implementation: layered synthesizer voices, gentle swells, slowly changing voicings, distant sparse phrases and diffuse reverb. These are creative production choices, not verified source instruments/effects.

Scene-specific interpretation: an inhabited relay station in an empty landscape beneath a copper sky. Patient solitude, a little melancholy and a trace of interior warmth. A faint dry wind-like texture is proposed for the scene; it is not an identified sound in the supplied reference. Avoid literal radio beeps, dialogue or alarms, which could become distracting through repetition. The track title's pyramid does not imply Egyptian instruments, chanting or exotic scales.

Start with elevenlabs-prompt-v1.txt in the Prompt/song-description field. Request one minute, two variants, instrumental only. At the user's quoted 900 credits/minute that is 1,800 credits; confirm the UI. No fixed C requirement in this first prompt: last session showed that insisting on a named drone could overconstrain the result. Beatless is the intended creative direction, not a measured proof of absent rhythm in the original.

After selecting a test, use that user-generated track as the reference and elevenlabs-long-version.txt for a five-minute, one-variant generation. It guides a new composition rather than extending the exact minute. Inspect actual exported duration and fades. Create an editorial crossfade preview before making an hour-long repeat.

## Reproduction and saved files

- analyze_reference.py: parameterized full-file measurement, recurrence candidates, sampled waveform matching, spectra and loudness. Requires Python/NumPy and FFmpeg; accepts source and output directory, plus --ffmpeg.
- measurements.json: source identity and whole-file statistics.
- waveform-matches.json: candidate matches, including unsuccessful candidates.
- sampled-spectrum.json: five excerpt spectra and peaks.
- loudness.txt: full-file EBU R128 summary.
- elevenlabs-prompt-v1.txt and elevenlabs-long-version.txt: exact proposed prompts.

For accumulated decisions and Ringfall feedback see creative/MUSIC_WORKFLOW.md. Numerical verification is not user listening approval. Documentation can be committed without committing the downloaded reference or repeated listening masters.

Source for current ElevenLabs prompting behavior: https://elevenlabs.io/docs/overview/capabilities/music/best-practices (checked 2026-09-26).
