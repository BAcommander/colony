from pathlib import Path
import json
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/'final/06-last-cable-station'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def change(p,a,b):
 s=p.read_text(encoding='utf-8-sig');assert a in s,(p,a);p.write_text(s.replace(a,b),encoding='utf-8')
feedback='the moviement seems ok, but it feels like the clouds in the distance could do alot more? any flickering of lights in the room, some sky lfight variants? how can we make this better?'
pr=read(H/'preview-validation.json');ir=read(H/'isolated-validation.json');ar=read(H/'analytic-validation.json')
assert pr['fingerprint']==ir['fingerprint']==ar['fingerprint']
assert pr['clips'][0]['validation']['decoded_frames']==600
assert pr['clips'][1]['three_repeated_decoded_payloads_identical']
assert all(v['pass'] for v in pr['clips'][0]['validation']['seam_checks'].values())
record={'date':'2026-10-03','status':'V2 preview delivered; new clouds and lighting await user review','source':read(H/'scene-plan-v2.json')['source'],'feedback_on_v1':feedback,'v1_approval_scope':'User said movement seems ok, then requested stronger distant clouds and room/sky light variations. Not blanket final approval.','preview':pr['clips'][0],'three_loop_review':pr['clips'][1],'fingerprint':pr['fingerprint'],'dimensions':[1280,720],'fps':30,'duration_seconds':20,'silent':True,'four_k_export_produced':False,'user_motion_approved':False,'changes':['Upper source-cloud transport 1.15 to 1.9 source px/s; valley bank transport 2.3 to 3.7 px/s','Additional broad, depth-masked periodic textured haze in central distant valley with protected tower/cables','Desk-lamp aperture dips with smaller coupled local spill changes','Slow local left-sky and sunlit desk attenuation, not global exposure modulation'],'preserved_v1_layers':ar['preserved_v1_layers'],'inspection':'Source mask overlay and temporal/decoded stills inspected. No continuous assistant playback claim.','storage':'Local uncommitted source/config/checks; review media ignored. No commit or push.'}
save(H/'delivery-v2.json',record)
(H/'README.md').write_text('''# The Last Cable Station - animation v2

2026-10-03. User found v1 movement okay but requested substantially more distant cloud activity, room-light flickering and sky-light variation, then explicitly requested the render. V2 is a new review candidate, not yet accepted.

- [Twenty-second 720p preview](last-cable-station-v2-preview-20s.mp4)
- [Three-loop review, sixty seconds](last-cable-station-v2-three-loops-60s.mp4)
- [Delivery record](delivery-v2.json)
- [Configuration](scene-plan-v2.json)
- [Preserved v1](../cable-animation-v1/README.md)

## Visible changes

The upper clouds travel at 1.9 source pixels/second and the distant valley banks at 3.7 (v1: 1.15/2.3). Three independently seeded haze formations cross the central distant valley at different heights, with overlapping local lifetimes and protected tower/cable geometry. This spreads activity through the distance instead of only changing a narrow cloud bank. The closer ravine and left cloud bank retain their v1 transport rates.

The desk lamp has a brief dip at 4.2-4.84 seconds, a shorter follow-up at 5.03-5.29 and a gentler hold at 14.6-16.0. The complete aperture and its bright core dim together; small matching spill changes occur nearby. A soft 5.8-17.5-second daylight event reduces warm light over the left sky and sunlit desk with 3.6-second eased transitions. This is local illumination shading; the full image does not change exposure. The planet, camera, parked cabin and architecture remain geometrically fixed.

The foreground cloud layers, habitat light schedules and console behaviour remain pixel-identical to v1 in isolated sampled source frames. render_cable_v2.py extends the unchanged v1 class; PeriodicDust/DustTransport supply the existing deterministic transport method. New parameters are in a separate source-hash-bound configuration. No v1 art, code, configuration, masks or media were overwritten.

## Checks and review scope

Four isolated eight-second tests cover the changed valley motion, added haze, daylight and lamp. Full v2 preview and three-repeat review fully decode at 720p/30 fps with exact counts and timestamps. Source protection assertions run on every generated frame; analytical layer endpoints/seams and encoded region/composite seams passed. All three decoded repetitions match exactly. Hashes and checks are in analytic-validation.json, isolated-validation.json and preview-validation.json.

Mask overlays, full-composition temporal stills and decoded stills were inspected; continuous playback and user artistic acceptance are not claimed. Watch at normal speed for cloud visibility, haze density, lamp timing, local lighting and the repeated join. V1 movement feedback does not approve the new effects.

## Reproduce

Use the existing local Python runtime with PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. render_cable_v2.py supports --stage samples, --stage isolated and --stage preview. Encoded destinations refuse overwrite. Dependencies and effective mask hashes are recorded; setup_scene.py preserves the initial v2 configuration. Diagnostic mask PNGs show only newly added effect masks; original cloud masks remain source-config-derived.

Review render only: 20 seconds, 1280x720, silent. Native source remains 1672x941; 4K export awaits visual review. Audio/transition acceptance remains separate, and final long-video duration remains unconfirmed. No credits, commit, push or long assembly occurred.
''',encoding='utf-8')
m=read(P/'manifest.json');m['animation_current']={'status':record['status'],'package':'../../music/cable-animation-v2/README.md','delivery':'../../music/cable-animation-v2/delivery-v2.json','preview':record['preview']['path'],'preview_sha256':record['preview']['sha256'],'source_sha256':record['source']['sha256'],'preview_seconds':20,'preview_dimensions':[1280,720],'fps':30,'masks_created':True,'renderer_implemented':True,'four_k_export_produced':False,'user_motion_approved':False,'previous_version':'../../music/cable-animation-v1/README.md','feedback_on_v1':feedback};save(P/'manifest.json',m)
change(P/'README.md','The [first twenty-second 720p animation preview](../../music/cable-animation-v1/README.md) is now delivered and technically checked; user motion review and 4K delivery remain pending.','The [v2 twenty-second 720p animation preview](../../music/cable-animation-v2/README.md) is delivered and technically checked, adding requested distant cloud activity and room/sky lighting changes. V1 movement was described as okay; v2 visual review and 4K delivery remain pending.')
change(R/'PRODUCTION_PIPELINE.md','| V3 art accepted; first 20-second 720p preview and repeated-join review delivered; motion acceptance pending | Mineral Valley Transit audio/transition accepted as good enough; long-form export pending | Review animation v1 before 4K; confirm final duration before long assembly |','| V1 movement okay; v2 20-second 720p preview adds requested distant clouds and room/sky light changes; review pending | Mineral Valley Transit audio/transition accepted as good enough; long-form export pending | Review animation v2 before 4K; confirm final duration before long assembly |')
ag=R/'AGENTS.md';s=ag.read_text(encoding='utf-8');start=s.index('Current Cable Station animation (');end=s.index('\n\n',start)
s=s[:start]+'Current Cable Station animation (2026-10-03): user said v1 movement "seems ok" but requested more distant cloud activity, room flickers and sky-light variation, then "do the render". V2 twenty-second 720p/30 fps silent preview and three-loop review delivered in music/cable-animation-v2/. See delivery-v2.json and README.md. Upper/distant bank transport increased, three depth-masked periodic haze formations added through the central valley, full-aperture desk-lamp dips coupled to small spill, and local left-sky/sunlit-desk daylight attenuation. Camera, planet, parked cabin and geometry remain fixed; foreground cloud, habitat and console isolated frames match v1 at tested times. V2 extends unchanged v1 renderer and existing PeriodicDust methods; v1 is preserved. Full decode/count/timestamps, analytical and encoded seams, source protection and repeated payload checks passed. Assistant inspected masks/temporal and decoded stills, not continuous playback. V2 artistic review and 4K export pending; no long assembly, commit or push. Approved v3 artwork remains unchanged.'+s[end:];ag.write_text(s,encoding='utf-8')
cat=read(R/'final/catalog.json')
for e in cat:
 if e['folder']=='06-last-cable-station':e['status']='V3 art and audio/transition accepted; v1 movement okay; v2 clouds and lighting preview awaits review';e['animation_preview']='../../music/cable-animation-v2/README.md'
save(R/'final/catalog.json',cat)
change(R/'final/README.md','Number 06 now has a first twenty-second 720p animation preview awaiting user review','Number 06 now has a revised twenty-second 720p v2 animation preview awaiting user review')
print('V2 delivery and current status saved')
