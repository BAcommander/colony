# 09 soundtrack preparation

Status: prompts prepared 2026-09-28; no audio generated or evaluated for this scene. These are musical design choices, not measurements of a reference recording.

## Files and manual generation

1. Paste `elevenlabs-prompt-v1.txt` into the Music prompt/song-description field, not lyrics. Use instrumental mode if available. Set 60 seconds and two variants if the interface offers those controls. The user runs generations manually with their own existing credits; inspect the actual displayed cost first. No API or paid generation was run here.
2. Listen at matched comfortable volume and choose one test. Stop and adjust only the unresolved characteristic if both miss. Do not blindly generate more variants.
3. For the chosen user-generated test, use the available audio-reference control and `elevenlabs-long-version.txt`. Aim for roughly five minutes and one variant if supported; follow the actual interface and reference limits. A reference guides feel and palette, not exact continuation.
4. Keep the downloaded originals and record actual settings, filenames, duration, selected variant and feedback in generation-record.json. The files currently contain null values because nothing has been generated.
5. Supply the export for local duration/fade/loudness inspection, candidate loop-point selection and a short join audition. Choose crossfade length from this track; Ringfall's 15 seconds is not a universal default. A prompt cannot guarantee a seamless loop.
6. Only after listening approval assemble the requested long duration locally. No duration has been selected for this scene. Long exports belong under ignored exports/, with hashes and reproduction instructions in the repo; do not claim those exports are backed up by Git.

## Scene-specific listening check

Do long swells feel natural rather than rhythmically pumping? Is the sea suggested by musical space without literal surf or sonar? Is the low-mid warmth comfortable without a booming bass bed?

Also check for unwanted vocal-like sounds, percussive transients, abrupt level changes, repetitive hooks, uncomfortable sub-bass, thin midrange and poor mono translation. These are listening questions, not claims about ungenerated audio.

## Shared decisions

Use the learned independent-voice and audible-midrange direction from creative/MUSIC_WORKFLOW.md. Do not impose a named fixed key, unverified reference BPM or compulsory drone note. Keep literal scene sound effects separate from this music pass. Long-form comfort matters more than elaborate instrumentation. Put exclusions only in a negative field if editing style chips; do not let comma splitting turn them into positive tags.

The adjacent description/tags are narrative publication drafts. Add accurate soundtrack wording and duration only after the audio and final upload are known. Do not claim human-composed or no AI music for an ElevenLabs generation.

## Official prompting source

[ElevenLabs Music best practices](https://elevenlabs.io/docs/overview/capabilities/music/best-practices), checked 2026-09-28: specify musical intent and instrumental-only output; audio references guide feel and palette. The scene palettes and workflow choices above are our own creative brief and accumulated user feedback. No quoted price or UI limit is assumed current.
