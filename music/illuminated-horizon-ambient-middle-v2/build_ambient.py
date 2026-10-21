"""Reshape a stereo mix into an ambient centre at unchanged source timing.

No time stretch, pitch shift, generation service, downloaded model or stems.
"""
from pathlib import Path
import hashlib
import json
import math
import subprocess
import numpy as np

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent/'illuminated-horizon-slow-middle-v1'/'source-original.mp4'
SR = 48000
NFFT, HOP = 8192, 2048

def run(args, log=None):
    p = subprocess.run([str(v) for v in args],cwd=ROOT,capture_output=True)
    if log: (ROOT/log).write_bytes(p.stdout+p.stderr)
    if p.returncode: raise RuntimeError(p.stderr.decode(errors='replace')[-5000:])
    return p.stdout

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def mean_smooth(x,size):
    size=max(1,int(size))
    if size%2==0: size+=1
    pad=[(0,0)]*x.ndim
    pad[0]=(size//2,size//2)
    padded=np.pad(x,pad,mode='edge')
    cs=np.concatenate([np.zeros_like(padded[:1],dtype=np.float64),
                       np.cumsum(padded,axis=0,dtype=np.float64)],axis=0)
    return ((cs[size:]-cs[:-size])/size).astype(np.float32)

def sustained_layer(x):
    """Keep persistent spectral energy, attenuating short-lived attacks.

    A shared stereo mask retains input phases, timing and channel relation.
    The time median is a DSP estimate, not instrument-level stem separation.
    """
    padded=np.pad(x,((NFFT//2,NFFT//2),(0,0)),mode='reflect')
    frames=np.lib.stride_tricks.sliding_window_view(padded,NFFT,axis=0)[::HOP]
    window=np.hanning(NFFT).astype(np.float32)
    count=len(frames)
    specs=[]
    for ch in range(2):
        specs.append(np.fft.rfft(frames[:,ch,:]*window,axis=-1).astype(np.complex64))
    amp=np.sqrt((np.abs(specs[0])**2+np.abs(specs[1])**2)*.5)
    # Downsample only the analysis envelope, not the audio or its timing.
    small=amp[::4]
    padded_amp=np.pad(small,((5,5),(0,0)),mode='edge')
    views=np.lib.stride_tricks.sliding_window_view(padded_amp,11,axis=0)
    floor=np.quantile(views,.25,axis=-1).astype(np.float32)
    floor=mean_smooth(floor,5)
    positions=np.arange(count,dtype=np.float32)/4
    lo=np.minimum(positions.astype(int),len(floor)-1)
    hi=np.minimum(lo+1,len(floor)-1)
    frac=(positions-lo)[:,None]
    persistent=floor[lo]*(1-frac)+floor[hi]*frac
    ratio=persistent/(amp+1e-7)
    mask=np.clip(ratio,0,1)**1.6
    # Slow spectral gain changes avoid rapidly chattering mask edges.
    mask=mean_smooth(mask,7)
    frequencies=np.fft.rfftfreq(NFFT,1/SR)
    hp=(frequencies/75)**4/(1+(frequencies/75)**4)
    lp=1/np.sqrt(1+(frequencies/6200)**8)
    mask*=hp*lp
    result=np.zeros((len(padded),2),dtype=np.float32)
    weight=np.zeros(len(padded),dtype=np.float32)
    for ch in range(2):
        timeframes=np.fft.irfft(specs[ch]*mask,n=NFFT,axis=-1).astype(np.float32)
        for i,frame in enumerate(timeframes):
            result[i*HOP:i*HOP+NFFT,ch]+=frame*window
    for i in range(count): weight[i*HOP:i*HOP+NFFT]+=window**2
    result/=np.maximum(weight[:,None],1e-8)
    return result[NFFT//2:NFFT//2+len(x)]

def convolution(x,ir):
    block=262144
    size=1<<(block+len(ir)-2).bit_length()
    kernel=np.fft.rfft(ir,n=size)
    out=np.zeros((len(x)+len(ir)-1,2),dtype=np.float32)
    for ch in range(2):
        for pos in range(0,len(x),block):
            a=x[pos:pos+block,ch]
            z=np.fft.irfft(np.fft.rfft(a,n=size)*kernel,n=size)
            length=min(len(a)+len(ir)-1,len(out)-pos)
            out[pos:pos+length,ch]+=z[:length].astype(np.float32)
    return out[:len(x)]

def spectral_bed(x):
    """Additive spectral bed with slow amplitudes and continuous oscillator phases.

    Reconstructs a new sustained texture from the contemporaneous source
    spectrum. Original note attacks/phases are deliberately not reproduced.
    Audio time is not remapped, looped or slowed. The FFT oscillator grid has
    0.732 Hz spacing; this is a texture reconstruction, not an isolated stem.
    """
    size,hop=65536,8192
    pad=np.pad(x,((size//2,size//2),(0,0)),mode='reflect')
    frames=np.lib.stride_tricks.sliding_window_view(pad,size,axis=0)[::hop]
    window=np.hanning(size).astype(np.float32)
    specs=[np.fft.rfft(frames[:,ch,:]*window,axis=-1).astype(np.complex64)
           for ch in range(2)]
    # A continuous shared oscillator grid avoids repeated randomized-frame
    # attacks or the flanging from summing differently stretched copies.
    rng=np.random.default_rng(20261021)
    initial=rng.uniform(-np.pi,np.pi,size//2+1)
    offset=np.angle(np.sum(specs[1]*np.conj(specs[0]),axis=0))
    f=np.fft.rfftfreq(size,1/SR)
    # Collapse neighbouring leakage bins onto persistent spectral peaks.
    # Keeping the full FFT grid as independent oscillators caused artificial
    # beating at the 0.732-Hz grid spacing in the internal diagnostic pass.
    average=np.mean((np.abs(specs[0])+np.abs(specs[1]))*.5,axis=0)
    peaks=np.ones(len(average),dtype=bool)
    for shift in range(1,5):
        peaks[shift:] &= average[shift:] > average[:-shift]
        peaks[:-shift] &= average[:-shift] >= average[shift:]
    peaks &= (f>=65)&(f<9000)&(average>np.max(average)*.0005)
    ids=np.flatnonzero(peaks)
    fractional=np.zeros(len(average))
    logs=np.log(np.maximum(average,1e-12))
    fractional[ids]=np.clip(.5*(logs[ids-1]-logs[ids+1])/
                           (logs[ids-1]-2*logs[ids]+logs[ids+1]),-.5,.5)
    advance=2*np.pi*(np.arange(size//2+1)+fractional)*hop/size
    tone=(f/65)**4/(1+(f/65)**4)/np.sqrt(1+(f/6500)**8)
    output=np.zeros((len(pad),2),dtype=np.float32)
    weight=np.zeros(len(pad),dtype=np.float32)
    for ch in range(2):
        amp=mean_smooth(np.abs(specs[ch]),19)
        amp=mean_smooth(amp,11)
        collapsed=np.zeros_like(amp)
        for k in ids:
            collapsed[:,k]=np.sqrt(np.sum(amp[:,k-3:k+4]**2,axis=1))
        amp=collapsed
        amp*=tone
        for i in range(len(frames)):
            phase=initial+advance*i+(offset if ch else 0)
            spec=amp[i]*np.exp(1j*phase)
            spec[0]=0
            signal=np.fft.irfft(spec,n=size).astype(np.float32)
            # Synthesis window sum is used because phase-continuous oscillator
            # frames already contain their own stationary analysis spectrum.
            output[i*hop:i*hop+size,ch]+=signal*window
        if ch==0:
            for i in range(len(frames)): weight[i*hop:i*hop+size]+=window
    output/=np.maximum(weight[:,None],1e-8)
    return output[size//2:size//2+len(x)]

def impulse(seed,length,rt60):
    rng=np.random.default_rng(seed)
    n=int(length*SR)
    t=np.arange(n)/SR
    ir=rng.normal(size=n)*np.exp(-math.log(1000)*t/rt60)
    # No prominent single echo or direct impulse. This is diffuse convolution
    # of the supplied recording, not an independently audible noise layer.
    spec=np.fft.rfft(ir)
    f=np.fft.rfftfreq(n,1/SR)
    spec*=1/np.sqrt(1+(f/4400)**8)
    spec*=(f/85)**4/(1+(f/85)**4)
    ir=np.fft.irfft(spec,n=n)
    ir/=max(float(np.sqrt(np.sum(ir**2))),1e-12)
    return ir.astype(np.float32)

def coarse_rms(x,step=480):
    n=len(x)//step
    return np.sqrt(np.mean(x[:n*step].reshape(n,step,2)**2,axis=(1,2))+1e-12)

def stats(x):
    return {'frames':len(x),'seconds':len(x)/SR,'finite':bool(np.isfinite(x).all()),
            'peak_dbfs':20*math.log10(max(float(np.max(np.abs(x))),1e-12)),
            'rms_dbfs':10*math.log10(max(float(np.mean(x.astype(np.float64)**2)),1e-24)),
            'full_scale_samples':int(np.count_nonzero(np.abs(x)>=1))}

def modulation(x):
    env=coarse_rms(x)
    env=env/max(float(np.mean(env)),1e-12)
    window=np.hanning(len(env))
    power=np.abs(np.fft.rfft((env-1)*window))**2
    f=np.fft.rfftfreq(len(env),.01)
    return {'normalised_envelope_variation':float(np.std(env)),
            'rhythmic_modulation_power_0_7_to_8_hz':float(np.sum(power[(f>=.7)&(f<=8)]))}

def main():
    assert sha(SOURCE)=='a60986de41c0cd5418ad9dd56bdbf442ac01b8a284dd6f9b8a6c2930e39443db'
    raw=ROOT/'source.f32'
    if not raw.exists():
        run(['ffmpeg','-hide_banner','-v','error','-n','-i',SOURCE,'-map','0:a:0',
             '-ar',SR,'-ac',2,'-f','f32le',raw])
    assert raw.stat().st_size==24480000*8
    src=np.memmap(raw,dtype='<f4',mode='r').reshape(-1,2)
    # Ten-second analysis/tail handles outside the requested transition window.
    a,b=80*SR,405*SR
    working=np.array(src[a:b],dtype=np.float32)
    print('Resynthesizing a sustained spectral bed at unchanged source timing.',flush=True)
    bed=spectral_bed(working)
    print('Adding restrained diffuse space to the sustained bed.',flush=True)
    long=convolution(bed,impulse(201022,5.0,4.0))
    ambient=.78*bed+.22*long
    # Level only the newly reconstructed pad's short envelope. This suppresses
    # inter-partial beating without changing original sample timing, pitches,
    # or the dynamics of the untouched opening and ending.
    envelope=coarse_rms(ambient)**2
    short_power=mean_smooth(envelope,3)
    slow_power=mean_smooth(envelope,501)
    pad_level=np.sqrt(slow_power/(short_power+1e-12))
    pad_level=mean_smooth(np.clip(pad_level,.45,2.2),5)
    level=np.interp(np.arange(len(ambient))/480,np.arange(len(pad_level)),pad_level)
    ambient*=level[:,None]
    # Match broad phrase energy, without chasing individual notes or pulses.
    target=mean_smooth(coarse_rms(working)**2,2001)
    current=mean_smooth(coarse_rms(ambient)**2,2001)
    gain=np.sqrt(target/(current+1e-12))
    gain=np.clip(gain,.1,20)
    gain=mean_smooth(gain,1001)
    g=np.interp(np.arange(len(ambient))/480,np.arange(len(gain)),gain).astype(np.float32)
    ambient*=g[:,None]
    del long,bed
    # Mix weight rises/falls smoothly with zero slope at each section boundary.
    t=np.arange(len(working))/SR+80
    blend=np.zeros(len(t),dtype=np.float32)
    ramp=(t>=90)&(t<180)
    blend[ramp]=(.5-.5*np.cos(np.pi*(t[ramp]-90)/90))
    blend[(t>=180)&(t<=300)]=1
    ramp=(t>300)&(t<390)
    blend[ramp]=(.5+.5*np.cos(np.pi*(t[ramp]-300)/90))
    # Centre: 95% ambient bed, 5% original; source timing is never changed.
    wet=.95*blend
    combined=working*(1-wet[:,None])+ambient*wet[:,None]
    # Keep broad loudness stable through the morph, without fast gain pumping.
    mixed_power=mean_smooth(coarse_rms(combined)**2,2001)
    correction=np.sqrt(target/(mixed_power+1e-12))
    correction=mean_smooth(np.clip(correction,.8,1.6),1001)
    corr=np.interp(np.arange(len(working))/480,np.arange(len(correction)),correction)
    corr=1+(corr-1)*blend
    combined*=corr[:,None]
    out=np.array(src,dtype=np.float32)
    out[a:b]=combined
    before=modulation(np.array(src[180*SR:300*SR]))
    after=modulation(out[180*SR:300*SR])
    reduction_db=10*math.log10(after['rhythmic_modulation_power_0_7_to_8_hz']/before['rhythmic_modulation_power_0_7_to_8_hz'])
    print('Middle pulse-envelope power change:',round(reduction_db,2),'dB',flush=True)
    assert reduction_db < -6, (before,after)
    assert np.array_equal(out[:90*SR],src[:90*SR])
    assert np.array_equal(out[390*SR:],src[390*SR:])
    gain=min(1.,10**(-2/20)/float(np.max(np.abs(out))))
    out*=gain
    pcm=ROOT/'master.f32'
    out.tofile(pcm)
    master=ROOT/'Illuminated-Horizon-Ambient-Middle-v2.wav'
    run(['ffmpeg','-hide_banner','-v','error','-n','-f','f32le','-ar',SR,'-ac',2,'-i',pcm,
         '-c:a','pcm_s24le',master])
    mp3=ROOT/'Illuminated-Horizon-Ambient-Middle-v2.mp3'
    run(['ffmpeg','-hide_banner','-v','error','-n','-i',master,'-c:a','libmp3lame','-b:a','320k',
         '-metadata','title=Illuminated Horizon - Ambient Middle v2',mp3])
    # A/B excerpts at the SAME original timing, with matched broad RMS.
    centre=out[200*SR:245*SR]
    original=np.array(src[200*SR:245*SR])
    original*=math.sqrt(float(np.mean(centre**2))/float(np.mean(original**2)))
    original.tofile(ROOT/'original-review.f32')
    run(['ffmpeg','-hide_banner','-v','error','-n','-f','f32le','-ar',SR,'-ac',2,
         '-i',ROOT/'original-review.f32','-af','afade=t=in:d=0.03,afade=t=out:st=43:d=2',
         '-c:a','libmp3lame','-b:a','320k',ROOT/'Original-Middle-Level-Matched-45s.mp3'])
    for name,ss,dur in [('Ambient-Middle-Review-45s.mp3',200,45),
                         ('Ambient-Entry-Review-v2.mp3',100,130),
                         ('Pulse-Return-Review-v2.mp3',285,120)]:
        run(['ffmpeg','-hide_banner','-v','error','-n','-ss',ss,'-i',master,'-t',dur,
             '-af',f'afade=t=in:d=0.03,afade=t=out:st={dur-2}:d=2',
             '-c:a','libmp3lame','-b:a','320k',ROOT/name])
    decoded=ROOT/'delivery-decoded.f32'
    run(['ffmpeg','-hide_banner','-v','error','-n','-i',mp3,'-f','f32le',decoded])
    final=np.memmap(decoded,dtype='<f4',mode='r').reshape(-1,2)
    delivery=stats(final)
    assert delivery['frames']==len(src) and delivery['finite'] and delivery['full_scale_samples']==0
    d=np.abs(np.diff(final,axis=0))
    peak_step=float(d.max())
    assert peak_step < .25, peak_step
    run(['ffmpeg','-hide_banner','-nostats','-i',mp3,'-af','ebur128=peak=true','-f','null','-'],
        'delivery-loudness.log')
    record={'status':'local listening candidate; user review pending',
            'source':str(SOURCE),'source_sha256':sha(SOURCE),
            'feedback_on_v1':'User hears whole-mix stretching and says it sounds crap; wants less repeating pulse and gradual return.',
            'method':'Source-spectrum additive sustained bed with continuous phases and slow amplitudes, plus restrained diffuse convolution; original timing retained.',
            'time_stretch':False,'pitch_shifting_filter':False,'external_music_generation_or_models':False,
            'spectral_oscillator_spacing_hz':SR/65536,
            'centre_direct_mix_fraction':.05,'fixed_headroom_gain_db':20*math.log10(gain),
            'pad_envelope_leveling':'30 ms RMS / 5 s target; 50 ms-smoothed gain; only reconstructed pad affected',
            'source_unchanged_before_fixed_gain_s':[[0,90],[390,510]],
            'sections_s':{'fade_to_ambient':[90,180],'ambient_hold':[180,300],'restore_pulse':[300,390]},
            'middle_before':before,'middle_after':after,'middle_modulation_power_change_db':reduction_db,
            'delivery':delivery,'max_adjacent_sample_step':peak_step,
            'limits':['No isolated instrument stems; middle is a new sustained spectral texture derived from a stereo master.',
                      'Texture timbre and fine phase/pitch detail differ from the source; it is not a clean pad stem.',
                      'Signal checks do not establish musical quality or user approval.',
                      'Assistant has not continuously auditioned the output.',
                      'Original and rejected v1 preserved; local files only; no commit or push.'],
            'outputs':{p.name:sha(p) for p in ROOT.glob('*.mp3')}}
    record['outputs'][master.name]=sha(master)
    (ROOT/'delivery-v2.json').write_text(json.dumps(record,indent=2))
    print(json.dumps(record,indent=2),flush=True)

if __name__=='__main__': main()
