"""Optional Snowline test: source-resequenced wind and two settling creaks.

One original wind recording is used. No additional field recordings or paid
models. Current output is a listening candidate, not recorded material foley.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from scipy import signal

from generate_polar_comms import decode
from generate_receiver_texture import RATE, rms, write_audio
from build_snowline_environment import WIND_EVENTS, event_envelope
from build_snowline_radio_session import validate_audio, listening_copy


def corr(a,b):
    a=a.reshape(-1).astype(float);b=b.reshape(-1).astype(float)
    a-=a.mean();b-=b.mean()
    denominator=np.linalg.norm(a)*np.linalg.norm(b)
    return float(np.dot(a,b)/denominator) if denominator>1e-15 else None


def overlapping_sections(source,count,rng):
    """Long overlapping source sections, without a fixed playback period."""
    source=source[RATE:29*RATE]
    total=np.zeros((count,2),dtype=np.float64)
    weights=np.zeros(count,dtype=np.float64)
    cursor=-round(12*RATE);grains=[]
    while cursor<count:
        length=round(rng.uniform(9,14)*RATE)
        start=int(rng.integers(0,len(source)-length+1))
        window=np.sin(np.pi*np.arange(length)/(length-1))**2
        a=max(0,cursor);b=min(count,cursor+length)
        if b>a:
            offset=a-cursor;w=window[offset:offset+b-a]
            total[a:b]+=source[start+offset:start+offset+b-a]*w[:,None]
            weights[a:b]+=w*w
        grains.append({'destination_seconds':cursor/RATE,'source_start_seconds':1+start/RATE,'length_seconds':length/RATE})
        cursor+=round(rng.uniform(3.5,5.3)*RATE)
    if weights.min()<.03:raise ValueError('Uncovered or weak wind grain overlap.')
    total/=np.sqrt(weights)[:,None]
    return total,grains


def varied_wind(source,baseline):
    result=np.zeros_like(baseline);records=[];lag_checks=[]
    sos=signal.butter(2,1800,fs=RATE,output='sos')
    for index,(start,duration,up,down,_) in enumerate(WIND_EVENTS):
        at=round(start*RATE);count=round(duration*RATE)
        reference=baseline[at:at+count]
        target=rms(reference);reference_peak=float(np.abs(reference).max())
        best=None
        # Keep active-passage RMS matched; choose a lower-crest assembly rather
        # than using a limiter or increasing the accepted broad level.
        for attempt in range(4):
            rng=np.random.default_rng(13600+index*20+attempt)
            x,grains=overlapping_sections(source,count,rng)
            x=signal.sosfiltfilt(sos,x,axis=0)
            t=np.arange(count)/RATE
            envelope=event_envelope(count,RATE,up,down)
            envelope*=.88+.08*np.sin(2*np.pi*t/(duration*.79)+rng.uniform(0,6))+.04*np.sin(2*np.pi*t/(duration*.43)+rng.uniform(0,6))
            x*=envelope[:,None]
            calibration=target/max(rms(x),1e-12)
            x=(x*calibration).astype(np.float32)
            peak=float(np.abs(x).max())
            if best is None or peak<best[0]:best=(peak,x,grains,calibration,attempt)
            if peak<=reference_peak*1.15:break
        peak,x,grains,calibration,attempt=best
        if peak>reference_peak*1.25:
            raise ValueError('New wind crest exceeds baseline tolerance; review source assembly.')
        match=20*np.log10(rms(x)/target)
        if abs(match)>.001:raise ValueError('Wind passage RMS matching failed.')
        result[at:at+count]=x
        records.append({'start_seconds':start,'duration_seconds':duration,'fade_in_seconds':up,'fade_out_seconds':down,
            'source_grains':grains,'seed':13600+index*20+attempt,'calibration_gain':calibration,
            'baseline_rms_dbfs':20*np.log10(target),'new_rms_dbfs':20*np.log10(rms(x)),
            'rms_difference_db':match,'baseline_peak':reference_peak,'new_peak':peak,
            'filter':'Same second-order1800Hz low-pass as baseline','pitch_or_playback_rate_change':False})
        offset=round((up+2)*RATE);length=6*RATE;lag=24*RATE
        if offset+lag+length<=count:
            lag_checks.append({'passage_start_seconds':start,'sample_start_seconds':start+offset/RATE,
                'window_seconds':6,'lag_seconds':24,
                'baseline_waveform_correlation':corr(reference[offset:offset+length],reference[offset+lag:offset+lag+length]),
                'variant_waveform_correlation':corr(x[offset:offset+length],x[offset+lag:offset+lag+length])})
    return result,records,lag_checks


def settling_creak(seed,seconds,right):
    rng=np.random.default_rng(seed);count=round(seconds*RATE)
    t=np.arange(count)/RATE;p=t/seconds
    excitation=np.zeros(count)
    cursor=0
    # Irregular small stick/slip releases feeding broad material resonances.
    while cursor<count-3:
        strength=rng.uniform(.4,1)
        excitation[cursor:cursor+3]+=strength*np.array([1,-.65,-.35])
        step=rng.uniform(.004,.015)*(1+.7*abs(cursor/count-.45))
        cursor+=max(3,round(step*RATE))
    body=np.zeros(count)
    for frequency,q,weight in [(235,7,.9),(610,9,.45),(1180,6,.14)]:
        b,a=signal.iirpeak(frequency,q,fs=RATE)
        low=signal.lfilter(b,a,excitation)
        b,a=signal.iirpeak(frequency*1.09,q,fs=RATE)
        high=signal.lfilter(b,a,excitation)
        body+=weight*(low*(1-p)+high*p)
    friction=signal.sosfiltfilt(signal.butter(2,[180,1700],fs=RATE,btype='bandpass',output='sos'),rng.normal(size=count))
    friction*=rms(body)*.18/max(rms(friction),1e-12)
    contact=body+friction
    # Restrain isolated stick/slip spikes so the quieter contact body remains
    # useful. This shapes the newly made effect only, not the music/mix.
    scale=max(float(np.percentile(np.abs(contact),99)),1e-12)
    x=np.tanh(contact/scale)*np.sin(np.pi*np.clip(p,0,1))**1.8
    x*=.0055/max(rms(x),1e-12)
    x*=min(1.,.025/max(float(np.abs(x).max()),1e-12))
    tail=round(.04*RATE);direct=np.pad(x,(0,tail));reflected=np.pad(x,(tail,0))
    gains=(.62,.82) if right else (.80,.63)
    out=np.column_stack([gains[0]*direct+.035*reflected,gains[1]*direct+.028*reflected]).astype(np.float32)
    return out,{'seed':seed,'duration_seconds':len(out)/RATE,'intended_source':'Quiet frame/pipe contact settling; original procedural friction/resonance study',
        'rms_dbfs':20*np.log10(rms(out)),'sample_peak':float(np.abs(out).max()),'position':'right window frame' if right else 'left lower pipe/frame',
        'recorded_foley':False,'perceived_material_and_realism':'requires listening'}


def mix(inputs,target):
    args=[imageio_ffmpeg.get_ffmpeg_exe(),'-v','error']
    for p in inputs:args+=['-i',str(p)]
    graph=''.join(f'[{i}:a]' for i in range(len(inputs)))+f'amix=inputs={len(inputs)}:duration=first:dropout_transition=0:normalize=0[a]'
    subprocess.run(args+['-filter_complex',graph,'-map','[a]','-c:a','flac','-sample_fmt','s32',
        '-bits_per_raw_sample','24','-n',str(target)],capture_output=True,check=True)


def preview(source,target,gain):
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(source),'-ss','54','-t','90',
        '-af',f'volume={gain:.15g}dB','-c:a','libmp3lame','-b:a','192k','-n',str(target)],capture_output=True,check=True)


def run(parent,wind_source,out):
    if out.exists() and any(out.iterdir()):raise ValueError('Choose a new/empty output directory.')
    r=json.loads((parent/'recipe.json').read_text(encoding='utf-8'))
    control=parent/'Snowline-radio-wind-and-ventilation-9min-v2.flac'
    old_wind=parent/'Snowline-exterior-wind-9min-v2.flac'
    vent=parent/'Snowline-ventilation-9min-v2.flac'
    base=Path(r['music_radio_parent']['path'])
    for p in [control,old_wind,vent]:
        expected=next(x['sha256'] for x in r['outputs'] if x['file']==p.name)
        if hashlib.sha256(p.read_bytes()).hexdigest()!=expected:raise ValueError('Baseline file changed.')
    if hashlib.sha256(wind_source.read_bytes()).hexdigest()!='324470a6fa73b57ef021edca2ddd6f4c20a6319bd0148bc2ea0f4f71c8d19a34':raise ValueError('Wrong wind original.')
    out.mkdir(parents=True,exist_ok=True);checks=[]
    def check(path,seconds):
        item=validate_audio(path,seconds);item['file']=path.relative_to(out).as_posix();checks.append(item)
    print('Assembling varied wind from the existing original...',flush=True)
    wind,passages,lag_checks=varied_wind(decode(wind_source),decode(old_wind))
    wind_path=out/'Snowline-varied-wind-9min-test.flac'
    write_audio(wind,wind_path,'flac');del wind
    check(wind_path,540)
    print('Making two quiet settling-creak candidates...',flush=True)
    creaks=np.zeros((540*RATE,2),dtype=np.float32);creak_events=[]
    for index,(time,seconds,right) in enumerate([(91.,1.65,True),(338.,2.15,False)]):
        x,info=settling_creak(13691+index,seconds,right)
        at=round(time*RATE);creaks[at:at+len(x)]+=x
        info['start_seconds']=time;creak_events.append(info)
        path=out/f'settling-creak-{index+1}.wav';write_audio(x,path,'pcm_s24le');check(path,len(x)/RATE)
    creak_path=out/'Snowline-two-creaks-9min-test.flac'
    write_audio(creaks,creak_path,'flac');del creaks
    check(creak_path,540)
    candidates={}
    for key,label,inputs in [('B-wind-only','wind-variation',[base,wind_path,vent]),
                              ('C-wind-and-creaks','wind-and-creaks',None)]:
        folder=out/key;folder.mkdir()
        lossless=folder/f'Snowline-{label}-9min-test.flac'
        if inputs is None:inputs=[Path(candidates['B-wind-only']['lossless']),creak_path]
        mix(inputs,lossless);check(lossless,540)
        listening=folder/f'Snowline-{label}-9min-test.mp3'
        metering=listening_copy(lossless,listening,folder);check(listening,540)
        short=out/f'{key}-90s-check.mp3'
        preview(lossless,short,metering['matching_passes'][-1]['gain_db']);check(short,90)
        candidates[key]={'lossless':str(lossless.resolve()),'listening':str(listening.resolve()),'metering':metering,
                         'short_check':short.name,'preview_source_start_seconds':54,'preview_seconds':90}
    baseline_short=out/'A-approved-v2-90s-check.mp3'
    preview(control,baseline_short,r['metering']['matching_passes'][-1]['gain_db']);check(baseline_short,90)
    source_hashes=[{'path':str(p.resolve()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [control,old_wind,vent,base,wind_source]]
    recipe={'date':'2026-11-02','user_request':'Test wind variation and two quiet settling creaks; retain approved v2 as comparison.',
        'test_only':True,'approved_preset_replaced':False,'seconds':540,'wind_originals_available':1,
        'wind_method':'Overlap9–14s original-rate source sections with unequal3.5–5.3s advances; same1800Hz placement filter; match each baseline wind passage RMS.',
        'new_field_recordings_or_paid_generations':False,'source_fragments_can_recur':True,
        'fixed24_second_cycle_tiled':False,'wind_passages':passages,'sampled_lag24_checks':lag_checks,
        'wind_level_scope':'Per-passage RMS matched; this does not establish equal perceived loudness or identical peak timing.',
        'creak_events':creak_events,'music_radio_and_ventilation_levels_changed':False,
        'candidate_B':'Wind variation only; isolates wind change.','candidate_C':'Same B mix plus two creaks; isolates added details.',
        'sources':source_hashes,'candidates':candidates,'outputs':checks,'assistant_listening':False,'user_test_feedback':'pending',
        'implementation':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in
            [Path(__file__),Path(__file__).with_name('build_snowline_environment.py'),Path(__file__).with_name('build_snowline_radio_session.py')]]}
    (out/'recipe.json').write_text(json.dumps(recipe,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'output':str(out.resolve()),'files_checked':len(checks),
        'passage_rms_difference_db':[x['rms_difference_db'] for x in passages],
        'lag24_checks':lag_checks,'creaks':creak_events,
        'candidate_lufs':{k:v['metering']['listening_copy']['integrated_lufs'] for k,v in candidates.items()}},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--parent',type=Path,required=True);p.add_argument('--wind',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();run(a.parent,a.wind,a.out)
