from pathlib import Path
import numpy as np, subprocess, json
R=Path(__file__).resolve().parent
FF=r'C:\Program Files\ShareX\ffmpeg.exe'
SRC=r'C:\Users\jazzs\Downloads\YTDown.com_YouTube_Media_KO0k7at4qCs_DEAD-WATER-Deep-Ambient-Music-Underground-Waterfall-Ambience_009_128k.mp3'
sr=8192
p=subprocess.Popen([FF,'-v','error','-i',SRC,'-ar',str(sr),'-ac','2','-f','f32le','pipe:1'],stdout=subprocess.PIPE)
features=[]; levels=[]; stereo=[]; chromas=[]
freq=np.fft.rfftfreq(sr,1/sr); edges=np.geomspace(20,4000,65)
masks=[(freq>=a)&(freq<b) for a,b in zip(edges[:-1],edges[1:])]
win=np.hanning(sr)
while True:
    raw=p.stdout.read(sr*2*4)
    if len(raw)<sr*2*4: break
    a=np.frombuffer(raw,np.float32).reshape(-1,2); y=a.mean(axis=1)
    power=abs(np.fft.rfft(y*win))**2
    features.append([power[m].sum() for m in masks])
    levels.append([float(np.mean(a*a)),float(np.max(abs(a)))])
    stereo.append([float(np.mean(a[:,0]*a[:,1])),float(np.mean(a[:,0]**2)),float(np.mean(a[:,1]**2)),float(np.mean(((a[:,0]-a[:,1])/2)**2))])
    if len(features)%1800==0: print('Analyzed minutes:',len(features)//60,flush=True)
p.wait()
F=np.array(features); L=np.array(levels); S=np.array(stereo)
np.savez_compressed(R/'features.npz',features=F,levels=L,stereo=S)
X=np.log10(F+1e-12); X=(X-X.mean(0))/(X.std(0)+1e-8)
n=len(X); nfft=2**int(np.ceil(np.log2(2*n)))
z=np.fft.rfft(X,nfft,axis=0); ac=np.fft.irfft(z*z.conj(),nfft,axis=0)[:n].mean(1)/np.arange(n,0,-1)
peaks=[i for i in range(30,n//2-1) if ac[i]>ac[i-1] and ac[i]>ac[i+1]]
peaks=sorted(peaks,key=lambda i:ac[i],reverse=True)[:25]
db=10*np.log10(L[:,0]+1e-15)
report={'seconds':n,'rms_dbfs_percentiles':dict(zip(['min','p5','median','p95','max'],np.percentile(db,[0,5,50,95,100]).tolist())), 'peak_dbfs_resampled':float(20*np.log10(L[:,1].max())), 'stereo_correlation':float(S[:,0].sum()/np.sqrt(S[:,1].sum()*S[:,2].sum())), 'side_to_mid_db':float(10*np.log10(S[:,3].sum()/(L[:,0].sum()-S[:,3].sum()))),'repeat_candidates_seconds_score':[(i,float(ac[i])) for i in peaks], 'band_energy':[(float(edges[i]),float(edges[i+1]),float(v)) for i,v in enumerate(F.sum(0)/F.sum())], 'minute_rms_dbfs': [float(10*np.log10(x.mean()+1e-15)) for x in L[:n//60*60,0].reshape(-1,60)]}
(R/'measurements.json').write_text(json.dumps(report,indent=2)); print(json.dumps({k:v for k,v in report.items() if k not in ['band_energy','minute_rms_dbfs']},indent=2))
