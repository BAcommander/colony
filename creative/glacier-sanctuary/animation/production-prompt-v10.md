# Glacier Sanctuary v10 — half-speed water and refinement research

Request: make water even slower and research additional improvements. Keep the v9 reflection-surface method and all non-water effects.

## Implemented
Time scale .18 -> .09: every wave travels at exactly half its v9 phase velocity. Same seed, directions, wavelengths, contrast and highlight settings. No global video slowdown, so snow, smoke and lamps retain their timing.

Sampling-aware ripple filtering: attenuate a component according to its screen-space phase gradient with a Gaussian footprint of0.75 source pixels. Fine distant components receive more attenuation than broad nearby components. This targets unstable detail rather than reducing the whole water layer's opacity.

Boundary damping: gradually reduce reflection displacement within14 source pixels of the water-mask boundary, down to40% at the edge. It is an artistic mask-distance approximation for calmer margins, not bathymetry or physical shoreline interaction. Source ice/shore remain protected.

## Research and scope
Primary source: NVIDIA GPU Gems Chapter1, Effective Water Simulation from Physical Models: https://developer.nvidia.com/gpugems/gpugems/part-i-natural-effects/chapter-1-effective-water-simulation-physical-models
The source discusses filtering under-sampled waves and controlling wave/reflection behavior with depth. V10 adapts these principles to the existing masked2D reflection surface. No model downloads or paid services.

Secondary reference consulted: Google Filament materials, specular anti-aliasing and roughness: https://github.com/google/filament/blob/main/docs/Materials.md.html
A full physically based reflection system would need real surface/view geometry and an environment representation. Those are absent from the still, so no claim of calibrated Fresnel, true depth or physically accurate ice interaction is made. Keep this as a potential larger reconstruction, not another unsolicited pipeline reset.

Next useful work after visual acceptance: solve continuous looping with commensurate wave periods and gradual atmosphere lifetimes, then check encoded boundaries. Do not use a global dissolve or simply slow the whole scene. This current clip remains an eight-second motion study.

Reproduce: python scripts/render_glacier.py --config creative/glacier-sanctuary/animation/scene-plan-v10.json --output NEW_FOLDER --layers water combined
