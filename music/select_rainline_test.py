from pathlib import Path
import json,hashlib,subprocess,array,math
R=Path('G:/AI/colony');P=R/'final/08-rainline-relay';M=P/'music';D=M/'selected-test-v1'
src=Path('C:/Users/jazzs/Downloads/Flooded_Forest_Radio_Room_2026-10-10T115135.mp4')
D.mkdir(exist_ok=True);dst=D/src.name
raw=src.read_bytes();sha=hashlib.sha256(raw).hexdigest()
if dst.exists():assert dst.read_bytes()==raw
else:dst.write_bytes(raw)
p=subprocess.run(['C:/Program Files/ShareX/ffmpeg.exe','-v','error','-i',str(src),'-map','0:a:0','-f','f32le','-acodec','pcm_f32le','pipe:1'],capture_output=True,check=True)
audio=array.array('f',p.stdout);assert len(audio)%2==0 and all(math.isfinite(x) for x in audio)
seconds=len(audio)/2/48000
selection={'date':'2026-10-10','title':'Flooded Forest Radio Room','original_path':str(src),'preserved_path':dst.relative_to(R).as_posix(),'sha256':sha,'bytes':len(raw),'container_duration_seconds':64.4,'decoded_audio_seconds':seconds,'sample_rate_hz':48000,'channels':2,'full_audio_decode_passed':True,'all_decoded_samples_finite':True,'user_feedback':'i like this one','selected_short_test':True,'approval_scope':'User likes this supplied short test; selection for longer music development. No long-track, join or complete-video approval.','exact_generation_settings_observed':None,'assistant_listening':False,'vocals_independently_checked':False,'rain_discussion':'User asked whether rain could be added. Assistant recommends a separate quiet SFX layer; no rain generated or mixed and no decision to include it is inferred.'}
def save(path,data):path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
save(D/'selection.json',selection)
prompt='''Instrumental only, about seven minutes. Use the attached reference for palette, tonal balance, harmonic character and spaciousness; compose a new piece with the same intimate feel.

Warm, beatless synth ambient with softly chorused analog pads and medium-length reverb. Mood: sheltered and quietly attentive in a radio room above a flooded alien forest.

Start with the warm foundation and a gentle midrange phrase already present. During 1:00-2:30, introduce a second independent voice answering across long gaps. Between 2:30 and 4:30, let the chords open into a slightly brighter voicing, with a few varied two- or three-note replies. After 4:30, bring back the close warmth; vary the phrases, rests and voicings gradually through the remaining minutes without building intensity.

Rounded attacks, clear midrange at low volume, modest centred bass and smooth upper tones. Keep the level even and the ending open, still gently moving, with no final cadence or fade to silence.

No vocals, drums, percussion, arpeggios, sound effects, glassy attacks, risers or climaxes.
'''
lp=M/'elevenlabs-long-version-v3-seven-minutes.txt';assert not lp.exists();lp.write_text(prompt,encoding='utf-8')
g=json.loads((M/'generation-record.json').read_text());g.update(status='short test selected; longer generation pending',short_test_files=[selection],selected_test=dst.relative_to(R).as_posix(),user_feedback='i like this one',short_test_selected=True,audio_approval=False,approval_scope=selection['approval_scope'],long_prompt=lp.relative_to(R).as_posix(),proposed_source_duration_seconds=420,source_duration_confirmed_by_user=False)
save(M/'generation-record.json',g)
rp=M/'README.md';s=rp.read_text(encoding='utf-8');start=s.index('Status:');end=s.index('\n',start)
s=s[:start]+'Status: 2026-10-10 — user selected **Flooded Forest Radio Room** with "i like this one". Original export preserved under selected-test-v1/; approximately sixty seconds of decoded stereo audio inside a 64.4-second video. Full audio decode passed; assistant has not independently listened or checked vocals. Longer source and final video duration remain undecided/unapproved.\n\nNext brief: [proposed seven-minute version](elevenlabs-long-version-v3-seven-minutes.txt), using the selected short test as reference. Seven minutes is a prepared recommendation, not a confirmed user setting. Earlier five-minute v2 brief remains preserved. User asked about rain; a separate quiet rain layer is recommended for mix control, but none has been generated or added. Generation remains manual.'+s[end:]
s=s.replace('The files currently contain null values because nothing has been generated.','The selected-test filename, hash and user feedback are now recorded; unobserved generation settings remain null.')
s=s.replace('Current: `elevenlabs-prompt-v2.txt` and `elevenlabs-long-version-v2.txt` (2026-09-29),','Current short brief: `elevenlabs-prompt-v2.txt`; proposed next long brief: `elevenlabs-long-version-v3-seven-minutes.txt`. Earlier v2 briefs (2026-09-29) were')
s=s.replace('Neither version has been generated or heard.','A short test has now been supplied and selected; the exact generation prompt/settings were not observed.')
rp.write_text(s,encoding='utf-8')
m=json.loads((P/'manifest.json').read_text());m['music_current']={'status':'Flooded Forest Radio Room short test selected; long source pending','record':'music/generation-record.json','selection':'music/selected-test-v1/selection.json','selected_test':dst.relative_to(R).as_posix(),'source_sha256':sha,'short_test_selected':True,'long_audio_approved':False,'proposed_long_prompt':'music/elevenlabs-long-version-v3-seven-minutes.txt','final_duration_seconds':None};save(P/'manifest.json',m)
rp=P/'README.md';s=rp.read_text(encoding='utf-8');s=s.replace('No audio generated or credits spent here. User runs short tests first, selects one, then a longer piece; local join review follows.','User selected Flooded Forest Radio Room on 2026-10-10. The original short export and feedback are preserved; the [proposed seven-minute brief](music/elevenlabs-long-version-v3-seven-minutes.txt) is ready. No assistant generation or credit spending. Longer music and local join review are pending.');rp.write_text(s,encoding='utf-8')
rp=R/'PRODUCTION_PIPELINE.md';s=rp.read_text(encoding='utf-8');line=next(x for x in s.splitlines() if x.startswith('| 08 |'));s=s.replace(line,line.replace('Short/long prompts ready; no audio','Flooded Forest Radio Room short test selected; proposed seven-minute brief ready').replace('music remains separate','long music generation pending'));rp.write_text(s,encoding='utf-8')
rp=R/'AGENTS.md';s=rp.read_text(encoding='utf-8');anchor='Current Rainline animation (';pos=s.index(anchor)
note='Current Rainline music (2026-10-10): user supplied Flooded_Forest_Radio_Room_2026-10-10T115135.mp4 and said "i like this one". Selected short test preserved byte-for-byte under final/08-rainline-relay/music/selected-test-v1/ with selection.json; approximately sixty seconds of stereo 48 kHz audio inside a 64.4-second container. Full finite audio decode passed; assistant listening and independent vocal absence are not claimed. Proposed seven-minute long brief is elevenlabs-long-version-v3-seven-minutes.txt; seven minutes is a recommendation, not confirmed generation setting. User asked about rain; recommended a separate quiet SFX layer, with no rain generation/mix or inclusion decision inferred. Long source, final duration, join and assembly remain pending. No credits, commit or push for this selection.\n\n'
assert 'Current Rainline music (2026-10-10)' not in s;rp.write_text(s[:pos]+note+s[pos:],encoding='utf-8')
print('Rainline short test preserved and selected; proposed seven-minute prompt saved. Decoded audio seconds:',seconds)
