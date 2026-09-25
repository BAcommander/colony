# Glacier Sanctuary v5 — reflection-based water and upper lantern

User asked to investigate more realistic water and add a brighter obvious on/off light at the dome top. Preserve previously accepted fog, snow and roof smoke; keep existing path lights and annex event.

## Research and decision
NVIDIA GPU Gems Chapter1, Effective Water Simulation from Physical Models: https://developer.nvidia.com/gpugems/gpugems/part-i-natural-effects/chapter-1-effective-water-simulation-physical-models
The guide describes combined directional waves and surface normals for water shading/reflections. Adapt that principle locally: five crossing wave components, perspective-compressed distance coordinates, slope-driven small image remapping and restrained lighting response. Remove the previous additive traveling brightness bands. Preserve the original water color and reflected sky. This is a2D reflection approximation, not a physically reconstructed3D lake or fluid simulation. A3D water surface/environment reconstruction would provide more physical control but requires new scene geometry and reflection reconstruction; not needed for this bounded free local test.

## Water
Wave directions, wavelengths, weights and integer temporal cycles are in scene-plan-v5.json. Use slopes to move the photographed reflection by small source-pixel offsets; scale toward the foreground. Keep ice and shore masks with safety margins. Restrict brightness response to existing reflected light and cap its strength. No regular horizontal brightness bands, foam, moving ice or global light pulsing. Judge natural reflection distortion at full-frame normal speed; do not equate large amplitude with realism.

## Dome lantern
Use existing upper windows, not a new fixture. Warm glow centered342,219, radius24, strength72. Bright state retains glass detail; two source-mapped window masks dim nearly fully. Event begins1s, holds3.5s including0.8s transitions, then returns. Halo follows the same event and disappears while windows are dim. Dome entrance and architecture remain fixed. No strobe or lens flare.

Eight-second720p30fps silent motion study. Render isolated water and dome_light plus combined. Full final looping remains pending. Research does not establish visual success: record user review separately.

Reproduce: python scripts/render_glacier.py --config creative/glacier-sanctuary/animation/scene-plan-v5.json --output creative/glacier-sanctuary/animation/review-v5
