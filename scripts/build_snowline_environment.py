"""Add exterior wind and quiet room ventilation to the fixed Snowline radio mix."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from scipy import signal

from generate_polar_comms import decode
from generate_receiver_texture import RATE, noise, rms, write_audio
from build_snowline_radio_session import validate_audio, listening_copy

SECONDS=540
WIND_EVENTS=[(42.,72.,12.,16.,3.7),(169.,58.,11.,17.,14.2),
             (298.,83.,15.,20.,8.1),(438.,69.,12.,19.,20.6)]


def wind_cycle(source):
    """28s source region with4s equal-power overlap ->24s circular cycle."""
    x=source[RATE:29*RATE]
    if len(x)!=28*RATE:raise ValueError('Need the original30-second wind source.')
    overlap=4*RATE
    phase=np.arange(overlap)/overlap*np.pi/2
    join=x[-overlap:]*np.cos(phase)[:,None]+x[:overlap]*np.sin(phase)[:,None]
    cycle=np.concatenate([x[overlap:-overlap],join])
    # Periodic context avoids a new filtering transient at the cycle boundary.
    padded=np.concatenate([cycle,cycle,cycle])
    filtered=signal.sosfiltfilt(signal.butter(2,1800,fs=RATE,output='sos'),padded,axis=0)
    return filtered[len(cycle):2*len(cycle)].astype(np.float32)


def event_envelope(count,rate,fade_in,fade_out):
    t=np.arange(count)/rate;duration=count/rate
    attack=np.sin(np.pi/2*np.clip(t/fade_in,0,1))**2
    release=np.sin(np.pi/2*np.clip((duration-t)/fade_out,0,1))**2
    return np.minimum(attack,release)


def make_wind(source):
    cycle=wind_cycle(source)
    out=np.zeros((SECONDS*RATE,2),dtype=np.float32)
    source_gain=10**(4.85/20)
    for start,duration,fade_in,fade_out,phase in WIND_EVENTS:
        count=round(duration*RATE);time=np.arange(count)/RATE
        offset=(round(phase*RATE)+np.arange(count))%len(cycle)
        envelope=event_envelope(count,RATE,fade_in,fade_out)
        # Broad movement, not a pulse or synchronized radio ducking.
        envelope*=.88+.08*np.sin(2*np.pi*time/21.7+.4)+.04*np.sin(2*np.pi*time/39.1+1.1)
        at=round(start*RATE)
        out[at:at+count]+=cycle[offset]*(source_gain*envelope[:,None])
    return out,{'source_gain_db':4.85,'gain_basis':'Earlier Deepwell/Snowline audition starting level; new scene balance pending',
                'distance_filter':'Second-order1800Hz low-pass, periodic source context; artistic closed-glazing approximation',
                'source_trim_seconds':[1,29],'source_overlap_seconds':4,'prepared_source_cycle_seconds':24,
                'source_cycle_repeats':True,'full_envelope_repeats_every24s':False,
                'events':[dict(zip(['start_seconds','duration_seconds','fade_in_seconds','fade_out_seconds','source_phase_seconds'],e)) for e in WIND_EVENTS],
                'rms_dbfs':20*np.log10(max(rms(out),1e-12))}


def make_ventilation(seconds=SECONDS,seed=1348,rate=12000,target_db=-48):
    rng=np.random.default_rng(seed)
    n=round(seconds*rate);time=np.arange(n)/rate
    x=noise(rng,n,rate,140,950)
    strength=.96+.025*np.sin(2*np.pi*2*time/seconds+.7)+.015*np.sin(2*np.pi*5*time/seconds+1.9)
    x*=strength
    # Two nearby grilles, narrow stereo image; no added oscillator or sub-bass.
    low=np.column_stack([.72*x+.025*np.roll(x,round(.031*rate)),
                         .70*x+.023*np.roll(x,round(.047*rate))]).astype(np.float32)
    del x,time
    high=signal.resample_poly(low,RATE//rate,1,axis=0,padtype='wrap').astype(np.float32)
    high*=10**(target_db/20)/max(rms(high),1e-12)
    steps=np.abs(np.diff(high,axis=0))
    seam=float(np.max(np.abs(high[0]-high[-1])))
    typical=float(np.percentile(steps,99))
    if seam>3*typical:raise ValueError('Ventilation circular boundary is atypical.')
    return high,{'seed':seed,'construction':'Original periodic band-shaped noise, no recording or voice model',
                 'synthesis_rate_hz':rate,'delivery_rate_hz':RATE,'nominal_band_hz':[140,950],
                 'target_rms_dbfs':target_db,'actual_rms_dbfs':20*np.log10(rms(high)),
                 'slow_level_cycles_in_full_source':[2,5],'added_tonal_oscillators':False,
                 'seam_step':seam,'ordinary_step_p99':typical,
                 'bandwidth_note':'12kHz synthesis is sufficient for this deliberately low-frequency air layer; wrap-aware upsampling to48kHz.'}


def run(parent,wind_source,out):
    if out.exists() and any(out.iterdir()):raise ValueError('Choose a new/empty output directory.')
    source_hash='324470a6fa73b57ef021edca2ddd6f4c20a6319bd0148bc2ea0f4f71c8d19a34'
    if hashlib.sha256(wind_source.read_bytes()).hexdigest()!=source_hash:raise ValueError('Wrong wind source.')
    parent_recipe=json.loads((parent/'recipe.json').read_text(encoding='utf-8'))
    source=parent/'Snowline-music-and-radio-9min-v1.flac'
    expected=next(o['sha256'] for o in parent_recipe['outputs'] if o['file']==source.name)
    if hashlib.sha256(source.read_bytes()).hexdigest()!=expected:raise ValueError('Radio/music parent changed.')
    out.mkdir(parents=True,exist_ok=True);checks=[]
    print('Building four sheltered exterior-wind passages...',flush=True)
    wind,wind_recipe=make_wind(decode(wind_source))
    wind_path=out/'Snowline-exterior-wind-9min-v1.flac'
    write_audio(wind,wind_path,'flac');del wind
    checks.append(validate_audio(wind_path,SECONDS))
    print('Building quiet room ventilation...',flush=True)
    vent,vent_recipe=make_ventilation()
    vent_path=out/'Snowline-ventilation-9min-v1.flac'
    write_audio(vent,vent_path,'flac');del vent
    checks.append(validate_audio(vent_path,SECONDS))
    target=out/'Snowline-radio-wind-and-ventilation-9min-v1.flac'
    graph='[0:a][1:a][2:a]amix=inputs=3:duration=first:dropout_transition=0:normalize=0[a]'
    print('Mixing without changing the music or radio source levels...',flush=True)
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(source),'-i',str(wind_path),'-i',str(vent_path),
        '-filter_complex',graph,'-map','[a]','-ar',str(RATE),'-ac','2','-c:a','flac',
        '-sample_fmt','s32','-bits_per_raw_sample','24','-n',str(target)],capture_output=True,check=True)
    checks.append(validate_audio(target,SECONDS))
    listening=out/'Snowline-radio-wind-and-ventilation-9min-v1.mp3'
    metering=listening_copy(target,listening,out)
    checks.append(validate_audio(listening,SECONDS))
    preview=out/'Snowline-radio-wind-and-ventilation-2min-preview-v1.mp3'
    gain=metering['matching_passes'][-1]['gain_db']
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(target),'-t','120',
        '-af',f'volume={gain:.15g}dB','-c:a','libmp3lame','-b:a','192k','-n',str(preview)],capture_output=True,check=True)
    checks.append(validate_audio(preview,120))
    recipe={'date':'2026-11-02','user_choice':'Exterior wind and quiet ventilation','seconds':SECONDS,
        'parent_mix':{'path':str(source.resolve()),'sha256':expected,'mix_gain':1.,'radio_schedule_or_event_gains_changed':False},
        'wind_source':{'path':str(wind_source.resolve()),'sha256':source_hash,'original_modified':False},
        'wind':wind_recipe,'ventilation':vent_recipe,'outputs':checks,'metering':metering,
        'preview':{'seconds':120,'same_whole_mix_gain_as_full_listening_copy':True,'separately_normalized':False},
        'processing':'Additive stems only. No compression, limiter, music EQ/time/pitch change or production intro/fade added.',
        'assistant_listening':False,'user_environment_balance_review':'pending','paid_generation':False,
        'reference_recordings_used':False,'implementation':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in
            [Path(__file__),Path(__file__).with_name('generate_receiver_texture.py'),Path(__file__).with_name('build_snowline_radio_session.py')]]}
    (out/'recipe.json').write_text(json.dumps(recipe,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'output':str(out.resolve()),'files_checked':len(checks),
        'ventilation_rms_dbfs':vent_recipe['actual_rms_dbfs'],
        'full_listening_lufs':metering['listening_copy']['integrated_lufs'],'wind_events':wind_recipe['events']},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--parent',type=Path,required=True);p.add_argument('--wind',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();run(a.parent,a.wind,a.out)
