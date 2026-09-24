# Independent craft overlay test

Authorized by the user on 2026-09-24. Five-second 720p prototype using a separately generated transparent craft, a local deterministic motion path, and native ComfyUI compositing. No video model is used for motion. No paid external service, custom-node install or model download.

## Files

- craft-source.png: original transparent RGBA asset, generated with the built-in image tool; prompt in asset-prompt.md. Alpha extrema 0..255, original dimensions 1983x793. Original generated file also preserved at the tool's output location.
- config.json: source/asset hashes, crop, grade, window polygon, and complete frame-by-frame trajectory.
- comfy-api.json: native LoadImage / RepeatImageBatch / LoadVideo / GetVideoComponents / ImageToMask / ImageCompositeMasked / CreateVideo / SaveVideo graph. A lossless midpoint is also saved for preservation checks.
- craft-test-720p.mp4: main preview, local-only.
- craft-test-comparison.mp4: original left, ComfyUI composite right, local-only.
- window-occlusion-mask.png, midpoint-matte.png, motion-union.png: reusable/checkable masks.
- path-review.jpg, decoded-midpoint.jpg, comfy-midpoint.png: visual review evidence.
- validation.json and result.json: technical measurements and ComfyUI completion record.

## Repeat

Start ComfyUI using scripts/start_comfy.ps1, then run:

```powershell
python scripts/craft_overlay_test.py
python scripts/review_craft_overlay.py
```

The test script authors lossless RGB and grayscale matte videos under .local/ComfyUI/input, submits the graph to localhost, and copies the rendered result here. Those intermediate sequences are rebuildable and excluded from Git. Test outputs are overwritten when deliberately rerunning these same commands; preserve/version this scene folder before artistic revisions.

The path moves from behind the left main-window edge toward the right, shrinking modestly. The path stays above the foreground chair/close rocks; only the window mask is required for this route. Do not reuse this occlusion assumption for routes crossing furniture or terrain. Asset RGB gain is [0.77,0.78,0.80]. Geometry stays rigid; there is no AI-video deformation. ComfyUI compositing/encoding took 6.707 seconds, excluding asset generation and local trajectory preparation.

## Review and limits

Verified 120 decoded frames,24fps,1280x720,exactly5seconds. Lossless ComfyUI midpoint differs by zero values outside its motion mask. Six path samples and the decoded MP4 midpoint were visually inspected; the actual lossless midpoint was compared numerically. No continuous playback review was performed. The original source is preserved.

The craft is clearly displaced across temporal samples, but no claim of user artistic approval is made. This is a rigid 2D cutout with no evolving view angle, cast shadow or glass reflection. It is not a ten-second loop and has no seamless-loop claim. The next decision is whether this independent action fits the desired ambient mood before adding complexity or building a repeatable flight route.
