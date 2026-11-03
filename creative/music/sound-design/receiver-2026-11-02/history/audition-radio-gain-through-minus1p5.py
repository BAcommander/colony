"""Change only the radio component of an existing short Snowline level test."""
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


def run(root, parent, out, db, feedback):
    root, parent, out = root.resolve(), parent.resolve(), out.resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError('Use a fresh review directory')
    if not math.isfinite(db):
        raise ValueError('Gain must be finite')
    prior_file = parent / 'review.json'
    prior = json.loads(prior_file.read_text(encoding='utf-8'))
    start, end = prior['source_window_seconds']
    seconds = end - start
    old_mix_file = root / prior['unfaded_excerpt_file'] if 'unfaded_excerpt_file' in prior else parent / 'same-minute-wind-adjusted-unfaded.flac'
    old_mix = decode(old_mix_file)
    if 'radio_component_file' in prior:
        old_radio = decode(root / prior['radio_component_file'])
    else:
        source = next(e for e in prior['sources'] if 'radio-2h' in e['file'])
        p = root / source['file']
        if file_hash(p) != source['sha256']:
            raise ValueError('Radio source hash differs')
        old_radio = decode(p, start=start, seconds=seconds)
    if len(old_radio) != len(old_mix) or len(old_mix) != round(seconds * RATE):
        raise ValueError('Excerpt duration mismatch')
    previous_info = next(e for e in prior['outputs'] if e['file'] == old_mix_file.name)
    if file_hash(old_mix_file) != previous_info['sha256']:
        raise ValueError('Previous context mix differs')
    out.mkdir(parents=True, exist_ok=True)
    multiplier = 10 ** (db / 20)
    radio_file = out / 'radio-adjusted.flac'
    write_audio(old_radio * multiplier, radio_file, 'flac')
    new_radio = decode(radio_file)
    gain_error = float(np.max(np.abs(new_radio.astype(float) - old_radio.astype(float) * multiplier)))
    delta = new_radio - old_radio
    raw_file = out / 'radio-adjusted-unfaded-context.flac'
    write_audio(old_mix + delta, raw_file, 'flac')
    new_mix = decode(raw_file)
    mix_error = float(np.max(np.abs((new_mix - old_mix) - delta)))
    quiet = np.all(old_radio == 0, axis=1)
    outside_error = float(np.max(np.abs(new_mix[quiet] - old_mix[quiet]))) if np.any(quiet) else 0.
    if gain_error > 1.3e-7 or mix_error > 3e-7 or outside_error != 0:
        raise ValueError('Radio-only change check failed')
    gain = prior['whole_listening_gain_db']
    full = out / 'Radio-minus1dB-in-context-60s.flac'
    mp3 = full.with_suffix('.mp3')
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff, '-v', 'error', '-i', str(raw_file), '-af', f'volume={gain:.15g}dB',
                    '-c:a', 'flac', '-sample_fmt', 's32', '-bits_per_raw_sample', '24',
                    '-n', str(full)], capture_output=True, check=True)
    subprocess.run([ff, '-v', 'error', '-i', str(full), '-c:a', 'libmp3lame', '-b:a', '192k',
                    '-n', str(mp3)], capture_output=True, check=True)
    reference = decode(full)
    playback_error = float(np.max(np.abs(reference.astype(float) - new_mix.astype(float) * 10 ** (gain / 20))))
    if playback_error > 1.5e-7:
        raise ValueError('Playback gain differs')
    checks = []
    for p in [radio_file, raw_file, full, mp3]:
        item = validate_file(p, seconds)
        item['file'] = p.name
        checks.append(item)
    meter = out / 'meter'
    meter.mkdir()
    measured = loudness(mp3, ff, meter)
    record = {'date': '2026-11-03', 'user_request': feedback,
              'parent_review': prior_file.relative_to(root).as_posix(), 'parent_review_sha256': file_hash(prior_file),
              'source_window_seconds': [start, end], 'seconds': seconds,
              'radio_increment_db_vs_previous_review': db,
              'radio_total_increment_db_vs_v4': prior.get('radio_total_increment_db_vs_v4', 0) + db,
              'radio_amplitude_multiplier': multiplier,
              'wind_increment_db_vs_v4': prior['wind_increment_db_vs_v4'],
              'wind_creak_music_ventilation_and_all_timings_unchanged': True,
              'whole_listening_gain_db': gain, 'independent_normalization': False,
              'events_in_window': prior['events_in_window'],
              'radio_voice_at_clip_seconds': prior['radio_voice_at_clip_seconds'],
              'wind_full_outer_envelope_seconds': prior['wind_full_outer_envelope_seconds'],
              'radio_component_file': radio_file.relative_to(root).as_posix(),
              'unfaded_excerpt_file': raw_file.relative_to(root).as_posix(),
              'validation': {'frames': len(new_mix), 'max_radio_gain_error': gain_error,
                             'radio_only_delta_error': mix_error, 'max_mix_change_outside_radio': outside_error,
                             'lossless_reference_playback_gain_error': playback_error},
              'outputs': checks, 'measured_excerpt_loudness': measured,
              'full_two_hour_mix_updated': False, 'assistant_listening': False, 'user_verdict': None,
              'implementation_sha256': file_hash(Path(__file__))}
    (out / 'review.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(out), 'validation': record['validation'],
                      'radio_voice_at_seconds': record['radio_voice_at_clip_seconds'],
                      'wind_increment_retained_db': record['wind_increment_db_vs_v4'],
                      'fully_decoded_files': len(checks), 'loudness': measured}, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--parent', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--radio-db', type=float, default=-1)
    p.add_argument('--feedback')
    a = p.parse_args()
    run(a.root, a.parent, a.out, a.radio_db, a.feedback)
