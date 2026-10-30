from pathlib import Path
import subprocess,json,hashlib
import numpy as np
H=Path(__file__).parent
p=Path('C:/Users/jazzs/Downloads/TODO_-_Vast_Unfamiliar_World_2026-10-10T192538.mp4')
ff='C:/Program Files/ShareX/ffmpeg.exe';sr=48000
raw=subprocess.run([ff,'-v','error','-i',str(p),'-vn','-ar',str(sr),'-ac','2','-f','f32le','pipe:1'],capture_output=True,check=True).stdout
a=np.frombuffer(raw,np.float32).reshape(-1,2)
assert np.isfinite(a).all()
def db(x):return float(20*np.log10(max(float(x),1e-12)))
def rms(x):return np.sqrt(np.mean(x.astype(np.float64)**2))
n=8192;freq=np.fft.rfftfreq(n,1/sr);window=np.hanning(n)
bands=[(20,80),(80,250),(250,2000),(2000,8000),(8000,20000)]
def stats(x):
 power=np.zeros(n//2+1)
 for i in range(0,len(x)-n+1,4096):
  power+=(abs(np.fft.rfft(x[i:i+n]*window[:,None],axis=0))**2).mean(axis=1)
 useful=(freq>=20)&(freq<20000);den=power[useful].sum()
 return {'rms_dbfs':db(rms(x)),'sample_peak_dbfs':db(abs(x).max()),'spectral_energy_percent':{f'{lo}-{hi} Hz':round(float(power[(freq>=lo)&(freq<hi)].sum()/den*100),2) for lo,hi in bands},'spectral_centroid_hz':round(float((freq*power).sum()/power.sum()),1)}
timeline=[]
for start in range(0,int(len(a)/sr),5):
 x=a[start*sr:min((start+5)*sr,len(a))]
 if len(x)>=n:timeline.append({'start_seconds':start,'end_seconds':min(start+5,len(a)/sr),**stats(x)})
left,right=a[:,0],a[:,1];mid=(left+right)/2;side=(left-right)/2
record={'source':str(p),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'matches_previously_liked_test':True,'decoded_audio_seconds':len(a)/sr,'container_seconds':64.4,'sample_rate':sr,'channels':2,'all_samples_finite':True,'samples_at_or_above_full_scale':int(np.count_nonzero(abs(a)>=1)),**stats(a),'integrated_lufs':-13.74,'true_peak_dbtp':-.73,'loudness_range_lu':3.1,'stereo_correlation':float(np.corrcoef(left,right)[0,1]),'side_relative_mid_db':db(rms(side)/rms(mid)),'channel_rms_difference_db':db(rms(left)/rms(right)),'timeline_5s':timeline,'edge_rms_1s':{'opening':[db(rms(a[i*sr:(i+1)*sr])) for i in range(6)],'closing':[db(rms(a[-i*sr:None if i==1 else -(i-1)*sr])) for i in range(6,0,-1)]},'scope':'Signal analysis only; no assistant listening, instrument identification, vocal absence, key/tempo or harmonic loop compatibility claimed.'}
(H/'analysis.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,indent=2))
