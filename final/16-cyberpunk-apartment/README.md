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

Current draft refresh, 2026-11-07: use the [shared V4 music prompt framework](../../creative/music/prompt-framework-v4.txt) before writing or generating apartment music. The user's strong preference for both revised Baal samples makes musical development, expressive contrast and a clear emotional relationship the priority. This feedback establishes the approach; it does not approve these ungenerated apartment prompts.

The apartment retains its own identity: warm analogue voices close to the listener, a cooler sustained distance beyond the glass, and the feeling of a small inhabited refuge in a vast city. The revised drafts give sparse and fuller passages room to develop, allow tension and release, and connect occasional phrases across changing harmony. Piano is not compulsory, and gradual expansion is allowed. Music keeps its own pacing independently of the repeating picture.

- [Amber Room V2](music/elevenlabs-amber-room-v2.txt) is the closer passage, moving from quiet uncertainty toward warmth before thinning into exposed voices.
- [City Through Glass V2](music/elevenlabs-city-through-glass-v2.txt) is the wider passage, letting distant harmonies and connected fragments expand, recede and return with a changed colour.

Both V2 prompts are **ungenerated and unreviewed drafts**. Start with short dry pilots at the same actual length and settings. Compare them at matched listening levels for a distinct emotional direction, meaningful sparse-to-full development, connected phrases and comfort over repeats. Record the exact prompt, settings, files and user feedback before extending a selected direction. Then audition both joins and multiple repeats before the longer work-session listen. Treat rain through the glass as a separate layer and compare the same music with and without it.

The original [Amber Room draft](music/elevenlabs-amber-room.txt) and [City Through Glass draft](music/elevenlabs-city-through-glass.txt) are preserved byte-for-byte as history. Their blanket "no build" wording is superseded in V2 by controlled musical expansion and peaks. The original [Snowline proposal for Crater Rim](../14-crater-rim-survey/music/README.md) remains context, not proof of the apartment's generation provenance or listening success. No new audio or generation is included in this prompt refresh.

## Reproduction and storage

animation-v3/render.py uses clean-apartment.png and NumPy/Pillow/FFmpeg (the original machine-local FFmpeg path is retained). prepare_art.py uses the original artwork in this package's parent directory plus the saved imagegen repairs. The four unmodified scripts are preserved in animation-v3/source-snapshot/. Working render.py and prepare_art.py now refuse to overwrite the imported deliverables; copy to a new version before revisions. Existing reports retain their historical paths for provenance.

The imported MP4 paths have narrow Git-ignore exceptions and Git LFS rules, matching Colony's short-master convention. Local inclusion is not a commit, push or remote backup. The original folder G:/AI/youtube/cyberpunk-apartment-loop remains intact so existing links and earlier versions keep working. Superseded draft videos, failed diagnostic images and caches were not imported.

## Expanded animation development â€” November5

[Scene-specific build plan](ANIMATION_DEVELOPMENT.md) Â· [Source map and both backlogs](../../creative/animation-development/2026-11-05-16-17/index.html). Twelve candidates are prioritized with source anchors, methods, prerequisites, coupled light/weather cues and visible proof gates. This original planning checkpoint is retained below the current draft link. Source originals/previous masters remain unchanged; the first draft does not imply artistic approval.
