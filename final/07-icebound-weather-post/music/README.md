# 07 soundtrack preparation

Status 2026-10-04: accepted transition extended into a verified one-hour soundtrack, now assembled with the latest v3 animation in the [one-hour 4K Colony video](../assembly-v1/README.md). Original source and auditions preserved. Full-hour listening and combined review remain pending; no assistant listening claim.

## Files and manual generation

1. Paste `elevenlabs-prompt-v3.txt` into the Music prompt/song-description field, not lyrics. Use instrumental mode if available. Set 60 seconds and two variants if the interface offers those controls. The user runs generations manually with their own existing credits; inspect the actual displayed cost first. No API or paid generation was run here.
2. Listen at matched comfortable volume and choose one test. Stop and adjust only the unresolved characteristic if both miss. Do not blindly generate more variants.
3. Use Colony Winter Night as the reference, enable the instrumental-only setting and paste elevenlabs-long-version-v3.txt into the prompt field. Request seven minutes and one version. A reference guides feel and palette, not exact continuation. Review the new export for unwanted voices before looping.
4. Keep the downloaded originals and record actual settings, filenames, duration, selected variant and feedback in generation-record.json. The record contains all three supplied test paths and hashes, rejected v2 feedback and the selected v3 direction; unknown settings remain null.
5. Supply the export for local duration/fade/loudness inspection, candidate loop-point selection and a short join audition. Choose crossfade length from this track; Ringfall's 15 seconds is not a universal default. A prompt cannot guarantee a seamless loop.
6. Only after listening approval assemble the requested long duration locally. The user requested one hour for the final delivery. Long exports belong under ignored exports/, with hashes and reproduction instructions in the repo; do not claim those exports are backed up by Git.

## Scene-specific listening check

Can warmth and cold coexist without bright icy chimes? Are pads distinguishable at low volume? Does it stay calm rather than becoming ominous horror ambience?

Also check for unwanted vocal-like sounds, percussive transients, abrupt level changes, repetitive hooks, uncomfortable sub-bass, thin midrange and poor mono translation. These are listening questions, not claims about ungenerated audio.

## Shared decisions

Use the learned independent-voice and audible-midrange direction from creative/MUSIC_WORKFLOW.md. Do not impose a named fixed key, unverified reference BPM or compulsory drone note. Keep literal scene sound effects separate from this music pass. Long-form comfort matters more than elaborate instrumentation. Put exclusions only in a negative field if editing style chips; do not let comma splitting turn them into positive tags.

The adjacent description/tags are narrative publication drafts. Add accurate soundtrack wording and duration only after the audio and final upload are known. Do not claim human-composed or no AI music for an ElevenLabs generation.

## Official prompting source

[ElevenLabs Music best practices](https://elevenlabs.io/docs/overview/capabilities/music/best-practices), checked 2026-09-28: specify musical intent and instrumental-only output; audio references guide feel and palette. The scene palettes and workflow choices above are our own creative brief and accumulated user feedback. No quoted price or UI limit is assumed current.

## Prompt versions

Current short prompt: `elevenlabs-prompt-v3.txt` (2026-10-04). V1/v2 prompts are preserved. V2 short tests were rejected; the user liked the v3 direction in Colony Winter Night but reported lyrics. The v3 longer prompt is untested. The new direction replaces the air-like noise bed and rare accents with a changing four-chord progression, bass movement, a three-note phrase with varied replies and a later countermelody. This is a proposed correction based on feedback, not a claim about the generated audio. See generation-record.json for the exact feedback and supplied file hashes.

Notes kept out of the prompt text on purpose:

- Attach your chosen one-minute test as the audio reference in the UI before running the long prompt. A reference guides feel and palette, not exact continuation.
- The current long prompt requests seven minutes; the final local loop target is one hour.
- A prompt cannot guarantee a seamless loop. Loop points, crossfades and seamlessness are decided locally after inspecting the export.
- Paste into the prompt/song-description field, not lyrics. If you edit style chips, keep exclusions in the negative row.
