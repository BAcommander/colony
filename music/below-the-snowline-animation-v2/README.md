# Below the Snowline — animation v2 and Hoth thumbnail

Responds to the user's v1 verdict: “decent” but needing substantial improvement, with a satellite glitch, more colored and dimming lights, building/interior activity and monitor-side/below-monitor buttons. Exact feedback is in `scene.json`; the reported defect is `user-dish-glitch.png`. “200%” is an ambition, not a measured quality claim.

## Deliverables

- `Below-the-Snowline-v2-preview-20s.mp4`: genuine twenty-second silent 1280×720 / 30 fps loop.
- `Below-the-Snowline-v2-three-loops-60s.mp4`: exact three-repeat review, not a unique minute.
- Three eight-second isolated excerpts: sky, controls and base activity. Excerpts are not seamless deliveries.
- `thumbnail-v2.png` and 1280×720 `thumbnail-v2.jpg`: new Hoth-inspired marketing candidate, using the Spirewatch thumbnail as a typography/layout reference. Exact built-in imagegen prompt in `thumbnail-prompt.txt`. Spirewatch is unnumbered; this scene remains catalog 13. Existing approved thumbnail is preserved.

## Changes

The original dish guard missed the left assembly, feed arm and lower support. The enlarged source-and-destination exclusion removes their pixels from cloud transport. `dish-before-after.png` shows v1 above v2 at 0/4/8/12 seconds. The fix retains the source dish; no generative repair or changed artwork was needed.

Eight red/amber/cyan physical indicators beside and below the displays now illuminate and dim independently. Seven keyboard lights have staggered deeper dips. Existing bridge emitters vary independently, with masks restricted to warm lamp faces. Two small colored habitat displays have traveling readout bands, and the room practical light has a restrained local dip with coupled reflected spill. Original warm-aperture dimming remains. Building activity comes from its lights and equipment, with no moving walls or invented silhouettes.

All retained mist, snow, steam, original radar/readout and habitat-window layers match v1 exactly at five isolated phases. Region-local evaluation accelerates rendering. Combined intermediate layers are rounded at layer boundaries; the resulting final native render is validated directly against encoded YUV, rather than claiming the whole v2 composite is byte-identical to v1. Same 1672×941 source; no 4K delivery yet.

The first v2 light-mask study touched bridge metal and left bright rims around button centers. It was corrected before video; the study is preserved in `history/first-light-masks`. The thumbnail is a generated marketing adaptation with framing/lighting differences and is never used as the animation source.

## Evidence and reproduction

`analytic-validation.json`, `regression-validation.json`, `isolated-validation.json`, `preview-validation.json` and `direct-validation.json` record source/config/code hashes, protected pixels, per-layer loop checks, full decoding/timing, regional and quiet-neighbor seams, exact repeats and native-to-decoded comparisons. The assistant inspected source masks and temporal/decoded stills, not continuous playback. User motion and thumbnail approval remain pending.

Use Python with NumPy/Pillow/OpenCV and FFmpeg/ffprobe on PATH. `render.py samples`, `render.py isolated`, `render.py preview`, then `verify_direct.py`, in a fresh copy with no existing MP4s. The renderer refuses to overwrite video. `baseline.py` preserves v1 effect math with local cloud coordinates; `scene.json` contains the effective new settings. `prepare.py` records initial setup and should not be rerun on the delivered package. `audit.py` optionally uses the preserved sibling v1 workspace for comparisons; it is not needed to render v2. No new installs, soundtrack, opening, commit or push.
