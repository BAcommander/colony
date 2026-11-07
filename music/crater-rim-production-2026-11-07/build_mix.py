"""Reproducible first Crater Rim hour audition from two supplied music sources."""
from pathlib import Path
import concurrent.futures, hashlib, json, math, shutil, subprocess
import numpy as np
from scipy import signal

H=Path(__file__).resolve().parent
R=H.parents[1]
C=R/'.local/crater-rim-audio-2026-11-07-v1'
E=R/'exports/14-crater-rim-survey/audio-1h-v1'
SR=48000
SECONDS=3600
N=SR*SECONDS
FF=shutil.which('ffmpeg')
PREFIX='Crater-Rim-Survey-1-Hour'

def save(path,data):
    path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(4*1024**2),b''):h.update(b)
    return h.hexdigest()

def run(args):
    return subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)

def decode(path,seconds):
    q=run([FF,'-v','error','-xerror','-err_detect','explode','-i',str(path),'-vn','-t',str(seconds),'-ar',str(SR),'-ac','2','-f','f32le','pipe:1'])
    x=np.frombuffer(q.stdout,'<f4').reshape(-1,2).copy()
    assert len(x)==round(seconds*SR) and np.isfinite(x).all()
    return x

def encode(raw,path,ext,seconds=None):
    args=[FF,'-v','error','-xerror','-n','-f','f32le','-ar',str(SR),'-ac','2','-i',str(raw)]
    if seconds is not None:args+=['-t',str(seconds)]
    args+=['-c:a','flac','-sample_fmt','s32','-bits_per_raw_sample','24'] if ext=='flac' else ['-c:a','libmp3lame','-b:a','192k']
    run(args+[str(path)])

def meter(path):
    q=run([FF,'-hide_banner','-nostats','-i',str(path),'-vn','-af','loudnorm=I=-23:TP=-2:LRA=11:print_format=json','-f','null','-'])
    s=q.stderr.decode('utf-8','replace');a=s.rfind('{');b=s.find('}',a)+1
    d=json.loads(s[a:b])
    return {'integrated_lufs':float(d['input_i']),'lra_lu':float(d['input_lra']),'true_peak_dbtp':float(d['input_tp']),'measurement_only':True}

def wind_material(source):
    x=source[SR:29*SR];k=4*SR;phase=np.arange(k)/k*np.pi/2
    join=x[-k:]*np.cos(phase)[:,None]+x[:k]*np.sin(phase)[:,None]
    cycle=np.concatenate([x[k:-k],join])
    padded=np.concatenate([cycle]*3)
    filtered=signal.sosfiltfilt(signal.butter(2,1800,fs=SR,output='sos'),padded,axis=0)
    out=filtered[len(cycle):2*len(cycle)].astype(np.float32)
    assert len(out)==24*SR
    raw=C/'wind-prepared-unscaled.f32';out.tofile(raw)
    flac=C/'wind-prepared-unscaled.flac';encode(raw,flac,'flac')
    before=meter(flac);gain=-38-before['integrated_lufs']
    out*=10**(gain/20)
    info={'original_trim_seconds':[1,29],'equal_power_overlap_seconds':4,'prepared_period_seconds':24,
          'filter':'2nd-order 1800Hz low-pass, zero phase in three-cycle context; retain middle cycle',
          'prepared_unscaled_measurements':before,'fixed_prepared_source_gain_db':gain,
          'nominal_plateau_target_lufs':-38,'gain_basis':'New scene audition, calibrated after shelter filtering; no normalization of sparse hour stem',
          'original_source_modified':False}
    return out,info

def room_material(seconds=197,seed=140711,target_db=-45):
    rate=12000;n=seconds*rate;rng=np.random.default_rng(seed)
    frequencies=np.fft.rfftfreq(n,1/rate);safe=np.maximum(frequencies,.01)
    response=1/np.sqrt((1+(140/safe)**8)*(1+(safe/950)**8));response[0]=0
    x=np.fft.irfft(np.fft.rfft(rng.normal(size=n))*response,n)
    x/=np.sqrt(np.mean(x*x));time=np.arange(n)/rate
    x*=.96+.025*np.sin(2*np.pi*2*time/seconds+.7)+.015*np.sin(2*np.pi*5*time/seconds+1.9)
    low=np.column_stack([.72*x+.025*np.roll(x,round(.031*rate)),.70*x+.023*np.roll(x,round(.047*rate))]).astype(np.float32)
    out=signal.resample_poly(low,4,1,axis=0,padtype='wrap').astype(np.float32)
    out*=10**(target_db/20)/math.sqrt(float(np.mean(out.astype(np.float64)**2)))
    typical=float(np.percentile(np.abs(np.diff(out,axis=0)),99));seam=float(np.max(np.abs(out[0]-out[-1])))
    assert seam<3*typical
    info={'construction':'Original deterministic periodic band-shaped noise; no recorded machinery, voices or pitched oscillator',
          'algorithm_reference':'scripts/build_snowline_environment.py make_ventilation and scripts/generate_receiver_texture.py noise; locally implemented with scene-specific period, seed and level',
          'period_seconds':seconds,'seed':seed,'nominal_band_hz':[140,950],'synthesis_rate':rate,'output_rate':SR,
          'target_stereo_rms_dbfs':target_db,'actual_stereo_rms_dbfs':20*math.log10(math.sqrt(float(np.mean(out.astype(np.float64)**2)))),
          'stereo':'Narrow image, unequal 31/47ms taps','level_modulation_cycles_per_period':[2,5],
          'period_boundary_step':seam,'ordinary_step_p99':typical,'new_scene_balance_pending':True}
    return out,info

def schedules():
    music=[];start=0;idx=0
    while start<SECONDS:
        track=idx%2;source_in=0 if idx==0 else 4;source_out=294
        fade_in=0 if idx==0 else (24 if track==1 else 30)
        fade_out=24 if track==0 else 30
        length=source_out-source_in
        music.append({'index':idx,'track':track,'start':start,'source_in':source_in,'source_out':source_out,
                      'natural_end':start+length,'output_end':min(SECONDS,start+length),'fade_in':fade_in,'fade_out':fade_out})
        start+=length-fade_out;idx+=1
    rng=np.random.default_rng(20261107);wind=[];start=45
    while start+80<3580:
        duration=65 if not wind else int(rng.integers(60,77))
        wind.append({'start':start,'end':start+duration,'duration':duration,'fade_in':12,'fade_out':18,
                     'source_phase_seconds':round(float(rng.uniform(0,24)),3)})
        start+=duration+int(rng.integers(110,151))
    return music,wind

def envelopes(loc,length,fade_in,fade_out):
    env=np.ones(len(loc),np.float64)
    if fade_in:
        k=round(fade_in*SR);head=loc<k;env[head]*=np.sin(loc[head]/k*np.pi/2)
    if fade_out:
        k=round(fade_out*SR);tail=loc>=length-k;env[tail]*=np.cos((loc[tail]-(length-k))/k*np.pi/2)
    return env

def validate(path,raw,seconds,lossless):
    expected_frames=round(seconds*SR)
    q=subprocess.Popen([FF,'-v','error','-xerror','-err_detect','explode','-i',str(path),'-vn','-ar',str(SR),'-ac','2','-f','f32le','pipe:1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    frames=0;peak=err=xx=yy=xy=diff2=0.;last=None
    with raw.open('rb') as f:
        while True:
            a=f.read(SR*8);b=q.stdout.read(len(a) if a else 1)
            if not a:assert not b;break
            assert len(a)==len(b)
            x=np.frombuffer(a,'<f4').astype(np.float64);y=np.frombuffer(b,'<f4').astype(np.float64)
            assert np.isfinite(y).all();delta=x-y
            peak=max(peak,float(abs(y).max()));err=max(err,float(abs(delta).max()))
            xx+=float(np.sum(x*x));yy+=float(np.sum(y*y));xy+=float(np.sum(x*y));diff2+=float(np.sum(delta*delta));frames+=len(y)//2;last=y[-2:]
    stderr=q.stderr.read();assert q.wait()==0,stderr.decode('utf-8','replace')
    assert frames==expected_frames and peak<1
    snr=10*math.log10(xx/max(diff2,1e-30));corr=xy/math.sqrt(xx*yy)
    if lossless:assert err<2.4e-7,err
    else:assert snr>25 and corr>.995,(snr,corr)
    return {'file':str(path),'bytes':path.stat().st_size,'sha256':sha(path),'seconds':seconds,'sample_frames':frames,
            'all_finite':True,'unclipped':True,'peak_dbfs':20*math.log10(peak),'reference_max_error':err,
            'reference_snr_db':snr,'reference_correlation':corr,'last_stereo_sample':last.tolist()}

def excerpts(raw,name,start,seconds,fades=True):
    p=C/(name+'.f32')
    with raw.open('rb') as f:f.seek(round(start*SR)*8);b=f.read(round(seconds*SR)*8)
    x=np.frombuffer(b,'<f4').reshape(-1,2).copy();assert len(x)==round(seconds*SR)
    if fades:
        a=round(.5*SR);z=2*SR
        x[:a]*=np.linspace(0,1,a,dtype=np.float32)[:,None]
        x[-z:]*=np.linspace(1,0,z,dtype=np.float32)[:,None]
    x.tofile(p);out=H/'review'/(name+'.mp3');encode(p,out,'mp3')
    check=validate(out,p,seconds,False);check.update(full_mix_start=start,review_only_fades_seconds=[.5,2] if fades else [0,0],separate_normalization=False)
    return check

def main():
    assert FF
    C.mkdir(parents=True,exist_ok=False);E.mkdir(parents=True,exist_ok=True)
    assert not any(E.iterdir()),'Choose a fresh delivery version'
    source_manifest=json.loads((H/'source-manifest.json').read_text(encoding='utf-8'))
    sources=[];fingerprints={}
    for item in source_manifest['sources']:
        path=Path(item['preserved_path']);assert sha(path)==item['sha256']
        sources.append(decode(path,300));fingerprints[str(path)]=item['sha256']
    wind_path=R/'music/sfx-library/assets/wind-soft-exterior-01.mp3'
    wind_sha='324470a6fa73b57ef021edca2ddd6f4c20a6319bd0148bc2ea0f4f71c8d19a34'
    assert sha(wind_path)==wind_sha;fingerprints[str(wind_path)]=wind_sha
    print('Preparing sheltered wind and independent room-air bed',flush=True)
    wind,winfo=wind_material(decode(wind_path,30));room,rinfo=room_material()
    music,events=schedules();gains=[-6.3,-5.9]
    plan={'date':'2026-11-07','authority':source_manifest['user_request'],'duration_seconds':SECONDS,'sample_rate':SR,'channels':2,
          'music_source_gains_db':gains,'music_schedule':music,'music_retained_region_seconds':[4,294],
          'first_track_keeps_original_start':True,'crossfade_seconds':{'Room_to_Basin':24,'Basin_to_Room':30},
          'crossfade_curve':'Equal-power cosine/sine, sample-indexed','subsequent_pair_period_seconds':526,
          'source_fingerprints':fingerprints,'wind_source':str(wind_path),'wind':winfo,'wind_events':events,'wind_event_count':len(events),
          'wind_off_gaps_seconds':[b['start']-a['end'] for a,b in zip(events,events[1:])],
          'room_air':rinfo,'opening':'No Colony opening fade baked; first source natural entrance retained. Apply current opening once in later video assembly.',
          'closing':'One sample-indexed 20s linear fade applied equally to all stems; final stereo sample zero',
          'no_music_eq_compression_pitch_or_stretch':True,'new_paid_generation':False,'additional_sfx':['sheltered wind','quiet room air'],
          'wind_modulation':'.92 + .05*sin(2*pi*event_time/31.7+.4) + .03*sin(2*pi*event_time/47.3+1.1)',
          'audio_visual_sync':'This new hour cue sheet is for later long-animation integration. Current V5 review repeats existing visuals; no synchronization claim.',
          'user_balance_and_join_review':'pending','assistant_listening':False}
    save(H/'mix-recipe.json',plan)
    raws={k:C/(k+'-hour.f32') for k in ['mix','dry','sfx','wind','room']};handles={k:p.open('xb') for k,p in raws.items()}
    off_frames=0;peaks={k:0. for k in raws};coverage_min=99
    try:
        for first in range(0,N,10*SR):
            count=min(10*SR,N-first);frames=np.arange(first,first+count,dtype=np.int64)
            dry=np.zeros((count,2),np.float32);coverage=np.zeros(count,np.uint8)
            for seg in music:
                loc=frames-round(seg['start']*SR);length=round((seg['source_out']-seg['source_in'])*SR);on=(loc>=0)&(loc<length)
                if not on.any():continue
                coverage[on]+=1;local=loc[on];env=envelopes(local,length,seg['fade_in'],seg['fade_out'])
                dry[on]+=(sources[seg['track']][round(seg['source_in']*SR)+local]*10**(gains[seg['track']]/20)*env[:,None]).astype(np.float32)
            coverage_min=min(coverage_min,int(coverage.min()));assert np.all((coverage>=1)&(coverage<=2))
            air=room[frames%len(room)].copy();gust=np.zeros_like(dry);active=np.zeros(count,bool)
            for event in events:
                loc=frames-event['start']*SR;length=event['duration']*SR;on=(loc>=0)&(loc<length)
                if not on.any():continue
                active|=on;local=loc[on];t=local/SR
                attack=np.sin(np.pi/2*np.clip(local/(event['fade_in']*SR),0,1))**2
                release=np.sin(np.pi/2*np.clip((length-1-local)/(event['fade_out']*SR),0,1))**2
                env=np.minimum(attack,release)*(.92+.05*np.sin(2*np.pi*t/31.7+.4)+.03*np.sin(2*np.pi*t/47.3+1.1))
                phase=(local+round(event['source_phase_seconds']*SR))%len(wind)
                gust[on]+=wind[phase]*env[:,None]
            closing=np.minimum(1,(N-1-frames)/(20*SR)).astype(np.float32)
            dry*=closing[:,None];gust*=closing[:,None];air*=closing[:,None]
            sfx=gust+air;mix=dry+sfx
            assert not gust[~active].any();off_frames+=int((~active).sum())
            for name,data in [('dry',dry),('wind',gust),('room',air),('sfx',sfx),('mix',mix)]:
                assert np.isfinite(data).all() and abs(data).max()<1
                peaks[name]=max(peaks[name],float(abs(data).max()));handles[name].write(data.tobytes())
            if first%(600*SR)==0:print(f'Rendered {first//SR}/3600 seconds',flush=True)
    finally:
        for h in handles.values():h.close()
    assert all(p.stat().st_size==N*8 for p in raws.values())
    dry=np.memmap(raws['dry'],dtype='<f4',mode='r',shape=(N,2));join_ref={};joins=[]
    for seg in music[1:]:
        a=round(seg['start']*SR);b=a+round(seg['fade_in']*SR)
        if b>=3580*SR:continue
        key=str(seg['track']);piece=dry[a:b]
        if key not in join_ref:join_ref[key]=piece.copy()
        else:assert np.array_equal(piece,join_ref[key])
        joins.append({'incoming_track':seg['track'],'start':seg['start'],'seconds':seg['fade_in'],'equals_first_corresponding_join':True})
    specs=[('mix',PREFIX+'-music-and-SFX-v1.flac','flac'),('mix',PREFIX+'-music-and-SFX-v1.mp3','mp3'),
           ('dry',PREFIX+'-dry-music-v1.flac','flac'),('sfx',PREFIX+'-SFX-only-v1.flac','flac'),
           ('wind',PREFIX+'-wind-only-v1.flac','flac'),('room',PREFIX+'-room-air-only-v1.flac','flac')]
    print('Encoding the full hour and independent stems',flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures=[pool.submit(encode,raws[k],E/name,ext) for k,name,ext in specs]
        for f in futures:f.result()
    print('Checking every decoded output sample against the recipe',flush=True)
    outputs=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        jobs={pool.submit(validate,E/name,raws[k],SECONDS,ext=='flac'):k for k,name,ext in specs}
        for f in concurrent.futures.as_completed(jobs):
            info=f.result();info['stem']=jobs[f];outputs.append(info);print('Verified '+Path(info['file']).name,flush=True)
    previews=[excerpts(raws['mix'],'Crater-Rim-music-wind-room-air-check-2min-v1',20,120),
              excerpts(raws['dry'],'Crater-Rim-Survey-Room-to-Basin-join-75s-v1',255,75),
              excerpts(raws['dry'],'Crater-Rim-Basin-to-Survey-Room-join-75s-v1',515,75),
              excerpts(raws['mix'],'Crater-Rim-full-pair-with-SFX-10min-v1',0,600)]
    levels=meter(E/(PREFIX+'-music-and-SFX-v1.flac'));assert levels['true_peak_dbtp']<-2
    for p,digest in fingerprints.items():assert sha(p)==digest
    save(H/'delivery-validation.json',{'status':'passed','seconds':SECONDS,'sample_frames_per_channel':N,'source_hashes_unchanged':True,
          'outputs':outputs,'reviews':previews,'full_mix_measurements':levels,'full_sample_reference_checks':True,
          'music_continuous_coverage_minimum':coverage_min,'wind_off_frames_exact_zero':off_frames,'repeated_dry_joins':joins,
          'raw_stem_peaks_dbfs':{k:20*math.log10(v) for k,v in peaks.items()},'assistant_listening':False,
          'user_join_balance_full_hour_review':'pending','video_full_length_created':False})
    print(json.dumps({'status':'passed','output':str(E),'mix':levels,'wind_passages':len(events),'reviews':str(H/'review')},indent=2),flush=True)

if __name__=='__main__':main()
