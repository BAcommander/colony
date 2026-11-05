"""Check exact retained layers and vehicle routes against the frozen V4 settings."""
import json
import numpy as np

from render_scene import HERE, ROOT, Scene, region, sha
import v4_renderer_snapshot as previous_renderer
import v2_renderer_snapshot as source_base

assert sha(HERE/'v4_renderer_snapshot.py') == sha(ROOT/'music/crater-rim-animation-v4/render_scene.py')
assert sha(HERE/'scene-plan-v4-snapshot.json') == sha(ROOT/'music/crater-rim-animation-v4/scene-plan.json')
current_plan = source_base.PLAN_PATH
try:
    source_base.PLAN_PATH = HERE/'scene-plan-v4-snapshot.json'
    old = previous_renderer.Scene()
finally:
    source_base.PLAN_PATH = current_plan
new = Scene()
for name in ['lamp', 'village', 'clouds', 'haze_layers', 'shadows', 'survey_display', 'colony_windows']:
    if name in old.c:
        assert old.c[name] == new.c[name], name
assert old.c['traffic']['route'] == new.c['traffic']['route']
assert np.array_equal(old.masks['traffic'], new.masks['traffic'])
for old_event, new_event in zip(old.c['traffic']['events'], new.c['traffic']['events']):
    for key in ['time', 'seconds', 'reverse']:
        assert old_event[key] == new_event[key]
added = np.zeros(new.base.shape[:2], bool)
for name in ['village_lights', 'sun_glare', 'traffic']:
    for scene in [old, new]:
        added[region(scene.rois[name])] |= scene.masks[name] > 0
times = [0, 7.97, 14.3, 19.8, 21.8, 25, 44.4, 45.1, 48.5, 56, 59+29/30]
for t in times:
    a, b = old.frame(t), new.frame(t)
    assert np.array_equal(a[~added], b[~added]), ('outside polish footprints', t)
    for name in ['clouds', 'haze', 'shadows', 'survey', 'windows', 'village', 'lamp']:
        assert np.array_equal(old.frame(t, name), new.frame(t, name)), (name, t)
    for old_event, new_event in zip(old.c['traffic']['events'], new.c['traffic']['events']):
        before, after = old.vehicle_state(t, old_event), new.vehicle_state(t, new_event)
        if before is None:
            assert after is None
        else:
            assert np.array_equal(before[0], after[0]) and np.array_equal(before[1], after[1])
report = {'sample_times_seconds': times, 'all_seven_retained_layers_pixel_exact': True,
          'full_composite_outside_polished_effects_pixel_exact': True,
          'vehicle_route_heading_timing_and_occlusion_masks_unchanged': True,
          'v4_source_renderer_and_plan_snapshots_exact': True,
          'frozen_inputs': new.fingerprint(), 'verification_script_sha256': sha(__file__)}
(HERE/'retained-layer-validation.json').write_text(json.dumps(report, indent=2)+'\n')
print('Seven prior layers retained at eleven times; road route, headings, timing and occlusion unchanged', flush=True)
