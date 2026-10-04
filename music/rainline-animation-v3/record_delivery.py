from pathlib import Path
import json
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/'final/08-rainline-relay'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
a=read(H/'analytic-validation.json');i=read(H/'isolated-validation.json');p=read(H/'preview-validation.json')
assert a['fingerprint']==i['fingerprint']==p['fingerprint']
assert len(i['clips'])==4 and p['clips'][0]['validation']['frames']==600
assert p['clips'][1]['validation']['frames']==1800 and p['clips'][1]['three_repeated_decoded_payloads_identical']
assert all(e['pass'] for clip in p['clips'] for e in clip['validation']['encoded_seam'].values())
status='V3 twenty-second silent 720p draft delivered; red/green beacons, refined middle-building panes, foreground activity and intermediate water; user review pending'
d={'date':'2026-10-04','version':'v3','status':status,'feedback':(H/'feedback-v2.txt').read_text(encoding='utf-8'),'fingerprint':p['fingerprint'],'preview':p['clips'][0],'three_loop_review':p['clips'][1],'isolated_tests':i['clips'],'silent':True,'native_source_dimensions':[1672,941],'preview_dimensions':[1280,720],'user_motion_approved':False,'four_k_produced':False,'inspection':'Inspected source-coordinate window crops, mask overlays, temporal samples and decoded video stills. No continuous playback claim.','preserved':'Original art and full v1/v2 code/config/media retained. Rain unchanged from v2; supporting mist field/timing unchanged, with current occlusion masks.','storage':'Local draft and records; no commit, push or credits.'}
save(H/'delivery-v3.json',d)
(H/'README.md').write_text('''# Rainline Relay — animation v3

2026-10-04. User requested red/green antenna cycling, another correction to the middle building mask, foreground room activity and water between v1 and v2. This is a new review candidate; v2 was not accepted as the final look.

- [20-second silent 720p/30 fps preview](rainline-relay-v3-preview-20s.mp4)
- [60-second review: three exact repeats](rainline-relay-v3-three-loops-60s.mp4)
- [Water test](water-isolated-v3-8s.mp4)
- [Building-light test](lights-isolated-v3-8s.mp4)
- [Foreground-room test](room-isolated-v3-8s.mp4)
- [Red/green antenna test](beacons-isolated-v3-8s.mp4)
- [Mask overlay](mask-review.png)
- [Delivery record](delivery-v3.json)

## Changes

The middle building is the nearer, larger habitat behind the tree. V2's light matte left a bright strip on the left of its rightmost pane and extended into the right bezel. V3 traces that glass boundary from enlarged source crops with supersampled edges. All three visible panes now share the room's dim/flicker events; the intervening tree, frame and divider are excluded. Incorrect rectangular near-building spill/reflection patches are removed. Its held dim state is gentler. Source comparison crops are preserved here for review.

Both antenna lamps alternate red and green on successive pulses, with different phase offsets. Dark gaps between colors avoid an orange blend. Each color schedule divides the twenty-second loop.

Water displacement is .45, exactly between v1's .22 and v2's .68. Speed is .12 between .10 and .14; contrast/specular response is also intermediate. Keep the corrected v2 water/root/post/vegetation mapping and wave family. This is a 2D reflection approximation; user playback is needed to judge the desired calmness.

Foreground activity now includes a stronger screen trace, a small changing radio level strip and restrained desk-lamp variation coupled to its warm desk spill. The lamp's saturated white core is included. Physical equipment, mug, furniture and camera remain fixed. V2 rain is retained; source-baked static streaks remain. Existing mist continues.

## Verification and status

Four isolated eight-second tests preceded the composite. Analytic layer endpoints/seams, finite frames and protected pixels passed. All 600 preview frames and 1800 repeated-review frames decoded with sequential timestamps; regional/composite encoded seam checks passed. The review contains three identical decoded copies, with no duplicated endpoint. Source/config/renderer/dependency/mask hashes match across reports.

Assistant inspected source/mask/temporal/decoded stills, not continuous playback. User normal-speed review remains pending. The sixty-second review is three repeats, not a unique minute. No scene 08 soundtrack, 4K delivery or long assembly yet. V1/v2 remain unchanged; no credits, commit or push.

Renderer: ../rainline-renderer/render_rainline.py, with --config pointing at this folder's scene-plan-v3.json. Run --stage samples, then --stage isolated, then --stage preview. The shared renderer accepts configuration paths and versioned output names; refuses to overwrite MP4s. Use the existing Python runtime and PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. build_v3.py records the additions from the preserved v2 renderer.
''',encoding='utf-8')
m=read(P/'manifest.json');old=m.get('animation_current',{})
if old and old.get('preview')!=d['preview']['path']:m.setdefault('animation_history',[]).append(old)
m['animation_current']={'status':status,'package':'../../music/rainline-animation-v3/README.md','delivery':'../../music/rainline-animation-v3/delivery-v3.json','preview':d['preview']['path'],'preview_sha256':d['preview']['sha256'],'source_sha256':d['fingerprint']['source_sha256'],'preview_seconds':20,'preview_dimensions':[1280,720],'fps':30,'four_k_export_produced':False,'user_motion_approved':False,'feedback_on_v2':d['feedback']}
save(P/'manifest.json',m)
rp=P/'README.md';s=rp.read_text(encoding='utf-8');start=s.index('The [revised 20-second v2');end=s.index(' User motion review pending',start)
s=s[:start]+'The [revised 20-second v3 animation draft](../../music/rainline-animation-v3/README.md) adds red/green antenna cycling, more precise middle-building glass masks, foreground screen/radio/lamp activity and water strength between v1 and v2. V1/v2 are preserved.'+s[end:];rp.write_text(s,encoding='utf-8')
rp=R/'PRODUCTION_PIPELINE.md';s=rp.read_text(encoding='utf-8').replace('V2 twenty-second 720p draft: corrected masks, revised rain/water, flicker and antenna lights; review pending','V3 twenty-second 720p draft: red/green beacons, refined panes, foreground activity and intermediate water; review pending').replace('Review v2 window edges, rain/water and lights at normal speed before 4K; music remains separate','Review v3 middle-building edges, foreground activity and calmer water before 4K; music remains separate');rp.write_text(s,encoding='utf-8')
rp=R/'AGENTS.md';s=rp.read_text(encoding='utf-8');start=s.index('Current Rainline animation (');end=s.index('\n\n',start)
s=s[:start]+'''Current Rainline animation (2026-10-04): user requested red/green antenna cycling, another middle-building mask correction, foreground room activity and water between v1/v2. Revised v3 silent twenty-second 720p/30 fps draft and three-loop sixty-second review delivered in music/rainline-animation-v3/; see README.md and delivery-v3.json. Same immutable artwork-v1.png SHA-256 2a159c964df74dc56ecec50bee9fdf66ebf48899c5b77050616863092cc365f8, 1672x941. Supersampled glass masks cover all three visible nearer-habitat panes, excluding tree/frame; incorrect rectangular near-building spill/reflection patches removed. Beacons alternate red/green with staggered pulses. Water displacement .45 and speed .12 are between v1 and v2, retaining corrected v2 masks and wave family. Foreground screen trace, radio level strip and subtle lamp/core/desk-spill variation added. Rain retained from v2, including static source-rain limitation. Shared configurable renderer: music/rainline-renderer/render_rainline.py. Four isolated eight-second tests, analytic seams/protected pixels, full 600/1800-frame decodes/timestamps, encoded regional/composite seams and three identical decoded repetitions passed. Assistant inspected source crops/masks/temporal/decoded stills, not continuous playback. V3 motion review, music, 4K and assembly pending. V1/v2 preserved; no credits, commit or push.''' +s[end:];rp.write_text(s,encoding='utf-8')
rp=R/'final/catalog.json';cat=read(rp)
for e in cat:
 if e['folder']=='08-rainline-relay':e.update(status='V3 preview: red/green antennas, refined middle-building glass, foreground activity, intermediate water; user review pending',animation_preview='../../music/rainline-animation-v3/README.md')
save(rp,cat)
print('Rainline v3 delivery and current status recorded')
