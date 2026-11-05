"""Retain V3 exactly outside the added panes, tower emitters and road footprint."""
import json
import numpy as np

from render_scene import HERE, ROOT, Scene, base, region, sha

previous = json.loads((ROOT/'music/crater-rim-animation-v3/scene-plan.json').read_text())
current = json.loads((HERE/'scene-plan.json').read_text())
for key, value in previous.items():
    if key not in ['version', 'previous_delivery', 'design_notes']:
        assert current[key] == value, ('prior setting changed', key)
assert sha(HERE/'v3_renderer_snapshot.py') == sha(ROOT/'music/crater-rim-animation-v3/render_scene.py')
assert sha(HERE/'v2_renderer_snapshot.py') == sha(ROOT/'music/crater-rim-animation-v3/v2_renderer_snapshot.py')
old, new = base.Scene(), Scene()
additions = np.zeros(new.base.shape[:2], bool)
for name in ['village_lights', 'sun_glare', 'traffic']:
    additions[region(new.rois[name])] |= new.masks[name] > 0
times = [0, 7.8, 14.3, 19, 21.8, 25, 44.4, 45.1, 48.5, 56, 59+29/30]
for t in times:
    before, after = old.frame(t), new.frame(t)
    assert np.array_equal(before[~additions], after[~additions]), ('outside additions', t)
    for name in ['clouds', 'haze', 'shadows', 'survey', 'windows', 'village', 'lamp']:
        assert np.array_equal(old.frame(t, name), new.frame(t, name)), (name, t)
# Both passages are absent across the loop seam; source geometry handles their visibility.
assert all(new.vehicle_state(t, e) is None for e in new.c['traffic']['events'] for t in [0, 59.99])
assert new.glare_amount(0) == new.glare_amount(30) == 0
assert new.glare_amount(19.8) > .1
report = {'sample_times': times, 'all_seven_prior_layers_pixel_exact': True,
          'prior_legacy_settings_equal': True, 'prior_renderer_snapshots_byte_identical': True,
          'composite_outside_three_new_footprints_pixel_exact': True,
          'traffic_absent_at_loop_join': True, 'glare_has_quiet_gaps': True,
          'source_and_frozen_inputs': new.fingerprint(), 'script_sha256': sha(__file__)}
(HERE/'retained-layer-validation.json').write_text(json.dumps(report, indent=2)+'\n')
print('All seven V3 layers and pixels outside V4 additions retained at eleven sampled states', flush=True)
