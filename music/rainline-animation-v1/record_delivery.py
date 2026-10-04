from pathlib import Path
import json
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/'final/08-rainline-relay'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
a=read(H/'analytic-validation.json');i=read(H/'isolated-validation.json');p=read(H/'preview-validation.json')
assert a['fingerprint']==i['fingerprint']==p['fingerprint']
assert len(i['clips'])==4 and p['clips'][0]['validation']['frames']==600
assert p['clips'][1]['validation']['frames']==1800 and p['clips'][1]['three_repeated_decoded_payloads_identical']
assert all(c['pass'] for c in p['clips'][0]['validation']['encoded_seam'].values())
d={'date':'2026-10-04','status':'First Rainline motion draft delivered; user review pending','user_request':'execute the plan then','fingerprint':p['fingerprint'],'preview':p['clips'][0],'three_loop_review':p['clips'][1],'isolated_tests':i['clips'],'native_source_dimensions':[1672,941],'preview_dimensions':[1280,720],'fps':30,'seconds':20,'silent':True,'four_k_produced':False,'user_motion_approved':False,'inspection':'Source, masks and temporal/decoded stills inspected. No continuous assistant playback claim.','credits_spent':0,'storage':'Local source/config/reports and ignored preview media; no commit/push or remote backup.'}
save(H/'delivery-v1.json',d)
(H/'README.md').write_text('''# Rainline Relay — animation v1

2026-10-04. User requested execution of the proposed animation plan. First silent 20-second 720p/30 fps draft delivered; new motion awaits user review. Source remains the selected 1672x941 artwork-v1.png, hash-bound in scene-plan-v1.json. Original art and previous scene renderers are unchanged.

- [20-second complete draft](rainline-relay-v1-preview-20s.mp4)
- [Three-loop 60-second review](rainline-relay-v1-three-loops-60s.mp4)
- [Rain alone](rain-isolated-v1-8s.mp4)
- [Water alone](water-isolated-v1-8s.mp4)
- [Far mist alone](mist_far-isolated-v1-8s.mp4)
- [Near mist alone](mist_near-isolated-v1-8s.mp4)
- [Mask review](mask-review.png)
- [Delivery record](delivery-v1.json)

## Implemented

Fine distant rain and clearer nearby exterior rain use independent seeded particles, falling forward with consistent slight crosswind. Four/five-second lifetimes divide the twenty-second loop; local birth/death fades hide resets. Far rain is blocked by mapped trunks, buildings and walkway. Near rain is an optical layer in front of exterior objects, always behind the interior frames and foreground furniture. The static rain already in the source remains; v1 adds transported streaks without distorting the photographed scene.

Water adapts the accepted ChannelSurface/ReflectionSurface logic with this scene's perspective and 24 filtered wave components, plus restrained flattened rain-impact rings. Roots, posts, plant islands and window boundaries are excluded. Inpainted sampling excludes solid areas to prevent displaced copies entering the moving water. This is a 2D reflection approximation, not a fluid simulation. Water boundaries and vegetation protection should receive particular user review.

Two mist layers use the existing PeriodicDust/DustTransport logic with separate routes, speed, scale and masks. This transports broken formations through the forest and over the distant water without whole-frame exposure changes. A mask review caught the lamp/equipment overlap and it was corrected before isolated renders; initial mask/config evidence is preserved in initial-mask-review/.

Two existing habitat windows have staggered held dim states with matching small spill/reflection modulation. Other practical lights and the desk lamp stay steady. The small radio screen receives a restrained moving trace; the analog meter's light varies gently. No camera motion, added objects, steam, foliage warp or glass distortion. All timing uses one twenty-second scene clock.

## Checks and review

Eight-second full-composition rain/water/far-mist/near-mist tests rendered separately before the composite. All source frames enforce unchanged pixels outside their active masks and finite values. Analytic layer endpoints/seams pass. All 600 preview frames and 1800 repeated-review frames decoded with sequential timestamps; layer/composite encoded seam gates pass. The repeated review contains three exact decoded copies of the twenty-second draft; it is not a unique minute. Source/config/code/mask hashes are bound across all reports.

Assistant inspected source, mask and temporal/decoded stills; continuous playback and natural motion quality are not claimed. User should review normal-speed rain visibility, believable water/reflections, stable roots/railings, mist depth and lighting restraint. Scene 08 music, longer scheduling, 4K delivery and long assembly remain pending. No credits, commit or push.

Reproduce: render_rainline.py --stage samples, then --stage isolated, then --stage preview, using the existing Python runtime and PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. Existing MP4 destinations are protected from overwrite. Config parameters are separate from the reusable source-bound adapter; dependencies are recorded by fingerprint.
''',encoding='utf-8')
m=read(P/'manifest.json');m['animation_planning']['status']='Proposal executed as first 20-second draft; prompt preserved'
m['animation_current']={'status':d['status'],'package':'../../music/rainline-animation-v1/README.md','delivery':'../../music/rainline-animation-v1/delivery-v1.json','preview':d['preview']['path'],'preview_sha256':d['preview']['sha256'],'source_sha256':d['fingerprint']['source_sha256'],'preview_seconds':20,'preview_dimensions':[1280,720],'fps':30,'masks_created':True,'renderer_implemented':True,'four_k_export_produced':False,'user_motion_approved':False}
save(P/'manifest.json',m)
rp=P/'README.md';s=rp.read_text(encoding='utf-8');s=s.replace('No animation or soundtrack produced yet. An [animation proposal prompt](animation-proposal-prompt-v1.txt) was prepared on 2026-10-04: rain and moving water first, forest mist, independent practical lights and radio-screen activity. This is prompt preparation only; no masks or renderer have been built.','The [first 20-second animation draft](../../music/rainline-animation-v1/README.md) is delivered on 2026-10-04 with layered rain, water/reflection motion, forest mist, habitat lights and radio activity. User motion review pending; no soundtrack or 4K delivery yet. The original [proposal prompt](animation-proposal-prompt-v1.txt) is preserved.');rp.write_text(s,encoding='utf-8')
rp=R/'PRODUCTION_PIPELINE.md';s=rp.read_text(encoding='utf-8').replace('Animation proposal prompt ready; no motion implementation','V1 twenty-second 720p draft delivered; rain/water/mist/lights/radio; review pending').replace('Review Rainline proposal before building rain/water/mist masks and renderer','Review v1 motion at normal speed before 4K; music tests remain separate');rp.write_text(s,encoding='utf-8')
rp=R/'AGENTS.md';s=rp.read_text(encoding='utf-8');start=s.index('Current Rainline planning (');end=s.index('\n\n',start)
s=s[:start]+'Current Rainline animation (2026-10-04): user requested "execute the plan then". First silent twenty-second 720p/30 fps draft and three-loop sixty-second review delivered in music/rainline-animation-v1/; see README.md and delivery-v1.json. Immutable artwork-v1.png SHA-256 2a159c964df74dc56ecec50bee9fdf66ebf48899c5b77050616863092cc365f8, 1672x941. Source-bound masks and adapter implement two rain depths, 24-wave water/reflection motion plus rain impacts, independent far/near mist transport, two window dim events/spill/reflections, screen trace and gentle radio-meter illumination. Interior lamp/equipment occlusion corrected before tests. Source static rain remains; no foliage/glass warp or camera motion. Four isolated eight-second full-frame tests, analytic seams/protected pixels, 600/1800-frame full decodes/timestamps, all encoded layer/composite seams and three identical payload repetitions passed. Assistant inspected source/mask/temporal/decoded stills, not continuous playback. User motion review, music, 4K and long assembly pending; the sixty-second review is three repeats, not unique minute motion. Original source and proposal preserved. No credits, commit or push; preview media local and ignored.'+s[end:];rp.write_text(s,encoding='utf-8')
rp=R/'final/catalog.json';cat=read(rp)
for e in cat:
 if e['folder']=='08-rainline-relay':e.update(status='V1 twenty-second animation preview delivered; user motion review pending; no soundtrack',animation_preview='../../music/rainline-animation-v1/README.md')
save(rp,cat)
print('Rainline first-draft delivery and current production status recorded')
