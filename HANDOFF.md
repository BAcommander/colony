# Where we are

Updated 2026-11-11. This file is the single "pick up here" note. It is rewritten, not appended to, before every commit and push.

## Last session (11 November 2026)

1. **Analysed the user's long-listening reference**, Ambient Outpost's 24/7 stream THE SIGNAL STATION. Both it and WINTER WATCH carry a constant noise-like weather bed with very few stand-out moments; our tracks are mostly tonal with intermittent effects. [Analysis](creative/music/reference-analysis/signal-station-2026-11-11/README.md).
2. **Took the first YouTube Studio snapshot.** Viewers watch about a third of any video length, click-through is the weakest number (3.1% overall, 1.4–2.4% on recent uploads), and playlists give the longest sessions. [Snapshot](creative/music/channel-research-2026-10-30/studio-export-2026-11-11/README.md).
3. **Added the improve-every-video rule** and the [improvement log](creative/IMPROVEMENT_LOG.md), which holds the six-step standing plan and the per-video experiment table.
4. **Started Beneath a Crimson Sky (#15, Skies of Baal) under the new plan.** Step 2 is built: a ten-minute continuous storm bed in two variants, dark and open, with optional distant thunder. [Storm bed](music/beneath-a-crimson-sky-storm-bed-v1/README.md).

## Next step

Step 3: audition the two 60-second Baal music tests under each storm bed, then choose. The two test files (`Crimson_Terrace_Vigil_2026-11-07T165049.mp4` and its `(1)` copy) live only on the PC where they were received, in `music/beneath-a-crimson-sky-test-intake-2026-11-08/sources/`. The storm-bed audio is in ignored `exports/` on the PC that built it; on another PC rebuild it:

```powershell
git lfs pull --include="music/sfx-library/assets/wind-soft-exterior-01.mp3,music/sfx-library/assets/grit-mineral-soft-01.mp3"
.local/audio-analysis/Scripts/python.exe music/beneath-a-crimson-sky-storm-bed-v1/build_bed.py
```

The build is seeded, needs NumPy, SciPy and imageio-ffmpeg, and refuses to overwrite an existing output folder.

## Waiting on the user

1. Storm bed: dark or open, and is the thunder right, too much, or unnecessary?
2. Runtime for #15: two hours, or longer?
3. Willing to generate both music tests as long pieces (two or three generations of about five minutes)?
4. Willing to generate two new effects in ElevenLabs: a longer low desert wind, and a continuous fine sand hiss? Prompts not yet written.
5. May the title name the inspiration (as the Hoth video did), or stay generic?
6. Is Monday 16 November fixed for #15?

## Release calendar

- Thu 12 Nov — #14 Crater Rim Survey: one-hour 4K final built; user watch-through and upload pending.
- Mon 16 Nov — #15 Beneath a Crimson Sky: in progress as above. Animation is a 60-second storm loop awaiting intensity review; no 4K yet; thumbnail not chosen.
- Thu 19 Nov — #16 Cyberpunk Apartment.

## Not done or not verified

- Nobody has listened to the storm bed yet.
- The constant-bed idea is a hypothesis; it has not been tested in one of our own mixes.
- The Studio snapshot was transcribed from on-screen tables and lacks devices, retention curves and per-video traffic sources.
- The 14-day figures for Below the Snowline are due 23 November.
