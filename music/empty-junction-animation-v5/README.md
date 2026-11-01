# The Empty Junction — windows and atmosphere rebuild, v5

V4 failed the user's visual review: “window masking is poor, clouds are poor, mist is poor we've made lots of these by now we need a drastic improvement”. V5 is a new review candidate, not an approved final animation.

## Review

- [One minute with the approved audio](Empty-Junction-v5-with-approved-audio-60s-720p.mp4).
- [Twenty-second matching detail comparison, V4 left / V5 right](Empty-Junction-v4-v5-details-20s.mp4). Rows show clouds, valley mist and gallery panes. Both sides use the same time, crop and enlargement; no contrast amplification.
- [Silent minute](Empty-Junction-v5-60s-720p.mp4) and [two exact repeats](Empty-Junction-v5-two-loops-120s-720p.mp4).

## What changed

Twenty-one complete pane masks replace the partial window rectangles: nine gallery panes, nine freight-hall apertures, two upper-room windows and the cabin door glass. Perspective-traced apertures include their light cores; separate warm-emission and white-core selection protects dark mullions without excluding white lamps. Dimming removes the emissive contribution while keeping a cool ambient floor. Pane events use unequal holds and unordered starts; five practical-lamp timings remain from V4.

The sky now transports the photographed cloud texture rather than adding residual sprites over the static photographed clouds. A refined silhouette separates sky from rock. Conservative sky samples fit only the slow illumination gradient; the tighter sky matte supplies the real cloud detail. Two-dimensional inpainting extends atmospheric texture behind hidden regions. Sustained forward travel lasts fifty seconds before a ten-second renewal to the next transported phase. This is a procedural approximation: renewal can soften/double cloud detail briefly and is part of the playback review.

Two new mist fields travel at different speeds through far and middle valley depths. Multiscale density and spatial curl break up the flow; explicit ridge silhouettes occlude it. The previous narrow terrain-flow stripe is removed. Cabin condensation and wind-timed near-ground powder retain the previous render methods and parameters. No new props, moving train, camera movement or paid generation.

Early internal sky studies were rejected before encoding: loose source sampling carried rock edges, and scanline interpolation smeared cloud details into horizontal bands. The delivered candidate uses the corrected two-dimensional texture extension. Enlarged temporal pane/sky/mist samples were inspected before the minute render.

A render was stopped when explicit brightest-pixel controls exposed white lamp cores missed by the warm-colour gate. The aborted file and earlier renderer are retained under history/white-core-correction/. The corrected candidate passes five exact core-coverage controls in [white-core-validation.json](white-core-validation.json); the gallery peak-dim samples were inspected again before restarting.

Two further internal checkpoints were stopped before delivery: foreground utility-mast protection was added to the mist, and equal continuously crossfaded transports were replaced with long forward travel and brief, staggered renewals. The equal-phase implementation could hover/soften around a fixed centre and repeated its cloud state at thirty seconds. The delivered cloud field has distinct zero/thirty-second states; a source-texture tracking diagnostic is saved separately. Aborted checkpoints remain in history/.

## Scope and checks

The source remains the exact 1672×941 artwork v3, SHA-256 `44bd1465510494ed91bc54c9461cb77da590179cb708c6dd21fcd6a6b51f8ba8`. Preview is downsampled to 1280×720/30 fps. The minute includes the active wind phase. This is a motion review; the later quiet units and scheduled final assembly have not been rebuilt in V5.

See [delivery-v5.json](delivery-v5.json) for complete frame/timestamp decoding, regional and quiet-neighbour seams, exact repeated picture sequence, six exact direct native-to-decoded YUV comparisons, and the complete AAC-to-approved-source audio comparison. The review minute uses H.264 QP0 after a CRF16 trial introduced an encoded brightness step at the join despite continuous native frames. The rejected compression trial and source comparisons remain in history/ and initial-encoding-source-controls.json. Native pixels outside effect masks are asserted unchanged during rendering. [Analytical checks](analytic-validation.json), [apertures](apertures.json), masks, temporal/decoded stills and exact dependency snapshots are retained.

The first sixty seconds of the approved V3 audio are used without new gain, EQ or fade processing; AAC encoding is the only audio change. This excerpt contains wind but precedes the first train and grit events. The complete approved hour is unchanged.

Assistant inspection covers temporal stills and decoded detail comparisons, not continuous playback. Technical checks are not visual approval. V4 and earlier media/artwork remain intact. No final 4K/hour video, upload, commit, push or remote backup is claimed.

Reproduce in a fresh copy with the recorded dependencies and existing Python/NumPy/OpenCV/Pillow/FFmpeg: `render_v5.py --stage samples`, `render_v5.py --stage render --seconds 60`, then `validate_v5.py`. Rendered outputs refuse overwrite.
