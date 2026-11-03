"""One540-second radio score: unique phrases and independently made packets.

No67-second source loop is tiled. Existing music and radio event gain are
preserved; full-session playback still needs user listening review.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np

from generate_polar_comms import decode, radio_voice, beep
from generate_receiver_texture import RATE, rms, noise, speaker, write_audio
from refine_receiver_events import click
from analyze_ambient_audio import loudness


def schedule(durations, seed=13540, total=540):
    rng=np.random.default_rng(seed)
    count=len(durations)
    order=rng.permutation(count).tolist()
    head=23.4;tail=26.
    spare=total-head-tail-sum(durations)-1.3*count
    if spare<15*(count-1):raise ValueError('Too many packets for the session.')
    weights=rng.uniform(.3,1.6,count-1)**1.3
    weights[rng.integers(count-1)]=3.6
    gaps=15+(spare-15*(count-1))*weights/weights.sum()
    events=[];cursor=head
    for position,index in enumerate(order):
        events.append({'voice_index':index,'open_seconds':float(cursor),
                       'lead_seconds':float(rng.uniform(.22,.52)),
                       'voice_seconds':float(durations[index]),
                       'tail_seconds':float(rng.uniform(.22,.48))})
        cursor+=durations[index]+1.3
        if position<len(gaps):cursor+=gaps[position]
    return events


def validate_audio(path,seconds):
    process=subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(path),
        '-ar',str(RATE),'-ac','2','-f','f32le','pipe:1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    frames=0;peak=0.;finite=True
    while True:
        raw=process.stdout.read(8*65536)
        if not raw:break
        x=np.frombuffer(raw,'<f4');frames+=x.size//2
        peak=max(peak,float(np.abs(x).max()));finite=finite and bool(np.isfinite(x).all())
    error=process.stderr.read();code=process.wait()
    if code or frames!=round(seconds*RATE) or not finite or peak>=1:
        raise ValueError(f'Audio validation failed: {path}, {frames}, {peak}, {error}')
    return {'file':path.name,'seconds':frames/RATE,'finite':finite,'sample_peak':peak,
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}


def mix_files(music,radio,target,gain):
    graph=f'[1:a]volume={gain:.15g}[r];[0:a][r]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[a]'
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(music),'-i',str(radio),
        '-filter_complex',graph,'-map','[a]','-ar',str(RATE),'-ac','2','-c:a','flac',
        '-sample_fmt','s32','-bits_per_raw_sample','24','-n',str(target)],capture_output=True,check=True)


def listening_copy(source,target,out):
    meter=out/'full-mix-meter';meter.mkdir()
    measured=loudness(source,imageio_ffmpeg.get_ffmpeg_exe(),meter)
    gain=-23-measured['integrated_lufs'];history=[]
    for attempt in range(3):
        candidate=out/f'full-mix-listening-pass-{attempt+1}.mp3'
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(source),
            '-af',f'volume={gain:.15g}dB','-c:a','libmp3lame','-b:a','192k','-n',str(candidate)],capture_output=True,check=True)
        folder=meter/f'pass-{attempt+1}';folder.mkdir()
        actual=loudness(candidate,imageio_ffmpeg.get_ffmpeg_exe(),folder)
        history.append({'gain_db':gain,'measured':actual})
        if abs(actual['integrated_lufs']+23)<=.15:break
        gain+=-23-actual['integrated_lufs']
    if abs(actual['integrated_lufs']+23)>.2:raise ValueError('Listening-copy loudness mismatch.')
    with target.open('xb') as dest:dest.write(candidate.read_bytes())
    return {'lossless_mix':measured,'listening_copy':actual,'matching_passes':history}


def run(voices,music,parent,out):
    if out.exists() and any(out.iterdir()):raise ValueError('Use a fresh output directory.')
    expected='987b1509075da8a9202f24a6b765f4e2b6d88d90cb90c28bdaf8719af77b252b'
    if hashlib.sha256(music.read_bytes()).hexdigest()!=expected:raise ValueError('Approved music hash mismatch.')
    out.mkdir(parents=True,exist_ok=True);(out/'packets').mkdir()
    v3=json.loads((parent/'recipe.json').read_text(encoding='utf-8'))
    source_gain=next(x['effect_gain'] for x in v3['auditions'] if x['file']=='music-comms-clearer.mp3')
    record=json.loads((voices/'voice-sources.json').read_text(encoding='utf-8-sig'))
    sources=record['sources']
    if len(sources)!=14 or len({x['sha256'] for x in sources})!=14:
        raise ValueError('Expected14 different source phrases.')
    rng=np.random.default_rng(13541)
    packets=[]
    print('Processing14 distinct voice packets...',flush=True)
    for index,item in enumerate(sources):
        path=voices/item['file']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:raise ValueError('Voice source changed.')
        x=radio_voice(decode(path,mono=True),index,rng)*v3['common_design_gain']
        packets.append(x.astype(np.float32))
    planned=schedule([len(x)/RATE for x in packets])
    radio=np.zeros((540*RATE,2),dtype=np.float32)
    activity=np.zeros(540*RATE,dtype=bool)
    acknowledgement_positions=set(np.random.default_rng(13542).choice(len(planned),5,replace=False).tolist())
    events=[]
    print('Scoring independent receiver events across9 minutes...',flush=True)
    for position,event in enumerate(planned):
        index=event['voice_index'];voice=packets[index]
        lead=event['lead_seconds'];tail=event['tail_seconds']
        duration=lead+len(voice)/RATE+tail
        n=round(duration*RATE);t=np.arange(n)/RATE
        gate=np.minimum(1.,np.minimum(np.arange(n),np.arange(n-1,-1,-1))/(RATE*.018))
        h=noise(rng,n,RATE,float(rng.uniform(220,360)),float(rng.uniform(2200,3000)))
        h*=.010*(.70+.25*np.sin(2*np.pi*t/rng.uniform(2.7,6.3)+rng.uniform(0,6)))
        static=speaker(h,RATE)*gate[:,None]
        frequency=620+rng.uniform(25,65)*np.sin(2*np.pi*t/rng.uniform(6,13)+rng.uniform(0,6))
        phase=2*np.pi*np.cumsum(frequency)/RATE
        carrier=speaker(np.sin(phase)*(.006+.004*np.sin(2*np.pi*t/7+rng.uniform(0,6))),RATE)*gate[:,None]
        packet=(static+carrier).astype(np.float32)
        voice_at=round(lead*RATE);packet[voice_at:voice_at+len(voice)]+=voice
        # Close the gate before the physical release-click tail.
        packet=np.pad(packet,((0,round(.08*RATE)),(0,0)))
        opening=click(rng);closing=click(rng,True)
        packet[:len(opening)]+=opening
        end_at=n-round(.025*RATE);packet[end_at:end_at+len(closing)]+=closing
        ack=None
        if position in acknowledgement_positions:
            hz=int(rng.choice([680,840,1020]));double=bool(rng.integers(2))
            b=beep(hz,float(rng.uniform(.07,.10)),second=double)
            offset=max(0,n-len(b)-round(.05*RATE))
            packet[offset:offset+len(b)]+=b
            ack={'frequency_hz':hz,'double':double,'offset_seconds':offset/RATE}
        start=round(event['open_seconds']*RATE)
        if start+len(packet)>=len(radio):raise ValueError('Packet overruns the guarded session.')
        radio[start:start+len(packet)]+=packet;activity[start:start+len(packet)]=True
        filename=f'packet-{position+1:02d}.wav'
        write_audio(packet,out/'packets'/filename,'pcm_s24le')
        events.append({**event,'voice_start_seconds':event['open_seconds']+lead,
            'close_seconds':event['open_seconds']+len(packet)/RATE,
            'source_file':sources[index]['file'],'source_sha256':sources[index]['sha256'],
            'packet_file':'packets/'+filename,'packet_sha256':hashlib.sha256((out/'packets'/filename).read_bytes()).hexdigest(),
            'acknowledgement':ack})
    assert len({x['source_sha256'] for x in events})==14
    assert not np.any(radio[~activity])
    radio_path=out/'Snowline-radio-score-9min-v1.flac'
    write_audio(radio,radio_path,'flac')
    radio_peak=float(np.abs(radio).max());silent_fraction=float((~activity).mean())
    del radio
    checks=[validate_audio(radio_path,540)]
    mix_path=out/'Snowline-music-and-radio-9min-v1.flac'
    print('Mixing with the unchanged approved music...',flush=True)
    mix_files(music,radio_path,mix_path,source_gain)
    checks.append(validate_audio(mix_path,540))
    listening=out/'Snowline-music-and-radio-9min-v1.mp3'
    metering=listening_copy(mix_path,listening,out)
    checks.append(validate_audio(listening,540))
    if hashlib.sha256(music.read_bytes()).hexdigest()!=expected:raise ValueError('Music was altered.')
    gaps=[events[i+1]['open_seconds']-events[i]['close_seconds'] for i in range(len(events)-1)]
    recipe={'date':'2026-11-02','seconds':540,'sample_rate':RATE,'seed':13540,
        'music':{'path':str(music.resolve()),'sha256':expected,'lossless_mix_music_gain':1.,'master_modified':False},
        'radio_source_gain':source_gain,'same_gain_as_v4_clearer_before_whole_mix_matching':True,
        'voice_processing':'Same radio_voice chain and design gain as v3/v4;14 distinct phonetic source recordings used once each.',
        'voice_sources':record,'events':events,'silent_fraction':silent_fraction,'radio_sample_peak':radio_peak,
        'quiet_gap_min_max_seconds':[min(gaps),max(gaps)],'quiet_gap_std_seconds':float(np.std(gaps)),
        'short_loop_tiled':False,'opening_or_closing_fade_added':False,'new_music_generated':False,
        'acknowledgement_events':len(acknowledgement_positions),'metering':metering,'outputs':checks,
        'assistant_listening':False,'user_full_session_review':'pending',
        'scope':'A single9-minute radio arrangement. Future repetition of this whole arrangement repeats its events; this is not an infinitely unique radio generator.',
        'implementation':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in
            [Path(__file__),Path(__file__).with_name('generate_polar_comms.py'),Path(__file__).with_name('refine_receiver_events.py'),Path(__file__).with_name('extend_receiver_voices.ps1')]]}
    (out/'recipe.json').write_text(json.dumps(recipe,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    lines=['Snowline: nine-minute radio cue sheet','Times refer to the complete approved music.','']
    for e in events:
        time=e['voice_start_seconds'];lines.append(f'{int(time//60)}:{time%60:05.2f}  {e["source_file"]}  {e["voice_seconds"]:.2f}s'+('  acknowledgement' if e['acknowledgement'] else ''))
    (out/'cue-sheet.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(out.resolve()),'transmissions':len(events),'unique_phrases':14,
        'silent_fraction':silent_fraction,'quiet_gap_min_max_seconds':recipe['quiet_gap_min_max_seconds'],
        'listening_lufs':metering['listening_copy']['integrated_lufs'],'checked_files':len(checks)},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--voices',type=Path,required=True);p.add_argument('--music',type=Path,required=True)
    p.add_argument('--parent',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();run(a.voices,a.music,a.parent,a.out)
