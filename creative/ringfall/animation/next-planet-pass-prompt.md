# Next experiment: isolated planetary atmosphere

Status: planned, not implemented or validated. This is the next local production task, not a request to generate another full-frame video. The user has requested documentation and Git publication first.

## Execution prompt for Codex

Read AGENTS.md, creative/ANIMATION_WORKFLOW.md and the Wan test findings before starting. Build a reproducible regional-motion experiment for Ringfall using free local ComfyUI + Wan2.2 TI2V-5B and local compositing. Use creative/ringfall/04-laptop-refined.png as the immutable master. Preserve all existing assets and write new versioned outputs.

The single goal of this experiment is convincing, clearly visible cloud-band movement on the planet at normal full-scene viewing size. Do not regenerate the room or add other effects yet. Extract a planet crop with sufficient context, recording its exact source coordinates and scale. Create and visually check an atmosphere mask inset from the silhouette, with explicit exclusions for foreground rings, terrain, window frames and any other occluders. Reuse existing v6 masks only after inspecting their accuracy. Feather into protected boundaries without admitting generated edges.

Generate a short atmosphere-motion candidate from that crop using the model prompt below. Start near the successful local benchmark budget: roughly 81 frames at 24 fps, 20 steps, uni_pc/simple, CFG 5, shift 8. Choose crop dimensions supported by the node and preserve aspect ratio by documented padding rather than stretching. Record seed, dimensions, settings, elapsed time and raw output. These settings are a starting point, not proven optimal for cropped generation.

Inspect generated camera drift, cloud flow, texture boiling and ring contamination before compositing. If a small rigid drift can be registered reliably, stabilize the patch to the reference and record the transform. Reject nonlinear deformation or unstable illumination rather than disguising it with opacity. Composite only accepted atmospheric pixels through the checked mask onto the original image. Preserve original foreground rings, silhouette and every pixel outside the motion mask before encoding. Generated ring deformation must not leak into the atmosphere beside the excluded rings.

Render a short full-scene preview at 1280x720 and a side-by-side original/animated review clip. Motion must be noticeable within two seconds at normal size, coherent along the cloud bands, and calm rather than boiling or sliding like a flat decal. Inspect full-scene temporal samples and playback when available; state exactly what was reviewed. Check mask leakage separately from artistic quality. Make at most two targeted candidates in this initial experiment; record any failure and the specific next adjustment instead of producing many unreviewed versions.

Deliver the best preview with an honest pass/fail assessment, reusable crop/mask configuration, ComfyUI API graph, generation prompt, seed, model hashes, render command and report. Update AGENTS.md and PROJECT.md with what actually worked. Do not call this short test a seamless ten-second loop or upscale it to 4K as a substitute for visual success.

If the atmosphere approach passes review, the subsequent phase is to build a ten-second loop for this region, then add controlled local mug steam and laptop animation. Generated footage requires an inspected region-only transition; a prompt cannot guarantee a loop. Reject ghosting or speed jumps. Never reverse the whole video or dissolve the whole frame. Final delivery is 3840x2160, exactly ten seconds, 30 fps/300 frames, silent, with source upscaling disclosed.

## Positive prompt for Wan — planet crop only

A stationary close view of a ringed gas giant. Broad cream and ochre atmospheric bands flow steadily along their existing horizontal paths. Soft cloud formations roll and curl within the bands with visible, unhurried motion and small evolving eddies. The atmosphere remains attached to the curved planet, with stable natural shading and consistent fine cloud texture. The planet's outline, position, rings and background remain fixed. Locked camera, constant exposure, realistic restrained contrast, continuous shot.

## Negative prompt

Camera motion, zoom, pan, wobble, rotating planet silhouette, shifting rings, bending rings, expanding planet, texture boiling, melting, smeared clouds, flat sliding decal, sudden storms, lightning, glowing effects, exposure pulsing, light beams, added moons, added objects, text, watermark, cuts, fades.

## Important boundary

The mask and compositor enforce protected geometry. Prompt instructions alone do not enforce it. Regional AI motion remains an experiment; neither full-frame Wan test established acceptable geometry preservation.
