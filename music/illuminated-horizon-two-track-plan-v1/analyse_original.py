"""Locate signal-based transition candidates in the unchanged original master."""
from pathlib import Path
import subprocess,json,sys,hashlib
sys.path.insert(0,r'C:\AI\ComfyUI\venv\Lib\site-packages')
import numpy as np
H=Path(__file__).resolve().parent
source=H.parent/'illuminated-horizon-slow-middle-v1'/'source-original.mp4'
rate=16000
raw=subprocess.run(['ffmpeg','-v','error','-i',str(source),'-vn','-ac','1','-ar',str(rate),'-f','f32le','pipe:1'],stdout=subprocess.PIPE,check=True).stdout
x=np.frombuffer(raw,dtype='<f4')
def db(v):return float(20*np.log10(max(float(v),1e-12)))
def rms(v):return float(np.sqrt(np.mean(v.astype(float)**2)))
# Four-second overlapping averages locate quieter passages, not musical phrase boundaries.
candidates=[]
for start in np.arange(15,len(x)/rate-19,1):
    center=rms(x[int(start*rate):int((start+4)*rate)])
    neighbourhood=rms(x[int((start-12)*rate):int((start+16)*rate)])
    candidates.append({'start_seconds':float(start),'four_second_rms_dbfs':db(center),'relative_to_28s_neighbourhood_db':db(center/max(neighbourhood,1e-12))})
chosen=[]
for row in sorted(candidates,key=lambda r:r['relative_to_28s_neighbourhood_db']):
    if all(abs(row['start_seconds']-v['start_seconds'])>=24 for v in chosen):chosen.append(row)
    if len(chosen)==6:break
def recurrence(start,duration):
    y=x[int(start*rate):int((start+duration)*rate)]
    # Short-window RMS autocorrelation; does not identify beat, meter or an instrument.
    frames=np.lib.stride_tricks.sliding_window_view(y,640)[::160]
    e=np.sqrt(np.mean(frames.astype(float)**2,axis=1)+1e-20)
    slow=np.convolve(np.pad(e,(100,100),mode='edge'),np.ones(201)/201,'valid')
    z=e-slow;z-=z.mean();n=len(z);q=1<<(2*n-1).bit_length()
    a=np.fft.irfft(abs(np.fft.rfft(z,q))**2,q)[:n]/np.arange(n,0,-1)
    a/=max(a[0],1e-20)
    peaks=sorted([i for i in range(25,151) if a[i]>a[i-1] and a[i]>=a[i+1]],key=lambda i:a[i],reverse=True)[:3]
    return {'start':start,'duration':duration,'rms_dbfs':db(rms(y)),'recurrence':[{'lag_seconds':i/100,'correlation':float(a[i])} for i in peaks]}
report={'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'decoded_audio_seconds':len(x)/rate,'source_unchanged':True,'recurrence_windows':[recurrence(15,45),recurrence(225,45),recurrence(435,45)],'local_energy_candidate_windows':sorted(chosen,key=lambda r:r['start_seconds']),'last_ten_seconds_rms_dbfs':db(rms(x[-10*rate:])),'last_one_second_rms_dbfs':db(rms(x[-rate:])),'interpretation_limits':'Signal review only. Low-energy windows are audition candidates, not verified phrase/harmonic boundaries. No reliable key or precise musical BPM claimed. A second track has not been supplied, so compatible harmony, overlap and smoothness cannot yet be verified. No source processing or generation performed.'}
(H/'original-transition-analysis.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
