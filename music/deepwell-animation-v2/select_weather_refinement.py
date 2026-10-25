"""Preserve internal soft-field study before selecting coherent moving forms."""
from pathlib import Path
import sys,json,shutil
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H/'baseline-snapshot'/'dependency-snapshot'))
sys.path.insert(0,r'C:\AI\ComfyUI\venv\Lib\site-packages')
from weather_refinement import refined_config
assert not (H/'history'/'soft-weather-study').exists(),'Preserve existing history'
A=H/'history'/'soft-weather-study';A.mkdir(parents=True)
for name in ['render_deepwell_v2.py','scene-plan-v2.json','analytic-validation.json','isolated-validation.json','mask-review.png']:
 shutil.copy2(H/name,A/name)
for p in H.glob('sample-*.png'):shutil.copy2(p,A/p.name)
for name in ['deepwell-v2-sky-isolated-8s.mp4','deepwell-v2-atmosphere-isolated-8s.mp4']:
 shutil.move(str(H/name),str(A/name))
c=refined_config(json.loads((H/'scene-plan-v2.json').read_text()));(H/'scene-plan-v2.json').write_text(json.dumps(c,indent=2)+'\n')
(A/'README.txt').write_text('Internal v2 study, not delivered or user-approved. Soft advected density technically passed but remained too faint in assistant still review (far-air one-second regional MAE around 0.03). Replaced by explicit moving, curling, locally fading wisps with terrain-guided centre-lines and brighter suspended mineral/brine material. Sharper source-cloud texture gives the planetary veil identifiable forms. Neither a pixel metric nor these assistant findings establish playback acceptance. Water and habitation clips remain unchanged in the v2 package; original full validation and renderer/config fingerprint are preserved here.\n')
print('Soft weather archived; coherent moving-form settings selected.')
