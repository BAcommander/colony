from pathlib import Path
import sys,json,hashlib,shutil,subprocess
import numpy as np
sys.path.insert(0,'C:/dev/SpeedySlideShow')
from colony import render as R
ROOT=Path('G:/AI/colony');H=Path(__file__).parent;M=ROOT/'final/10-nightward-station/music';D=M/'long-a-unfolding-warmth-v1';D.mkdir(exist_ok=True)
src=Path('C:/Users/jazzs/Downloads/Unfolding_Warmth_2026-10-10T193419.mp4');dst=D/src.name
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if dst.exists():assert sha(dst)==sha(src)
else:shutil.copy2(src,dst)
cache=H/'.local';cache.mkdir(exist_ok=True)
if (H/'source-audio.npy').exists():(H/'source-audio.npy').replace(cache/'source-audio.npy')
a=np.load(cache/'source-audio.npy');SR=48000;FF=R.get_ffmpeg_path();n=12*SR
stats=json.loads((H/'source-analysis.json').read_text());gain=round(-20.5-stats['integrated_lufs'],1)
def features(b):
 level=float(20*np.log10(np.sqrt(np.mean(b*b))+1e-12));x=b[::4]
 frames=np.stack([x[i:i+4096] for i in range(0,len(x)-4096,4096)])
 power=np.mean(abs(np.fft.rfft(frames*np.hanning(4096)[None,:,None],axis=1))**2,axis=(0,2));freq=np.fft.rfftfreq(4096,1/12000)
 bands=np.array([power[(freq>=lo)&(freq<hi)].sum() for lo,hi in zip([40,150,400,1000,2500],[150,400,1000,2500,6000])]);return level,10*np.log10(bands/bands.sum()+1e-12)
heads={s:features(a[s*SR:s*SR+n]) for s in range(18,43,2)};tails={e:features(a[e*SR-n:e*SR]) for e in range(270,285,2)}
candidates=[]
for s,(hl,hs) in heads.items():
 for e,(tl,ts) in tails.items():
  level=abs(hl-tl);spectral=float(abs(hs-ts).mean());candidates.append((level+.3*spectral+.005*(s+284-e),s,e,level,spectral))
_,start,end,level,spectral=min(candidates);phase=np.linspace(0,np.pi/2,n)
source=a[start*SR:end*SR];blend=(source[-n:]*np.cos(phase)[:,None]+source[:n]*np.sin(phase)[:,None]).astype(np.float32)
join=np.concatenate([a[(end-36)*SR:(end-12)*SR],blend,a[(start+12)*SR:(start+36)*SR]]).astype(np.float32)
triple=np.concatenate([source[:-n],blend,source[n:-n],blend,source[n:]]).astype(np.float32)
join*=10**(gain/20);triple*=10**(gain/20)
triple[:5*SR]*=np.linspace(0,1,5*SR)[:,None];triple[-8*SR:]*=np.linspace(1,0,8*SR)[:,None]
def render(samples,path):
 assert not path.exists();assert np.isfinite(samples).all() and abs(samples).max()<1
 subprocess.run([FF,'-v','error','-n','-f','f32le','-ar',str(SR),'-ac','2','-i','pipe:0','-c:a','libmp3lame','-b:a','192k',str(path)],input=samples.tobytes(),check=True)
 raw=subprocess.run([FF,'-v','error','-i',str(path),'-ar',str(SR),'-ac','2','-f','f32le','pipe:1'],capture_output=True,check=True).stdout
 decoded=np.frombuffer(raw,np.float32);assert len(decoded)==samples.size and np.isfinite(decoded).all() and abs(decoded).max()<1
 return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'duration_seconds':len(samples)/SR,'full_decode':True,'all_samples_finite':True,'sample_peak_dbfs':float(20*np.log10(abs(decoded).max()))}
short=render(join,D/'Farpoint-Unfolding-Warmth-join-review-60s-v1.mp3')
long=render(triple,D/'Farpoint-Unfolding-Warmth-three-repeats-v1.mp3')
record={'date':'2026-10-10','source':dst.relative_to(ROOT).as_posix(),'source_sha256':sha(dst),'analysis':stats,'source_start_seconds':start,'source_end_seconds':end,'overlap_seconds':12,'repeat_interval_seconds':end-start-12,'curve':'equal-power sine/cosine','gain_db':gain,'candidate_level_difference_db':level,'candidate_coarse_spectral_distance_db':spectral,'candidate_method':'RMS and coarse-spectrum match away from measured opening/closing fades. Numeric candidate only, no harmonic compatibility or assistant listening claim.','auditions':[short,long],'short_join_seconds':[24,36],'triple_join_seconds':[[end-start-12,end-start],[2*(end-start-12),2*(end-start-12)+12]],'triple_boundary_fades_seconds':[5,8],'user_join_approved':False,'long_source_selected_for_final':False,'assistant_listening':False,'final_duration_seconds':None,'feedback':"here's the first version, what do you think can we loop it etc?"}
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
save(D/'audition-v1.json',record)
(D/'README.txt').write_text(f'Farpoint Station — Unfolding Warmth loop candidate\n\nActual source {len(a)/SR:.3f}s; original preserved. Candidate cut {start}s–{end}s, twelve-second equal-power overlap, {gain} dB fixed gain. Sixty-second audition join at 24–36s. Three-repeat review {len(triple)/SR:.0f}s with single five/eight-second opening/closing fades. Full finite decodes and no clipping checked. Numeric matching does not prove a natural musical join; user listening review remains pending. Second longer variation has not arrived. No final long runtime selected; no 4K or final assembly produced here.\n',encoding='utf-8')
p=M/'generation-record.json';g=json.loads(p.read_text(encoding='utf-8'));g.update(status='First longer source Unfolding Warmth received; loop audition ready, second longer source pending',long_export=record['source'],long_source_sha256=record['source_sha256'],long_source_decoded_seconds=len(a)/SR,local_join_review=short['path'],local_join_record='long-a-unfolding-warmth-v1/audition-v1.json',local_join_approved=False,selected_test=None);save(p,g)
p=ROOT/'PRODUCTION_PIPELINE.md';s=p.read_text(encoding='utf-8').replace('Both short music tests liked; paired seven-minute prompts ready, longer audio pending','First longer source Unfolding Warmth (4:59) received; join audition ready; second variant pending');p.write_text(s,encoding='utf-8')
print(json.dumps({'cut_seconds':[start,end],'gain_db':gain,'auditions':[short,long],'triple_join_seconds':record['triple_join_seconds']},indent=2),flush=True)
