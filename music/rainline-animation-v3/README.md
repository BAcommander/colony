# Rainline Relay — animation v3

2026-10-04. User requested red/green antenna cycling, another correction to the middle building mask, foreground room activity and water between v1 and v2. This is a new review candidate; v2 was not accepted as the final look.

- [20-second silent 720p/30 fps preview](rainline-relay-v3-preview-20s.mp4)
- [60-second review: three exact repeats](rainline-relay-v3-three-loops-60s.mp4)
- [Water test](water-isolated-v3-8s.mp4)
- [Building-light test](lights-isolated-v3-8s.mp4)
- [Foreground-room test](room-isolated-v3-8s.mp4)
- [Red/green antenna test](beacons-isolated-v3-8s.mp4)
- [Mask overlay](mask-review.png)
- [Delivery record](delivery-v3.json)

## Changes

The middle building is the nearer, larger habitat behind the tree. V2's light matte left a bright strip on the left of its rightmost pane and extended into the right bezel. V3 traces that glass boundary from enlarged source crops with supersampled edges. All three visible panes now share the room's dim/flicker events; the intervening tree, frame and divider are excluded. Incorrect rectangular near-building spill/reflection patches are removed. Its held dim state is gentler. Source comparison crops are preserved here for review.

Both antenna lamps alternate red and green on successive pulses, with different phase offsets. Dark gaps between colors avoid an orange blend. Each color schedule divides the twenty-second loop.

Water displacement is .45, exactly between v1's .22 and v2's .68. Speed is .12 between .10 and .14; contrast/specular response is also intermediate. Keep the corrected v2 water/root/post/vegetation mapping and wave family. This is a 2D reflection approximation; user playback is needed to judge the desired calmness.

Foreground activity now includes a stronger screen trace, a small changing radio level strip and restrained desk-lamp variation coupled to its warm desk spill. The lamp's saturated white core is included. Physical equipment, mug, furniture and camera remain fixed. V2 rain is retained; source-baked static streaks remain. Existing mist continues.

## Verification and status

Four isolated eight-second tests preceded the composite. Analytic layer endpoints/seams, finite frames and protected pixels passed. All 600 preview frames and 1800 repeated-review frames decoded with sequential timestamps; regional/composite encoded seam checks passed. The review contains three identical decoded copies, with no duplicated endpoint. Source/config/renderer/dependency/mask hashes match across reports.

Assistant inspected source/mask/temporal/decoded stills, not continuous playback. User normal-speed review remains pending. The sixty-second review is three repeats, not a unique minute. No scene 08 soundtrack, 4K delivery or long assembly yet. V1/v2 remain unchanged; no credits, commit or push.

Renderer: ../rainline-renderer/render_rainline.py, with --config pointing at this folder's scene-plan-v3.json. Run --stage samples, then --stage isolated, then --stage preview. The shared renderer accepts configuration paths and versioned output names; refuses to overwrite MP4s. Use the existing Python runtime and PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. build_v3.py records the additions from the preserved v2 renderer.
