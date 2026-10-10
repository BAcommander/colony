from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/'final/06-last-cable-station'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def change(p,a,b):
 s=p.read_text(encoding='utf-8-sig');assert a in s,(p,a);p.write_text(s.replace(a,b),encoding='utf-8')
report=read(H/'preview-validation.json');isolated=read(H/'isolated-validation.json');analytic=read(H/'analytic-validation.json')
assert report['clips'][0]['validation']['decoded_frames']==600
assert report['clips'][1]['three_repeated_decoded_payloads_identical']
assert all(v['pass'] for v in report['clips'][0]['validation']['seam_checks'].values())
assert report['fingerprint']==isolated['fingerprint']==analytic['fingerprint']
analytic['inspection']='Source mask overlay, full-composition temporal stills and decoded isolated frames inspected; no continuous-playback claim. User motion review pending.';save(H/'analytic-validation.json',analytic)
record={'date':'2026-10-03','status':'First animation preview delivered; user motion review pending','source':read(H/'scene-plan-v1.json')['source'],'preview':report['clips'][0],'three_loop_review':report['clips'][1],'isolated_review':'music/cable-animation-v1/isolated-validation.json','analytic_validation':'music/cable-animation-v1/analytic-validation.json','fingerprint':report['fingerprint'],'dimensions':[1280,720],'duration_seconds':20,'fps':30,'silent':True,'four_k_export_produced':False,'user_motion_approved':False,'inspection':'Source mask overlay, temporal stills, decoded isolated and combined frames inspected. Continuous playback not claimed.','implementation':'Local source-bound procedural layers. Uses Floodplain encoder/checks and its periodic cloud transport method; source-specific motion_review.py is Basalt-only, so equivalent isolated tests are run by the Cable adapter.','limits':'Source-cloud transport is a 2D approximation; natural movement and visibility require user playback review.','backup':'Saved locally; no commit or push. Preview videos remain ignored.'}
save(H/'delivery-v1.json',record)
(H/'README.md').write_text('''# The Last Cable Station - animation v1

2026-10-03. First full twenty-second preview delivered following the user's render request. Motion is awaiting user review; original approved artwork and other scene renderers are unchanged.

- [20-second 720p preview](last-cable-station-v1-preview-20s.mp4)
- [Three loops, 60 seconds](last-cable-station-v1-three-loops-60s.mp4)
- [Delivery checks and fingerprints](delivery-v1.json)
- [Source-bound configuration](scene-plan-v1.json)
- [Original planning brief](../../final/06-last-cable-station/animation-plan-v1/README.md)

Valley clouds, upper sky, the bright left cloud bank and lower ravine use separately masked source-texture transport with slower distant motion. Three habitat window apertures have independent dim/off holds, including a wrapped hold at the join. Selected existing right-console status strokes update subtly; the left map and desk lamp stay steady. The parked cabin, camera, tower, cables, planet and room remain fixed. Two copies of each moving texture renew with staggered zero-opacity resets; this is a 2D approximation, not a fluid simulation.

Full-composition mask overlay and temporal stills, decoded isolated frames and a decoded combined frame were inspected. No continuous assistant playback or user artistic acceptance is claimed. Check the movement at normal speed, especially cloud travel, cliff/cable edges and the three-loop joins. The existing audio/transition approval does not approve these visuals.

## Verification

Four isolated eight-second clips fully decoded at 720p/30 fps. The full preview has 600 frames and the repeat review 1,800, with sequential timestamps. Each source frame asserts unchanged pixels outside permitted masks and exact cable/planet protection. Every layer has matching periodic endpoints and passes the last-to-first step comparison; the encoded preview passes separate region/composite seam checks. All three decoded repetitions match exactly. See isolated-validation.json, analytic-validation.json and preview-validation.json. Numeric checks do not establish artistic quality.

## Reproduce and continue

Use the local Python runtime with PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. Run render_cable.py --stage samples, then --stage isolated, then --stage preview. Media destinations refuse overwrite; choose a new version for changed timing or masks. setup_scene.py preserves the initial config and refuses an existing destination. masks/*.png are inspection exports; the renderer rebuilds full-precision masks from config geometry. Dependency hashes are recorded for ambient_effects.py, render_floodplain.py and water_surface.py under the repository scripts folder.

The original source is 1672x941. This delivery is a 1280x720 silent review preview. After visual acceptance, export and validate the upscaled 4K master with the same source/config and motion timing. The final music-video duration remains unconfirmed; no long assembly or new audio work occurred here. All files are local; no commit or push performed.
''',encoding='utf-8')
m=read(P/'manifest.json');m['animation_current']={'status':record['status'],'package':'../../music/cable-animation-v1/README.md','delivery':'../../music/cable-animation-v1/delivery-v1.json','preview':record['preview']['path'],'preview_sha256':record['preview']['sha256'],'source_sha256':record['source']['sha256'],'masks_created':True,'renderer_implemented':True,'preview_seconds':20,'preview_dimensions':[1280,720],'fps':30,'four_k_export_produced':False,'user_motion_approved':False};m['animation_plan']['status']='Historical planning brief; implementation and first preview now in animation_current';save(P/'manifest.json',m)
change(P/'README.md','Animation is planned in [animation-plan-v1](animation-plan-v1/README.md); masks, implementation and renders remain pending.','The [first twenty-second 720p animation preview](../../music/cable-animation-v1/README.md) is now delivered and technically checked; user motion review and 4K delivery remain pending. The [planning brief](animation-plan-v1/README.md) is preserved.')
change(R/'PRODUCTION_PIPELINE.md','| V3 art accepted; motion plan v1 saved, no implementation | Mineral Valley Transit audio/transition accepted as good enough; long-form export pending | Map masks and test valley/sky motion from animation-plan-v1; confirm final duration before long assembly |','| V3 art accepted; first 20-second 720p preview and repeated-join review delivered; motion acceptance pending | Mineral Valley Transit audio/transition accepted as good enough; long-form export pending | Review animation v1 before 4K; confirm final duration before long assembly |')
ag=R/'AGENTS.md';s=ag.read_text(encoding='utf-8');start=s.index('Animation plan saved at final/06-last-cable-station/animation-plan-v1/');end=s.index('Assistant signal analysis only',start)
s=s[:start]+'The first animation preview is now delivered; see current Cable Station animation below. No long delivery produced. '+s[end:]
at=s.index('\n\nCurrent Saltline music')
entry='\n\nCurrent Cable Station animation (2026-10-03): user requested "make the render". Local adapter, source-bound masks/config and first twenty-second 720p/30 fps silent preview are in music/cable-animation-v1/. Full preview: last-cable-station-v1-preview-20s.mp4; three-loop review: last-cable-station-v1-three-loops-60s.mp4. Independent valley/upper/left/ravine cloud transport, three window schedules and right-console updates; camera, parked cabin, cable tower, cables, planet and room stay fixed. Four isolated eight-second tests and full preview decoded; exact counts/timestamps, protected-source assertions, analytic/encoded layer seams and three repeated decoded payloads passed. See delivery-v1.json. Assistant inspected masks/temporal and decoded stills, not continuous playback; user visual review pending. Approved v3 source is preserved at its original hash. Planned 4K delivery waits for preview review; native source is 1672x941. No long assembly, commit or push. Original planning brief remains at final/06-last-cable-station/animation-plan-v1/.'
s=s[:at]+entry+s[at:];ag.write_text(s,encoding='utf-8')
catalog=read(R/'final/catalog.json')
for c in catalog:
 if c['folder']=='06-last-cable-station':c['status']='V3 art accepted; audio/transition accepted; first 720p animation preview awaiting user review';c['animation_preview']='../../music/cable-animation-v1/README.md'
save(R/'final/catalog.json',catalog)
change(R/'final/README.md','Animations for 06-14 have not been produced.','Number 06 now has a first twenty-second 720p animation preview awaiting user review; animations for 07-14 have not been produced.')
print('Cable Station preview delivery and current status saved')
