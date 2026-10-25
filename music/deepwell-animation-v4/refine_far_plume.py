"""Keep the far vent's visible material against sky rather than pale cliff."""
from pathlib import Path
import json,shutil
H=Path(__file__).resolve().parent;A=H/'history'/'far-plume-contrast-study';assert not A.exists();A.mkdir(parents=True)
for name in ['scene-plan-v4.json','analytic-validation.json','preview-size-4.000s.png','preview-size-10.000s.png','preview-size-16.000s.png']:
 shutil.copy2(H/name,A/name)
c=json.loads((H/'scene-plan-v4.json').read_text());far=next(q for q in c['steam'] if q['name']=='tank_steam_far');far.update(drift=8.0,curl=8.5,opacity=1.4,baseline=.76)
(H/'scene-plan-v4.json').write_text(json.dumps(c,indent=2)+'\n')
(A/'README.txt').write_text('Internal full-composition 720p study, not delivered or user-approved. Rolling steam and purple lights are clearly different from v3 in the inspected stills. The far-right plume drifted into the pale cliff, reducing material/background contrast despite greater optical depth. Keep its roof anchor fixed; reduce its rightward drift/curl into the clearer grey-sky area and retain a more persistent source. This is a source-specific path/contrast correction, not a measured artistic improvement or a promise of physical flow simulation.\n')
print('Far roof vent anchor retained; flow and contrast selection refined.')
