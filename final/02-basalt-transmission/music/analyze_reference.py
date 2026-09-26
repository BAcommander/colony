"""Local, reproducible signal analysis; does not identify instruments by ear."""
import argparse,json,subprocess,hashlib
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('output');p.add_argument('--ffmpeg',default=r'C:\Program Files\ShareX\ffmpeg.exe');a=p.parse_args()
R=Path(a.output);R.mkdir(parents=True,exist_ok=True);sr=8192
proc=subprocess.Popen([a.ffmpeg,'-v','error','-i',a.source,'-ar',str(sr),'-ac','2','-f','f32le','pipe:1'],stdout=subprocess.PIPE)
freq=np.fft.rfftfreq(sr,1/sr);edges=np.geomspace(20,4000,65);masks=[(freq>=lo)&(freq<hi) for lo,hi in zip(edges[:-1],edges[1:])];win=np.hanning(sr)
features=[];levels=[];stereo=[]
while True:
 raw=proc.stdout.read(sr*8)
 if len(raw)<sr*8:break
 x=np.frombuffer(raw,np.float32).reshape(-1,2).astype(float)
 power=(abs(np.fft.rfft(x*win[:,None],axis=0))**2).mean(1)
 features.append([power[m].sum() for m in masks]);levels.append(np.mean(x*x))
 stereo.append([np.mean(x[:,0]*x[:,1]),np.mean(x[:,0]**2),np.mean(x[:,1]**2)])
 if len(features)%3600==0:print('Hours analysed:',len(features)//3600,flush=True)
assert proc.wait()==0
F=np.array(features);L=np.array(levels);S=np.array(stereo);n=len(L)
np.savez_compressed(R/'features.npz',features=F,levels=L,stereo=S)
X=np.log10(F+1e-12);X=(X-X.mean(0))/(X.std(0)+1e-8);nfft=2**int(np.ceil(np.log2(2*n)))
z=np.fft.rfft(X,nfft,axis=0);ac=np.fft.irfft(z*z.conj(),nfft,axis=0)[:n].mean(1)/np.arange(n,0,-1)
peaks=sorted([i for i in range(30,n//2-1) if ac[i]>ac[i-1] and ac[i]>ac[i+1]],key=lambda i:ac[i],reverse=True)[:15]
db=10*np.log10(L+1e-20)
report={'source_name':Path(a.source).name,'source_sha256':hashlib.sha256(Path(a.source).read_bytes()).hexdigest(),'analysed_seconds':n,'rms_dbfs_p5_median_p95':np.percentile(db,[5,50,95]).tolist(),'stereo_correlation':float(S[:,0].sum()/np.sqrt(S[:,1].sum()*S[:,2].sum())),'recurrence_candidates_seconds_score':[(i,float(ac[i])) for i in peaks],'opening_40s_dbfs':np.round(db[:40],1).tolist(),'ending_40s_dbfs':np.round(db[-40:],1).tolist()}
(R/'measurements.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
def audio(t,d,sample_rate=8192):
 r=subprocess.run([a.ffmpeg,'-v','error','-ss',str(t),'-i',a.source,'-t',str(d),'-ar',str(sample_rate),'-ac','2','-f','f32le','pipe:1'],capture_output=True,check=True)
 return np.frombuffer(r.stdout,np.float32).reshape(-1,2)
matches=[]
for lag in peaks[:3]:
 for t in [60,300,900,1800]:
  x=audio(t,20).mean(1);y=audio(t+lag-2,24).mean(1)
  size=2**int(np.ceil(np.log2(len(x)+len(y))))
  cc=np.fft.irfft(np.fft.rfft(y,size)*np.fft.rfft(x,size).conj(),size)[:len(y)-len(x)+1]
  energy=np.r_[0,np.cumsum(y.astype(float)**2)];norm=cc/np.sqrt(np.sum(x.astype(float)**2)*(energy[len(x):]-energy[:-len(x)])+1e-30)
  k=int(np.argmax(norm));matches.append({'start':t,'offset_seconds':lag-2+k/sr,'waveform_correlation':float(norm[k])})
(R/'waveform-matches.json').write_text(json.dumps(matches,indent=2));print('MATCHES',json.dumps(matches),flush=True)
spectra=[]
for t in [60,300,900,1800,3000]:
 x=audio(t,60,22050).astype(float);sz=32768;f=np.fft.rfftfreq(sz,1/22050);ps=[]
 for j in range(0,len(x)-sz,sz//2):ps.append((abs(np.fft.rfft(x[j:j+sz]*np.hanning(sz)[:,None],axis=0))**2).mean(1))
 power=np.mean(ps,0);ix=np.where((power[1:-1]>power[:-2])&(power[1:-1]>power[2:]))[0]+1
 ix=sorted([i for i in ix if 30<f[i]<1500],key=lambda i:power[i],reverse=True)[:10]
 spectra.append({'start':t,'energy_percent':{f'{lo}-{hi}':round(float(100*power[(f>=lo)&(f<hi)].sum()/power.sum()),2) for lo,hi in [(0,80),(80,250),(250,1000),(1000,4000),(4000,11025)]},'prominent_peaks_hz':[round(float(f[i]),2) for i in ix]})
(R/'sampled-spectrum.json').write_text(json.dumps(spectra,indent=2));print('SPECTRA',json.dumps(spectra),flush=True)
q=subprocess.run([a.ffmpeg,'-hide_banner','-nostats','-i',a.source,'-af','ebur128=peak=true:framelog=verbose','-f','null','-'],capture_output=True,check=True)
(R/'loudness.txt').write_bytes(q.stderr);print(q.stderr.decode(errors='replace')[-800:])
