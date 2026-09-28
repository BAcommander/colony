# Saltline Receiver — animation production brief v1

Status: prepared 2026-09-28; revised art pending user review. Source: ../artwork-v2-animation.png. Composition is an inhabited radio receiver settlement above a dry salt pan on a Mars-inspired world with an atmosphere.

## Intended result

Make the vast exterior feel quietly alive through upper-sky cloud transport and separately readable middle/far dust veils. Keep all three dishes absolutely stationary, including their rims, support struts and shadows. Preserve red sediment, the solid salt crust, the pressure modules, utility conduit and distant settlement. Supporting movement is independent warm-window activity and one modest service-light change. No spacecraft, dish rotations, liquid salt-pan waves, camera moves or extra machines.

Use Basalt's successful source-texture cloud transport as a reference, starting at 2.5 source pixels/second to the right. Freeze terrain contours and remove the sun and halo from sampled moving texture as well as the output. Upper cloud bands must move recognizably at full composition; do not substitute fine flicker. Local lifetime blending must not produce duplicated cloud edges.

Far dust crosses a broad basin strip at an initial 8 source pixels/second with low density; a separate nearer tongue moves around 14 pixels/second. These are starting trials, not accepted values. Give veils broad internal structure and transparent, irregular edges, not a uniform smoke ribbon. The two layers need different phases and trajectories. Keep low dust on the salt pan behind station equipment, with no dust running through buildings, antenna supports or the roof vent. Source-coordinate masks are conservative clear patches and require edge refinement before expansion. Do not add chimney smoke to compensate for distant inactivity.

Retain enough steady inhabited windows to keep the shelter inviting. Mask whole apertures, use slow independent fades and off holds, and keep practical light spill attached. The salt pan's bright grazing highlight remains a fixed ground texture, not animated as liquid water.

## Production instructions

Read AGENTS.md, creative/ANIMATION_WORKFLOW.md and creative/NEXT_SCENE_RUNBOOK.md. Use the immutable artwork-v2-animation.png named and hashed in scene-plan.json. This is an art candidate; no user approval of this revision or motion is implied. Retain artwork-v1.png and thumbnail-v1 files unchanged. Use local NumPy/OpenCV/FFmpeg, no paid tools or full-scene diffusion.

The JSON is a scene-specific preparation specification, NOT a drop-in config accepted by existing scene renderers. Masks are draft binary regions at 1672x941. Review source-scale edges, protect occluders, then feather inward. Do not blur masks across solid structures. Implement a scene adapter around reusable effect functions rather than copying existing hardcoded scene coordinates. Rebuild masks with `python scripts/build_preparation_masks.py PATH_TO_THIS_DIRECTORY/scene-plan.json` from repo root after changing coordinates. Source hashes are enforced.

First render each principal effect as an isolated eight-second 1280x720/30fps excerpt at actual intended speed, with full static scene behind it. Name one recognizable feature, direction and visible travel. View at 1x; numeric differences alone do not establish visual success. Tune structure, then travel, then density. Keep useful quiet regions. Review the actual frame boundaries against railings, buildings and light apertures. Do not call draft mask generation an animation check.

Once motion reads naturally, add supporting effects and create a genuine 20-second cycle (600 frames, 30fps, silent). Use one timeline for all layers, forward travel with hidden local resets, and constant camera/exposure. No global fades, reversed motion, duplicate endpoint or migrating light pools. Preserve source pixels outside active masks before encoding. Quantized frequencies must retain calm speeds; log speed deviations. If twenty seconds forces unnaturally fast water/cloud movement, compare a longer cycle instead of speeding it up silently.

Review the complete preview and three repeated cycles, check every layer seam and encoded last-to-first motion against normal adjacent frames, decode every frame, then deliver a 3840x2160 export after the preview passes available visual checks. State that native source detail is 1672x941 and the 4K output is resampled. Save configs, mask revisions, code hashes, source hash, exact feedback and numeric reports separately. No animation has been rendered during this preparation task.
