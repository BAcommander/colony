"""Adjust only creak gain in an existing two-hour Snowline delivery."""
import argparse
import json
import math
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np

from analyze_ambient_audio import loudness
from build_snowline_18min_audition import pcm
from build_snowline_two_hour_mix import FRAMES, file_hash, validate_file
from render_snowline_wind_and_creaks import mix


def verify_change(old_stem, new_stem, old_master, new_master, gain):
    streams = [pcm(p) for p in [old_stem, new_stem, old_master, new_master]]
    frames, gain_error, mix_error, outside, peak = 0, 0., 0., 0., 0.
    try:
        while True:
            blocks = [next(s, None) for s in streams]
            if all(x is None for x in blocks):
                break
            if any(x is None for x in blocks) or len({len(x) for x in blocks}) != 1:
                raise ValueError('Revision durations differ')
            old, new, before, after = blocks
            if not all(np.isfinite(x).all() for x in blocks):
                raise ValueError('Non-finite samples')
            gain_error = max(gain_error, float(np.max(np.abs(new.astype(float) - old.astype(float) * gain))))
            mix_error = max(mix_error, float(np.max(np.abs((after - before) - (new - old)))))
            quiet = np.all(old == 0, axis=1)
            if np.any(quiet):
                outside = max(outside, float(np.max(np.abs(after[quiet] - before[quiet]))))
            peak = max(peak, float(np.max(np.abs(after))))
            frames += len(old)
        if frames != FRAMES or gain_error > 1.3e-7 or mix_error > 3e-7 or outside != 0 or peak >= 1:
            raise ValueError(f'Gain-only revision check failed: {frames}, {gain_error}, {mix_error}, {outside}, {peak}')
    finally:
        for s in streams:
            s.close()
    return {'frames': frames, 'all_samples_finite': True, 'amplitude_multiplier': gain,
            'max_creak_gain_error': gain_error, 'max_creak_only_mix_error': mix_error,
            'max_mix_difference_outside_creaks': outside, 'lossless_mix_sample_peak': peak}


def run(root, parent, out, db, version):
    root, parent, out = root.resolve(), parent.resolve(), out.resolve()
    if not math.isfinite(db):
        raise ValueError('Gain must be finite')
    if out.exists() and any(out.iterdir()):
        raise ValueError('Use a fresh destination')
    prior_path = parent / 'recipe.json'
    prior = json.loads(prior_path.read_text(encoding='utf-8'))
    if 'source_stems' in prior:
        stems = [(root / e['file'], e['sha256']) for e in prior['source_stems']]
    else:
        stems = [(parent / e['file'], e['sha256']) for e in prior['outputs'] if e['file'].startswith('stems/')]
    if len(stems) != 5 or 'creaks' not in stems[-1][0].name:
        raise ValueError('Expected ordered five-stem source recipe')
    old_master = parent / prior.get('master_file', 'Below-the-Snowline-2-Hours-unfaded-master-v1.flac')
    old_master_sha = next(e['sha256'] for e in prior['outputs'] if e['file'] == old_master.name)
    required = stems + [(old_master, old_master_sha)]
    for path, expected in required:
        if file_hash(path) != expected:
            raise ValueError(f'Prior source hash differs: {path}')
    out.mkdir(parents=True, exist_ok=True)
    (out / 'stems').mkdir()
    old_stem = stems[-1][0]
    new_stem = out / 'stems' / f'Snowline-creaks-2h-v{version}.flac'
    print(f'Increasing only the existing creak stem by{db:g}dB...', flush=True)
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-i', str(old_stem),
                    '-af', f'volume={db:.15g}dB', '-c:a', 'flac', '-sample_fmt', 's32',
                    '-bits_per_raw_sample', '24', '-n', str(new_stem)], capture_output=True, check=True)
    master = out / f'Below-the-Snowline-2-Hours-unfaded-master-v{version}.flac'
    print('Remixing with the unchanged music, radio, wind and ventilation stems...', flush=True)
    mix([p for p, _ in stems[:-1]] + [new_stem], master)
    full = out / f'Below-the-Snowline-2-Hours-v{version}.mp3'
    gain_db = prior['delivery_processing']['listening_gain_db']
    print('Encoding the two-hour MP3 at the same listening gain and closing fade...', flush=True)
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-i', str(master),
                    '-af', f'volume={gain_db:.15g}dB,afade=t=out:st=7180:d=20',
                    '-c:a', 'libmp3lame', '-b:a', '192k', '-n', str(full)], capture_output=True, check=True)
    preview = out / f'Creak-plus-{db:g}dB-30s-check.mp3'
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-i', str(master), '-ss', '83', '-t', '30',
                    '-af', f'volume={gain_db:.15g}dB', '-c:a', 'libmp3lame', '-b:a', '192k', '-n', str(preview)],
                   capture_output=True, check=True)
    multiplier = 10 ** (db / 20)
    print('Checking the complete two-hour gain-only change and decoding both MP3 files...', flush=True)
    validation = verify_change(old_stem, new_stem, old_master, master, multiplier)
    full_check = validate_file(full, 7200)
    preview_check = validate_file(preview, 30)
    meter = out / 'meter'
    meter.mkdir()
    measured = loudness(full, imageio_ffmpeg.get_ffmpeg_exe(), meter)
    for path, expected in required:
        if file_hash(path) != expected:
            raise ValueError('A prior source was modified')
    outputs = [{'file': p.relative_to(out).as_posix(), 'seconds': 30 if p == preview else 7200,
                'sha256': file_hash(p), 'bytes': p.stat().st_size} for p in [new_stem, master, full, preview]]
    record = {'date': '2026-11-03', 'user_feedback_verbatim': 'creak still is too quiet, go up another db',
              'seconds': 7200, 'parent_recipe': prior_path.relative_to(root).as_posix(),
              'parent_recipe_sha256': file_hash(prior_path), 'creak_additional_gain_db': db,
              'creak_additional_amplitude_multiplier': multiplier,
              'same_music_radio_wind_ventilation_and_all_event_timing': True,
              'master_file': master.name,
              'source_stems': [{'file': p.relative_to(root).as_posix(), 'sha256': h} for p, h in stems[:-1]] +
                              [{'file': new_stem.relative_to(root).as_posix(), 'sha256': file_hash(new_stem)}],
              'previous_master': {'file': old_master.relative_to(root).as_posix(), 'sha256': old_master_sha},
              'validation': validation, 'mp3_check': full_check, 'preview_check': preview_check,
              'preview': {'source_start_seconds': 83, 'seconds': 30, 'first_creak_seconds': 8},
              'delivery_processing': prior['delivery_processing'], 'whole_mix_renormalized': False,
              'listening_loudness': measured, 'outputs': outputs, 'user_review': None,
              'assistant_listening': False, 'new_paid_calls': 0,
              'implementation_sha256': file_hash(Path(__file__))}
    (out / 'recipe.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(out), 'additional_creak_db': db, 'multiplier': multiplier,
                      'validation': validation, 'loudness': measured}, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--parent', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--gain-db', type=float, default=1)
    p.add_argument('--version', type=int, default=2)
    a = p.parse_args()
    run(a.root, a.parent, a.out, a.gain_db, a.version)
