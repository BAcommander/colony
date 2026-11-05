"""Verify V2 preservation outside the specifically authorized V3 additions."""
import importlib.util
import json
import sys

import numpy as np

from render_scene import HERE, ROOT, Scene, region, sha

path = ROOT/'music/crater-rim-animation-v2/render_scene.py'
spec = importlib.util.spec_from_file_location('prior_crater_v2', path)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
old, new = module.Scene(), Scene()
additions = np.zeros(new.base.shape[:2], bool)
for name in ['village', 'lamp']:
    additions[region(new.rois[name])] |= new.masks[name] > 0
times = [0, 6, 14.3, 22, 28, 40, 44.4, 52, 59+29/30]
for t in times:
    before, after = old.frame(t), new.frame(t)
    assert np.array_equal(before[~additions], after[~additions]), ('outside new additions', t)
    for name in ['clouds', 'haze', 'shadows', 'survey', 'windows']:
        assert np.array_equal(old.frame(t, name), new.frame(t, name)), (name, t)
assert new.lamp_amount(14.3) > .7
assert new.lamp_amount(44.4) > .6
assert new.lamp_amount(0) == new.lamp_amount(30) == new.lamp_amount(59.9) == 0
# An undimmed source white core cannot be hidden by the warm-spill colour key.
core = new.lamp_parts['core'] > .99
source = new.base[region(new.rois['lamp'])]
dimmed = new.frame(14.3, 'lamp')[region(new.rois['lamp'])]
white = core & (source.min(axis=2) > 190)
assert white.any() and np.all(dimmed[white].max(axis=1) < source[white].max(axis=1))
for name in ['wall', 'desk', 'reflection', 'shade_lip']:
    assert new.lamp_parts[name].max() > 0
report = {'times_seconds': times, 'all_five_prior_layers_pixel_exact': True,
          'full_composite_outside_new_additions_pixel_exact': True,
          'source_white_core_and_coupled_spill_checked': True,
          'v2_renderer_sha256': sha(path), 'v3_frozen_inputs': new.fingerprint(),
          'verification_script_sha256': sha(__file__)}
(HERE/'retained-layer-validation.json').write_text(json.dumps(report, indent=2)+'\n')
print('V2 weather, display and windows retained exactly at nine sampled times; lamp core/spill checks passed', flush=True)
