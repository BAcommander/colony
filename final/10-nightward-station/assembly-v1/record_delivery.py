from pathlib import Path
import json,shutil
R=Path('G:/AI/colony');P=R/'final/10-nightward-station';H=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
d=read(P/'assembly-v1/delivery-validation.json');v=read(P/'delivery-v6/delivery-validation.json');a=read(P/'music/one-hour-v1/delivery.json')
assert d['duration_seconds']==3600 and d['validation']['video_packet_count']==108000
assert d['validation']['all_60_encoded_loop_payloads_identical'] and d['validation']['full_video_audio_decode']
assert all(x['pass'] for x in v['validation']['encoded_seam'].values())
assert (P/'delivery-v6/visual-inspection.json').exists()
rel=Path(d['output']).relative_to(R).as_posix()
summary=f'''Farpoint Station — one-hour 4K delivery, 2026-10-10

Video: {d['output']}
Soundtrack: {R/a['file']}
3600 seconds, 3840x2160, 30 fps; H.264 with stereo 48 kHz AAC at 192 kb/s. Size: {d['bytes']:,} bytes. Native artwork 1672x941, Lanczos upscaled.

The user chose Unfolding Warmth for the full Farpoint video after approving the join. One hour was recommended in response to their proposed runtime. The generated source is 298.54 seconds; retained 0:42–4:44, twelve-second equal-power sine/cosine overlaps, 230-second repeat interval and fixed -7 dB gain. One ten-second opening and twenty-second closing fade; no SFX. Full audio decode passed with exact 172800000 samples per channel, no clipping, {a['validation']['integrated_lufs']} LUFS and {a['validation']['true_peak_dbtp']} dBTP.

Latest v6 minute animation retained: source stars drift right/up, broad planetary weather, station lights/screens, cabinet LEDs and confined bar cleanup. Original effects snapshot loaded instead of the subsequently changed shared module. Source/config/renderer/loaded dependency/mask hashes match the preview. NumPy runtime version differs; all ten saved source states match byte for byte. All 1800 4K frames/timestamps and regional/composite seam checks passed; distinct states at 0/20/40 seconds and no duplicated endpoint.

Actual Colony engine used its Prepared cache to retain the verified master without scene re-encode. No additional gain, fades, overlay, SFX or loudness matching. Full video/audio decode, all 108000 video timestamps, 60 identical encoded loop payloads and exact first-minute decoded YUV identity passed.

Assistant inspected colour-aware decoded stills, not continuous playback or full-hour listening. User authorized the current scene for final assembly; no separate detailed v6 motion verdict inferred. Full combined review and upload checks remain pending. No upload, commit or push in this delivery. Long media and cache remain local; prior Git backups do not cover these new outputs.
'''
(P/'assembly-v1/README.txt').write_text(summary,encoding='utf-8')
(P/'delivery-v6/README.txt').write_text('Farpoint Station: sixty-second 4K v6 master\n\n'+summary.split('Latest v6',1)[1].split('Actual Colony',1)[0]+'See delivery-validation.json and visual-inspection.json.\n',encoding='utf-8')
(P/'music/one-hour-v1/README.txt').write_text('Farpoint Station: one-hour Unfolding Warmth soundtrack\n\n'+summary.split('The user chose',1)[1].split('Latest v6',1)[0]+'Soundtrack: '+str(R/a['file'])+'\nSee delivery.json.\n',encoding='utf-8')
(P/'YOUTUBE-FILES.txt').write_text(f'''FARPOINT STATION — UPLOAD FILES

Video: {d['output']}
Thumbnail: {P/'thumbnail-v2.jpg'}
Title: {P/'youtube-title.txt'}
Description: {P/'description.txt'}
Tags: {P/'youtube-tags.txt'}
Soundtrack: {R/a['file']}
Checks: {P/'assembly-v1/README.txt'}

One hour, 4K/30 fps; original artwork upscaled from 1672x941. Approved Unfolding Warmth music join. No added SFX. Not uploaded.
''',encoding='utf-8')
p=P/'manifest.json';m=read(p)
m['status']='One-hour 4K Farpoint video delivered and technically verified; full combined review/upload checks pending'
m['music_current']={'status':'Unfolding Warmth selected; approved join extended to one hour','user_join_approved':True,'target_final_duration_seconds':3600,'record':'music/one-hour-v1/delivery.json','source':a['source'],'sfx':None}
m['final_assembly']={'status':'Delivered and technically verified; full combined review/upload checks pending','record':'assembly-v1/delivery-validation.json','file':rel,'sha256':d['sha256'],'duration_seconds':3600,'dimensions':[3840,2160],'fps':30}
m['video']={'file':v['master']['path'],'sha256':v['master']['sha256'],'duration_seconds':60,'dimensions':[3840,2160],'fps':30,'silent':True,'native_source_dimensions':[1672,941]}
m['four_k_current']={'file':v['master']['path'],'sha256':v['master']['sha256'],'record':'delivery-v6/delivery-validation.json','preserved_dependency_snapshot':True,'exact_saved_preview_source_samples':True,'user_authorized_for_assembly':True}
if 'animation' in m:
 m['animation'].update(master_4k=v['master']['path'],status='V6 authorized for final assembly; one-hour 4K delivered',user_authorized_for_assembly=True)
save(p,m)
p=P/'music/generation-record.json';m=read(p);m.update(status='Unfolding Warmth selected; approved join and one-hour 4K video delivered',audio_approval=True,local_join_approved=True,delivery_duration_seconds=3600,final_duration_seconds=3600,final_video=rel,one_hour_record='one-hour-v1/delivery.json',full_hour_listening_approved=False,assembly_authorization=a['approval']);save(p,m)
p=P/'music/long-a-unfolding-warmth-v1/audition-v1.json';m=read(p);m.update(long_source_selected_for_final=True,final_duration_seconds=3600,subsequent_selection=a['approval']);save(p,m)
p=R/'PRODUCTION_PIPELINE.md';lines=p.read_text(encoding='utf-8').splitlines()
for i,line in enumerate(lines):
 if line.startswith('| 10 |'):lines[i]='| 10 | [Farpoint Station](final/10-nightward-station/README.md) | Latest v6 minute rendered to verified 4K using preserved effects; authorized for final assembly | Unfolding Warmth selected, join approved; one-hour soundtrack verified | One-hour 4K Colony export delivered and technically verified; full combined review/upload checks pending |'
p.write_text('\n'.join(lines)+'\n',encoding='utf-8')
p=R/'AGENTS.md';s=p.read_text(encoding='utf-8');i=s.index('Current Farpoint music (');j=s.index('\n\n',i)
current='Current Farpoint music/production (2026-10-10): User chose Unfolding Warmth for full Farpoint after accepting the join; one hour recommended and produced. Delivered exports/10-nightward-station/Farpoint-Station-1-Hour-4K-v1.mp4 via actual Colony; see final/10-nightward-station/assembly-v1/. Source 0:42–4:44, twelve-second equal-power joins, 230-second repeat interval, fixed -7 dB, one 10/20-second opening/closing fade; no SFX. Exact full audio decode/no clipping passed. Latest v6 rendered at native 1672x941 then Lanczos upscaled to 4K/30 fps, genuine sixty-second master. Preserved ambient_effects snapshot restores preview dependency; NumPy differs but all ten saved source states match exactly. Full 1800-frame timestamps/regional seams passed; final full audio/video decode, 108000 video timestamps, 60 identical loop payloads and first-minute decoded YUV identity passed. Decoded stills inspected, not continuous playback. Current scene authorized for assembly; no separate detailed v6 verdict inferred. Full combined review/upload checks pending. Originals preserved, second longer music option not needed for this delivery. New media local; no commit/push or remote backup.'
s=s[:i]+current+s[j:]
s=s.replace('V6 playback review pending; user confirmation still covers only v2 cloud visibility. 4K follows full-preview acceptance with identical motion and disclosed upscaling. Music/assembly separate.','Latest v6 subsequently authorized for final assembly on 2026-10-10; verified one-hour 4K delivery now complete. See Current Farpoint music/production. Full combined review remains pending.')
p.write_text(s,encoding='utf-8')
p=P/'README.md';s=p.read_text(encoding='utf-8')
s=s.replace('V6 user review is pending. Export 4K only after acceptance, with identical motion and disclosed upscaling from 1672x941. No soundtrack or long assembly yet.','Latest v6 authorized for final assembly on 2026-10-10; verified one-hour 4K video delivered with approved Unfolding Warmth loop. See [upload files](YOUTUBE-FILES.txt) and [delivery checks](assembly-v1/README.txt). Full combined review/upload checks remain pending; source detail is upscaled from 1672x941.')
s=s.replace('Music: [one-minute test prompt](music/elevenlabs-prompt-v1.txt), [longer-piece prompt](music/elevenlabs-long-version.txt), [manual workflow and listening checks](music/README.md). No audio generated or credits spent here. User runs short tests first, selects one, then a longer piece; local join review follows.','Music: Unfolding Warmth selected and approved join extended to one hour. See [soundtrack record](music/one-hour-v1/delivery.json) and [music history](music/README.md). Original tests/prompts retained. No paid generation performed in this delivery.')
p.write_text(s,encoding='utf-8')
p=P/'music/README.md';s=p.read_text(encoding='utf-8');start=s.index('Latest (');end=s.index('\n\n',start)
s=s[:start]+'Latest (2026-10-10): Unfolding Warmth selected for the full Farpoint video. Approved 0:42–4:44 cut, twelve-second equal-power join and -7 dB gain extended to one hour with single 10/20-second opening/closing fades, no SFX. See [soundtrack checks](one-hour-v1/delivery.json), [upload files](../YOUTUBE-FILES.txt) and [final video checks](../assembly-v1/README.txt). Full combined review/upload checks remain pending. Earlier preparation states below are historical; a second long variation is not required for this delivery.'+s[end:]
s=s.replace('Current (2026-10-10):','Earlier tests (2026-10-10):').replace('Current tests (2026-10-10):','Earlier prompts (2026-10-10):')
p.write_text(s,encoding='utf-8')
lesson=R/'creative/ANIMATION_KNOWLEDGE_BANK.md';text=lesson.read_text(encoding='utf-8')
text=text.replace("v6's positional stars, bar cleanup and cabinet LEDs await full-preview review, with technical evidence recorded.","v6's positional stars, bar cleanup and cabinet LEDs were subsequently authorized for the one-hour 4K assembly on 2026-10-10. Technical delivery passed; full combined playback review remains pending.")
marker='Farpoint dependency preservation (2026-10-10):'
if marker not in text:
 text+='\n'+marker+' the shared ambient_effects.py had changed after the saved v6 preview. Load the hash-verified scene dependency snapshot in the delivery adapter instead of replacing the shared file or ignoring a fingerprint mismatch. Source/config/renderer/mask hashes and all ten saved preview source states matched exactly; record the differing NumPy runtime explicitly. The unchanged native render then passed full 4K frame/seam and Colony hour-long picture/packet checks. See [Farpoint delivery](../final/10-nightward-station/delivery-v6/delivery-validation.json). This verifies retained output, not new artistic approval.\n'
lesson.write_text(text,encoding='utf-8')
for name in ['render_delivery.py','build_audio.py','assemble-with-colony.py','record_delivery.py']:shutil.copy2(H/name,P/'assembly-v1'/name)
print('Farpoint delivery records and tracker updated.',flush=True)
