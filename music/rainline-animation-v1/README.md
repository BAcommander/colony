# Rainline Relay — animation v1

2026-10-04. User requested execution of the proposed animation plan. First silent 20-second 720p/30 fps draft delivered; new motion awaits user review. Source remains the selected 1672x941 artwork-v1.png, hash-bound in scene-plan-v1.json. Original art and previous scene renderers are unchanged.

- [20-second complete draft](rainline-relay-v1-preview-20s.mp4)
- [Three-loop 60-second review](rainline-relay-v1-three-loops-60s.mp4)
- [Rain alone](rain-isolated-v1-8s.mp4)
- [Water alone](water-isolated-v1-8s.mp4)
- [Far mist alone](mist_far-isolated-v1-8s.mp4)
- [Near mist alone](mist_near-isolated-v1-8s.mp4)
- [Mask review](mask-review.png)
- [Delivery record](delivery-v1.json)

## Implemented

Fine distant rain and clearer nearby exterior rain use independent seeded particles, falling forward with consistent slight crosswind. Four/five-second lifetimes divide the twenty-second loop; local birth/death fades hide resets. Far rain is blocked by mapped trunks, buildings and walkway. Near rain is an optical layer in front of exterior objects, always behind the interior frames and foreground furniture. The static rain already in the source remains; v1 adds transported streaks without distorting the photographed scene.

Water adapts the accepted ChannelSurface/ReflectionSurface logic with this scene's perspective and 24 filtered wave components, plus restrained flattened rain-impact rings. Roots, posts, plant islands and window boundaries are excluded. Inpainted sampling excludes solid areas to prevent displaced copies entering the moving water. This is a 2D reflection approximation, not a fluid simulation. Water boundaries and vegetation protection should receive particular user review.

Two mist layers use the existing PeriodicDust/DustTransport logic with separate routes, speed, scale and masks. This transports broken formations through the forest and over the distant water without whole-frame exposure changes. A mask review caught the lamp/equipment overlap and it was corrected before isolated renders; initial mask/config evidence is preserved in initial-mask-review/.

Two existing habitat windows have staggered held dim states with matching small spill/reflection modulation. Other practical lights and the desk lamp stay steady. The small radio screen receives a restrained moving trace; the analog meter's light varies gently. No camera motion, added objects, steam, foliage warp or glass distortion. All timing uses one twenty-second scene clock.

## Checks and review

Eight-second full-composition rain/water/far-mist/near-mist tests rendered separately before the composite. All source frames enforce unchanged pixels outside their active masks and finite values. Analytic layer endpoints/seams pass. All 600 preview frames and 1800 repeated-review frames decoded with sequential timestamps; layer/composite encoded seam gates pass. The repeated review contains three exact decoded copies of the twenty-second draft; it is not a unique minute. Source/config/code/mask hashes are bound across all reports.

Assistant inspected source, mask and temporal/decoded stills; continuous playback and natural motion quality are not claimed. User should review normal-speed rain visibility, believable water/reflections, stable roots/railings, mist depth and lighting restraint. Scene 08 music, longer scheduling, 4K delivery and long assembly remain pending. No credits, commit or push.

Reproduce: render_rainline.py --stage samples, then --stage isolated, then --stage preview, using the existing Python runtime and PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. Existing MP4 destinations are protected from overwrite. Config parameters are separate from the reusable source-bound adapter; dependencies are recorded by fingerprint.
