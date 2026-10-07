# Farpoint Station — minute completion candidate

Latest verdict: the user rejected sparse planetary coverage, the blue glow and invisible star changes. V4 is not accepted. See [feedback](user-feedback-coverage-2026-10-07.json) and the [v5 revision](../farpoint-animation-v5/README.md).

The user invoked `FARPOINT STATION — FINISH THE SCENE` on 2026-10-07, authorizing the saved completion prompt. V2 cloud visibility was confirmed by the user. V3's extra clouds/shadows did not establish a separate planetary phenomenon for them. This version implements the requested aurora, storm illumination, stars, connected reflections and genuine minute timing. Its new look requires user playback review.

## Review delivery

- [60-second silent 720p preview](farpoint-station-v4-preview-60s.mp4)
- [180-second review: three exact minute repetitions](farpoint-station-v4-three-loops-180s.mp4)
- [Delivery evidence](delivery-v4.json)
- [Scene configuration](scene-plan-v4.json)

Watch the blue-green folds along the darker left limb; they move along the arc and change height. Principal cloud detail travels forward over fixed terrain. Three soft cloud-local storm events occur around 11.2, 36.5 and 52.8 seconds. Six original stars vary gently without moving. The original amber glass streaks dim with the warm desk lamp at 12.7 and 44.2 seconds. The monitor retains its schematic, moving marker, small dial and log; instruments and habitat windows have independent activity and quiet holds.

## Timing and preservation

This is a unique sixty-second timeline, not repeated/stretched prototypes. The cloud extraction, stationary reconstructed terrain, optical premultiplication and velocity field are identical to v3/v2. Six spatially separate feathered formations travel directly at those velocities, with staggered sixty-second lifetimes and five-second local appearance/disappearance intervals. Resets occur at zero opacity. Nearby copies of the whole cloud field are not blended. Because local formations now have different ages, the composite cloud arrangement differs from the forward prototypes; preservation means their source separation, character and travel rates, not pixel-identical cloud frames.

The lower cloud has two separate thirty-second formation lifetimes at its v3 speed. Its foreground crater exclusion is retained. The supporting veil uses the existing twenty-second field at unchanged speed. Cloud terrain reconstruction remains a 2D approximation. The aurora and star phases close over a minute. Monitor speed adjustments are recorded in `loop_speed_changes`; the main marker/log keep their twenty-second cycle. Window and indicator events span the full minute, including a window hold through the join.

Source: `final/10-nightward-station/artwork-v3-close-world-leds.png`, native 1672x941, SHA-256 `9728b8a9baa773365b2eff1a7b0bb030836050f02309e4a04e29bae6d2104c4b`. Camera, solid geometry, terrain positions and original limb remain fixed. V1–v3 renderers, configurations, art and videos are preserved. The aurora is fictional world-building; star variation is a cinematic choice. The original artwork does not establish the amber streaks' emitter; connecting them to the desk light is an artistic interpretation.

## Inspection and gates

The assistant inspected source, actual-strength 720p temporal/decoded stills, masks and forced-dark states. Continuous playback was not available. The first evenly spaced auroral draft was revised before delivery to irregularly spaced, curved, softened filaments with gaps. Forced-dark reflection inspection exposed rectangular glass darkening; the corrected core mask follows source brightness and includes white cores. Technical evidence and user acceptance are separate.

`analytic-validation.json` covers per-layer periodic states, unchanged seam thresholds, exact retained arrays and distinct 0/20/40-second states. `preview-validation.json` covers every decoded frame and timestamp, regional/composite encoded seams, no duplicate endpoint and exact three-cycle decoded identity. `supplemental-validation.json` records video-only streams, effect coverage in the final third, retained masks and adjacent motion through the join. Source protection and finite pixels are asserted on every rendered source frame. Fingerprints include source, configuration, inherited code/configuration, shared dependencies and raw float32 masks.

The initial four isolated clips are preserved with `isolated-validation.json` and `renderer-before-reflection-mask-correction.py`. The two affected habitation/reflection clips were rerendered after that correction; use `corrected-isolated-validation.json` for their current versions. The aurora/storm and planet-only results were unaffected by this local mask change. The complete minute uses the corrected renderer.

After the user's acceptance of this complete preview, export a 3840x2160/30fps silent minute with identical motion settings, disclose upscaling and validate it again. No 4K acceptance, music, assembly, publication, commit/push or remote backup is implied by this preview delivery.

## Reproduction

From `C:/Colony`, using the saved configuration:

```powershell
python music/farpoint-animation-v4/render_farpoint_v4.py --stage samples
python music/farpoint-animation-v4/render_farpoint_v4.py --stage isolated
python music/farpoint-animation-v4/review_reflection_fix.py
python music/farpoint-animation-v4/render_farpoint_v4.py --stage preview
python music/farpoint-animation-v4/audit_delivery.py
```

Video destinations refuse overwrite. Preserve existing deliveries before choosing new output names. `prepare_plan.py` records configuration construction; routine rendering reads `scene-plan-v4.json`. Local NumPy, OpenCV, Pillow and FFmpeg only; no paid service or model installation.
