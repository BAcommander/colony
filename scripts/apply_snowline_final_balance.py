"""Apply the tested wind/radio balance to the complete two-hour Snowline mix."""
import argparse
import json
import math
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np

from analyze_ambient_audio import loudness
from build_snowline_18min_audition import pcm
from build_snowline_two_hour_mix import FRAMES, file_hash, stream_flac, validate_file
from generate_polar_comms import decode
from render_snowline_wind_and_creaks import mix


def adjusted_blocks(path, db):
    factor = 10 ** (db / 20)
    for block in pcm(path):
        yield block * factor


def verify(stems, old_radio, intermediate, old_wind, master):
    # music, newradio, newwind, ventilation, creaks, oldradio, radio-1, oldwind, master
    streams = [pcm(p) for p in stems + [old_radio, intermediate, old_wind, master]]
    peaks = [0.] * len(streams)
    frames, sum_error = 0, 0.
    gain_errors = [0., 0., 0.]
    quiet_errors = [0., 0.]
    factors = [10 ** (-1 / 20), 10 ** (-.5 / 20), 10 ** (2 / 20)]
    try:
        while True:
            b = [next(s, None) for s in streams]
            if all(x is None for x in b):
                break
            if any(x is None for x in b) or len({len(x) for x in b}) != 1:
                raise ValueError('Full-length streams differ')
            for i, x in enumerate(b):
                if not np.isfinite(x).all():
                    raise ValueError('Non-finite audio')
                peaks[i] = max(peaks[i], float(np.max(np.abs(x))))
            for i, (before, after) in enumerate([(b[5], b[6]), (b[6], b[1]), (b[7], b[2])]):
                gain_errors[i] = max(gain_errors[i], float(np.max(np.abs(after.astype(float) - before.astype(float) * factors[i]))))
            for i, (before, after) in enumerate([(b[5], b[1]), (b[7], b[2])]):
                quiet = np.all(before == 0, axis=1)
                if np.any(quiet):
                    quiet_errors[i] = max(quiet_errors[i], float(np.max(np.abs(after[quiet]))))
            summed = b[0].copy()
            for x in b[1:5]:
                summed += x
            sum_error = max(sum_error, float(np.max(np.abs(b[-1] - summed))))
            frames += len(b[0])
            if frames % (600 * 48000) < 65536:
                print(f'Complete mix check: {frames / 48000 / 60:.0f}/120 minutes', flush=True)
    finally:
        for s in streams:
            s.close()
    if frames != FRAMES or max(gain_errors) > 1.3e-7 or sum_error > 3e-7 or max(quiet_errors) != 0 or max(peaks) >= 1:
        raise ValueError(f'Balance validation failed: {frames}, {gain_errors}, {sum_error}, {quiet_errors}, {peaks}')
    return {'frames': frames, 'seconds': frames / 48000, 'all_samples_finite': True,
            'max_radio_minus1db_error': gain_errors[0], 'max_radio_additional_minus0p5db_error': gain_errors[1],
            'max_wind_plus2db_error': gain_errors[2], 'max_radio_or_wind_signal_outside_original_windows': max(quiet_errors),
            'max_five_stem_sum_error': sum_error, 'sample_peaks': peaks}


def run(root, parent, out):
    root, parent, out = root.resolve(), parent.resolve(), out.resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError('Use a fresh output folder')
    prior_file = parent / 'recipe.json'
    prior = json.loads(prior_file.read_text(encoding='utf-8'))
    original = [(root / e['file'], e['sha256']) for e in prior['source_stems']]
    if len(original) != 5 or 'radio' not in original[1][0].name or 'wind' not in original[2][0].name:
        raise ValueError('Unexpected stem order')
    for p, expected in original:
        if file_hash(p) != expected:
            raise ValueError(f'Stem source hash differs: {p}')
    out.mkdir(parents=True, exist_ok=True)
    (out / 'stems').mkdir()
    (out / 'references').mkdir()
    intermediate = out / 'references/radio-minus1db-step.flac'
    radio = out / 'stems/Snowline-radio-minus1p5dB-2h-v5.flac'
    wind = out / 'stems/Snowline-wind-plus2dB-2h-v5.flac'
    print('Applying the exact tested radio gain steps: -1dB, then -0.5dB...', flush=True)
    stream_flac(adjusted_blocks(original[1][0], -1), intermediate)
    stream_flac(adjusted_blocks(intermediate, -.5), radio)
    print('Applying +2dB to the entire wind stem, preserving its timing and shape...', flush=True)
    stream_flac(adjusted_blocks(original[2][0], 2), wind)
    ordered = [original[0][0], radio, wind, original[3][0], original[4][0]]
    master = out / 'Below-the-Snowline-2-Hours-unfaded-master-v5.flac'
    print('Mixing the full two-hour V5 master with unchanged music, ventilation and creaks...', flush=True)
    mix(ordered, master)
    full = out / 'Below-the-Snowline-2-Hours-v5.mp3'
    gain = prior['delivery_processing']['listening_gain_db']
    print('Encoding full two-hour MP3 at the same playback gain and single closing fade...', flush=True)
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-i', str(master),
                    '-af', f'volume={gain:.15g}dB,afade=t=out:st=7180:d=20',
                    '-c:a', 'libmp3lame', '-b:a', '192k', '-n', str(full)], capture_output=True, check=True)
    print('Checking all345,600,000 frames of the gain changes and final mix...', flush=True)
    validation = verify(ordered, original[1][0], intermediate, original[2][0], master)
    references = [
        (195, root / 'exports/13-below-the-snowline/level-tests/radio-minus1p5db-wind-plus2db-v1/radio-adjusted-unfaded-context.flac'),
        (1615, root / 'exports/13-below-the-snowline/level-tests/wind-plus2db-v1/same-minute-wind-adjusted-unfaded.flac')]
    matched = []
    for start, reference in references:
        excerpt = decode(master, start=start, seconds=60)
        target = decode(reference)
        error = float(np.max(np.abs(excerpt - target)))
        if error != 0:
            raise ValueError(f'Full mix differs from tested excerpt: {start}, {error}')
        matched.append({'source_start_seconds': start, 'seconds': 60,
                        'reference': reference.relative_to(root).as_posix(),
                        'reference_sha256': file_hash(reference), 'max_sample_error': error})
    print('Both full-mix excerpts match the tested radio/wind minutes exactly. Checking MP3...', flush=True)
    full_check = validate_file(full, 7200)
    meter = out / 'meter'
    meter.mkdir()
    measured = loudness(full, imageio_ffmpeg.get_ffmpeg_exe(), meter)
    for p, expected in original:
        if file_hash(p) != expected:
            raise ValueError('An original stem was modified')
    record = {'date': '2026-11-03', 'user_request': 'so can we get the full 2 hour mix now?',
              'seconds': 7200, 'short_test_settings_authorized_for_full_mix': True,
              'parent_recipe': prior_file.relative_to(root).as_posix(), 'parent_recipe_sha256': file_hash(prior_file),
              'wind_gain_db_vs_v4': 2, 'wind_amplitude_multiplier': 10 ** (2 / 20),
              'radio_gain_db_vs_v4': -1.5, 'radio_gain_steps_db': [-1, -.5],
              'radio_amplitude_multiplier_total': 10 ** (-1.5 / 20),
              'music_ventilation_creaks_unchanged': True, 'all_event_timing_unchanged': True,
              'counts': {'radio_calls': 47, 'wind_passages': 80, 'creaks': 24},
              'master_file': master.name,
              'source_stems': [{'file': p.relative_to(root).as_posix(), 'sha256': file_hash(p)} for p in ordered],
              'original_sources': [{'file': p.relative_to(root).as_posix(), 'sha256': h} for p, h in original],
              'validation': validation, 'tested_excerpt_matches': matched, 'mp3_check': full_check,
              'listening_loudness': measured, 'delivery_processing': prior['delivery_processing'],
              'whole_mix_renormalized': False,
              'outputs': [{'file': p.relative_to(out).as_posix(), 'seconds': 7200,
                           'sha256': file_hash(p), 'bytes': p.stat().st_size} for p in [radio, wind, master, full]],
              'new_paid_calls': 0, 'assistant_listening': False, 'full_two_hour_user_verdict': None,
              'new_video_assembled': False, 'implementation_sha256': file_hash(Path(__file__))}
    (out / 'recipe.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(out), 'validation': validation,
                      'tested_excerpt_matches': matched, 'loudness': measured,
                      'mp3': full_check}, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--parent', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    run(a.root, a.parent, a.out)
