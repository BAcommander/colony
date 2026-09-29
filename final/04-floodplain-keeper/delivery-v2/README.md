# Floodplain Keeper - editor handoff

2026-09-29: user accepted the v2 look with "then i think we're good" and asked for the files to assemble their next video. The 4K delivery preserves the accepted source, masks, settings and timing without altering the preview renderer or config.

- Video: ../video-4k-v2.mp4 - 3840x2160, 30 fps, 600 frames / 20 seconds, silent H.264 QP0. Upscaled directly from 1672x941 native scene frames using Lanczos; this does not create native 4K detail.
- Audio: ../../../exports/04-floodplain-keeper/Floodplain-Keeper-Shelter-Recovery-1-Hour-v1.mp3 - one hour, stereo MP3. The short join was approved; full-hour listening remains pending.
- Thumbnail: ../thumbnail-v1.jpg - 1280x720. Existing thumbnail review status is unchanged by animation approval.
- Upload text: ../youtube-title.txt, ../description.txt and ../youtube-tags.txt.

Repeat the video loop to fill one hour (180 repeats at normal speed) and place the one-hour audio underneath. Use 30 fps and retain direct joins between video repetitions. The audio already contains its opening and closing fades. No combined video was generated in this handoff.

Reproduce from repository root using the Python/NumPy/Pillow/OpenCV environment documented in ../animation-v1/README.md:

```powershell
python scripts/render_floodplain_delivery.py
```

Existing delivery destinations refuse overwrite. The renderer verifies the accepted v2 fingerprint, generates native frames with protected-pixel assertions, upscales/encodes once, then fully decodes the 4K master and checks each masked region's encoded seam with the same gate as the preview. A sixty-second stream-copy review in exports/04-floodplain-keeper/animation-v2 is fully decoded, with all three payloads compared frame by frame and timestamp continuity checked. Exact hashes and results are in delivery-validation.json.

Assistant inspected a decoded 4K still; no continuous-playback review claimed. Approval applies to the v2 preview look. The short master has an exact Git LFS path; source audio, one-hour soundtrack and repeated review clip remain local ignored exports and require separate backup.
