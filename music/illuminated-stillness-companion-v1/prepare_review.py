"""Preserve the candidate, measure signals, and audition both track handovers."""
from pathlib import Path
import sys,json,subprocess,hashlib,shutil
sys.path.insert(0,r'C:\AI\ComfyUI\venv\Lib\site-packages')
import numpy as np
H=Path(__file__).resolve().parent
supplied=Path(r'C:\Users\jazzs\Downloads\Illuminated_Stillness_2026-10-25T232654.mp4')
source=H/'source-original.mp4'
original=H.parent/'illuminated-horizon-slow-middle-v1'/'source-original.mp4'
review=H/'Horizon-Stillness-Horizon-transition-audition-54s.mp3'
assert not source.exists() and not review.exists(),'Keep earlier candidate files'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copyfile(supplied,source);assert digest(source)==digest(supplied)
def decode(path,start=None,duration=None):
    cmd=['ffmpeg','-v','error']
    if start is not None:cmd+=['-ss',str(start)]
    cmd+=['-i',str(path)]
    if duration is not None:cmd+=['-t',str(duration)]
    cmd+=['-vn','-ac','2','-ar','48000','-f','f32le','pipe:1']
    return np.frombuffer(subprocess.run(cmd,stdout=subprocess.PIPE,check=True).stdout,dtype='<f4').reshape(-1,2).copy()
def rms(x):return float(np.sqrt(np.mean(x.astype(float)**2)))
def db(v):return float(20*np.log10(max(v,1e-12)))
def recurrence(x):
    mono=x[::3].mean(axis=1).astype(float)
    frames=np.lib.stride_tricks.sliding_window_view(mono,640)[::160]
    e=np.sqrt(np.mean(frames**2,axis=1)+1e-20)
    z=e-np.convolve(np.pad(e,(100,100),mode='edge'),np.ones(201)/201,'valid');z-=z.mean()
    n=len(z);q=1<<(2*n-1).bit_length()
    a=np.fft.irfft(abs(np.fft.rfft(z,q))**2,q)[:n]/np.arange(n,0,-1);a/=max(a[0],1e-20)
    peaks=sorted([i for i in range(25,151) if a[i]>a[i-1] and a[i]>=a[i+1]],key=lambda i:a[i],reverse=True)[:3]
    return [{'lag_seconds':i/100,'correlation':round(float(a[i]),4)} for i in peaks]
b=decode(source);assert len(b)==30*48000
tail=decode(original,490,20);head=decode(original,0,20);a_control=decode(original,225,24)
assert len(tail)==len(head)==20*48000
g_a=10**(-21/20)/rms(a_control);g_b=10**(-21/20)/rms(b[5*48000:25*48000])
tail*=g_a;head*=g_a;b*=g_b
overlap=8*48000
def join(a,b):
    phase=np.linspace(0,np.pi/2,overlap,endpoint=True)
    blend=a[-overlap:]*np.cos(phase)[:,None]+b[:overlap]*np.sin(phase)[:,None]
    return np.concatenate([a[:-overlap],blend,b[overlap:]])
mix=join(join(tail,b),head)
assert len(mix)==54*48000 and np.isfinite(mix).all()
peak=float(np.max(np.abs(mix)));common_gain=min(1.0,0.85/max(peak,1e-12));mix*=common_gain
proc=subprocess.run(['ffmpeg','-v','error','-n','-f','f32le','-ar','48000','-ac','2','-i','pipe:0','-c:a','libmp3lame','-b:a','320k',str(review)],input=mix.astype('<f4').tobytes(),check=True)
decoded=decode(review);assert len(decoded)==54*48000 and np.isfinite(decoded).all() and np.max(abs(decoded))<1
report={'source_user_path':str(supplied),'source_preserved_copy':source.name,'source_sha256':digest(source),'original_sha256':digest(original),'audio_seconds':30,'container_seconds':34.4,'user_feedback':'this has potential','artistic_status':'Promising B candidate, not final music or transition approval','candidate_interior_recurrence':recurrence(b[5*48000:29*48000]),'original_middle_recurrence':recurrence(a_control),'limits':'Envelope repetition does not identify instruments or establish perceptual beatlessness. Assistant has not listened. Harmonic fit/transition quality are for user audition.','audition':{'path':review.name,'sha256':digest(review),'seconds':54,'decoded_samples_per_channel':len(decoded),'decoded_peak_dbfs':db(float(np.max(abs(decoded)))),'fixed_a_gain_db':db(g_a),'fixed_b_gain_db':db(g_b),'shared_headroom_gain_db':db(common_gain),'matching':'Both bodies matched by one fixed RMS gain each to -21 dBFS; not perceptual loudness certification. No stretching, pitch shifting, EQ or separation.','timeline':[{'seconds':[0,12],'audio':'Original Horizon 8:10–8:22'},{'seconds':[12,20],'audio':'8-second equal-power Horizon tail → Stillness start'},{'seconds':[20,34],'audio':'Stillness 0:08–0:22'},{'seconds':[34,42],'audio':'8-second equal-power Stillness ending → Horizon opening'},{'seconds':[42,54],'audio':'Horizon 0:08–0:20'}]},'generation':'No paid generation or long extension submitted. No commit/push requested.'}
(H/'candidate-and-transition-review.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
