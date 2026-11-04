# Below the Snowline — V4 repair and cannon-light review

User feedback,2026-11-03: V3 console lights looked fake, the flying craft needed a more realistic Star Wars influence, fog showed a horizontal line, and mountain/ice geometry tore while the sky moved. User also requested cannon charging and lights on radar/mast structures. All four supplied screenshots are preserved in `feedback/`. V3 is not treated as artistically approved.

## Review

`Below-the-Snowline-v4-with-V6-audio-2min.mp4` is the new continuous120-second720p30 candidate. It uses the same V5 source art and byte-identical two-minute V6 audio excerpt as V3. QP0 H.264 and explicit BT.709 metadata avoid the lossy segment changes caught during V3 development. No final seamless-loop, full4K export, listening approval or publication is implied.

## Repairs and additions

1. Console: only the existing red/amber lens faces are relit by scaling their original textured RGB. No solid colour fills, invented cyan tiles or enlarged switch-face overlays. Original bezels and unlit controls remain in the source.
2. Shuttle: a new detailed Imperial Lambda-class inspired RGBA asset replaces the polygon silhouette. Premultiplied alpha, subpixel placement, atmospheric colour blending and two different viewing sizes integrate it into the sky. Passes are0:24–1:02 and1:26–1:54. Generated master alpha is preserved.
3. Fog line: integer Fourier modes make the fog textures periodic in both directions, removing the discontinuity exposed by the previous wrapped noise. Ravine-mask falloff is also broader.
4. Sky tearing: the cloud-safe region is remapped from the actual source geometry, with a substantial feather/clearance from mountains, ice, frost and equipment. Both source sampling and output coverage use the conservative region. Named landmarks and every pixel outside that region remain exact in isolated cloud checks across ten phases. `cloud-mask-review.png` visualises the region; its coloured overlay is diagnostic only.
5. Cannon: two slow charge cycles,0:31–0:56 and1:28–1:53. Small amber power nodes feed restrained cyan barrel strips and muzzle cores. No weapon discharge or new audio is added.
6. Structure lights: beacons are mapped to the dish feed-mast tip, tower support joint and right roof sensor post. Positions, phases and colours are in `geometry-v4.json`.

## Shuttle asset and exact prompt

Built-in `image_gen` was used once, with `transparent_background=true`.

- [Generated RGBA master](assets/lambda-shuttle-master.png)
- [Exact generation prompt](assets/shuttle-prompt.txt)

The original returned image is copied byte-for-byte into this project. It is a generated interpretation, not a claimed canon-perfect production model. Source landscape and original controls were not regenerated. No external model/API runner was used; generation cost was not independently recorded.

## Audio and validation

Audio is unchanged from V3:3:00–5:00 of the V6 unfaded lossless master, +0.4dB once,0.5-second entry/two-second exit review fades. Existing music, radio, wind, creak, ventilation and snow are already included. The snow event remains0:44.783–0:54.783. No SFX was stacked on top.

`audit_repairs.py` checks the reported geometry/material/texture defects and produces `repair-validation.json`. `render_v4.py samples` creates temporal stills; `render_v4.py render` renders six contiguous segments; `finish_review.py` assembles and fully decodes the video/audio, checks timestamps/colour/protected pixels/joins, compares decoded pictures with native frames and compares the complete AAC with the expected lossless excerpt. `delivery-validation.json` is produced only after those checks pass. `cache/` contains rebuildable intermediate outputs and inspection crops.

Assistant inspection covers source-coordinate crops, generated-asset transparency, temporal/decoded stills and technical checks. Continuous playback/listening and user artistic approval remain distinct. Original source, V2/V3 previews and full V6 soundtrack are retained. This work stays on main; no commit/push was requested in this turn.
