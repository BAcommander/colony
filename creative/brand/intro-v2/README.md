# Ambient Colony opening — v2

2026-10-13. Current default in the actual Colony final-video tool. V1 worked technically but the user rejected the visual treatment: opening too bright, channel/title/underline too small, PRESENTS absent, tagline needed at the bottom earlier and held longer. [V1 media and source snapshot](../intro-v1/) are preserved.

## Changes

- Opening black overlay increased from 50% to **88%**, leaving a faint view of the running scene. Held until 0:10, then released gradually to 0:20.
- **AMBIENT COLONY** font size almost doubled (3.9% → 7.7% of frame height), with a proportionately larger orbital logo. Appears 2–3.2s, holds through 8s, fades by 9s.
- **PRESENTS** has its own delayed fade under the channel name: 4.8–5.8s, held through 8s, cleared by 9s.
- Location title font increased about 47% (11.2% → 16.5% of frame height), with safe wrapping/shrinking for long names. Amber underline is about 3.7 times wider and thicker. Title appears 10–11s, fades 14–15s.
- **Stay a while and listen:** is centered at 89% of frame height. It appears 12–13s, two seconds before the title begins fading. It remains fully visible through 20s, five seconds after the title clears, then fades 20–21.5s. All text is clear by 22s.

The user's revised tagline instruction supersedes v1's strictly sequential, centered tagline. Audio remains silence to 0:05 with its existing slow rise to normal at 0:20. No new music or production video is requested. Timings above are the implemented interpretation for review, not a claim of user approval.

## Future use

Open `C:/dev/SpeedySlideShow/dist/Colony.exe`, enter the public title and leave **Include opening** enabled. Preview opening works without any music and produces a silent 25-second sample. Future scripted assembly passes `intro=IntroSettings(public_title)`. The native graphics include bundled Barlow Condensed fonts, warm ivory, amber accents and the orbital mark from our thumbnail identity.

The renderer now budgets 22 seconds for graphics. It must not truncate image inputs at the old 20-second cutoff; that would cut the final tagline fade. Only the complete opening loop unit(s) are rendered with the treatment, keeping scene phase into subsequent copied clean units. On a twenty-second scene loop the opening chunk spans forty seconds; text is still clear by 22. No runtime is added. Existing masters, later SFX event times, audio joins, levels and closing fades are preserved. Avoid stacking the intro fade with a baked-in opening fade; use an unfaded opening mix or untick the tool's fade option.

Play the intro once at livestream startup, outside the looping playlist. A finished branded MP4 repeated by another application will naturally repeat its opening.

## Review files and checks

- `colony-intro-v2-silent-preview.mp4`: 25 seconds, 720p/30 fps, generated silence only, actual Colony engine over the same Rainline v5 scene used for v1. This is a branding sample, not a new Rainline release.
- `timing-contact-sheet.jpg` and `frame-*.png`: decoded 1/6/13/16/19/23-second samples, including title/tagline overlap and the continued lower hold.
- `native-4k-graphics/`: four transparent graphic cards drawn at native 4K output resolution. The sample video remains 720p.
- `delivery.json`, export manifest, `preview-validation.json` and `implementation-verification.json`: source/settings, validation, source/executable hashes and build evidence.
- `feedback.json`: exact v1 feedback and interpretation for v2.

Regression checks cover the deeper darkness, enlarged lettering/rule, delayed PRESENTS, low tagline overlapping and outlasting the title, exact copied clean tail frames, non-divisor loop phase, audio envelope, late SFX timing and no-music preview. Small 180p test fixtures use contrast thresholds appropriate to subpixel-antialiased letters; native/720p stills are also inspected.

Recreate from this repo with `python scripts/preview_colony_intro.py`. It defaults to v2 and preserves an existing video by versioning the filename. The earlier app is saved as `C:/dev/SpeedySlideShow/dist/Colony-intro-v1-2026-10-13.exe`.

Assistant inspected decoded temporal stills and native graphics, not continuous playback. User review of v2 remains pending. Saved locally; no commit, push, remote-backup verification, music generation or full-release regeneration in this revision.
