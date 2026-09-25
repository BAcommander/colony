# Ambient Colony: next-scene runbook

## Accepted references

- Ringfall v9b: cozy observatory, recognizable exhaust/window/ground-light actions. Approved 2026-09-24. Preserve its renderer and art.
- Basalt v6: exterior landscape with slower cloud transport, near-plains smoke and independent far-valley wind. User called it decent, requested seamless completion, then asked to save it. Twenty seconds, 600 frames, 30fps, silent, 3840x2160 resampled from 1672x941 art. Details: basalt-transmission/animation/delivery-v6.json.

## Restore

Clone the repo with Git LFS installed, then run `git lfs pull`. The Basalt master path is `creative/basalt-transmission/animation/baseline-v6-loop-4k-master.mp4`. Verify SHA-256 `6275bbce0504903fceeaa4b00a7e3b13bc3b07b6fe18f8515877097e8cfbee0c`. Draft MP4s and three-repeat previews are reproducible local outputs, not tracked. No new twenty-minute Basalt v6 delivery has been assembled; older long exports are historical drafts.

## Produce efficiently

1. Read AGENTS.md, ANIMATION_WORKFLOW.md, and the accepted scene manifest. Preserve/hash the new still. Record source-space coordinates, layer order, masks and protected geometry. No automatic transfer of scene-specific coordinates.
2. Choose concrete visible actions by depth: sky cloud edge moves right, distant low wind tongue crosses a valley, near smoke remains supporting, windows have separate schedules. Avoid percentage improvement promises.
3. Render eight-second isolated principal-motion tests at 720p/30fps, full composition, actual speed. Build coherent shape transport before adjusting speed, then opacity. Source high-pass shimmer is not equivalent to moving broad clouds. Purely enlarging a mask over blank sky adds no subject to move.
4. Keep near and far haze independent. Center particle travel on the visible region; v5 near smoke was lost by reducing opacity and sending paths out of frame. Stronger one-region smoke does not solve an inactive distance. Track recognizable features as diagnostic support, never artistic acceptance.
5. After motion reads well, implement a twenty-second cycle. Basalt uses overlapping locally staggered cloud lifetimes with forward travel and zero-weight resets, and paired periodic dust tongues. This may soften/double texture: review playback for ghosting. Half-speed cloud copies (4.5 source px/s) were preferred to v5's 9 px/s. Do not use a full-frame dissolve, reverse motion or camera drift.
6. Freeze moon, architecture, foreground and terrain silhouettes. Remove moon from sampled moving texture as well as protecting its output mask. Keep rock occlusion tight and inspect boundaries at source scale.
7. Review full twenty-second 720p composite. Record the user's exact verdict. Use motion_review.py and validate_motion_review.py for isolated media, hashes, full decode and encoded seam checks. No checksum, difference heatmap or still montage proves motion looks natural. State if only still samples were inspected.
8. Once accepted, render 4K with the same timings/config and QP0 encoding, validate every frame and compare seam against normal steps. Disclose upscaling. A three-repeat stream-copy preview exposes joins without player restart; it is not a longer unique animation.
9. Only then assemble the requested long video by stream copy, and check duration, timestamps and repeated frames. Do not repeatedly render twenty-minute drafts during look development. Default duration is twenty-second loop; longer unique loops are an artistic choice, not necessary for seamlessness.
10. Save brief, config, masks, scripts/dependencies, source and output hashes, validation, exact feedback and accepted manifest. Update current authority in AGENTS.md. Push approved large media with narrow Git LFS tracking and verify remote object availability. Do not silently omit approved media or purchase storage.

## Reproduction commands for Basalt

`python scripts/motion_review.py --config creative/basalt-transmission/animation/scene-plan-v6.json --output creative/basalt-transmission/animation/review-v6 --seconds 20`

`python scripts/validate_motion_review.py --config creative/basalt-transmission/animation/scene-plan-v6.json --review creative/basalt-transmission/animation/review-v6/review.json`

`python scripts/render_basalt.py --version v6 --stage final`

Existing destinations are protected from overwrite. Pull the approved master instead of unnecessarily rerendering it. A fresh rerender requires recreating local review clips and retaining honest user acceptance; changes to code/config invalidate hash-bound review records. The renderer remains Basalt-specific, not a universal image animator.


## Executable controls added after Glacier review

Do not merely reread historical notes and hand-edit another renderer for each adjustment. `creative/effect-presets.json` and `scripts/apply_scene_presets.py` provide reusable tuning controls; use a stable input config and a fresh output. `render_glacier.py --layers water` renders only a changed layer. `--compare-config OLD_CONFIG` stacks old/new full-size frames for direct comparison. These controls currently target the Glacier effect schema; new scenes still need explicit masks and anchors. Do not promise automatic one-shot scene adaptation.

When repeated deformation attempts look wrong, preserve the photographed surface and test a constrained overlay against the rejected version. Freeze accepted layers with sampled pixel comparisons. Present one useful comparison instead of repeatedly claiming a new effect is more realistic. User artistic judgment remains the acceptance criterion.


## Glacier accepted-water and sixty-second lessons

The user accepted v10 after the v8b 24-wave reconstructed reflection surface was made calmer in v9 and slower in v10. Sparse glints and small image warps had repeatedly failed. Preserve the successful method; tune speed separately from visibility and contrast. V10's gentle sampling filter and boundary damping reduce fine ripple instability and shoreline distortion. This is a source-based 2D approximation, not a physical water simulation.

For the requested sixty-second v11 loop, keep supporting effect rates and quantize each water frequency to the nearest positive integer cycle over sixty seconds. Mean speed deviation from v10 is 5.15%, maximum 12.11%. Quantize snow lifetimes to divisors of sixty and hide trajectory resets with local opacity fades. Use paired fading twenty-second fog lifetimes; existing ten/twenty-second lamp/smoke periods divide sixty. No full-frame fade or reversed motion. The overall scene differs at twenty/thirty seconds.

Render both resolutions from one source-frame pass after the look is accepted. Verify 1,800 frames per sixty-second loop, source pixels outside motion masks, each analytic layer seam, encoded seam against ordinary steps, and repeated-payload identity. Store exact user acceptance separately from full-export validation. Do not claim continuous playback from still samples. Use the delivery manifest to restore the approved master instead of rendering again.
