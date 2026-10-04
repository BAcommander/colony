# Rainline Relay — animation v5

2026-10-05. User felt v4 was nearly there and requested a foreground light blink and rain on the windows. V5 is a review candidate; this request does not establish final visual approval.

- [20-second silent 720p/30 fps preview](rainline-relay-v5-preview-20s.mp4)
- [60-second review: three exact repetitions](rainline-relay-v5-three-loops-60s.mp4)
- [Glass-rain isolated test](glass-isolated-v5-8s.mp4)
- [Foreground-room isolated test](room-isolated-v5-8s.mp4)
- [Delivery record](delivery-v5.json)

## Changes

The desk lamp has two brief, clearly dark blinks at approximately four and fourteen seconds. The existing white emitter, warm desk light and nearby halo dim together. Remaining slow lamp variation is reduced. Furniture, shade and camera remain fixed.

Twelve sparse rain beads slide along the foreground window glass, leaving narrow wet trails. Each has a locally refracted view and restrained cool highlights. Motion is clipped to the existing glass mask, protecting frames and foreground equipment. Ten- and twenty-second lifetimes divide the loop; local fade-in/out hides particle resets. This is a procedural optical approximation, not a fluid simulation.

V4 water strength/speed, radio and screen activity, corrected building panes, red/green antenna cycles, exterior rain and mist are retained. Separate frames for eight retained layers match v4 byte-for-byte at 0 and 7 seconds; this sampled regression does not claim full playback review.

## Checks and status

Two eight-second isolated tests preceded the complete draft. Analytic layer endpoints/seams, finite source frames and unchanged protected pixels passed. All 600 preview and 1800 repeated-review frames decoded with sequential timestamps. Regional/composite encoded seam gates passed, and the review contains three exact decoded copies without duplicate endpoints. Reports bind source/config/code/dependency/mask hashes.

Assistant inspected masks, temporal samples and decoded isolated/composite stills, not continuous playback. User normal-speed review is pending. The source is 1672x941; this preview is 1280x720. No 4K, music or long assembly for scene 08 yet. Earlier versions remain preserved. The exact v4 renderer is saved as ../rainline-animation-v4/renderer-v4-snapshot.py and verified against its delivery hash. Draft media remain local and ignored by Git. No credits, commit or push.

Run ../rainline-renderer/render_rainline.py with --config pointing to scene-plan-v5.json and --stage samples, isolated, then preview. Existing MP4 destinations are protected. Use the existing Python runtime with PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. prepare_v5.py records the initial configuration changes and snapshot step; it is not intended to overwrite a later renderer. The final scene-plan-v5.json is authoritative, including subsequent bead visibility and lamp-halo refinements.
