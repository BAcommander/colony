# Glacier Sanctuary v8b — replace the failed water approach

User explicitly rejected foreground snow and repeated barely changing water trials. Remove foreground_snow entirely. Preserve distant snowfall, fog, smoke, lantern and exterior/annex lighting.

## Different implementation
Use scripts/water_surface.py ReflectionSurface to reconstruct a continuous moving reflection layer throughout the existing water mask. Inpaint fixed ice and shoreline from the sampled texture so remapping cannot drag duplicate ice into the water. The visible original ice/shore remain protected by the output mask. Preserve source colors, reflection placement and scene composition.

Build a perspective water plane,24 deterministic wind-wave components and per-component dispersive phase velocities. Combine their slopes to remap the reconstructed reflection texture and derive continuous orientation/specular response. Wave scales .65–5 in normalized world units, time scale .2, specular strength34. This replaces old sparse glints and regular brightness bands. It is an art-directed reflection reconstruction on an approximate plane, not a calibrated physical lake simulation.

An internal v8 candidate used excessively broad waves and was rejected in still inspection for blurred patches. V8b uses smaller crossing ripples and less texture smoothing. Keep internal candidates distinct; do not give the user another unchanged-looking result merely because a render completed.

Check full-frame and water-only views, masked boundaries, source ice stability, wave repetition and temporal naturalness. Sampled stills show a visibly different surface pattern. Numerical change is diagnostic, not artistic acceptance. All240 frames of delivered clips must decode. Eight-second motion study; not seamless or final4K. No foreground snow.

Reproduce: python scripts/render_glacier.py --config creative/glacier-sanctuary/animation/scene-plan-v8b.json --output NEW_FOLDER --layers water combined
