from pathlib import Path
import json,hashlib,re
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/'final/09-offshore-night-office'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
a=read(H/'analytic-validation.json');i=read(H/'isolated-validation.json');v=read(H/'preview-validation.json')
cache=read(H/'cache-validation.json');assert cache['fingerprint']==a['fingerprint'] and all(cache['cached_vs_uncached_source_frames_exact'].values())
assert a['fingerprint']==i['fingerprint']==v['fingerprint']
assert len(i['clips'])==3 and all(x['validation']['frames']==240 for x in i['clips'])
assert v['clips'][0]['validation']['frames']==1800 and v['clips'][1]['validation']['frames']==5400
assert v['clips'][0]['three_distinct_twenty_second_sections'] and v['clips'][1]['three_repeated_decoded_payloads_identical']
assert all(x['pass'] for c in v['clips'] for x in c['validation']['encoded_seam'].values())
assert all(a['retained_v2_sampled_exact'].values())
old=read(H.parent/'shoreless-animation-v2/delivery-v2.json');preserved={}
for name,key in [('preview','preview'),('review','three_loop_review')]:
 c=old[key];assert hashlib.sha256((R/c['path']).read_bytes()).hexdigest()==c['sha256'];preserved[c['path']]=c['sha256']
for path,sha in [('final/09-offshore-night-office/artwork-v1.png',old['fingerprint']['source_sha256']),('music/shoreless-animation-v2/scene-plan-v2.json',old['fingerprint']['config_sha256']),('music/shoreless-animation-v2/render_shoreless_v2.py',old['fingerprint']['renderer_sha256'])]:
 assert hashlib.sha256((R/path).read_bytes()).hexdigest()==sha;preserved[path]=sha
status='V3 genuine sixty-second silent 720p loop: calmer far-right sea, restrained right screen, retained left monitor, walkway flickers and unique minute lighting; review pending'
d={'date':'2026-10-06','status':status,'user_feedback':(H/'feedback-v2.txt').read_text(encoding='utf-8').strip(),'fingerprint':v['fingerprint'],'preview':v['clips'][0],'three_loop_review':v['clips'][1],'isolated_tests':i['clips'],'retained_v2_sampled_exact':a['retained_v2_sampled_exact'],'previous_media_source_config_renderer_preserved':preserved,'native_source_dimensions':[1672,941],'preview_dimensions':[1280,720],'duration_seconds':60,'fps':30,'silent':True,'user_motion_approved':False,'four_k_produced':False,'environment_period_seconds':20,'environment_frequency_change_percent':0,'unique_minute_evidence':'Different source states at 0/20/40 and different decoded 600-frame sections; independent minute-wide lighting/sunlight.','inspection':'Source/mask/temporal and decoded isolated/composite stills inspected; no continuous playback claim.','storage':'Local ignored media and environment cache. No credits, Git commit or push.'}
save(H/'delivery-v3.json',d)
d['cache_validation']=cache;save(H/'delivery-v3.json',d)
(H/'README.md').write_text('''# The Shoreless Colony animation v3 — one minute

2026-10-06. Requested revision and genuine sixty-second loop. User review pending.

- [Sixty-second silent 720p loop](shoreless-colony-v3-preview-60s.mp4)
- [Three-minute review: three exact repetitions](shoreless-colony-v3-three-loops-180s.mp4)
- [Delivery evidence](delivery-v3.json)
- [Scene plan](scene-plan-v3.json)
- [Renderer adapter](render_shoreless_v3.py)
- [Water region diagnostic](local-water-adjustment.png)

## Focused changes

Only the sea beyond the third tower is calmed. Source-space x1085–1145 forms a smooth transition; beyond x1145 displacement is 75% of v2 (.30 versus .40). Frequency, cloud travel, sea contrast and foam strength retain their previous settings. Sampled isolated water pixels left of x1085 match v2 exactly. The red diagnostic marks the affected water region; it is not in the video.

The conspicuous right-monitor waveform is removed. Original source imagery remains, with tiny tracking brackets, two restrained indicators and the existing narrow log/status activity. The v2 left monitor's route marker, sequential link highlights and node pulses are preserved, including continued activity after twenty seconds. Sampled left-monitor comparisons at 0, 7, 27 and 47 seconds match the corresponding v2 phase exactly. User expressed a preference for the left treatment; this does not approve every new v3 screen detail.

Three real walkway lamps at source coordinates (479,419), (826,415) and (893,414) have independent brief dim events. Masks include the emitting cores and nearby warm spill. Other walkway lights remain steady. Cabin masks are unchanged from corrected v2.

## Genuine minute timing

The principal sea/cloud/turbine/foam fields retain their twenty-second periods and speeds. Five- and ten-second antenna timing also divides the minute. No wave-frequency requantization or speed change is required. Lighting is composed independently across all sixty seconds: new cabin holds, exterior/room flickers, eight staggered walkway events and three differently timed/weighted sunlight openings. One cabin hold crosses the loop boundary. The complete frames at 0/20/40 differ; the three encoded twenty-second sections also differ. This is not three copied twenty-second videos.

The renderer reuses the unchanged, hash-bound v1/v2 implementations and masks. Source-resolution periodic environment frames are cached as lossless float32 arrays and composed with the actual minute lighting state. Cropped local masks avoid unnecessary full-frame work. The cache is reproducible and local under .environment-cache/; its fingerprint must match before reuse. Existing versions and source artwork remain unchanged.

## Checks and review scope

Three eight-second isolated tests cover water, computers and walkway lamps. Analytical layer seams/endpoints, source protection, sampled retained-layer comparisons and unique minute states passed. The 1,800-frame preview and 5,400-frame three-loop review fully decoded with sequential timestamps. Regional/composite encoded seam gates passed, no duplicate endpoint was added, and all three decoded minute repetitions match exactly. See analytic-validation.json, isolated-validation.json and preview-validation.json.

Assistant inspected source crops, masks, temporal samples and decoded stills, not continuous playback. Technical results do not establish artistic approval. Review the far-right water strength, subtle screen treatment and full-minute light timing at normal speed. The loop is 1280x720, 30 fps and silent. No music, 4K master or long assembly was produced; a future 4K export would upscale the native 1672x941 artwork.

Reproduce with render_shoreless_v3.py --stage samples, then isolated, then preview using the existing runtime and PYTHONPATH=G:/AI/youtube/.runtime/scene-tools. Outputs refuse overwrite. No paid generation, commit or push.
''',encoding='utf-8')
m=read(P/'manifest.json');previous=m.get('animation_current')
if previous and previous.get('preview')!=d['preview']['path']:m.setdefault('animation_history',[]).append(previous)
m['animation_current']={'status':status,'package':'../../music/shoreless-animation-v3/README.md','delivery':'../../music/shoreless-animation-v3/delivery-v3.json','preview':d['preview']['path'],'preview_sha256':d['preview']['sha256'],'source_sha256':d['fingerprint']['source_sha256'],'preview_seconds':60,'preview_dimensions':[1280,720],'fps':30,'user_motion_approved':False,'four_k_export_produced':False};save(P/'manifest.json',m)
rp=P/'README.md';s=rp.read_text(encoding='utf-8')
before='A [twenty-second v2 animation draft](../../music/shoreless-animation-v2/README.md) adds corrected window masks, sea foam, red/green rooftop antennas, clearer monitors, local flickers and sunlight. The v1 sea/cloud movement and turbine rotation are retained. User motion review is pending; no soundtrack or 4K delivery yet.'
after='A [genuine sixty-second v3 loop](../../music/shoreless-animation-v3/README.md) calms only the far-right sea, restores restrained right-monitor activity, preserves the preferred left monitor and adds walkway flickers. Independent cabin, room and sunlight schedules span the whole minute. User motion review is pending; no soundtrack or 4K delivery yet.'
assert before in s or after in s;rp.write_text(s.replace(before,after,1),encoding='utf-8')
rp=R/'PRODUCTION_PIPELINE.md';s=rp.read_text(encoding='utf-8');line=next(x for x in s.splitlines() if x.startswith('| 09 |'))
rp.write_text(s.replace(line,'| 09 | [The Shoreless Colony](final/09-offshore-night-office/README.md) | V3 genuine sixty-second 720p loop: calmer far-right sea, restrained right monitor, walkway flickers and unique minute lighting; review pending | Short/long prompts ready; no audio | Review v3 local water, monitors and minute timing before 4K |',1),encoding='utf-8')
rp=R/'AGENTS.md';s=rp.read_text(encoding='utf-8')
note='Current Shoreless animation (2026-10-06): user found only the far-right sea slightly excessive, rejected the large right-monitor graph, preferred the left monitor, and requested walkway flickers plus a one-minute loop. V3 silent sixty-second 720p/30 fps preview and three-repeat 180-second review are delivered in music/shoreless-animation-v3/; see README.md and delivery-v3.json. Same immutable artwork-v1.png SHA-256 f042d109358089f0e89b11c99a84505fba9a825dca3428ed7109055d29253f69, native 1672x941. Water displacement transitions from .40 to .30 only across source x1085–1145 beyond the third tower; sampled water left of x1085 is unchanged. Original right-screen images now have restrained tracking details; sampled left monitor retains v2 exactly at 0/7/27/47 seconds. Three real walkway lamps flicker with warm spill. Unique minute-wide cabin/exterior/room events and sunlight compose over unchanged-speed twenty-second environmental fields; this is not a copied twenty-second video. Cropped local effects and fingerprinted float32 environment caching reduce repeated work. Three isolated tests, analytic seams/protected pixels, distinct 0/20/40 source states and encoded sections, full 1800/5400-frame decodes/timestamps, regional/composite encoded seams and three exact decoded minute repetitions passed. Assistant inspected mask/temporal/decoded stills, not continuous playback. User visual review, music, 4K and long assembly pending. V1/v2 and prior scenes preserved; no credits, commit or push. Knowledge bank updated with the local-water correction and rejection of the prominent waveform.'
s,n=re.subn(r'Current Shoreless animation \([^\n]+',note,s,count=1);assert n==1;rp.write_text(s,encoding='utf-8')
rp=R/'final/catalog.json';cat=read(rp)
for e in cat:
 if e['folder']=='09-offshore-night-office':e.update(status=status,animation_preview='../../music/shoreless-animation-v3/README.md')
save(rp,cat)
rp=R/'creative/ANIMATION_KNOWLEDGE_BANK.md';s=rp.read_text(encoding='utf-8');a=s.index('### 09 The Shoreless Colony');b=s.index('## Render and delivery improvements to retain',a)
entry='''### 09 The Shoreless Colony

**Current candidate:** genuine sixty-second v3 revision, user review pending. User prefers v2 left-monitor activity and rejected its conspicuous right waveform. [Scene record](../music/shoreless-animation-v3/README.md), [configuration](../music/shoreless-animation-v3/scene-plan-v3.json), [adapter](../music/shoreless-animation-v3/render_shoreless_v3.py). V1/v2 remain preserved.

- Local criticism needs a local correction: user found only water beyond the third tower too strong. V3 smoothly reduces displacement from .40 to .30 across source x1085–1145; sampled water to the left remains exactly v2. Preserve sea speed, texture and the unaffected composition.
- Readable screen activity can still be excessive. The large cyan waveform was rejected; preserve original imagery with small route/tracking details. The left v2 route/node treatment is explicitly preferred. V3 preserves it at sampled times throughout the minute and restores the original right display with restrained details. New right treatment awaits review.
- Walkway flickers attach to three actual emitters, include white cores and local warm spill, and are staggered over the minute. Leave other lamps steady. No new invented light geometry.
- Complete pane masks need forced-dim crop review: small coordinate errors left bright strips on middle/far cabins in earlier attempts. Correct against actual source pixels, include bright cores/warm dividers, and preserve dark frames. V3 retains corrected v2 apertures.
- Foam follows photographed moving crests with broken coverage and caisson wash; it is an optical approximation. Tune independently of underlying water displacement. V3 retains v2 foam settings.
- Red/green antenna colors need a complete color cycle dividing the loop. Five-second pulses give a ten-second color cycle here; preserve true mast-tip placement and protected sampling/output.
- Extend a loop without slowing it: v3 retains twenty-second atmospheric fields and composes unique sixty-second cabin, lamp, walkway and sunlight schedules. Check full scenes at 0/20/40 and decoded sections for distinctness. Cached environment pixels are lossless float32 and bound to code/config/source fingerprints; light composition uses the actual minute time.
- Localized shafts and water warmth avoid global exposure pumping. The minute uses three distinct sunlight openings, not a stretched twenty-second timing envelope.
- Existing turbine blades rotate optically over reconstructed sky with fixed hub/mast restored. This remains an unapproved candidate method; inspect extraction edges/background before reuse elsewhere.

'''
rp.write_text(s[:a]+entry+s[b:],encoding='utf-8')
print('V3 minute delivery, scene status and knowledge bank recorded')
