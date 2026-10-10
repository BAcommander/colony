# The Last Cable Station - animation plan v1

2026-10-03. Planning only, requested by the user. The approved v3 still was inspected at full composition and its hash/dimensions verified. No masks, renderer adapter, animation or motion acceptance have been produced. Music/transition is accepted separately.

## Intended result

A quiet operator booth overlooking a living, cloud-filled valley. Broad atmospheric movement should be visible at normal viewing size; occasional colony light changes and small console updates support it. The warm interior provides a steady foreground against the moving distance.

Source: `../artwork-v3-final.png`, 1672x941, SHA-256 `72fe97b682c4ff5de7ef577e2464163941c90a48fbf1268e4f8271e3afd97c37`. Use this clean approved plate, preserving its mineral colours and fine construction. Thumbnail pixels are not the animation source. Freeze the source; masks must be tied to this hash.

## Motion, in priority order

1. **Valley clouds — the principal motion.** Let broad cloud edges drift gently right through the central gap, behind the cable tower and beneath the far station. A separate, slightly quicker layer moves through the low right-hand ravine; the bright left-side cloud bank has its own phase. Keep the movement coherent with one overall wind direction, reducing apparent speed with distance. Start transport trials around 1.5-3 source pixels/second in the central valley and 2-4 in the closer ravine; these are tuning ranges, not accepted values. Preserve the cloud mass and textured edges rather than making the whole view milkier.
2. **Upper clouds — slower supporting landscape motion.** Move the existing sky cloud texture gently right at an initial 0.5-1.5 source pixels/second. The pale planet stays fixed. Remove planet, cliff and cable pixels from the sampled moving texture as well as protecting their final silhouettes, so no copied fragments drift across the sky.
3. **Habitat lights — occasional signs of occupation.** Select two or three existing window apertures on the far settlement after a source-resolution inspection. Most windows and the covered walkway stay steady. Give selected windows independent off/on holds, initially about 3-7 seconds within the twenty-second loop, with short eased transitions and small matching local spill. Mask the entire aperture, including bright cores. Check they read at 720p; do not compensate for tiny distant windows with exaggerated brightness.
4. **Console activity — restrained foreground support.** Confine sparse status-row changes to the right screen and a very soft occasional marker update to the left map screen. Preserve the original layout and brightness balance. No moving bezel, new readable text or bright scanning stripe. Keep the desk lamp steady to anchor the interior lighting.

## Geometry and depth

Keep camera, window framing, cables, tower, receiving building, parked cabin, cliff edges, rock texture, plants, desk, chair/jacket, mug, lamp and screen housings fixed. Clouds may pass in front of deliberately mapped distant terrain, but must not deform it. Nearby ledges, cables, the tower and settlement remain foreground occluders over relevant cloud layers.

Map the three window openings separately, then apply one shared exterior motion field through them so mullions do not create discontinuous drift. Restore interior silhouettes and fixed glass details over the exterior composite. The scene-plan bounding boxes are approximate planning extents, not completed masks; refine paths and thin-cable protection at source resolution before rendering.

The parked cable cabin stays stationary for v1. A later transit test would need a verified route, perspective scaling, a clean plate behind the cabin and credible occlusion at the terminal; it should be reviewed separately before inclusion. Its movement is not needed to establish the first atmospheric loop.

## Production order

1. Map source-bound window, sky, three cloud-depth, geometry-protection, aperture and screen masks. Inspect overlays at full composition and zoomed cable/roof/window edges.
2. Adapt the existing local NumPy/OpenCV/FFmpeg cloud-transport and lighting methods into a Cable Station adapter and one scene configuration. Reuse effect logic, never another scene's coordinates. Approved renderers remain unchanged.
3. Produce eight-second 720p isolated valley and sky tests at normal speed. The visible test is a recognizable cloud edge travelling across a named gap while cables and cliffs stay sharp. Set coherent shape and travel first, opacity last. Do not add console polish until the landscape movement reads.
4. Build a genuine **20-second, 30 fps, 1280x720 silent preview** with all layers, plus a three-repeat join preview. Use forward-moving staggered cloud lifetimes with zero-opacity resets; schedules wrap correctly. No reversed motion, duplicate endpoint or full-frame dissolve. Timing and layer parameters must be shared with the eventual master.
5. Review cloud visibility, ghosting, cliff/cable occlusion, stable room exposure, plausible lights and the join. Record actual playback or still inspection separately from user acceptance. If motion fails visually, fix that specific defect before 4K.
6. After preview acceptance, produce the **3840x2160/30 fps short master**, upscaled from the 1672x941 source. A genuine sixty-second version can be a later requested delivery; it must retain effect speeds and independently scheduled lights, not simply copy three twenty-second clips.
7. Once the short master and final upload duration are settled, extend the accepted Mineral Valley Transit soundtrack and assemble with Colony. Two hours remains a proposal, not a confirmed duration. Keep long media under ignored exports/.

## Required checks

- Unchanged source pixels outside permitted masks before encoding; inspect thin cables, planet rim, roofs, console borders and window frames.
- No NaNs, correct depth order and continuous layer states/velocities through the join.
- Full decode, exact 600 frames/20 seconds/30 fps, silent preview/master and sequential timestamps.
- Compare each encoded layer's last-to-first change with ordinary frame steps; separately check the composite seam. Numeric periodicity does not establish natural motion.
- Confirm repeated payload identity in the join preview. Preserve source/config/code hashes, settings, checks and exact user feedback. Version every export and keep originals.

This plan is saved locally. No render, paid generation, commit or push was performed for the planning request.
