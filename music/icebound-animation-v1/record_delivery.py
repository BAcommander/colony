from pathlib import Path
import json
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/'final/07-icebound-weather-post'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def change(p,a,b):
 s=p.read_text(encoding='utf-8-sig');assert a in s,(p,a);p.write_text(s.replace(a,b),encoding='utf-8')
pr=read(H/'preview-validation.json');ir=read(H/'isolated-validation.json');ar=read(H/'analytic-validation.json');c=read(H/'scene-plan-v1.json')
assert pr['fingerprint']==ir['fingerprint']==ar['fingerprint']
assert c['source']['sha256']==read(P/'manifest.json')['current_artwork_candidate']['sha256']
assert pr['clips'][0]['validation']['decoded_frames']==600 and pr['clips'][1]['three_repeated_decoded_payloads_identical']
assert all(x['pass'] for x in pr['clips'][0]['validation']['seam_checks'].values())
feedback='do a draft, based on all my recent feedback on toher animations is there any improvements we should add from the get go?'
record={'date':'2026-10-03','status':'First twenty-second 720p animation draft delivered; user review pending','user_request':feedback,'source':c['source'],'fingerprint':pr['fingerprint'],'preview':pr['clips'][0],'three_loop_review':pr['clips'][1],'feedback_applied':c['feedback_applied'],'dimensions':[1280,720],'fps':30,'duration_seconds':20,'silent':True,'four_k_produced':False,'user_motion_approved':False,'inspection':'Source plate, lighting crop, full mask overlay, temporal full-scene stills and decoded isolated/composite stills inspected. No continuous assistant playback claim.','storage':'Local uncommitted code/config/checks; review media ignored. No credits, commit or push.'}
save(H/'delivery-v1.json',record)
(H/'README.md').write_text('''# Icebound Weather Post - first animation draft

2026-10-03. User requested a draft incorporating recent animation feedback from the start. This is a twenty-second 720p/30 fps silent candidate, not yet user-approved. The approved v3 still is preserved and hash-bound.

- [Twenty-second preview](icebound-weather-post-v1-preview-20s.mp4)
- [Three-loop review, sixty seconds](icebound-weather-post-v1-three-loops-60s.mp4)
- [Delivery record](delivery-v1.json)
- [Source-coordinate configuration](scene-plan-v1.json)
- [Mask review](mask-review.png)

## Changes informed by recent feedback

Cloud texture moves coherently to the right across the broad sky above the stepped ice cliffs, at 2.6 source pixels/second. The mast and ringed moon are excluded from both the sampled moving texture and its output. There is no global exposure pulse or movement of cliff/ice geometry.

Two independent wind layers cross the frozen basin: farther haze at 4.8 source pixels/second and nearer spindrift at 8.5. Each has two staggered formations and local twenty-second lifetimes, expanding the active landscape beyond one small patch. These are textured optical overlays, not a fluid/snow simulation; terrain shapes remain fixed. There are no foreground snow particles.

Initial isolated test A used a snow colour too close to the ice in inspected full-scene stills. Test B uses paler snow at unchanged opacity, speed and coverage. Initial clips, configuration, renderer and validation are preserved as test-A history; the current draft uses scene-plan-v1.json and the matching B isolated tests.

The main right-hand room window dims independently for 6.6 seconds; two distant windows have separate 7.3/6.7-second holds, including a wrapped hold across the loop. The left room and other lights stay steady. The entrance lamp has a short double dip and a separate gentle longer dip, coupled to restrained doorway/snow spill. A little main-room spill follows its window state. Complete lit apertures include their white cores. No prominent computer screens are visible in this source, so no invented display is added.

The camera, weather mast, station, connections, ice cliffs, frozen sea and ringed moon stay geometrically fixed. New masks and anchors are mapped specifically to this image. render_icebound.py imports unchanged Cable cloud/light primitives and Saltline periodic transport; it does not copy their scene coordinates or modify their accepted renderers.

## Checks and review scope

Three eight-second full-composition isolated clips test the sky and each wind depth. Individual analytic endpoints/seams, protected-source assertions and finite frame values pass. The complete preview and repeated review fully decode with exact frame counts, sequential timestamps and regional/composite encoded seams within the existing gate. All three decoded repetitions are identical. See analytic-validation.json, isolated-validation.json and preview-validation.json for hashes and evidence.

Source/mask details, temporal stills and decoded frames were inspected. Continuous assistant playback and artistic acceptance are not claimed. Review normal-speed visibility, haze density, light scheduling and the repeated join. This draft does not establish 4K delivery, soundtrack generation or long-video duration. Native source is 1672x941.

## Reproduce

Use render_icebound.py --stage samples, --stage isolated and --stage preview with the existing local Python runtime and PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. Encoded destinations refuse overwrite. setup_scene.py records the initial configuration; source, effective masks and dependency hashes are stored in validation reports. No paid generation, model install, Git commit/push or long assembly occurred.
''',encoding='utf-8')
m=read(P/'manifest.json');m['animation_current']={'status':record['status'],'package':'../../music/icebound-animation-v1/README.md','delivery':'../../music/icebound-animation-v1/delivery-v1.json','preview':record['preview']['path'],'preview_sha256':record['preview']['sha256'],'source_sha256':c['source']['sha256'],'preview_seconds':20,'preview_dimensions':[1280,720],'fps':30,'masks_created':True,'renderer_implemented':True,'four_k_export_produced':False,'user_motion_approved':False};save(P/'manifest.json',m)
change(P/'README.md','No animation or soundtrack produced.','The [first twenty-second 720p animation draft](../../music/icebound-animation-v1/README.md) is delivered and technically checked: broad cloud travel, two independent basin wind layers and staggered practical lights with local spill. User motion review and 4K delivery remain pending. No soundtrack produced.')
change(P/'README.md','Current status, 2026-09-28:','Current status, 2026-10-03:')
change(R/'PRODUCTION_PIPELINE.md','| No motion implementation; v3 art accepted | Short/long prompts ready; no audio | Map distant snow transport, low ice haze and practical lights |','| First twenty-second 720p v1 draft delivered; clouds, two basin wind depths and independent lights; review pending | Short/long prompts ready; no audio | Review animation v1 before 4K; run music tests separately |')
ag=R/'AGENTS.md';s=ag.read_text(encoding='utf-8');assert 'Current Icebound animation (' not in s
head='Current Icebound animation (2026-10-03): user requested a draft incorporating recent feedback. First twenty-second 720p/30 fps silent preview and three-loop review delivered in music/icebound-animation-v1/; see README.md and delivery-v1.json. Approved artwork-v3-final.png remains unchanged, source SHA 5b49468b673b762a63909defa6b202f0bff19755cd829f84c1390d63702d499d. Broad sky source-cloud transport, separate far/nearer basin spindrift, independent complete-aperture room/habitat light holds and entrance-lamp dips with restrained local spill. Mast, moon, structures and ice geometry fixed; no foreground snow. New source-space masks reuse unchanged accepted transport logic. Isolated clips, analytic/encoded layer and composite seams, full decode/count/timestamps, source protection and exact repeated decoded payload checks passed. Assistant inspected masks, temporal/decoded stills, not continuous playback. User artistic review and 4K delivery pending; no soundtrack, long assembly, credits, commit or push.\n\n'
idx=s.index('Current Cable Station music (');s=s[:idx]+head+s[idx:];ag.write_text(s,encoding='utf-8')
cat=read(R/'final/catalog.json')
for e in cat:
 if e['folder']=='07-icebound-weather-post':e.update(status='V3 art accepted; v1 animation preview delivered pending review; no soundtrack',animation_preview='../../music/icebound-animation-v1/README.md')
save(R/'final/catalog.json',cat)
print('Icebound draft delivery and current production status saved')
