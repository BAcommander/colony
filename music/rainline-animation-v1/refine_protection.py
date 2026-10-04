from pathlib import Path
import json,shutil
H=Path(__file__).resolve().parent
history=H/'initial-mask-review';history.mkdir(exist_ok=True)
for name in ['scene-plan-v1.json','mask-review.png','analytic-validation.json']:
 assert not (history/name).exists();shutil.copy2(H/name,history/name)
p=H/'scene-plan-v1.json';c=json.loads(p.read_text())
c['interior_occluders']=[[[174,347],[204,347],[213,384],[228,405],[252,437],[246,457],[185,463],[154,447],[156,407],[177,387]],[[154,409],[185,395],[191,404],[154,421]],[[373,500],[477,503],[481,607],[371,607]],[[305,487],[376,486],[380,564],[303,564]],[[213,521],[318,520],[320,550],[211,550]]]
c['protected_exterior'].append([[268,0],[315,0],[304,92],[309,174],[331,208],[314,260],[305,334],[335,399],[282,416],[269,360],[279,279],[260,234],[264,180],[275,108]])
c['notes'].append('Initial mask review caught interior lamp/equipment occlusion; explicit exclusions applied before any motion test. Desk lamp remains steady.')
p.write_text(json.dumps(c,indent=2)+'\n')
# Keep setup reproduction consistent with the refined plan.
source=H/'setup_scene.py';s=source.read_text();marker="target=H/'scene-plan-v1.json'"
insert='c["interior_occluders"]='+repr(c['interior_occluders'])+'\nc["protected_exterior"].append('+repr(c['protected_exterior'][-1])+')\nc["notes"].append('+repr(c['notes'][-1])+')\n'
assert marker in s;source.write_text(s.replace(marker,insert+marker))
print('Foreground room occluders and near left trunk protected')
