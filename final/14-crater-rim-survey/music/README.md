# 14 — Crater Rim Survey soundtrack preparation

Prepared 2026-09-29 as v1 and rewritten the same day as v2; proposed musical direction only. No audio generated, evaluated or approved. No credits spent by the assistant.

Read [the shared music workflow](../../../creative/MUSIC_WORKFLOW.md). The user runs any ElevenLabs generations manually after checking the actual displayed cost and available controls. Do not use a paid API or plugin.

1. Use elevenlabs-prompt-v2.txt in the Music description field, not lyrics. Choose instrumental output and aim for 60 seconds/two variants if supported.
2. Listen at comfortable matched volume and choose a test; revise the specific defect if neither works.
3. Use the selected own test as an audio reference, if the current interface offers it, with elevenlabs-long-version-v2.txt; aim for about five minutes/one variant. A reference guides feel and palette, not exact continuation.
4. Save original exports and fill generation-record.json with actual settings, cost shown, filenames, durations and feedback.
5. Inspect the supplied export locally for duration, fades, levels and candidate loop points; make a short join audition. Choose overlap from the actual piece rather than assuming Ringfall's 15 seconds fits.
6. Assemble a long version only after listening approval and a chosen duration. Large repeats live under ignored exports/ with reproduction records; they are not backed up merely because prompts are in Git.

## Scene-specific listening check

Does the harmony gently open without a heroic build? Are sparse musical gestures irregular and soft, with enough midrange activity to avoid a static drone?

Also check for unwanted vocals, percussion, abrupt level changes, uncomfortable sub-bass, thin midrange and poor mono translation. Keep scene sound effects separate from the music pass. Do not impose a fixed named key or a compulsory drone note.

The publication copy is a draft. Add accurate soundtrack wording and runtime once known; do not claim human composition or no AI music for generated audio.

## Prompt versions

Current: `elevenlabs-prompt-v2.txt` and `elevenlabs-long-version-v2.txt` (2026-09-29), written to the prompt writing rules in creative/MUSIC_WORKFLOW.md. `elevenlabs-prompt-v1.txt` and `elevenlabs-long-version.txt` are preserved history. Neither version has been generated or heard.

Notes kept out of the prompt text on purpose:

- Attach your chosen one-minute test as the audio reference in the UI before running the long prompt. A reference guides feel and palette, not exact continuation.
- The long prompt says "about five minutes". If you choose ten minutes, edit that number before pasting.
- A prompt cannot guarantee a seamless loop. Loop points, crossfades and seamlessness are decided locally after inspecting the export.
- Paste into the prompt/song-description field, not lyrics. If you edit style chips, keep exclusions in the negative row.
