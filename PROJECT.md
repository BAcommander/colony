# Ambient Colony — project context

Last updated: 2026-09-24.

## Current approved state

Next scene selected on 2026-09-25: concept09 Basalt Transmission. User requested a detailed first-pass production prompt for a twenty-minute video. Saved creative/basalt-transmission/animation/production-prompt-v1.md and source-hashed scene-plan-v1.json. Planned delivery is sixty repetitions of a twenty-second local loop (4K,30fps,silent); this duration interpretation is stated to the user. No animation rendered in this prompt-writing turn. The plan emphasizes roof exhaust, low valley haze and independent room-light changes, with optional masked sky detail.

The user approved Ringfall v9b as finally good and requested that the final 4K video be pushed too. Approved file: creative/ringfall/animation/ringfall-ambient-v9b-20s-final.mp4 (20 seconds, 30 fps, 3840x2160, silent, upscaled source art). It is tracked in Git, with hash and acceptance in approved-v9b.json beside it. Local procedural compositing is the accepted default. AGENTS.md and creative/ANIMATION_WORKFLOW.md now provide the concise reusable process; creative/scene-plan-template.json captures new scene parameters. Current renderers still require scene-specific coordinates; this is not yet a generic one-command renderer.

The sections below retain historical chronology. Earlier pending-review, no-final, regional-AI-next-step and local-only-final statements are superseded by this approval and storage decision.

## Confirmed by the user

- Channel: https://www.youtube.com/@ambientcolony
- Repository: https://github.com/BAcommander/colony
- Local project folder: C:\Colony
- The user started the channel the night before this conversation.
- The repository is intended to store their music and the animations we make.
- Initial creative request: generate approximately ten inspiration images to choose from, then develop an exceptionally high-quality, loopable ten-second video prompt for the channel's videos.

## Branding and references

The supplied channel screenshot shows the name Ambient Colony and tagline "Sci-fi soundscapes for sleep, focus & study", a desert outpost banner, and a ringed-planet avatar. At the time of the screenshot the channel had no uploaded content.

The user supplied four individual scene references and a fifth screenshot containing multiple video thumbnails. References include a sunset radio room, a snowy geodesic research habitat, a remote desert lookout, an aging panoramic control room, and dark coastal/industrial outposts.

Working interpretation, awaiting selection: quiet remote environments, detailed retro-industrial equipment, warm inhabited shelters against vast landscapes, photorealistic cinematic framing, and restrained movement suited to ambient listening. These are starting directions, not final user-approved art rules.

## Initial concept round

1. Dusk Relay — desert radio room at sunset.
2. Glacier Sanctuary — warm research dome beneath an arctic rock arch.
3. The Last Lookout — remote desert ridge station.
4. Cloudline Control — mountaintop control room above clouds.
5. Tidal Listening Post — coastal receiver station and satellite dishes.
6. Ringfall Observatory — lunar interior overlooking a ringed planet.
7. Forest Signal — rainy forest field station.
8. Below the Ice — subglacial observation/control room.
9. Basalt Transmission — shelter on an alien basalt plain.
10. Night Shift Greenhouse — colony greenhouse and radio workspace.

Generation used the built-in image-generation tool. Inventory verified on 2026-09-24: concepts 01 through 09 are saved in creative/concepts. No saved image for concept 10 was found; it remains planned. The concept gallery indexes the actual assets.

## Selected direction and feedback

The user selected concept 06, Ringfall Observatory, as the first focus. Their main criticism was that the foreground looked fake / too AI-generated. After three variants, they chose 03-working-lunar-habitat.png, the version with the laptop on the desk. They requested a substantially larger rug, fixing the desk mug to have one handle rather than two, restoring a small coffee table, and improving overall quality. Keep the lunar vista, ringed planet, laptop workspace, and warm atmosphere. Prefer believable furniture and restrained material textures. Variant prompts are in creative/ringfall/prompts.md; the next refinement prompt is in creative/ringfall/04-laptop-refined-prompt.md.

## Files and workflow

- AGENTS.md: short persistent instructions for agents working in this folder.
- PROJECT.md: durable context, decisions, and learnings.
- creative/concepts/: locally saved concept images.
- creative/video-loop-prompt.md: draft image-to-video prompt with motion suggestions and seam checks.
- AGENTS.md, Active video section: authoritative evolving Ringfall local-animation brief, preferences, and render findings, saved here at the user's explicit request.
- scripts/render_ringfall.py: reproducible local animation renderer. Built with existing local tools; no service charges.
- creative/ringfall/animation/ringfall-loop-v5-4k.mp4: previous local render, technically valid but rejected by user for limited scene-wide motion. It is not an approved final.
- creative/ringfall/animation/motion-brief-v6.md and motion-plan-v6.json: authorized six-layer direction, now implemented. Current export is creative/ringfall/animation/ringfall-v6-b-final.mp4, ten seconds at 3840x2160/30 fps, approximately 24.1 MB, upscaled from the existing source. Technical checks completed, but the user rejected the result as too subtle.
- scripts/render_ringfall_v6.py: layered local renderer with independent effect selection, reusable masks, and JSON scene settings. Planetary band detail, colony light sweeps and linked window reflections are implemented along with steam, laptop and beacon.
- creative/ANIMATION_WORKFLOW.md: preview-first production with separate visual and technical acceptance. Renderer now supports preview/final stages and version labels; a 720p preview verified the CLI changes using the existing v5 effects.

Workflow: refine the local animation brief, prepare reusable scene layers, prototype dominant motion at 720p, evaluate the whole composition, check loop continuity, then export 4K. Local rendering is confirmed; external video generation is not the default. Music workflow and large-media storage remain undecided.

## Learnings and limits

- Latest feedback: v6 still does not achieve the desired visible motion. Investigated free local image-to-video generation. User authorized setup and testing on 2026-09-24: ComfyUI + Wan2.2 TI2V-5B with native offloading. Official documentation states 8GB VRAM suitability. This PC has an RTX 4060 with approximately 8GB VRAM and approximately 64GB system RAM. Actual local tests completed; see wan-tests/README.md for timing and quality failures. Local GPU generation would avoid per-video credits; paid cloud/API nodes remain excluded.

- Confirmed cost and workflow preference: always prioritize local animated MP4 creation through this chat using existing Codex usage and local tools. No paid plugins, external video-generation charges, or separately purchased credits. The proposed Runway comparison is dropped. Do not interpret future animation prompts as requests to use an external generator unless the user explicitly says so.

- User feedback establishes that a fixed image with steam, laptop activity and a small light does not meet the desired visual ambition. Broader background activity and full-scene motion review are required. Passing technical continuity checks alone does not establish artistic success.
- Prompting for identical endpoints alone does not establish a seamless loop. Actual motion continuity and the transition need inspection.
- A first local animation has been rendered and validated. No music has been produced in this session yet.
- On 2026-09-24, the user requested committing and pushing the learnings and 2D concepts. Initialized C:\Colony as a Git checkout connected to https://github.com/BAcommander/colony.git; the remote was empty. Track source art, scripts, masks, prompts and reports. Local runtimes/weights and experimental videos are excluded.

## Reusable hybrid workflow and next task

The user requested that the workflow carry forward to future images. AGENTS.md now records source preservation, motion-aware scene design, regional AI generation, protected geometry masks, local procedural supporting effects, separate artistic/technical checks, region-only loop construction and preview-before-4K delivery. This is the chosen direction to test, not a proven solution yet.

Next task: isolate Ringfall's planetary atmosphere, generate short cloud motion, composite it into the untouched master while protecting rings and silhouette, and inspect a full-scene preview. Full execution and model prompts are in creative/ringfall/animation/next-planet-pass-prompt.md. No regional render has been started. Previous AGENTS.md and all historical learnings are preserved in creative/history/animation-learning-log-2026-09-24.md.

Local AI test setup: .local/ComfyUI and .local/comfy-env, with verified models installed. Reproducible prompt/API workflow: scripts/run_wan_test.py and creative/ringfall/animation/wan-tests/. Two tests completed: 91.84s and 215.04s render time. Visible motion improved but geometry and effect placement failed sampled-frame review; neither is approved. Runtime/model downloads stay excluded from Git.

Regional planet experiment completed: two cropped Wan candidates plus one cached-latent decoder comparison. Masking preserved unrelated geometry exactly before encoding, but atmospheric quality failed: drift, a dark blotch in candidate01 and bright-edge contamination/artifacts in candidate02. See creative/ringfall/animation/planet-pass/README.md. The delivered short preview/comparison is diagnostic only. No loop or 4K export was made. Possible next method: generate atmosphere texture independently and map it onto fixed geometry; still untested.

Latest user feedback: isolated planet motion still feels no better than the original steam. Researched independent foreground/effect overlays, native ComfyUI masked compositing, optional video overlay nodes and VACE masked generation. Details and primary sources: creative/overlay-research-2026-09-24.md. The proposed next direction is a clearly readable independent motion element; a maintenance craft is an example, not an approved addition. No tools/models installed and no new video rendered during research.

The user authorized and received a five-second independent maintenance-craft test. Built-in image generation created a true-alpha craft; deterministic local motion and native ComfyUI compositing produced a 720p MP4 and comparison. Everything outside the midpoint matte was preserved in the lossless Comfy output. Details: creative/ringfall/animation/craft-overlay/README.md. The clip is not looped; 2D asset realism and artistic acceptance remain open. The asset, prompt, trajectory, masks and graph are reusable.

Latest direction: the user rejected moving spacecraft as cheap-looking and requested the original ambience with richer steam, laptop activity, moving colony lights and subtle planet motion. Implemented a local independent-layer v7b pass and exported a ten-second 4K review MP4. Authoritative prompt: creative/ringfall/animation/ambient-v7-prompt.md. Output: creative/ringfall/animation/ringfall-ambient-v7b-final.mp4; preview and validation reports sit beside it. Geometry and numerical continuity checks passed; sampled-frame review only, user artistic approval pending. Craft and generative-planet tests remain historical rejected directions.

User accepted v7b as a much-improved, subtle, unbroken direction, then requested20seconds and additional ring/distant effects. v8 preserves that baseline and adds protected ring-material light drift plus a slow colony service-light sequence. The complete scene has a distinct20-second cycle. Updated prompt/settings and validation are beside the local review exports. New version awaits artistic feedback; no spacecraft or geometry warping.

## Latest creative decision: v9 brief (2026-09-24)

User rates v8 about 6/10 and finds ring motion invisible. Saved creative/ringfall/animation/ambient-v9-final-brief.md: visible vent exhaust, individual colony lights turning on/off and readable ring-material transport. Updated AGENTS.md. Proposed only; no new render this turn. Retain twenty-second free/local workflow, compare at normal viewing size before 4K, preserve prior exports.

## Ringfall v9b implementation — 2026-09-24

Implemented the final revised brief with local overlays: two colony exhaust plumes, four individually scheduled existing-window states, and stronger angular ring texture transport. Initial v9 window-core defect corrected in v9b. Current renderer: scripts/render_ringfall_v9.py. Exports: ringfall-ambient-v9b-20s-preview.mp4 and ringfall-ambient-v9b-20s-final.mp4; comparison: ringfall-v9b-original-comparison.mp4. Prior versions retained. Preview numeric checks passed; temporal samples inspected, no continuous playback review. User artistic approval remains pending, and 4K uses upscaled source artwork.
