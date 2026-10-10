# Rainline Relay — one-hour audio v1

Created 2026-10-10 at the user's request. Both MP3s are stereo 48 kHz/192 kb/s, exactly one hour. Originals remain unchanged. The user has approved the music crossfade. V1 rain was too loud at peak; a requested further-reduced v3 is now the current review candidate.

- [Music-only hour](../../../../exports/08-rainline-relay/Rainline-Relay-Above-the-Flooded-Canopy-1-Hour-v1.mp3): -20.5 LUFS, -9.6 dBTP.
- [Hour with rain](../../../../exports/08-rainline-relay/Rainline-Relay-1-Hour-with-Rain-v1.mp3): -20.7 LUFS, -6.6 dBTP.
- [Music join, sixty seconds](Rainline-music-join-review-60s-v1.mp3): overlap at 0:24–0:36.
- [Rain preview, 4:20](Rainline-rain-mix-preview-v1.mp3): enters 0:20–0:40, fades away 1:50–2:20, silent 2:20–3:50, returns 3:50–4:10.

Current v3: [4:20 quieter rain preview](Rainline-rain-mix-preview-v3.mp3), [one hour with quieter rain](../../../../exports/08-rainline-relay/Rainline-Relay-1-Hour-with-Rain-v3.mp3), and [exact checks/settings](rain-mix-delivery-v3.json). Rain alone is reduced another 12.5% from the positively reviewed v2, to 43.75% of v1 amplitude; music and all timings stay unchanged. V3 rain balance now approved by the user and included in the final one-hour 4K video.

Historical v1 rain recipe: source -4 dB, starts after 20 seconds, two minutes on including twenty/thirty-second fades, ninety seconds off, two-second equal-power source-loop overlap. These are initial creative settings, not user-approved balance. Source 30-second MP3 is preserved in music/shared-rain-overlay/. Prepared 28-second float WAV is alongside this record.

The music excerpt is source 0:20–6:48, twelve-second equal-power joins, fixed -6 dB gain, with one ten-second opening and twenty-second closing fade. All four files fully decoded to exact expected sample counts, all samples finite and no clipping. Technical checks do not establish harmonic compatibility, vocal absence or listening comfort. See one-hour-delivery-v1.json for hashes and all timings.

Colony's updated executable is C:/dev/SpeedySlideShow/dist/Colony.exe; previous build is preserved as dist/Colony-before-rain-2026-10-10.exe. Use the music-only hour with its optional SFX controls to change the rain. Use the premixed hour with no additional SFX for this exact mix. Preview mix is independent of video preview. The later one-hour 4K video assembly is now delivered; see ../../assembly-v1/.

Reproduction script: make_rainline_hour.py (uses the installed Colony SFX module). Preserve existing outputs and choose new version names before rerunning. Media are local, not backed up by Git; no commit or push performed.
