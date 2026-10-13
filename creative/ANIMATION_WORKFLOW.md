# Reusable local animation workflow

## Use the accumulated scene lessons

Read [ANIMATION_KNOWLEDGE_BANK.md](ANIMATION_KNOWLEDGE_BANK.md) before every new scene or substantial revision. Choose the relevant accepted examples and candidate methods explicitly; record the choice, required remapping and known failure to avoid in the scene plan. The bank covers videos 01–09 and supplements the technical gates below. Update its existing effect/video entries after user feedback instead of keeping improvements only in the latest chat.

## Approved baseline

Ringfall v9b was approved by the user on 2026-09-24. Use local masked procedural overlays as the default, not whole-scene or cropped video diffusion. The accepted export is ringfall/animation/ringfall-ambient-v9b-20s-final.mp4. Its source, brief, renderer, masks, settings, checks and approved-v9b.json are the reference package. Prior AI-video experiments are historical failures for this scene, not pending next steps.

## Once-only opening titles

Direction requested 2026-10-13: the user supplied five screenshots of Ambient Outpost's PROJECT HADES opening and said, "i'd like to start to incorporate this intro into all our future videos". Original supplied screenshots and their provenance are saved in [the reference manifest](brand/references/ambient-outpost-project-hades-2026-10-13/manifest.json). This is a visual reference for a Colony treatment, not an asset to insert into our videos.

Observed screenshot sequence: at roughly 1 second the scene is visible and relatively dark; at 4 seconds a small, centered, widely spaced AMBIENT OUTPOST credit appears; at 8 seconds that credit remains with a smaller partly obscured line underneath; at 11 seconds a large stacked PROJECT HADES title is visible; at 21 seconds the title is gone and the scene is brighter. YouTube's controls/pause symbol and channel watermark are interface/reference details, not part of the proposed Colony intro. These five frames do not establish precise fades, letter movement, camera movement, sound design or audio timing. The actual reference video/audio has not been watched or heard.

User audio correction, 2026-10-13: the user reports barely any music/SFX during the reference's first 5–10 seconds and explicitly requests our audio to start fading in slowly at 0:05. This supersedes the initial proposal to start audible music immediately. The assistant has not independently heard the reference. Start our opening gain at silence, hold through 0:05, then use a gentle fade; reaching the established listening level at 0:20 is a proposed first prototype, not a user-approved fade duration. Preserve later scene-specific SFX onsets rather than moving all ambience to 0:05.

Original v2 feedback, 2026-10-13: the user says v1 works but rejects the look: first five seconds insufficiently dark; AMBIENT COLONY too small; PRESENTS missing; location title/amber rule too small; tagline should sit near the bottom, arrive before the main title fades, and hold about five seconds afterward. This supersedes the earlier sequential centered tagline. Latest wording is **Stay a while and listen**, with no trailing colon, per the subsequent v3 correction. No spoken line or sonic sting.

V3 keeps the v2 timing (an interpretation for review, not a measured reference or user approval):

| Time | Treatment |
| --- | --- |
| 0–10 s | Running scene behind an 88% black overlay, much darker than v1. Audio silent to 5, then its existing slow entrance. |
| 2–9 s | Almost-double AMBIENT COLONY lettering and enlarged orbital logo; fade in 2–3.2, hold to 8, fade to 9. |
| 4.8–9 s | Separate PRESENTS under the channel name; fade in to 5.8, hold to 8, clear at 9. |
| 10–15 s | Larger public title and longer/thicker amber underline; appear 10–11, fade 14–15. Scene begins revealing at 10. |
| 12–20 s | Lower tagline at 89% of frame height, fade in 12–13 while the title remains, hold fully visible through 20 (five seconds after title clears). |
| 20–21.5 s | Fade the final lower tagline. Scene and audio have reached normal by 20; all text is clear by 22. |

V3 moves PRESENTS closer under AMBIENT COLONY, from 56.5% to 52.5% frame height, and removes the tagline colon. User requested these corrections followed by commit/push. The opening occupies 22 seconds inside the requested runtime, not an added segment. Preserve the v1 evidence and source snapshot; use [intro-v3](brand/intro-v3/README.md) for current defaults.

Use our [established visual identity](../final/THUMBNAIL_STYLE.md): clean warm-ivory letters, restrained amber only if it helps, comfortable margins, and placement that keeps the key landscape/architecture readable. The bundled [Barlow Condensed fonts](brand/fonts/README.md) provide reproducible text rendering. The reference's distressed title texture is not a change to Colony's typography. Default to opacity transitions and fixed framing; extra motion, glitches or a separate sonic sting are not established by these screenshots.

Implementation belongs to final assembly: keep the approved silent scene loop clean and apply the opening exactly once per new finished video. Keep environmental motion running beneath the darker opening; hold that darkening through the channel credit and begin its gradual lift with the main location title, rather than brightening the scene immediately from time zero. Start the audio fade at 0:05 and maintain continuous audio after its entrance. Replace the previous opening envelope in the new assembly recipe; do not stack fades on an already-faded soundtrack or add time to the requested runtime. Existing music joins, baseline gain, SFX event scheduling and closing fades remain scene-specific. See [the music workflow](MUSIC_WORKFLOW.md#future-video-intro-audio--2026-10-13). Opening dimming is a once-only title treatment, not permission to add exposure changes or full-frame dissolves to the repeating loop. Existing approved exports remain preserved; any retrofit requires a separately requested version. For continuous broadcasts, the intro must not recur with every scene/music repeat.

Implemented in `C:/dev/SpeedySlideShow/colony/intro.py`, renderer and GUI; see [the reusable opening package](brand/intro-v3/README.md). The rebuilt app defaults to an opening with a blank public-title field and optional 0:05–0:20 audio entrance. Preview opening works with no music. New scripted assembly opts in with `IntroSettings(public_title)`; historical scripts remain compatible. The user clarified this is a future-production upgrade and no current music/video is being made. A silent 25-second v3 demo and native 4K graphic cards are saved; current technical/build checks are in its implementation-verification.json. The user rejected v1 aesthetically despite technical passes. Scene colour stays YUV, complete opening units retain phase and subsequent clean units are copied. Tests compare all clean tail frames and preview/export states. Assistant inspected decoded temporal stills; artistic timing and future listening review remain pending. Validate each release's title spelling, placement and audio entrance before publication. For broadcasts, play the opening at startup outside the repeated clean playlist.

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
