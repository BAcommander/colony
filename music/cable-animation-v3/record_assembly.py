from pathlib import Path
import json,shutil
R=Path('G:/AI/colony');H=Path(__file__).resolve().parent;P=R/'final/06-last-cable-station';A=P/'assembly-v1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def replace(p,a,b):
    s=p.read_text(encoding='utf-8-sig');assert a in s,(p,a);p.write_text(s.replace(a,b),encoding='utf-8')
d=read(A/'delivery-validation.json');v=read(P/'delivery-v3/delivery-validation.json');a=read(P/'music/long-source-v1/two-hour-delivery-v1.json');approval=read(H/'approved-v3-preview.json')
assert d['duration_seconds']==a['decoded_seconds']==7200 and d['validation']['full_video_audio_decode']
shutil.copy2(H/'assemble-with-colony.py',A/'assemble-with-colony.py')
shutil.copy2(H/'approved-v3-preview.json',P/'delivery-v3/approved-v3-preview.json')
replace(H/'README.md','Artistic review remains pending.','The user accepted this v3 look with "ok perfect" on 2026-10-03. The matching 4K master and confirmed two-hour Colony assembly are delivered; see ../../final/06-last-cable-station/assembly-v1/README.md.')
replace(H/'README.md','Continuous assistant playback and user artistic acceptance are not claimed.','Continuous assistant playback is not claimed. User acceptance is recorded separately in approved-v3-preview.json.')
replace(H/'README.md','The 720p preview is silent; 4K delivery awaits motion review. Final long-video duration remains unconfirmed, and no long assembly, credits, commit or push occurred.','The 720p preview is silent. The accepted look now has a verified 4K master and a two-hour combined export; full combined review remains pending. No credits, commit or push occurred.')
(A/'README.md').write_text('''# The Last Cable Station - two-hour Colony export

2026-10-03. The user accepted the v3 preview with "ok perfect", requested assembly through the existing tool and confirmed two hours. The actual Colony engine at C:/dev/SpeedySlideShow/colony/render.py produced the final MP4. App source was unchanged.

[Finished two-hour 4K video](../../../exports/06-last-cable-station/Last-Cable-Station-2-Hours-4K-v1.mp4)

7,200 seconds, 3840x2160 at 30 fps, H.264 and stereo 48 kHz AAC at 192 kb/s. The twenty-second master repeats 360 times. The original artwork is 1672x941, upscaled with Lanczos; no new native detail is claimed.

The selected Mineral Valley Transit soundtrack retains source 0:38-7:43, sixteen-second equal-power overlaps and fixed -7 dB gain, with one ten-second opening and twenty-second closing fade. Colony adds no gain, crossfade or overlay. The tool's peak limiter remains below its trigger for this soundtrack.

## Verification

The 4K loop passed full decoded frame/timestamp checks, per-region and composite encoded seam checks, and three exact decoded repetitions. Colony then fully decoded the two-hour video/audio. All 216,000 copied video packets have sequential timestamps, and every one of the 360 loop payloads matches. The first assembled loop's 600 decoded YUV pictures exactly match the verified 4K master. This carries the short-master seam validation through the full file.

See delivery-validation.json, colony-export.json and ../delivery-v3/delivery-validation.json. Opening, middle and ending decoded stills were inspected; continuous assistant playback, extended musical listening, upload checks and user approval of the full export are not claimed.

The runner seeds Colony's existing Prepared cache with a byte-identical master, preserving the established Floodplain/Saltline workaround for source colour changes from the app scaler. Colony performs the actual audio chain, stream-copy assembly, progress and full decode. Existing outputs are protected; --verify-only resumes delivery checks.

Video, MP3 and cached media remain local ignored exports; they are not backed up by Git. No commit, push or upload was performed.
''',encoding='utf-8')
(P/'YOUTUBE-FILES.md').write_text('''# The Last Cable Station - YouTube files

- [Final two-hour 4K MP4](../../exports/06-last-cable-station/Last-Cable-Station-2-Hours-4K-v1.mp4)
- [Thumbnail JPEG](thumbnail-v1.jpg)
- [Suggested title](youtube-title.txt)
- [Description](description.txt)
- [Search tags](youtube-tags.txt)
- [Two-hour soundtrack MP3](../../exports/06-last-cable-station/Last-Cable-Station-Mineral-Valley-Transit-2-Hours-v1.mp3)
- [Assembly and validation](assembly-v1/README.md)

The combined video is technically verified. Full combined viewing/listening and upload checks remain pending. The thumbnail retains its prior pending-review status. Long media remain local, ignored by Git.
''',encoding='utf-8')
replace(P/'README.md','Current status, 2026-09-28:','Current status, 2026-10-03:')
replace(P/'README.md','The user described v2 as getting there; v3 visual review and 4K delivery remain pending.','The user accepted v3 with "ok perfect" and confirmed two hours. The [4K master](video-4k-v3.mp4) and [two-hour Colony export](assembly-v1/README.md) are delivered and technically verified. See [YouTube files](YOUTUBE-FILES.md). Full combined review and upload checks remain pending.')
m=read(P/'manifest.json');m['status']='V3 artwork and animation look accepted; two-hour 4K Colony video delivered; full combined review and thumbnail review pending'
m['animation_current'].update(status='V3 look accepted; 4K master delivered and verified',user_motion_approved=True,four_k_export_produced=True,approval='delivery-v3/approved-v3-preview.json',four_k_delivery='delivery-v3/delivery-validation.json')
m['video']=v['master'];m['audio']={'file':a['file'],'sha256':a['sha256'],'duration_seconds':7200,'record':'music/long-source-v1/two-hour-delivery-v1.json'}
m['combined_export']={'file':Path(d['output']).relative_to(R).as_posix(),'sha256':d['sha256'],'bytes':d['bytes'],'duration_seconds':7200,'record':'assembly-v1/delivery-validation.json','tool':'Colony','full_combined_review':False};save(P/'manifest.json',m)
g=read(P/'music/generation-record.json');g.update(status='Two-hour soundtrack and combined 4K Colony video delivered; full listening pending',delivery_duration_seconds=7200,target_delivery_duration_seconds=7200,duration_status='User explicitly confirmed 2 hours on 2026-10-03',approval_scope='Supplied audio/transition accepted; two-hour extension and assembly authorized. Full long-form listening remains unclaimed.',two_hour_delivery='long-source-v1/two-hour-delivery-v1.json');save(P/'music/generation-record.json',g)
for file in [P/'music/README.md',P/'music/long-source-v1/README.md']:
    s=file.read_text(encoding='utf-8')
    if file.parent.name=='music':
        s=s.replace('The two-hour delivery target remains proposed, not confirmed.','The user confirmed two hours. The [two-hour soundtrack](../../../exports/06-last-cable-station/Last-Cable-Station-Mineral-Valley-Transit-2-Hours-v1.mp3) and [combined 4K Colony export](../assembly-v1/README.md) are delivered and fully decode-verified. See long-source-v1/two-hour-delivery-v1.json; full listening remains pending.')
        s=s.replace('No duration has been selected for this scene.','The user selected two hours, now delivered.')
    else:
        s=s.replace('Two-hour delivery is still a proposed duration, and animation has not started.','User confirmed two hours and accepted v3 animation. The [two-hour MP3](../../../../exports/06-last-cable-station/Last-Cable-Station-Mineral-Valley-Transit-2-Hours-v1.mp3) and combined 4K Colony video are now delivered. See two-hour-delivery-v1.json: same cut/overlap/gain, single ten-second opening/twenty-second closing fades, exact 7200-second decoded duration, -20.4 LUFS and -9.6 dBTP. Reproduce with ../../../../music/cable-animation-v3/make-two-hours-v1.py. Full combined review and listening remain pending.')
    file.write_text(s,encoding='utf-8')
replace(R/'PRODUCTION_PIPELINE.md','V3 20-second 720p preview adds screen activity; v2 clouds and lighting preserved; review pending','V3 look accepted; twenty-second 4K master delivered and verified')
replace(R/'PRODUCTION_PIPELINE.md','Mineral Valley Transit audio/transition accepted as good enough; long-form export pending','Two-hour Mineral Valley Transit MP3 delivered; approved sixteen-second joins; full decode passed')
replace(R/'PRODUCTION_PIPELINE.md','Review animation v3 before 4K; confirm final duration before long assembly','Two-hour 4K Colony export verified; full combined review and upload checks pending')
ag=R/'AGENTS.md';s=ag.read_text(encoding='utf-8')
for name,paragraph in [('Current Cable Station music (','Current Cable Station music (2026-10-03): user accepted the audio/transition as good enough, then explicitly confirmed 2 hours for the requested Colony assembly. Two-hour MP3 delivered at exports/06-last-cable-station/Last-Cable-Station-Mineral-Valley-Transit-2-Hours-v1.mp3. Same source 0:38-7:43, sixteen-second equal-power overlaps, 409-second repeat interval and fixed -7 dB gain; single ten-second opening/twenty-second closing fades. Full decode and exact 7200-second sample count passed, -20.4 LUFS/-9.6 dBTP. See final/06-last-cable-station/music/long-source-v1/two-hour-delivery-v1.json. Two-hour 4K combined video delivered through actual Colony tool at exports/06-last-cable-station/Last-Cable-Station-2-Hours-4K-v1.mp4; see assembly-v1/. Full video/audio decode, all 216000 packet timestamps and 360 exact loop payload repetitions passed. Originals preserved; full listening/combined review and upload checks remain pending. Local ignored media are not Git-backed; no commit or push.'),('Current Cable Station animation (','Current Cable Station animation (2026-10-03): user accepted v3 screen animation with "ok perfect" and requested Colony assembly. Approved preview and source/config/code hashes are in music/cable-animation-v3/approved-v3-preview.json. Matching twenty-second silent 4K/30 fps master is final/06-last-cable-station/video-4k-v3.mp4, upscaled from 1672x941. See delivery-v3/delivery-validation.json for full decode, layer/composite encoded seams, source protection, timestamps and three exact repeated decoded payload checks. Same v3 clouds/haze, lamp/local daylight and screen activity as accepted preview; originals and prior versions preserved. Two-hour combined export delivered and technically verified via existing Colony Prepared cache without scene re-encode or app edits. Assistant inspected temporal and decoded stills, not continuous playback; full combined user review pending. No commit, push or remote backup of new master yet.')]:
    start=s.index(name);end=s.index('\n\n',start);s=s[:start]+paragraph+s[end:]
ag.write_text(s,encoding='utf-8')
cat=read(R/'final/catalog.json')
for e in cat:
    if e['folder']=='06-last-cable-station':e.update(status='V3 artwork and animation look accepted; two-hour 4K Colony export delivered; combined review pending',assembly='06-last-cable-station/assembly-v1/README.md')
save(R/'final/catalog.json',cat)
replace(R/'final/README.md','Number 06 now has a twenty-second 720p v3 preview with animated screens awaiting user review','Number 06 now has an accepted v3 animation look, verified twenty-second 4K master and finished two-hour Colony export awaiting combined review')
inv=read(R/'final/local-export-inventory.json')
for path,report in [(a['file'],a),(Path(d['output']).relative_to(R).as_posix(),d)]:
    assert not any(x['path']==path for x in inv['files'])
    inv['files'].append({'path':path,'bytes':report['bytes'],'sha256':report['sha256'],'storage':'local ignored; not Git-backed'})
save(R/'final/local-export-inventory.json',inv)
print('Cable Station final delivery records updated')
