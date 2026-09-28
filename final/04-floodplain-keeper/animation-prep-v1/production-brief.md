# Floodplain Keeper — animation production brief v1

Status: prepared 2026-09-28; revised art pending user review. Source: ../artwork-v2-animation.png. Composition is a sheltered water-management control room looking out over an inhabited extraterrestrial floodplain.

## Intended result

Make the exterior feel active and the interior reassuringly still. Primary motion 1 is slow, visible reflection travel across the right-hand open channel. Primary motion 2 is broad cloud transport above the colony. Supporting actions: a slow screen marker, two or three independent distant window transitions, and a gentle mast beacon. Keep the beaker, gauge, chair, lamp and all window frames fixed. Do not add rain, foreground particles or gratuitous steam.

Adapt Glacier's accepted 24-wave reflection reconstruction, using its slow .09 time scale as a trial baseline rather than a promise of the same appearance. Recalibrate the perspective plane, sky reflection sampling and shoreline damping for this small channel. Do not apply Glacier's screen-coordinate equations blindly. Fixed reeds, pipework, gate walls and railings must never become moving reflection samples. Source reflection texture must be cleaned/excluded as well as the output masked. Use broader low-contrast reflected cloud forms, avoid glint showers and wobbling whole-water warps.

Clouds drift right at an initial 2 source pixels/second through both window apertures, sampling a coherent common sky. Exclude the moon and mast from input texture and output. Test cloud overlap for doubled contours. The source now contains stronger cloud shapes; do not add opaque mist just to make changes measurable.

Coordinates in scene-plan.json map five proposed layers. The water regions are conservative patches only: refine around vegetation before expanding them. Lights include the complete illuminated aperture, not just orange pixels; couple any changed window with its small water reflection when that reflection is clearly identifiable. Keep most lights steady.

## Production instructions

Read AGENTS.md, creative/ANIMATION_WORKFLOW.md and creative/NEXT_SCENE_RUNBOOK.md. Use the immutable artwork-v2-animation.png named and hashed in scene-plan.json. This is an art candidate; no user approval of this revision or motion is implied. Retain artwork-v1.png and thumbnail-v1 files unchanged. Use local NumPy/OpenCV/FFmpeg, no paid tools or full-scene diffusion.

The JSON is a scene-specific preparation specification, NOT a drop-in config accepted by existing scene renderers. Masks are draft binary regions at 1672x941. Review source-scale edges, protect occluders, then feather inward. Do not blur masks across solid structures. Implement a scene adapter around reusable effect functions rather than copying existing hardcoded scene coordinates. Rebuild masks with `python scripts/build_preparation_masks.py PATH_TO_THIS_DIRECTORY/scene-plan.json` from repo root after changing coordinates. Source hashes are enforced.

First render each principal effect as an isolated eight-second 1280x720/30fps excerpt at actual intended speed, with full static scene behind it. Name one recognizable feature, direction and visible travel. View at 1x; numeric differences alone do not establish visual success. Tune structure, then travel, then density. Keep useful quiet regions. Review the actual frame boundaries against railings, buildings and light apertures. Do not call draft mask generation an animation check.

Once motion reads naturally, add supporting effects and create a genuine 20-second cycle (600 frames, 30fps, silent). Use one timeline for all layers, forward travel with hidden local resets, and constant camera/exposure. No global fades, reversed motion, duplicate endpoint or migrating light pools. Preserve source pixels outside active masks before encoding. Quantized frequencies must retain calm speeds; log speed deviations. If twenty seconds forces unnaturally fast water/cloud movement, compare a longer cycle instead of speeding it up silently.

Review the complete preview and three repeated cycles, check every layer seam and encoded last-to-first motion against normal adjacent frames, decode every frame, then deliver a 3840x2160 export after the preview passes available visual checks. State that native source detail is 1672x941 and the 4K output is resampled. Save configs, mask revisions, code hashes, source hash, exact feedback and numeric reports separately. No animation has been rendered during this preparation task.
