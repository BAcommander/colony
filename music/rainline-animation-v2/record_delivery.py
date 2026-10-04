from pathlib import Path
import json
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/'final/08-rainline-relay'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
a=read(H/'analytic-validation.json');i=read(H/'isolated-validation.json');p=read(H/'preview-validation.json')
assert a['fingerprint']==i['fingerprint']==p['fingerprint']
assert len(i['clips'])==4 and p['clips'][0]['validation']['frames']==600
assert p['clips'][1]['validation']['frames']==1800 and p['clips'][1]['three_repeated_decoded_payloads_identical']
assert all(e['pass'] for c in p['clips'] for e in c['validation']['encoded_seam'].values())
d={'date':'2026-10-04','version':'v2','status':'Revised twenty-second 720p draft delivered; user review pending','feedback':(H/'feedback-v1.txt').read_text(encoding='utf-8'),'fingerprint':p['fingerprint'],'preview':p['clips'][0],'three_loop_review':p['clips'][1],'isolated_tests':i['clips'],'silent':True,'native_source_dimensions':[1672,941],'preview_dimensions':[1280,720],'user_motion_approved':False,'four_k_produced':False,'inspection':'Source-coordinate grids, masks, temporal source samples and decoded video stills inspected. No continuous playback claim.','preserved':'Original artwork and complete v1 code/config/media retained unchanged.','storage':'Local draft and records; no commit, push or credits.'}
save(H/'delivery-v2.json',d)
(H/'README.md').write_text('''# Rainline Relay — revised animation v2

2026-10-04. V1 was not accepted: the user reported poor window masking, requested better rain, flickering lights and antenna lights, and questioned whether the water moved. This revision is a new review candidate, not an approved final.

- [20-second silent 720p/30 fps preview](rainline-relay-v2-preview-20s.mp4)
- [60-second review: three exact repeats](rainline-relay-v2-three-loops-60s.mp4)
- [Water alone, eight seconds](water-isolated-v2-8s.mp4)
- [Rain alone, eight seconds](rain-isolated-v2-8s.mp4)
- [Habitat and walkway lights alone](lights-isolated-v2-8s.mp4)
- [Antenna lights alone](beacons-isolated-v2-8s.mp4)
- [Mask overlay](mask-review.png)
- [Delivery validation](delivery-v2.json)

## Changes

Source-coordinate crop inspection found the main cabin's lower-right glass boundary cut diagonally across valid water in v1; the side panes also needed corrected top/bottom edges. V2 traces those glass limits and maps complete habitat panes around the bezels and central divider. Luminous interiors dim with restrained spill; dark details are less affected. The near window is no longer a partial rectangle overlapping the tree. Window dim events remain staggered, with additional short, uneven flickers; one walkway practical also flickers occasionally. The desk lamp stays steady.

Two small red beacons are anchored to visible antenna tips at source (1013,231) and (1365,284). They have separate five/four-second pulse periods and phases, with softened transitions and local halos. No large lens flare or global exposure change.

Rain now uses three depth groups, faster falls, longer tapered trails and independent seeded arrivals. Far rain stays behind mapped architecture; nearer rain is an optical overlay in front of exterior objects but behind cabin frames and equipment. The source's static rain remains a limitation: this revision does not remove or move every baked-in streak.

Water retains the 24-wave reconstructed reflection method, with broader waves, stronger coherent displacement and revised speed. This is still a 2D approximation. Water boundaries, roots, three walkway posts, floating vegetation and the foreground plant are remapped to the actual source, rather than applying the original broad exclusions or treating every green reflection as solid vegetation. Source, room and existing scene renderers are preserved. Mist and radio activity continue as supporting layers.

## Validation and next decision

Four isolated eight-second full-composition clips preceded the composite. Per-layer endpoint/seam checks, finite source frames and protected pixels passed. All 600 composite and 1800 review frames decoded with sequential timestamps; encoded regional/composite seam checks passed and the review's three decoded repetitions exactly match the preview. No duplicated endpoint. Reports bind source/config/code/dependency/mask hashes.

Assistant inspected source grids, masks, temporal samples and decoded stills, not continuous playback. User normal-speed review remains necessary for rain readability, believable water speed, edge quality and restraint of lights. No 4K export, soundtrack or long assembly is produced for scene 08 yet. The sixty-second review repeats the twenty-second draft; it is not a unique minute.

`render_rainline.py --stage samples`, then `--stage isolated`, then `--stage preview`. Optional `--config` accepts a subsequent scene-plan path; outputs remain protected against overwrite. Use the existing Python runtime with PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. `build_v2.py` captures the structural compositor changes from the preserved v1 implementation. V1 remains available in ../rainline-animation-v1/. No credits, commit or push.
''',encoding='utf-8')
m=read(P/'manifest.json')
history=m.setdefault('animation_history',[])
old=m.get('animation_current',{})
if old and old.get('preview')!=d['preview']['path']:history.append(old)
m['animation_current']={'status':d['status'],'package':'../../music/rainline-animation-v2/README.md','delivery':'../../music/rainline-animation-v2/delivery-v2.json','preview':d['preview']['path'],'preview_sha256':d['preview']['sha256'],'source_sha256':d['fingerprint']['source_sha256'],'preview_seconds':20,'preview_dimensions':[1280,720],'fps':30,'masks_created':True,'renderer_implemented':True,'four_k_export_produced':False,'user_motion_approved':False,'feedback_on_v1':'Poor window masks; improve rain and water visibility; add flicker and antenna lights.'}
save(P/'manifest.json',m)
rp=P/'README.md';s=rp.read_text(encoding='utf-8').replace('The [first 20-second animation draft](../../music/rainline-animation-v1/README.md) is delivered on 2026-10-04 with layered rain, water/reflection motion, forest mist, habitat lights and radio activity.','The [revised 20-second v2 animation draft](../../music/rainline-animation-v2/README.md) is delivered on 2026-10-04 with remapped glass/light/water masks, layered rain, stronger water reflections, mist, brief light flickers, antenna beacons and radio activity. V1 is preserved; the user requested these corrections.');rp.write_text(s,encoding='utf-8')
rp=R/'PRODUCTION_PIPELINE.md';s=rp.read_text(encoding='utf-8').replace('V1 twenty-second 720p draft delivered; rain/water/mist/lights/radio; review pending','V2 twenty-second 720p draft: corrected masks, revised rain/water, flicker and antenna lights; review pending').replace('Review v1 motion at normal speed before 4K; music tests remain separate','Review v2 window edges, rain/water and lights at normal speed before 4K; music remains separate');rp.write_text(s,encoding='utf-8')
rp=R/'AGENTS.md';s=rp.read_text(encoding='utf-8');start=s.index('Current Rainline animation (');end=s.index('\n\n',start)
s=s[:start]+'''Current Rainline animation (2026-10-04): user rejected v1 window masking, requested improved rain, light flicker and antenna lights, and questioned water visibility. Revised v2 silent twenty-second 720p/30 fps draft and three-loop sixty-second review delivered in music/rainline-animation-v2/; see README.md and delivery-v2.json. Same immutable artwork-v1.png SHA-256 2a159c964df74dc56ecec50bee9fdf66ebf48899c5b77050616863092cc365f8, 1672x941. Glass boundaries and complete habitat apertures are remapped; water now uses corrected root/post/plant masks, broader 24-wave reflections and stronger coherent displacement. Three tapered rain depths, brief uneven habitat/walkway flicker and two asynchronous red antenna beacons are added; mist/radio continue. Static source rain remains. Four isolated eight-second clips, analytic layer seams/protected pixels, full 600/1800-frame decodes/timestamps and regional/composite encoded seams passed; all three repeated decoded payloads match. Assistant inspected source grids/masks/temporal/decoded stills, not continuous playback. V2 user motion review, music, 4K and assembly pending. V1 original code/config/media preserved; no credits, commit or push.''' +s[end:];rp.write_text(s,encoding='utf-8')
rp=R/'final/catalog.json';cat=read(rp)
for e in cat:
 if e['folder']=='08-rainline-relay':e.update(status='V2 animation preview delivered after mask/rain/water/light feedback; user review pending; no soundtrack',animation_preview='../../music/rainline-animation-v2/README.md')
save(rp,cat)
print('Rainline v2 delivery and current status recorded')
