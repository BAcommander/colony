# Icebound Weather Post - sixty-second v3 preview

2026-10-03. User accepted the v2 look, then requested the suggested sixty-second loop with more varied lighting. This minute is delivered at 1280x720/30 fps, silent. The new timing awaits review; v2 acceptance remains recorded separately.

- [One-minute preview](icebound-weather-post-v3-minute-720p.mp4)
- [Three-minute join review](icebound-weather-post-v3-three-minutes-720p.mp4)
- [Delivery record](delivery-v3.json)
- [Full minute timing configuration](scene-plan-v3.json)
- [Accepted v2 look](../icebound-animation-v2/approved-v2-preview.json)

## Timing changes

The main right-hand room has dim holds of 7.5, 8.9 and 7.4 seconds, including a hold beginning at 55.4 seconds and continuing through the join. The two mapped habitat windows have independent 6.2-12.1-second holds and different intervening lit periods. Original aperture masks, dim floors and transition softness are retained, and the room spill follows its window.

Both red antenna beacons keep their original size, colour and double-flash appearance. Seed 7303 generates fixed but varied gaps between flashes across the full minute: twelve upper-mast groups and ten side-antenna groups. Gaps wrap coherently at the join. Entrance-lamp dips are spread across the minute; its local spill still follows the lamp. Unmapped lights stay steady.

Clouds, basin spindrift and snowfall retain the exact existing local twenty-second cycles and speeds, including ten-second nearer-flake lifetimes. This is a sixty-second composite because lighting changes across the entire minute; it is not three copies of the v2 MP4. The same weather phase at seconds 0,20,40 has different lighting. Source weather frames are cached in memory while every complete frame is composited with its own lighting timestamp. No approved code/config or original artwork was modified.

## Verification

All unchanged weather layers match v2 source frames at six sampled times, with zero speed deviation. Additional spot checks at 0.7,8,28 seconds found exact combined pixels outside lighting areas. New light-layer analytic endpoints and seams pass; the composite matches at 0/60 seconds and differs at 0/20/40. The complete 1800-frame preview and 5400-frame repeat fully decode with sequential timestamps and regional/composite encoded seam checks. All three decoded minute repetitions match exactly. See analytic-validation.json and preview-validation.json.

Temporal and decoded stills were inspected; continuous assistant playback and acceptance of the new timing are not claimed. Native source remains 1672x941. 4K export, soundtrack and long assembly remain pending. No credits, model installation, Git commit or push occurred.

Reproduce using render_icebound_minute.py --stage samples and --stage preview with the existing Python runtime and PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. Source/config/code hashes are bound to the accepted v2 manifest. Encoded destinations refuse overwrite.
