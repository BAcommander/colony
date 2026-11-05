# Scene16/17 first-draft assets

Built-in imagegen supplied three assets for the authorized visual build: a Gate Camp cleanup plate, a clean background beneath the city plant, and a transparent expedition rover. Exact requests and returned paths are in the three `*-generation.json` records. Original generated PNGs and source references are preserved.

The full generated Gate Camp image is not the new scene source. `prepare_assets.py` consumes only the confined left mug-handle patch to make `../gate-camp-animation-v3/artwork-v2-mug-repair.png`; every original source pixel outside that footprint is asserted unchanged. Rope and scrub backfill is consumed only under their movable cutouts. The city generated background is resized/aligned to the original plant crop and consumed only under two original leaf masks. The rest of the art is preserved.

The rover raw alpha range is0–254. Cropping uses alpha coverage and retains the actual RGBA result. Rendering resamples premultiplied colour/coverage, then applies scene exposure, body placement, contact shadow and foreground occlusion. Its approach/parking/reverse animation is an experiment for visual review, not an approved scene element or an authentic franchise vehicle.

`asset-preparation.json` records dimensions/hashes and geometry. Do not rerun preparation over a later approved source without a new version. No paid API, source-audio upload or new model install was used.
