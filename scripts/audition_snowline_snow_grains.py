"""Audition one supplied snow-grain take against a fixed current Snowline window."""
import argparse
import json
import math
import shutil
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from scipy import signal

from analyze_ambient_audio import loudness
from build_snowline_two_hour_mix import file_hash, validate_file
from generate_polar_comms import decode
from generate_receiver_texture import RATE, rms, write_audio


def run(root, source, parent, out):
    root, source, parent, out = [p.resolve() for p in (root, source, parent, out)]
    if out.exists() and any(out.iterdir()):
        raise ValueError('Preserve previous auditions; use a fresh output directory')
    current_file = root / 'creative/music/sound-design/receiver-2026-11-02/snowline-working-mix-current.json'
    current = json.loads(current_file.read_text(encoding='utf-8'))
    master = root / current['lossless_assembly_master']['file']
    master_hash = current['lossless_assembly_master']['sha256']
    if file_hash(master) != master_hash:
        raise ValueError('Current V5 lossless master differs')
    prior_file = parent / 'review.json'
    prior = json.loads(prior_file.read_text(encoding='utf-8'))
    base_path = parent / 'same-minute-wind-adjusted-unfaded.flac'
    wind_path = parent / 'wind-only-adjusted.flac'
    for p in (base_path, wind_path):
        expected = next(e['sha256'] for e in prior['outputs'] if e['file'] == p.name)
        if file_hash(p) != expected:
            raise ValueError('Existing wind comparison differs: ' + str(p))
    start, end = prior['source_window_seconds']
    seconds = end - start
    if (start, end) != (1615, 1675):
        raise ValueError('This audition uses the established 26:55–27:55 wind/creak window')
    original_hash = file_hash(source)
    base, wind = decode(base_path), decode(wind_path)
    # The old wind+2dB excerpt is a current V5 reference in this radio-free minute.
    actual = decode(master, start=start, seconds=seconds)
    reference_error = float(np.max(np.abs(base - actual)))
    if reference_error != 0 or len(base) != round(seconds * RATE):
        raise ValueError('Reference is not the current full V5 window exactly')
    del actual
    out.mkdir(parents=True, exist_ok=True)
    originals = out / 'source-originals'
    originals.mkdir()
    preserved = originals / 'supplied-snow-grains.mp3'
    shutil.copyfile(source, preserved)
    if file_hash(preserved) != original_hash:
        raise ValueError('Source-copy hash mismatch')
    x = decode(preserved)
    duration = len(x) / RATE
    if not .1 <= duration <= 20 or np.max(np.abs(x)) >= 1:
        raise ValueError('Review the source before using this short-take audition')
    # Artistic placement trial: retain the complete take and its original
    # internal dynamics, with light exterior dulling and tiny boundary fades.
    filtered = signal.sosfiltfilt(signal.butter(2, 2800, fs=RATE, output='sos'), x, axis=0)
    envelope = np.ones(len(x))
    for length, rising in ((round(.02 * RATE), True), (round(.08 * RATE), False)):
        length = min(length, len(x) // 4)
        edge = .5 - .5 * np.cos(np.linspace(0, np.pi, length))
        if rising:
            envelope[:length] *= edge
        else:
            envelope[-length:] *= edge[::-1]
    filtered *= envelope[:, None]
    onset = 24.
    at = round(onset * RATE)
    if at + len(x) > len(base):
        raise ValueError('Full source does not fit the review window')
    wind_event = wind[at:at + len(x)]
    wind_rms, wind_peak = rms(wind_event), float(np.max(np.abs(wind_event)))
    # An explicitly provisional level: -9dB by event-wide RMS, constrained so
    # isolated grain ticks remain at least3dB below the local wind's sample peak.
    relative_db, peak_margin_db = -9., -3.
    body_gain = wind_rms * 10 ** (relative_db / 20) / max(rms(filtered), 1e-12)
    peak_gain = wind_peak * 10 ** (peak_margin_db / 20) / max(float(np.max(np.abs(filtered))), 1e-12)
    gain = min(body_gain, peak_gain)
    event = (filtered * gain).astype(np.float32)
    stem = np.zeros_like(base)
    stem[at:at + len(event)] = event
    added = out / 'Snow-grains-only-60s.flac'
    write_audio(stem, added, 'flac')
    decoded_stem = decode(added)
    raw_base = out / 'A-current-v5-unfaded-60s.flac'
    raw_new = out / 'B-snow-grains-unfaded-60s.flac'
    write_audio(base, raw_base, 'flac')
    write_audio(base + decoded_stem, raw_new, 'flac')
    a, b = decode(raw_base), decode(raw_new)
    allowed = np.zeros(len(base), dtype=bool)
    allowed[at:at + len(event)] = True
    sum_error = float(np.max(np.abs(b - (a + decoded_stem))))
    outside_error = float(np.max(np.abs(b[~allowed] - a[~allowed])))
    if np.max(np.abs(a - base)) != 0 or sum_error != 0 or outside_error != 0:
        raise ValueError('A/B preservation failed')
    playback_gain = current['mp3']['listening_gain_db']
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    paths = [preserved, added, raw_base, raw_new]
    gain_errors = []
    meters = {}
    for label, raw in [('A-current-v5', raw_base), ('B-with-snow-grains', raw_new)]:
        lossless, listening = out / (label + '-60s.flac'), out / (label + '-60s.mp3')
        subprocess.run([ff, '-v', 'error', '-i', str(raw), '-af', f'volume={playback_gain:.15g}dB',
                        '-c:a', 'flac', '-sample_fmt', 's32', '-bits_per_raw_sample', '24',
                        '-n', str(lossless)], capture_output=True, check=True)
        subprocess.run([ff, '-v', 'error', '-i', str(lossless), '-c:a', 'libmp3lame', '-b:a', '192k',
                        '-n', str(listening)], capture_output=True, check=True)
        error = float(np.max(np.abs(decode(lossless).astype(float) - decode(raw).astype(float) * 10 ** (playback_gain / 20))))
        if error > 1.5e-7:
            raise ValueError('Whole-listening gain changed')
        gain_errors.append(error)
        meter = out / ('meter-' + label)
        meter.mkdir()
        meters[label] = loudness(listening, ff, meter)
        paths += [lossless, listening]
    checks = []
    for p in paths:
        item = validate_file(p, duration if p == preserved else seconds)
        item['file'] = p.relative_to(out).as_posix()
        checks.append(item)
    if file_hash(source) != original_hash or file_hash(master) != master_hash:
        raise ValueError('An original changed')
    recipe = {'date': '2026-11-03', 'scope': 'Short A/B audition only; existing full two-hour V5 unchanged',
              'source': {'original_path': str(source), 'preserved_file': preserved.relative_to(out).as_posix(),
                         'sha256': original_hash, 'bytes': preserved.stat().st_size, 'decoded_seconds': duration,
                         'sample_rate': RATE, 'channels': 2, 'format': 'User-supplied192kbps MP3; not a lossless original',
                         'sample_peak': float(np.max(np.abs(x))), 'rms_dbfs': 20 * math.log10(rms(x)),
                         'related_brief': 'creative/music/sound-design/receiver-2026-11-02/elevenlabs-spindrift-detail-v1.txt',
                         'executed_prompt_model_settings_cost': None},
              'current_master': {'file': master.relative_to(root).as_posix(), 'sha256': master_hash},
              'source_window_seconds': [start, end], 'seconds': seconds,
              'snow_event': {'start_in_clip_seconds': onset, 'end_in_clip_seconds': onset + duration,
                             'complete_take': True, 'looped': False, 'pitch_or_time_edit': False,
                             'lowpass_hz': 2800, 'lowpass_order': 2, 'zero_phase_filter': True,
                             'edge_fades_seconds': [.02, .08], 'source_gain_after_filter_db': 20 * math.log10(gain),
                             'target_event_rms_db_vs_wind': relative_db, 'peak_margin_db_vs_local_wind': peak_margin_db,
                             'peak_guard_limited': peak_gain < body_gain,
                             'actual_event_rms_db_vs_wind': 20 * math.log10(rms(event) / wind_rms),
                             'actual_peak_db_vs_wind': 20 * math.log10(float(np.max(np.abs(event))) / wind_peak),
                             'calibration': 'Provisional source-specific audition starting point; not a universal/approved balance'},
              'existing_events_in_clip': {'wind_full_outer_envelope_seconds': [6, 45],
                                          'creak_start_seconds': 10, 'radio_calls': 0},
              'unchanged': ['music', 'wind', 'ventilation', 'creak', 'radio', 'existing event timing'],
              'whole_listening_gain_db': playback_gain, 'independent_normalization': False,
              'validation': {'frames': len(base), 'current_v5_reference_error': reference_error,
                             'exact_new_mix_sum_error': sum_error, 'difference_outside_snow_event': outside_error,
                             'lossless_playback_gain_errors': gain_errors, 'all_outputs_fully_decoded': True},
              'loudness': meters, 'outputs': checks, 'new_paid_calls': 0, 'assistant_listening': False,
              'snow_user_verdict': None, 'full_two_hour_updated': False,
              'implementation_sha256': file_hash(Path(__file__))}
    (out / 'review.json').write_text(json.dumps(recipe, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(out), 'snow_event': recipe['snow_event'],
                      'validation': recipe['validation'], 'loudness': meters}, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--parent', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    run(args.root, args.source, args.parent, args.out)
