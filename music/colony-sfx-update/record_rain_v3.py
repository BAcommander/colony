from pathlib import Path
import json
root=Path('G:/AI/colony');package=root/'final/08-rainline-relay';folder=package/'music/long-source-v1'
d=json.loads((folder/'rain-mix-delivery-v3.json').read_text())
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
p=package/'music/generation-record.json';r=json.loads(p.read_text(encoding='utf-8'))
r.update(status='Music join approved; v2 rain liked; requested quieter v3 delivered',rain_settings=d['sfx'],
 rain_delivery_record='music/long-source-v1/rain-mix-delivery-v3.json',
 current_rain_export=Path(d['files'][1]['path']).relative_to(root).as_posix(),
 rain_feedback=d['user_feedback'],approval_scope=d['approval_scope'])
dump(p,r)
p=package/'manifest.json';m=json.loads(p.read_text(encoding='utf-8'));m['music_current'].update(
 status=r['status'],rain_delivery_record=r['rain_delivery_record'],current_rain_export=r['current_rain_export'],
 user_rain_mix_approved=False,rain_v2_positive_feedback=True)
dump(p,m)
dump(root/'music/shared-rain-overlay/rain-preset-current.json',{
 'name':'Rainline restrained intermittent rain','date':'2026-10-10','settings':d['sfx'],
 'source_sha256':d['rain_sha256'],'music_reference_lufs':-20.5,
 'rain_amplitude_relative_to_v1':.4375,
 'feedback_history':[{'version':1,'gain_db':-4,'feedback':'Too loud when rain reaches peak'},
 {'version':2,'gain_db':-10.020599913279625,'feedback':'Sounds better; reduce peak another 10–15%'},
 {'version':3,'gain_db':d['sfx']['gain_db'],'feedback':'Requested midpoint 12.5% reduction implemented; separate listening verdict pending'}],
 'reuse':'Starting point for this exact rain source against similarly quiet music. Rebalance other sources/music by listening at the maximum rain plateau; do not copy the gain universally.',
 'evidence':'final/08-rainline-relay/music/long-source-v1/rain-mix-delivery-v3.json',
 'tool':'C:/dev/SpeedySlideShow/colony/sfx.py',
 'app_defaults_changed':False})
lesson='''## Rain and reusable ambience — learned with Rainline, 2026-10-10

Keep music and environmental sound as independent sources. Approve the music crossfade separately, then judge the SFX at its maximum sustained level, not only while it fades in. A comfortable entrance can still become too loud at the plateau. Preserve a music-only long export so SFX revisions never require changing the accepted music join.

User feedback: v1 rain was too loud at peak. Halving its amplitude in v2 sounded better; the user then requested another 10–15% peak reduction. V3 uses the midpoint, 12.5% below v2: 43.75% of v1 rain amplitude overall. For this exact supplied rain file, the gains are v1 -4 dB, v2 -10.0206 dB, v3 -11.1804 dB. These are amplitude changes, not claims of proportional perceived loudness. V2 received positive feedback; v3 implements the requested adjustment but has no separate listening verdict yet.

Reusable starting recipe: rain enters after 20 seconds; 120 seconds on including a 20-second fade-in and 30-second fade-out; 90 seconds fully off. Smooth the 30-second source's repeat with a two-second equal-power overlap (28-second prepared loop). Rain follows the same envelope after level changes; the approved music stays untouched. Quiet intervals and slow re-entry provide variation without pushing rain into the foreground. These timings were retained during volume review, not independently compared or universally approved.

Use the saved preset with this rain source against music near the Rainline dry hour's -20.5 LUFS, then audition the plateau and quieter music passages. Different recordings or music levels need a fresh balance; do not apply this dB gain blindly or change the application's global default from one scene's feedback. Avoid applying rain twice: choose music-only plus the SFX input, or the premixed hour alone. Colony has separate video and audio-mix previews; the mix preview uses actual timings.

Evidence: [v3 delivery and exact feedback](../final/08-rainline-relay/music/long-source-v1/rain-mix-delivery-v3.json), [reusable preset](../music/shared-rain-overlay/rain-preset-current.json), [original rain record](../music/shared-rain-overlay/rain-source-v1.json). Full sample-count, finite-sample and peak checks support delivery integrity, not a listening verdict. Source, v1 and v2 are preserved. User explicitly approved the music transition: "the transition between pieces sounds totally fine".

'''
p=root/'creative/MUSIC_WORKFLOW.md';s=p.read_text(encoding='utf-8');heading='## Rain and reusable ambience'
if heading in s:
 start=s.index(heading);end=s.find('\n## ',start+3);s=s[:start]+lesson+(s[end+1:] if end>=0 else '')
else:s=s.replace('## Evidence and analysis discipline',lesson+'## Evidence and analysis discipline',1)
p.write_text(s,encoding='utf-8')
p=root/'PRODUCTION_PIPELINE.md';s=p.read_text(encoding='utf-8')
s=s.replace('half-volume rain v2 delivered and fully decoded; rain balance review pending','v2 rain liked; further 12.5% reduction delivered as v3; rain review pending').replace('Review quieter rain v2 and v5 motion','Review quieter rain v3 and v5 motion')
p.write_text(s,encoding='utf-8')
p=root/'AGENTS.md';s=p.read_text(encoding='utf-8');start=s.index('Current Rainline music (');end=s.index('\n\n',start);part=s[start:end]
part=part.replace('current v2 is -10.0206 dB (exactly half v1 amplitude)', 'current v3 is -11.1804 dB (43.75% of v1 amplitude)')
part=part.replace('Rain v2 balance and full-hour listening remain pending; v1 preserved.', 'User said v2 sounds better and requested another 10–15% peak reduction. V3 implements 12.5% less rain than v2, with unchanged music/fade/gap timings; preview and hour passed full decode checks. Separate v3 listening and full-hour review remain pending; previous versions preserved. See rain-mix-delivery-v3.json. Reuse lessons and exact feedback are in creative/MUSIC_WORKFLOW.md under Rain and reusable ambience, with music/shared-rain-overlay/rain-preset-current.json; source-specific starting point, not a universal or globally changed app default.')
s=s[:start]+part+s[end:];p.write_text(s,encoding='utf-8')
# Keep current navigation current; historical delivery records remain immutable.
for p in (package/'README.md',package/'music/README.md',folder/'README.md'):
 s=p.read_text(encoding='utf-8')
 s=s.replace('quieter rain v2','quieter rain v3').replace('quieter rain v2','quieter rain v3')
 s=s.replace('Half-volume rain v2','Further-reduced rain v3').replace('half-amplitude v2 is now','further-reduced v3 is now')
 s=s.replace('Rainline-rain-mix-preview-v2-half-volume.mp3','Rainline-rain-mix-preview-v3.mp3')
 s=s.replace('Rainline-Relay-1-Hour-with-Rain-v2-half-volume.mp3','Rainline-Relay-1-Hour-with-Rain-v3.mp3')
 s=s.replace('rain-mix-delivery-v2.json','rain-mix-delivery-v3.json').replace('Current v2','Current v3').replace('current v2','current v3')
 s=s.replace('-10.0206 dB relative to the supplied rain (50% of v1 amplitude)', '-11.1804 dB relative to the supplied rain (43.75% of v1 amplitude)')
 s=s.replace('Rain alone is reduced by 6.0206 dB, to exactly 50% of v1 amplitude;', 'Rain alone is reduced another 12.5% from the positively reviewed v2, to 43.75% of v1 amplitude;')
 s=s.replace('Rain v2 listening review remains pending.', 'V2 sounded better; separate v3 listening review remains pending.')
 p.write_text(s,encoding='utf-8')
print('Recorded v3 delivery, approval scope, reusable rain preset and music workflow lessons.')
