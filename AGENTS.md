# Ambient Colony — working instructions

## Current authority and approved result

On 2026-09-24 the user approved Ringfall v9b: "finally good". Use it as the quality and workflow baseline for future scenes. This supersedes all historical pending-review and failed-experiment directions. Read creative/ANIMATION_WORKFLOW.md before starting an animation; PROJECT.md contains project context. Full prior instructions are archived in creative/history/animation-learning-log-through-v9b-2026-09-24.md.

Approved master: creative/ringfall/04-laptop-refined.png. Approved animation: creative/ringfall/animation/ringfall-ambient-v9b-20s-final.mp4. Renderer: scripts/render_ringfall_v9.py. Creative brief: creative/ringfall/animation/ambient-v9-final-brief.md. Acceptance/provenance: creative/ringfall/animation/approved-v9b.json.

## Defaults and authorization

Current next scene (2026-09-25): Basalt Transmission, source creative/concepts/09-basalt-transmission.png. Detailed execution brief: creative/basalt-transmission/animation/production-prompt-v1.md; source hash and provisional plan: scene-plan-v1.json beside it. User requested a detailed prompt for a twenty-minute video. Current interpretation: a twenty-second loop repeated sixty times, 1200 seconds/36000 frames at30fps, silent until music is supplied. Brief only prepared; no Basalt render exists yet. Map this scene's anchors/masks before implementation. Priorities: roof exhaust, terrain-occluded valley haze, restrained independent room-light states. Source suggests an atmosphere, unlike Ringfall. Keep Ringfall as the approved quality reference. Check long-delivery file size before choosing Git storage.

- Produce local MP4s from this chat. No paid plugins, cloud video services, API fees or separately purchased credits. Built-in image generation and free local tools/models are authorized; do not install another model merely because it exists.
- Requests to build animation mean execute locally. Requests only for a prompt/document mean save and deliver that document without silently rendering.
- Default to a genuine twenty-second loop, 30 fps/600 frames, silent, 1280x720 preview then 3840x2160 final. Follow explicit scene-specific changes. Disclose upscaled source detail.
- Preserve originals and version exports. Do not overwrite approved art/video. Deliver actual media with absolute local paths.
- Record feedback and update current status, not just an ever-growing append-only log. Separate proposals, implementation, numeric verification and user approval.

## Method that worked

Use an immutable source plate plus independent, precisely masked procedural motion layers. Local Python/NumPy/OpenCV and FFmpeg produced the accepted Ringfall; ComfyUI or video diffusion is not required. Reuse working effect logic, encoding and checks. Do not restart experiments that already failed.

Ringfall's successful hierarchy: visible colony vent exhaust and independent window off/on events; coherent material texture traveling along protected ring bands; supporting mug steam, laptop telemetry, planetary cloud detail, ground lights and mast activity. Fixed camera and solid geometry preserve the original image's realism. The user accepts calm, subtle movement when it is readable and unbroken. No spacecraft or new moving focal objects in Ringfall.

For each new still, remap coordinates, masks, light sources and occlusion to that image. Ringfall renderers are currently source-specific (1672x941 assertion and hardcoded coordinates); they are not a generic one-command pipeline. Adapt reusable effect functions and put new scene-specific values in a configuration. Never copy Ringfall coordinates blindly or modify its approved renderer to create a different scene.

## Fast execution sequence

1. Read the approved reference and latest brief. Choose one or two principal motions and a few supporting ones; state concrete visible changes, not percentage improvement promises.
2. Freeze the source and record hash/dimensions. Map source locations, protected geometry, masks and depth order once. Use creative/scene-plan-template.json to capture the plan.
3. Build the largest missing motion first. Keep working supporting effects. Use one scene configuration and shared timing for preview/final; avoid new whole-renderer copies for parameter-only revisions.
4. Inspect full-scene temporal samples and detailed masks, then render one 720p preview. Review playback when available. Fix the specific defect; do not spend many revisions on already-good foreground steam while the background stays static.
5. Apply separate visual and numeric gates from creative/ANIMATION_WORKFLOW.md. A checksum or large pixel delta cannot prove artistic quality. State actual inspection, never claim playback review from still samples.
6. Export 4K after the preview passes available visual checks, validate the encoded file and inspect a decoded frame. Show the MP4 and record the user's verdict. Do not claim 10/10 on their behalf.
7. Update the brief, approved manifest and this file's current state. Commit/push source art, code, configuration, masks, prompts, reports and approved final media. Preserve rejected experiments as history rather than active instructions.

## Specific lessons to carry forward

- v4-v6: only tiny steam/screen/beacon activity was insufficient. Full composition and background movement matter.
- Full-scene and cropped Wan2.2 attempts: deformation, drift, texture artifacts and ring contamination. Masks cannot fix bad pixels inside a generated region. Do not rerun these as the default.
- Craft overlay: compositing worked technically, but user rejected the spacecraft as cheap-looking. More objects did not improve this scene.
- v8: fine brightness modulation on rings was invisible to the user. v9b transports a coherent angular material field inside fixed bands. It is stylized material motion, not physically simulated orbital rotation.
- Exhaust: anchor precisely to vents, evolve internal wisps, expand/dissipate, preserve rooflines and occluders. In vacuum use directed exhaust, not wind or buoyant chimney smoke. Keep sources plausible.
- Lights: stagger real off/on holds; leave steady lights too. Mask the complete aperture, including saturated white cores. Warm-color thresholding alone left white cores lit in the discarded v9 draft. Couple small local spill to lamp state.
- Steam: rising transport should not slow simply because the overall loop gets longer. Clamp sine envelopes before fractional powers to avoid NaNs at floating-point boundaries.
- Loops: use one configured duration everywhere, forward motion through the seam, matching states and velocities, and no duplicate endpoint. Check individual layers and encoded last-to-first steps. Avoid ping-pong, full-frame dissolves and global exposure changes.
- Art first: realistic furniture/materials, a single mug handle, stable geometry, no synthetic clutter. Higher resolution and stronger opacity are not substitutes for believable motion.

## Repository and tooling

Approved v9b MP4 is explicitly tracked by a narrow .gitignore exception at the user's request. Draft videos, .local/ runtimes/weights and caches remain ignored. For future approved finals, check size and repository limits before choosing ordinary Git or a large-file strategy; do not silently omit requested media. Never force-push. Music has not yet been produced.

Python has NumPy, Pillow, OpenCV and imageio-ffmpeg. The Ringfall renderer imports v8, v7, v6 and the core renderer plus scene-v6.json; retain those dependencies. Free ComfyUI/Wan is installed under .local/ for optional future experiments, not the accepted production path. Hardware: RTX 4060 8GB VRAM, approximately 64GB RAM. Keep services on localhost and paid/API nodes disabled.
