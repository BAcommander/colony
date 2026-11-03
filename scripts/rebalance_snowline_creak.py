"""Gain-only revision of the supplied Snowline creak; preserve the B base."""
import argparse
import json
import math
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np

from analyze_ambient_audio import loudness
from audition_snowline_supplied_creak import sha, encode, check_difference
from build_snowline_radio_session import validate_audio
from render_snowline_wind_and_creaks import mix


def check_gain(before, after, gain):
    processes = [subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-i', str(p),
                  '-ar', '48000', '-ac', '2', '-f', 'f32le', 'pipe:1'],
                  stdout=subprocess.PIPE, stderr=subprocess.PIPE) for p in [before, after]]
    frames, error = 0, 0.
    try:
        while True:
            blocks = [p.stdout.read(65536 * 8) for p in processes]
            if not any(blocks):
                break
            if not all(blocks) or len({len(b) for b in blocks}) != 1:
                raise ValueError('Unequal decoded streams')
            a, b = [np.frombuffer(raw, '<f4') for raw in blocks]
            error = max(error, float(np.max(np.abs(b.astype(float) - a.astype(float) * gain))))
            frames += len(a) // 2
        for p in processes:
            message = p.stderr.read()
            if p.wait():
                raise ValueError(message.decode(errors='replace'))
    finally:
        for p in processes:
            if p.poll() is None:
                p.kill()
            p.wait()
    if frames != 25920000 or error > 1.3e-7:
        raise ValueError(f'Stem gain check failed: {frames}, {error}')
    return {'frames': frames, 'amplitude_multiplier': gain, 'max_gain_error': error}


def run(parent, out, gain):
    if not math.isfinite(gain) or gain <= 0:
        raise ValueError('Gain must be positive and finite')
    if out.exists() and any(out.iterdir()):
        raise ValueError('Use a fresh output directory')
    prior = json.loads((parent / 'recipe.json').read_text(encoding='utf-8'))
    original_stem = parent / 'Snowline-supplied-creak-stem-9min-v1.flac'
    expected = next(e['sha256'] for e in prior['outputs'] if e['file'] == original_stem.name)
    base = Path(prior['base']['file'])
    if sha(original_stem) != expected or sha(base) != prior['base']['sha256']:
        raise ValueError('Prior creak stem or B base differs from the verified source')
    out.mkdir(parents=True, exist_ok=True)
    stem = out / 'Snowline-supplied-creak-stem-9min-v2.flac'
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-i', str(original_stem),
                    '-af', f'volume={gain:.15g}', '-c:a', 'flac', '-sample_fmt', 's32',
                    '-bits_per_raw_sample', '24', '-n', str(stem)], capture_output=True, check=True)
    lossless = out / 'Snowline-B-plus-supplied-creak-9min-v2.flac'
    mix([base, stem], lossless)
    listening = out / 'Snowline-B-plus-supplied-creak-9min-v2.mp3'
    preview = out / 'D-supplied-creak-v2-90s-check.mp3'
    second = out / 'D-supplied-creak-v2-second-event-30s.mp3'
    fixed_gain = prior['listening_copy_gain_db']
    encode(lossless, listening, fixed_gain)
    encode(lossless, preview, fixed_gain, 54, 90)
    encode(lossless, second, fixed_gain, 326, 30)
    checks = []
    for p, seconds in [(stem, 540), (lossless, 540), (listening, 540), (preview, 90), (second, 30)]:
        checks.append(validate_audio(p, seconds))
    gain_check = check_gain(original_stem, stem, gain)
    windows = [(round(e['start_seconds'] * 48000),
                round((e['start_seconds'] + e['duration_seconds']) * 48000)) for e in prior['events']]
    mix_check = check_difference(base, stem, lossless, windows)
    meter = out / 'meter'
    meter.mkdir()
    measured = loudness(listening, imageio_ffmpeg.get_ffmpeg_exe(), meter)
    if abs(measured['integrated_lufs'] + 23) > .2:
        raise ValueError('Fixed-gain listening level needs review')
    assert sha(original_stem) == expected and sha(base) == prior['base']['sha256']
    record = {'date': '2026-11-03', 'user_feedback_verbatim': 'i think it could be like 10% louder',
              'change': 'Only creak stem amplitude multiplied; same source, timing, balance and B base',
              'creak_amplitude_multiplier': gain, 'creak_change_db': 20 * math.log10(gain),
              'prior_recipe_file': str((parent / 'recipe.json').resolve()),
              'prior_recipe_sha256': sha(parent / 'recipe.json'),
              'prior_stem_file': str(original_stem.resolve()), 'prior_stem_sha256': expected,
              'base': prior['base'], 'event_positions_seconds': [e['start_seconds'] for e in prior['events']],
              'listening_copy_gain_db': fixed_gain, 'whole_mix_renormalized': False,
              'preview': {'start_seconds': 54, 'seconds': 90, 'creak_at_seconds': 37},
              'second_preview': {'start_seconds': 326, 'seconds': 30, 'creak_at_seconds': 12},
              'gain_check': gain_check, 'mix_preservation_check': mix_check, 'metering': measured,
              'outputs': checks, 'approved_v2_environment_replaced': False,
              'user_v2_level_review': None, 'assistant_listening': False,
              'implementation_sha256': sha(Path(__file__))}
    (out / 'recipe.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(out.resolve()), 'creak_change_db': record['creak_change_db'],
                      'gain_check': gain_check, 'mix_check': mix_check, 'metering': measured,
                      'fully_validated_files': len(checks)}, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--parent', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--gain', type=float, default=1.1)
    args = p.parse_args()
    run(args.parent, args.out, args.gain)
