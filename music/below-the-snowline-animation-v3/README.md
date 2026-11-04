# Below the Snowline — V3 animation review

User request, 2026-11-03: make the scene substantially more animated and exciting, then overlay music for a two-minute test. “500%” is creative direction, not a measurable quality claim.

## Review

`Below-the-Snowline-v3-with-V6-audio-2min.mp4` is a continuous 120-second, 1280×720, 30 fps review. This is a new animation candidate, not an approved final or a claim of a seamless two-minute loop. The same original 1672×941 V5 artwork is retained; the preview renders at 720p. Earlier V1/V2 files remain intact.

## Motion

- Source-cloud transport with both sampling and destination exclusions around the satellite dish, skyline and window frame.
- Snow at three depths, changing density and streak length with the selected soundtrack's wind envelope. Broader drifting ravine fog, ridge powder, stronger windborne ledge snow and two anchored vent plumes.
- Two small distant transport silhouettes, visible during 0:24–0:59 and 1:26–1:51. Two walking silhouettes inside the glazed bridge, clipped behind its framing. These are intentional new procedural scene details, not recovered original artwork details.
- A stronger radar sweep with moving contacts, changing telemetry bars, independent instrument/key/window illumination, receiver-lamp activity near the radio event, roof safety beacons and steam from the mug.
- Stationary camera; independent effect timing throughout the two minutes. No old 20-second composite is tiled.

## Audio

Uses 3:00–5:00 of the current two-hour V6 **unfaded lossless master**, including its existing music, radio, wind, creaks, ventilation and snow. Apply the established +0.4 dB listening gain once, plus only a 0.5-second entry and two-second exit fade for this review. No additional SFX overlay, normalization or composition change. The channel intro is not part of this animation test.

Wind enters at 0:08, fades out by 1:20 and returns at 1:48. The first new snow take occurs at approximately 0:44.783–0:54.783. The existing radio call begins around 0:25. These are offsets into this review; the full soundtrack is unchanged.

## Reproduce and verify

`render_v3.py samples` produces stills. `render_v3.py render` renders six contiguous segments in four local worker processes. `finish_review.py` assembles them with `Snowline-V6-review-audio-2min.flac`, decodes all frames/audio, checks timestamps/colour/joins/protected pixels, and compares selected decoded frames to the renderer and the entire AAC soundtrack to the lossless excerpt. Scripts refuse to overwrite existing video; use a fresh cache when rerendering.

The audio excerpt command is recorded in `audio-recipe.json`. `events.json` contains the exact local wind/snow timings. `delivery-validation.json` is written only after the delivery passes. Source art is preserved byte-for-byte. The delivered preview uses QP0 H.264 after RGB-to-BT.709 YUV conversion, avoiding independent lossy-encoder changes at segment boundaries. The first CRF17 test failed the join check and is retained only in the ignored cache; missing primary/transfer tags in the initial assembly were also corrected without changing picture data. Assistant review is of temporal and decoded stills plus technical checks; continuous playback, listening and user artistic approval are not inferred.

No paid generation, upload, final 4K/two-hour export, commit or push is part of this review request. Work stays in the current main checkout.
