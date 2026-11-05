# 16 â€” Cyberpunk Apartment

Current2026-11-05: [V4 complete sixty-second visual draft](../../music/cyberpunk-apartment-animation-v4/README.md),720p/60fps, silent. [Watch both drafts and detail reviews](../../creative/animation-development/2026-11-05-16-17/review.html). All twelve candidates have a first-pass treatment; user visual review, long event schedule, audio and4K remain pending. Previous art and masters are preserved.

Imported into Ambient Colony on 2026-10-25. On 2026-11-04 the user moved it to #16 after [Beneath a Crimson Sky](../15-beneath-a-crimson-sky/README.md). Cyberpunk Apartment remains the working title.

- [4K V3 loop](animation-v3/Cyberpunk-Apartment-V3-4K.mp4): ten seconds, 60 fps, silent, 3840 Ã— 2160.
- [1080p V3 loop](animation-v3/Cyberpunk-Apartment-V3-1080p.mp4): ten seconds, 60 fps, silent.
- [Clean artwork](artwork-v3.png): native 1672 Ã— 941. The 4K video is an upscale.
- [Original animation brief](animation-v3/brief.txt), [image repair prompts](animation-v3/art-prompts.txt), and [original delivery notes](animation-v3/README.txt).
- [Import manifest](manifest.json), [historical delivery checks](animation-v3/delivery-report.json), and [car-removal close-up](animation-v3/car-removal-check.jpg).

## Existing motion

V3 removes four hovering cars, uses irregular ground traffic, traveling sign lights, independent window details, rain, mist, water/floor reflections and restrained steam from the cup. Camera and architecture remain fixed. This import copies the existing deliverables byte-for-byte; no animation was regenerated.

## Status and remaining work

The user selected this existing animation for addition to the Colony catalog. The public title, thumbnail, description, search tags, soundtrack and runtime are pending. Apply the established Colony opening once during later assembly.

Prior verification/playback statements in animation-v3 are historical records from the original September delivery, not new playback claims from this import. This migration verifies hashes and file relationships. No new creative review or rendering was performed.

## Music drafts

These two prompts use the contrast between exposed and fuller passages from the [Snowline listening proposal for Crater Rim](../14-crater-rim-survey/music/README.md). The apartment's palette is warm analogue tones close to the listener and cooler sustained harmonics out beyond the glass. Give the music its own pacing across many repeats of the ten-second visual loop.

- [Amber Room](music/elevenlabs-amber-room.txt) is the closer passage. Warm, rounded synth voices gather into fuller harmony, then thin out at different speeds.
- [City Through Glass](music/elevenlabs-city-through-glass.txt) is the wider passage. A cooler sustained layer expands slowly, then gives way to a little warmth from the room.

Start with one dry pilot per prompt at the same length and settings. Compare them at matched listening levels for contrast, comfort and how soon a swell or fragment becomes predictable. If both work, try two passages of roughly five minutes using the actual generation settings. Audition both joins and three repeats before the work-session listen. Treat rain heard through the glass as a separate layer and compare the same music with and without it.

Both prompts are drafts for manual generation and listening review. Record the exact text, settings and source files when testing.

## Reproduction and storage

animation-v3/render.py uses clean-apartment.png and NumPy/Pillow/FFmpeg (the original machine-local FFmpeg path is retained). prepare_art.py uses the original artwork in this package's parent directory plus the saved imagegen repairs. The four unmodified scripts are preserved in animation-v3/source-snapshot/. Working render.py and prepare_art.py now refuse to overwrite the imported deliverables; copy to a new version before revisions. Existing reports retain their historical paths for provenance.

The imported MP4 paths have narrow Git-ignore exceptions and Git LFS rules, matching Colony's short-master convention. Local inclusion is not a commit, push or remote backup. The original folder G:/AI/youtube/cyberpunk-apartment-loop remains intact so existing links and earlier versions keep working. Superseded draft videos, failed diagnostic images and caches were not imported.

## Expanded animation development â€” November5

[Scene-specific build plan](ANIMATION_DEVELOPMENT.md) Â· [Source map and both backlogs](../../creative/animation-development/2026-11-05-16-17/index.html). Twelve candidates are prioritized with source anchors, methods, prerequisites, coupled light/weather cues and visible proof gates. This original planning checkpoint is retained below the current draft link. Source originals/previous masters remain unchanged; the first draft does not imply artistic approval.
