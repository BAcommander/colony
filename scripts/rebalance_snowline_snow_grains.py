"""Compare louder snow-only gains on the same fixed Snowline V5 excerpt."""
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


def run(root, parent, out, increments, feedback):
    root, parent, out = [p.resolve() for p in (root, parent, out)]
    if out.exists() and any(out.iterdir()):
        raise ValueError('Use a fresh output directory')
    if not increments or any(not math.isfinite(db) for db in increments) or len(set(increments)) != len(increments):
        raise ValueError('Choose distinct finite gain increments')
    parent_file = parent / 'review.json'
    prior = json.loads(parent_file.read_text(encoding='utf-8'))
    inputs = [parent / 'A-current-v5-unfaded-60s.flac', parent / 'Snow-grains-only-60s.flac']
    originals = []
    for p in inputs:
        expected = next(e['sha256'] for e in prior['outputs'] if e['file'] == p.name)
        if file_hash(p) != expected:
            raise ValueError('Parent audio differs: ' + str(p))
        originals.append((p, expected))
    base, old_snow = [decode(p) for p in inputs]
    seconds = prior['seconds']
    if len(base) != round(seconds * RATE) or old_snow.shape != base.shape:
        raise ValueError('Input durations differ')
    onset = prior['snow_event']['start_in_clip_seconds']
    ending = prior['snow_event']['end_in_clip_seconds']
    allowed = np.zeros(len(base), dtype=bool)
    allowed[round(onset * RATE):round(ending * RATE)] = True
    if np.any(old_snow[~allowed]):
        raise ValueError('Unexpected snow outside its recorded event')
    gain = prior['whole_listening_gain_db']
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    out.mkdir(parents=True, exist_ok=True)
    variants = []
    for db in increments:
        label = ('plus' if db >= 0 else 'minus') + f'{abs(db):g}'.replace('.', 'p') + 'dB'
        folder = out / label
        folder.mkdir()
        factor = 10 ** (db / 20)
        stem = folder / 'snow-adjusted-60s.flac'
        write_audio(old_snow * factor, stem, 'flac')
        snow = decode(stem)
        gain_error = float(np.max(np.abs(snow.astype(float) - old_snow.astype(float) * factor)))
        raw = folder / 'mix-unfaded-60s.flac'
        write_audio(base + snow, raw, 'flac')
        mixed = decode(raw)
        sum_error = float(np.max(np.abs(mixed - (base + snow))))
        outside = float(np.max(np.abs(mixed[~allowed] - base[~allowed])))
        if gain_error > 1.3e-7 or sum_error != 0 or outside != 0:
            raise ValueError('Snow-only adjustment check failed')
        lossless = folder / f'Snow-{label}-60s.flac'
        mp3 = lossless.with_suffix('.mp3')
        focus = folder / f'Snow-{label}-focus-20s.mp3'
        subprocess.run([ff, '-v', 'error', '-i', str(raw), '-af', f'volume={gain:.15g}dB',
                        '-c:a', 'flac', '-sample_fmt', 's32', '-bits_per_raw_sample', '24',
                        '-n', str(lossless)], capture_output=True, check=True)
        for target, trim in [(mp3, []), (focus, ['-ss', '20', '-t', '20'])]:
            subprocess.run([ff, '-v', 'error', '-i', str(lossless), *trim,
                            '-c:a', 'libmp3lame', '-b:a', '192k', '-n', str(target)], capture_output=True, check=True)
        playback_error = float(np.max(np.abs(decode(lossless).astype(float) - mixed.astype(float) * 10 ** (gain / 20))))
        if playback_error > 1.5e-7:
            raise ValueError('Playback gain changed')
        checks = []
        for p in [stem, raw, lossless, mp3, focus]:
            check = validate_file(p, 20 if p == focus else seconds)
            check['file'] = p.relative_to(out).as_posix()
            checks.append(check)
        meter = folder / 'meter'
        meter.mkdir()
        measured = loudness(mp3, ff, meter)
        variants.append({'snow_increment_db_vs_first_test': db, 'amplitude_multiplier': factor,
                         'source_gain_after_filter_db': prior['snow_event']['source_gain_after_filter_db'] + db,
                         'event_rms_db_vs_wind_analytical': prior['snow_event']['actual_event_rms_db_vs_wind'] + db,
                         'initial_wind_peak_constraint_reapplied': False,
                         'limiter_compressor_or_normalization_added': False,
                         'validation': {'frames': len(mixed), 'snow_gain_max_error': gain_error,
                                        'exact_new_mix_sum_error': sum_error, 'difference_outside_snow_event': outside,
                                        'lossless_playback_gain_max_error': playback_error},
                         'outputs': checks, 'loudness': measured})
    for p, expected in originals:
        if file_hash(p) != expected:
            raise ValueError('Parent audio changed')
    record = {'date': '2026-11-03', 'user_feedback_verbatim': feedback,
              'scope': 'Louder short snow auditions only; full two-hour V5 unchanged',
              'parent_review': parent_file.relative_to(root).as_posix(), 'parent_review_sha256': file_hash(parent_file),
              'current_master': prior['current_master'], 'source': prior['source'],
              'source_window_seconds': prior['source_window_seconds'], 'seconds': seconds,
              'snow_event': prior['snow_event'],
              'variants': variants, 'whole_listening_gain_db': gain, 'independent_normalization': False,
              'focus_excerpt': {'start_in_minute_seconds': 20, 'seconds': 20,
                                'snow_in_focus_seconds': [onset - 20, ending - 20],
                                'stronger_middle_approximately_seconds': [9, 11], 'creak_in_focus': False},
              'unchanged': ['music', 'wind', 'ventilation', 'creak', 'radio', 'timing', 'snow filtering and edges'],
              'level_note': 'Both gains are relative to the first snow audition, not consecutive increases. The initial conservative peak-relative calibration is not reapplied.',
              'assistant_listening': False, 'user_preference': None, 'full_two_hour_updated': False,
              'new_paid_calls': 0, 'backup_scope': 'Local additions after the earlier verified backup',
              'implementation_sha256': file_hash(Path(__file__))}
    (out / 'review.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(out), 'variants': [{k: v[k] for k in ('snow_increment_db_vs_first_test', 'validation', 'loudness')} for v in variants]}, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--parent', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--db', type=float, nargs='+', default=[6, 9])
    p.add_argument('--feedback', required=True)
    args = p.parse_args()
    run(args.root, args.parent, args.out, args.db, args.feedback)
