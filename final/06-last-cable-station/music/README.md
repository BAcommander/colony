# 06 soundtrack preparation

Status (2026-10-03): user selected Colony Cableway Transit, then supplied Mineral Valley Transit as the longer version. Actual decoded audio is eight minutes (480 seconds). Original files are preserved under exports/06-last-cable-station/source/. A 66-second join audition and 20:43 three-repeat preview are ready; see [analysis and auditions](long-source-v1/README.md). Sixteen-second crossfade, source 0:38-7:43, fixed -7 dB gain. User accepted the audio/transition as good enough; no assistant listening claimed. The user confirmed two hours. The [two-hour soundtrack](../../../exports/06-last-cable-station/Last-Cable-Station-Mineral-Valley-Transit-2-Hours-v1.mp3) and [combined 4K Colony export](../assembly-v1/README.md) are delivered and fully decode-verified. See long-source-v1/two-hour-delivery-v1.json; full listening remains pending.

## Files and manual generation

1. Paste `elevenlabs-prompt-v2.txt` into the Music prompt/song-description field, not lyrics. Use instrumental mode if available. Set 60 seconds and two variants if the interface offers those controls. The user runs generations manually with their own existing credits; inspect the actual displayed cost first. No API or paid generation was run here.
2. Listen at matched comfortable volume and choose one test. Stop and adjust only the unresolved characteristic if both miss. Do not blindly generate more variants.
3. For the chosen user-generated test, use the available audio-reference control and `elevenlabs-long-version-v3-seven-minutes.txt`. The supplied longer version followed the seven-minute request; for another generation aim for roughly seven minutes and one variant if supported; follow the actual interface and reference limits. A reference guides feel and palette, not exact continuation.
4. Keep the downloaded originals and record actual settings, filenames, duration, selected variant and feedback in generation-record.json. The selected short test is now recorded; unobserved generation settings and unfinished stages remain null.
5. Supply the export for local duration/fade/loudness inspection, candidate loop-point selection and a short join audition. Choose crossfade length from this track; Ringfall's 15 seconds is not a universal default. A prompt cannot guarantee a seamless loop.
6. Only after listening approval assemble the requested long duration locally. The user selected two hours, now delivered. Long exports belong under ignored exports/, with hashes and reproduction instructions in the repo; do not claim those exports are backed up by Git.

## Scene-specific listening check

Does it feel spacious and gently hopeful without becoming a triumphant film score? Are the swells slow and independent rather than synchronized pumping? Is the occasional phrase subtle enough for repeated listening?

Also check for unwanted vocal-like sounds, percussive transients, abrupt level changes, repetitive hooks, uncomfortable sub-bass, thin midrange and poor mono translation. These are listening questions, not claims about ungenerated audio.

## Shared decisions

Use the learned independent-voice and audible-midrange direction from creative/MUSIC_WORKFLOW.md. Do not impose a named fixed key, unverified reference BPM or compulsory drone note. Keep literal scene sound effects separate from this music pass. Long-form comfort matters more than elaborate instrumentation. Put exclusions only in a negative field if editing style chips; do not let comma splitting turn them into positive tags.

The adjacent description/tags are narrative publication drafts. Add accurate soundtrack wording and duration only after the audio and final upload are known. Do not claim human-composed or no AI music for an ElevenLabs generation.

## Official prompting source

[ElevenLabs Music best practices](https://elevenlabs.io/docs/overview/capabilities/music/best-practices), checked 2026-09-28: specify musical intent and instrumental-only output; audio references guide feel and palette. The scene palettes and workflow choices above are our own creative brief and accumulated user feedback. No quoted price or UI limit is assumed current.

## Prompt versions

Current: `elevenlabs-prompt-v2.txt` and `elevenlabs-long-version-v3-seven-minutes.txt` (2026-09-29), written to the prompt writing rules in creative/MUSIC_WORKFLOW.md. `elevenlabs-prompt-v1.txt` and `elevenlabs-long-version.txt` are preserved history. The supplied short test is selected; its actual generation prompt/settings were not observed. V3 seven-minute brief was supplied before the longer export; exact generation settings and prompt were not observed. V1/v2 remain preserved.

Notes kept out of the prompt text on purpose:

- Attach your chosen one-minute test as the audio reference in the UI before running the long prompt. A reference guides feel and palette, not exact continuation.
- The current long prompt requests about seven minutes; the actual supplied export contains eight minutes of audio.
- A prompt cannot guarantee a seamless loop. Loop points, crossfades and seamlessness are decided locally after inspecting the export.
- Paste into the prompt/song-description field, not lyrics. If you edit style chips, keep exclusions in the negative row.
