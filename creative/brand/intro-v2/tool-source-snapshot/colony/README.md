# Colony

A small internal tool built on the Speedy SlideShow exporter: loop one short
video under a playlist of audio tracks and export a single MP4, typically a
long ambient video for YouTube.

- **Video**: loops for the whole export; its own audio is dropped. The output
  keeps the video's size and frame rate (no scaling, ever).
- **Opening titles** (on by default in the app): enter the public video title.
  V2 starts near black (88% black overlay). Larger orbital logo and AMBIENT
  COLONY appear at 2 seconds; **PRESENTS** reveals underneath at 4.8 seconds.
  The enlarged location title and longer amber underline appear at 10 seconds.
  **Stay a while and listen:** appears near the bottom at 12 seconds, before
  the main title fades at 14–15. It holds until 20, five seconds after the title
  clears, then fades out by 21.5. Scene reveals from 10 to 20; everything is
  clear by 22. Ivory Barlow Condensed/amber graphics follow the thumbnail style
  and are rendered natively at the output resolution, including 4K.
- **Opening audio**: the checked fade option holds silence until 0:05, then
  gently raises the final music/SFX mix to its supplied level at 0:20. Use a
  soundtrack made without its old opening fade. Colony cannot remove a fade
  baked into a recording: untick this option to keep supplied fades. SFX event
  times and closing fades stay in place. The opening adds no runtime and never
  repeats with the scene loop.
- **Preview opening**: twenty-five seconds through the real export path,
  including selected music/SFX if present. Without a music playlist it produces
  a clearly labelled silent visual preview; no soundtrack needs to be made first.
  This preview keeps the full playlist's SFX and subscription schedule.
- **Audio**: add tracks one by one (or several at once), reorder, remove.
  Every track plays in full, in order, with an equal-power crossfade between
  separate files (default 5 s, 0 = none; the control is disabled with a
  single track). Supplied fades remain baked in, so choose the opening audio
  option accordingly. Each track keeps the level it was
  supplied at unless "Match every track to -14 LUFS" is on, which applies a
  fixed gain per track (the music keeps its dynamics). A peak limiter at
  -1.5 dBFS is always in the chain and touches nothing already under it.
- **Rain / SFX** (optional): choose a separate environmental recording and mix it
  underneath the playlist. Set its volume in dB, start delay, continuous or
  intermittent mode, rain duration (including its fades), quiet gap, fade-in,
  fade-out and source-loop crossfade. Times are seconds. The source is decoded
  to a reusable PCM loop with an equal-power tail/head overlap; the overlap is
  capped at one third of very short sources. Rain never changes playlist length
  or normalises the music. A final limiter protects the combined audio.
  The final rain event also fades at the end of the export.
- **Preview mix**: audition the actual opening music and rain settings without
  choosing a video. Intermittent mode covers the first fade, gap and return,
  up to ten minutes; continuous mode previews 90 seconds. Timing is not compressed,
  so a start delay longer than the preview stays silent. Video preview remains
  separate and silent. Rain settings are recorded in the export manifest;
  the controls reset to defaults when the app is restarted.
- **Overlay** (optional): a greenscreen clip (flat `#00FF00` background,
  e.g. a subscribe banner) keyed over the video bottom centre, N px up from
  the bottom (default 100, in 1080p pixels: scaled with the export's
  height). Shown once, centred on the middle of the video (default), or
  every N minutes (first showing at N, not at the start). Each showing
  starts on the loop boundary nearest its time, so it can be up to half a
  loop early or late; the window shows the planned times before you
  export. The overlay's own sound is not used.
  With opening titles enabled, subscription showings are deferred until the
  first loop boundary at or after 0:22; a showing that no longer fits is omitted.
- **Preview**: a short MP4 with the real export settings (a loop, the
  overlay chunk, a loop), opened in your video player, to check the seam
  and the overlay's size, placement and edges. Its encodes are reused by
  the export that follows.
- **Export**: a summary (inputs, length, levels, overlay times, destination)
  before it starts; staged progress with elapsed time and an ETA per step;
  the video is encoded once (seconds of work) and then copied for the whole
  length, so the export time is mostly the audio. Measured: a 72-minute,
  10-track, 1080p export takes about 1.5 minutes. File size is set by the
  video: a busy 1080p loop runs about 3 GB per hour.
- **Finished files**: an existing file is never overwritten silently (the
  export goes to `name (2).mp4`, also if the original is open in a player);
  the file is written under a temporary name and renamed only when
  complete. The finished file's streams, size, frame rate and duration are
  checked, optionally by a full decode, and a manifest
  (`name.export.json`: inputs, settings, overlay times, checks) is written
  beside it. A failed export leaves `name.error.log` instead. The checks
  are technical: whether the seam and the overlay LOOK right is yours.

## Run / build / test

```
python -m colony.gui                 # from the repo root
colony\build.bat                     # -> dist\Colony.exe (single file, ffmpeg bundled)
python -m pytest tests/test_colony.py tests/test_colony_sfx.py tests/test_colony_intro.py -q
```

How it renders, and why, is in the docstring of `colony/render.py`.

Opening implementation: `colony/intro.py`, with OFL fonts in `colony/assets/fonts/`.
Only complete initial loop units are re-encoded for the opening; all later clean
units retain the existing stream-copy path. The opening stays in YUV, using the
source colour matrix for graphics. Prepared opening chunks are cached by source,
settings, renderer and font hashes. Export manifests record exact timings, wording
and font hashes. API callers opt in with `IntroSettings(title=...)`; old scripted
exports remain compatible. The GUI defaults to enabled on each new launch, with a
blank title to prevent accidentally reusing another release's name.

For continuous broadcasts, the branded intro belongs at stream startup, outside
the file/playlist being repeated. Replaying a completed MP4 necessarily replays
its opening; the tool cannot change a streaming program's playlist behaviour.

V1 worked technically but was rejected as too bright/small, with PRESENTS missing
and the tagline in the wrong place/time. V2 implements that feedback; user visual
review remains pending. No existing finished videos are automatically regenerated.

## Decisions (from the first two-hour Basalt export)

- **Overlay colour shift, fixed.** The overlay chunk's background came out
  warmer than the loop around it, graphic or no graphic: the first version
  keyed the graphic in RGBA and let ffmpeg's overlay filter choose its
  working format, which pushed the whole background through RGB and back
  with a different matrix and dropped the bt709 tags. Now only the graphic
  is converted (with the loop's own matrix), the overlay filter is pinned
  to yuv420, and both encodes carry the same explicit colour tags.
  `TestRender.test_overlay_chunk_keeps_colour` compares raw pixels.
- **Audio level is kept, not matched, by default.** That export came out
  at -16 LUFS against a -17.7 soundtrack. YouTube turns loud uploads down
  to -14 LUFS and leaves quiet ones alone, so the gain bought nothing and
  broke the level match with the other videos using the same soundtrack.
  Matching is opt-in for playlists of mixed sources, and targets -14.
- **One showing, halfway.** The subscribe banner every 15 minutes was the
  old default doing what it said. The default is now once, centred on the
  middle; "every N minutes" stays as the other mode.
- **Not done, on purpose.** No output size or duration choice: the output
  matches the video and the audio, which is what the copy-only path (one
  encode, then stream copy) depends on.
