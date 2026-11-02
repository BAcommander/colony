"""Sparse push-to-talk revision; preserve v3 voice processing and event levels."""
import argparse
import hashlib
import json
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from scipy import signal

from generate_polar_comms import decode, beep
from generate_receiver_texture import RATE, rms, write_audio, check_audio
from analyze_ambient_audio import loudness


def click(rng, release=False):
    n=round(.045*RATE)
    t=np.arange(n)/RATE
    raw=rng.normal(size=n)
    raw=signal.sosfiltfilt(signal.butter(2,[450,4800],fs=RATE,btype='bandpass',output='sos'),raw)
    raw*=np.exp(-t/(.0035 if release else .0055))*(1-np.exp(-t/.0005))
    body=np.sin(2*np.pi*(1250 if release else 1750)*t)*np.exp(-t/.004)
    x=(raw*.7+body*.3)
    x*=.024/max(float(np.abs(x).max()),1e-12)
    # Finite one-shot: zero-filled room tap, without circular pre-echo.
    tail=round(.025*RATE)
    direct=np.pad(x,(0,tail))
    delayed=np.pad(x,(tail,0))
    return np.column_stack([.77*direct+.03*delayed,.64*direct+.025*delayed]).astype(np.float32)


def build(parent):
    r=json.loads((parent/'recipe.json').read_text(encoding='utf-8'))
    old={key:decode(parent/f'{key}.wav') for key in ['static','carrier','transmissions']}
    n=len(old['static']);seconds=n/RATE
    if abs(seconds-67)>.001:
        raise ValueError('This revision targets the verified67-second v3 source.')
    voices=np.zeros_like(old['transmissions']);gate=np.zeros(n);details=[]
    events=[x for x in r['events'] if x['kind']=='transmission']
    windows=[]
    for source_index,new_start,lead,tail in [(0,7.1,.30,.28),(3,32.3,.80,.33),(5,55.85,.35,.52)]:
        event=events[source_index]
        old_at=round(event['start_seconds']*RATE)
        length=round(event['duration_seconds']*RATE)
        new_at=round(new_start*RATE)
        original=old['transmissions'][old_at:old_at+length]
        voices[new_at:new_at+length]=original
        opening=new_start-lead;closing=new_start+length/RATE+tail
        a,b=round(opening*RATE),round(closing*RATE)
        local=np.ones(b-a)
        edge=round(.016*RATE)
        local[:edge]=.5-.5*np.cos(np.linspace(0,np.pi,edge))
        local[-edge:]=.5+.5*np.cos(np.linspace(0,np.pi,edge))
        gate[a:b]=np.maximum(gate[a:b],local)
        windows.append((opening,closing))
        details.append({'kind':'transmission','source_v3_index':source_index,
                        'start_seconds':new_start,'duration_seconds':length/RATE,
                        'receiver_open_seconds':opening,'receiver_close_seconds':closing,
                        'copied_voice_maximum_error':float(np.max(np.abs(voices[new_at:new_at+length]-original)))})
    t=np.arange(n)/RATE
    # Let the noise colour/level breathe only while receiving. It is fully off
    # between packets; the accepted voice samples do not get re-normalized.
    low=signal.sosfiltfilt(signal.butter(2,1100,fs=RATE,output='sos'),old['static'],axis=0)
    high=old['static']-low
    blend=.5+.5*np.sin(2*np.pi*t/19.7+.8)
    shaped=low*(.78+.22*blend[:,None])+high*(.42+.38*(1-blend[:,None]))
    movement=.72+.20*np.sin(2*np.pi*t/11.9+.7)+.08*np.sin(2*np.pi*t/3.7)
    static=shaped*(gate*movement)[:,None]
    carrier=old['carrier']*gate[:,None]
    clicks=np.zeros_like(voices);beeps=np.zeros_like(voices)
    rng=np.random.default_rng(1314)
    for opening,closing in windows:
        for at,release in [(opening,False),(closing-.025,True)]:
            x=click(rng,release);i=round(at*RATE)
            clicks[i:i+len(x)]+=x
            details.append({'kind':'receiver_close_click' if release else 'receiver_open_click',
                            'start_seconds':at,'duration_seconds':len(x)/RATE})
    for start,hz,double in [(31.83,840,False),(59.99,680,True)]:
        x=beep(hz,.09,amplitude=.014,second=double)
        i=round(start*RATE);beeps[i:i+len(x)]+=x
        details.append({'kind':'receiver_acknowledgement','start_seconds':start,
                        'frequency_hz':hz,'double':double,'duration_seconds':len(x)/RATE})
    stems={'static':static.astype(np.float32),'carrier':carrier.astype(np.float32),
           'transmissions':voices,'beeps':beeps,'clicks':clicks}
    full=sum(stems.values())
    # Click tails may run up to45ms beyond the gate's exact close; allow them
    # for the silence audit while requiring the rest of each gap to be zero.
    active=np.zeros(n,dtype=bool)
    for opening,closing in windows:
        active[round(opening*RATE):round((closing+.06)*RATE)]=True
    if float(np.abs(full[~active]).max())>1e-8:
        raise ValueError('The receiver leaked into an intended silent gap.')
    for item in details:
        if item.get('copied_voice_maximum_error',0)>1e-8:
            raise ValueError('Accepted voice character changed.')
    recipe={'revision':'v4 sparse receiver: three original v3 transmissions, gated static/carrier, six clicks, two acknowledgements',
            'sample_rate':RATE,'seconds':seconds,'events':sorted(details,key=lambda x:x['start_seconds']),
            'receiver_windows_seconds':windows,'silent_fraction':float((~active).mean()),
            'maximum_signal_in_silent_regions':float(np.abs(full[~active]).max()),
            'preserved_voice_gain':True,'global_source_normalization':False,
            'source_parent':str(parent.resolve()),'source_recipe_sha256':hashlib.sha256((parent/'recipe.json').read_bytes()).hexdigest(),
            'influence':'User-described radio texture, dark noise and slow carrier movement. No reference recording is used and reference beep identity was never confirmed.',
            'assistant_listening':False}
    return stems,recipe,r


def run(parent,music,out):
    if out.exists() and any(out.iterdir()):raise ValueError('Use a fresh output directory.')
    out.mkdir(parents=True,exist_ok=True)
    stems,recipe,parent_record=build(parent);full=sum(stems.values());checks=[]
    for name,samples in [*stems.items(),('receiver-gated',full)]:
        path=out/f'{name}.wav';write_audio(samples,path,'pcm_s24le')
        checks.append(check_audio(path,recipe['seconds']))
    for name,samples in [('receiver-gated',full),('receiver-gated-three-repeat-review',np.tile(full,(3,1)))]:
        path=out/f'{name}.mp3';write_audio(samples,path,'libmp3lame')
        checks.append(check_audio(path,len(samples)/RATE))
    bed=decode(music,start=90,seconds=recipe['seconds'])
    if len(bed)!=len(full):raise ValueError('Music excerpt is incomplete.')
    fade=np.minimum(1.,np.minimum(np.arange(len(bed)),np.arange(len(bed)-1,-1,-1))/RATE)
    parent_gains={x['file']:x['effect_gain'] for x in parent_record['auditions']}
    auditions=[]
    for name,parent_name in [('music-only','music-only.mp3'),('music-gated-quiet','music-comms-quiet.mp3'),('music-gated-clearer','music-comms-clearer.mp3')]:
        # Preserve the previous per-event source gain, instead of making the
        # remaining voices louder to compensate for fewer events.
        effect_gain=parent_gains[parent_name]
        samples=(bed+full*effect_gain)*fade[:,None]
        wav=out/f'{name}-prematch.wav';write_audio(samples,wav,'pcm_s24le')
        meter=out/f'{name}-meter';meter.mkdir()
        before=loudness(wav,imageio_ffmpeg.get_ffmpeg_exe(),meter);gain_db=-23-before['integrated_lufs'];history=[]
        for attempt in range(3):
            path=out/f'{name}-pass-{attempt+1}.mp3'
            write_audio(samples*10**(gain_db/20),path,'libmp3lame')
            folder=meter/f'pass-{attempt+1}';folder.mkdir()
            after=loudness(path,imageio_ffmpeg.get_ffmpeg_exe(),folder)
            history.append({'gain_db':gain_db,'measurements':after})
            if abs(after['integrated_lufs']+23)<=.15:break
            gain_db+=-23-after['integrated_lufs']
        if abs(after['integrated_lufs']+23)>.2:raise ValueError('Loudness matching failed.')
        final=out/f'{name}.mp3'
        with final.open('xb') as dest:dest.write(path.read_bytes())
        checks.append(check_audio(final,recipe['seconds']))
        auditions.append({'file':final.name,'effect_source_gain':effect_gain,'same_source_gain_as_v3':True,
                           'matching_passes':history,'measured':after})
    recipe.update({'outputs':checks,'auditions':auditions,
                   'music':{'path':str(music.resolve()),'sha256':hashlib.sha256(music.read_bytes()).hexdigest(),
                            'start_seconds':90,'seconds':recipe['seconds'],'master_modified':False},
                   'renderer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   'circular_join_step':float(np.abs(full[0]-full[-1]).max())})
    (out/'recipe.json').write_text(json.dumps(recipe,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'output':str(out.resolve()),'files_checked':len(checks),
                      'silent_fraction':recipe['silent_fraction'],'silence_peak':recipe['maximum_signal_in_silent_regions'],
                      'levels':[(x['file'],x['measured']['integrated_lufs']) for x in auditions]},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--parent',type=Path,required=True);p.add_argument('--music',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();run(a.parent,a.music,a.out)
