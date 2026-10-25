"""Preserve the full internal candidate before fixing salt drift at a support."""
from pathlib import Path
import shutil,json
H=Path(__file__).resolve().parent;A=H/'history'/'support-occlusion-fix';assert not A.exists();A.mkdir(parents=True)
for name in ['render_deepwell_v2.py','scene-plan-v2.json','analytic-validation.json','preview-validation.json','isolated-validation.json','isolated-refined-weather-validation.json','mask-review.png','pipeline-overlap-diagnosis.json']:
 shutil.copy2(H/name,A/name)
for p in list(H.glob('sample-*.png'))+list(H.glob('decoded-*.png')):shutil.copy2(p,A/p.name)
for name in ['Deepwell-v2-preview-20s.mp4','Deepwell-v2-three-loops-60s.mp4','deepwell-v2-atmosphere-isolated-8s.mp4']:
 source=(H/name).resolve();assert source.is_relative_to(H.resolve());shutil.move(str(source),str(A/name))
(A/'README.txt').write_text('Internal candidate, not delivered/approved. All encode/decode, native/YUV controls and seam checks passed, but an extra named-pipeline protection check found 34 source pixels at bbox [896,350,907,354] changed by salt_far at t=4. The mineral-surface drift mask omitted pipeline support occlusion (the air layers already had it). Fix the mask; retain the check and add it to every rendered frame. The source plate and all other effects are unchanged. Preserve these videos/records as history. Sky/water/habitation isolates remain at package root, with original hashes and final-config direct native/YUV controls.\n')
print('Full internal candidate preserved before exact support-occlusion correction.')
