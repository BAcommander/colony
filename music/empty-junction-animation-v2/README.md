# The Empty Junction — animation v2

Complete 60-second silent 1280x720/30 fps improvement candidate. User called v1 decent but requested a much stronger scene; this pass implements the proposed environmental and lighting improvements. User reviewed v2 as okay but still too static. The current [v3 candidate](../empty-junction-animation-v3/README.md) adds nearer motion. V2 remains preserved, without full artistic approval.

- [Full minute](empty-junction-v2-preview-60s.mp4)
- [Three-minute join review](empty-junction-v2-three-loops-180s.mp4)
- [Delivery and fingerprints](delivery-v2.json)
- [Configuration](scene-plan-v2.json)
- [Historical v1](../empty-junction-animation-v1/README.md)

## Changes

A broader, broken blue-grey cloud bank travels rightward above the mineral pass at 3.4 native pixels/second. The original source-cloud transport remains below it, with its original speeds and protected skyline. Seeded multiscale optical density supplies the new bank; it is a deliberate procedural addition, not cloud detail recovered from the photograph. The warm horizon remains open.

Far mist reaches higher around the central spire bases, alternately veiling and revealing them. Side-cutting wisps retain separate routes and timing. Each parcel changes thickness, internal texture and edge shape as it advances; far/side speeds are 3.0/4.2 native pixels/second. Staggered sixty-second lifetimes fade each parcel to zero at renewal. The weather is a 2D approximation, not a physical fluid simulation.

Door-lamp dips are softer (35–44 percent), while the warm doorway and illuminated step spill have stronger coupling to the same state. Existing hall/gallery/upper-room holds are three seconds longer, with slower transitions. Cabin-window, roof amber, yard and path-light layers remain sample-exact to v1. Several windows and lamps stay steady.

An optional 4.5-percent twilight-shading still study is retained as twilight-shading-study-maximum.png, but omitted from the animation. It contributed little at full composition; diffuse twilight did not support an emphatic moving shadow.

The original artwork, mineral geometry, rails, parked wagons, camera and foreground remain fixed. No new hardware, moving train, screen, aurora or foreground precipitation. Fine turnout details remain as supplied by the approved art; no engineering-accuracy claim.

## Source and implementation

Immutable source: final/11-empty-junction/artwork-v2.png, 1672x941, SHA-256 ed7b02777c1dcc35504bc0628739688b56515f09ece89d58f299f2dd6013a4be.

render_junction_v2.py subclasses v1 for source mapping, protected geometry, lights, encoding and validation. New environmental logic lives in EvolvingField; scene-specific values live in scene-plan-v2.json. The original renderer, configuration, source and media remain unchanged. A single deterministic sixty-second clock drives every effect. The review repeats the entire unique minute exactly three times.

## Review and evidence

The assistant inspected normal-size temporal/decoded stills, masks, forced-dim and actual light states. Continuous playback was unavailable. The broad cloud bank is intentionally more prominent than v1; naturalness, pacing and perceived improvement remain for user playback review.

- analytic-validation.json: finite pixels, periodic layer states, seam steps and velocity diagnostics, unique 0/20/40-second states, exact native protection.
- isolated-validation.json: three full-composition ten-second clips at actual strength and speed.
- retained-and-light-validation.json: unchanged v1 dependency hashes, identical sky mask, five retained lighting layers and coupled emitter/door/tread samples.
- coverage-delivery-validation.json: five weather regions throughout the minute, fixed structural areas, encoded source-cloud transport, light states and silent streams.
- preview-validation.json: all 1,800/5,400 frames decoded, sequential timestamps, no duplicate endpoint, unchanged regional/composite seam limits and three identical decoded repetitions.

Numeric coverage and tracking do not establish artistic acceptance. Source/config/code/dependency/native-mask hashes bind the evidence. The tread diagnostic originally sampled a dark riser at y725; it was corrected to the visibly illuminated tread at y735 without changing the renderer.

## Reproduction

From C:/Colony, with existing pinned dependencies and saved configuration:

~~~powershell
python music/empty-junction-animation-v2/render_junction_v2.py --stage samples
python music/empty-junction-animation-v2/render_junction_v2.py --stage isolated
python music/empty-junction-animation-v2/review_checks.py
python music/empty-junction-animation-v2/audit_delivery.py --preflight
python music/empty-junction-animation-v2/render_junction_v2.py --stage preview
python music/empty-junction-animation-v2/audit_delivery.py
~~~

Video destinations refuse overwrite. Reproduce in a separate checkout without existing outputs, or version the destination. build_plan.py records configuration construction; ordinary reproduction uses the saved JSON. finish_records.py updates the current project records only after every validation fingerprint agrees.

Local Python/NumPy/OpenCV/Pillow/FFmpeg; no paid tools or new models. No music, assembly, commit/push or remote backup in this pass. Export the 3840x2160/30 fps silent minute only after full-preview acceptance, using identical motion and disclosing upscaling from 1672x941.
