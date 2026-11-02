"""Original procedural receiver textures and optional music auditions.

Seeded filtered noise, a slow carrier and gated resonant noise; no recorded
radio, speech, franchise audio, external model or paid service is used.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np

from analyze_ambient_audio import loudness

RATE = 48000


def rms(x):
    return float(np.sqrt(np.mean(np.asarray(x, dtype=float)**2)))


def noise(rng, n, rate, low, high):
    """One periodic, band-shaped real-noise period; not a physical RF model."""
    f = np.fft.rfftfreq(n, 1/rate)
    safe = np.maximum(f, .01)
    response = 1/np.sqrt((1+(low/safe)**8)*(1+(safe/high)**8))
    response[0] = 0
    z = np.fft.rfft(rng.normal(size=n)) * response
    x = np.fft.irfft(z, n)
    return x/max(rms(x), 1e-12)


def movement(rng, time, seconds, cycles):
    phase = rng.uniform(0, 2*np.pi, len(cycles))
    x = sum(np.sin(2*np.pi*k*time/seconds+p)/np.sqrt(k)
            for k, p in zip(cycles, phase))
    return x/max(float(np.max(np.abs(x))), 1e-12)


def speaker(x, rate):
    # Near-mono receiver with modest unequal room taps; no wide weather bed.
    left = .77*x + .055*np.roll(x, round(.031*rate))
    right = .64*x + .045*np.roll(x, round(.047*rate))
    return np.column_stack([left, right])


def make_receiver(seconds=67, seed=1302, rate=RATE):
    n = round(seconds*rate)
    if seconds < 8 or n/rate != seconds:
        raise ValueError('Use at least eight seconds and an integer sample count.')
    rng = np.random.default_rng(seed)
    time = np.arange(n)/rate
    air = noise(rng, n, rate, 180, 3100)
    air *= .72+.25*movement(rng, time, seconds, [1, 3, 7, 11])
    static = speaker(air, rate)
    static *= .055/max(rms(static), 1e-12)

    # The mean frequency completes an integer number of cycles. Frequency and
    # level controls are independent and close on this full period.
    centre = round(620*seconds)/seconds
    frequency = centre+75*movement(rng, time, seconds, [1, 2, 5])
    frequency -= frequency.mean()-centre
    phase = 2*np.pi*np.r_[0, np.cumsum(frequency[:-1])]/rate
    amplitude = .12+.88*((movement(rng, time, seconds, [2, 3, 8])+1)/2)**2
    carrier = speaker(np.sin(phase)*amplitude, rate)
    carrier *= rms(static)*.16/max(rms(carrier), 1e-12)

    # Speech-like modulation of noise, not speech synthesis or a voice sample.
    activity = np.zeros(n)
    events = []
    for fraction, duration in [(0.10, 4.8), (.34, 5.5), (.63, 4.1), (.84, 3.8)]:
        start = seconds*fraction
        duration = min(duration, seconds-start-.5)
        if duration <= 0:
            continue
        q = (time-start)/duration
        gate = np.where((q>0)&(q<1), np.sin(np.pi*np.clip(q, 0, 1))**2, 0)
        syllables = np.maximum(0., movement(rng, time, seconds,
                              [max(1, round(seconds*k)) for k in [2.3, 3.7, 4.9]])+.25)**1.6
        bands = [(280, 650), (750, 1250), (1500, 2400)]
        burst = sum(noise(rng, n, rate, low, high)*weight
                    for (low, high), weight in zip(bands, [.9, .6, .23]))
        activity += burst*gate*syllables
        events.append({'start_seconds': start, 'duration_seconds': duration})
    activity = speaker(activity, rate)
    activity *= rms(static)*.27/max(rms(activity), 1e-12)
    stems = {'static': static.astype(np.float32), 'carrier': carrier.astype(np.float32),
             'nonverbal-activity': activity.astype(np.float32)}
    info = {'seconds': seconds, 'sample_rate': rate, 'seed': seed,
            'static_rms_dbfs': 20*np.log10(rms(stems['static'])),
            'static_nominal_band_hz': [180, 3100], 'carrier_centre_hz': centre,
            'carrier_min_max_hz': [float(frequency.min()), float(frequency.max())],
            'carrier_cycle_closure_error': abs(float(frequency.sum()/rate)-round(float(frequency.sum()/rate))),
            'carrier_to_static_rms_db': 20*np.log10(.16),
            'activity_to_static_rms_db': 20*np.log10(.27),
            'activity_events': events,
            'activity_type': 'gated resonant noise; no actual words, recording or voice model',
            'speaker': 'near-mono with unequal31/47ms circular room taps',
            'loop_scope': 'One generated full67-second period by default. Periodic construction is not an artistic seam verdict or a claim of non-repetition.'}
    return stems, info


def write_audio(audio, path, codec):
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-f', 'f32le',
                    '-ar', str(RATE), '-ac', '2', '-i', 'pipe:0', '-c:a', codec,
                    *(['-b:a', '192k'] if codec=='libmp3lame' else []), '-n', str(path)],
                   input=audio.astype('<f4').tobytes(), capture_output=True, check=True)


def check_audio(path, seconds):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    raw = subprocess.check_output([ffmpeg, '-v', 'error', '-i', str(path), '-ar', str(RATE),
                                   '-ac', '2', '-f', 'f32le', 'pipe:1'])
    x = np.frombuffer(raw, '<f4').reshape(-1, 2)
    peak = float(np.abs(x).max())
    if not np.isfinite(x).all() or peak >= 1 or abs(len(x)/RATE-seconds) > .001:
        raise ValueError(f'Invalid encoded audio: {path}')
    return {'file': path.name, 'seconds': len(x)/RATE, 'sample_peak': peak,
            'finite': True, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def run(out, seconds, seed, music=None, music_start=90):
    if out.exists() and any(out.iterdir()):
        raise ValueError('Use a new or empty output directory.')
    out.mkdir(parents=True, exist_ok=True)
    stems, recipe = make_receiver(seconds, seed)
    checks = []
    for name, samples in stems.items():
        path = out/f'{name}.wav'
        write_audio(samples, path, 'pcm_s24le')
        checks.append(check_audio(path, seconds))
    idle = stems['static']+stems['carrier']
    full = idle+stems['nonverbal-activity']
    for name, samples in [('receiver-idle', idle), ('receiver-with-activity', full)]:
        path = out/f'{name}.mp3'
        write_audio(samples, path, 'libmp3lame')
        checks.append(check_audio(path, seconds))
    master = out/'receiver-with-activity.wav'
    write_audio(full, master, 'pcm_s24le')
    checks.append(check_audio(master, seconds))
    repeated = out/'receiver-three-repeat-review.mp3'
    write_audio(np.tile(full, (3, 1)), repeated, 'libmp3lame')
    checks.append(check_audio(repeated, seconds*3))
    recipe['circular_join_step'] = float(np.abs(full[0]-full[-1]).max())
    recipe['ordinary_step_p99'] = float(np.percentile(np.abs(np.diff(full, axis=0)), 99))
    recipe['assistant_listening'] = False
    recipe['software'] = {'numpy': np.__version__}
    auditions = []
    if music:
        length = min(60, seconds)
        raw = subprocess.check_output([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-i', str(music),
                                       '-ss', str(music_start), '-t', str(length), '-ar', str(RATE),
                                       '-ac', '2', '-f', 'f32le', 'pipe:1'])
        bed = np.frombuffer(raw, '<f4').reshape(-1, 2).copy()
        if len(bed) != round(length*RATE):
            raise ValueError('Music window is shorter than requested.')
        effect = full[:len(bed)]
        fades = np.minimum(1., np.minimum(np.arange(len(bed)), np.arange(len(bed)-1, -1, -1))/RATE)
        for name, relative in [('music-only', None), ('music-radio-quiet', -20), ('music-radio-clearer', -14)]:
            gain = 0. if relative is None else rms(bed)*10**(relative/20)/rms(effect)
            samples = (bed+effect*gain)*fades[:, None]
            intermediate = out/f'{name}-prematch.wav'
            write_audio(samples, intermediate, 'pcm_s24le')
            meter_dir = out/f'{name}-measurements'
            meter_dir.mkdir()
            before = loudness(intermediate, imageio_ffmpeg.get_ffmpeg_exe(), meter_dir)
            match_db = -23-before['integrated_lufs']
            history = []
            for attempt in range(3):
                candidate = out/f'{name}-match-pass-{attempt+1}.mp3'
                write_audio(samples*10**(match_db/20), candidate, 'libmp3lame')
                pass_dir = meter_dir/f'pass-{attempt+1}'
                pass_dir.mkdir()
                after = loudness(candidate, imageio_ffmpeg.get_ffmpeg_exe(), pass_dir)
                history.append({'gain_db': match_db, 'measured': after})
                if abs(after['integrated_lufs']+23) <= .15:
                    break
                match_db += -23-after['integrated_lufs']
            if abs(after['integrated_lufs']+23)>.2:
                raise ValueError('Audition did not reach matched loudness.')
            path = out/f'{name}.mp3'
            # Preserve encoded pass files and deliver the verified final bytes.
            with path.open('xb') as dest:
                dest.write(candidate.read_bytes())
            checks.append(check_audio(path, length))
            auditions.append({'file': path.name, 'effect_to_music_rms_db_before_matching': relative,
                              'effect_source_gain': gain, 'whole_mix_matching_gain_db': match_db,
                              'matching_passes': history, 'measured': after})
        recipe['music'] = {'source': str(music.resolve()), 'sha256': hashlib.sha256(music.read_bytes()).hexdigest(),
                           'start_seconds': music_start, 'seconds': length,
                           'review_only_fades_seconds': 1, 'target_audition_lufs': -23,
                           'approved_master_modified': False}
    recipe['auditions'] = auditions
    recipe['outputs'] = checks
    recipe['generator_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (out/'recipe.json').write_text(json.dumps(recipe, indent=2, allow_nan=False)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'output': str(out.resolve()), 'files_checked': len(checks), 'auditions': auditions,
                      'loop_join_step': recipe['circular_join_step'], 'ordinary_step_p99': recipe['ordinary_step_p99']}, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--seconds', type=float, default=67)
    p.add_argument('--seed', type=int, default=1302)
    p.add_argument('--music', type=Path)
    p.add_argument('--music-start', type=float, default=90)
    args = p.parse_args()
    run(args.out, args.seconds, args.seed, args.music, args.music_start)
