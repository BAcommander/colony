# Farpoint Station v5 — wider weather, no aurora

Latest verdict: star movement was still imperceptible. The user authorized bar removal and requested lower-right cabinet LEDs. No new cloud verdict was given. See [exact feedback](user-feedback-stars-bars-leds-2026-10-07.json) and [v6 delivery](../farpoint-animation-v6/README.md). V5 is superseded and not accepted.

The user rejected v4's sparse planetary coverage, implausible blue glow and imperceptible star changes. See [exact feedback and reference paths](../farpoint-animation-v4/user-feedback-coverage-2026-10-07.json). V5 removes the aurora and adds weather across the central and lower regions.

- [Complete 60-second preview](farpoint-station-v5-preview-60s.mp4)
- [180-second review: three exact repetitions](farpoint-station-v5-three-loops-180s.mp4)
- [Delivery record](delivery-v5.json)
- [Configuration](scene-plan-v5.json)

Silent, 1280x720, 30 fps. User requested changes; see the current verdict above. The assistant inspected full-size temporal/decoded stills and masks, not continuous playback.

## Changes

The existing upper weather retains its speed. Three additional broken cloud fronts cross the central plain and lower hemisphere along the planet's curvature. Their edges and clear gaps make transport identifiable in the samples. Terrain positions and crater geometry stay fixed; cloud opacity can pass over them.

The additional clouds are synthesized procedural texture with local light/shadow compositing. They are not recovered detail from the original artwork or a physical simulation. Two seamless texture fields move forward at different rates, returning after sixty seconds. Their mixture evolves the cloud shapes. The first wide-field trial was too diffuse and read as haze; the final candidate uses a narrower density transition and distinct cloud patches. The original limb and solid geometry are protected.

The rejected aurora is absent from the active layers. No replacement coloured glow was added.

Six original stars have stronger, independent, smooth brightness changes over 10–20 seconds. Their positions and original footprints stay fixed; most stars are unchanged. This is cinematic variation, not starfield drift. Its amplitude is checked in the decoded 720p test.

The monitor, window holds, LEDs, desk lamp, connected amber reflections, original moving clouds, lower cloud patch and storms retain v4 exactly at sampled times. This preservation does not imply user approval of those elements.

## Evidence and scope

- analytic-validation.json: exact sampled v4 layer retention at 0/7/20/40/54 seconds, source protection, finite pixels, periodic states, per-layer seam gates and distinct 0/20/40 states.
- isolated-validation.json: full decoding/timestamps for separate ten-second full-composition weather and star tests at actual strength.
- preview-validation.json: full 1,800/5,400-frame decoding, sequential timestamps, encoded regional/composite seams, no duplicate endpoint and exact three-cycle identity.
- coverage-star-validation.json: weather activity in six named regions through the final third, original-star brightness ranges in the encoded 720p test, and video-only streams.
- visual-review.json: actual inspection and pending user verdict.

Immutable source: final/10-nightward-station/artwork-v3-close-world-leds.png, native 1672x941, SHA-256 9728b8a9baa773365b2eff1a7b0bb030836050f02309e4a04e29bae6d2104c4b. V1–v4 art, code, configurations and videos are preserved. Fingerprints include source, configuration, inherited code/configurations, shared dependencies and raw masks.

Numerical coverage does not prove natural clouds or successful star visibility. Review the actual complete preview before accepting this version. Export 4K only after acceptance, with the same motion and disclosed source upscaling. No music, long assembly, paid services, model installation or remote backup in this pass.

## Reproduction

Run from C:/Colony with the saved configuration:

~~~powershell
python music/farpoint-animation-v5/render_farpoint_v5.py --stage samples
python music/farpoint-animation-v5/render_farpoint_v5.py --stage isolated
python music/farpoint-animation-v5/render_farpoint_v5.py --stage preview
python music/farpoint-animation-v5/audit_delivery.py
~~~

Video destinations refuse overwrite. Choose new names for later revisions. The plan stage records configuration construction; routine rendering reads the saved JSON. Local Python/NumPy/OpenCV/Pillow/FFmpeg only.
