"""Polar receiver revision: local synthetic voices, less hiss, irregular beeps.

Uses original phonetic phrases rendered by installed Windows voices. No film,
reference-track or recorded human audio is used for the effect.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from scipy import signal

from generate_receiver_texture import RATE, rms, speaker, write_audio, check_audio
from analyze_ambient_audio import loudness


def decode(path, mono=False, start=None, seconds=None):
    args = [imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-i', str(path)]
    if start is not None:
        args += ['-ss', str(start), '-t', str(seconds)]
    channels = 1 if mono else 2
    raw = subprocess.check_output(args+['-ar', str(RATE), '-ac', str(channels), '-f', 'f32le', 'pipe:1'])
    x = np.frombuffer(raw, '<f4').reshape(-1, channels).copy()
    if not len(x) or not np.isfinite(x).all():
        raise ValueError(f'Invalid source: {path}')
    return x[:, 0] if mono else x


def radio_voice(x, index, rng):
    voiced = np.flatnonzero(np.abs(x)>.002)
    if not len(voiced):
        raise ValueError('Silent synthetic voice source.')
    x = x[max(0, voiced[0]-240):min(len(x), voiced[-1]+1200)]
    high = 2300 if index%2 else 2700
    x = signal.sosfiltfilt(signal.butter(4, [330, high], fs=RATE,
                          btype='bandpass', output='sos'), x)
    x /= max(rms(x), 1e-12)
    # Mild saturation/low resolution and irregular losses remove clean TTS
    # presentation. This is an equipment effect, not a voice impersonation.
    x = np.tanh(x*.8)
    x = signal.resample_poly(signal.resample_poly(x, 1, 4), 4, 1)[:len(x)]
    x = np.round(x*384)/384
    time = np.arange(len(x))/RATE
    envelope = .81+.13*np.sin(2*np.pi*.83*time+rng.uniform(0, 6))
    for _ in range(5):
        centre = rng.uniform(.2, max(.21, len(x)/RATE-.1))
        envelope *= 1-.75*np.exp(-.5*((time-centre)/rng.uniform(.009, .027))**2)
    fade = np.minimum(1., np.minimum(np.arange(len(x)), np.arange(len(x)-1, -1, -1))/(RATE*.07))
    x *= envelope*fade
    x *= (.043 if index%2 else .052)/max(rms(x), 1e-12)
    return speaker(x, RATE).astype(np.float32)


def beep(hz, duration, amplitude=.014, second=False):
    def pulse(frequency, length, level):
        n = round(length*RATE)
        t = np.arange(n)/RATE
        edge = np.minimum(1., np.minimum(t, (n-1)/RATE-t)/.018)
        edge = .5-.5*np.cos(np.pi*np.clip(edge, 0, 1))
        return (np.sin(2*np.pi*frequency*t)+.06*np.sin(4*np.pi*frequency*t))*edge*level
    wave = pulse(hz, duration, amplitude)
    if second:
        gap = np.zeros(round(.055*RATE))
        wave = np.r_[wave, gap, pulse(hz*1.22, duration*.8, amplitude*.8)]
    return speaker(wave, RATE).astype(np.float32)


def make_comms(base, voices, seed=1313):
    rng = np.random.default_rng(seed)
    hiss = decode(base/'static.wav')*.16
    carrier = decode(base/'carrier.wav')*.42
    n = len(hiss)
    seconds = n/RATE
    transmissions = np.zeros_like(hiss)
    beeps = np.zeros_like(hiss)
    events = []
    source_record = json.loads((voices/'voice-sources.json').read_text(encoding='utf-8-sig'))
    for index, (item, start) in enumerate(zip(source_record['sources'], [4.4, 14.0, 24.7, 35.8, 46.2, 56.4])):
        path = voices/item['file']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:
            raise ValueError(f'Voice source hash changed: {path}')
        x = radio_voice(decode(path, mono=True), index, rng)
        at = round(start*RATE)
        x = x[:min(len(x), n-at-round(RATE))]
        if not len(x):
            continue
        transmissions[at:at+len(x)] += x
        # Short, restrained squelch detail tied to the receiver opening/closing.
        for edge_start in [at, at+len(x)]:
            end = min(n, edge_start+round(.16*RATE))
            gate = np.sin(np.linspace(0, np.pi, end-edge_start))**2
            hiss[edge_start:end] *= 1+.25*gate[:, None]
        events.append({'kind': 'transmission', 'source': item['file'], 'voice': item['voice'],
                       'start_seconds': start, 'duration_seconds': len(x)/RATE})
    starts = []
    while len(starts)<5:
        candidate = float(rng.uniform(1.5, seconds-2))
        if all(abs(candidate-x)>7 for x in starts):
            starts.append(candidate)
    for index, start in enumerate(sorted(starts)):
        hz = float(rng.choice([680, 840, 1020]))
        duration = float(rng.uniform(.065, .115))
        x = beep(hz, duration, second=index in [1, 4])
        at = round(start*RATE)
        beeps[at:at+len(x)] += x
        events.append({'kind': 'acknowledgement', 'start_seconds': start, 'frequency_hz': hz,
                       'duration_seconds': len(x)/RATE, 'double': index in [1, 4]})
    stems = {'static': hiss, 'carrier': carrier, 'transmissions': transmissions, 'beeps': beeps}
    gain = .045/max(rms(sum(stems.values())), 1e-12)
    stems = {k:(v*gain).astype(np.float32) for k, v in stems.items()}
    recipe = {'seed': seed, 'seconds': seconds, 'sample_rate': RATE,
              'revision': 'less static; speech cadence from local synthetic phonetic phrases; irregular soft equipment beeps',
              'hiss_gain_relative_to_initial_stem_before_overall_gain': .16,
              'carrier_gain_relative_to_initial_stem_before_overall_gain': .42,
              'common_design_gain': gain, 'events': sorted(events, key=lambda e:e['start_seconds']),
              'voice_provenance': source_record,
              'notes': ['Original effect: no extracted reference/franchise audio or cloned voice.',
                        'Invented phonetic text avoids meaningful dialogue; perceived intelligibility/realism still needs listening.',
                        'Reference influence is the user-described static/activity/slow-tone relationship and measured dark spectral character, not a verified replica.',
                        'No assistant listening verdict or AAA-quality certification.'],
              'source_files': [{'path':str(p.resolve()), 'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
                               for p in [base/'static.wav', base/'carrier.wav', voices/'voice-sources.json']]}
    return stems, recipe


def run(base, voices, music, out):
    if out.exists() and any(out.iterdir()):
        raise ValueError('Use a new/empty output directory.')
    out.mkdir(parents=True, exist_ok=True)
    stems, recipe = make_comms(base, voices)
    full = sum(stems.values())
    checks = []
    for name, samples in [*stems.items(), ('receiver-comms', full)]:
        path = out/f'{name}.wav'
        write_audio(samples, path, 'pcm_s24le')
        checks.append(check_audio(path, recipe['seconds']))
    for name, samples in [('receiver-comms', full), ('chatter-and-beeps', stems['transmissions']+stems['beeps'])]:
        path = out/f'{name}.mp3'
        write_audio(samples, path, 'libmp3lame')
        checks.append(check_audio(path, recipe['seconds']))
    repeat = out/'receiver-comms-three-repeat-review.mp3'
    write_audio(np.tile(full, (3, 1)), repeat, 'libmp3lame')
    checks.append(check_audio(repeat, recipe['seconds']*3))
    music_audio = decode(music, start=90, seconds=60)
    if len(music_audio)!=60*RATE:
        raise ValueError('Music excerpt is incomplete.')
    effect = full[:len(music_audio)]
    fade = np.minimum(1., np.minimum(np.arange(len(effect)), np.arange(len(effect)-1, -1, -1))/RATE)
    auditions = []
    for name, relative in [('music-only', None), ('music-comms-quiet', -20), ('music-comms-clearer', -14)]:
        effect_gain = 0. if relative is None else rms(music_audio)/rms(effect)*10**(relative/20)
        samples = (music_audio+effect_gain*effect)*fade[:, None]
        wav = out/f'{name}-prematch.wav'
        write_audio(samples, wav, 'pcm_s24le')
        meter = out/f'{name}-meter'
        meter.mkdir()
        before = loudness(wav, imageio_ffmpeg.get_ffmpeg_exe(), meter)
        gain_db = -23-before['integrated_lufs']
        history = []
        for attempt in range(3):
            path = out/f'{name}-pass-{attempt+1}.mp3'
            write_audio(samples*10**(gain_db/20), path, 'libmp3lame')
            folder = meter/f'pass-{attempt+1}'
            folder.mkdir()
            after = loudness(path, imageio_ffmpeg.get_ffmpeg_exe(), folder)
            history.append({'gain_db': gain_db, 'measurements': after})
            if abs(after['integrated_lufs']+23)<=.15:
                break
            gain_db += -23-after['integrated_lufs']
        if abs(after['integrated_lufs']+23)>.2:
            raise ValueError('Loudness matching failed.')
        final = out/f'{name}.mp3'
        with final.open('xb') as dest:
            dest.write(path.read_bytes())
        checks.append(check_audio(final, 60))
        auditions.append({'file':final.name, 'relative_effect_rms_db':relative,
                          'effect_gain':effect_gain, 'matching_passes':history, 'measured':after})
    recipe.update({'outputs':checks, 'auditions':auditions,
                   'music':{'path':str(music.resolve()),'sha256':hashlib.sha256(music.read_bytes()).hexdigest(),
                            'excerpt_start_seconds':90,'excerpt_seconds':60,'approved_master_modified':False},
                   'circular_join_step':float(np.abs(full[0]-full[-1]).max()),
                   'ordinary_step_p99':float(np.percentile(np.abs(np.diff(full, axis=0)), 99)),
                   'implementation':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
                                      for p in [Path(__file__),Path(__file__).with_name('generate_receiver_texture.py'),Path(__file__).with_name('make_receiver_voices.ps1')]]})
    (out/'recipe.json').write_text(json.dumps(recipe, indent=2, allow_nan=False)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'output':str(out.resolve()),'files_checked':len(checks),
                      'audition_levels':[(x['file'],x['measured']['integrated_lufs']) for x in auditions],
                      'events':recipe['events'],'join_step':recipe['circular_join_step'],
                      'ordinary_step_p99':recipe['ordinary_step_p99']},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base',type=Path,required=True)
    p.add_argument('--voices',type=Path,required=True)
    p.add_argument('--music',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    run(a.base,a.voices,a.music,a.out)
