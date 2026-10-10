from pathlib import Path
import json
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/'final/07-icebound-weather-post'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def change(p,a,b):
 s=p.read_text(encoding='utf-8-sig');assert a in s,(p,a);p.write_text(s.replace(a,b),encoding='utf-8')
pr=read(H/'preview-validation.json');ar=read(H/'analytic-validation.json');c=read(H/'scene-plan-v3.json')
assert pr['fingerprint']==ar['fingerprint']
assert pr['clips'][0]['validation']['decoded_frames']==1800 and pr['clips'][1]['three_repeated_decoded_payloads_identical']
assert pr['distinct_at_0_20_40_seconds']
assert all(x['pass'] for x in pr['clips'][0]['validation']['seam_checks'].values())
d={'date':'2026-10-03','status':'Requested sixty-second preview delivered; approved v2 look retained; new light schedule review pending','user_request':c['user_request'],'preview':pr['clips'][0],'three_loop_review':pr['clips'][1],'fingerprint':pr['fingerprint'],'accepted_look':'../icebound-animation-v2/approved-v2-preview.json','duration_seconds':60,'dimensions':[1280,720],'fps':30,'silent':True,'weather_local_cycle_seconds':20,'weather_speed_change_percent':0,'not_three_copied_twenty_second_videos':True,'four_k_produced':False,'user_new_schedule_approved':False,'inspection':'Full-scene temporal stills and decoded still inspected; continuous assistant playback not claimed.','storage':'Local uncommitted code/config/checks. Preview media ignored; no credits, commit or push.'}
save(H/'delivery-v3.json',d)
(H/'README.md').write_text('''# Icebound Weather Post - sixty-second v3 preview

2026-10-03. User accepted the v2 look, then requested the suggested sixty-second loop with more varied lighting. This minute is delivered at 1280x720/30 fps, silent. The new timing awaits review; v2 acceptance remains recorded separately.

- [One-minute preview](icebound-weather-post-v3-minute-720p.mp4)
- [Three-minute join review](icebound-weather-post-v3-three-minutes-720p.mp4)
- [Delivery record](delivery-v3.json)
- [Full minute timing configuration](scene-plan-v3.json)
- [Accepted v2 look](../icebound-animation-v2/approved-v2-preview.json)

## Timing changes

The main right-hand room has dim holds of 7.5, 8.9 and 7.4 seconds, including a hold beginning at 55.4 seconds and continuing through the join. The two mapped habitat windows have independent 6.2-12.1-second holds and different intervening lit periods. Original aperture masks, dim floors and transition softness are retained, and the room spill follows its window.

Both red antenna beacons keep their original size, colour and double-flash appearance. Seed 7303 generates fixed but varied gaps between flashes across the full minute: twelve upper-mast groups and ten side-antenna groups. Gaps wrap coherently at the join. Entrance-lamp dips are spread across the minute; its local spill still follows the lamp. Unmapped lights stay steady.

Clouds, basin spindrift and snowfall retain the exact existing local twenty-second cycles and speeds, including ten-second nearer-flake lifetimes. This is a sixty-second composite because lighting changes across the entire minute; it is not three copies of the v2 MP4. The same weather phase at seconds 0,20,40 has different lighting. Source weather frames are cached in memory while every complete frame is composited with its own lighting timestamp. No approved code/config or original artwork was modified.

## Verification

All unchanged weather layers match v2 source frames at six sampled times, with zero speed deviation. Additional spot checks at 0.7,8,28 seconds found exact combined pixels outside lighting areas. New light-layer analytic endpoints and seams pass; the composite matches at 0/60 seconds and differs at 0/20/40. The complete 1800-frame preview and 5400-frame repeat fully decode with sequential timestamps and regional/composite encoded seam checks. All three decoded minute repetitions match exactly. See analytic-validation.json and preview-validation.json.

Temporal and decoded stills were inspected; continuous assistant playback and acceptance of the new timing are not claimed. Native source remains 1672x941. 4K export, soundtrack and long assembly remain pending. No credits, model installation, Git commit or push occurred.

Reproduce using render_icebound_minute.py --stage samples and --stage preview with the existing Python runtime and PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. Source/config/code hashes are bound to the accepted v2 manifest. Encoded destinations refuse overwrite.
''',encoding='utf-8')
m=read(P/'manifest.json');old=m['animation_current'];assert 'icebound-animation-v2' in old['package']
m['animation_current']={**old,'status':d['status'],'package':'../../music/icebound-animation-v3/README.md','delivery':'../../music/icebound-animation-v3/delivery-v3.json','preview':d['preview']['path'],'preview_sha256':d['preview']['sha256'],'preview_seconds':60,'previous_version':'../../music/icebound-animation-v2/README.md','accepted_look_version':'v2','user_motion_approved':False,'new_schedule_user_approved':False,'latest_feedback':c['user_request']};save(P/'manifest.json',m)
change(P/'README.md','The [v2 twenty-second 720p animation draft](../../music/icebound-animation-v2/README.md) is delivered and technically checked, adding requested snowfall and two red antenna beacons to the preserved v1 clouds, basin wind and station lighting. User accepted the v2 look on 2026-10-03 ("i think it\'s good"); possible refinements are under discussion. 4K delivery remains pending.','User accepted the v2 look on 2026-10-03 ("i think it\'s good"). The requested [sixty-second v3 preview](../../music/icebound-animation-v3/README.md) is delivered and technically checked, with varied window/beacon timing and unchanged weather speeds. New timing review and 4K delivery remain pending.')
change(R/'PRODUCTION_PIPELINE.md','V2 twenty-second preview look accepted; snowfall and antenna beacons included','V2 look accepted; requested sixty-second v3 preview delivered with varied lighting; new timing review pending')
change(R/'PRODUCTION_PIPELINE.md','Decide whether to extend light timing before 4K; run music tests separately','Review minute light timing before 4K; run music tests separately')
ag=R/'AGENTS.md';s=ag.read_text(encoding='utf-8');start=s.index('Current Icebound animation (');end=s.index('\n\n',start)
paragraph='Current Icebound animation (2026-10-03): user accepted the v2 snowfall/beacon look ("i think it\'s good") then requested the proposed sixty-second version ("ok do your 60s suggestion"). Sixty-second 720p/30 fps silent v3 preview and three-minute join review delivered in music/icebound-animation-v3/; see README.md and delivery-v3.json. Window holds now vary independently over the minute, including a wrapped main-room hold; both antenna lights retain double flashes with seeded varied gaps; entrance dips/spill spread across the minute. V2 weather local twenty-second cycles, snow lifetimes, speeds, masks and visual parameters are preserved; this is a unique sixty-second lighting composite, not three copied videos. All original layers match at six sampled times, analytic endpoints/seams and distinct 0/20/40 frames pass. Full 1800/5400 frame decodes, timestamps, regional/composite encoded seams and three exact minute payload repetitions passed. V2 accepted fingerprint is checked; original v1/v2 art/config/code/media remain intact. Assistant inspected temporal/decoded stills, not continuous playback. New minute timing review, 4K delivery and soundtrack remain pending; no long assembly, credits, commit or push.'
ag.write_text(s[:start]+paragraph+s[end:],encoding='utf-8')
cat=read(R/'final/catalog.json')
for e in cat:
 if e['folder']=='07-icebound-weather-post':e.update(status='V3 art and v2 animation look accepted; requested sixty-second v3 preview delivered; timing review pending; no soundtrack',animation_preview='../../music/icebound-animation-v3/README.md')
save(R/'final/catalog.json',cat)
print('One-minute Icebound delivery and current status saved')
