"""Preserve the new three-minute B track and make reversible join auditions."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,sys,json,re,hashlib,shutil
sys.path.insert(0,r'C:\AI\ComfyUI\venv\Lib\site-packages')
import numpy as np
H=Path(__file__).resolve().parent
user=Path(r'C:\Users\jazzs\Downloads\Illuminated_Stillness_2026-10-25T233322 (1).mp4')
bsource=H/'source-original.mp4'
asource=H.parent/'illuminated-horizon-slow-middle-v1'/'source-original.mp4'
assert not bsource.exists(),'Keep previous candidate intact'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copyfile(user,bsource);assert digest(user)==digest(bsource)
rate=48000
def run(args,**kwargs):return subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True,**kwargs)
def decode(path,start=None,length=None):
    args=['ffmpeg','-v','error']
    if start is not None:args+=['-ss',str(start)]
    args+=['-i',str(path)]
    if length is not None:args+=['-t',str(length)]
    args+=['-vn','-ac','2','-ar',str(rate),'-f','f32le','pipe:1']
    return np.frombuffer(run(args).stdout,dtype='<f4').reshape(-1,2).copy()
def loudness(path,start,length):
    p=run(['ffmpeg','-hide_banner','-nostats','-ss',str(start),'-i',str(path),'-t',str(length),'-vn','-af','loudnorm=I=-20:TP=-2:LRA=11:print_format=json','-f','null','-'])
    log=p.stderr.decode(errors='replace');data=json.loads(re.findall(r'\{[^{}]*"input_i"[^{}]*\}',log,re.S)[-1])
    return {'window_seconds':[start,start+length],'integrated_lufs':float(data['input_i']),'true_peak_dbtp':float(data['input_tp']),'lra':float(data['input_lra'])}
def recurrence(x):
    x=x[::3].mean(axis=1).astype(float)
    w=np.lib.stride_tricks.sliding_window_view(x,640)[::160]
    e=np.sqrt(np.mean(w*w,axis=1)+1e-20)
    z=e-np.convolve(np.pad(e,(100,100),mode='edge'),np.ones(201)/201,'valid');z-=z.mean()
    n=len(z);q=1<<(2*n-1).bit_length();a=np.fft.irfft(abs(np.fft.rfft(z,q))**2,q)[:n]/np.arange(n,0,-1);a/=max(a[0],1e-20)
    peaks=sorted([i for i in range(25,151) if a[i]>a[i-1] and a[i]>=a[i+1]],key=lambda i:a[i],reverse=True)[:3]
    return {'strongest_lags':[{'seconds':i/100,'correlation':round(float(a[i]),4)} for i in peaks],'original_075s_lag_correlation':round(float(a[75]),4),'original_150s_lag_correlation':round(float(a[150]),4)}
with ThreadPoolExecutor(max_workers=2) as pool:
    fa=pool.submit(loudness,asource,60,120);fb=pool.submit(loudness,bsource,15,150)
    tail=decode(asource,480,30);head=decode(asource,0,30);b=decode(bsource)
    la=fa.result();lb=fb.result()
assert len(tail)==len(head)==30*rate and len(b)==180*rate
patterns=[{'start_seconds':s,'duration_seconds':24,**recurrence(b[s*rate:(s+24)*rate])} for s in [5,78,149]]
ga=10**((-20-la['integrated_lufs'])/20);gb=10**((-20-lb['integrated_lufs'])/20)
tail*=ga;head*=ga;b*=gb
overlap=8*rate
def join(a,b):
    t=np.linspace(0,np.pi/2,overlap)
    return np.concatenate([a[:-overlap],a[-overlap:]*np.cos(t)[:,None]+b[:overlap]*np.sin(t)[:,None],b[overlap:]])
mix=join(join(tail,b),head)
assert len(mix)==224*rate and np.isfinite(mix).all()
headroom=min(1.0,0.85/max(float(np.max(abs(mix))),1e-12));mix*=headroom
outputs=[]
for name,start,end in [('Horizon-to-Stillness-entry-review-45s.mp3',7,52),('Stillness-to-Horizon-return-review-45s.mp3',179,224),('Horizon-Stillness-Horizon-full-companion-review-3m44s.mp3',0,224)]:
    path=H/name;assert not path.exists()
    pcm=mix[start*rate:end*rate].astype('<f4')
    run(['ffmpeg','-v','error','-n','-f','f32le','-ar',str(rate),'-ac','2','-i','pipe:0','-c:a','libmp3lame','-b:a','320k',str(path)],input=pcm.tobytes())
    check=decode(path)
    assert len(check)==(end-start)*rate and np.isfinite(check).all() and np.max(abs(check))<1
    outputs.append({'path':name,'duration_seconds':end-start,'sha256':digest(path),'decoded_sample_frames':len(check),'decoded_peak_dbfs':float(20*np.log10(max(float(np.max(abs(check))),1e-12))),'full_review_interval_seconds':[start,end]})
manifest={'date':'2026-10-25','source_user_path':str(user),'source_copy':bsource.name,'source_sha256':digest(bsource),'source_audio_seconds':180,'source_video_container_seconds':184.4,'original_horizon':str(asource),'original_sha256':digest(asource),'user_status':'New three-minute upload supplied without text. Prior thirty-second Stillness had potential. No approval of this long generation or its joins is inferred.','measured_body_loudness':{'horizon':la,'stillness':lb},'fixed_gain_db':{'horizon':-20-la['integrated_lufs'],'stillness':-20-lb['integrated_lufs'],'shared_headroom':20*np.log10(headroom)},'processing':'One fixed gain per track based on measured interior loudness, common headroom if needed, eight-second equal-power crossfades. No time stretching, pitch shift, EQ, separation or dynamic loudness processing. Existing source fades retained.','stillness_recurrence_windows':patterns,'analysis_limits':'Envelope recurrence is not an instrument or beat detector. Assistant signal checks do not establish audible contrast, harmonic compatibility, smooth joins or artistic acceptance. No assistant listening claimed.','full_review_timeline':[{'seconds':[0,22],'audio':'Horizon 8:00–8:22'},{'seconds':[22,30],'audio':'Horizon tail → Stillness 0:00–0:08 overlap'},{'seconds':[30,194],'audio':'Stillness 0:08–2:52'},{'seconds':[194,202],'audio':'Stillness 2:52–3:00 → Horizon 0:00–0:08 overlap'},{'seconds':[202,224],'audio':'Horizon 0:08–0:30'}],'short_review_timing':'Each forty-five-second excerpt has fifteen seconds before the transition, an eight-second overlap, then twenty-two seconds after. No extra edge fades.','outputs':outputs,'scope':'Local listening reviews only. Sources preserved. No credit spend, music generation, full-hour assembly, video render, commit or push.'}
(H/'delivery-review.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'audio_seconds':180,'body_loudness':manifest['measured_body_loudness'],'fixed_gain_db':manifest['fixed_gain_db'],'recurrence_windows':patterns,'reviews':outputs},indent=2))
