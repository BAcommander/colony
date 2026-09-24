# Local animation workflow

## Current direction: regional AI plus local compositing

Use AGENTS.md as the current authority and apply its workflow to each new selected image. This hybrid approach is planned; its first regional AI experiment has not yet been validated. The hand-composited v6 and both full-frame Wan tests failed artistic review.

Keep an immutable master plate. Define one principal motion region and protected geometry. Crop and generate complex organic motion locally, then composite only the accepted area through inspected masks. Preserve foreground occluders from the source. Use procedural methods where placement and repeatability matter, such as mug steam and screen activity. Full-frame Wan generation is not the default: both initial tests changed objects and geometry.

For each scene, record crop coordinates, aspect-preserving padding, registration transforms if any, source hashes, masks, prompt/negative prompt, seed/model/settings, runtime, raw generation and composite command. Inspect the generated region before compositing: masks cannot repair boiling or deformed texture inside the accepted area. Prototype the principal motion alone before adding supporting effects.

Start with a short generation benchmark and a full-scene preview. After visual success, construct a ten-second loop. Generated footage needs a checked region-only transition with no ghosting or speed jump; prompting for a loop is insufficient. Procedural layers use periodic timing. Only then finish at 4K. The next concrete task is [Ringfall's planet pass](ringfall/animation/next-planet-pass-prompt.md).

For future concepts, include plausible, readable motion sources and clear separation from protected objects. Source quality, temporal quality and spatial resolution are separate concerns. Record failures and do not call a method proven until its output passes inspection.

## Defaults

Local generation, compositing and MP4 rendering are the default. Free local models are authorized; no paid plugins, paid external generation or separate credits. Use existing source art and installed local tools. Update AGENTS.md with the active brief and durable user feedback. Keep proposals, implemented features, technically verified results and user-approved results distinct.

## Scene package

Each scene should contain a source image, an animation brief, a versioned motion plan, reusable masks, previews, finals, and a short render report. Record source hash, dimensions, frame rate, duration, render command, renderer version, parameter values and output paths. Keep coordinate data and tunable motion parameters in the scene configuration as the layered implementation develops; avoid copying a whole renderer merely to change an amplitude or output resolution.

## Work in this order

1. **Read feedback and identify the visual failure.** Write a concrete correction, such as "the colony needs visible activity across the ground", not "make it 500% better".
2. **Map the scene into depth and motion layers.** Identify a principal motion region, secondary activity and quiet regions. For Ringfall, the atmosphere and colony are the background priorities. Keep a motion-freeze list for geometry that must remain fixed.
3. **Build the largest missing effect first.** Reuse validated steam and screen work, but do not spend the revision only on those when the user has criticized the background.
4. **Render a lightweight full-scene preview.** Default 1280x720, ten seconds, 30 fps. Render at the draft size, not 4K followed by downsampling. Cache the static plate and prepared masks. Use the same effect logic and time base for preview and final.
5. **Review visual quality before resolution.** Inspect the complete scene at its intended viewing scale and temporal samples across the loop. Use playback when available. Detail crops and change heatmaps diagnose defects; they do not prove that the full shot feels alive. State exactly what was inspected; do not claim playback review from a contact sheet alone.
6. **Check technical continuity separately.** Validate duration, dimensions, decoded frame count, last-to-first position/brightness/motion continuity, and masking invariants. Measure individual layers as well as aggregate changes so one moving region cannot hide a static background. Do not weaken a failing test to label a render seamless.
7. **Iterate on the most important defect.** Change the appropriate layer and render a new preview. Reuse existing checked assets and do not repeat unrelated checks. Ordinary reversible revisions do not require another permission request.
8. **Export once the draft works.** Render 3840x2160 only after the visual draft meets its brief. Keep the same duration, phase, layer order and amplitudes. Validate the encoded final and inspect a decoded full-scene frame. Tell the user if the source was upscaled.
9. **Deliver and capture feedback.** Show the actual MP4. Summarize visible changes and remaining limitations. A technically valid render is not automatically artistically successful; record user criticism as the latest authoritative feedback.

## Two separate quality gates

**Visual gate:** the intended foreground/background activity reads at normal size; hierarchy is calm and convincing; masks and lighting are coherent; the revision addresses the user's actual criticism.

**Technical gate:** duration, frame count, resolution, encoding and seam continuity pass. Static geometry remains fixed and files are reproducible.

Both gates matter. More effects, a larger file, a 4K label, or larger numerical opacity values are not evidence of better art.

## Tooling currently available

`scripts/render_ringfall_v6.py` implements the layered scene: atmosphere detail advection, masked colony work-lights, linked glass reflections, volumetric steam, laptop activity and beacon. Use `--stage preview` or `--stage final`, `--version`, `--qa-only`, and `--only` with one or more layer names. It reuses the prior renderer's foreground and encoding functions. `creative/ringfall/animation/scene-v6.json` contains parameters and mask geometry; `motion-plan-v6.json` records implementation status. Saved reports contain per-layer mask/phase checks and aggregate decoded loop checks. Source image and earlier exports remain intact.
