# Ambient Colony music workflow

Updated 2026-09-26. Current authority for music work; complements the visual animation workflow.

## Current state

Ringfall: user generated music manually in ElevenLabs, selected a direction after short tests, supplied a longer export, and accepted the short crossfade audition with "yeah i couldn't relaly hear any transitions". A one-hour MP3 was made and fully decode-verified. Longer listening evaluation remains pending; do not claim final musical approval or that it is a completed video.

Basalt: user slightly preferred Basalt Transmission Outpost, then supplied a ten-minute export titled Copper Dusk Transmission. User could not hear the prepared join and requested two hours for playlist duration variety. Two-hour audio delivered and decode/loudness verified. User listened for eight minutes and reported it was totally fine; short crossfade also accepted. Full two-hour audition has not been claimed. See final/02-basalt-transmission/music/two-hour-delivery.md. Do not infer reference selection from the generated filename.

User uses existing ElevenLabs credits. Quoted rate: 900 credits/minute; verify the UI price before each generation. This workflow does not authorize the assistant to spend credits or upload reference audio automatically. User runs paid generations manually; local analysis and assembly incur no ElevenLabs credits.

Channel benchmark (2026-09-29): the user wants Ambient Colony to compete with the YouTube channel Ambient Outpost, which the user puts at about 160k subscribers. Treat it as a quality and long-form listening-comfort benchmark, not a copying target; prompts, art and titles stay original.

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
3. Write a scene-specific one-minute prompt following the prompt writing rules below: length and mode first, a distinct genre and production anchor, sequential positive musical description, one short generic exclusion sentence last.
4. User generates two short variants, chooses one, and reports what works or distracts.
5. Revise only the unresolved characteristics. Avoid continuing to spend credits once the direction works.
6. User selects Use as reference on their chosen test, requests about five minutes/one variant, and supplies the export.
7. Inspect actual duration, fades, levels and candidate loop points. Create a join audition and three-repeat preview.
8. After a successful listening check, make the requested one-hour audio with only one opening/closing fade. Decode-check duration and peak headroom. Preserve source exports and version revisions.
9. Record prompt, model/settings shown, filenames, checks, exact feedback, and approval scope. Keep recording status distinct from committed/pushed status.

## Prompt writing rules (v2, 2026-09-29)

Established by a full review of the 04-14 v1 prompts against the official ElevenLabs Music best-practices page and the compose API reference (both checked 2026-09-29), the Ringfall v1-to-v2 prompt experience and the Basalt long prompt that produced the accepted ten-minute export. The v2 prompts are untested: no generation has compared v1 with v2. These rules are documented reasoning until a listening test confirms them.

Structure, in this order:

1. Length and mode first: "Instrumental only, 60 seconds." or "Instrumental only, about five minutes." The docs recommend stating length plainly. The API accepts 3 seconds to 10 minutes per prompt generation; the UI decides what it offers.
2. One sentence of genre and production anchor in studio vocabulary: pad type, reverb type, tape or analog character, noise bed. The docs say anything left open gets the most average answer, so each scene names a distinct anchor instead of "cinematic electronic ambient" for all eleven.
3. One sentence of scene mood. Further scene narrative is weak steering; keep it short.
4. Positive musical description as sequential narration: "start with ... already in place", "around 1:00 bring in", "between 1:30 and 3:30", "after 3:30 hold". Timing cues are supported by the docs. Name pauses and rests explicitly.
5. One short mix-and-ending paragraph: midrange clear at low volume, bass centred and modest, treble smooth, level even, end open with no cadence.
6. One generic exclusion sentence last, about eight items: vocals, drums, percussion, arpeggios, sound effects, risers, climaxes, plus at most one scene-specific risk such as bells or a sub-heavy drone. Never list literal effect nouns (horns, rail clatter, sonar pings, ice cracks, dripping). "Sound effects" covers them and keeps negative nouns from leaking into the output or the style chips.

Rules:

- Short prompts about 1000-1250 characters, long prompts about 900-1100. The v1 short prompts were 1750-2080 and the v1 long prompts 2090-2600. The accepted Ringfall prompt was about 1500 and the working Basalt long prompt 879. The docs state that length and detail do not correlate with quality.
- The long prompt does not repeat the short prompt. The attached reference carries the palette. The long prompt names the anchor, the mood, a scene-specific arc with timings and the exclusions.
- No workflow notes inside the prompt. "If the interface supports it", "use my selected test", "local editing will determine loop points", "seamlessness will be checked after export" and "do not force a mathematically seamless loop" are instructions for people and belong in the package README.
- No explanatory sentences aimed at a reader, such as "the railway informs the feeling, not literal sound effects". They add nothing the model can play and reintroduce effect nouns.
- Do not ask for a timbre and then forbid its family. The v1 Empty Junction prompt asked for a brass-like tone and forbade horns. Do not write ambiguous exclusions such as "instrument sound effects".
- Differentiate scenes deliberately: register, harmonic leaning (major-leaning for daylight scenes such as Deepwell and Crater Rim, suspended and open for night scenes), reverb character, rate of change and one accent timbre per scene. Eleven near-identical templates produce eleven near-identical tracks.
- Keep the Ringfall lessons: independent voices, audible midrange, restrained centred bass, no compulsory drone note. A named key is supported by the docs and is not the same as a fixed drone; test it on one scene before adopting it.
- Keep "Instrumental only" in the text even when the UI has an instrumental switch.
- The long-piece duration is the user's choice. Five minutes is the written default; Basalt used ten. Edit the number in the prompt to match the UI setting.

To confirm with the first v2 generation: whether timing cues are followed in free-time material, whether "sound effects" alone keeps out literal effects, and whether the shorter prompt reduces the two-variant tonal extremes seen in the Basalt tests.

## Saved evidence

creative/music/ringfall/ contains the historical brief, revised prompt, measurements, loop checks and reproduction scripts migrated from G:/AI/youtube/ringfall-audio-analysis. Historical scripts include original machine-local paths; edit paths deliberately before reuse. Raw feature caches and large loudness logs were omitted from the migration; compact numeric summaries and sources are retained. Basalt analysis and prompt live in final/02-basalt-transmission/music/.

Official prompting guidance checked 2026-09-26: https://elevenlabs.io/docs/overview/capabilities/music/best-practices . Explicit musical descriptors and instrumental intent are supported; reference generation guides feel and palette, not exact continuation. Follow the actual UI for duration, reference limits and pricing.

## Prepared scenes 04-07, 2026-09-28

Each final package now has `music/elevenlabs-prompt-v1.txt`, `elevenlabs-long-version.txt`, `README.md` and `generation-record.json`. No tests generated or credits spent. Floodplain uses flowing warm midrange layers; Saltline uses sparse distant musical replies; Cable Station uses suspended airy voices; Icebound balances warm lower mids with soft cold upper textures. These are proposed musical palettes, not analyzed or approved recordings. Preserve independent harmonic movement and avoid the overly fixed, sub-heavy drone of early Ringfall trials. Official Music best-practices checked again on 2026-09-28; follow the actual UI for available settings and cost.

## Prepared scenes 08-10, 2026-09-28

Final packages contain one-minute and longer ElevenLabs prompts, listening criteria and blank generation records. Rainline: warm interweaving voices and gentle musical replies, no radio or rain effects. Offshore: broad unequal harmonic swells and open depth, no periodic pumping or literal surf. Nightward: close warmth and distant suspended voices with soft metallic colour, no telemetry beeps. These are proposals; no audio generated or credits spent. Use the same short-test, selected-reference and local join-review sequence.

Naming update: catalog 09 is The Shoreless Colony (formerly Offshore Night Office); 10 is Farpoint Station (formerly Nightward Station). Current music prompts use the selected names; palettes and manual testing workflow are unchanged. Existing directory slugs remain stable.


## Prepared scenes 11-14, 2026-09-29

Release folders have scene-specific short and long music prompts, listening checks and blank generation records. Empty Junction: patient irregular replies between warm close and distant soft voices; no train rhythms. Deepwell: overlapping independent voices and reflective soft upper texture; no water effects. Below the Snowline: intimate warmth against cool sustained distance; no shrill crystalline notes. Crater Rim: open suspended harmony and sparse musical questions; no heroic build. No audio generated or credits spent.

## v2 prompts for scenes 04-14, 2026-09-29

Each package music folder now holds elevenlabs-prompt-v2.txt and elevenlabs-long-version-v2.txt as the current prompts, written to the rules above. The v1 files are preserved unchanged as history. READMEs point to v2 and hold the workflow notes removed from the prompt text. No audio generated, no credits spent, no user listening feedback on v2; generation records remain blank.

## Local soundtrack deliveries, reconciled 2026-09-29

Basalt revision v2 (2026-09-26): YouTube displayed an audio Content ID claim at 30:54–31:05. Local waveform tracing mapped it to generated source 4:27–4:38. At user request, source 4:17–4:48 was removed before repetition and a retained-audio 12-second crossfade added. Versioned two-hour MP3, original-picture-stream MP4, and two short auditions are saved in exports/02-basalt-transmission. See final/02-basalt-transmission/music/revision-v2/. New-cut listening feedback and revised YouTube checks pending. Originals preserved; no claim-resolution guarantee and no YouTube action taken.


Glacier update (2026-09-27): both one-minute tests described as usable; user preferred Sanctuary Under Blue Dusk direction and supplied Amber Arch Sanctuary ten-minute export. At user request, four-hour MP3 completed with source 0:32-9:52, 15-second equal-power joins, -5 dB gain and single opening/closing fades. Full decode verified. See final/03-glacier-sanctuary/music/long-source-v1/four-hour-delivery.md. Audio ready for video assembly; no explicit join verdict or full-length listening approval claimed.

Glacier Content ID update (2026-09-27): user reports two SME claims, on behalf of MT Recordings and Filtr, blocking some territories. First claim covers long ranges exceeding a full repeat cycle; small-cut remedy is not supported. See final/03-glacier-sanctuary/music/content-id-2026-09-27/. Support draft prepared, not sent; claim validity unknown. Check complete candidate generations privately/unlisted before long assembly going forward, while recognizing later claims remain possible. Technical audio validation is not rights clearance.


Glacier replacement delivered: user approved Amber Refuge join with "loop sounds fine" after private source upload showed No notices. Versioned four-hour MP3 and original-picture-stream MP4 completed. Source 0:29-8:31, 15-second equal-power overlap, -4.7 dB gain. See final/03-glacier-sanctuary/music/replacement-amber-refuge/delivery-v2.md. Full replacement YouTube checks pending; original claimed files preserved.
