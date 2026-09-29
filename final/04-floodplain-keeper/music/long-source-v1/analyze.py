"""Technical join-candidate search; no listening or harmonic-compatibility claim."""
from pathlib import Path
import hashlib,json,subprocess,shutil
import numpy as np
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
FF=r'C:/Program Files/ShareX/ffmpeg.exe'
ORIGINAL=Path('C:/Users/jazzs/Downloads/Shelter_Recovery_2026-09-29T165637.mp4')
SOURCE=ROOT/'exports/04-floodplain-keeper/source'/ORIGINAL.name
SOURCE.parent.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if not SOURCE.exists():shutil.copy2(ORIGINAL,SOURCE)
assert sha(SOURCE)==sha(ORIGINAL)
sr=12000
raw=subprocess.run([FF,'-v','error','-i',str(SOURCE),'-map','0:a:0','-ar',str(sr),'-ac','2','-f','f32le','pipe:1'],capture_output=True,check=True).stdout
x=np.frombuffer(raw,np.float32).reshape(-1,2)
n=len(x)//sr
blocks=x[:n*sr].reshape(n,sr,2)
levels=10*np.log10(np.maximum(np.mean(blocks**2,axis=(1,2)),1e-20))
f=np.fft.rfftfreq(sr,1/sr)
power=np.mean(abs(np.fft.rfft(blocks*np.hanning(sr)[None,:,None],axis=1))**2,axis=2)
edges=[30,80,160,320,640,1280,2560,5000]
bands=np.stack([power[:,(f>=a)&(f<b)].sum(axis=1) for a,b in zip(edges[:-1],edges[1:])],axis=1)
features=10*np.log10(np.maximum(bands/bands.sum(axis=1,keepdims=True),1e-12))
candidates=[]
for overlap in [8,12,16,20]:
 for start in range(10,46):
  for end in range(n-50,n-5):
   left=levels[end-overlap:end];right=levels[start:start+overlap]
   if min(left.mean(),right.mean())<np.median(levels)-4:continue
   level=abs(float(left.mean()-right.mean()))
   spectrum=float(np.sqrt(np.mean((features[end-overlap:end].mean(0)-features[start:start+overlap].mean(0))**2)))
   score=spectrum+level+.005*(start+n-end)
   candidates.append({'score':round(score,4),'start_seconds':start,'end_seconds':end,'overlap_seconds':overlap,'mean_level_difference_db':round(level,3),'spectrum_distance_db':round(spectrum,3)})
candidates.sort(key=lambda a:a['score'])
report={'source':SOURCE.relative_to(ROOT).as_posix(),'original_path':str(ORIGINAL),'sha256':sha(SOURCE),'bytes':SOURCE.stat().st_size,'audio_seconds':len(x)/sr,'container_seconds':424.4,'decoded_analysis_sample_rate':sr,'first_45_seconds_rms_dbfs':levels[:45].round(2).tolist(),'last_50_seconds_rms_dbfs':levels[-50:].round(2).tolist(),'minute_rms_dbfs':[round(float(10*np.log10(np.mean(x[i*sr:min((i+60)*sr,len(x))]**2))),2) for i in range(0,n,60)],'join_candidates':candidates[:20],'best_per_overlap':{str(o):next(c for c in candidates if c['overlap_seconds']==o) for o in [8,12,16,20]},'limits':'Spectrum and level similarity only; positions are not musically aligned by ear. Overlap duration and harmony require user audition. No assistant listening.'}
(OUT/'analysis.json').write_text(json.dumps(report,indent=2)+'\n')
r=subprocess.run([FF,'-hide_banner','-nostats','-i',str(SOURCE),'-vn','-af','ebur128=peak=true:framelog=verbose','-f','null','-'],capture_output=True,check=True)
(OUT/'source-loudness.txt').write_text(r.stderr.decode(errors='replace'))
print(json.dumps(report,indent=2))
