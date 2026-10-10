from pathlib import Path
import json
root=Path('G:/AI/colony')
report=root/'final/07-icebound-weather-post/music/long-source-v1'
feedback="yeah i guess it's fine, can we make the hour long loop?"
p=report/'audition-v1.json'
c=json.loads(p.read_text(encoding='utf-8'))
c.update(status='User accepted transition and requested one-hour loop',user_join_approved=True,user_feedback=feedback,approval_date='2026-10-04',approval_scope='Transition accepted and one-hour audio requested; no full-hour listening claim.')
p.write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
target=report/'make-one-hour-v1.py'
assert not target.exists()
s=(root/'music/cable-animation-v3/make-two-hours-v1.py').read_text(encoding='utf-8')
replacements={
 'Mineral Valley Transit':'Winter Colony Night',
 '06-last-cable-station':'07-icebound-weather-post',
 'Last-Cable-Station-Mineral-Valley-Transit-2-Hours-v1.mp3':'Icebound-Weather-Post-Winter-Colony-Night-1-Hour-v1.mp3',
 '7154f7e3bf623d29e2b7419aba4efa8079b0237ae5ee0551150b2482d68300d8':'57232ba3451862836625c88aaabf22a2d7d3d056c50417bb86fcc85d85fbb626',
 'TOTAL=7200*SR':'TOTAL=3600*SR',
 'Last Cable Station':'Icebound Weather Post',
 'Two Hours':'One Hour',
 'sixteen-second':'eight-second',
 'of 120 minutes':'of 60 minutes',
 'two hours':'one hour',
 'two-hour':'one-hour',
 '2026-10-03':'2026-10-04',
 'Audio previously accepted as good enough; user requested combined final and confirmed 2 hours on 2026-10-04':feedback,
 'Short join approved and one-hour assembly requested. No full one-hour listening review claimed.':'Short join approved and one-hour audio requested. No full one-hour listening review claimed.',
 '.read_text()':'.read_text(encoding="utf-8")'
}
for a,b in replacements.items():s=s.replace(a,b)
# Keep the feedback literal valid inside the generated Python dictionary.
s=s.replace("'user_feedback':'"+feedback+"'", "'user_feedback':"+repr(feedback))
compile(s,str(target),'exec')
target.write_text(s,encoding='utf-8')
print(target)
