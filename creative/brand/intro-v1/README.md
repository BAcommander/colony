# Ambient Colony opening — reusable v1

Historical version: user rejected this look on 2026-10-13. See [current v2](../intro-v2/README.md) and its exact feedback. The media/evidence and `tool-source-snapshot/` preserve v1; the shared preview script now generates v2.

Implemented 2026-10-13 in the actual Colony final-video tool at `C:/dev/SpeedySlideShow/colony/`. This is an upgrade for future production. The user clarified that they are not making a new video or music now; the silent Rainline sample is a styling/timing demonstration only.

## Treatment

- Warm ivory `#F3EBDD`, Barlow Condensed SemiBold titles, Regular tagline, restrained amber `#E7A83E` accents, matching our [thumbnail identity](../../../final/THUMBNAIL_STYLE.md).
- Native orbital logo: fine ivory circle with its upper-right satellite dot, amber divider, spaced AMBIENT COLONY lettering. This reconstructs the simple existing mark in graphics; it is not a newly generated scene/logo.
- Brand fades in at 2–3 seconds, holds to 7, fades out by 8. Scene stays dark during the credit.
- Public location title fades in at 10–11, holds to 14, fades out by 15. One or two centered lines; long titles shrink to fit. Scene lifts gradually from half brightness at 10 to normal by 20.
- Final text is exactly **Stay a while and listen:**, appearing at 15.5–16.3, holding to 18.5, fading out by 20. The colon is intentional, following the user's supplied wording.
- Audio holds silence until 5 seconds, then a gentle half-cosine fade reaches the supplied listening level at 20. No sting or voiceover. Later SFX onsets remain where they were scheduled.

The start at 0:05, final tagline/order, thumbnail styling and logo are user instructions. Other timings are implemented first-version design choices awaiting visual/listening feedback. Reference evidence remains the [five supplied screenshots](../references/ambient-outpost-project-hades-2026-10-13/manifest.json); no claim of watching/hearing the reference video.

## Future production

1. Open `C:/dev/SpeedySlideShow/dist/Colony.exe`. **Include opening** is enabled by default; enter the current public title. The title starts blank so a previous release name cannot carry into another export.
2. **Preview opening** renders 25 seconds with the actual export treatment. Music is optional: an empty playlist gives a silent visual preview. The existing video-loop preview remains separate.
3. For the new audio entrance, supply an audio mix without the old opening fade. The tool applies its fade once after mixing music/SFX. It cannot undo a fade baked into a file; untick the fade option when retaining supplied fades. Preserve scene-specific gains, music joins, SFX timing, total duration and closing fades.
4. The opening occupies the first 20 seconds of the requested duration. Only the complete opening loop unit(s) are encoded with graphics; later clean units retain the existing stream-copy route. Text/dimming disappear by 20 even when an opening unit is longer. Background stays in YUV with explicit colour tags. The opening cache includes source, font, renderer and settings fingerprints.
5. Future scripted assembly must pass `intro=IntroSettings(public_title)` to `colony.render.render`. Existing API calls default to no intro for backwards compatibility; historical assembly scripts and approved masters are preserved. Reuse a verified `Prepared` cache where required by existing scene colour checks.
6. A separate subscribe overlay is deferred to the first complete loop boundary after the opening if necessary. Its own approval remains separate.
7. For a continuous livestream, play the opening once at stream startup and keep the continuing playlist clean. Repeating a whole finished branded file in an external player will repeat its intro.

## Review and evidence

- `colony-intro-v1-silent-preview.mp4`: 25 seconds, 1280×720, 30 fps, silent audio; made through the actual tool over the existing Rainline v5 preview. This is not a new Rainline release or a music audition.
- `timing-contact-sheet.jpg`, `frame-*.png`: decoded visual samples. Assistant inspected these; continuous playback and user artistic approval are not claimed.
- `native-4k-graphics/`: native-resolution transparent title/logo/tagline cards. Text is rendered at output resolution, including 4K; the demo video is 720p.
- `delivery.json` and the export manifest: exact settings, source and font hashes, full-decode verification.
- `implementation-verification.json`: source/executable fingerprints, tests, build and startup evidence. The prior executable is preserved as `dist/Colony-before-intro-2026-10-13.exe`.
- Recreate: `python scripts/preview_colony_intro.py` from this repo. `--tool-root`, `--video`, `--title`, and `--output` are available. Outputs are versioned by the tool rather than overwriting an existing video.

Technical checks cover audio silence/ramp, once-only text, unchanged clean tail frames, scene phase with non-divisor loops, preserved late SFX, preview/export agreement, retained supplied audio, title safety, native 4K graphics and a no-music preview. Current Colony suite: **67 tests pass**. Rebuilt app passes a ten-second startup smoke check and includes both fonts plus their OFL licence.

Saved locally in the two repositories. No commit/push or remote-backup verification is claimed for this change. No existing release was regenerated and no music was generated or required.
