# Ambient Colony music workflow

Updated 2026-09-26. Current authority for music work; complements the visual animation workflow.

## Current state

Ringfall: user generated music manually in ElevenLabs, selected a direction after short tests, supplied a longer export, and accepted the short crossfade audition with "yeah i couldn't relaly hear any transitions". A one-hour MP3 was made and fully decode-verified. Longer listening evaluation remains pending; do not claim final musical approval or that it is a completed video.

Basalt: first two one-minute Music v2.5 tests received and measured. Basalt Transmission Outpost is midrange-dominant; Copper Dusk Transmission is sub-bass-dominant. User listening preference and approval are pending. See final/02-basalt-transmission/music/test-01/README.md. Do not infer a winner from signal measurements alone.

User uses existing ElevenLabs credits. Quoted rate: 900 credits/minute; verify the UI price before each generation. This workflow does not authorize the assistant to spend credits or upload reference audio automatically. User runs paid generations manually; local analysis and assembly incur no ElevenLabs credits.

## Lessons established by the Ringfall session

1. First prompt overconstrained movement: persistent E drone, subdued treble, no prominent melody and numerous exclusions. User preferred Night Watch over Dusk, describing Dusk as more droney, and rated the overall direction only about halfway to the reference.
2. Signal comparison supported revision. Initial Night Watch had about 80% of measured stereo spectral energy below 80 Hz; Dusk concentrated about 91% at 80–250 Hz. A sampled DEAD WATER reference passage had about 44% at 250–1000 Hz. Both tests had much steadier levels and more similar stereo channels. These were sample measurements, not perceptual loudness percentages or instrument identifications.
3. Revised prompt restored independent harmonic voices, audible midrange, gentle swells, occasional distant two/three-note phrases, and gradual voicing changes. It removed the fixed E requirement. User said both revised one-minute tests were decent and could work. This supports the direction; it does not prove each wording change caused the improvement.
4. Use one minute x two variants to establish a sound. At the user's quoted rate this is 1,800 credits total. Two minutes helps assess development, but isn't essential for initial palette tests.
5. Once a test is liked, the user found Use as reference easier than section editing for creating a longer new piece. Audio reference guides style; it does not preserve or extend the exact original minute. Keep the preferred test downloaded.
6. Prompt goes in Song description/Prompt, not Custom lyrics. Remove Markdown quote markers. Explicitly say instrumental only. If editing style chips, keep exclusions in the negative row: comma splitting turned "new lead instrument" and "final cadence or fade-out" into positive tags during an attempted edit.
7. Request about five minutes and one variant after the palette works. Inspect the actual export: the Ringfall attachment had 360 seconds of decoded audio inside a 364.4-second video. Do not infer duration from the requested setting.
8. Prompted loopability is not an editing guarantee. The longer Ringfall file still faded in/out. A 0:20–5:30 excerpt with 15-second equal-power overlaps gave a 15-minute three-cycle preview. User could not readily hear the transitions. These cut points and fade settings are specific to that track, not universal defaults.
9. One-hour Ringfall delivery: exact decoded 3600 seconds, stereo 48 kHz MP3 at 192 kb/s; gain 0.7, 10-second opening fade and 20-second closing fade; 15-second sine/cosine crossfades. Verified decoded sample peak about -4.56 dBFS. User approval covers the transition audition; extended listening remains pending.
10. Match listening levels when comparing; louder can bias preference. Keep atmosphere, foreground activity, tonal weight, and long-form comfort as separate judgments. Avoid promises of a percentage improvement.

## Evidence and analysis discipline

- No reliable assistant listening tool was available during these sessions. Distinguish signal measurements, user listening feedback, and creative suggestions.
- Do not claim instrument identities, water/wind sources, reverb duration, BPM, key mode or absence of vocals solely from spectral analysis.
- Persistent frequency peaks may be overtones, not chord notes. E-related peaks in DEAD WATER and C-related peaks in PYRAMID do not establish major/minor keys.
- For wide stereo sources, average left/right spectral power rather than downmixing before comparing bass balance. The initial DEAD WATER report used mono downmixes; later comparisons used stereo power and are not numerically interchangeable.
- Spectrum-derived recurrence is a candidate; validate with aligned waveform excerpts across several positions. Do not confuse similarity scores with a percentage of identical composition.
- Full-file low stereo correlation does not prove a particular reverb, good mono compatibility or desirable width. Preserve a stable bass foundation and audition mono on generated work.
- External downloaded references stay local; preserve filenames/hashes and analysis, not copyrighted MP3s in Git. Create original descriptive prompts. Use a selected user-generated test as the ElevenLabs audio reference for long-form generation.

## Repeatable sequence

1. Read scene description and last accepted feedback.
2. Analyse reference duration, spectrum, dynamics and recurrence; label limits.
3. Write a scene-specific one-minute prompt emphasizing positive musical behavior before a short exclusion list.
4. User generates two short variants, chooses one, and reports what works or distracts.
5. Revise only the unresolved characteristics. Avoid continuing to spend credits once the direction works.
6. User selects Use as reference on their chosen test, requests about five minutes/one variant, and supplies the export.
7. Inspect actual duration, fades, levels and candidate loop points. Create a join audition and three-repeat preview.
8. After a successful listening check, make the requested one-hour audio with only one opening/closing fade. Decode-check duration and peak headroom. Preserve source exports and version revisions.
9. Record prompt, model/settings shown, filenames, checks, exact feedback, and approval scope. Keep recording status distinct from committed/pushed status.

## Saved evidence

creative/music/ringfall/ contains the historical brief, revised prompt, measurements, loop checks and reproduction scripts migrated from G:/AI/youtube/ringfall-audio-analysis. Historical scripts include original machine-local paths; edit paths deliberately before reuse. Raw feature caches and large loudness logs were omitted from the migration; compact numeric summaries and sources are retained. Basalt analysis and prompt live in final/02-basalt-transmission/music/.

Official prompting guidance checked 2026-09-26: https://elevenlabs.io/docs/overview/capabilities/music/best-practices . Explicit musical descriptors and instrumental intent are supported; reference generation guides feel and palette, not exact continuation. Follow the actual UI for duration, reference limits and pricing.
