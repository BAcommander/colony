# 08 soundtrack — Rainline Relay

Status: 2026-10-10 — user selected the final **Above the Flooded Canopy** seven-minute piece, requested one hour, and supplied a separate 30-second rain recording. Both a music-only hour and an intermittent-rain hour are delivered. Every decoded sample was checked; both are exactly 3,600 seconds with no clipping. Music transition and quieter v3 rain approved by the user; full-hour listening remains pending; no assistant listening or independent vocal-absence claim.

Current rain revision: `long-source-v1/Rainline-rain-mix-preview-v3.mp3`; exact settings and validation: `long-source-v1/rain-mix-delivery-v3.json`. V1 is preserved.

See [delivery and listening notes](long-source-v1/README.md) and [exact recipe/checks](long-source-v1/one-hour-delivery-v1.json). The supplied source and earlier selected short test are preserved. No new generation credits, commit or push.

The Colony tool at `C:/dev/SpeedySlideShow/dist/Colony.exe` now supports optional continuous/intermittent SFX, gain, start delay, rain duration, gap, fades, loop crossfade and a separate mix preview. Use the **music-only** hour plus rain in its SFX field when changing the mix. Alternatively use the premixed rain hour with SFX removed to avoid adding rain twice. Settings are stored in the export manifest but do not persist in the UI between launches.

## Source and review

1. Selected short test: Flooded Forest Radio Room, preserved in selected-test-v1/.
2. Selected long source: Above the Flooded Canopy, preserved in long-source-v1/. Exact generation settings remain unobserved; seven-minute decoded audio verified.
3. Candidate loop uses source 0:20–6:48, twelve-second equal-power overlaps and fixed -6 dB gain. Only the full hour has a ten-second opening and twenty-second closing fade. The user approved the music join: "the transition between pieces sounds totally fine".
4. Rain mix starts after twenty seconds: two minutes on (including fades), ninety seconds off, twenty-second fade-in and thirty-second fade-out. Current v3 rain gain is -11.1804 dB relative to the supplied rain (43.75% of v1 amplitude), with a two-second source-loop crossfade.
5. Review the sixty-second music join (join at 0:24–0:36) and the 4:20 rain preview (first gap 2:20–3:50). All current exports and source hashes are in the delivery record.
6. Long exports are local under exports/. Latest v5 animation was authorized for final assembly; 4K master and final one-hour video are delivered. Combined review/upload checks remain pending.

## Scene-specific listening check

Do the soft phrases feel like gentle replies without becoming radio effects or a repeating hook? Can the interweaving midrange voices be heard quietly, with warmth rather than a blanket of bass?

Also check for unwanted vocal-like sounds, percussive transients, abrupt level changes, repetitive hooks, uncomfortable sub-bass, thin midrange and poor mono translation. These are listening questions, not claims about ungenerated audio.

## Shared decisions

Use the learned independent-voice and audible-midrange direction from creative/MUSIC_WORKFLOW.md. Do not impose a named fixed key, unverified reference BPM or compulsory drone note. Keep literal scene sound effects separate from this music pass. Long-form comfort matters more than elaborate instrumentation. Put exclusions only in a negative field if editing style chips; do not let comma splitting turn them into positive tags.

The adjacent description/tags are narrative publication drafts. Add accurate soundtrack wording and duration only after the audio and final upload are known. Do not claim human-composed or no AI music for an ElevenLabs generation.

## Official prompting source

[ElevenLabs Music best practices](https://elevenlabs.io/docs/overview/capabilities/music/best-practices), checked 2026-09-28: specify musical intent and instrumental-only output; audio references guide feel and palette. The scene palettes and workflow choices above are our own creative brief and accumulated user feedback. No quoted price or UI limit is assumed current.

## Prompt versions

Current short brief: `elevenlabs-prompt-v2.txt`; long-generation brief: `elevenlabs-long-version-v3-seven-minutes.txt`. Earlier v2 briefs (2026-09-29) were written to the prompt writing rules in creative/MUSIC_WORKFLOW.md. `elevenlabs-prompt-v1.txt` and `elevenlabs-long-version.txt` are preserved history. Both short and long sources have now been supplied; exact generation prompt/settings were not observed.

Notes kept out of the prompt text on purpose:

- Attach your chosen one-minute test as the audio reference in the UI before running the long prompt. A reference guides feel and palette, not exact continuation.
- The old v2 long prompt says five minutes; the proposed v3 says seven. Match the prompt duration to the chosen setting.
- A prompt cannot guarantee a seamless loop. Loop points, crossfades and seamlessness are decided locally after inspecting the export.
- Paste into the prompt/song-description field, not lyrics. If you edit style chips, keep exclusions in the negative row.
