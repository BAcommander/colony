from pathlib import Path
import sys,json,hashlib,subprocess,re,shutil
import numpy as np
sys.path.insert(0,'C:/dev/SpeedySlideShow')
from colony import render as R
ROOT=Path('G:/AI/colony');P=ROOT/'final/09-offshore-night-office';M=P/'music';D=M/'long-source-v1'
D.mkdir(exist_ok=True)
src=Path('C:/Users/jazzs/Downloads/Alien_Sea_Viewport_2026-10-10T160442.mp4');dst=D/src.name
sha=hashlib.sha256(src.read_bytes()).hexdigest()
if dst.exists():assert hashlib.sha256(dst.read_bytes()).hexdigest()==sha
else:shutil.copy2(src,dst)
FF=R.get_ffmpeg_path();SR=48000
raw=subprocess.run([FF,'-v','error','-i',str(dst),'-vn','-ar',str(SR),'-ac','2','-f','f32le','pipe:1'],capture_output=True,check=True).stdout
a=np.frombuffer(raw,np.float32).reshape(-1,2);assert np.isfinite(a).all()
info=R.measure_track(FF,str(dst));gain=round(-20.5-info.loudness,1)
# Compare candidate 12-second overlap levels near the beginning/end, outside generated fades.
# Numerical alignment only; these scores do not establish harmonic compatibility.
n=12*SR;candidates=[]
def features(b):
 db=20*np.log10(np.sqrt(np.mean(b*b))+1e-12)
 x=b[::4];frames=np.stack([x[i:i+4096] for i in range(0,len(x)-4096,4096)])
 ps=np.mean(abs(np.fft.rfft(frames*np.hanning(4096)[None,:,None],axis=1))**2,axis=(0,2))
 f=np.fft.rfftfreq(4096,1/12000)
 bands=np.array([ps[(f>=lo)&(f<hi)].sum() for lo,hi in zip([40,150,400,1000,2500],[150,400,1000,2500,6000])])
 shape=10*np.log10(bands/bands.sum()+1e-12)
 return float(db),shape
heads={s:features(a[s*SR:s*SR+n]) for s in range(12,41,2)}
tails={e:features(a[e*SR-n:e*SR]) for e in range(430,455,2)}
for start,(hl,hs) in heads.items():
 for end,(tl,ts) in tails.items():
  level=abs(hl-tl);spectral=float(abs(hs-ts).mean());score=level+.25*spectral+.005*(start+454-end)
  candidates.append((score,start,end,level,spectral))
best=min(candidates);_,start,end,level,spectral=best
phase=np.linspace(0,np.pi/2,n)
blend=a[end*SR-n:end*SR]*np.cos(phase)[:,None]+a[start*SR:start*SR+n]*np.sin(phase)[:,None]
clip=np.concatenate([a[(end-36)*SR:(end-12)*SR],blend,a[(start+12)*SR:(start+36)*SR]]).astype(np.float32)*10**(gain/20)
assert len(clip)==60*SR and np.isfinite(clip).all() and abs(clip).max()<1
out=D/'Shoreless-music-join-review-60s-v1.mp3';assert not out.exists() or '--resume-record' in sys.argv
if not out.exists():subprocess.run([FF,'-n','-v','error','-f','f32le','-ar',str(SR),'-ac','2','-i','pipe:0','-c:a','libmp3lame','-b:a','192k',str(out)],input=clip.tobytes(),check=True)
raw=subprocess.run([FF,'-v','error','-i',str(out),'-ac','2','-ar',str(SR),'-f','f32le','pipe:1'],capture_output=True,check=True).stdout
b=np.frombuffer(raw,np.float32);assert len(b)==60*SR*2 and np.isfinite(b).all() and abs(b).max()<1
record={'date':'2026-10-10','source':dst.relative_to(ROOT).as_posix(),'source_sha256':sha,'decoded_audio_seconds':len(a)/SR,
 'source_integrated_lufs':info.loudness,'full_source_audio_decode_passed':True,'source_start_seconds':start,'source_end_seconds':end,
 'overlap_seconds':12,'repeat_interval_seconds':end-start-12,'curve':'equal-power sine/cosine','gain_db':gain,
 'candidate_level_difference_db':level,'candidate_coarse_spectral_distance_db':spectral,
 'rationale':'Measured level/coarse-spectrum candidate outside generated fades; no harmonic compatibility or listening claim.',
 'audition':out.relative_to(ROOT).as_posix(),'audition_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'audition_seconds':60,
 'audition_join_window_seconds':[24,36],'audition_full_decode_passed':True,'audition_peak_dbfs':float(20*np.log10(abs(b).max())),
 'user_join_approved':False,'assistant_listening':False,'user_feedback':'heres the music','final_duration_seconds':None,
 'approval_scope':'Long source supplied for scene 9; new join audition pending. Final duration, water balance and animation review remain unset.'}
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
save(D/'audition-v1.json',record)
water='Soft ocean swells heard from a sheltered room above the water. Slow, irregular washes and gentle lapping around distant platform supports, with occasional quiet foam fizz. Rounded, lightly muffled, subtle stereo width and restrained peaks. Continuous, seamless loop, no fade. Water only: no music, voices, birds, wind, thunder, machinery or crashing surf.\n'
(M/'water-sfx-prompt-v1.txt').write_text(water,encoding='utf-8')
p=M/'generation-record.json';g=json.loads(p.read_text(encoding='utf-8'));g.update(status='Alien Sea Viewport long source received; transition audition ready for review',long_export=record['source'],long_source_sha256=sha,long_source_decoded_seconds=len(a)/SR,local_join_review=record['audition'],local_join_record='music/long-source-v1/audition-v1.json',local_join_approved=False,water_sfx_prompt='water-sfx-prompt-v1.txt',approval_scope=record['approval_scope']);save(p,g)
p=P/'manifest.json';m=json.loads(p.read_text(encoding='utf-8'));m['music_current'].update(status=g['status'],long_source=record['source'],long_source_sha256=sha,join_record='music/long-source-v1/audition-v1.json',user_join_approved=False,water_sfx_status='Prompt prepared; no water audio supplied');save(p,m)
p=ROOT/'PRODUCTION_PIPELINE.md';s=p.read_text(encoding='utf-8').replace('Open Water / Alien Ocean Vista short test selected; long source pending','Alien Sea Viewport eight-minute source supplied; music join audition ready; water prompt prepared');p.write_text(s,encoding='utf-8')
p=ROOT/'AGENTS.md';s=p.read_text(encoding='utf-8');startpos=s.index('Current Shoreless music (');endpos=s.index('\n\n',startpos)
note='Current Shoreless music (2026-10-10): Open Water / Alien Ocean Vista short test selected. User supplied Alien_Sea_Viewport_2026-10-10T160442.mp4 as longer source; decoded audio is eight minutes despite seven-minute prompt. Original preserved in final/09-offshore-night-office/music/long-source-v1/. Full finite source decode passed. Sixty-second music join audition delivered there; crossfade at 0:24â€“0:36. Exact candidate cut/gain and hashes in audition-v1.json; numerical matching only, no assistant listening or harmonic verdict. User join review pending before a long loop; final duration unset. Water prompt saved as music/water-sfx-prompt-v1.txt: gentle distant platform swells from shelter, no generated/supplied water SFX yet. Animation review/4K/assembly remain pending. No paid generation, commit or push.'
s=s[:startpos]+note+s[endpos:];p.write_text(s,encoding='utf-8')
for p in (P/'README.md',M/'README.md'):
 s=p.read_text(encoding='utf-8');s=s.replace('Longer generation and local join review are next; final duration is not set.', 'Alien Sea Viewport longer source is now preserved; join audition ready in music/long-source-v1/; final duration is not set.')
 s=s.replace('Longer source, final duration and join review remain pending.', 'Eight-minute Alien Sea Viewport source received; sixty-second join audition is ready in long-source-v1/ (crossfade at 0:24â€“0:36). Final duration and join approval remain pending. Water SFX prompt: water-sfx-prompt-v1.txt.')
 p.write_text(s,encoding='utf-8')
print(json.dumps(record,indent=2),flush=True)
