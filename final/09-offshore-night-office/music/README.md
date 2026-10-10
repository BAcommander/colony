# 09 soundtrack preparation

Current delivery (2026-10-10): approved music join and water v2 are included in the final two-hour 4K video. See [upload files](../YOUTUBE-FILES.txt) and [checks](../assembly-v1/README.txt). Earlier preparation notes below describe previous states; full combined review/upload checks remain pending.


Status: 2026-10-10 — user prefers test B, Open Water, and supplied Alien Ocean Vista. Selected source preserved in selected-test-v1/ with selection.json; full finite audio decode passed. Eight-minute Alien Sea Viewport source received; sixty-second join audition is ready in long-source-v1/ (crossfade at 0:24â€“0:36). Final duration and join approval remain pending. Water SFX prompt: water-sfx-prompt-v1.txt. Exact generation settings were not observed; no assistant listening claim.

## Files and manual generation

1. Paste `elevenlabs-prompt-v2.txt` into the Music prompt/song-description field, not lyrics. Use instrumental mode if available. Set 60 seconds and two variants if the interface offers those controls. The user runs generations manually with their own existing credits; inspect the actual displayed cost first. No API or paid generation was run here.
2. Listen at matched comfortable volume and choose one test. Stop and adjust only the unresolved characteristic if both miss. Do not blindly generate more variants.
3. For the chosen user-generated test, use the available audio-reference control and `elevenlabs-long-version-v2.txt`. Aim for roughly five minutes and one variant if supported; follow the actual interface and reference limits. A reference guides feel and palette, not exact continuation.
4. Keep the downloaded originals and record actual settings, filenames, duration, selected variant and feedback in generation-record.json. The selected test and feedback are recorded; unobserved generation settings remain null.
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

## Prompt versions

Current: `elevenlabs-prompt-v2.txt` and `elevenlabs-long-version-v2.txt` (2026-09-29), written to the prompt writing rules in creative/MUSIC_WORKFLOW.md. `elevenlabs-prompt-v1.txt` and `elevenlabs-long-version.txt` are preserved history. New v3 test B is now selected; original v1/v2 briefs are preserved as history.

Notes kept out of the prompt text on purpose:

- Attach your chosen one-minute test as the audio reference in the UI before running the long prompt. A reference guides feel and palette, not exact continuation.
- The long prompt says "about five minutes". If you choose ten minutes, edit that number before pasting.
- A prompt cannot guarantee a seamless loop. Loop points, crossfades and seamlessness are decided locally after inspecting the export.
- Paste into the prompt/song-description field, not lyrics. If you edit style chips, keep exclusions in the negative row.
