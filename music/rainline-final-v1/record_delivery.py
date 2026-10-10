from pathlib import Path
import json,shutil
R=Path('G:/AI/colony');P=R/'final/08-rainline-relay';H=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
d=read(P/'assembly-v1/delivery-validation.json');v=read(P/'delivery-v5/delivery-validation.json')
assert d['duration_seconds']==3600 and d['validation']['video_packet_count']==108000
assert d['validation']['all_180_encoded_loop_payloads_identical'] and d['validation']['full_video_audio_decode']
assert all(c['pass'] for c in v['validation']['encoded_seam'].values())
rel=Path(d['output']).relative_to(R).as_posix()
(P/'assembly-v1/README.md').write_text(f'''# Rainline Relay â€” final one-hour 4K video

Delivered 2026-10-10: [final MP4](../../../{rel}). 3600 seconds, 3840x2160 at 30 fps, H.264 and stereo 48 kHz AAC at 192 kb/s. File size {d['bytes']:,} bytes. Native artwork is 1672x941, upscaled with Lanczos.

Actual Colony export engine: C:/dev/SpeedySlideShow/colony/render.py. Uses the verified twenty-second v5 master through the existing Prepared cache to preserve source pictures. Approved v3 rain soundtrack is premixed, so no additional SFX is applied. Loudness matching is off; no additional gain, music crossfades, fades or graphic overlay. The existing final limiter remains in the tool chain.

All video and audio fully decoded; all 108,000 video packet timestamps are sequential. All 180 repeated video packet sequences match. Every decoded YUV frame in the first loop matches the seam-checked 4K master. See delivery-validation.json and the native colony-export.json for evidence, source hashes and application version hashes.

User approved the music transition and v3 rain mix and explicitly requested latest scene 8 for final 4K assembly. This is authorization to use v5; it does not invent a separate detailed v5 timing verdict or full-hour viewing/listening review. Assistant inspected decoded stills, not continuous playback. Combined user review and upload checks remain pending. No upload, paid service, commit, push or remote backup performed. Original art, prior previews and earlier audio mixes preserved.

Reproduce with music/rainline-final-v1/render_delivery.py then assemble-with-colony.py. Existing media protected; --verify-only resumes checks. New master and long media remain local.
''',encoding='utf-8')
(P/'delivery-v5/README.md').write_text('''# Rainline Relay â€” twenty-second 4K v5 master

Rendered from the unchanged native source, configuration, masks, renderer and dependencies used for the latest v5 preview; fingerprints match. No creative or timing changes. Native 1672x941 frames are Lanczos-upscaled to 3840x2160, 30 fps, 600 frames, silent. Explicit BT.709 colour conversion/tags; H.264 QP0 yuv420p, no B frames.

All 600 encoded frames and timestamps verified. Every region and composite last-to-first seam passes the same adjacent-step gate. No duplicate endpoint; source protection asserted on every generated frame. Decoded first and eight-second stills inspected. No continuous playback claim. See delivery-validation.json. User requested final one-hour assembly with this latest scene version on 2026-10-10; no separate detailed motion review is inferred.
''',encoding='utf-8')
(P/'YOUTUBE-FILES.md').write_text(f'''# Rainline Relay â€” upload files

- [Final one-hour 4K video](../../{rel})
- [Thumbnail JPEG](thumbnail-v1.jpg)
- [Suggested title](youtube-title.txt)
- [Description](description.txt)
- [Tags](youtube-tags.txt)
- [Delivery checks](assembly-v1/README.md)

The video contains the approved music and quieter v3 rain mix. Upload review remains pending. Source artwork is upscaled from 1672x941.
''',encoding='utf-8')
p=P/'manifest.json';m=read(p)
m['music_current'].update(status='Music transition and v3 rain mix approved; included in final one-hour video',user_rain_mix_approved=True)
m['final_assembly']={'status':'Delivered and technically verified; combined playback/upload review pending','record':'assembly-v1/delivery-validation.json','file':rel,'sha256':d['sha256'],'duration_seconds':3600,'dimensions':[3840,2160],'fps':30}
m['four_k_current']={'file':v['master']['path'],'sha256':v['master']['sha256'],'record':'delivery-v5/delivery-validation.json','same_preview_fingerprint':True,'user_authorized_for_assembly':True}
save(p,m)
p=P/'music/generation-record.json';m=read(p);m.update(status='Music transition and v3 rain mix approved; final 4K hour assembled',final_video=rel);save(p,m)
p=R/'PRODUCTION_PIPELINE.md';s=p.read_text(encoding='utf-8');lines=s.splitlines()
for i,line in enumerate(lines):
 if line.startswith('| 08 |'):lines[i]='| 08 | [Rainline Relay](final/08-rainline-relay/README.md) | Latest twenty-second v5 rendered unchanged to verified 4K; user authorized final assembly | Music transition and quieter v3 rain mix approved; one-hour soundtrack verified | One-hour 4K Colony export delivered and technically verified; review combined video and upload checks |'
p.write_text('\n'.join(lines)+'\n',encoding='utf-8')
p=R/'AGENTS.md';s=p.read_text(encoding='utf-8')
prefix='Current Rainline production (2026-10-10): '
summary=prefix+'User approved quieter rain v3 ("yeah that\'s good") and requested final one-hour 4K through Colony. Delivered exports/08-rainline-relay/Rainline-Relay-1-Hour-4K-v1.mp4; see final/08-rainline-relay/assembly-v1/. Latest unchanged twenty-second v5 master at final/08-rainline-relay/video-4k-v5-20s.mp4 uses native 1672x941 source upscaled to 3840x2160/30 fps. Source/config/renderer/dependency/mask fingerprint matches preview; full 600-frame timestamps and regional/composite seam checks passed. Actual Colony Prepared cache preserves pictures; approved premixed rain-v3 hour used with no additional SFX, gain, fades, overlay or loudness matching. Full video/audio decode, all 108000 video timestamps, 180 identical encoded repetitions and first-loop decoded YUV identity passed. Music join and rain balance approved; latest v5 authorized for assembly without inventing separate detailed motion verdict. Decoded stills inspected, not continuous playback. Full combined review/upload checks pending. Original files preserved; new media local, no commit, push or remote backup.'
if prefix in s:
 start=s.index(prefix);end=s.index('\n\n',start);s=s[:start]+summary+s[end:]
else:s=s.replace('\n\n','\n\n'+summary+'\n\n',1)
# Supersede pending next-step wording in the existing Rainline music paragraph.
start=s.index('Current Rainline music (');end=s.index('\n\n',start);part=s[start:end]
part=part.replace('Separate v3 listening and full-hour review remain pending;', 'User approved v3 rain balance and requested final assembly; full-hour review remains pending;')
part=part.replace('V5 motion, 4K and video assembly remain pending.', 'Latest v5 4K and final one-hour assembly now delivered; see Current Rainline production.')
s=s[:start]+part+s[end:];p.write_text(s,encoding='utf-8')
p=P/'README.md';s=p.read_text(encoding='utf-8');s=s.replace('# 08 - Rainline Relay', '# 08 - Rainline Relay\n\nCurrent delivery: [one-hour 4K video and upload files](YOUTUBE-FILES.md), assembled through Colony with the approved quieter v3 rain mix. Complete decode, timing and repetition checks passed. See [assembly evidence](assembly-v1/README.md). Earlier preparation notes below are historical; final combined viewing/upload checks remain pending.',1)
s=s.replace('User motion review and 4K delivery remain pending.', 'Latest v5 is now authorized for final assembly and delivered in 4K.').replace('the music transition is approved; quieter rain v3 listening review remains pending.', 'the music transition and quieter rain v3 are approved.').replace('Further-reduced rain v3, full-hour listening and combined video remain pending review.', 'Rain v3 approved and final combined video delivered; full-hour viewing/listening remains pending.')
p.write_text(s,encoding='utf-8')
for name in ('render_delivery.py','assemble-with-colony.py'):
 shutil.copy2(H/name,P/'assembly-v1'/name)
print('Delivery records and live status updated.',flush=True)

p=P/'music/README.md';s=p.read_text(encoding='utf-8');s=s.replace('Music transition approved by the user; quieter rain v3 and extended listening remain pending;', 'Music transition and quieter v3 rain approved by the user; full-hour listening remains pending;').replace('Animation v5 review, 4K and final video assembly remain separate pending steps.', 'Latest v5 animation was authorized for final assembly; 4K master and final one-hour video are delivered. Combined review/upload checks remain pending.').replace('Animation v5 review, 4K and final video assembly remain separate pending steps.', 'Final one-hour 4K video now delivered.')
s=s.replace('Long exports are local under exports/. Animation v5 review, 4K and final video assembly remain separate pending steps.', 'Long exports are local under exports/. Final one-hour 4K video is delivered; combined review/upload checks remain pending.')
p.write_text(s,encoding='utf-8')
p=P/'music/long-source-v1/README.md';s=p.read_text(encoding='utf-8').replace('V2 sounded better; separate v3 listening review remains pending.', 'V3 rain balance now approved by the user and included in the final one-hour 4K video.').replace('No completed Rainline video or new animation is produced in this audio session.', 'The later one-hour 4K video assembly is now delivered; see ../../assembly-v1/.')
p.write_text(s,encoding='utf-8')

p=R/'AGENTS.md';s=p.read_text(encoding='utf-8');start=s.index('Current Rainline animation (');end=s.index('\n\n',start);part=s[start:end]
part=part.replace('user review, music, 4K and assembly pending.', 'User later approved the music/rain mix and requested latest-v5 final assembly on 2026-10-10. The verified twenty-second 4K master and one-hour Colony export are delivered; see Current Rainline production. Full combined playback/upload review remains pending.')
s=s[:start]+part+s[end:];p.write_text(s,encoding='utf-8')
