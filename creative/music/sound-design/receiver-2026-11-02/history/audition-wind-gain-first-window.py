"""Same-window Snowline balance test: adjust only the wind stem."""
import argparse
import json
import math
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np

from analyze_ambient_audio import loudness
from build_snowline_two_hour_mix import file_hash, validate_file
from generate_polar_comms import decode
from generate_receiver_texture import RATE, write_audio


def summed(layers):
    result = layers[0].copy()
    for layer in layers[1:]:
        result += layer
    return result


def run(root, parent, out, db, start, seconds, feedback):
    root, parent, out = root.resolve(), parent.resolve(), out.resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError('Use a fresh audition directory')
    if not math.isfinite(db) or start < 0 or seconds <= 0 or start + seconds > 7200:
        raise ValueError('Invalid gain or source window')
    prior = json.loads((parent / 'recipe.json').read_text(encoding='utf-8'))
    sources = [(root / e['file'], e['sha256']) for e in prior['source_stems']]
    if len(sources) != 5 or 'wind' not in sources[2][0].name:
        raise ValueError('Expected music/radio/wind/ventilation/creaks order')
    master = parent / prior['master_file']
    master_sha = next(e['sha256'] for e in prior['outputs'] if e['file'] == master.name)
    for p, expected in sources + [(master, master_sha)]:
        if file_hash(p) != expected:
            raise ValueError(f'Source differs: {p}')
    layers = [decode(p, start=start, seconds=seconds) for p, _ in sources]
    if any(len(x) != round(seconds * RATE) or not np.isfinite(x).all() for x in layers):
        raise ValueError('Excerpt source decode failed')
    old = decode(master, start=start, seconds=seconds)
    source_sum_error = float(np.max(np.abs(summed(layers) - old)))
    if source_sum_error != 0:
        raise ValueError('Excerpt sources do not reproduce the current mix exactly')
    out.mkdir(parents=True, exist_ok=True)
    multiplier = 10 ** (db / 20)
    old_wind = layers[2]
    wind = out / 'wind-only-adjusted.flac'
    write_audio(old_wind * multiplier, wind, 'flac')
    layers[2] = decode(wind)
    gain_error = float(np.max(np.abs(layers[2].astype(float) - old_wind.astype(float) * multiplier)))
    if gain_error > 1.3e-7:
        raise ValueError('Wind gain mismatch')
    raw = out / 'same-minute-wind-adjusted-unfaded.flac'
    write_audio(summed(layers), raw, 'flac')
    new = decode(raw)
    delta_error = float(np.max(np.abs((new - old) - (layers[2] - old_wind))))
    if delta_error > 3e-7:
        raise ValueError('Changes beyond wind detected')
    fixed_gain = prior['delivery_processing']['listening_gain_db']
    lossless = out / f'Wind-plus{db:g}dB-creak-unchanged-60s.flac'
    listening = lossless.with_suffix('.mp3')
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff, '-v', 'error', '-i', str(raw), '-af', f'volume={fixed_gain:.15g}dB',
                    '-c:a', 'flac', '-sample_fmt', 's32', '-bits_per_raw_sample', '24',
                    '-n', str(lossless)], capture_output=True, check=True)
    subprocess.run([ff, '-v', 'error', '-i', str(lossless), '-c:a', 'libmp3lame', '-b:a', '192k',
                    '-n', str(listening)], capture_output=True, check=True)
    reference = decode(lossless)
    listening_gain_error = float(np.max(np.abs(reference.astype(float) - new.astype(float) * 10 ** (fixed_gain / 20))))
    if listening_gain_error > 1.5e-7:
        raise ValueError('Listening gain changed')
    checks = []
    for p in [wind, raw, lossless, listening]:
        item = validate_file(p, seconds)
        item['file'] = p.relative_to(out).as_posix()
        checks.append(item)
    meter = out / 'meter'
    meter.mkdir()
    measured = loudness(listening, ff, meter)
    record = {'date': '2026-11-03', 'user_request': feedback,
              'parent_recipe': (parent / 'recipe.json').relative_to(root).as_posix(),
              'scope': 'One-minute level test only; existing full two-hour V4 files unchanged',
              'source_window_seconds': [start, start + seconds], 'seconds': seconds,
              'wind_increment_db_vs_v4': db, 'wind_amplitude_multiplier': multiplier,
              'same_wind_envelope_and_timing': True, 'same_creak_music_radio_ventilation': True,
              'wind_gain_applies_to_entire_stem_in_window': True,
              'whole_listening_gain_db': fixed_gain, 'independent_normalization': False,
              'wind_full_outer_envelope_seconds': [6, 45], 'creak_at_clip_seconds': 10,
              'radio_stem_peak_in_window': float(np.max(np.abs(layers[1]))),
              'validation': {'frames': len(new), 'old_source_sum_error': source_sum_error,
                             'wind_gain_error': gain_error, 'wind_only_mix_delta_error': delta_error,
                             'lossless_reference_playback_gain_error': listening_gain_error},
              'sources': [{'file': p.relative_to(root).as_posix(), 'sha256': h} for p, h in sources],
              'source_master_sha256': master_sha, 'outputs': checks, 'measured_excerpt_loudness': measured,
              'assistant_listening': False, 'user_balance_verdict': None,
              'full_two_hour_mix_updated': False, 'new_paid_calls': 0,
              'implementation_sha256': file_hash(Path(__file__))}
    (out / 'review.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(out), 'wind_increment_db': db,
                      'validation': record['validation'], 'radio_stem_peak': record['radio_stem_peak_in_window'],
                      'outputs_fully_decoded': len(checks), 'loudness': measured}, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--parent', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--wind-db', type=float, default=2)
    p.add_argument('--start', type=float, default=1615)
    p.add_argument('--seconds', type=float, default=60)
    p.add_argument('--feedback')
    a = p.parse_args()
    run(a.root, a.parent, a.out, a.wind_db, a.start, a.seconds, a.feedback)
