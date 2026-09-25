# Ambient Colony subscribe banner v1

Ten-second, silent, graphics-only overlay in the channel's ivory/amber style. This is a first rendered version for user visual review; it is not marked creatively approved.

## Files

- `subscribe-v1-10s-4k-green.mp4`: 3840x2160, 30 fps, H.264, green background. Apply your editor's chroma-key effect and sample the green field (source RGB 0,255,0). Adjust edge cleanup on the actual clip; compressed green may differ slightly.
- `subscribe-v1-10s-4k-alpha.mov`: 3840x2160, 30 fps, ProRes 4444 with straight alpha. Place above the video; use straight/unmatted alpha if the editor asks. This avoids green-key edge cleanup. A player showing a black background does not necessarily mean alpha is missing.
- `subscribe-v1-preview.mp4`: 720p preview composited over ten seconds of the existing Ringfall video, for review. The background is baked into this preview; do not use it as an overlay.
- `subscribe-v1-still.png`: full-size transparent sample at four seconds.
- `preview-still.jpg`: sample over Ringfall artwork.
- `manifest.json`: dimensions, timing, hashes, complete decode/no-audio checks and decoded alpha samples.

All media contains no audio stream: no SFX, music or click sounds. The button is a visual subscribe invitation, not an interactive control.

## Design and timing

Opaque charcoal rounded panel, ivory orbital mark and channel name, amber divider and Subscribe button, and the line "Stay a while and listen." Barlow Condensed fonts are bundled under `creative/brand/fonts` with their license. Font styling follows `final/THUMBNAIL_STYLE.md`; it does not exactly reproduce generated letterforms.

The graphic sits at lower centre on a 4K canvas: left 800 px, resting top 1664 px, width 2240 px, height 312 px. Blank from 0-0.4 seconds; one-second eased slide up; readable hold from 1.4-8.8 seconds; one-second slide down; blank from 9.8-10 seconds. The orbital dot travels gently during the hold. No flashing, bounce, cursor, fake subscribed state or bell animation. No alpha fades against green; movement takes the panel outside the frame.

Put it on a separate video track. Trim the blank head/tail if desired. Reposition/scale as needed for the scene; avoid covering the main subject. Use sparingly in an ambient video. Do not bake it into the short scene loop and repeat it throughout a long upload.

## Reproduce

From repository root, with Python, Pillow, NumPy, OpenCV and imageio-ffmpeg installed:

```powershell
python scripts/render_subscribe_banner.py --output final/channel-assets/subscribe-v2
```

Rendering protects existing video destinations. `--still-only` exports design samples without a video render. Both delivery formats and the preview share one graphic/timeline. The renderer constructs native text and shapes; no image-generation service or paid API is used.

Encoder reference: [FFmpeg ProRes documentation](https://ffmpeg.org/ffmpeg-codecs.html). Alpha export uses `prores_ks`, profile 4 (4444), `yuva444p10le`, and 16-bit alpha storage. Actual alpha is decoded and tested in the render script; compatibility still depends on the target editor.
