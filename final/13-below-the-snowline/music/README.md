# 13 — Below the Snowline soundtrack preparation

V3 prepared 2026-10-30 after ambient-practice research and the user's listening ratings, for the confirmed November lineup. Proposed musical direction only; no V3 audio generated, evaluated or approved. V1/V2 from 2026-09-29 remain history. [Research and month pack](../../../creative/music/november-2026/README.md).

Read [the shared music workflow](../../../creative/MUSIC_WORKFLOW.md). The user runs any ElevenLabs generations manually after checking the actual displayed cost and available controls. Do not use a paid API or plugin.

1. Use elevenlabs-prompt-v3.txt in the Music description field, not lyrics. Choose instrumental output and aim for 120 seconds/two variants if supported.
2. Listen at comfortable matched volume and choose a test; revise the specific defect if neither works.
3. Use the selected own test as an audio reference, if the current interface offers it, with elevenlabs-long-version-v3.txt; aim for about eight minutes/one variant. A reference guides feel and palette, not exact continuation.
4. Save original exports and fill generation-record.json with actual settings, cost shown, filenames, durations and feedback.
5. Inspect the supplied export locally for duration, fades, levels and candidate loop points; make a short join audition. Choose overlap from the actual piece rather than assuming Ringfall's 15 seconds fits.
6. Assemble a long version only after listening approval and a chosen duration. Large repeats live under ignored exports/ with reproduction records; they are not backed up merely because prompts are in Git.

## Current V3 listening check

Warm shelter and deep distance without shrill cold timbres, a vocal-like lead or threatening sub-bass. Compare the same dry musical bed with and without the proposed ambience at matched loudness. Source viewpoint and SFX balance remain proposals.

### Previous V2 question, retained for history

Does the room feel warm while the musical distance feels cool and immense? Check for shrill icy timbres, vocal-like pads and excessively ominous bass.

Also check for unwanted vocals, percussion, abrupt level changes, uncomfortable sub-bass, thin midrange and poor mono translation. Keep scene sound effects separate from the music pass. Do not impose a fixed named key or a compulsory drone note.

The publication copy is a draft. Add accurate soundtrack wording and runtime once known; do not claim human composition or no AI music for generated audio.

## Prompt versions

Current: `elevenlabs-prompt-v3.txt` and `elevenlabs-long-version-v3.txt` (2026-10-30), with separate `ambience-prompt-v3.txt`. Read the November research and V3 workflow. V2 files from 2026-09-29 are preserved untested history. `elevenlabs-prompt-v1.txt` and `elevenlabs-long-version.txt` are preserved history. None of these scene prompt versions has been generated or heard.

Notes kept out of the prompt text on purpose:

- Attach a short excerpt of your selected own dry test as reference, following the actual UI limit, before running the long prompt. A reference guides feel and palette, not exact continuation.
- The long prompt says "about eight minutes". If the actual supported/chosen duration differs, edit that number before pasting.
- A prompt cannot guarantee a seamless loop. Loop points, crossfades and seamlessness are decided locally after inspecting the export.
- Paste into the prompt/song-description field, not lyrics. If you edit style chips, keep exclusions in the negative row.
