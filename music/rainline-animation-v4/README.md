# Rainline Relay — animation v4

2026-10-04. User could not see v3 foreground/radio movement, requested a better rear-building mask and another 25% water reduction. V4 is a review candidate, not an accepted final.

- [20-second silent 720p/30 fps preview](rainline-relay-v4-preview-20s.mp4)
- [60-second review: three exact repetitions](rainline-relay-v4-three-loops-60s.mp4)
- [Foreground-room test](room-isolated-v4-8s.mp4)
- [Water test](water-isolated-v4-8s.mp4)
- [Building-light test](lights-isolated-v4-8s.mp4)
- [Beacon regression test](beacons-isolated-v4-8s.mp4)
- [Rear pane mask close-up](rear-mask.png)
- [Delivery record](delivery-v4.json)

## Changes

The previous additive meter was only four source pixels high with little contrast against the amber radio display. V4 draws two visibly extending/retracting segmented level bars, perspective-mapped inside the existing LCD. The blue display now has a readable scrolling cyan signal and faint grid within its existing chart panel. Bezel, equipment and remaining interface stay fixed. These are designed procedural instrument graphics, not real telemetry or new text.

The desk lamp has two longer gentle dips with 18%/16% event depths, plus a small slow variation. The saturated emitter and its existing warm desk light change together. No moving furniture, mug, knobs or camera.

Rear habitat glass is traced across its three visible panes. The right edge is corrected; a source-color gate includes warm interiors and bright white light cores while excluding cool metal/dividers. Removed inaccurate rectangular spill/reflection patches. Rear mask and dimmed-state close-ups are saved for inspection.

Water displacement is .3375 versus v3's .45, a 25% reduction. Reflection contrast, specular strength and rain-impact brightness also use a .75 multiplier. Keep v3 speed .12, wave family and corrected water/root/post/vegetation masks. This remains a 2D reflection approximation. Rain, middle-habitat scheduling and red/green antenna cycles otherwise continue.

## Checks and status

Four eight-second isolated tests preceded the complete draft. Analytic layer endpoints/seams, finite source frames and unchanged protected pixels passed. All 600 preview and 1800 review frames decoded with sequential timestamps; regional/composite encoded seam gates passed. The repeated review contains three exact decoded copies with no duplicate endpoint. Reports bind source/config/code/dependency/mask hashes.

Assistant inspected source crops, masks, temporal samples and decoded stills; no continuous playback claim. User normal-speed review is pending. No 4K, music or long assembly for scene 08 yet. V1/v2/v3 exports and configuration remain preserved. The exact v3 renderer is retained at ../rainline-animation-v3/renderer-v3-snapshot.py, verified against v3's recorded hash before extending the shared renderer. No credits, commit or push.

Run ../rainline-renderer/render_rainline.py with --config pointing to scene-plan-v4.json and --stage samples, isolated, then preview. Existing MP4 destinations are protected. Use the existing Python runtime with PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. prepare_v4.py records the v3-to-v4 configuration changes and snapshot step; it is not intended to overwrite a later renderer.
