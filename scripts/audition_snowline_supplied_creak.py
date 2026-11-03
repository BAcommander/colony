"""Audition a supplied creak at the existing two Snowline test positions."""
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np

from analyze_ambient_audio import loudness
from build_snowline_radio_session import validate_audio
from generate_polar_comms import decode
from generate_receiver_texture import RATE, rms, write_audio
from render_snowline_wind_and_creaks import mix


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encode(source, target, gain_db, start=None, seconds=None):
    args = [imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-i', str(source)]
    if start is not None:
        args += ['-ss', str(start), '-t', str(seconds)]
    subprocess.run(args + ['-af', f'volume={gain_db:.15g}dB', '-c:a', 'libmp3lame',
                          '-b:a', '192k', '-n', str(target)], capture_output=True, check=True)


def check_difference(base, added, result, windows):
    """Check every decoded sample, including exact preservation outside events."""
    processes = [subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-i', str(p),
                  '-ar', str(RATE), '-ac', '2', '-f', 'f32le', 'pipe:1'],
                  stdout=subprocess.PIPE, stderr=subprocess.PIPE) for p in [base, added, result]]
    frames = 0
    error = 0.
    outside = 0.
    try:
        while True:
            blocks = [p.stdout.read(65536 * 8) for p in processes]
            if not any(blocks):
                break
            if not all(blocks) or len({len(b) for b in blocks}) != 1:
                raise ValueError('Mismatched decoded streams')
            a, b, c = [np.frombuffer(raw, '<f4').reshape(-1, 2) for raw in blocks]
            error = max(error, float(np.max(np.abs(c - (a + b)))))
            active = np.zeros(len(a), dtype=bool)
            for begin, end in windows:
                lo = max(0, begin - frames)
                hi = min(len(a), end - frames)
                if hi > lo:
                    active[lo:hi] = True
            if np.any(~active):
                outside = max(outside, float(np.max(np.abs(c[~active] - a[~active]))))
            frames += len(a)
        for p in processes:
            message = p.stderr.read()
            if p.wait():
                raise ValueError(message.decode(errors='replace'))
    finally:
        for p in processes:
            if p.poll() is None:
                p.kill()
            p.wait()
    if frames != 540 * RATE or error > 2e-7 or outside != 0:
        raise ValueError(f'Mix preservation failed: {frames}, {error}, {outside}')
    return {'frames': frames, 'max_recipe_error': error, 'max_outside_event_difference': outside}


def run(source, parent, out):
    if out.exists() and any(out.iterdir()):
        raise ValueError('Use a fresh output directory')
    previous = json.loads((parent / 'recipe.json').read_text(encoding='utf-8'))
    base = parent / 'B-wind-only/Snowline-wind-variation-9min-test.flac'
    old_c = parent / 'C-wind-and-creaks/Snowline-wind-and-creaks-9min-test.flac'
    expected = next(e['sha256'] for e in previous['outputs']
                    if e['file'] == 'B-wind-only/Snowline-wind-variation-9min-test.flac')
    if sha(base) != expected:
        raise ValueError('B base hash differs from earlier checked test')
    original_hash = sha(source)
    out.mkdir(parents=True, exist_ok=True)
    originals = out / 'source-originals'
    originals.mkdir()
    preserved = originals / 'supplied-frame-creak.mp3'
    shutil.copyfile(source, preserved)
    assert sha(preserved) == original_hash
    x = decode(preserved)
    if not np.isfinite(x).all() or not len(x) or np.max(np.abs(x)) >= 1:
        raise ValueError('Invalid source samples')
    duration = len(x) / RATE
    if not 0.1 <= duration <= 20:
        raise ValueError('Inspect source duration before using this audition renderer')
    # Retain the complete take; tiny boundary fades do not trim its tail.
    fade = np.ones(len(x), dtype=np.float64)
    up, down = min(round(.01 * RATE), len(x) // 4), min(round(.08 * RATE), len(x) // 4)
    fade[:up] = np.linspace(0, 1, up)
    fade[-down:] = np.linspace(1, 0, down)
    x = x * fade[:, None]
    stem = np.zeros((540 * RATE, 2), dtype=np.float32)
    events = []
    windows = []
    for index, (start, balance) in enumerate([(91., (.82, 1.12)), (338., (1.12, .82))]):
        gains = np.array(balance, dtype=np.float64)
        gains /= np.sqrt(np.mean(gains ** 2))
        event = x * gains[None, :]
        # A conservative event-body target with a separate peak guard; this
        # calibrates the new source, rather than copying old gain coefficients.
        body_gain = 10 ** (-54. / 20) / max(rms(event), 1e-12)
        peak_gain = 10 ** (-28. / 20) / max(float(np.max(np.abs(event))), 1e-12)
        gain = min(body_gain, peak_gain)
        event = (event * gain).astype(np.float32)
        at = round(start * RATE)
        stem[at:at + len(event)] += event
        windows.append((at, at + len(event)))
        event_path = out / f'placed-creak-{index + 1}.wav'
        write_audio(event, event_path, 'pcm_s24le')
        events.append({'start_seconds': start, 'duration_seconds': duration,
                       'source': preserved.relative_to(out).as_posix(), 'same_take_reused': True,
                       'position': 'right window frame' if index == 0 else 'left lower frame/pipe',
                       'channel_balance_gains': gains.tolist(), 'source_gain_db': 20 * np.log10(gain),
                       'rms_dbfs': 20 * np.log10(rms(event)),
                       'sample_peak': float(np.max(np.abs(event))), 'file': event_path.name})
    stem_path = out / 'Snowline-supplied-creak-stem-9min-v1.flac'
    write_audio(stem, stem_path, 'flac')
    del stem
    lossless = out / 'Snowline-B-plus-supplied-creak-9min-v1.flac'
    mix([base, stem_path], lossless)
    gain_db = previous['candidates']['B-wind-only']['metering']['matching_passes'][-1]['gain_db']
    full = out / 'Snowline-B-plus-supplied-creak-9min-v1.mp3'
    encode(lossless, full, gain_db)
    previews = []
    for label, path in [('B-no-creaks', base), ('C-old-procedural', old_c), ('D-supplied-creak', lossless)]:
        target = out / f'{label}-90s-check.mp3'
        encode(path, target, gain_db, 54, 90)
        previews.append(target)
    second = out / 'D-supplied-creak-second-event-30s.mp3'
    encode(lossless, second, gain_db, 326, 30)
    meter = out / 'meter'
    meter.mkdir()
    measured = loudness(full, imageio_ffmpeg.get_ffmpeg_exe(), meter)
    if abs(measured['integrated_lufs'] + 23) > .2:
        raise ValueError('Fixed-base-gain listening copy needs review')
    checks = []
    for p, seconds in [(preserved, duration), (stem_path, 540), (lossless, 540), (full, 540),
                       *[(p, 90) for p in previews], (second, 30),
                       *[(out / e['file'], duration) for e in events]]:
        item = validate_audio(p, seconds)
        item['file'] = p.relative_to(out).as_posix()
        checks.append(item)
    difference = check_difference(base, stem_path, lossless, windows)
    assert sha(source) == original_hash and sha(base) == expected
    recipe = {'date': '2026-11-03', 'test_only': True, 'approved_v2_preset_replaced': False,
              'user_message': 'ehres your creek sfx',
              'source': {'original_path': str(source.resolve()), 'preserved_file': preserved.relative_to(out).as_posix(),
                         'sha256': original_hash, 'decoded_seconds': duration,
                         'format': 'Supplied MP3, 48kHz stereo; not a lossless WAV original',
                         'executed_prompt_model_settings_and_cost': None},
              'base': {'file': str(base.resolve()), 'sha256': expected, 'gain': 1},
              'events': events, 'different_generated_takes': False,
              'processing': {'complete_take_retained': True, 'edge_fades_seconds': [.01, .08],
                             'body_target_dbfs': -54, 'peak_guard_dbfs': -28,
                             'gain_only_and_channel_balance': True, 'eq_compression_pitch_time_change': False},
              'listening_copy_gain_db': gain_db, 'comparison_gain_held_fixed': True,
              'preview': {'start_seconds': 54, 'seconds': 90, 'first_creak_seconds_in_preview': 37},
              'second_preview': {'start_seconds': 326, 'seconds': 30, 'creak_seconds_in_preview': 12},
              'loudness': measured, 'full_sample_difference_check': difference, 'outputs': checks,
              'assistant_listening': False, 'user_selection': None, 'new_paid_calls_by_assistant': 0,
              'implementation_sha256': sha(Path(__file__))}
    (out / 'recipe.json').write_text(json.dumps(recipe, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(out.resolve()), 'events': events, 'checks': len(checks),
                      'meter': measured, 'difference_check': difference}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--parent', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    run(args.source, args.parent, args.out)
