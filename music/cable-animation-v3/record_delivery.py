from pathlib import Path
import json

H=Path(__file__).resolve().parent; R=H.parents[1]; P=R/'final/06-last-cable-station'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d): p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def change(p,a,b):
    s=p.read_text(encoding='utf-8-sig'); assert a in s,(p,a)
    p.write_text(s.replace(a,b),encoding='utf-8')

pr=read(H/'preview-validation.json'); ir=read(H/'isolated-validation.json'); ar=read(H/'analytic-validation.json')
assert pr['fingerprint']==ir['fingerprint']==ar['fingerprint']
assert pr['clips'][0]['validation']['decoded_frames']==600
assert pr['clips'][1]['three_repeated_decoded_payloads_identical']
assert all(v['pass'] for v in pr['clips'][0]['validation']['seam_checks'].values())
feedback="its' getting there, can we do anything with the computer screens?"
record={'date':'2026-10-03','status':'V3 screen animation preview delivered; user review pending',
 'source':read(H/'scene-plan-v3.json')['source'],'feedback_on_v2':feedback,
 'changes':['Moving marker and timed node activity follow the existing left-screen route',
 'Source log text scrolls inside a perspective-mapped right-screen viewport',
 'Existing status rows brighten independently; a small cursor and meter update'],
 'preview':pr['clips'][0],'three_loop_review':pr['clips'][1],'fingerprint':pr['fingerprint'],
 'preserved_v2_outside_screens_at_seconds':ar['v2_outside_screens_exact_at_seconds'],
 'dimensions':[1280,720],'fps':30,'duration_seconds':20,'silent':True,
 'four_k_export_produced':False,'user_motion_approved':False,
 'inspection':'Full-composition temporal stills, screen crops and decoded still inspected. Continuous playback not claimed.',
 'storage':'Local source/config/checks; review media ignored. No commit or push.'}
save(H/'delivery-v3.json',record)
(H/'README.md').write_text('''# The Last Cable Station - animation v3

2026-10-03. User described v2 as getting there and requested computer-screen activity. V3 adds only screen activity, preserving the v2 environment and lighting. Artistic review remains pending.

- [Twenty-second 720p preview](last-cable-station-v3-preview-20s.mp4)
- [Three-loop review, sixty seconds](last-cable-station-v3-three-loops-60s.mp4)
- [Isolated screen test, eight seconds](computers-isolated-v3-8s.mp4)
- [Delivery record](delivery-v3.json)
- [Configuration](scene-plan-v3.json)
- [Preserved v2](../cable-animation-v2/README.md)

The left monitor carries a small moving route marker and two timed node highlights along its existing map. The right monitor's original log texture scrolls upward inside a perspective-mapped viewport; existing status strokes brighten independently, with a small cursor and changing meter. Screen bezels and existing layouts stay fixed. All motion uses the common twenty-second period. The marker fades out before its return; log transport wraps forward through the join.

The v3 renderer extends the unchanged v2 renderer, which retains the v1 dependency. Source pixels outside the computer apertures match v2 exactly at 0, 4, 8, 12, 16 and 19.9667 seconds. The source plate remains the approved 1672x941 v3 artwork, bound by hash. Old versions are preserved.

The isolated test, full 600-frame preview and 1800-frame repeated review decode with correct counts and timestamps. Analytical screen endpoints/seams and encoded regional/composite seams pass. All three decoded repetitions match exactly; source-protection assertions run during rendering. See analytic-validation.json, isolated-validation.json and preview-validation.json for evidence and dependency hashes.

Full-scene temporal stills, enlarged screen crops and a decoded frame were inspected. Continuous assistant playback and user artistic acceptance are not claimed. Review at normal speed for screen activity and the join. The 720p preview is silent; 4K delivery awaits motion review. Final long-video duration remains unconfirmed, and no long assembly, credits, commit or push occurred.

Reproduce using render_cable_v3.py --stage samples, --stage isolated and --stage preview with the existing Python runtime and PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. Encoded outputs refuse overwrite. setup_scene.py records the initial config; effective masks and dependencies are fingerprinted in each validation report.
''',encoding='utf-8')
m=read(P/'manifest.json'); old=m['animation_current']; assert 'v2/' in old['package']
m['animation_current']={**old,'status':record['status'],'package':'../../music/cable-animation-v3/README.md',
 'delivery':'../../music/cable-animation-v3/delivery-v3.json','preview':record['preview']['path'],
 'preview_sha256':record['preview']['sha256'],'previous_version':'../../music/cable-animation-v2/README.md','feedback_on_v2':feedback}
save(P/'manifest.json',m)
change(P/'README.md','The [v2 twenty-second 720p animation preview](../../music/cable-animation-v2/README.md) is delivered and technically checked, adding requested distant cloud activity and room/sky lighting changes. V1 movement was described as okay; v2 visual review and 4K delivery remain pending.',
 'The [v3 twenty-second 720p animation preview](../../music/cable-animation-v3/README.md) is delivered and technically checked, adding map and console screen activity while preserving the v2 clouds and lighting. The user described v2 as getting there; v3 visual review and 4K delivery remain pending.')
change(R/'PRODUCTION_PIPELINE.md','V1 movement okay; v2 20-second 720p preview adds requested distant clouds and room/sky light changes; review pending','V3 20-second 720p preview adds screen activity; v2 clouds and lighting preserved; review pending')
change(R/'PRODUCTION_PIPELINE.md','Review animation v2 before 4K; confirm final duration before long assembly','Review animation v3 before 4K; confirm final duration before long assembly')
ag=R/'AGENTS.md'; s=ag.read_text(encoding='utf-8'); start=s.index('Current Cable Station animation ('); end=s.index('\n\n',start)
s=s[:start]+'Current Cable Station animation (2026-10-03): user described v2 as "getting there" and asked for computer-screen activity. V3 twenty-second 720p/30 fps silent preview and three-loop review delivered in music/cable-animation-v3/; see README.md and delivery-v3.json. Left screen has a moving route marker and node highlights; right screen has perspective-mapped source-log scrolling, independent status highlights, a cursor and small meter. V3 extends unchanged v2; clouds, haze, lamp and local daylight remain unchanged, with outside-screen source pixels matching v2 at six sampled times. V1/v2 and approved v3 artwork are preserved. Isolated eight-second screen test, full decode/count/timestamps, analytical/encoded seams, source protection and repeated payload checks passed. Assistant inspected temporal/decoded stills and screen crops, not continuous playback. V3 artistic review and 4K export pending; final long duration unconfirmed. No long assembly, commit or push.'+s[end:]
ag.write_text(s,encoding='utf-8')
cat=read(R/'final/catalog.json')
for e in cat:
    if e['folder']=='06-last-cable-station':
        e['status']='V3 art and audio/transition accepted; v3 screen animation preview awaits review'
        e['animation_preview']='../../music/cable-animation-v3/README.md'
save(R/'final/catalog.json',cat)
change(R/'final/README.md','Number 06 now has a revised twenty-second 720p v2 animation preview awaiting user review','Number 06 now has a twenty-second 720p v3 preview with animated screens awaiting user review')
print('V3 delivery and current status saved')
