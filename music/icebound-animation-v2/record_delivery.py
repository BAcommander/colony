from pathlib import Path
import json
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/'final/07-icebound-weather-post'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def change(p,a,b):
 s=p.read_text(encoding='utf-8-sig');assert a in s,(p,a);p.write_text(s.replace(a,b),encoding='utf-8')
pr=read(H/'preview-validation.json');ir=read(H/'isolated-validation.json');ar=read(H/'analytic-validation.json');c=read(H/'scene-plan-v2.json')
assert pr['fingerprint']==ir['fingerprint']==ar['fingerprint']
assert pr['clips'][0]['validation']['decoded_frames']==600 and pr['clips'][1]['three_repeated_decoded_payloads_identical']
assert all(x['pass'] for x in pr['clips'][0]['validation']['seam_checks'].values())
record={'date':'2026-10-03','status':'V2 snowfall and antenna-beacon preview delivered; user review pending','user_request':c['feedback'],'fingerprint':pr['fingerprint'],'preview':pr['clips'][0],'three_loop_review':pr['clips'][1],'preserved_v1':ar['v1_isolated_layers'],'dimensions':[1280,720],'fps':30,'duration_seconds':20,'silent':True,'four_k_produced':False,'user_motion_approved':False,'inspection':'Full-composition temporal stills, antenna close-ups and decoded stills inspected. Continuous assistant playback not claimed.','storage':'Local uncommitted code/config/checks; review media ignored. No credits, commit or push.'}
save(H/'delivery-v2.json',record)
(H/'README.md').write_text('''# Icebound Weather Post - snowfall and beacons v2

2026-10-03. User requested visible snowfall and blinking radar-style lights at the antenna top. This supersedes the v1 choice to omit snow particles. The original still and v1 draft remain preserved. V2 is a twenty-second 720p/30 fps silent review candidate, not yet accepted.

- [Twenty-second preview](icebound-weather-post-v2-preview-20s.mp4)
- [Three-loop review, sixty seconds](icebound-weather-post-v2-three-loops-60s.mp4)
- [Eight-second isolated additions](snow-and-beacons-isolated-v2-8s.mp4)
- [Delivery record](delivery-v2.json)
- [Configuration](scene-plan-v2.json)
- [Preserved v1](../icebound-animation-v1/README.md)

Fine snow falls diagonally down and right, with three size/speed groups and a sparse nearer group for depth. Seeded paths use ten/twenty-second lifetimes, subpixel Gaussian footprints and slight directional blur. Flakes fade to zero before path renewal; no reversed motion or full-frame dissolve. The snowfall can pass in front of the scenery as an optical overlay. It does not warp the underlying landscape or station and is not a physical accumulation simulation.

Two small red beacons are anchored at source coordinates (274,55) and (240,107), on the existing upper mast and side antenna tips. Separate four/five-second schedules create staggered double flashes. Each includes a compact bright core and restrained red halo. No beam or new antenna geometry is added.

The unchanged v1 renderer supplies the original clouds, basin spindrift, window schedules and lamp/spill activity. Its delivered dependency fingerprint is checked on initialization. Every original isolated layer matches v1 exactly at 0,8,16 seconds. The new renderer is a composition wrapper, so the base source-protection checks still run before the requested snow/beacon overlays.

## Verification and review

An eight-second isolated additions test, complete 600-frame preview and 1800-frame repeated review fully decode with sequential timestamps. Analytic snow/beacon endpoints and seam checks pass; snow opacity fields repeat exactly and lifetimes divide the loop. The complete encoded regional/composite seams pass the existing gate. All three decoded repetitions match exactly. See analytic-validation.json, isolated-validation.json and preview-validation.json for hashes and evidence.

Full-scene temporal stills, antenna close-ups and decoded stills were inspected. Continuous assistant playback and user artistic acceptance are not claimed. Review snow density/speed, beacon timing and the repeated join at normal size. 4K delivery, soundtrack and long assembly remain pending; native artwork is 1672x941.

Reproduce using render_icebound_v2.py --stage samples, --stage isolated and --stage preview with the existing Python runtime and PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. Existing encoded destinations refuse overwrite. No paid generation, model installation, commit or push occurred.
''',encoding='utf-8')
m=read(P/'manifest.json');old=m['animation_current'];assert 'icebound-animation-v1' in old['package']
m['animation_current']={**old,'status':record['status'],'package':'../../music/icebound-animation-v2/README.md','delivery':'../../music/icebound-animation-v2/delivery-v2.json','preview':record['preview']['path'],'preview_sha256':record['preview']['sha256'],'previous_version':'../../music/icebound-animation-v1/README.md','latest_feedback':c['feedback']};save(P/'manifest.json',m)
change(P/'README.md','The [first twenty-second 720p animation draft](../../music/icebound-animation-v1/README.md) is delivered and technically checked: broad cloud travel, two independent basin wind layers and staggered practical lights with local spill. User motion review and 4K delivery remain pending.','The [v2 twenty-second 720p animation draft](../../music/icebound-animation-v2/README.md) is delivered and technically checked, adding requested snowfall and two red antenna beacons to the preserved v1 clouds, basin wind and station lighting. User motion review and 4K delivery remain pending.')
change(R/'PRODUCTION_PIPELINE.md','First twenty-second 720p v1 draft delivered; clouds, two basin wind depths and independent lights; review pending','V2 twenty-second 720p preview adds requested snowfall and antenna beacons; review pending')
change(R/'PRODUCTION_PIPELINE.md','Review animation v1 before 4K; run music tests separately','Review animation v2 before 4K; run music tests separately')
ag=R/'AGENTS.md';s=ag.read_text(encoding='utf-8');start=s.index('Current Icebound animation (');end=s.index('\n\n',start)
new='Current Icebound animation (2026-10-03): user requested snowfall and blinking radar-style antenna lights after v1. V2 twenty-second 720p/30 fps silent preview and three-loop review delivered in music/icebound-animation-v2/; see README.md and delivery-v2.json. Fine diagonal snowfall uses three size/speed groups, seeded periodic paths, subpixel footprints and zero-opacity renewals. Two small red double-flash beacons at the upper mast/side antenna tips use staggered four/five-second schedules. This explicit request supersedes the v1 omission of snow particles. Unchanged v1 clouds, basin spindrift, room/habitat windows and entrance/spill remain identical in isolated sampled frames; v1 renderer/config/media and approved artwork are preserved. Underlying geometry remains fixed; foreground flakes are optical overlays. Isolated additions, analytic/encoded layer and composite seams, full decode/count/timestamps and three repeated decoded payload checks passed. Assistant inspected temporal/decoded stills and beacon crops, not continuous playback. User artistic review, 4K delivery and soundtrack remain pending; no long assembly, credits, commit or push.'
ag.write_text(s[:start]+new+s[end:],encoding='utf-8')
cat=read(R/'final/catalog.json')
for e in cat:
 if e['folder']=='07-icebound-weather-post':e.update(status='V3 art accepted; v2 snowfall/beacon preview pending review; no soundtrack',animation_preview='../../music/icebound-animation-v2/README.md')
save(R/'final/catalog.json',cat)
print('V2 Icebound preview and current production status saved')
