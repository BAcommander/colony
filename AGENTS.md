# Ambient Colony — working instructions

## Current authority and approved result

On 2026-09-24 the user approved Ringfall v9b: "finally good". Use it as the quality and workflow baseline for future scenes. This supersedes all historical pending-review and failed-experiment directions. Read creative/ANIMATION_WORKFLOW.md before starting an animation; PROJECT.md contains project context. Full prior instructions are archived in creative/history/animation-learning-log-through-v9b-2026-09-24.md.

Approved master: creative/ringfall/04-laptop-refined.png. Approved animation: creative/ringfall/animation/ringfall-ambient-v9b-20s-final.mp4. Renderer: scripts/render_ringfall_v9.py. Creative brief: creative/ringfall/animation/ambient-v9-final-brief.md. Acceptance/provenance: creative/ringfall/animation/approved-v9b.json.

## Defaults and authorization

Current scene (2026-09-25): Glacier Sanctuary v10 look accepted by the user; v11 is its requested sixty-second 4K delivery. Preserve the slow 24-wave reconstructed reflection surface (.09 time scale, sampling filter and boundary damping), distant snow/fog, vent smoke and exterior/upper-lantern light schedules. Foreground snow stays absent. V11 quantizes water frequencies and particle lifetimes for a sixty-second cycle; it is not three copies of a twenty-second clip. Read creative/glacier-sanctuary/animation/README.md and final-v11/delivery-validation.json for actual delivery state. Config: scene-plan-v11.json. Reproduce with scripts/render_glacier_delivery.py; approved destinations are protected from overwrite. User acceptance applies to the v10 look and instruction to finish; technical checks do not claim user review of the new full-length export.

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
4. Render isolated principal layers at full composition with scripts/motion_review.py before combining. Judge recognizable directional travel at 1x/720p; crops and amplified difference maps are diagnostic only. Then render one complete twenty-second preview. Review playback when available. Fix the specific defect; do not spend many revisions on already-good foreground steam while the background stays static.
5. Apply separate visual and numeric gates from creative/ANIMATION_WORKFLOW.md. A checksum or large pixel delta cannot prove artistic quality. State actual inspection, never claim playback review from still samples.
6. Export 4K after the preview passes available visual checks, validate the encoded file and inspect a decoded frame. Show the MP4 and record the user's verdict. Do not claim 10/10 on their behalf.
7. Update the brief, approved manifest and this file's current state. Commit/push source art, code, configuration, masks, prompts, reports and approved final media. Preserve rejected experiments as history rather than active instructions.

## Specific lessons to carry forward

- v4-v6: only tiny steam/screen/beacon activity was insufficient. Full composition and background movement matter.
- Full-scene and cropped Wan2.2 attempts: deformation, drift, texture artifacts and ring contamination. Masks cannot fix bad pixels inside a generated region. Do not rerun these as the default.
- Craft overlay: compositing worked technically, but user rejected the spacecraft as cheap-looking. More objects did not improve this scene.
- Basalt v3 feedback: more opacity in one middle-ground area was too much, not a solution to static far/upper regions. Separate depth layers and redistribute motion. When advecting sky source texture, masking the moon in the output alone is insufficient: exclude it from the texture source too, or copies can drift elsewhere.
- Basalt v2 feedback: numerical motion was not enough; the user still could barely see the background. V3 transports source cloud detail and increases gust travel/scale. Do not repeat tiny modulation adjustments or infer visual acceptance from successful rendering.
- Basalt v1b feedback: merely including haze in the layer list does not mean the background reads as alive. V2 gives wind separate drifting sheets and sky a protected material field. Compare full scenes, retain the earlier version, and record the user verdict instead of declaring success from pixel metrics.
- v8: fine brightness modulation on rings was invisible to the user. v9b transports a coherent angular material field inside fixed bands. It is stylized material motion, not physically simulated orbital rotation.
- Exhaust: anchor precisely to vents, evolve internal wisps, expand/dissipate, preserve rooflines and occluders. In vacuum use directed exhaust, not wind or buoyant chimney smoke. Keep sources plausible.
- Lights: stagger real off/on holds; leave steady lights too. Mask the complete aperture, including saturated white cores. Warm-color thresholding alone left white cores lit in the discarded v9 draft. Couple small local spill to lamp state.
- Steam: rising transport should not slow simply because the overall loop gets longer. Clamp sine envelopes before fractional powers to avoid NaNs at floating-point boundaries.
- Glacier water: sparse glints and tiny image warps repeatedly failed the user. V8b finally read as moving water; v9/v10 calmed the same 24-wave reflection method. Once a method is accepted, preserve it and change speed independently. Use sampling-aware filtering and boundary damping; this remains a 2D approximation, not fluid simulation.
- Extending accepted loops: retain effect speeds; quantize wave frequencies to integer cycles of the requested duration, and particle lifetimes to divisors with invisible resets. Record the speed deviations. Render preview/final from one source-frame pass; validate the encoded join and a repeated-payload preview. A longer loop is not automatically smoother.
- Long deliveries: encode/composite only the short loop, repeat with stream copy, then fully decode-check frame count, sequential timestamps and repeated-frame identity. Test the delivery encode seam separately: Basalt CRF16 caused a seam outlier despite correct duration and low spatial error; QP0 master payload reuse fixed it. Never weaken the seam gate. An assembly success does not prove temporal quality.
- Loops: use one configured duration everywhere, forward motion through the seam, matching states and velocities, and no duplicate endpoint. Check individual layers and encoded last-to-first steps. Avoid ping-pong, full-frame dissolves and global exposure changes.
- Art first: realistic furniture/materials, a single mug handle, stable geometry, no synthetic clutter. Higher resolution and stronger opacity are not substitutes for believable motion.

## Repository and tooling

Subscribe overlay v1 (2026-09-25): local ten-second graphics-only candidate in final/channel-assets/subscribe-v1, visual review pending. Native renderer scripts/render_subscribe_banner.py uses bundled OFL Barlow Condensed fonts from creative/brand/fonts. Green-screen H.264 and straight-alpha ProRes 4444 exports, both 4K/30 fps/no audio; actual Ringfall footage supplies the composited review preview. Read the asset README for timeline and placement. Use once at an appropriate point in a long edit; never repeat a subscribe banner with every ambient scene loop. Do not mark the first candidate user-approved from technical checks. Video drafts remain local until accepted.

Description/search-tag convention (2026-09-25): read final/DESCRIPTION_STYLE.md. Save one description.txt and one comma-separated youtube-tags.txt per video package. Use the shared sign-off "Welcome to Ambient Colony. Stay a while and listen." Keep concise original scene lore, three relevant description hashtags, and each Studio tag list strictly under 500 characters including commas/spaces. Record counts and hashes in the package manifest. Current masters are silent; add music/genre/production claims only after the actual soundtrack is known. Search tags are supporting metadata, not a substitute for titles, thumbnails and good descriptions.

Approved release collection (2026-09-25): final/ contains Ringfall, Basalt and Glacier video/thumbnail packages. User approved the thumbnail set: "man they look awesome". Read final/THUMBNAIL_STYLE.md and reuse the Ringfall PNG as the visual identity reference for future thumbnails. Exact built-in image-generation prompts and provenance hashes are saved per package. Keep clean condensed ivory titles, orbital mark, amber rules, short captions and catalog numbers; adapt title placement to preserve each scene's focal subject. Preserve approved v1 files and version revisions. Final videos are byte-identical copies of existing approved masters, tracked through exact Git LFS rules; original production paths remain valid. These are silent loops, not completed long-form music uploads.

Approved v9b MP4 is explicitly tracked by a narrow .gitignore exception at the user's request. Draft videos, .local/ runtimes/weights and caches remain ignored. For future approved finals, check size and repository limits before choosing ordinary Git or a large-file strategy; do not silently omit requested media. Never force-push. Ringfall now has a generated one-hour music listening file; see creative/MUSIC_WORKFLOW.md for provenance, user feedback and approval scope. Basalt music is at prompt/testing stage.

Python has NumPy, Pillow, OpenCV and imageio-ffmpeg. The Ringfall renderer imports v8, v7, v6 and the core renderer plus scene-v6.json; retain those dependencies. Free ComfyUI/Wan is installed under .local/ for optional future experiments, not the accepted production path. Hardware: RTX 4060 8GB VRAM, approximately 64GB RAM. Keep services on localhost and paid/API nodes disabled.


## Next scene: carry these decisions forward

Read creative/NEXT_SCENE_RUNBOOK.md before producing another scene. Basalt v6 is now the accepted landscape-motion reference alongside Ringfall v9b. Start with isolated short full-frame transport tests; recognizable motion before loop design, source-coordinate masks before strength tuning. User-visible acceptance is separate from numeric validation. Preserve explicit feedback and current authority rather than treating older pending statuses as active.

Approved media policy: Basalt's exact 113.7 MB master uses a single-path Git LFS rule; do not add blanket video tracking, generated twenty-minute repeats, failed trials, caches or model weights. Git push must upload LFS content as well as the pointer; verify the LFS object remotely before claiming backup complete. No paid capacity purchases. Store source/config/code hashes and restore instructions with each approved delivery.


Music workflow (2026-09-26): read creative/MUSIC_WORKFLOW.md before soundtrack work. Ringfall crossfade audition accepted; extended listening pending. Basalt reference analysis and exact prompts are in final/02-basalt-transmission/music/. The user runs ElevenLabs generations with existing credits; do not spend credits automatically. Distinguish signal analysis from listening, and saved files from committed/remote backup.
