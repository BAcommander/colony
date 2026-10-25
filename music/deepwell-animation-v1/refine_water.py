"""Preserve the broad-wave study and select the finer brine-specific settings."""
from render_deepwell import *
import shutil
if (H/'water-fine-isolated-validation.json').exists():raise RuntimeError('Fine water is already frozen; preserve the study and make a new revision for further changes.')
archive=H/'history'/'broad-water-study';archive.mkdir(exist_ok=True)
for name in ['scene-plan-v1.json','analytic-validation.json','isolated-validation.json','render_deepwell.py','deepwell-water-isolated-8s.mp4','mask-review.png']:
 p=H/name
 if p.exists():shutil.copy2(p,archive/name)
for p in H.glob('sample-*.png'):shutil.copy2(p,archive/p.name)
c=json.loads((H/'scene-plan-v1.json').read_text());c['water']=json.loads((H/'water-detail-proposed-config.json').read_text());write_json('scene-plan-v1.json',c)
s=Deepwell();samples(s)
out=H/'deepwell-water-fine-isolated-8s.mp4';item=encode(s,out,8,'water');item['validation'],_=decode_verify(s,out,240)
write_json('water-fine-isolated-validation.json',{'fingerprint':s.fingerprint(),'clip':item,'reason':'The broad study softened source reflections. Shorter, filtered wind waves retain finer brine detail. Speed/strength changes are scene-specific; no inherited artistic approval.','unchanged_secondary_isolates':'deepwell-sky-isolated-8s.mp4 and deepwell-screen-isolated-8s.mp4 were rendered with the same source, masks and layer code. Their original configuration/fingerprint and complete validation are retained in history/broad-water-study/isolated-validation.json. Only water settings changed.'})
print('Fine water sample and isolated validation complete',flush=True)
