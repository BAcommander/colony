# 14 — Crater Rim Survey soundtrack preparation

V3 prepared 2026-10-30 after ambient-practice research and the user's listening ratings, for the confirmed November lineup. Proposed musical direction only; no V3 audio generated, evaluated or approved. V1/V2 from 2026-09-29 remain history. [Research and month pack](../../../creative/music/november-2026/README.md).

Read [the shared music workflow](../../../creative/MUSIC_WORKFLOW.md). The user runs any ElevenLabs generations manually after checking the actual displayed cost and available controls. Do not use a paid API or plugin.

## V4 listening proposal from Snowline

On 2026-11-04 the user called the Snowline musical ideas the best so far and said earlier tracks could feel repetitive and boring. The [saved Hoth brief](../../../music/hoth-reference-analysis-2026-11-01/below-the-snowline-reference-test-prompt.txt) calls for exposed passages, fuller sustained textures and occasional melodic fragments. The [approved Snowline music](../../../music/below-the-snowline-production-2026-11-01/paired-loop-v1/README.md) combines two related pieces. Both had substantial level variation after excluding their edges. The exact generation prompts and settings are unverified, so the user's preference supports testing that direction without establishing which ingredient caused it.

The Crater Rim V3 continuation asks the piece to settle back toward the same density. V4 gives the scene more room to move between sparse and full textures, with quiet stretches, staggered changes in the voices and familiar harmony returning in a different voicing or register. The landscape is morning light, a warm room and an open basin. The exterior air remains a separate mix layer.

1. Start with [Survey Room](elevenlabs-crater-room-v4.txt). For a comparison, use the [duration-free V3 review draft](../../../music/prompt-learnings-2026-11-01/review-drafts/14-crater-rim-survey-music-v4-review.txt) at the same settings and length. Aim for two minutes in the generation settings. Level-match the dry exports and listen unlabelled for a familiar swell or phrase coming back, sudden peaks, and whether the quieter passages make the fuller ones feel earned. One export per prompt is a first listen, since variation can also come from the generation.
2. If Survey Room earns a longer test, pair it with [Across the Basin](elevenlabs-crater-basin-v4.txt). Try two complementary passages of roughly five minutes, subject to the available settings. Keep the first closer and warmer and the second wider and more exposed. Record the actual prompt, settings and source files. Choose overlap points by listening to the exports, then audition both joins and three repeats.
3. Compare the preferred dry arrangement with the same music plus distant basin air. Follow the work-session listening gate before extending the mix. The eventual repeat length comes from the arrangement and joins.

These V4 prompts are ungenerated review candidates. The V3 workflow below remains the comparison reference.

## V3 workflow

1. Use elevenlabs-prompt-v3.txt in the Music description field, not lyrics. Choose instrumental output and aim for 120 seconds/two variants if supported.
2. Listen at comfortable matched volume and choose a test; revise the specific defect if neither works.
3. Use the selected own test as an audio reference, if the current interface offers it, with elevenlabs-long-version-v3.txt; aim for about eight minutes/one variant. A reference guides feel and palette, not exact continuation.
4. Save original exports and fill generation-record.json with actual settings, cost shown, filenames, durations and feedback.
5. Inspect the supplied export locally for duration, fades, levels and candidate loop points; make a short join audition. Choose overlap from the actual piece rather than assuming Ringfall's 15 seconds fits.
6. Assemble a long version only after listening approval and a chosen duration. Large repeats live under ignored exports/ with reproduction records; they are not backed up merely because prompts are in Git.

## Current V3 listening check

Open morning scale without a returning two-note question, a celebratory lift or exaggerated stereo motion. Compare the same dry musical bed with and without the proposed ambience at matched loudness. Source viewpoint and SFX balance remain proposals.

### Previous V2 question, retained for history

Does the harmony gently open without a heroic build? Are sparse musical gestures irregular and soft, with enough midrange activity to avoid a static drone?

Also check for unwanted vocals, percussion, abrupt level changes, uncomfortable sub-bass, thin midrange and poor mono translation. Keep scene sound effects separate from the music pass. Do not impose a fixed named key or a compulsory drone note.

The publication copy is a draft. Add accurate soundtrack wording and runtime once known; do not claim human composition or no AI music for generated audio.

## Prompt versions

Current: `elevenlabs-prompt-v3.txt` and `elevenlabs-long-version-v3.txt` (2026-10-30), with separate `ambience-prompt-v3.txt`. Read the November research and V3 workflow. V2 files from 2026-09-29 are preserved untested history. `elevenlabs-prompt-v1.txt` and `elevenlabs-long-version.txt` are preserved history. None of these scene prompt versions has been generated or heard.

Notes kept out of the prompt text on purpose:

- Attach a short excerpt of your selected own dry test as reference, following the actual UI limit, before running the long prompt. A reference guides feel and palette, not exact continuation.
- The long prompt says "about eight minutes". If the actual supported/chosen duration differs, edit that number before pasting.
- A prompt cannot guarantee a seamless loop. Loop points, crossfades and seamlessness are decided locally after inspecting the export.
- Paste into the prompt/song-description field, not lyrics. If you edit style chips, keep exclusions in the negative row.
