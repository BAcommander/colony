# Farpoint Station — animation v1

2026-10-07. First animation candidate for catalog 10. **Planet motion rejected by the user as effectively invisible.** Exact feedback is saved in `user-feedback-2026-10-07.json`. Numeric checks below describe the historical delivery, not artistic acceptance. Continue with the [v2 forward motion test](../farpoint-animation-v2/README.md).

- [Twenty-second silent 720p preview](farpoint-station-v1-preview-20s.mp4)
- [Sixty-second review: three repetitions](farpoint-station-v1-three-loops-60s.mp4)
- [Production prompt](../../final/10-nightward-station/animation-prompt-v1.txt)
- [Source-bound scene configuration](scene-plan-v1.json)
- [Delivery evidence](delivery-v1.json)

The immutable source is `final/10-nightward-station/artwork-v3-close-world-leds.png`, 1672x941, SHA-256 `9728b8a9baa773365b2eff1a7b0bb030836050f02309e4a04e29bae6d2104c4b`. The camera, limb, stars, white station and dark cabin retain their composition. Blue and pink accents remain steady. The source file is never edited.

## Visible effects

Pale cloud radiance is extracted from three mapped planetary regions, separated from a locally reconstructed stationary terrain plate, and transported along arcs around the planet's fitted centre. The upper cloud band advances right; the central diagonal wisps advance up/right; the right-hand formation travels mainly right. Distance toward the limb reduces apparent speed. Original geometry outside the active regions remains exact before resizing/encoding. Terrain positions inside cloud regions are fixed, but cloud removal reconstructs obscured colour/detail; this is an optical approximation, not recovered ground truth or planetary rotation.

A thinner blurred atmospheric layer travels independently at lower strength. Two overlapping locally staggered lifetimes keep transport moving forward through the twenty-second boundary. Blending may soften fine cloud detail, so cloud edges and apparent motion at the join are explicit user review points.

The left habitat window dims from 3.4 seconds for 5.8 seconds; the middle window's 4.8-second event starts at 17.6 seconds and wraps through the join. The narrow right window remains steady. Separate pane masks include bright cores; warm divider reflections and small local spill dim with the panes. Forced-dark crops exposed initial bright border strips, which were corrected with source-coordinate mapping and supersampled masks before delivery.

The original station diagram gains a small travelling marker and sequential node acknowledgements. A narrow status region scrolls inside a perspective transform; the bezel, chair occlusion and original display layout remain fixed. The desk light has one brief dip around 12.7 seconds, including its whole emitting tube, halo and nearby desk spill. No identifiable exterior vent justified exhaust.

## Review and validation

The isolated clips cover eight seconds each at actual strength, full composition and 720p: [clouds](clouds-isolated-v1-8s.mp4), [veil](veil-isolated-v1-8s.mp4), [habitation](habitation-isolated-v1-8s.mp4). The habitation excerpt covers early window and screen activity; the later lamp dip is covered by source samples and the complete preview. `lamp-temporal.png` includes the dim state at 12.95 seconds.

See `analytic-validation.json`, `coverage-validation.json`, `isolated-validation.json` and `preview-validation.json` for actual results, hashes and scope. The renderer asserts exact source protection on every generated frame. Analytic endpoint and sampled seam comparisons are separate from encoded regional/composite seam checks. Every delivered frame is decoded and its timestamp checked; the review's three decoded cycles are compared exactly.

Assistant inspection covers source crops, extraction/reconstruction, masks, forced-dark windows, temporal samples and decoded stills. Continuous playback was not inspected. Numeric checks and still inspection do not establish user acceptance or prove natural motion. Review the planetary cloud travel at normal size/speed, the right-hand cloud edge, window transitions, small monitor details and lamp dip.

The first veil test did not survive 8-bit quantization. That failed test and its configuration/code are preserved in `history/initial-veil-invisible/`. The delivered candidate increases the veil's speed from 0.52 to 0.8 source pixels/second and gain from 0.12 to 0.35. Principal cloud rates are unchanged. This is an internal correction, not user feedback.

## Reproduce

From `C:/Colony`, using the installed Python with NumPy, Pillow and OpenCV:

```powershell
python music/farpoint-animation-v1/render_farpoint.py --stage samples
python music/farpoint-animation-v1/render_farpoint.py --stage isolated
python music/farpoint-animation-v1/render_farpoint.py --stage preview
```

Video destinations refuse overwrite. Preserve or version existing exports before an intentional rerender. Configuration fixes all source coordinates, event times and speeds. The adapter reuses `scripts/ambient_effects.py` and Floodplain's encoder; their hashes and its imported water dependency are recorded. Existing scene renderers are unchanged.

Preview: 1280x720, 30 fps, 20 seconds/600 frames, silent. Repeated review: 60 seconds/1,800 frames, three copies of the same twenty-second loop. A genuine sixty-second animation has not been produced. 4K follows preview acceptance and would upscale the native 1672x941 plate. Music and long assembly remain pending. No paid service, generation credit or model installation was used. Media is local and ignored; this session has not committed or pushed the package.
