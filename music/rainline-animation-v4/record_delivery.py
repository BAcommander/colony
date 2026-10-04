from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/'final/08-rainline-relay';V3=H.parent/'rainline-animation-v3'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
a=read(H/'analytic-validation.json');i=read(H/'isolated-validation.json');p=read(H/'preview-validation.json')
assert a['fingerprint']==i['fingerprint']==p['fingerprint']
assert len(i['clips'])==4 and p['clips'][0]['validation']['frames']==600
assert p['clips'][1]['validation']['frames']==1800 and p['clips'][1]['three_repeated_decoded_payloads_identical']
assert all(e['pass'] for clip in p['clips'] for e in clip['validation']['encoded_seam'].values())
snapshot=V3/'renderer-v3-snapshot.py';assert hashlib.sha256(snapshot.read_bytes()).hexdigest()==read(V3/'delivery-v3.json')['fingerprint']['renderer_sha256']
status='V4 twenty-second silent 720p draft delivered; readable room/radio activity, refined rear panes, water strength reduced 25%; review pending'
d={'date':'2026-10-04','version':'v4','status':status,'feedback':(H/'feedback-v3.txt').read_text(encoding='utf-8'),'fingerprint':p['fingerprint'],'preview':p['clips'][0],'three_loop_review':p['clips'][1],'isolated_tests':i['clips'],'silent':True,'native_source_dimensions':[1672,941],'preview_dimensions':[1280,720],'user_motion_approved':False,'four_k_produced':False,'inspection':'Inspected enlarged source instrument/rear-glass crops, masks, temporal full-scene samples and decoded stills. No continuous playback claim.','water_change':{'displacement_before':.45,'displacement_after':.3375,'strength_multiplier':.75,'speed_retained':.12,'also_reduced':['reflection contrast','specular response','rain-impact brightness']},'v3_renderer_snapshot':snapshot.relative_to(R).as_posix(),'storage':'Local draft and records; earlier art/media/config retained; no credits, commit or push.'}
save(H/'delivery-v4.json',d)
(H/'README.md').write_text('''# Rainline Relay — animation v4

2026-10-04. User could not see v3 foreground/radio movement, requested a better rear-building mask and another 25% water reduction. V4 is a review candidate, not an accepted final.

- [20-second silent 720p/30 fps preview](rainline-relay-v4-preview-20s.mp4)
- [60-second review: three exact repetitions](rainline-relay-v4-three-loops-60s.mp4)
- [Foreground-room test](room-isolated-v4-8s.mp4)
- [Water test](water-isolated-v4-8s.mp4)
- [Building-light test](lights-isolated-v4-8s.mp4)
- [Beacon regression test](beacons-isolated-v4-8s.mp4)
- [Rear pane mask close-up](rear-mask.png)
- [Delivery record](delivery-v4.json)

## Changes

The previous additive meter was only four source pixels high with little contrast against the amber radio display. V4 draws two visibly extending/retracting segmented level bars, perspective-mapped inside the existing LCD. The blue display now has a readable scrolling cyan signal and faint grid within its existing chart panel. Bezel, equipment and remaining interface stay fixed. These are designed procedural instrument graphics, not real telemetry or new text.

The desk lamp has two longer gentle dips with 18%/16% event depths, plus a small slow variation. The saturated emitter and its existing warm desk light change together. No moving furniture, mug, knobs or camera.

Rear habitat glass is traced across its three visible panes. The right edge is corrected; a source-color gate includes warm interiors and bright white light cores while excluding cool metal/dividers. Removed inaccurate rectangular spill/reflection patches. Rear mask and dimmed-state close-ups are saved for inspection.

Water displacement is .3375 versus v3's .45, a 25% reduction. Reflection contrast, specular strength and rain-impact brightness also use a .75 multiplier. Keep v3 speed .12, wave family and corrected water/root/post/vegetation masks. This remains a 2D reflection approximation. Rain, middle-habitat scheduling and red/green antenna cycles otherwise continue.

## Checks and status

Four eight-second isolated tests preceded the complete draft. Analytic layer endpoints/seams, finite source frames and unchanged protected pixels passed. All 600 preview and 1800 review frames decoded with sequential timestamps; regional/composite encoded seam gates passed. The repeated review contains three exact decoded copies with no duplicate endpoint. Reports bind source/config/code/dependency/mask hashes.

Assistant inspected source crops, masks, temporal samples and decoded stills; no continuous playback claim. User normal-speed review is pending. No 4K, music or long assembly for scene 08 yet. V1/v2/v3 exports and configuration remain preserved. The exact v3 renderer is retained at ../rainline-animation-v3/renderer-v3-snapshot.py, verified against v3's recorded hash before extending the shared renderer. No credits, commit or push.

Run ../rainline-renderer/render_rainline.py with --config pointing to scene-plan-v4.json and --stage samples, isolated, then preview. Existing MP4 destinations are protected. Use the existing Python runtime with PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. prepare_v4.py records the v3-to-v4 configuration changes and snapshot step; it is not intended to overwrite a later renderer.
''',encoding='utf-8')
m=read(P/'manifest.json');old=m.get('animation_current',{})
if old and old.get('preview')!=d['preview']['path']:m.setdefault('animation_history',[]).append(old)
m['animation_current']={'status':status,'package':'../../music/rainline-animation-v4/README.md','delivery':'../../music/rainline-animation-v4/delivery-v4.json','preview':d['preview']['path'],'preview_sha256':d['preview']['sha256'],'source_sha256':d['fingerprint']['source_sha256'],'preview_seconds':20,'preview_dimensions':[1280,720],'fps':30,'four_k_export_produced':False,'user_motion_approved':False,'feedback_on_v3':d['feedback']};save(P/'manifest.json',m)
rp=P/'README.md';s=rp.read_text(encoding='utf-8');start=s.index('The [revised 20-second v3');end=s.index(' User motion review pending',start)
s=s[:start]+'The [revised 20-second v4 animation draft](../../music/rainline-animation-v4/README.md) adds readable scrolling screen/radio meters and clearer lamp changes, corrects rear-habitat glass masks, and reduces water strength another 25%. Earlier versions are preserved.'+s[end:];rp.write_text(s,encoding='utf-8')
rp=R/'PRODUCTION_PIPELINE.md';s=rp.read_text(encoding='utf-8').replace('V3 twenty-second 720p draft: red/green beacons, refined panes, foreground activity and intermediate water; review pending','V4 twenty-second 720p draft: readable foreground/radio, refined rear panes, water reduced 25%; review pending').replace('Review v3 middle-building edges, foreground activity and calmer water before 4K; music remains separate','Review v4 foreground readability, rear window edges and gentler water before 4K; music remains separate');rp.write_text(s,encoding='utf-8')
rp=R/'AGENTS.md';s=rp.read_text(encoding='utf-8');start=s.index('Current Rainline animation (');end=s.index('\n\n',start)
s=s[:start]+'''Current Rainline animation (2026-10-04): user could not see v3 room/radio motion, requested improved rear-building masking and another 25% water reduction. V4 silent twenty-second 720p/30 fps draft and three-loop sixty-second review delivered in music/rainline-animation-v4/; see README.md and delivery-v4.json. Same immutable artwork-v1.png SHA-256 2a159c964df74dc56ecec50bee9fdf66ebf48899c5b77050616863092cc365f8, 1672x941. Foreground now has perspective-mapped scrolling screen signal and dual segmented radio level bars, with clearer held lamp/core/desk-spill dips. Rear panes are retraced with a warm/white emission gate, excluding metal/dividers; incorrect rear rectangular spill/reflection masks removed. Water displacement .3375 is 25% below v3 .45; contrast/specular/impact strength also multiplied by .75, speed .12 retained. Rain and red/green beacon cycles continue. Shared renderer: music/rainline-renderer/render_rainline.py; exact hash-verified v3 code snapshot preserved at music/rainline-animation-v3/renderer-v3-snapshot.py. Four isolated eight-second tests, analytic seams/protected pixels, full 600/1800-frame decodes/timestamps, encoded regional/composite seams and three identical decoded repetitions passed. Assistant inspected source crops/masks/temporal/decoded stills, not continuous playback. V4 user review, music, 4K and assembly pending; previous versions preserved. No credits, commit or push.''' +s[end:];rp.write_text(s,encoding='utf-8')
rp=R/'final/catalog.json';cat=read(rp)
for e in cat:
 if e['folder']=='08-rainline-relay':e.update(status='V4 preview: readable instruments/room lighting, corrected rear panes, water strength reduced 25%; user review pending',animation_preview='../../music/rainline-animation-v4/README.md')
save(rp,cat)
print('Rainline v4 delivery and current status recorded')
