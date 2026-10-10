from pathlib import Path
import json
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/'final/07-icebound-weather-post'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def change(p,a,b):
 s=p.read_text(encoding='utf-8-sig');assert a in s,(p,a);p.write_text(s.replace(a,b),encoding='utf-8')
d=read(H/'delivery-v2.json')
approval={'date':'2026-10-03','user_feedback':"i think it's good, is there anything else we could change?",'scope':'V2 preview look accepted. User asks for possible refinements; no revised timing, longer loop, 4K export or soundtrack authorized by this message.','preview':d['preview'],'fingerprint':d['fingerprint'],'longer_loop_status':'Optional suggestion only; not implemented or approved'}
save(H/'approved-v2-preview.json',approval)
d.update(status='V2 preview look accepted; possible refinements under discussion',user_motion_approved=True,approval_record='approved-v2-preview.json');save(H/'delivery-v2.json',d)
m=read(P/'manifest.json');m['animation_current'].update(status=d['status'],user_motion_approved=True,approval='../../music/icebound-animation-v2/approved-v2-preview.json');save(P/'manifest.json',m)
change(H/'README.md','V2 is a twenty-second 720p/30 fps silent review candidate, not yet accepted.','V2 is a twenty-second 720p/30 fps silent preview. User accepted the look with "i think it\'s good" and asked about possible refinements; see approved-v2-preview.json. Longer timing changes remain proposals only.')
change(H/'README.md','Continuous assistant playback and user artistic acceptance are not claimed.','Continuous assistant playback is not claimed. User acceptance of the v2 look is recorded separately.')
change(P/'README.md','User motion review and 4K delivery remain pending.','User accepted the v2 look on 2026-10-03 ("i think it\'s good"); possible refinements are under discussion. 4K delivery remains pending.')
change(R/'PRODUCTION_PIPELINE.md','V2 twenty-second 720p preview adds requested snowfall and antenna beacons; review pending','V2 twenty-second preview look accepted; snowfall and antenna beacons included')
change(R/'PRODUCTION_PIPELINE.md','Review animation v2 before 4K; run music tests separately','Decide whether to extend light timing before 4K; run music tests separately')
ag=R/'AGENTS.md';s=ag.read_text(encoding='utf-8');start=s.index('Current Icebound animation (');end=s.index('\n\n',start);paragraph=s[start:end]
paragraph=paragraph.replace('User artistic review, 4K delivery and soundtrack remain pending;','User accepted the v2 look with "i think it\'s good, is there anything else we could change?"; exact preview/fingerprint and approval scope are in approved-v2-preview.json. A longer cycle with less predictable light timings is only an optional suggestion, not requested implementation. 4K delivery and soundtrack remain pending;')
ag.write_text(s[:start]+paragraph+s[end:],encoding='utf-8')
cat=read(R/'final/catalog.json')
for e in cat:
 if e['folder']=='07-icebound-weather-post':e['status']='V3 art and v2 animation look accepted; possible refinements under discussion; no soundtrack'
save(R/'final/catalog.json',cat)
print('V2 look acceptance recorded; no render settings changed')
