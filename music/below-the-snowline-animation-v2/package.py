from pathlib import Path
import json,sys,hashlib,shutil,subprocess
from PIL import Image
H=Path(__file__).parent;R=Path('G:/AI/colony');D=R/'music/below-the-snowline-animation-v2';F=R/'final/13-below-the-snowline'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for n in ['analytic-validation.json','regression-validation.json','isolated-validation.json','preview-validation.json','direct-validation.json']:
 d=json.loads((H/n).read_text(encoding='utf-8-sig'));assert all(sha(H/p)==v for p,v in d['fingerprint'].items()),('Stale',n)
assert sha(H/'source.png')==sha(F/'ice-planet-retheme-v3/artwork-v5.png')
manifest={'date':'2026-10-25','status':'V2 animation and Hoth thumbnail candidates; technical checks passed; user review pending','user_approved':False,'source_sha256':sha(H/'source.png'),'dimensions':list(Image.open(H/'source.png').size),'method':'Local masked compositing; thumbnail generated separately with built-in imagegen','thumbnail':{'master':'thumbnail-v2.png','upload':'thumbnail-v2.jpg','prompt':'thumbnail-prompt.txt','reference':'music/spirewatch-animation-v4/thumbnail-v1.png','reference_sha256':sha(R/'music/spirewatch-animation-v4/thumbnail-v1.png'),'dimensions':list(Image.open(H/'thumbnail-v2.png').size),'scene_changes':'Generated marketing adaptation; composition/lighting differs. Not an animation plate.'},'review':'Temporal/decoded still inspection; not continuous playback','files':{str(p.relative_to(H)).replace('\\','/'):{'sha256':sha(p),'bytes':p.stat().st_size} for p in H.rglob('*') if p.is_file() and p.name!='package-manifest.json'}}
(H/'package-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if '--apply' not in sys.argv:print('Package prepared');raise SystemExit
if D.exists():raise RuntimeError('Preserve existing destination')
paths=[R/'AGENTS.md',R/'PROJECT.md',R/'PRODUCTION_PIPELINE.md',R/'creative/ANIMATION_KNOWLEDGE_BANK.md',R/'final/catalog.json',F/'manifest.json',F/'README.md']
before={p:p.read_bytes() for p in paths};changes={}
note='Below the Snowline animation v2 (2026-10-25): v1 is a decent checkpoint needing more work, not accepted final motion. User reported a satellite ghost and requested colored/dimming lights, building/interior activity, console buttons and a Hoth thumbnail inspired by Spirewatch. music/below-the-snowline-animation-v2/ fixes source/destination cloud exclusion around the dish feed/support; before/after crops show removed ghost fragments. Eight console indicators, seven phased keys, source-masked bridge emitters, two habitat displays and room-practical/spill variation add activity. Seven retained isolated layers match v1 at five phases. Same native 1672x941 artwork v5. Twenty-second silent 720p30 preview and exact three-repeat review passed full decoding/timestamps/region/quiet-neighbor seams, protected-pixel/periodicity and direct native-to-decoded checks. Assistant inspected temporal/decoded stills, not continuous playback. Separate built-in-imagegen Hoth thumbnail PNG/JPEG candidate uses Spirewatch typography; scene geometry/lighting can differ. Motion/thumbnail user review pending; no audio, 4K, commit or push. Earlier art, v1 and approved thumbnail preserved.'
for name in ['AGENTS.md','PROJECT.md']:
 p=R/name;lines=before[p].decode('utf-8-sig').splitlines(keepends=True);tail=''.join(l for l in lines[1:] if not l.startswith('Below the Snowline animation v1 (2026-10-25):'));changes[p]=lines[0]+'\n'+note+'\n\n'+tail
p=R/'PRODUCTION_PIPELINE.md';lines=before[p].decode('utf-8-sig').splitlines();count=0
for i,line in enumerate(lines):
 if line.startswith('| 13 |'):
  lines[i]='| 13 | [Below the Snowline](music/below-the-snowline-animation-v2/README.md) | V2: dish ghost fixed; colored console/base lighting and activity; 20s720p checked | Retheme prompts pending; no audio | Review v2 animation and new Hoth thumbnail; 4K pending |';count+=1
assert count==1;changes[p]='\n'.join(lines)+'\n'
p=R/'creative/ANIMATION_KNOWLEDGE_BANK.md';changes[p]=before[p].decode('utf-8-sig')+'\n\n## Below the Snowline v2 — candidate, 2026-10-25\n\nV1 was decent but the user caught a duplicated fragment beside the dish. A polygon that covers the reflector can still miss feed arms, machinery and support legs; those pixels can enter transported cloud samples and appear beside the real structure. V2 enlarges both source and destination exclusions and saves matched temporal before/after crops plus an exact static-guard assertion. Retain this as a technical fix, not user acceptance of v2. New console/bridge lights require full lens coverage and source emitter selection: initial small masks left bright button rims and dimmed a patch of bridge metal. Correct masks before increasing strength. Seven retained layers match at five sampled phases; final encoded seam/repeat/direct-render checks pass. See [v2 package](../music/below-the-snowline-animation-v2/README.md).\n'
p=R/'final/catalog.json';data=json.loads(before[p].decode('utf-8-sig'));e=next(x for x in data if x.get('catalog_number')=='13');e['status']='Ice-planet animation v2 and Hoth thumbnail candidates technically prepared; user review pending; no audio/4K'
e['animation_preview']={'folder':'../../music/below-the-snowline-animation-v2','video':'Below-the-Snowline-v2-preview-20s.mp4','duration_seconds':20,'fps':30,'user_approved':False};e['thumbnail_candidate']='../../music/below-the-snowline-animation-v2/thumbnail-v2.jpg';changes[p]=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
p=F/'manifest.json';data=json.loads(before[p].decode('utf-8-sig'));data['animation_preview']=e['animation_preview'];data['thumbnail_candidate']=e['thumbnail_candidate'];changes[p]=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
p=F/'README.md';lines=before[p].decode('utf-8-sig').splitlines(keepends=True);changes[p]=lines[0]+'\nLatest: [animation v2 and Hoth thumbnail candidate](../../music/below-the-snowline-animation-v2/README.md), 2026-10-25. Dish ghost fix and richer equipment/building lighting; user review pending. V1 below is a historical checkpoint.\n\n'+''.join(lines[1:])
for p in paths:
 if p.read_bytes()!=before[p]:raise RuntimeError('Concurrent change: '+str(p))
shutil.copytree(H,D)
for n,item in manifest['files'].items():assert sha(D/n)==item['sha256']
for p,t in changes.items():p.write_text(t,encoding='utf-8')
print('Saved and hash-verified '+str(D))
