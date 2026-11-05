# Crater Rim Survey — final visibility polish candidate, V5

Built 2026-11-05 after the user said the V4 glints and tower beacons were small and far away and hard to see, asked to push them, and requested one final improvement round. “Push” was interpreted in commentary as increased visual strength; no Git push is implied. This is a final polish candidate, with user playback acceptance still pending.

[Complete minute](Crater-Rim-Survey-v5-60s-loop.mp4) · [Normal-size before/after](Crater-Rim-Survey-v4-vs-v5-normal-size-20s.mp4) · [Village detail](Crater-Rim-Survey-v5-village-detail-12s.mp4) · [Road detail](Crater-Rim-Survey-v5-road-detail-20s.mp4) · [Three-repeat join review](Crater-Rim-Survey-v5-3-loops-180s.mp4)

The normal-size comparison shows V4 for the first ten seconds and V5 for the second ten. Both use scene time 0:17–0:27 at the same 1280×720 size. Every decoded comparison picture matches its source segment; the comparison has no zoom or extra effect amplification. This provides a useful viewing check beyond enlarged crops or changed-pixel measurements.

The three beacons retain their corrected source anchors and onset times. V5 adds small bright centres within the coloured emitters, a larger bounded halo and a local mount response. Pulse duration rises from 1.29 to 2.72 seconds, with longer holds. Coloured daytime points alone had limited luminance contrast; the brighter centres give them a better chance of surviving reduction to 720p. These are source-specific settings, not a universally accepted beacon preset.

Greenhouse reflections cover more of the curved glass, with broader lobes, a soft connecting reflection, stronger local radiance and longer holds. They remain inside the existing glass mask, retain the bright pane frames and respond to the existing cloud shadow. First sunbreak: 0:17–0:25.7, plateau around 0:19.3–0:21.9. Second: 0:43–0:51.6, plateau around 0:45.6–0:47.6. Camera and global exposure remain fixed.

The final additional polish is traffic readability. Vehicles get clearer pale/rust roof colours, darker windscreens and slightly larger footprints within the existing road scale. Small running lenses stay attached to their bodies. Premultiplied colour and coverage now resample together before compositing, avoiding the extra dark edge caused by averaging straight colour against transparent black and then applying alpha again. V4's corrected route, headings, two passage schedules and solid road/rock/vegetation/ledge occlusion remain unchanged.

No new effect layers were introduced. All seven V3 weather, habitation, display and lamp layers remain exact at eleven sampled times; so does the full composite outside the three polished footprints. [Retained-layer checks](retained-layer-validation.json) · [Settings](scene-plan.json) · [Full delivery checks](delivery.json) · [Comparison verification](comparison-validation.json) · [Detail checks](detail-review-validation.json). Original artwork and V4 remain preserved.

This is a silent 1280×720/30fps review. Native source detail is 1672×941; a later 4K master will upscale it. Native/mask and colour-aware decoded temporal stills are inspection evidence, not an assistant continuous-playback verdict. User artistic approval remains pending. No new music, SFX, artwork generation, paid service, upload, commit or push was included. Review/intermediate MP4s stay local under the storage policy.

Reproduce in fresh MP4 destinations with NumPy, Pillow, OpenCV and imageio-ffmpeg:

```powershell
python music/crater-rim-animation-v5/render_scene.py samples
python music/crater-rim-animation-v5/check_retained_layers.py
python music/crater-rim-animation-v5/render_scene.py full
python music/crater-rim-animation-v5/validate_delivery.py
python music/crater-rim-animation-v5/make_detail_reviews.py
python music/crater-rim-animation-v5/make_comparison_review.py
```

## Longer version and backup authority

The user subsequently gave positive V5 feedback (“ok brilliant”) and explicitly requested saving the longer-version details, then committing and pushing. [Resume guide](LONG_VERSION.md), [proposed600s plan](long-version-plan.json), [pinned environment](requirements-resume.txt) and [baseline/plan check](continuation-plan-validation.json) preserve the next steps. The long renderer is unbuilt; audio and final runtime are unselected. The earlier no-push wording above describes the original render session. The current selected backup is recorded in [the checkpoint package](../production-backup-2026-11-05-crater-rim/README.md); actual remote evidence belongs in its local verification receipt.
