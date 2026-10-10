from pathlib import Path
import json
root=Path('G:/AI/colony'); folder=root/'final/07-icebound-weather-post/music'; out=folder/'long-source-v1'
a=json.loads((out/'analysis.json').read_text(encoding='utf-8')); j=json.loads((out/'audition-v1.json').read_text(encoding='utf-8'))
assert [f['seconds'] for f in j['files']]==[58,977]
p=folder/'generation-record.json'; r=json.loads(p.read_text(encoding='utf-8'))
r.update(status='Seven-minute Winter Colony Night supplied; join and three-repeat auditions delivered; listening pending',
         long_export={'original_path':a['original_path'],'preserved_path':a['source'],'sha256':a['sha256'],'decoded_audio_seconds':a['audio_seconds']},
         local_join_review={'record':'long-source-v1/audition-v1.json','crossfade_audition_seconds':[25,33],'status':'user listening pending'},
         long_prompt_status='Long export supplied 2026-10-04; actual UI settings not observed',
         vocal_free_user_confirmation=False,
         approval_scope='Short-test musical direction liked; longer file supplied without explicit listening verdict. Join, absence of unwanted vocals and full long-form listening not approved.')
p.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
(out/'README.md').write_text('''# Icebound Weather Post — Winter Colony Night auditions

2026-10-04. Original seven-minute export preserved byte-for-byte under exports/07-icebound-weather-post/source/. SHA-256 and decoded duration (420.010667 seconds at analysis rate) are in analysis.json. User supplied the longer file after choosing Colony Winter Night's musical direction and reporting unwanted lyrics in that earlier short test. No assistant listening or vocal-absence claim.

Candidate retains source 1:23–6:54 (331 seconds), using an eight-second equal-power sine/cosine crossfade and fixed -8 dB gain. The first search reached its boundary; the expanded search found this level/coarse-spectrum candidate. Original search records are preserved. These measurements cannot establish harmonic compatibility.

- Short audition: exports/07-icebound-weather-post/Icebound-Weather-Post-Winter-Colony-Night-join-v1.mp3 — 58 seconds; transition at 0:25–0:33.
- Three-repeat preview: exports/07-icebound-weather-post/Icebound-Weather-Post-Winter-Colony-Night-three-repeats-v1.mp3 — 16:17; transitions at 5:23–5:31 and 10:46–10:54.

Both MP3s fully decoded with exact sample counts and finite samples. Measured short/long levels are -20.3/-20.2 LUFS and true peaks -9.0/-8.9 dBFS. No clipping. Short audition uses 0.15/0.3-second edge fades; three-repeat preview uses one 5-second opening and 10-second closing fade. See audition-v1.json and loudness logs.

User listening to the join and checking for unwanted voices remain pending. One-hour delivery is the requested target; it has not been made. Animation status remains separate. Media are local ignored exports, not backed up by Git. No credits, commit or push.

Reproduce with analyze.py then make-auditions-v1.py using the existing Python/NumPy runtime and local FFmpeg. Encoding refuses to overwrite existing exports.
''',encoding='utf-8')
p=folder/'README.md'; s=p.read_text(encoding='utf-8'); start=s.index('Status 2026-10-04:'); end=s.index('\n\n',start)
s=s[:start]+'Status 2026-10-04: longer Winter Colony Night export supplied (seven minutes). A 58-second join audition and 16:17 three-repeat preview are delivered; see [long-source-v1](long-source-v1/README.md). User join review and confirmation of no unwanted voices remain pending before the requested one-hour delivery. Assistant signal analysis only; no listening claim.'+s[end:]; p.write_text(s,encoding='utf-8')
p=root/'PRODUCTION_PIPELINE.md'; s=p.read_text(encoding='utf-8').replace('Colony Winter Night direction selected; vocals unwanted; seven-minute instrumental prompt ready; one-hour target','Seven-minute Winter Colony Night supplied; join and 16:17 auditions ready; one-hour target').replace('await instrumental long export and audition join','review music join at 0:25–0:33 and check for unwanted voices'); p.write_text(s,encoding='utf-8')
p=root/'AGENTS.md'; s=p.read_text(encoding='utf-8'); start=s.index('Current Icebound music ('); end=s.index('\n\n',start)
s=s[:start]+'Current Icebound music (2026-10-04): user supplied seven-minute Winter Colony Night after selecting the Colony Winter Night short-test direction and reporting unwanted lyrics there. Original is preserved under exports/07-icebound-weather-post/source/; analysis and auditions in final/07-icebound-weather-post/music/long-source-v1/. Candidate source 1:23–6:54, eight-second equal-power overlap, fixed -8 dB gain. A 58-second short audition has transition at 0:25–0:33; three-repeat preview lasts 16:17. Full decodes/sample counts/finite checks passed; -20.3/-20.2 LUFS and -9.0/-8.9 dBFS true peaks. User join review and absence-of-vocals confirmation pending. One-hour target requested but not yet produced. Assistant signal analysis only, no listening claim. No credits, commit or push; media local and ignored.'+s[end:]; p.write_text(s,encoding='utf-8')
print('Source, audition evidence and current production status saved.')
