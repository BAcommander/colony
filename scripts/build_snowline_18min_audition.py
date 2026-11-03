"""18-minute Snowline trial: sparse radio and more frequent, stronger wind crests."""
import argparse
import json
import math
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from scipy import signal

from analyze_ambient_audio import loudness
from audition_snowline_supplied_creak import sha
from build_snowline_environment import event_envelope
from build_snowline_radio_session import validate_audio
from generate_polar_comms import decode
from generate_receiver_texture import RATE, rms, write_audio
from render_snowline_wind_and_creaks import overlapping_sections, mix

SECONDS = 1080
# New full-session timing; not a repeated nine-minute SFX schedule.
WIND = [(15, 65, 12, 17), (107, 58, 10, 16), (188, 72, 14, 19),
        (288, 61, 11, 17), (374, 68, 13, 18), (473, 57, 10, 16),
        (554, 72, 14, 19), (652, 64, 12, 18), (738, 69, 13, 18),
        (837, 58, 11, 17), (920, 74, 14, 20), (1018, 49, 10, 15)]
VOICE_TIMES = [47, 205, 354, 522, 659, 835, 987]
PACKET_INDICES = [9, 0, 6, 12, 13, 2, 8]  # Seven different existing packets, two acknowledgements.
CREAK_TIMES = [91, 338, 704, 1007]


def repeat_twice(source, target):
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-stream_loop', '1',
                    '-i', str(source), '-t', str(SECONDS), '-ar', str(RATE), '-ac', '2',
                    '-c:a', 'flac', '-sample_fmt', 's32', '-bits_per_raw_sample', '24',
                    '-n', str(target)], capture_output=True, check=True)


def pcm(path):
    p = subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-i', str(path),
                          '-ar', str(RATE), '-ac', '2', '-f', 'f32le', 'pipe:1'],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        while True:
            raw = p.stdout.read(65536 * 8)
            if not raw:
                break
            yield np.frombuffer(raw, '<f4').reshape(-1, 2)
        error = p.stderr.read()
        if p.wait():
            raise ValueError(error.decode(errors='replace'))
    finally:
        if p.poll() is None:
            p.kill()
        p.wait()


def check_repeat(source, extended):
    original = decode(source)
    frames, error = 0, 0.
    for block in pcm(extended):
        index = (frames + np.arange(len(block))) % len(original)
        error = max(error, float(np.max(np.abs(block - original[index]))))
        frames += len(block)
    if frames != SECONDS * RATE or len(original) != 540 * RATE or error != 0:
        raise ValueError(f'Repeat source changed: {frames}, {error}')
    return {'frames': frames, 'exact_two_copies': True, 'max_sample_difference': error}


def peak_multiplier(envelope):
    t = np.clip((envelope - .6) / .4, 0, 1)
    return 1 + .10 * (t * t * (3 - 2 * t))


def check_wind_gain(before, after):
    a, b = pcm(before), pcm(after)
    frames, error, unchanged_error = 0, 0., 0.
    try:
        while True:
            x, y = next(a, None), next(b, None)
            if x is None and y is None:
                break
            if x is None or y is None or len(x) != len(y):
                raise ValueError('Wind duration mismatch')
            multiplier = np.ones(len(x), dtype=np.float64)
            for start, duration, up, down in WIND:
                lo = max(0, start * RATE - frames)
                hi = min(len(x), (start + duration) * RATE - frames)
                if hi > lo:
                    t = (frames + np.arange(lo, hi)) / RATE - start
                    env = np.minimum(np.sin(np.pi / 2 * np.clip(t / up, 0, 1)) ** 2,
                                     np.sin(np.pi / 2 * np.clip((duration - t) / down, 0, 1)) ** 2)
                    multiplier[lo:hi] = peak_multiplier(env)
            error = max(error, float(np.max(np.abs(y.astype(float) - x.astype(float) * multiplier[:, None]))))
            quiet = multiplier == 1
            if np.any(quiet):
                unchanged_error = max(unchanged_error, float(np.max(np.abs(y[quiet] - x[quiet]))))
            frames += len(x)
    finally:
        a.close()
        b.close()
    if frames != SECONDS * RATE or error > 1.5e-7 or unchanged_error != 0:
        raise ValueError(f'Wind crest gain failed: {frames}, {error}, {unchanged_error}')
    return {'frames': frames, 'max_gain_error': error,
            'max_quieter_buildup_difference': unchanged_error, 'max_multiplier': 1.1}


def check_sum(sources, result):
    streams = [pcm(p) for p in sources + [result]]
    frames, error = 0, 0.
    try:
        while True:
            blocks = [next(s, None) for s in streams]
            if all(x is None for x in blocks):
                break
            if any(x is None for x in blocks) or len({len(x) for x in blocks}) != 1:
                raise ValueError('Mix duration mismatch')
            expected = blocks[0].copy()
            for layer in blocks[1:-1]:
                expected += layer
            error = max(error, float(np.max(np.abs(blocks[-1] - expected))))
            frames += len(expected)
    finally:
        for s in streams:
            s.close()
    if frames != SECONDS * RATE or error > 3e-7:
        raise ValueError(f'Mix sum failed: {frames}, {error}')
    return {'frames': frames, 'max_sum_error': error, 'source_gains': [1] * len(sources)}


def check_sparse(path, events):
    frames, outside = 0, 0.
    windows = [(round(e['start_seconds'] * RATE), round(e['end_seconds'] * RATE)) for e in events]
    for block in pcm(path):
        active = np.zeros(len(block), dtype=bool)
        for start, end in windows:
            lo, hi = max(0, start - frames), min(len(block), end - frames)
            if hi > lo:
                active[lo:hi] = True
        if np.any(~active):
            outside = max(outside, float(np.max(np.abs(block[~active]))))
        frames += len(block)
    if frames != SECONDS * RATE or outside != 0:
        raise ValueError('Unexpected effect outside event windows')
    return {'frames': frames, 'max_signal_outside_events': outside}


def run(root, out):
    if out.exists() and any(out.iterdir()):
        raise ValueError('Use a fresh output directory')
    radio_parent = root / 'exports/sfx/snowline-receiver-2026-11-02/full-session-v1'
    wind_parent = root / 'exports/sfx/snowline-receiver-2026-11-02/wind-creak-test-v2'
    creak_parent = root / 'exports/sfx/snowline-creak-2026-11-03/audition-v2'
    r = json.loads((radio_parent / 'recipe.json').read_text(encoding='utf-8'))
    w = json.loads((wind_parent / 'recipe.json').read_text(encoding='utf-8'))
    c = json.loads((creak_parent / 'recipe.json').read_text(encoding='utf-8'))
    music = root / 'exports/restored-snowline-2026-11-02/Below-the-Snowline-paired-loop-9min-v1.flac'
    wind_source = root / 'exports/restored-snowline-2026-11-02/wind-soft-exterior-01.mp3'
    ventilation = root / 'exports/sfx/snowline-receiver-2026-11-02/environment-session-v2/Snowline-ventilation-9min-v2.flac'
    wind_reference = wind_parent / 'Snowline-varied-wind-9min-test.flac'
    creak_source = creak_parent / 'Snowline-supplied-creak-stem-9min-v2.flac'
    required = [(music, r['music']['sha256']),
                (wind_source, '324470a6fa73b57ef021edca2ddd6f4c20a6319bd0148bc2ea0f4f71c8d19a34'),
                (ventilation, '36939090e8896854d9d5c874984912bdba427d3ff5c67799ba260a3a48a2f312'),
                (wind_reference, next(e['sha256'] for e in w['outputs'] if e['file'] == wind_reference.name)),
                (creak_source, next(e['sha256'] for e in c['outputs'] if e['file'] == creak_source.name))]
    for path, expected in required:
        if sha(path) != expected:
            raise ValueError(f'Source hash differs: {path}')
    intervals = np.diff(VOICE_TIMES)
    assert np.all((intervals >= 120) & (intervals <= 180)) and len(set(PACKET_INDICES)) == 7
    gaps = [WIND[i + 1][0] - WIND[i][0] - WIND[i][1] for i in range(len(WIND) - 1)]
    assert min(gaps) >= 20 and max(gaps) <= 35 and WIND[-1][0] + WIND[-1][1] <= SECONDS
    out.mkdir(parents=True, exist_ok=True)
    paths = {k: out / f'Snowline-{k}-18min-v1.flac'
             for k in ['music', 'ventilation', 'radio', 'wind-unlifted', 'wind', 'creaks']}
    print('Extending the unchanged music and ventilation sources...', flush=True)
    repeat_twice(music, paths['music'])
    repeat_twice(ventilation, paths['ventilation'])
    print('Placing seven distinct radio packets at2-3-minute intervals...', flush=True)
    radio = np.zeros((SECONDS * RATE, 2), dtype=np.float32)
    radio_events = []
    for target, index in zip(VOICE_TIMES, PACKET_INDICES):
        old = r['events'][index]
        packet_path = radio_parent / old['packet_file']
        if sha(packet_path) != old['packet_sha256']:
            raise ValueError('Radio packet differs')
        packet = decode(packet_path) * r['radio_source_gain']
        at = round((target - old['lead_seconds']) * RATE)
        radio[at:at + len(packet)] += packet
        radio_events.append({'voice_start_seconds': target, 'start_seconds': at / RATE,
                             'end_seconds': (at + len(packet)) / RATE,
                             'packet_file': str(packet_path.relative_to(root)),
                             'packet_sha256': old['packet_sha256'], 'source_phrase_sha256': old['source_sha256'],
                             'source_gain': r['radio_source_gain'], 'acknowledgement': old['acknowledgement']})
    write_audio(radio, paths['radio'], 'flac')
    del radio
    print('Retaining current creak level at four sparse full-session positions...', flush=True)
    takes = [decode(creak_source, start=t, seconds=4) for t in [91, 338]]
    creaks = np.zeros((SECONDS * RATE, 2), dtype=np.float32)
    creak_events = []
    for i, start in enumerate(CREAK_TIMES):
        take = takes[i % 2]
        at = start * RATE
        creaks[at:at + len(take)] = take
        creak_events.append({'start_seconds': start, 'end_seconds': start + len(take) / RATE,
                             'source_stem_start_seconds': [91, 338][i % 2], 'additional_gain': 1,
                             'same_single_supplied_take_reused': True})
    write_audio(creaks, paths['creaks'], 'flac')
    del creaks, takes
    reference = decode(wind_reference)
    power, count = 0., 0
    for e in w['wind_passages']:
        a = round((e['start_seconds'] + e['fade_in_seconds']) * RATE)
        b = round((e['start_seconds'] + e['duration_seconds'] - e['fade_out_seconds']) * RATE)
        power += float(np.sum(reference[a:b].astype(float) ** 2))
        count += reference[a:b].size
    target_rms = math.sqrt(power / count)
    reference_peak = float(np.max(np.abs(reference)))
    del reference
    source = decode(wind_source)
    wind = np.zeros((SECONDS * RATE, 2), dtype=np.float32)
    wind_events = []
    sos = signal.butter(2, 1800, fs=RATE, output='sos')
    for i, (start, duration, up, down) in enumerate(WIND):
        best = None
        for attempt in range(4):
            seed = 183100 + i * 10 + attempt
            rng = np.random.default_rng(seed)
            x, grains = overlapping_sections(source, duration * RATE, rng)
            x = signal.sosfiltfilt(sos, x, axis=0)
            t = np.arange(len(x)) / RATE
            env = event_envelope(len(x), RATE, up, down)
            movement = .88 + .08 * np.sin(2 * np.pi * t / (duration * .79) + rng.uniform(0, 6))
            movement += .04 * np.sin(2 * np.pi * t / (duration * .43) + rng.uniform(0, 6))
            x *= (env * movement)[:, None]
            gain = target_rms / rms(x[up * RATE:(duration - down) * RATE])
            x *= gain
            peak = float(np.max(np.abs(x)))
            if best is None or peak < best[0]:
                best = (peak, x, gain, seed, grains)
            if peak <= reference_peak:
                break
        peak, x, gain, seed, grains = best
        # Linear source calibration preserves dynamics; no compressor/limiter.
        crest_guard = min(1., reference_peak / peak)
        x = (x * crest_guard).astype(np.float32)
        at = start * RATE
        wind[at:at + len(x)] = x
        wind_events.append({'start_seconds': start, 'end_seconds': start + duration,
                            'duration_seconds': duration, 'fade_in_seconds': up, 'fade_out_seconds': down,
                            'seed': seed, 'grains': grains, 'source_calibration_gain': gain,
                            'crest_guard_linear_gain': crest_guard, 'unlifted_peak': float(np.max(np.abs(x))),
                            'unlifted_outside_fades_rms': rms(x[up * RATE:(duration - down) * RATE])})
        print(f'Wind passage {i + 1}/12 assembled', flush=True)
    write_audio(wind, paths['wind-unlifted'], 'flac')
    # Decode the saved reference for exact gain verification after quantization.
    del wind
    wind = decode(paths['wind-unlifted'])
    for start, duration, up, down in WIND:
        a, b = start * RATE, (start + duration) * RATE
        env = event_envelope(b - a, RATE, up, down)
        wind[a:b] *= peak_multiplier(env)[:, None]
    write_audio(wind, paths['wind'], 'flac')
    del wind, source
    lossless = out / 'Snowline-18min-sparse-radio-stronger-wind-v1.flac'
    sources = [paths[k] for k in ['music', 'radio', 'wind', 'ventilation', 'creaks']]
    print('Mixing the complete18-minute session...', flush=True)
    mix(sources, lossless)
    listening = out / 'Snowline-18min-sparse-radio-stronger-wind-v1.mp3'
    fixed_gain = c['listening_copy_gain_db']
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-i', str(lossless),
                    '-af', f'volume={fixed_gain:.15g}dB', '-c:a', 'libmp3lame', '-b:a', '192k',
                    '-n', str(listening)], capture_output=True, check=True)
    print('Checking all files, source repeats, sparse events, crest gain and complete mix...', flush=True)
    checks = [validate_audio(p, SECONDS) for p in list(paths.values()) + [lossless, listening]]
    validation = {'music_repeat': check_repeat(music, paths['music']),
                  'ventilation_repeat': check_repeat(ventilation, paths['ventilation']),
                  'radio_silence': check_sparse(paths['radio'], radio_events),
                  'creak_silence': check_sparse(paths['creaks'], creak_events),
                  'wind_peak_gain': check_wind_gain(paths['wind-unlifted'], paths['wind']),
                  'complete_mix': check_sum(sources, lossless)}
    meter = out / 'meter'
    meter.mkdir()
    measured = loudness(listening, imageio_ffmpeg.get_ffmpeg_exe(), meter)
    for path, expected in required:
        if sha(path) != expected:
            raise ValueError('Original source changed')
    record = {'date': '2026-11-03', 'seconds': SECONDS,
              'user_request': "ok can we try a new mix, that when the wind reaches maximum it's like a bit louder, can we cut the chatter down to about once every 2-3 minutes, and can we make an 18 minute version i can listen to next?",
              'test_only': True, 'current_accepted_preset_replaced': False,
              'music': {'source_sha256': sha(music), 'exact9min_circular_source_repeated_twice': True,
                        'gain': 1, 'new_music_or_fades': False},
              'ventilation': {'source_sha256': sha(ventilation), 'exact9min_source_repeated_twice': True, 'gain': 1},
              'radio': {'events': radio_events, 'count': 7, 'voice_onset_intervals_seconds': intervals.tolist(),
                        'same_per_event_source_gain': True, 'source_rms_renormalized': False,
                        'independent18min_schedule': True, 'unique_source_phrases': 7,
                        'acknowledgement_packets': sum(e['acknowledgement'] is not None for e in radio_events)},
              'wind': {'events': wind_events, 'count': 12, 'off_gaps_seconds': gaps,
                       'coverage_seconds_including_fades': sum(e[1] for e in WIND),
                       'reference_core_rms': target_rms, 'reference_sample_peak': reference_peak,
                       'same_source_and1800hz_filter': True, 'one_original_source_only': True,
                       'source_fragments_can_recur': True, 'nine_min_composite_not_tiled': True,
                       'peak_region_max_amplitude_multiplier': 1.1,
                       'peak_region_max_lift_db': 20 * math.log10(1.1),
                       'lift_shape': 'Smooth rise from0 extra gain at outer-envelope<=0.6 to10% extra at envelope1; independently varying source texture remains.',
                       'meaning_of10percent': 'Amplitude relative to the same new wind assembly without peak lift; not a perceived-loudness claim or exact comparison of different-waveform old/new global peaks.'},
              'creaks': {'events': creak_events, 'source_sha256': sha(creak_source),
                         'requested_previous10percent_increase_retained': True, 'new_gain': 1},
              'whole_listening_gain_db': fixed_gain, 'whole_mix_renormalized': False,
              'sources': [{'file': str(p.relative_to(root)), 'sha256': h} for p, h in required],
              'outputs': checks, 'validation': validation, 'listening_loudness': measured,
              'assistant_listening': False, 'user_review': None, 'new_paid_calls': 0,
              'implementation_sha256': sha(Path(__file__))}
    (out / 'recipe.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    cues = ['Snowline18-minute trial — cue sheet', 'Radio times are voice starts. Wind times include fades.', '', 'RADIO']
    cues += [f'{int(t // 60):02d}:{t % 60:02d}' for t in VOICE_TIMES]
    cues += ['', 'WIND'] + [f'{int(s // 60):02d}:{s % 60:02d}–{int((s+d)//60):02d}:{(s+d)%60:02d}' for s, d, _, _ in WIND]
    cues += ['', 'CREAKS'] + [f'{int(t // 60):02d}:{t % 60:02d}' for t in CREAK_TIMES]
    (out / 'cue-sheet.txt').write_text('\n'.join(cues) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(out.resolve()), 'seconds': SECONDS, 'radio_calls': 7,
                      'radio_intervals': intervals.tolist(), 'wind_passages': 12,
                      'wind_off_gaps': gaps, 'files_fully_checked': len(checks),
                      'loudness': measured, 'validation': validation}, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    run(a.root.resolve(), a.out)
