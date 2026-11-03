"""Add two sparse, wind-linked snow takes to the unchanged two-hour Snowline V5."""
import argparse
import hashlib
import json
import math
import shutil
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from scipy import signal

from analyze_ambient_audio import loudness
from build_snowline_18min_audition import pcm
from build_snowline_two_hour_mix import FRAMES, file_hash, stream_flac, validate_file, zeros
from generate_polar_comms import decode
from generate_receiver_texture import RATE, rms, write_audio
from render_snowline_wind_and_creaks import mix


def schedule_snow(schedule, count=24, seed=113032):
    """Find irregular4–6minute starts inside wind plateaus, away from other cues."""
    rng = np.random.default_rng(seed)
    forbidden = [(e['start_seconds'] - 6 - 10, e['end_seconds'] + 6)
                 for key in ('radio', 'creaks') for e in schedule[key]['events']]
    ranges = []
    for index, wind in enumerate(schedule['wind']['events']):
        lo = wind['start_seconds'] + wind['fade_in_seconds'] + 1
        hi = wind['end_seconds'] - wind['fade_out_seconds'] - 10 - 1
        pieces = [(max(100, lo), min(7160, hi))]
        for a, b in forbidden:
            updated = []
            for x, y in pieces:
                if b <= x or a >= y:
                    updated.append((x, y))
                else:
                    if x < a:
                        updated.append((x, a))
                    if b < y:
                        updated.append((b, y))
            pieces = updated
        ranges += [(x, y, index) for x, y in pieces if y - x >= .1]
    attempts = 0

    def search(previous, depth):
        nonlocal attempts
        attempts += 1
        if attempts > 10000:
            raise ValueError('Could not fit the selected snow density')
        if depth == count:
            return [] if previous >= 6800 else None
        lo, hi = (140, 260) if depth == 0 else (previous + 240, previous + 360)
        target = 200 if depth == 0 else previous + rng.uniform(270, 330)
        candidates = []
        for a, b, wind_index in ranges:
            left, right = max(a, lo), min(b, hi)
            if right - left >= .05:
                start = round(float(rng.uniform(left, right)) * RATE) / RATE
                candidates.append((abs(start - target) + rng.uniform(0, 15), start, wind_index))
        for _, start, wind_index in sorted(candidates):
            rest = search(start, depth + 1)
            if rest is not None:
                return [{'start_seconds': start, 'end_seconds': start + 10,
                         'wind_event_index': wind_index, 'take_index': depth % 2}] + rest
        return None

    events = search(0, 0)
    if events is None:
        raise ValueError('No valid full-session snow schedule')
    gaps = np.diff([e['start_seconds'] for e in events])
    if len(events) != count or min(gaps) < 240 - 1 / RATE or max(gaps) > 360 + 1 / RATE:
        raise ValueError('Snow spacing differs from requested design')
    for event in events:
        w = schedule['wind']['events'][event['wind_event_index']]
        if not (event['start_seconds'] >= w['start_seconds'] + w['fade_in_seconds'] and
                event['end_seconds'] <= w['end_seconds'] - w['fade_out_seconds']):
            raise ValueError('Snow does not fit the full wind envelope')
        if any(a < event['start_seconds'] < b for a, b in forbidden):
            raise ValueError('Snow conflicts with protected radio/creak cue')
    return events, {'seed': seed, 'count': count, 'onset_intervals_seconds': [float(min(gaps)), float(max(gaps))],
                    'mean_interval_seconds': float(np.mean(gaps)), 'all_inside_wind_plateaus': True,
                    'radio_and_creak_clearance_seconds': 6, 'source_takes_alternate': True,
                    'backtracking_states': attempts, 'coverage_seconds': count * 10}


def snow_blocks(events, takes):
    cursor = 0
    for event in events:
        at = round(event['start_seconds'] * RATE)
        yield from zeros(at - cursor)
        take = takes[event['take_index']]
        for pos in range(0, len(take), 65536):
            yield take[pos:pos + 65536]
        cursor = at + len(take)
    yield from zeros(FRAMES - cursor)


def verify_all(base, snow, master, events, expected_snow_hash):
    streams = [pcm(p) for p in (base, snow, master)]
    digest = hashlib.sha256()
    frames, sum_error, outside_error, peak = 0, 0., 0., 0.
    try:
        while True:
            blocks = [next(s, None) for s in streams]
            if all(b is None for b in blocks):
                break
            if any(b is None for b in blocks) or len({len(b) for b in blocks}) != 1:
                raise ValueError('Full streams differ in duration')
            a, b, c = blocks
            if any(not np.isfinite(x).all() for x in blocks):
                raise ValueError('Non-finite audio')
            active = np.zeros(len(a), dtype=bool)
            for e in events:
                lo = max(0, round(e['start_seconds'] * RATE) - frames)
                hi = min(len(a), round(e['end_seconds'] * RATE) - frames)
                if hi > lo:
                    active[lo:hi] = True
            if np.any(b[~active]):
                raise ValueError('Snow outside its events')
            sum_error = max(sum_error, float(np.max(np.abs(c - (a + b)))))
            if np.any(~active):
                outside_error = max(outside_error, float(np.max(np.abs(c[~active] - a[~active]))))
            peak = max(peak, *(float(np.max(np.abs(x))) for x in blocks))
            digest.update(b.astype('<f4', copy=False).tobytes())
            frames += len(a)
            if frames % (600 * RATE) < 65536:
                print(f'Full snow/mix check: {frames / RATE / 60:.0f}/120 minutes', flush=True)
    finally:
        for s in streams:
            s.close()
    if frames != FRAMES or sum_error != 0 or outside_error != 0 or peak >= 1 or digest.hexdigest() != expected_snow_hash:
        raise ValueError('Full two-hour snow validation failed')
    return {'frames': frames, 'seconds': frames / RATE, 'exact_base_plus_snow_error': sum_error,
            'difference_outside_snow_events': outside_error, 'snow_pcm_matches_event_plan': True,
            'all_samples_finite': True, 'maximum_sample_peak': peak}


def run(root, new_source, out):
    root, new_source, out = [p.resolve() for p in (root, new_source, out)]
    if out.exists() and any(out.iterdir()):
        raise ValueError('Use a fresh output directory')
    case = root / 'creative/music/sound-design/receiver-2026-11-02'
    current = json.loads((case / 'snowline-working-mix-current.json').read_text())
    base = root / current['lossless_assembly_master']['file']
    if 'audio-2h-v5' not in str(base) or file_hash(base) != current['lossless_assembly_master']['sha256']:
        raise ValueError('Expected unchanged V5 parent')
    original_schedule = json.loads((root / 'exports/13-below-the-snowline/audio-2h-v1/recipe.json').read_text())
    gain_review = root / 'exports/13-below-the-snowline/level-tests/snow-grains-gain-v6/review.json'
    gain_data = json.loads(gain_review.read_text())
    selected = gain_data['variants'][0]
    if selected['snow_increment_db_vs_first_test'] != 2:
        raise ValueError('Expected latest1dB reduction from+3 to+2')
    first_stem = gain_review.parent / next(e['file'] for e in selected['outputs'] if e['file'].endswith('snow-adjusted-60s.flac'))
    take_a = decode(first_stem, start=24, seconds=10)
    x = decode(new_source)
    if len(x) != 10 * RATE or np.max(np.abs(x)) >= 1:
        raise ValueError('Review the new take duration/peaks')
    filtered = signal.sosfiltfilt(signal.butter(2, 2800, fs=RATE, output='sos'), x, axis=0)
    for length, rising in ((round(.02 * RATE), True), (round(.08 * RATE), False)):
        edge = .5 - .5 * np.cos(np.linspace(0, np.pi, length))
        if rising:
            filtered[:length] *= edge[:, None]
        else:
            filtered[-length:] *= edge[::-1, None]
    matched_gain = rms(take_a) / rms(filtered)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'source-assets').mkdir()
    (out / 'source-originals').mkdir()
    first_original = root / 'music/sfx-library/assets/snow-grains-ledge-01.mp3'
    for number, source in enumerate((first_original, new_source), 1):
        shutil.copyfile(source, out / f'source-originals/supplied-snow-grains-{number:02d}.mp3')
    takes = []
    for i, audio in enumerate((take_a, (filtered * matched_gain).astype(np.float32)), 1):
        path = out / f'source-assets/snow-take-{i:02d}-placed-level.flac'
        write_audio(audio, path, 'flac')
        takes.append(decode(path))
    rms_match_db = 20 * math.log10(rms(takes[1]) / rms(takes[0]))
    if abs(rms_match_db) > .002 or np.max(np.abs(takes)) >= 1 or np.max(np.abs(takes[0] - take_a)) != 0:
        raise ValueError('Source placement calibration failed')
    events, scheduling = schedule_snow(original_schedule)
    for event in events:
        event['source_file'] = f'source-assets/snow-take-{event["take_index"] + 1:02d}-placed-level.flac'
    stem = out / 'Snowline-snow-2h-v6.flac'
    print('Writing24 alternating snow events at the selected+2dB level...', flush=True)
    snow_info = stream_flac(snow_blocks(events, takes), stem)
    master = out / 'Below-the-Snowline-2-Hours-unfaded-master-v6.flac'
    print('Adding snow to unchanged V5; all prior layer levels and timings retained...', flush=True)
    mix([base, stem], master)
    print('Checking every full-length sample against the snow cue plan...', flush=True)
    validation = verify_all(base, stem, master, events, snow_info['expected_decoded_pcm_sha256'])
    full = out / 'Below-the-Snowline-2-Hours-v6.mp3'
    gain = current['mp3']['listening_gain_db']
    print('Encoding the full two hours at fixed playback gain with one closing fade...', flush=True)
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff, '-v', 'error', '-i', str(master), '-af', f'volume={gain:.15g}dB,afade=t=out:st=7180:d=20',
                    '-c:a', 'libmp3lame', '-b:a', '192k', '-n', str(full)], capture_output=True, check=True)
    full_check = validate_file(full, 7200)
    meter = out / 'meter'
    meter.mkdir()
    measured = loudness(full, ff, meter)
    previews = []
    for take_index in (0, 1):
        event = next(e for e in events if e['take_index'] == take_index)
        begin = event['start_seconds'] - 4
        target = out / f'Snow-take-{take_index + 1:02d}-in-full-mix-20s.mp3'
        subprocess.run([ff, '-v', 'error', '-ss', f'{begin:.12f}', '-i', str(master), '-t', '20',
                        '-af', f'volume={gain:.15g}dB', '-c:a', 'libmp3lame', '-b:a', '192k',
                        '-n', str(target)], capture_output=True, check=True)
        check = validate_file(target, 20)
        previews.append({'file': target.name, 'source_start_seconds': begin, 'snow_at_seconds': 4,
                         'take_index': take_index, 'validation': check})
    if file_hash(base) != current['lossless_assembly_master']['sha256']:
        raise ValueError('Parent master changed')
    record = {'date': '2026-11-03', 'user_request': 'go down1moreDB, add this take, regenerate2hours with snow about every5minutes, commit/push everything today',
              'seconds': 7200, 'parent_master': {'file': base.relative_to(root).as_posix(), 'sha256': file_hash(base)},
              'prior_source_stems': json.loads((base.parent / 'recipe.json').read_text())['source_stems'],
              'first_take_gain_db_vs_initial_snow_trial': 2, 'delta_db_vs_previous_plus3_trial': -1,
              'first_take_prepared_stem': {'file': first_stem.relative_to(root).as_posix(), 'sha256': file_hash(first_stem)},
              'sources': [{'file': f'source-originals/supplied-snow-grains-{i:02d}.mp3', 'sha256': file_hash(p),
                           'bytes': p.stat().st_size, 'decoded_seconds': 10} for i, p in enumerate((first_original, new_source), 1)],
              'new_take_processing': {'lowpass_hz': 2800, 'order': 2, 'zero_phase': True,
                                      'edge_fades_seconds': [.02, .08], 'gain_after_filter_db': 20 * math.log10(matched_gain),
                                      'rms_match_to_reduced_first_take_db': rms_match_db,
                                      'note': 'Provisional event-wide RMS match, not proof of equal perceived loudness; no copied raw-source gain.'},
              'schedule': scheduling, 'events': events, 'validation': validation,
              'counts': {'radio_calls': 47, 'wind_passages': 80, 'creaks': 24, 'snow_passages': 24, 'snow_source_takes': 2},
              'source_take_uses': [12, 12], 'original_five_layers_unchanged': True,
              'delivery_processing': {'listening_gain_db': gain, 'mp3_opening_fade': False, 'mp3_closing_fade_seconds': 20,
                                      'lossless_master': 'Unity V5-plus-snow sum, no playback gain or opening/closing fades. Apply+0.4dB once to match listening level; intro/closing once during assembly, no extra SFX.'},
              'previews': previews, 'mp3_check': full_check, 'listening_loudness': measured,
              'outputs': [{'file': p.name, 'bytes': p.stat().st_size, 'sha256': file_hash(p)} for p in (stem, master, full)],
              'full_two_hour_user_verdict': None, 'new_take_in_mix_user_verdict': None,
              'executed_generation_prompt_model_settings_cost': None, 'assistant_listening': False,
              'new_paid_calls': 0, 'video_assembled': False, 'implementation_sha256': file_hash(Path(__file__))}
    (out / 'recipe.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    stamp = lambda t: f'{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{t % 60:06.3f}'
    lines = ['Below the Snowline — V6 snow additions; original radio/wind/creak cues unchanged.']
    lines += [f'{stamp(e["start_seconds"])} - {stamp(e["end_seconds"])} | take{e["take_index"] + 1} | wind{e["wind_event_index"] + 1}' for e in events]
    (out / 'snow-cue-sheet.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(out), 'snow_schedule': scheduling, 'validation': validation, 'loudness': measured}, indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--new-source', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    run(a.root, a.new_source, a.out)
