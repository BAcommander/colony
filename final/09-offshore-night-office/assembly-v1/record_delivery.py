from pathlib import Path
import json,shutil
R=Path('G:/AI/colony');P=R/'final/09-offshore-night-office';H=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
d=read(P/'assembly-v1/delivery-validation.json');v=read(P/'delivery-v3/delivery-validation.json');a=read(P/'music/two-hour-v1/delivery.json')
assert d['duration_seconds']==7200 and d['validation']['video_packet_count']==216000
assert d['validation']['all_120_encoded_loop_payloads_identical'] and d['validation']['full_video_audio_decode']
assert all(x['pass'] for x in v['validation']['encoded_seam'].values())
rel=Path(d['output']).relative_to(R).as_posix()
summary=f'''The Shoreless Colony: final two-hour 4K video delivered 2026-10-10.

File: {d['output']}
7200 seconds, 3840x2160, 30 fps. H.264 with stereo 48 kHz AAC at 192 kb/s. Size: {d['bytes']:,} bytes. Native artwork 1672x941, Lanczos upscaled.

The user approved the music join and water-v2 balance and requested this two-hour 4K assembly. Source cut 0:40–7:24, fixed -6.9 dB music gain, twelve-second equal-power overlap and 392-second repeat interval. Water -19.411621485714146 dB, first onset 45 seconds, 35 seconds including twelve-second fade-in/eighteen-second fade-out, then 265 seconds off. One ten-second opening and twenty-second closing fade. No further SFX, normalization or fades during assembly.

Unchanged v3 native scene layers were rendered as a genuine sixty-second 4K master; source/config/renderer/dependency/mask fingerprint matches the preview. All 1800 frames/timestamps and regional/composite seams passed. Current v3 was authorized for final assembly; no additional detailed timing verdict is inferred.

The actual Colony engine reused the verified master through its Prepared cache. Full audio/video decode, all 216000 timestamps, 120 identical encoded repetitions and exact first-minute decoded YUV identity passed. See delivery-validation.json and colony-export.json. Assistant inspected decoded stills, not continuous playback. Full combined listening/viewing and upload checks remain pending. Originals preserved; media local, no commit/push/remote backup or upload.
'''
(P/'assembly-v1/README.txt').write_text(summary,encoding='utf-8')
(P/'delivery-v3/README.txt').write_text('The Shoreless Colony — 60-second 4K v3 master\n\nUnchanged native source layers, masks, configuration and renderer; fingerprint matches the v3 preview. 1800 frames at 30 fps, silent, 3840x2160, Lanczos upscaled from 1672x941. H.264 QP0 yuv420p, explicit BT.709 conversion and tags. Every frame, timestamp and regional/composite loop seam checked. Distinct 0/20/40-second frames; no duplicate endpoint. Decoded stills inspected at 0 and 8 seconds, no continuous playback claim. See delivery-validation.json. User authorized this current animation for the requested final two-hour assembly.\n',encoding='utf-8')
(P/'music/two-hour-v1/README.txt').write_text('The Shoreless Colony — approved two-hour soundtrack\n\nThe user approved'+summary.split('The user approved',1)[1].split('Unchanged v3',1)[0]+'\nSoundtrack: '+str(R/a['file'])+'\nExact hashes and settings: delivery.json\nApproval: approval.json\n',encoding='utf-8')
(P/'YOUTUBE-FILES.txt').write_text(f'''THE SHORELESS COLONY — UPLOAD FILES

Video: {d['output']}
Thumbnail: {P/'thumbnail-v2.jpg'}
Title: {P/'youtube-title.txt'}
Description: {P/'description.txt'}
Tags: {P/'youtube-tags.txt'}
Soundtrack: {R/a['file']}
Checks: {P/'assembly-v1/README.txt'}

Two hours, 4K/30 fps; original artwork upscaled from 1672x941. Approved music join and quieter water-v2 mix. Not uploaded.
''',encoding='utf-8')
p=P/'manifest.json';m=read(p);m['music_current'].update(status='Music join and water v2 approved; two-hour soundtrack and final video delivered',user_join_approved=True,user_water_mix_approved=True,target_final_duration_seconds=7200,two_hour_record='music/two-hour-v1/delivery.json');m['final_assembly']={'status':'Delivered and technically verified; full combined review/upload checks pending','record':'assembly-v1/delivery-validation.json','file':rel,'sha256':d['sha256'],'duration_seconds':7200,'dimensions':[3840,2160],'fps':30};m['four_k_current']={'file':v['master']['path'],'sha256':v['master']['sha256'],'record':'delivery-v3/delivery-validation.json','same_preview_fingerprint':True,'user_authorized_for_assembly':True};save(p,m)
p=P/'music/generation-record.json';m=read(p);m.update(status='Approved music join and water v2; final two-hour 4K video delivered',local_join_approved=True,water_mix_approved=True,final_duration_seconds=7200,final_video=rel);save(p,m)
p=R/'PRODUCTION_PIPELINE.md';lines=p.read_text(encoding='utf-8').splitlines()
for i,line in enumerate(lines):
 if line.startswith('| 09 |'):lines[i]='| 09 | [The Shoreless Colony](final/09-offshore-night-office/README.md) | Latest genuine sixty-second v3 rendered unchanged to verified 4K; authorized for final assembly | Music join and quieter water v2 approved; two-hour soundtrack verified | Two-hour 4K Colony export delivered and technically verified; full combined review/upload checks pending |'
p.write_text('\n'.join(lines)+'\n',encoding='utf-8')
p=R/'AGENTS.md';s=p.read_text(encoding='utf-8');i=s.index('Current Shoreless music (');j=s.index('\n\n',i)
current='Current Shoreless music (2026-10-10): User approved transition and quieter water v2 and requested two-hour loop plus 4K final. Delivered exports/09-offshore-night-office/Shoreless-Colony-2-Hours-4K-v1.mp4 via actual Colony; see final/09-offshore-night-office/assembly-v1/. Two-hour soundtrack uses source 0:40–7:24, twelve-second equal-power joins/392-second interval, -6.9 dB music, water -19.41162149 dB with 35-second events including 12/18-second fades and 265 seconds off, onset45. Single10/20-second opening/closing fades. Full sample decode and no-clipping check passed. Current v3 source fingerprint retained in sixty-second 4K master upscaled from1672x941. Full1800-frame and regional seam checks passed; final216000 timestamps,120 identical minute payloads, decoded first-minute identity and full audio/video decode passed. Music/water balance approved; latest animation authorized for final without inventing separate detailed timing verdict. Full combined user review/upload checks pending. Original files preserved; no commit, push or remote backup. Exact hashes/settings in delivery records.'
s=s[:i]+current+s[j:];i=s.index('Current Shoreless animation (');j=s.index('\n\n',i);part=s[i:j].replace('User visual review, music, 4K and long assembly pending.','Latest v3 later authorized for final assembly on 2026-10-10; verified 4K master and two-hour music/video now delivered. See Current Shoreless music. Full combined review/upload checks pending.');s=s[:i]+part+s[j:];p.write_text(s,encoding='utf-8')
p=R/'creative/MUSIC_WORKFLOW.md';s=p.read_text(encoding='utf-8');i=s.index('## Water ambience');j=s.index('\n## ',i+4);part=s[i:j].replace('This is a pending trial, not an approved default;','User approved v2 and the music join on 2026-10-10 ("transition is fine , water is fine") and requested the two-hour delivery. This is an accepted Shoreless setting, not a universal default;').replace('Music join approval remains separate.','Both approvals are recorded in the two-hour delivery; full-length listening remains pending.');s=s[:i]+part+s[j:];p.write_text(s,encoding='utf-8')
for p in [P/'README.md',P/'music/README.md']:
 s=p.read_text(encoding='utf-8');lines=s.splitlines();lines[1:1]=['','Current delivery (2026-10-10): approved music join and water v2 are included in the final two-hour 4K video. See '+('[upload files](YOUTUBE-FILES.txt) and [checks](assembly-v1/README.txt).' if p.parent==P else '[upload files](../YOUTUBE-FILES.txt) and [checks](../assembly-v1/README.txt).')+' Earlier preparation notes below describe previous states; full combined review/upload checks remain pending.',''];p.write_text('\n'.join(lines)+'\n',encoding='utf-8')
for name in ['render_delivery.py','build_audio.py','assemble-with-colony.py','record_delivery.py']:shutil.copy2(H/name,P/'assembly-v1'/name)
print('Shoreless delivery records and production tracker updated.',flush=True)
