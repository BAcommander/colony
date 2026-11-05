# Crater Rim Survey — village activity and desk-lamp flicker, V3

Updated 2026-11-05 after the user highlighted the village and desk lamp and requested movement/effects in the settlement and occasional room-light flicker.

[Complete minute](Crater-Rim-Survey-v3-60s-loop.mp4) · [Three-repeat join review](Crater-Rim-Survey-v3-3-loops-180s.mp4) · [Village detail](Crater-Rim-Survey-v3-village-detail-10s.mp4) · [Lamp detail](Crater-Rim-Survey-v3-lamp-detail-8s.mp4)

Two soft rooftop/greenhouse ventilation plumes rise and drift right. Overlapping ten-second puffs have different seeded shapes and hidden local births/deaths, with a sixty-second overall schedule. Two small figures cross the existing terrace paths at separate times, with foot contact, subtle alternating steps and source-mapped planter occlusion. Their size follows the distant doorways. Emissions from these rooftop features are an artistic interpretation of the still, rather than confirmed equipment function.

The desk lamp has two brief flicker clusters around 0:14 and 0:44. The first has two uneven dips, the second one dip. The full white emitter, nearby warm shade lip, wall pool, desk contribution and thermos-side reflection share the same power envelope. Dimming occurs in linear light. Inward source masks and a chair exclusion preserve the daylight, exterior, window frame and foreground blanket. The lamp remains exactly at the previous source level between events.

V2's clouds, three-depth basin haze, terrain shadows, radar/telemetry and existing window holds are retained. [Regression checks](retained-layer-validation.json) compare all five old layers and the full composite outside the two new footprints at nine times, including lamp dips. The original clean art is unchanged; V2's renderer and transport helpers are frozen here for reproducibility. [Settings and anchors](scene-plan.json) · [Renderer](render_scene.py) · [Complete delivery checks](delivery.json).

This is a silent 1280×720/30fps review candidate. The native plate is 1672×941; later 4K delivery will upscale it. Enlarged detail videos are crops of the actual encoded minute, with no change to effect strengths or timing. [Detail verification](detail-review-validation.json). Masks and native/decoded temporal stills were inspected; user playback verdict remains pending. No new music, SFX, artwork generation, paid service, publication, commit or push was included.

Reproduce in fresh MP4 destinations using the existing Python environment with NumPy, Pillow, OpenCV and imageio-ffmpeg:

```powershell
python music/crater-rim-animation-v3/render_scene.py samples
python music/crater-rim-animation-v3/render_scene.py tests
python music/crater-rim-animation-v3/check_retained_layers.py
python music/crater-rim-animation-v3/render_scene.py full
python music/crater-rim-animation-v3/validate_delivery.py
python music/crater-rim-animation-v3/make_detail_reviews.py
```

The first local plume pass, before broader ten-second formations and shade-lip coupling, remains under `history/first-local-pass/`. Previous V2 and V1 packages remain intact. Review/diagnostic MP4s stay local under the storage policy; no remote backup is implied.
