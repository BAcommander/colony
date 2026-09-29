# Saltline Receiver — principal-motion trial v1

## Current review: sustained distant-dust coverage v5, 2026-09-29

User feedback on v4: “did you tone down the distant fog? i struggle to see it now,”. Audit found no parameter or mask reduction: the encoded distant-dust region is pixel-identical to v3 for all 240 shared frames. However, v4 runs twelve seconds, and its finite forward-moving gusts progressively leave the clear basin without replacement. The per-region source delta falls from 6.22 at the start to 2.66 at the end; this is a coverage diagnostic, not an artistic visibility grade. See `v4-far-visibility-audit.json`.

V5 supplies two staggered incoming gusts as the earlier ones leave view. Original far-dust speed, colour, optical depth, maximum opacity, shape and masks are retained. Local fade-ins hide births; this trial is not a seamless loop. Foreground dust remains absent. Building lights, service-lamp events, cloud parameters and localized sunlight trial stay unchanged. The far layer is exact to v4 through six seconds; later differences are the incoming dust. See `v5-coverage-check.json` for source sample comparisons.

Current review: `saltline-v5-combined-12s.mp4`; numeric/dependency report: `combined-v5-validation.json`. Twelve seconds, 1280×720/30 fps, silent. Full decode/timestamp checks and per-frame protected-source-pixel assertions passed. Assistant inspected full-composition temporal samples; no continuous playback claim. Far-dust v3 look is accepted; v5 replenishment and v4/v5 lights/sunlight still await visual review. No completed loop or 4K final.

## Current review: lighting and sunlight v4, 2026-09-29

User feedback: “far dust is good, foreground looks too much as is fake, did we do anything with the lights on the buildings or the sunlight? can we try?” Acceptance applies to the far-dust look in the v3 eight-second prototype. Foreground v3 dust is rejected and removed from v4. Clouds retain their existing parameters; no separate cloud acceptance is inferred.

V4 adds complete-aperture, independently scheduled events to two foreground rooms and two ridge habitats, leaving the door and other windows steady. Small local spill follows each light; a service lamp has two restrained brief dips. Most lights remain on. Slow fades lead into genuine off holds rather than continuous synchronized pulsing.

A soft passing cloud shadow attenuates the existing sunlit dry crust at the far left. It is confined below the accepted far-dust region and protects equipment. The sun, its halo, ground texture and whole-scene exposure remain fixed. This is an artistic lighting approximation, not a physically simulated cloud/solar path.

Current review clip: `saltline-v4-combined-12s.mp4`, twelve seconds at 720p/30 fps, silent, **not a loop**. The retained far-dust and sky layers were compared pixel-for-pixel at sample times against v3 (`v4-retained-layer-check.json`). Full decode/timestamp and protected-source-pixel checks are in `combined-v4-validation.json`. Native plate remains 1672×941. Assistant inspected source-resolution aperture crops and temporal/decoded stills; no continuous-playback claim. New lights/sunlight await user review; no seamless loop or 4K final yet.

Reproduce with `python render_saltline.py --stage combined --config scene-plan-v4.json` using fresh destinations. Config and masks are scene-bound; originals and old trials stay preserved.

## Current review: textured gusts v3, 2026-09-29

Both previous dust versions were rejected as invisible. Exact second rejection: “right i can't see any dust man on either, ive increase your effort level to high, please stop wasting my time”. V2 is history, not the current review.

V3 changes the method: coherent multiscale dust bodies, broken billowing edges and optical extinction. Near dust now traverses the red foreground service road, where warm illuminated particles contrast with the ground; far dust has darker mineral colouring against the pale basin. The near and far speeds are 38 and 20 source pixels/s. Structure translates with the gust, and each body follows a depth-specific path. Geometry is composited without warping; explicit masks protect habitats, lamp, conduit and dish equipment.

Current single review clip: `saltline-dust-v3-combined-8s.mp4`. It contains both dust depths and the unchanged cloud-transport parameters, at full 1280×720 composition and actual speed. This is an eight-second forward-motion prototype, not a seamless loop. `combined-v3-validation.json` records full decode, timestamps, source-frame protected-pixel assertions and dependency hashes. Assistant inspected unamplified full-composition temporal samples and decoded video frames; continuous playback and user acceptance remain pending.

Config: `scene-plan-v3.json`. New reusable method: `dust_transport.py`. Reproduce with `python render_saltline.py --stage combined --config scene-plan-v3.json` using fresh output destinations. The next step after principal-motion review is a complete loop with supporting lights; no 4K final yet.

## Current review: dust v2, 2026-09-29

User rejected both v1b dust excerpts: “i cant see any dust movement. near or far”. Cloud settings remain unchanged; no cloud acceptance is inferred. V2 replaces the small draft dust patches with wider basin regions and explicit conservative dish/vent exclusions. It uses distinct irregular dust tongues with warm, brighter scattering and varied internal density. Far travel is 12 source pixels/s (96 pixels over eight seconds); near travel is 24 pixels/s (192 pixels). These are revised actual-speed trials, not accepted strengths or loops.

Current clips: `far_dust-transport-v2-8s.mp4` and `near_dust-transport-v2-8s.mp4`. Current config: `scene-plan-v2.json`; numeric report: `isolated-v2-validation.json`. Source-frame protected pixels are checked for every frame, and both clips are fully decoded with sequential timestamps. Full-scene temporal samples inspected by the assistant; continuous playback and user visual verdict remain pending.

Reproduce using `python render_saltline.py --stage isolated --config scene-plan-v2.json --layers far_dust near_dust`, with fresh output names for any rerender. Earlier versions remain preserved as history.

Source selected for animation on 2026-09-29: `final/05-saltline-receiver/artwork-v2-animation.png`; user feedback: “yes lets animate, whats the plan?” Original artwork and preparation remain unchanged.

This source-bound adapter reuses the accepted cloud-transport approach and the existing Floodplain encoder/decode checks. Source coordinates come from Saltline's own draft masks, feathered strictly inward. Every rendered source frame asserts exact preservation outside the active regions.

First review: three isolated eight-second 1280×720/30 fps silent transport excerpts, with `v1b` in the filenames. These are forward-motion prototypes, **not loops**. Sky speed is 2.5 source pixels/s; far dust 8 pixels/s; nearer dust 14 pixels/s. Dust trials use broad structured tongues; current density is a trial, not an accepted strength. Full encoded decoding and sequential timestamps are reported in `isolated-v1b-validation.json`. Source/config/renderer/mask hashes bind the report.

The initial unsuffixed trial is superseded: temporal still inspection caught a copied antenna-feed tip within the draft sky mask. V1b restricts sky transport to above source y=275, clear of all equipment and the sun. Lower sky remains fixed. Original trial media and its report are retained as history, not the current review.

Review visible cloud-edge travel, dust visibility and boundary occlusion at normal speed. Inward mask feathering preserves geometry numerically, but does not establish natural-looking motion. Continuous playback review and user motion acceptance remain pending.

Next: retain or adjust principal transport based on review, add staggered whole-window and restrained service-lamp events, then make a genuine 20-second cycle and three-repeat review. Check per-layer and encoded seams before the 4K export. 4K will be upscaled from 1672×941. No music is included in this motion task.

Reproduce from this directory using the existing local Python installation:

```text
python render_saltline.py --stage isolated
```

Existing destinations are protected against overwrite. Draft videos are local ignored outputs. The current adapter/config are staged here because the chat workspace starts in `music/`; the main production tracker links this record.
