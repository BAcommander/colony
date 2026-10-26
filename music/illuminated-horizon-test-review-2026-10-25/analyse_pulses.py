"""Read-only signal check of the two new musical auditions, not a listening verdict."""
from pathlib import Path
import sys,subprocess,json,hashlib
sys.path.insert(0,r'C:\AI\ComfyUI\venv\Lib\site-packages')
import numpy as np
H=Path(__file__).resolve().parent
sources=[Path(r'C:\Users\jazzs\Downloads\Open_Skyline_2026-10-25T225849.mp4'),Path(r'C:\Users\jazzs\Downloads\Nightfall_Across_Glass_2026-10-25T225849.mp4')]
rate=16000;hop=160;win=640
def autocorr(z):
    z=z-z.mean();n=len(z);q=1<<(2*n-1).bit_length()
    a=np.fft.irfft(abs(np.fft.rfft(z,q))**2,q)[:n]
    a/=np.arange(n,0,-1);return a/max(a[0],1e-20)
def measure(env):
    # Remove changes taking several seconds; retain repeated short envelope motion.
    slow=np.convolve(np.pad(env,(100,100),mode='edge'),np.ones(201)/201,'valid')
    z=env-slow;a=autocorr(z)
    peaks=[i for i in range(25,min(151,len(a)-1)) if a[i]>a[i-1] and a[i]>=a[i+1]]
    peaks=sorted(peaks,key=lambda i:a[i],reverse=True)[:4]
    return {'envelope_cv':float(np.std(env)/max(np.mean(env),1e-12)), 'repeated_envelope_lags':[{'seconds':round(i*hop/rate,3),'correlation':round(float(a[i]),3),'twice_lag_correlation':round(float(a[2*i]),3) if 2*i<len(a) else None} for i in peaks]}
report={'method':'FFT band RMS envelope, 40ms windows/10ms hop; detrended autocorrelation. Recurrence supports rhythmic motion but does not identify an instrument or establish perceived beat. No listening performed.','files':[]}
for source in sources:
    raw=subprocess.run(['ffmpeg','-v','error','-i',str(source),'-vn','-ac','1','-ar',str(rate),'-f','f32le','pipe:1'],stdout=subprocess.PIPE,check=True).stdout
    x=np.frombuffer(raw,dtype='<f4').astype(float)
    frames=np.lib.stride_tricks.sliding_window_view(x,win)[::hop]
    spectrum=abs(np.fft.rfft(frames*np.hanning(win),axis=1))**2
    freq=np.fft.rfftfreq(win,1/rate)
    bands={}
    for name,lo,hi in [('bass',40,200),('middle',200,1200),('upper',1200,6500),('broadband',40,6500)]:
        energy=np.sqrt(spectrum[:,(freq>=lo)&(freq<hi)].sum(axis=1)+1e-20)
        bands[name]={'interior_5_to_29s':measure(energy[500:2900]),'successive_8s': [measure(energy[s*100:(s+8)*100]) for s in (5,13,21)]}
    report['files'].append({'file':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'decoded_audio_seconds':len(x)/rate,'bands':bands})
(H/'pulse-analysis.json').write_text(json.dumps(report,indent=2)+'\n')
for item in report['files']:
    print(Path(item['file']).name)
    for name,values in item['bands'].items():print(name,json.dumps(values['interior_5_to_29s']), 'window strongest:',[v['repeated_envelope_lags'][:1] for v in values['successive_8s']])
