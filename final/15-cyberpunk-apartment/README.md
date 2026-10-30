# 15 — Cyberpunk Apartment

Imported into Ambient Colony on 2026-10-25 at the user's request, appended after 14 — Crater Rim Survey. Cyberpunk Apartment is the existing working title; final public naming and publication packaging remain open. Spirewatch and Beneath a Crimson Sky remain unnumbered.

- [4K V3 loop](animation-v3/Cyberpunk-Apartment-V3-4K.mp4): ten seconds, 60 fps, silent, 3840 × 2160.
- [1080p V3 loop](animation-v3/Cyberpunk-Apartment-V3-1080p.mp4): ten seconds, 60 fps, silent.
- [Clean artwork](artwork-v3.png): native 1672 × 941. The 4K video is an upscale.
- [Original animation brief](animation-v3/brief.txt), [image repair prompts](animation-v3/art-prompts.txt), and [original delivery notes](animation-v3/README.txt).
- [Import manifest](manifest.json), [historical delivery checks](animation-v3/delivery-report.json), and [car-removal close-up](animation-v3/car-removal-check.jpg).

## Existing motion

V3 removes four hovering cars, uses irregular ground traffic, traveling sign lights, independent window details, rain, mist, water/floor reflections and restrained steam from the cup. Camera and architecture remain fixed. This import copies the existing deliverables byte-for-byte; no animation was regenerated.

## Status and remaining work

The user selected this existing animation for addition to the Colony catalog. That does not establish approval of a final public title, thumbnail, soundtrack, long-form assembly or upload. No music, Colony thumbnail, description, search tags or music prompts have been prepared for this package. Next: confirm the public title, prepare Colony packaging, select music and the eventual upload runtime. Apply the established Colony opening once during later assembly; do not bake it into every loop.

Prior verification/playback statements in animation-v3 are historical records from the original September delivery, not new playback claims from this import. This migration verifies hashes and file relationships. No new creative review or rendering was performed.

## Reproduction and storage

animation-v3/render.py uses clean-apartment.png and NumPy/Pillow/FFmpeg (the original machine-local FFmpeg path is retained). prepare_art.py uses the original artwork in this package's parent directory plus the saved imagegen repairs. The four unmodified scripts are preserved in animation-v3/source-snapshot/. Working render.py and prepare_art.py now refuse to overwrite the imported deliverables; copy to a new version before revisions. Existing reports retain their historical paths for provenance.

The imported MP4 paths have narrow Git-ignore exceptions and Git LFS rules, matching Colony's short-master convention. Local inclusion is not a commit, push or remote backup. The original folder G:/AI/youtube/cyberpunk-apartment-loop remains intact so existing links and earlier versions keep working. Superseded draft videos, failed diagnostic images and caches were not imported.
