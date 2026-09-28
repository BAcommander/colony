# Ambient Colony music workflow

Updated 2026-09-26. Current authority for music work; complements the visual animation workflow.

## Current state

Ringfall: user generated music manually in ElevenLabs, selected a direction after short tests, supplied a longer export, and accepted the short crossfade audition with "yeah i couldn't relaly hear any transitions". A one-hour MP3 was made and fully decode-verified. Longer listening evaluation remains pending; do not claim final musical approval or that it is a completed video.

Basalt: user slightly preferred Basalt Transmission Outpost, then supplied a ten-minute export titled Copper Dusk Transmission. User could not hear the prepared join and requested two hours for playlist duration variety. Two-hour audio delivered and decode/loudness verified. User listened for eight minutes and reported it was totally fine; short crossfade also accepted. Full two-hour audition has not been claimed. See final/02-basalt-transmission/music/two-hour-delivery.md. Do not infer reference selection from the generated filename.

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

## Prepared scenes 04-07, 2026-09-28

Each final package now has `music/elevenlabs-prompt-v1.txt`, `elevenlabs-long-version.txt`, `README.md` and `generation-record.json`. No tests generated or credits spent. Floodplain uses flowing warm midrange layers; Saltline uses sparse distant musical replies; Cable Station uses suspended airy voices; Icebound balances warm lower mids with soft cold upper textures. These are proposed musical palettes, not analyzed or approved recordings. Preserve independent harmonic movement and avoid the overly fixed, sub-heavy drone of early Ringfall trials. Official Music best-practices checked again on 2026-09-28; follow the actual UI for available settings and cost.

## Prepared scenes 08-10, 2026-09-28

Final packages contain one-minute and longer ElevenLabs prompts, listening criteria and blank generation records. Rainline: warm interweaving voices and gentle musical replies, no radio or rain effects. Offshore: broad unequal harmonic swells and open depth, no periodic pumping or literal surf. Nightward: close warmth and distant suspended voices with soft metallic colour, no telemetry beeps. These are proposals; no audio generated or credits spent. Use the same short-test, selected-reference and local join-review sequence.

Naming update: catalog 09 is The Shoreless Colony (formerly Offshore Night Office); 10 is Farpoint Station (formerly Nightward Station). Current music prompts use the selected names; palettes and manual testing workflow are unchanged. Existing directory slugs remain stable.
