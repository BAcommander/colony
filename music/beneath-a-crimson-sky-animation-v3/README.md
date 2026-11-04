# Beneath a Crimson Sky: V3 dry gusts

[Watch the 60-second silent preview](beneath-a-crimson-sky-v3-dry-gusts-60s.mp4), 1280×720 at 30 fps. This candidate adds dry mineral dust moving low across the plain in three staggered passes. The parapet and terrain hide the dust where they should, leaving the terrace sheltered. This applies Snowline's lessons about separating weather by depth and keeping silhouettes intact. The existing V2 cloud movement, more distant dust, lantern, windows and three intracloud flashes carry through.

Gusts enter at 3, 24.5 and 48.5 seconds and last 21.5, 20 and 19 seconds respectively, with the last pass wrapping through the seam. They move at 7.2–8.2 preview pixels per second. See the [lore and SFX plan](../../final/15-beneath-a-crimson-sky/weather-and-sfx.md) for the dry setting and possible thunder cues.

[Delivery checks](delivery-v3.json) cover all 1,800 decoded frames, timestamp spacing, source pixel protection, silence and the dust seam. The first encode exposed an FFmpeg range conversion; declaring limited-range BT.709 at the raw input restored exact unchanged pixels. Sampled decoded frames were inspected. User playback review is pending.

Reproduce with `python music/beneath-a-crimson-sky-animation-v3/render_dust_pass.py` using NumPy, OpenCV, imageio-ffmpeg and the hash-checked V2 clip. This is a screen-space pass for the 720p preview; after acceptance, rebuild the dust on the full-resolution animation before the 4K master.
