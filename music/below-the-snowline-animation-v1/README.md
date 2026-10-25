# Below the Snowline — ice-planet animation v1

Twenty-second silent 1280×720 / 30 fps preview from the selected artwork v5 (1672×941). This is a local masked-compositing candidate, not a 3D simulation or a claim of studio production quality.

- `Below-the-Snowline-v1-preview-20s.mp4`: complete loop.
- `Below-the-Snowline-v1-three-loops-60s.mp4`: exact three-repeat seam-review copy, not a unique minute.
- Four eight-second isolated tests: sky, weather, interior and lighting. These excerpts are not seamless deliveries.

## Motion

Forward transport of the original sky texture, three separate drifting powder/mist regions, three scales of exterior snow, six independently timed warm apertures, an original-graphic radar sweep and fading contacts, six separately changing terminal readouts, and anchored steam rising from the mug. Camera, architecture, cannon and dish remain structurally fixed. Snow stays outside the pressure window. The cannon stays idle.

The visible additions are radar activity and coffee steam. No unrelated ships or props were added. Exterior vent exhaust was considered but omitted because the plate lacks an unambiguous exposed outlet. Foreground flakes may cross exterior structures; distant snow is occluded by the bridge. Source cloud sampling excludes the dish and terrain as well as masking the destination.

## Review and provenance

User selected the artwork with “looks good i think” and requested animation plus possible new details. This does not approve the resulting motion. Exact feedback and scene-space coordinates are in `scene.json`. `source.png` is a byte-identical copy of `final/13-below-the-snowline/ice-planet-retheme-v3/artwork-v5.png`.

Methods draw on Icebound v2 snowfall, Cable/Basalt source-cloud transport and Deepwell v3 steam/whole-pane masking. All coordinates were remapped. The first powder study had excessive fine texture; its renderer/config/still are preserved in `history/first-study`. The revised fields use broad periodic Gaussian forms.

The assistant inspected masks, temporal source frames and decoded stills; continuous playback and artistic approval are not claimed. Consult `analytic-validation.json`, `isolated-validation.json`, `preview-validation.json` and `direct-validation.json` for completed checks. No soundtrack, opening, 4K export, commit or push. A future 4K render would be upscaled from native 1672×941 detail using the same scene settings after preview acceptance.

## Reproduce

Requires Python with NumPy, Pillow and OpenCV, plus FFmpeg/ffprobe on PATH. This machine uses the bundled Codex Python and installed OpenCV from `C:/AI/ComfyUI/venv/Lib/site-packages`; no packages/models were installed.

Run `python render.py samples`, `python render.py isolated`, then `python render.py preview` in a fresh copy without existing MP4 outputs. Rendering refuses to overwrite videos. Source/config/renderer/helper hashes and output hashes are in the validation reports and package manifest. Preserve the original package when changing settings.
