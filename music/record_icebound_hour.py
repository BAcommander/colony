from pathlib import Path
import json,hashlib
root=Path('G:/AI/colony'); package=root/'final/07-icebound-weather-post'; music=package/'music'; report=music/'long-source-v1'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def status(p,prefix,new):
    s=p.read_text(encoding='utf-8'); start=s.index(prefix); end=s.index('\n\n',start)
    p.write_text(s[:start]+new+s[end:],encoding='utf-8')
d=read(report/'one-hour-delivery-v1.json'); a=read(report/'analysis.json'); j=read(report/'audition-v1.json')
assert d['decoded_seconds']==3600 and d['decoded_samples_per_channel']==172800000 and d['true_peak_dbtp']<0 and j['user_join_approved']
feedback=j['user_feedback']
delivery_text=f'''# Icebound Weather Post — one-hour soundtrack

Delivered 2026-10-04: [one-hour MP3](../../../../{d['file']}). Exactly 3,600 decoded seconds, stereo 48 kHz, MP3 192 kb/s. Original source and auditions remain preserved.

User accepted the join and requested the hour: "{feedback}". Uses source 1:23–6:54, eight-second sine/cosine equal-power overlaps, 323-second repeat interval and fixed -8 dB gain, matching the accepted audition. Only the beginning and end of the complete hour receive fades: 10 seconds in, 20 seconds out.

Full decode checked every sample for finite values and clipping, and verified 172,800,000 samples per channel. Integrated loudness {d['integrated_lufs']} LUFS; true peak {d['true_peak_dbtp']} dBTP. Exact joins, source/script/export hashes and measured results are in one-hour-delivery-v1.json. Reproduce with make-one-hour-v1.py; existing exports are protected against overwrite.

Approval covers the short transition and extension request, not full-hour listening. No assistant listening or verified absence-of-vocals claim. Video assembly was not requested in this step; minute animation timing review and 4K delivery remain separate. Local ignored audio is not backed up by Git. No paid generation, commit or push.
'''
(report/'one-hour-delivery-v1.md').write_text(delivery_text,encoding='utf-8')
r=read(music/'generation-record.json')
r.update(status='One-hour Winter Colony Night MP3 delivered and fully verified; short transition approved',
         audio_approval=True,approval_scope='Short transition accepted and one-hour extension requested; full-hour listening not claimed',
         latest_user_feedback=feedback,local_join_review={'record':'long-source-v1/audition-v1.json','status':'user accepted 2026-10-04'},
         delivery={'record':'long-source-v1/one-hour-delivery-v1.json','path':d['file'],'sha256':d['sha256'],'seconds':3600})
save(music/'generation-record.json',r)
status(music/'README.md','Status 2026-10-04:','Status 2026-10-04: user accepted the transition and requested the one-hour loop. The [one-hour Winter Colony Night MP3](long-source-v1/one-hour-delivery-v1.md) is delivered and fully decode-verified. Original seven-minute source and both auditions are preserved. Full-hour listening and video assembly remain pending; no assistant listening claim.')
p=report/'README.md'; s=p.read_text(encoding='utf-8'); s=s.replace('User listening to the join and checking for unwanted voices remain pending. One-hour delivery is the requested target; it has not been made.', 'User accepted the short join and requested the hour on 2026-10-04. The [one-hour delivery](one-hour-delivery-v1.md) is now complete. Full-hour listening remains pending; absence of vocals is not independently verified.');p.write_text(s,encoding='utf-8')
p=package/'README.md';s=p.read_text(encoding='utf-8').replace('Current status, 2026-10-03:', 'Current status, 2026-10-04:').replace('No soundtrack produced.', 'The [one-hour Winter Colony Night soundtrack](music/long-source-v1/one-hour-delivery-v1.md) is delivered; short transition approved and full decode passed. Combined video remains pending.').replace('music/elevenlabs-prompt-v1.txt','music/elevenlabs-prompt-v3.txt').replace('music/elevenlabs-long-version.txt','music/elevenlabs-long-version-v3.txt').replace('Audio prompts are prepared only; the user runs credit-consuming generations manually.', 'The user generated the soundtrack manually; local looping used the accepted transition.');p.write_text(s,encoding='utf-8')
p=package/'manifest.json'; m=read(p)
m['music_preparation'].update(status='Historical preparation; current delivered soundtrack is in music_current',delivery_duration_seconds=3600)
# Refresh current mutable preparation records; original prompt hashes stay exact.
for f in m['music_preparation']['files']:
    f['sha256']=hashlib.sha256((package/f['path']).read_bytes()).hexdigest()
m['music_current']={'status':'One-hour MP3 delivered; transition approved; full decode passed','record':'music/long-source-v1/one-hour-delivery-v1.json','file':d['file'],'sha256':d['sha256'],'seconds':3600,'user_join_approved':True,'full_hour_listening_approved':False}
save(p,m)
p=root/'PRODUCTION_PIPELINE.md';s=p.read_text(encoding='utf-8').replace('Last updated: 2026-10-03.','Last updated: 2026-10-04.').replace('Seven-minute Winter Colony Night supplied; join and 16:17 auditions ready; one-hour target','One-hour Winter Colony Night MP3 delivered; eight-second join accepted; full decode passed').replace('review music join at 0:25–0:33 and check for unwanted voices','review full-hour soundtrack before combined assembly');p.write_text(s,encoding='utf-8')
status(root/'AGENTS.md','Current Icebound music (','Current Icebound music (2026-10-04): user accepted the Winter Colony Night transition and requested the hour with "'+feedback+'". Delivered exports/07-icebound-weather-post/Icebound-Weather-Post-Winter-Colony-Night-1-Hour-v1.mp3; see final/07-icebound-weather-post/music/long-source-v1/one-hour-delivery-v1.md/.json. Exact 3600 seconds, stereo 48 kHz/192 kb/s MP3. Same source 1:23–6:54, eight-second equal-power overlaps, 323-second repeat interval and fixed -8 dB gain; one ten-second opening and twenty-second closing fade. Every decoded sample finite, exact sample count and no clipping; '+str(d['integrated_lufs'])+' LUFS and '+str(d['true_peak_dbtp'])+' dBTP. Approval covers short join and extension, not full-hour listening; no assistant listening or independent vocal-absence claim. Original source and auditions preserved. Minute animation timing review, 4K and combined assembly remain pending. No credits, commit or push; ignored audio is local, not Git-backed.')
p=root/'final/local-export-inventory.json';inv=read(p);inv['date']='2026-10-04'
items=[{'path':d['file'],'bytes':d['bytes'],'sha256':d['sha256']},{'path':a['source'],'bytes':a['bytes'],'sha256':a['sha256'],'source_path':a['original_path']}]+[{k:f[k] for k in ['path','bytes','sha256']} for f in j['files']]
existing={v['path'] for v in inv['files']}
for item in items:
    if item['path'] not in existing:inv['files'].append({**item,'storage':'local ignored; not backed up by Git'})
save(p,inv)
print('One-hour delivery records, inventory and production status saved.')
