from pathlib import Path
import json,hashlib,shutil,sys,platform,subprocess
sys.path.insert(0,r'C:/AI/ComfyUI/venv/Lib/site-packages')
import numpy,cv2,PIL
H=Path(__file__).parent;R=Path('G:/AI/colony');D=R/'music/below-the-snowline-animation-v1';release=R/'final/13-below-the-snowline'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
for name in ['analytic-validation.json','isolated-validation.json','preview-validation.json','direct-validation.json']:
 report=read(H/name)
 assert all(sha(H/p)==h for p,h in report['fingerprint'].items()),('Stale validation',name)
assert sha(H/'source.png')==sha(release/'ice-planet-retheme-v3/artwork-v5.png')
inventory={str(p.relative_to(H)).replace('\\','/'):{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(H.rglob('*')) if p.is_file() and p.name!='package-manifest.json'}
manifest={'date':'2026-10-25','catalog_number':'13','status':'20-second 720p30 silent animation candidate; technical checks passed, user playback review pending','artwork_feedback':'looks good i think','artwork_selected_for_animation':True,'motion_user_approved':False,'method':'Local source-texture transport and masked procedural compositing','source_dimensions':[1672,941],'preview_dimensions':[1280,720],'preview':'Below-the-Snowline-v1-preview-20s.mp4','repeat_review':'Below-the-Snowline-v1-three-loops-60s.mp4','source_sha256':sha(H/'source.png'),'files':inventory,'review':'Source/mask/temporal/decoded still inspection only. No continuous playback claimed.','runtime':{'python':sys.version,'platform':platform.platform(),'ffmpeg':subprocess.check_output(['ffmpeg','-version'],text=True).splitlines()[0]},'backup':'Local files only; no commit or push.'}
manifest['runtime'].update({'numpy':numpy.__version__,'opencv':cv2.__version__,'pillow':PIL.__version__})
(H/'package-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
if '--apply' not in sys.argv: print('Package ready: '+str(len(inventory))+' files');raise SystemExit
if D.exists():raise RuntimeError('Destination exists; preserve it')
# Read shared records just before narrow updates, leaving other scene entries intact.
paths=[R/'AGENTS.md',R/'PROJECT.md',R/'PRODUCTION_PIPELINE.md',R/'final/catalog.json',release/'manifest.json',release/'README.md',release/'ice-planet-retheme-v3/manifest.json']
before={p:p.read_bytes() for p in paths};changes={}
note='Below the Snowline animation v1 (2026-10-25): user selected ice-planet artwork v5 with "looks good i think" and requested animation with possible new details. music/below-the-snowline-animation-v1/ contains a genuine twenty-second silent 720p30 preview and exact three-repeat review. Original sky texture transports forward; three powder/mist regions, depth-grouped exterior snow, six independent warm apertures, radar sweep/contacts, six terminal readouts and mug steam animate through new source-coordinate masks. Cannon/dish and architecture remain structurally fixed. First fine-textured powder study was replaced by broad periodic forms. Analytic per-layer periodicity/protected pixels, full isolated/600/1800-frame decoding/timestamps/regional/quiet-neighbour seams, exact repeat identity and twelve direct native-to-decoded YUV checks passed. Assistant inspected temporal/decoded stills, not continuous playback. Artwork selected; animation user review pending. No audio, 4K, opening, commit or push. Source native 1672x941; future 4K would be upscaled. Earlier art/approved packaging and unrelated scenes preserved.'
for name in ['AGENTS.md','PROJECT.md']:
 p=R/name;text=before[p].decode('utf-8-sig');lines=text.splitlines(keepends=True)
 # Remove the superseded single-line retheme status; retain unrelated current notes.
 tail=''.join(l for l in lines[1:] if not l.startswith('2026-10-25: Catalog 13 Below the Snowline has'))
 changes[p]=lines[0]+'\n'+note+'\n\n'+tail
p=R/'PRODUCTION_PIPELINE.md';lines=before[p].decode('utf-8-sig').splitlines();count=0
for i,l in enumerate(lines):
 if l.startswith('| 13 |'):
  lines[i]='| 13 | [Below the Snowline](music/below-the-snowline-animation-v1/README.md) | Ice-planet v5 art selected; 20s 720p30 animation v1 technically checked | Retheme music prompts pending; no audio | Review complete animation; 4K and revised thumbnail/publication packaging pending |';count+=1
assert count==1;changes[p]='\n'.join(lines)+'\n'
p=R/'final/catalog.json';data=json.loads(before[p].decode('utf-8-sig'));e=next(x for x in data if x.get('catalog_number')=='13')
e['status']='Ice-planet v5 artwork selected; twenty-second silent animation v1 technically checked, user motion review pending; music/4K/revised packaging pending'
e['retheme_candidate']['user_approved']=True;e['retheme_candidate']['status']='Artwork selected for animation; previous approved thumbnail preserved'
e['animation_preview']={'folder':'../../music/below-the-snowline-animation-v1','video':'Below-the-Snowline-v1-preview-20s.mp4','duration_seconds':20,'fps':30,'user_approved':False}
changes[p]=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
p=release/'manifest.json';data=json.loads(before[p].decode('utf-8-sig'));data['retheme_candidate']=e['retheme_candidate'];data['animation_preview']=e['animation_preview'];changes[p]=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
p=release/'ice-planet-retheme-v3/manifest.json';data=json.loads(before[p].decode('utf-8-sig'));data['user_approved']=True;data['approval_scope']='Artwork selected for animation: looks good i think';data['status']='Artwork selected; animation v1 lives at music/below-the-snowline-animation-v1 and awaits motion review';changes[p]=json.dumps(data,indent=2)+'\n'
p=release/'README.md';lines=before[p].decode('utf-8-sig').splitlines(keepends=True);changes[p]=lines[0]+'\n## Current animation — 2026-10-25\n\nArtwork v5 selected by the user. [Twenty-second animation v1 and three-repeat review](../../music/below-the-snowline-animation-v1/README.md) are technically checked and await user playback feedback. No audio or 4K yet. Prior artwork-candidate notes below are historical.\n\n'+''.join(lines[1:])
for p in paths:
 if p.read_bytes()!=before[p]:raise RuntimeError('Concurrent edit: '+str(p))
shutil.copytree(H,D)
for name,item in inventory.items():assert sha(D/name)==item['sha256']
for p,text in changes.items():p.write_text(text,encoding='utf-8')
print('Saved and hash-verified '+str(D))
