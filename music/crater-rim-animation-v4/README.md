# Crater Rim Survey — greenhouse glints, tower beacons and road traffic, V4

Latest user feedback, 2026-11-05: glints and beacons are small/distant and hard to see. [V5](../crater-rim-animation-v5/README.md) supplies the stronger final-round candidate and a source-exact normal-size before/after. V4 is preserved as the comparison baseline.

Built 2026-11-05 after the user requested occasional sun glare, more village/tower lights and road traffic, saying “we're getting closer.” This expresses positive direction; V4 still needs its own playback verdict.

[Complete minute](Crater-Rim-Survey-v4-60s-loop.mp4) · [Three-repeat review](Crater-Rim-Survey-v4-3-loops-180s.mp4) · [Village detail](Crater-Rim-Survey-v4-village-detail-12s.mp4) · [Road detail](Crater-Rim-Survey-v4-road-detail-20s.mp4)

Two brief sunbreaks brighten fixed reflection patches on the greenhouse's curved glass around 0:19–0:21 and 0:46. Existing pane-frame brightness is largely retained; an inward glass mask confines the glints, and the existing terrain shadow attenuates their strength. These are local reflections with unchanged camera and global exposure. The sun-glare request was interpreted as an occasional greenhouse reflection.

Three small red/amber warning beacons sit on the existing mast/pipe structures and pulse independently. Their settings, source-coordinate anchors and round halos are in the [scene plan](scene-plan.json). Two utility rovers follow the winding asphalt, one down during 0:04–0:29 and another up during 0:32–0:57. Their world-ground footprint, cabin, wheels, small attached running lights and contact shadow scale with depth and turn with the road. Rock, road, foreground vegetation and ledge masks hide the entrance/exit while the vehicles retain full opacity.

Source-scale inspection caught the first route following the inside curb after the bend and crossing vegetation later. The corrected centerline stays on the asphalt; review the road close-up for remaining geometry issues. Enlarging the complete tower context also caught beacon coordinates based on incomplete crops. The corrected points are physically attached to the existing structures. Initial plans/samples and the internal first test remain under `history/`.

All V3 clouds, haze, shadows, survey display, window holds, ventilation plumes, terrace walkers and coupled lamp flicker are retained. [Regression checks](retained-layer-validation.json) compare all seven prior isolated layers and the composite outside the three new footprints at eleven sampled states. Frozen V3/V2 renderer snapshots are byte-identical to the prior source. [Full delivery checks](delivery.json) cover source sampling, every native protected pixel during rendering, loop steps, all decoded frames/timestamps, exact native-to-YUV controls including glint/beacon/traffic states, and exact three-loop repetitions. [Detail checks](detail-review-validation.json) bind both enlarged crops to the actual minute.

The review is silent 1280×720/30fps. Clean artwork remains native 1672×941 and unchanged. Native/mask/colour-correct decoded temporal stills were inspected; no assistant continuous-playback verdict or user acceptance is inferred. A later 4K master will upscale the original detail. No soundtrack/SFX change, paid service, generated artwork, upload, commit or push was included. Repeated and internal diagnostic videos stay local under the storage policy.

Reproduce with NumPy, Pillow, OpenCV and imageio-ffmpeg in fresh MP4 destinations:

```powershell
python music/crater-rim-animation-v4/render_scene.py samples
python music/crater-rim-animation-v4/check_retained_layers.py
python music/crater-rim-animation-v4/render_scene.py full
python music/crater-rim-animation-v4/validate_delivery.py
python music/crater-rim-animation-v4/make_detail_reviews.py
```
