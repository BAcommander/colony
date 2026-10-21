# Spirewatch v5 — bright thumbnail-derived rebuild

Delivered 2026-10-21. Technically verified; user playback review pending. V4 was rejected because its older dark plate did not match its much brighter thumbnail. V5 uses a new clean plate edited directly from that thumbnail.

- [Complete sixty-second preview](spirewatch-v5-preview-60s.mp4)
- [Three exact repeats, 180-second review](spirewatch-v5-three-loops-180s.mp4)
- [New clean artwork](artwork-v5.png)
- [Thumbnail reference](../spirewatch-animation-v4/thumbnail-v1.png)
- [Exact built-in imagegen prompt](artwork-generation-prompt.txt)

The cyan spire, warm city/room, bright bridge and reflective water are present in the source itself. The animation does not dim them toward the old plate. Normal frame brightness in sampled city/room/spire regions closely matches the thumbnail (source-comparison.json); these are descriptive measurements, not a percentage quality claim.

All coordinates/masks were redrawn for the new 1672x941 plate. V4 masks were not reused. Upper clouds move faster than lower sky haze, with source-distance bounds protecting structures. Source waterfall material travels downward; water has calm bounded ripples. The tower sends light upward at 3–18s, holds at its crown, then returns downward at 37–54s. District channels acknowledge with delays. Cyan/amber/cyan bridge traffic occurs at 4–21 / 25–43 / 46–59s, with broken water responses. Warm windows have independent long holds. The original monitor map has tracking markers and a restrained scan. Lamp dips are around 32s; local intracloud light peaks around 28.6/54.6s. No detached lightning graphic or global exposure pulse.

First cloud-mask samples revealed pulled roof/antenna details; those were corrected before encoded previews. The rejected mask-pass stills/config are retained under history/first-mask-pass/. Assistant inspected source, native temporal samples and decoded stills, not continuous playback.

All layer endpoints/protected source checks, every 1800/5400 decoded frame/timestamp, regional/composite and quiet-neighbour seams, exact repeats and six contiguous-render boundary pictures passed. Four eight-second full-frame tests cover clouds, tower, transit and composite. Records: analytic-validation.json, short-tests.json, preview-validation.json, repeat-validation.json, chunk-join-validation.json and delivery-v5.json.

No new music received, so eight-minute music synchronization remains pending. Preview is silent 1280x720/30fps, not a 4K or long final. Earlier versions remain preserved. New media/records are local, uncommitted and unpushed.

Reproduce with existing Python runtime plus PYTHONPATH=G:/AI/youtube/.runtime/scene-tools: check_v5.py, render_parallel.py, render_spirewatch.py, check_chunk_joins.py. Config is scene-plan-v5.json. Rendering refuses existing destinations. Native artwork is 1672x941; any eventual 4K delivery is an upscale. Preserve clean scene loops and apply the established Colony opening once during final assembly.
