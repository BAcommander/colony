"""Diagnostic tonal/residual/transient views; does not identify real sound sources."""
import argparse
import hashlib
import html
import json
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from scipy import signal, ndimage

RATE = 16000
FFT = 2048
HOP = 512


def split_texture(audio, rate=RATE):
    _, times, z = signal.stft(audio.T, rate, nperseg=FFT, noverlap=FFT-HOP,
                              boundary='zeros', padded=True)
    magnitude = np.sqrt(np.mean(np.abs(z) ** 2, axis=0))
    horizontal = ndimage.median_filter(magnitude, size=(1, 31), mode='reflect')
    vertical = ndimage.median_filter(magnitude, size=(31, 1), mode='reflect')
    h2, p2 = horizontal ** 2, vertical ** 2
    harmonic = h2 / np.maximum(h2 + 4 * p2, 1e-20)
    percussive = p2 / np.maximum(p2 + 4 * h2, 1e-20)
    residual = 1 - harmonic - percussive
    masks = {'sustained': harmonic, 'residual': residual, 'transient': percussive}
    parts = {}
    for name, mask in masks.items():
        _, output = signal.istft(z * mask[None, :, :], rate, nperseg=FFT,
                                 noverlap=FFT-HOP, boundary=True)
        parts[name] = output.T[:len(audio)]
    power = magnitude ** 2
    allocation = {name: float((power * mask).sum() / max(power.sum(), 1e-20)) for name, mask in masks.items()}
    freq = np.fft.rfftfreq(FFT, 1/rate)
    flatness = {}
    for low, high in [(40,160),(160,500),(500,2000),(2000,8000)]:
        band = power[(freq >= low) & (freq < high)]
        values = np.exp(np.mean(np.log(np.maximum(band, 1e-20)), axis=0)) / np.maximum(band.mean(axis=0), 1e-20)
        flatness[f'{low}-{high}Hz'] = np.percentile(values, [5,50,95]).tolist()
    return parts, allocation, flatness


def db(value, factor=10):
    return float(factor * np.log10(max(float(value), 1e-15)))


def stats(audio):
    seconds = len(audio) // RATE
    levels = np.mean(audio[:seconds*RATE].reshape(seconds, RATE, 2).astype(float)**2, axis=(1,2))
    energy = float(np.mean(audio.astype(float)**2))
    left,right=audio[:,0].astype(float),audio[:,1].astype(float)
    denom=np.sqrt(np.dot(left,left)*np.dot(right,right))
    f=np.fft.rfftfreq(FFT,1/RATE)
    _,_,z=signal.stft(audio.T,RATE,nperseg=FFT,noverlap=FFT-HOP,boundary=None)
    p=(np.abs(z)**2).mean(axis=(0,2))
    bands={f'{a}-{b}Hz':float(100*p[(f>=a)&(f<b)].sum()/max(p.sum(),1e-20)) for a,b in [(0,80),(80,250),(250,1000),(1000,4000),(4000,8001)]}
    return {'rms_dbfs':db(energy),'sample_peak_dbfs':db(np.abs(audio).max(),20),
            'one_second_rms_p5_p50_p95_dbfs':[db(v) for v in np.percentile(levels,[5,50,95])],
            'stereo_correlation':float(np.dot(left,right)/denom) if denom>1e-15 else None,
            'spectral_energy_percent':bands},levels


def encode(audio,path):
    result=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-f','f32le','-ar',str(RATE),
                           '-ac','2','-i','pipe:0','-c:a','libmp3lame','-b:a','128k','-n',str(path)],
                          input=audio.astype('<f4').tobytes(),capture_output=True)
    if result.returncode:raise RuntimeError(result.stderr.decode(errors='replace'))


def diagnose(source,out):
    if out.exists() and any(out.iterdir()):raise ValueError('Use a new/empty output directory')
    out.mkdir(parents=True,exist_ok=True)
    raw=subprocess.check_output([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(source),'-map','0:a:0',
                                 '-ar',str(RATE),'-ac','2','-f','f32le','pipe:1'])
    audio=np.frombuffer(raw,'<f4').reshape(-1,2)
    if len(audio)<RATE*45 or not np.isfinite(audio).all():raise ValueError('Need at least 45 seconds of finite decoded audio')
    print('Separating sustained, residual and transient structures...',flush=True)
    parts,allocation,flatness=split_texture(audio)
    reconstructed=sum(parts.values())
    error=float(np.max(np.abs(reconstructed-audio)))
    assert error<2e-6,error
    measurements={};levels={}
    for name,x in [('original',audio),*parts.items()]:measurements[name],levels[name]=stats(x)
    n=len(levels['original'])
    residual_ratio=levels['residual']/np.maximum(levels['original'],1e-15)
    percussive_ratio=levels['transient']/np.maximum(levels['original'],1e-15)
    starts=range(10,n-35)
    residual_start=max(starts,key=lambda i:residual_ratio[i:i+30].mean())
    transient_start=max(starts,key=lambda i:percussive_ratio[i:i+30].max())
    steady_start=min(starts,key=lambda i:np.std(10*np.log10(np.maximum(levels['residual'][i:i+30],1e-15))))
    candidates=[('residual-focus',residual_start),('transient-focus',transient_start),('steady-texture',steady_start)]
    clips=[];cards=[]
    for name,start in candidates:
        end=start+30
        original=audio[start*RATE:end*RATE]
        focus=(parts['residual']+parts['transient'])[start*RATE:end*RATE]
        gain_db=min(12.,db(.8/max(float(np.abs(focus).max()),1e-12),20))
        gain_db=max(0.,gain_db)
        names=[('original',original,0),('tone-reduced-same-gain',focus,0),('tone-reduced-boosted',focus*10**(gain_db/20),gain_db)]
        for mode,x,gain in names:
            filename=f'{name}-{mode}.mp3';encode(x,out/filename)
            clip={'selection':name,'start_seconds_in_recording':start,'duration_seconds':30,'mode':mode,'gain_db':gain,'file':filename}
            clips.append(clip)
        cards.append(f'<section><h2>{html.escape(name)} · recording {start//60}:{start%60:02d}</h2><p>Original → reduced sustained tones at the same gain → inspection aid boosted {gain_db:.1f} dB. These are processed views, not isolated SFX stems.</p>')
        for mode,_,gain in names:
            cards.append(f'<p>{html.escape(mode)}'+(f' (+{gain:.1f} dB)' if gain else '')+f'</p><audio controls preload="none" src="{name}-{mode}.mp3"></audio>')
        cards.append('</section>')
    limits=['No assistant listening or semantic sound-source recognition.','Harmonic/residual/transient separation classifies spectrogram shapes, not music versus effects.','Noise may be synthesized texture, musical reverb, environmental sound or codec artefacts. Musical material can leak into every output.','Do not infer a percentage of actual non-musical sound from these masks or the extracted waveform levels.','Boosted listening aids are intentionally louder; only the same-gain pair preserves the original comparison level.','16 kHz analysis limits bandwidth to 8 kHz. Windows identify candidate inspection regions, not verified events.','This fresh ten-minute live DVR sample cannot establish the content of the whole broadcast or the earlier October recording.']
    report={'source':str(source.resolve()),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'decoded_seconds':len(audio)/RATE,'method':{'sample_rate':RATE,'fft_size':FFT,'hop':HOP,'median_kernels':[31,31],'soft_mask_margin':2,'stereo_mask':'shared across channels','reference':'https://www.audiolabs-erlangen.de/resources/2014-ISMIR-ExtHPSep/'},
            'limitations':limits,'maximum_reconstruction_error':error,'mask_weighted_spectral_allocation_not_sfx_percent':allocation,
            'original_spectral_flatness_p5_p50_p95':flatness,'component_measurements':measurements,'clips':clips}
    (out/'diagnosis.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    page='<!doctype html><html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>WINTER WATCH · texture inspection</title><style>body{background:#101919;color:#ede8dc;font:16px/1.6 system-ui}main{max-width:1000px;margin:auto;padding:28px}h1{font:38px Georgia}p,li{color:#b6c5bf}section{border-top:1px solid #42554a;margin-top:28px;padding-top:15px}audio{width:100%}a{color:#dfbd83}</style><main><p>AMBIENT COLONY / DIAGNOSTIC AUDIO</p><h1>Inspect the texture behind the sustained tones</h1><p>Fresh bounded sample, 2 November 2026. Candidate regions selected by signal measurements, not heard or source-labelled by the assistant.</p><ul>'+''.join('<li>'+html.escape(x)+'</li>' for x in limits)+'</ul>'+''.join(cards)+'<p><a href="diagnosis.json">Exact measurements and method</a></p></main></html>'
    (out/'listen.html').write_text(page,encoding='utf-8',newline='\n')
    print(json.dumps({'decoded_seconds':report['decoded_seconds'],'reconstruction_error':error,'allocation':allocation,'measurements':measurements,'clips':[(x['selection'],x['start_seconds_in_recording']) for x in clips[::3]]},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('source',type=Path);parser.add_argument('output',type=Path);args=parser.parse_args();diagnose(args.source,args.output)
