from pathlib import Path
import json,hashlib,shutil
root=Path('G:/AI/colony')
package=root/'final/08-rainline-relay'
folder=package/'music/long-source-v1'
d=json.loads((folder/'one-hour-delivery-v1.json').read_text())
def dump(p,data):p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
def relative(p):return Path(p).relative_to(root).as_posix()
record=package/'music/generation-record.json'
r=json.loads(record.read_text(encoding='utf-8'))
r.update(status='One-hour music-only and intermittent rain versions delivered; join/mix listening review pending',
 long_export=relative(d['source']),long_source_sha256=d['source_sha256'],source_duration_confirmed_by_user=True,
 delivery_duration_seconds=3600,audio_approval=False,
 user_feedback="here's the final 7 minute peace, i think we make this into a 1 hour long variant? can we update our tool to allow the rain SFX to be added aswell? maybe intermittently with fade in-s and ourts which can be customized?",
 local_join_review='music/long-source-v1/Rainline-music-join-review-60s-v1.mp3',
 delivery_record='music/long-source-v1/one-hour-delivery-v1.json',
 approval_scope=d['approval_scope'],rain_source=relative(d['rain_source']),rain_settings=d['sfx'],
 one_hour_exports=[relative(f['path']) for f in d['files'][:2]])
dump(record,r)
p=package/'manifest.json';m=json.loads(p.read_text(encoding='utf-8'))
m['music_current'].update(status=r['status'],long_source=r['long_export'],long_source_sha256=d['source_sha256'],
 final_duration_seconds=3600,delivery_record=r['delivery_record'],exports=r['one_hour_exports'],
 user_join_approved=False,user_rain_mix_approved=False,assistant_listening=False)
dump(p,m)
p=package/'music/README.md';s=p.read_text(encoding='utf-8');end=s.index('## Scene-specific listening check')
s='''# 08 soundtrack — Rainline Relay

Status: 2026-10-10 — user selected the final **Above the Flooded Canopy** seven-minute piece, requested one hour, and supplied a separate 30-second rain recording. Both a music-only hour and an intermittent-rain hour are delivered. Every decoded sample was checked; both are exactly 3,600 seconds with no clipping. New join/mix and extended listening remain pending; no assistant listening or independent vocal-absence claim.

See [delivery and listening notes](long-source-v1/README.md) and [exact recipe/checks](long-source-v1/one-hour-delivery-v1.json). The supplied source and earlier selected short test are preserved. No new generation credits, commit or push.

The Colony tool at `C:/dev/SpeedySlideShow/dist/Colony.exe` now supports optional continuous/intermittent SFX, gain, start delay, rain duration, gap, fades, loop crossfade and a separate mix preview. Use the **music-only** hour plus rain in its SFX field when changing the mix. Alternatively use the premixed rain hour with SFX removed to avoid adding rain twice. Settings are stored in the export manifest but do not persist in the UI between launches.

## Source and review

1. Selected short test: Flooded Forest Radio Room, preserved in selected-test-v1/.
2. Selected long source: Above the Flooded Canopy, preserved in long-source-v1/. Exact generation settings remain unobserved; seven-minute decoded audio verified.
3. Candidate loop uses source 0:20–6:48, twelve-second equal-power overlaps and fixed -6 dB gain. Only the full hour has a ten-second opening and twenty-second closing fade. The user directly requested the hour; the new join is not yet approved.
4. Rain mix starts after twenty seconds: two minutes on (including fades), ninety seconds off, twenty-second fade-in and thirty-second fade-out. Rain gain is -4 dB relative to the supplied rain, with a two-second source-loop crossfade.
5. Review the sixty-second music join (join at 0:24–0:36) and the 4:20 rain preview (first gap 2:20–3:50). All current exports and source hashes are in the delivery record.
6. Long exports are local under exports/. Animation v5 review, 4K and final video assembly remain separate pending steps.

'''+s[end:]
s=s.replace('proposed next long brief:', 'long-generation brief:').replace('A short test has now been supplied and selected; the exact generation prompt/settings were not observed.', 'Both short and long sources have now been supplied; exact generation prompt/settings were not observed.')
p.write_text(s,encoding='utf-8')
p=package/'README.md';s=p.read_text(encoding='utf-8').replace('User motion review pending; no soundtrack or 4K delivery yet.', 'User motion review and 4K delivery remain pending. One-hour music-only and rain soundtracks are now delivered; their join/mix listening review remains pending.')
start=s.index('Music:');end=s.index('\n\n',start)
s=s[:start]+'''Music: [current soundtrack and listening notes](music/README.md). User selected Above the Flooded Canopy and requested one hour on 2026-10-10. Music-only and intermittent-rain MP3s are delivered with complete decode checks and short review files; see [delivery](music/long-source-v1/README.md). No assistant generation or credit spending. New join/mix, full-hour listening and combined video remain pending.'''+s[end:]
p.write_text(s,encoding='utf-8')
p=root/'PRODUCTION_PIPELINE.md';s=p.read_text(encoding='utf-8').replace('Last updated: 2026-10-08.', 'Last updated: 2026-10-10.',1)
s=s.replace('Flooded Forest Radio Room short test selected; proposed seven-minute brief ready | Review v5 lamp timing and glass rain before 4K; long music generation pending', 'One-hour Above the Flooded Canopy music-only and intermittent-rain versions delivered; full decode passed; join/mix review pending | Review music join/rain mix and v5 motion; 4K and final assembly pending')
p.write_text(s,encoding='utf-8')
p=root/'AGENTS.md';s=p.read_text(encoding='utf-8');start=s.index('Current Rainline music (');end=s.index('\n\n',start)
s=s[:start]+'''Current Rainline music (2026-10-10): user selected final Above_the_Flooded_Canopy_2026-10-10T120411.mp4, requested one hour and customizable intermittent rain, then supplied Gentle_continuous_ra_#2-1791634292024.mp3. Source audio is 420.0107 seconds, rain 30 seconds; originals preserved. Music-only and rain MP3 hours delivered in exports/08-rainline-relay/; exact recipe and checks in final/08-rainline-relay/music/long-source-v1/one-hour-delivery-v1.json. Candidate source 0:20–6:48, twelve-second equal-power overlaps, 376-second repeat interval, fixed -6 dB gain, ten/twenty-second opening/closing fades. Both decode to exactly 3600 seconds with finite samples/no clipping; dry -20.5 LUFS/-9.6 dBTP, rain mix -20.7 LUFS/-6.6 dBTP. Rain -4 dB, starts at 20 seconds, 120 seconds on including 20/30-second fades, 90 seconds off; source-loop overlap two seconds. Sixty-second join and 260-second rain mix review delivered. User requested extension; new join, rain balance and full-hour listening are not approved. Assistant has not listened or independently checked vocals. Colony tool C:/dev/SpeedySlideShow now has optional SFX controls, mix preview and manifest settings; 43 existing and 11 new real-audio tests passed, rebuilt usual dist/Colony.exe startup smoke passed and old executable preserved. Use dry hour plus SFX or premixed hour alone to avoid double rain. Tool source changes are in that separate repository, uncommitted. V5 motion, 4K and video assembly remain pending. No new credits, commit, push or remote media backup.'''+s[end:]
p.write_text(s,encoding='utf-8')
(folder/'README.md').write_text('''# Rainline Relay — one-hour audio v1

Created 2026-10-10 at the user's request. Both MP3s are stereo 48 kHz/192 kb/s, exactly one hour. Originals remain unchanged. The new crossfade and rain mix await listening review.

- [Music-only hour](../../../../exports/08-rainline-relay/Rainline-Relay-Above-the-Flooded-Canopy-1-Hour-v1.mp3): -20.5 LUFS, -9.6 dBTP.
- [Hour with rain](../../../../exports/08-rainline-relay/Rainline-Relay-1-Hour-with-Rain-v1.mp3): -20.7 LUFS, -6.6 dBTP.
- [Music join, sixty seconds](Rainline-music-join-review-60s-v1.mp3): overlap at 0:24–0:36.
- [Rain preview, 4:20](Rainline-rain-mix-preview-v1.mp3): enters 0:20–0:40, fades away 1:50–2:20, silent 2:20–3:50, returns 3:50–4:10.

Rain recipe: source -4 dB, starts after 20 seconds, two minutes on including twenty/thirty-second fades, ninety seconds off, two-second equal-power source-loop overlap. These are initial creative settings, not user-approved balance. Source 30-second MP3 is preserved in music/shared-rain-overlay/. Prepared 28-second float WAV is alongside this record.

The music excerpt is source 0:20–6:48, twelve-second equal-power joins, fixed -6 dB gain, with one ten-second opening and twenty-second closing fade. All four files fully decoded to exact expected sample counts, all samples finite and no clipping. Technical checks do not establish harmonic compatibility, vocal absence or listening comfort. See one-hour-delivery-v1.json for hashes and all timings.

Colony's updated executable is C:/dev/SpeedySlideShow/dist/Colony.exe; previous build is preserved as dist/Colony-before-rain-2026-10-10.exe. Use the music-only hour with its optional SFX controls to change the rain. Use the premixed hour with no additional SFX for this exact mix. Preview mix is independent of video preview. No completed Rainline video or new animation is produced in this audio session.

Reproduction script: make_rainline_hour.py (uses the installed Colony SFX module). Preserve existing outputs and choose new version names before rerunning. Media are local, not backed up by Git; no commit or push performed.
''',encoding='utf-8')
app=Path('C:/dev/SpeedySlideShow')
stage=Path(__file__).parent
for name in ('sfx.py',):shutil.copy2(app/'colony'/name,stage/name)
exe=app/'dist/Colony.exe'
build=dict(date='2026-10-10',app=str(exe),sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),
 previous_executable=str(app/'dist/Colony-before-rain-2026-10-10.exe'),
 regression_tests='43 passed',sfx_tests='11 passed; real FFmpeg audio + integration',
 gui_smoke='Tk constructed; packaged executable survived ten seconds, responded, then closed normally',
 manual_visual_review=False,commit_push=False,
 source_hashes={str(p.relative_to(app)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
   [app/'colony/render.py',app/'colony/sfx.py',app/'colony/gui.py',app/'tests/test_colony_sfx.py']})
dump(stage/'tool-delivery-v1.json',build)
cache=stage/'source-decoded.npy'
if cache.is_file():cache.unlink()
print('Updated Rainline records, live tracker and tool delivery evidence')
