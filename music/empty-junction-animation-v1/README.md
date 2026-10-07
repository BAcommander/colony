# The Empty Junction — animation v1

Historical v1 delivery: genuine sixty-second silent 1280x720/30 fps candidate and a three-repeat 180-second review. User called it decent but requested substantial improvements. The current [v2 candidate](../empty-junction-animation-v2/README.md) implements those changes and awaits playback review. V1 code, configuration and media are preserved; no full artistic approval or 4K is implied.

- [Complete minute](empty-junction-v1-preview-60s.mp4)
- [Three-minute join review](empty-junction-v1-three-loops-180s.mp4)
- [Delivery record](delivery-v1.json)
- [Configuration](scene-plan-v1.json)
- [Executed production brief](../../final/11-empty-junction/animation-production-prompt-v1.txt)

## Visible actions

Existing cloud material travels rightward above the mineral pass. Upper groups move at 3.4 native pixels/second and horizon groups at 2.1; their narrow profiles remain subordinate to the mineral towers. A stationary, smoothly reconstructed sky gradient replaces the original cloud radiance beneath moving cloud groups. The image is an optical approximation with independent zero-opacity local renewal, not a physical atmosphere.

A broken pale mist bank crosses the far pass at 2.6 native pixels/second. Separate wisps travel at 4.0 native pixels/second across the left and right cuttings behind the freight district. Source-specific masks protect the buildings, gallery and antenna. The mist uses remapped Saltline optical-density/lifecycle helpers, with new colours, shapes, speeds, source anchors and terrain masks. Fresh formations sustain the minute; the foreground platform and rails stay clear.

Three small freight-hall window groups, two gallery groups and one upper room have independent held dim states. The cabin door glazing has only a mild local change. The hooded doorway lamp, two freight-yard lights and right service lamp have sparse events with local spill. The roof amber light has two brief double acknowledgements across the minute; the existing trackside amber signal stays steady. Many windows and lamps remain steady.

The camera, trains, points, doors, buildings and mineral silhouettes remain fixed. No invented display, added LEDs, stars, aurora, moving train or foreground precipitation. The upper-right pipe appears capped, so the optional plume was omitted. Fine turnout mechanics are ambiguous in the approved still; this animation preserves them and makes no engineering-accuracy claim.

## Source and implementation

Immutable source: final/11-empty-junction/artwork-v2.png, native 1672x941, SHA-256 ed7b02777c1dcc35504bc0628739688b56515f09ece89d58f299f2dd6013a4be. This is the approved clean artwork, not the thumbnail.

The renderer uses one configuration and a deterministic sixty-second clock. Sky/mist lifetimes have independent phases and locally invisible resets. No full-frame dissolve, reversed weather, slowed prototype or three copied twenty-second clips. The 180-second review is explicitly three repetitions of the unique minute.

Initial issues corrected before full delivery:
- A coarse skyline selection sampled small rock fragments. Source-colour refinement near the boundary excludes those pixels from both cloud extraction and output.
- A first global colour gate also protected dark cloud cores, leaving them static. Restricting the gate to the skyline restored transport; encoded feature tracking checks the correction.
- Hard source cutouts could carry the former occluder's edge into the sky. Only atmospheric residual is extrapolated over missing sample areas; protected source-object pixels are never copied.
- The first mist colour/contrast was too close to existing valley haze. Revised pale mist gives the moving formations clearer separation.
- Lamp masks initially left thin bright edges. Complete emitters and stronger near-core halo coupling corrected the forced-dim inspection.

The initial candidates remain in history/. None was user-approved. Main source artwork and other scene renderers were not edited.

## Evidence and acceptance

analytic-validation.json records periodic states, individual layer seam checks, velocity diagnostics, distinct 0/20/40-second states, finite pixels and exact source protection outside active masks before encoding.

isolated-validation.json covers three ten-second full-composition tests at actual strength/speed: sky, pass weather and habitation. These are diagnostic excerpts, not the finished delivery.

preview-validation.json covers full 1,800/5,400-frame decodes, sequential timestamps, correct fps/dimensions, unchanged encoded regional/composite seam gates, no duplicate endpoint and exact decoded three-cycle identity.

coverage-delivery-validation.json checks five named weather regions through the last third of the minute, sample-exact protected structural regions, encoded cloud travel, actual light changes and silent video streams. Source/config/code/dependency/native-mask hashes bind the records.

The assistant inspected native source details, masks, forced-dim lights, normal-size temporal samples and decoded stills. Continuous playback was unavailable. Pixel differences, tracking and seam metrics are supporting technical evidence, not artistic acceptance. The user's full-preview verdict decides the result.

## Reproduction

From C:/Colony:

~~~powershell
python music/empty-junction-animation-v1/render_junction.py --stage samples
python music/empty-junction-animation-v1/render_junction.py --stage isolated
python music/empty-junction-animation-v1/render_junction.py --stage preview
python music/empty-junction-animation-v1/audit_delivery.py
~~~

Read the saved scene-plan-v1.json for routine rendering. build_plan.py records initial plan construction. Existing video destinations refuse overwrite; reproduce in a separate checkout without those outputs or use a new versioned destination. Preserve dependency bytes and compare fingerprints before reuse.

Local Python/NumPy/OpenCV/Pillow and FFmpeg only. No paid services, new model, soundtrack, long assembly, commit/push or remote backup in this production pass. After preview acceptance, export and validate a silent 3840x2160/30 fps minute using identical settings, explicitly upscaled from 1672x941.
