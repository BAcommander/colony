from pathlib import Path
import json,hashlib
R=Path('G:/AI/colony');P=R/'final/07-icebound-weather-post';H=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def paragraph(p,prefix,value):
    s=p.read_text(encoding='utf-8');i=s.index(prefix);j=s.index('\n\n',i)
    p.write_text(s[:i]+value+s[j:],encoding='utf-8')
d=read(P/'assembly-v1/delivery-validation.json');v=read(P/'delivery-v3/delivery-validation.json');a=read(P/'music/long-source-v1/one-hour-delivery-v1.json')
assert d['duration_seconds']==3600 and d['validation']['video_packet_count']==108000
assert d['validation']['all_60_encoded_loop_payloads_identical'] and d['validation']['full_video_audio_decode']
assert all(c['pass'] for c in v['validation']['encoded_seam'].values())
rel=Path(d['output']).relative_to(R).as_posix()
(P/'delivery-v3/README.md').write_text('''# Icebound Weather Post — sixty-second 4K master

2026-10-04. User requested: "use our tool to make the final hour long video". The latest v3 minute is used for that assembly. This authorizes delivery; it does not constitute a separately stated full v3/4K playback verdict. Earlier v2 look acceptance remains preserved.

[Silent 4K master](../video-4k-v3-60s.mp4): 3840x2160, 30 fps, 1800 frames, sixty seconds. Rendered from the unchanged scene renderer/configuration used for the verified minute preview, with source/config/dependency fingerprint matching. Native 1672x941 source frames are upscaled with Lanczos. H.264 QP0 yuv420p preserves the encoded picture data for repetition.

Full master decoded; all frame dimensions/timestamps and every adjacent frame's regional/composite motion were checked. Last-to-first seam passes the unchanged max-step gate for each layer and composite. Endpoint is not duplicated; frames at 0/20/40 differ because minute lighting is unique. Weather retains its accepted twenty-second local cycle and speed. Decoded stills inspected, not continuous playback.

The final hour checks sixty identical encoded loop payload repetitions, first-loop decoded YUV identity with this master and full video/audio decode. See ../assembly-v1/. Originals and previous previews remain intact. New master is local, not remotely backed up. Reproduce with music/icebound-animation-v3/render_delivery.py from repository root; existing output is protected.
''',encoding='utf-8')
(P/'assembly-v1/README.md').write_text(f'''# Icebound Weather Post — one-hour Colony video

Delivered 2026-10-04: [final MP4](../../../{rel}). Exactly 3600 seconds, 3840x2160 at 30 fps, H.264 with stereo 48 kHz AAC 192 kb/s. File size {d['bytes']:,} bytes. Source detail is upscaled from 1672x941.

The user's existing Colony engine at C:/dev/SpeedySlideShow/colony/render.py assembled the latest sixty-second v3 animation with the accepted one-hour Winter Colony Night soundtrack. Existing Prepared cache contains a byte-identical verified short master, avoiding the app scaler's previously observed colour change. App code is unchanged. No overlay, additional audio gain, new fades or extra music crossfade was applied. The soundtrack already contains its approved eight-second joins and single opening/closing fades.

Verified full video/audio decode, all 108,000 sequential video packet timestamps and sixty exact loop payload repetitions. Every decoded YUV frame in the first assembled minute matches the seam-verified 4K master. Hashes, app/runner versions and settings are in delivery-validation.json; native tool manifest is colony-export.json.

User asked to make the final hour-long video; no separate full v3 timing verdict, continuous assistant playback, full-hour user listening or upload checks are claimed. Decoded stills inspected. Original media and earlier versions preserved. Video, soundtrack and cache are local ignored exports, not backed up by Git. No paid generation, app changes, commit, push or upload occurred.

Runner: music/icebound-animation-v3/assemble-with-colony.py. Existing output protected; --verify-only resumes final checks.
''',encoding='utf-8')
(P/'YOUTUBE-FILES.md').write_text(f'''# Icebound Weather Post — YouTube files

- [Final one-hour 4K video](../../{rel})
- [One-hour soundtrack](../../{a['file']})
- [Thumbnail JPEG](thumbnail-v1.jpg)
- [Suggested title](youtube-title.txt)
- [Description](description.txt)
- [Tags](youtube-tags.txt)
- [Delivery checks](assembly-v1/README.md)

Technical checks passed. Combined viewing/listening and upload checks remain pending. Thumbnail keeps its existing review status. Long exports remain local and ignored by Git.
''',encoding='utf-8')
paragraph(P/'README.md','Current status,','Current status, 2026-10-04: clean v3 artwork and v2 animation look accepted. At the user\'s request, the latest sixty-second v3 animation was rendered to 4K and assembled with the one-hour Winter Colony Night soundtrack using Colony. The [final hour-long video](assembly-v1/README.md) is delivered and technically verified; see [YouTube files](YOUTUBE-FILES.md). Full combined review and upload checks remain pending. No separate full v3 timing verdict is inferred; thumbnail v1 retains its previous pending-review status.')
m=read(P/'manifest.json');m['status']='One-hour 4K Colony video delivered and technically verified; combined review pending'
m['animation_current'].update(status='Latest sixty-second v3 used for authorized final assembly; 4K master delivered and verified',four_k_export_produced=True,four_k_delivery='delivery-v3/delivery-validation.json',assembly_authorized=True,assembly_request='use our tool to make the final hour long video')
m['video']=v['master'];m['combined_export']={'file':rel,'sha256':d['sha256'],'bytes':d['bytes'],'duration_seconds':3600,'record':'assembly-v1/delivery-validation.json','tool':'Colony','full_combined_review':False};save(P/'manifest.json',m)
paragraph(P/'music/README.md','Status 2026-10-04:','Status 2026-10-04: accepted transition extended into a verified one-hour soundtrack, now assembled with the latest v3 animation in the [one-hour 4K Colony video](../assembly-v1/README.md). Original source and auditions preserved. Full-hour listening and combined review remain pending; no assistant listening claim.')
g=read(P/'music/generation-record.json');g.update(status='One-hour soundtrack and combined 4K Colony video delivered; full listening pending',combined_video={'file':rel,'record':'../assembly-v1/delivery-validation.json'});save(P/'music/generation-record.json',g)
# Keep mutable preparation hashes current.
m=read(P/'manifest.json')
for f in m['music_preparation']['files']:f['sha256']=hashlib.sha256((P/f['path']).read_bytes()).hexdigest()
save(P/'manifest.json',m)
p=R/'PRODUCTION_PIPELINE.md';s=p.read_text(encoding='utf-8');s=s.replace('V2 look accepted; requested sixty-second v3 preview delivered with varied lighting; new timing review pending','V2 look accepted; sixty-second v3 4K master delivered for requested final assembly').replace('Review minute light timing before 4K; review full-hour soundtrack before combined assembly','One-hour 4K Colony export verified; full combined review and upload checks pending');p.write_text(s,encoding='utf-8')
paragraph(R/'AGENTS.md','Current Icebound animation (','Current Icebound animation (2026-10-04): user requested "use our tool to make the final hour long video". Latest sixty-second v3 animation rendered unchanged from source to final/07-icebound-weather-post/video-4k-v3-60s.mp4, 4K/30 fps/1800 frames, Lanczos upscaled from 1672x941. Full decode/timestamps, distinct 0/20/40 frames, no duplicate endpoint and all regional/composite encoded seam gates passed; see delivery-v3/. Existing Colony engine assembled exports/07-icebound-weather-post/Icebound-Weather-Post-1-Hour-4K-v1.mp4 with the accepted one-hour soundtrack. Prepared cache preserved source colour/pictures without app changes. Full video/audio decode, 108000 timestamps, sixty identical loop packet payloads and decoded first-minute identity passed; see assembly-v1/. User authorized latest version for final assembly; separate full v3 timing verdict is not inferred from that request. Earlier v2 look acceptance remains preserved. Assistant inspected decoded stills, not continuous playback. Full combined review and upload checks pending. Originals preserved; no commit/push or remote backup of new media.')
p=R/'AGENTS.md';s=p.read_text(encoding='utf-8').replace('Minute animation timing review, 4K and combined assembly remain pending.', 'Latest v3 4K master and one-hour Colony combined video are now delivered; see Current Icebound animation. Full combined review remains pending.');p.write_text(s,encoding='utf-8')
p=R/'final/catalog.json';cat=read(p)
for e in cat:
    if e['folder']=='07-icebound-weather-post':e.update(status='One-hour 4K Colony export delivered; combined review pending',assembly='07-icebound-weather-post/assembly-v1/README.md',duration_seconds=3600,music_prompt='music/elevenlabs-prompt-v3.txt')
save(p,cat)
p=R/'final/local-export-inventory.json';inv=read(p)
assert not any(x['path']==rel for x in inv['files'])
inv['files'].append({'path':rel,'bytes':d['bytes'],'sha256':d['sha256'],'storage':'local ignored; not backed up by Git'});save(p,inv)
print('Icebound final video delivery, inventory and current status saved',flush=True)
