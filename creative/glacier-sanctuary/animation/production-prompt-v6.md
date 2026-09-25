# Glacier Sanctuary v6 — heavier snow, irregular lamps, intact water

User requested heavier snow and more exterior flicker, rejected water again, and challenged pipeline efficiency. Do not claim another water model is realistic without review.

Snow count210 ->326 (approximately55% more), same speed/size/opacity ranges and seed. Fog, roof exhaust, upper lantern and annex event remain unchanged; compare their isolated pixels against v5.

Water: stop remapping the photographed surface. Preserve all original water pixels except32 sparse soft reflection glints, each9–28 source pixels wide and0.6–1.4 high, moving at6px/s with gradual appearance/disappearance. Maximum alpha .12. Ice/shore exclusion retained. This is a conservative reflection overlay, not a fluid simulation. Judge whether it is preferable to the rejected distortion; no success claim from metrics.

Exterior lights: retain warm halos and snow pools but add occasional short, staggered dips (0.20–0.65s with smooth transitions). Couple lamp-core dimming and associated halo/spill using the same phase. Avoid sustained rapid strobing. Keep main facility lighting steady apart from existing authorized events.

Pipeline delivered: reusable creative/effect-presets.json, scripts/apply_scene_presets.py, renderer --layers selection and --compare-config full-size stacked comparison. These reduce tuning/review overhead but do not automatically map masks for a new image. Source-scene geometry still requires deliberate setup.

Reproduce presets from v5 with apply_scene_presets.py SOURCE NEW_OUTPUT snow_heavier water_still_glints exterior_irregular_flicker. This applies relative snow density once; use an unchanged source config rather than repeatedly applying it. Render with render_glacier.py --config creative/glacier-sanctuary/animation/scene-plan-v6.json --output NEW_REVIEW_FOLDER. Add --layers water --compare-config creative/glacier-sanctuary/animation/scene-plan-v5.json for a full-size comparison: v5 top, v6 bottom. Eight-second study, not seamless.
