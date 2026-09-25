# Reusable local animation workflow

## Approved baseline

Ringfall v9b was approved by the user on 2026-09-24. Use local masked procedural overlays as the default, not whole-scene or cropped video diffusion. The accepted export is ringfall/animation/ringfall-ambient-v9b-20s-final.mp4. Its source, brief, renderer, masks, settings, checks and approved-v9b.json are the reference package. Prior AI-video experiments are historical failures for this scene, not pending next steps.

## Start a new scene efficiently

Copy scene-plan-template.json into the new scene's animation directory and fill it out. Preserve the original still and calculate its SHA-256. Choose plausible principal motion before touching code. Identify static architecture, furniture, silhouettes, foreground occluders and areas that must not change. Map coordinates at source resolution, not preview resolution. Do not reuse Ringfall's positions or masks on another image.

Reuse the effect logic and encoder. Current Ringfall code is source-specific; adapting a new scene still requires remapping and configuring effects. Move new tunable values into its scene configuration rather than repeatedly forking renderers. Share one duration, phase convention and layer stack between preview and final.

| Effect | Successful technique | Avoid |
| --- | --- | --- |
| Steam/exhaust | Anchored evolving density, forward transport, expanding width, smooth birth/dissipation | Static translucent stamp, visible reset, plume detached from source |
| Window lighting | Whole-aperture mask, staggered off/on holds, coupled small spill | Only dimming warm pixels, leaving white cores lit, synchronized pulsing |
| Ring material | Coherent angular texture transport through fixed band mask | Invisible brightness shimmer, shifting outlines, moving sky/gaps |
| Planet | Low-contrast independent texture under protected geometry/shading | Whole-disc deformation, terminator drift, ring contamination |
| Screen | Perspective-confined telemetry/scan on original display | Replacing screen layout, moving bezel, global brightness changes |

Not every scene needs every effect. Preserve quiet areas and make the main motion readable at normal viewing size. Respect scene physics; directed vent exhaust is the artistic interpretation for this airless scene.

## Preview, refine, export

1. Prototype the principal layer first and inspect its mask at full composition and close range. Retain working secondary effects.
2. Render a 1280x720, twenty-second, 30 fps preview using the actual effect timeline. Save settings and temporal samples. Compare with the original still when helpful.
3. Review readable motion, realism, attachment, occlusion, lamp spill, stable exposure and geometry. Use playback when available; otherwise state that only temporal samples were inspected. Fix the largest concrete defect, not all amplitudes at once.
4. Verify 600 decoded frames, exactly twenty seconds, correct dimensions/fps, no audio, a distinct full-length cycle, unchanged source pixels outside active masks before encoding, and periodic endpoints. Check both individual layers and the encoded seam against ordinary adjacent-frame changes. Endpoint equality alone does not establish continuous motion. Inspect three repetitions in playback when possible. No duplicate endpoint, ping-pong or full-frame fade.
5. Export 3840x2160 only after available visual checks pass. Use the same source, timings, masks and effect strengths as preview. Inspect a decoded final frame and validate again. Disclose source upscaling. Do not rerender an approved export just for documentation.
6. Deliver the actual MP4, record the user's verdict, and make the accepted version the next baseline. User approval and technical checks are separate facts.

## Reproduce Ringfall

From repository root, with Python plus NumPy, Pillow, OpenCV and imageio-ffmpeg installed:

```powershell
python scripts/render_ringfall_v9.py --qa-only
python scripts/render_ringfall_v9.py --stage preview
python scripts/render_ringfall_v9.py --stage final
```

The approved final is already in Git; play it directly. Rendering refuses to overwrite existing video destinations. For a deliberate new revision, select a new output stem in a working copy of the renderer before rendering; preserve the approved export and renderer. The current CLI is not a generic new-scene interface. It depends on render_ringfall_v8.py, render_ringfall_v7.py, render_ringfall_v6.py, render_ringfall.py and scene-v6.json. Current source coordinates require the 1672x941 Ringfall master.

## Save once, reuse next time

Each accepted scene package needs source/hash, creative brief, scene configuration, masks/source anchors, renderer and dependencies, preview/final settings, validation, user feedback and an approved manifest with final file hash. Keep the latest decision at the top of AGENTS.md/scene README; archive old chronology rather than leaving contradictory next steps active.

Commit source art, supporting assets, scripts, prompts, configuration, masks, reports and approved final video. Ringfall's approximately 35 MB approved MP4 is tracked in ordinary Git through an explicit ignore exception. Draft videos, weights, runtimes and caches stay local. For larger future finals, check storage limits and choose a suitable strategy before pushing. Do not assume an approved final is backed up merely because its settings were pushed.


## Enforced motion review (Basalt audit, 2026-09-25)

Run `python scripts/motion_review.py --config creative/basalt-transmission/animation/scene-plan-v4.json --output creative/pipeline-audit-2026-09-25/review-v4` from repo root. Choose a fresh output directory for every revision. This renders eight-second, 30fps excerpts of sky, far haze, near wind and combined motion at 720p, retaining the actual twenty-second timeline. Excerpts are not loop deliveries. No effect strength is changed by isolation.

Inspect each at normal size and 1x speed. Name a visible feature, its direction and destination: a cloud edge shifts horizontally above the mesa; a broad low dust tongue crosses behind a distant rock. If only an amplified difference map reveals motion, the principal motion has not passed. If opacity produces a smoke stripe, change spatial structure/transport, not just opacity. Preserve architecture, moon and foreground. Check dust occlusion at terrain edges. Judge one candidate variable at a time: coherent shape/scale first, travel second, optical density last.

The generated `scene-plan-VERSION-visual-review.json` starts pending. Keep user rejection explicit. After genuine user acceptance, record their feedback and normal-speed review, mark accepted, and retain clip/config/source/code hashes. Do not manufacture approval or mark accepted from sampled stills. `render_basalt.py --stage final` and `assemble_basalt.py assemble` reject missing, pending, rejected or stale reviews. These are workflow checks, not tamper-proof security controls. Code/config changes require fresh review. Ringfall's approved historical render is unaffected.

After the short motion test passes, review the complete twenty-second composite and its seam before final export. Include that full-loop preview and hash in the accepted review's clips. Numeric protected-pixel, duration, decode and seam checks remain separate requirements. Lossless QP0 master avoids previously observed CRF-induced seam changes; verify the encoded seam even with correct analytic endpoints. Repeat the verified loop for twenty minutes only after visual acceptance.


## Basalt v6 loop lessons

When a forward-transport prototype reads well, reduce its speed independently from visibility before adding periodicity. Overlapping locally staggered cloud lifetimes can hide resets, but can also soften or double source features: explicitly review this tradeoff in playback. Never claim analytic periodicity proves natural motion. For plains particles, center trajectories on the intended region; merely increasing opacity while most particles travel offscreen wastes effort. V6 restores this coverage and retains separate near/far previews.

For twenty-second review exports run `python scripts/validate_motion_review.py --config creative/basalt-transmission/animation/scene-plan-v6.json --review creative/basalt-transmission/animation/review-v6/review.json`. It decodes every clip and compares encoded last-to-first change against ordinary adjacent-frame changes, separately per isolated layer. Keep visual acceptance separate.
