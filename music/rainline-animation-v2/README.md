# Rainline Relay — revised animation v2

2026-10-04. V1 was not accepted: the user reported poor window masking, requested better rain, flickering lights and antenna lights, and questioned whether the water moved. This revision is a new review candidate, not an approved final.

- [20-second silent 720p/30 fps preview](rainline-relay-v2-preview-20s.mp4)
- [60-second review: three exact repeats](rainline-relay-v2-three-loops-60s.mp4)
- [Water alone, eight seconds](water-isolated-v2-8s.mp4)
- [Rain alone, eight seconds](rain-isolated-v2-8s.mp4)
- [Habitat and walkway lights alone](lights-isolated-v2-8s.mp4)
- [Antenna lights alone](beacons-isolated-v2-8s.mp4)
- [Mask overlay](mask-review.png)
- [Delivery validation](delivery-v2.json)

## Changes

Source-coordinate crop inspection found the main cabin's lower-right glass boundary cut diagonally across valid water in v1; the side panes also needed corrected top/bottom edges. V2 traces those glass limits and maps complete habitat panes around the bezels and central divider. Luminous interiors dim with restrained spill; dark details are less affected. The near window is no longer a partial rectangle overlapping the tree. Window dim events remain staggered, with additional short, uneven flickers; one walkway practical also flickers occasionally. The desk lamp stays steady.

Two small red beacons are anchored to visible antenna tips at source (1013,231) and (1365,284). They have separate five/four-second pulse periods and phases, with softened transitions and local halos. No large lens flare or global exposure change.

Rain now uses three depth groups, faster falls, longer tapered trails and independent seeded arrivals. Far rain stays behind mapped architecture; nearer rain is an optical overlay in front of exterior objects but behind cabin frames and equipment. The source's static rain remains a limitation: this revision does not remove or move every baked-in streak.

Water retains the 24-wave reconstructed reflection method, with broader waves, stronger coherent displacement and revised speed. This is still a 2D approximation. Water boundaries, roots, three walkway posts, floating vegetation and the foreground plant are remapped to the actual source, rather than applying the original broad exclusions or treating every green reflection as solid vegetation. Source, room and existing scene renderers are preserved. Mist and radio activity continue as supporting layers.

## Validation and next decision

Four isolated eight-second full-composition clips preceded the composite. Per-layer endpoint/seam checks, finite source frames and protected pixels passed. All 600 composite and 1800 review frames decoded with sequential timestamps; encoded regional/composite seam checks passed and the review's three decoded repetitions exactly match the preview. No duplicated endpoint. Reports bind source/config/code/dependency/mask hashes.

Assistant inspected source grids, masks, temporal samples and decoded stills, not continuous playback. User normal-speed review remains necessary for rain readability, believable water speed, edge quality and restraint of lights. No 4K export, soundtrack or long assembly is produced for scene 08 yet. The sixty-second review repeats the twenty-second draft; it is not a unique minute.

`render_rainline.py --stage samples`, then `--stage isolated`, then `--stage preview`. Optional `--config` accepts a subsequent scene-plan path; outputs remain protected against overwrite. Use the existing Python runtime with PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. `build_v2.py` captures the structural compositor changes from the preserved v1 implementation. V1 remains available in ../rainline-animation-v1/. No credits, commit or push.
