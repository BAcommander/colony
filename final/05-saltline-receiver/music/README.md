# 05 soundtrack preparation

Status (2026-10-03): user approved the Red World Basin transition and requested the two-hour version. The two-hour MP3 is delivered and fully decode-verified; see long-source-v1/two-hour-delivery-v1.md and generation-record.json. It preserves the approved twelve-second crossfade and fixed gain. The two-hour Colony video is delivered and technically verified; full two-hour listening and combined review remain pending. Exact generation settings/prompt were not observed; no assistant listening claim. V1/v2/v3 prompts and original media are preserved.

## Files and manual generation

1. Paste `elevenlabs-prompt-v2.txt` into the Music prompt/song-description field, not lyrics. Use instrumental mode if available. Set 60 seconds and two variants if the interface offers those controls. The user runs generations manually with their own existing credits; inspect the actual displayed cost first. No API or paid generation was run here.
2. Listen at matched comfortable volume and choose one test. Stop and adjust only the unresolved characteristic if both miss. Do not blindly generate more variants.
3. For the chosen user-generated test, use the available audio-reference control and `elevenlabs-long-version-v3-seven-minutes.txt`. Aim for roughly seven minutes and one variant if supported; follow the actual interface and reference limits. A reference guides feel and palette, not exact continuation.
4. Keep the downloaded originals and record actual settings, filenames, duration, selected variant and feedback in generation-record.json. The chosen short and supplied long exports are recorded; unobserved settings and unfinished stages remain null.
5. Supply the export for local duration/fade/loudness inspection, candidate loop-point selection and a short join audition. Choose crossfade length from this track; Ringfall's 15 seconds is not a universal default. A prompt cannot guarantee a seamless loop.
6. Only after listening approval assemble the requested long duration locally. The user selected a two-hour target. Long exports belong under ignored exports/, with hashes and reproduction instructions in the repo; do not claim those exports are backed up by Git.

## Scene-specific listening check

Does the reply sound musical rather than like a notification? Is the low-mid warmth present without boomy bass? Does the track have more harmonic life than a static desert drone?

Also check for unwanted vocal-like sounds, percussive transients, abrupt level changes, repetitive hooks, uncomfortable sub-bass, thin midrange and poor mono translation. These are listening questions, not claims about ungenerated audio.

## Shared decisions

Use the learned independent-voice and audible-midrange direction from creative/MUSIC_WORKFLOW.md. Do not impose a named fixed key, unverified reference BPM or compulsory drone note. Keep literal scene sound effects separate from this music pass. Long-form comfort matters more than elaborate instrumentation. Put exclusions only in a negative field if editing style chips; do not let comma splitting turn them into positive tags.

The adjacent description/tags are narrative publication drafts. Add accurate soundtrack wording and duration only after the audio and final upload are known. Do not claim human-composed or no AI music for an ElevenLabs generation.

## Official prompting source

[ElevenLabs Music best practices](https://elevenlabs.io/docs/overview/capabilities/music/best-practices), checked 2026-09-28: specify musical intent and instrumental-only output; audio references guide feel and palette. The scene palettes and workflow choices above are our own creative brief and accumulated user feedback. No quoted price or UI limit is assumed current.

## Prompt versions

Current short prompt: `elevenlabs-prompt-v2.txt`; current long prompt: `elevenlabs-long-version-v3-seven-minutes.txt` (2026-10-03), written to the prompt writing rules in creative/MUSIC_WORKFLOW.md. V1 prompts and `elevenlabs-long-version-v2.txt` are preserved history. The supplied short test is user-selected; its actual prompt was not observed. The longer export has been supplied; its exact prompt/settings were not observed.

Notes kept out of the prompt text on purpose:

- Attach your chosen one-minute test as the audio reference in the UI before running the long prompt. A reference guides feel and palette, not exact continuation.
- The current long prompt says "about seven minutes", matching the requested generation target.
- A prompt cannot guarantee a seamless loop. Loop points, crossfades and seamlessness are decided locally after inspecting the export.
- Paste into the prompt/song-description field, not lyrics. If you edit style chips, keep exclusions in the negative row.

## Current seven-minute generation

Use the selected Red Basin Listening Station test as the reference in ElevenLabs and the v3 seven-minute prompt as the musical brief. Generate one longer candidate using the duration control offered by the interface; check its displayed cost before running. The reference guides the musical direction, not an exact continuation. Do not paste these workflow notes into the prompt.

The prompt keeps the opening and ending textures compatible but cannot guarantee a seamless join. Supply the resulting export for local analysis, loop-point selection and a short crossfade audition. The transition is now approved and the two-hour soundtrack is delivered. The two-hour combined video is now delivered; see ../assembly-v1/. Do not treat seven minutes as the exact decoded duration or decide the overlap before hearing/testing the result.
