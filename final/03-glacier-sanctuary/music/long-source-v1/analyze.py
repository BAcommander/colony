from pathlib import Path
import subprocess,json,numpy as np
R=Path(__file__).resolve().parent
FF=r'C:\Program Files\ShareX\ffmpeg.exe'
SRC=r'C:\Users\jazzs\Downloads\Amber_Arch_Sanctuary_2026-09-27T160221.mp4'
sr=12000
raw=subprocess.run([FF,'-v','error','-i',SRC,'-vn','-ar',str(sr),'-ac','2','-f','f32le','pipe:1'],capture_output=True,check=True).stdout
a=np.frombuffer(raw,np.float32).reshape(-1,2)
n=len(a)//sr
blocks=a[:n*sr].reshape(n,sr,2)
rms=20*np.log10(np.maximum(np.sqrt(np.mean(blocks**2,axis=(1,2))),1e-10))
power=np.mean(abs(np.fft.rfft(blocks*np.hanning(sr)[None,:,None],axis=1))**2,axis=2)
freq=np.fft.rfftfreq(sr,1/sr)
edges=[30,80,160,320,640,1280,2560,5000]
bands=np.stack([power[:,(freq>=lo)&(freq<hi)].sum(axis=1) for lo,hi in zip(edges[:-1],edges[1:])],axis=1)
features=10*np.log10(np.maximum(bands/bands.sum(axis=1,keepdims=True),1e-10))
candidates=[]
for start in range(15,61):
 for end in range(550,min(n-3,598)):
  level=abs(float(rms[start:start+15].mean()-rms[end-15:end].mean()))
  spectrum=float(np.sqrt(np.mean((features[start:start+15].mean(axis=0)-features[end-15:end].mean(axis=0))**2)))
  if min(rms[start:start+15].mean(),rms[end-15:end].mean())<np.median(rms)-5:continue
  candidates.append((spectrum+level,start,end,level,spectrum))
candidates.sort()
report={'decoded_seconds':len(a)/sr,'sample_peak_dbfs':float(20*np.log10(abs(a).max())), 'minute_rms_dbfs':[round(float(20*np.log10(np.sqrt(np.mean(a[i*sr:min((i+60)*sr,len(a))]**2)))),2) for i in range(0,n,60)],'first_20_seconds_rms':rms[:20].round(2).tolist(),'last_20_seconds_rms':rms[-20:].round(2).tolist(),'join_candidates':candidates[:12],'limitation':'Spectral and level matching only; no assistant listening or harmonic compatibility confirmation.'}
(R/'analysis.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
