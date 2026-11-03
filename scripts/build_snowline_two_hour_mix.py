"""Stream a two-hour Snowline soundtrack with a full-session SFX arrangement."""
import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from scipy import signal

from analyze_ambient_audio import loudness
from build_snowline_18min_audition import pcm, peak_multiplier
from build_snowline_environment import event_envelope
from generate_polar_comms import decode
from generate_receiver_texture import RATE, rms, write_audio
from render_snowline_wind_and_creaks import overlapping_sections, mix

SECONDS = 7200
FRAMES = SECONDS * RATE
CHUNK = 65536


def file_hash(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def zeros(frames):
    while frames:
        n = min(frames, CHUNK)
        yield np.zeros((n, 2), dtype=np.float32)
        frames -= n


def circular(source):
    count = 0
    while count < FRAMES:
        stream = pcm(source)
        read = 0
        try:
            for block in stream:
                take = min(len(block), FRAMES - count)
                yield block[:take]
                count += take
                read += take
                if count == FRAMES:
                    break
        finally:
            stream.close()
        if not read:
            raise ValueError('Empty looping source')


def sequence(prefix, events, trace):
    cursor = 0
    for block in pcm(prefix):
        cursor += len(block)
        yield block
    if cursor != 1080 * RATE:
        raise ValueError('Expected exact18-minute prefix')
    for event in events:
        at = round(event['start_seconds'] * RATE)
        if at < cursor:
            raise ValueError('Overlapping or out-of-order event')
        yield from zeros(at - cursor)
        cursor = at
        start = cursor
        for block in pcm(event['file']):
            cursor += len(block)
            yield block
        if cursor - start != event['frames']:
            raise ValueError('Event source duration differs')
        trace.append({'start_frame': start, 'end_frame': cursor,
                      'source': str(event['file']), 'source_sha256': file_hash(event['file'])})
    if cursor > FRAMES:
        raise ValueError('Event overruns soundtrack')
    yield from zeros(FRAMES - cursor)


def stream_flac(blocks, target):
    p = subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-f', 'f32le',
                          '-ar', str(RATE), '-ac', '2', '-i', 'pipe:0', '-c:a', 'flac',
                          '-sample_fmt', 's32', '-bits_per_raw_sample', '24', '-n', str(target)],
                         stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    h, frames = hashlib.sha256(), 0
    try:
        for block in blocks:
            raw = block.astype('<f4', copy=False).tobytes()
            p.stdin.write(raw)
            h.update(raw)
            frames += len(block)
        p.stdin.close()
        error = p.stderr.read()
        if p.wait():
            raise ValueError(error.decode(errors='replace'))
    finally:
        if p.poll() is None:
            p.kill()
        p.wait()
    if frames != FRAMES:
        raise ValueError(f'Wrong streamed duration: {frames}')
    return {'frames': frames, 'expected_decoded_pcm_sha256': h.hexdigest()}


def validate_all(stems, master, expected):
    streams = [pcm(p) for p in stems + [master]]
    hashes = [hashlib.sha256() for _ in streams]
    peaks = [0.] * len(streams)
    frames, error = 0, 0.
    try:
        while True:
            blocks = [next(s, None) for s in streams]
            if all(x is None for x in blocks):
                break
            if any(x is None for x in blocks) or len({len(x) for x in blocks}) != 1:
                raise ValueError('Unequal delivery durations')
            summed = blocks[0].copy()
            for b in blocks[1:-1]:
                summed += b
            error = max(error, float(np.max(np.abs(blocks[-1] - summed))))
            for i, b in enumerate(blocks):
                if not np.isfinite(b).all():
                    raise ValueError('Non-finite audio')
                peaks[i] = max(peaks[i], float(np.max(np.abs(b))))
                hashes[i].update(b.astype('<f4', copy=False).tobytes())
            frames += len(blocks[0])
            if frames // RATE % 600 < 2 and frames % (600 * RATE) < CHUNK:
                print(f'Full sample check: {frames / RATE / 60:.0f}/120 minutes', flush=True)
    finally:
        for s in streams:
            s.close()
    if frames != FRAMES or error > 3e-7 or max(peaks) >= 1:
        raise ValueError(f'Delivery check failed: {frames}, {error}, {peaks}')
    for i, item in enumerate(expected):
        if hashes[i].hexdigest() != item['expected_decoded_pcm_sha256']:
            raise ValueError(f'Stem differs from streamed source plan: {stems[i]}')
    return {'frames': frames, 'seconds': frames / RATE, 'max_five_stem_sum_error': error,
            'all_stem_pcm_hashes_match_source_plan': True, 'all_samples_finite': True,
            'sample_peaks': peaks, 'pcm_sha256': [h.hexdigest() for h in hashes]}


def validate_file(path, seconds):
    frames, peak = 0, 0.
    for block in pcm(path):
        if not np.isfinite(block).all():
            raise ValueError('Non-finite encoded audio')
        peak = max(peak, float(np.max(np.abs(block))))
        frames += len(block)
    if frames != seconds * RATE or peak >= 1:
        raise ValueError(f'Encoded file failed: {frames}, {peak}')
    return {'frames': frames, 'seconds': frames / RATE, 'sample_peak': peak,
            'finite': True, 'sha256': file_hash(path), 'bytes': path.stat().st_size}


def verify_creak_gain(before, after):
    streams = [pcm(p) for p in [before, after]]
    frames, error = 0, 0.
    try:
        while True:
            a, b = [next(s, None) for s in streams]
            if a is None and b is None:
                break
            if a is None or b is None or len(a) != len(b):
                raise ValueError('Creak reference lengths differ')
            error = max(error, float(np.max(np.abs(b.astype(float) - a.astype(float) * 1.1))))
            frames += len(a)
    finally:
        for s in streams:
            s.close()
    if frames != 1080 * RATE or error > 1.3e-7:
        raise ValueError(f'Creak increase differs: {frames}, {error}')
    return {'frames': frames, 'amplitude_multiplier': 1.1, 'max_gain_error': error}


def verify_prefix(previous, old_creaks, new_creaks, master):
    streams = [pcm(p) for p in [previous, old_creaks, new_creaks, master]]
    frames, error, outside = 0, 0., 0.
    try:
        while frames < 1080 * RATE:
            blocks = [next(s, None) for s in streams]
            if any(x is None for x in blocks):
                raise ValueError('Incomplete prefix')
            n = min(len(x) for x in blocks)
            n = min(n, 1080 * RATE - frames)
            a, old, new, actual = [x[:n] for x in blocks]
            error = max(error, float(np.max(np.abs((actual - a) - (new - old)))))
            quiet = np.all(old == 0, axis=1)
            if np.any(quiet):
                outside = max(outside, float(np.max(np.abs(actual[quiet] - a[quiet]))))
            frames += n
    finally:
        for s in streams:
            s.close()
    if error > 3e-7 or outside != 0:
        raise ValueError(f'Opening18-minute preservation failed: {error}, {outside}')
    return {'frames': frames, 'max_creak_only_revision_error': error,
            'max_change_outside_creaks': outside}


def make_wind_clip(source, start, duration, up, down, index, recipe, target):
    desired = recipe['wind']['reference_core_rms']
    ceiling = recipe['wind']['reference_sample_peak']
    sos = signal.butter(2, 1800, fs=RATE, output='sos')
    best = None
    for attempt in range(4):
        seed = 723100 + index * 10 + attempt
        rng = np.random.default_rng(seed)
        x, grains = overlapping_sections(source, duration * RATE, rng)
        x = signal.sosfiltfilt(sos, x, axis=0)
        t = np.arange(len(x)) / RATE
        env = event_envelope(len(x), RATE, up, down)
        movement = .88 + .08 * np.sin(2 * np.pi * t / (duration * .79) + rng.uniform(0, 6))
        movement += .04 * np.sin(2 * np.pi * t / (duration * .43) + rng.uniform(0, 6))
        x *= (env * movement)[:, None]
        calibration = desired / rms(x[up * RATE:(duration - down) * RATE])
        x *= calibration
        peak = float(np.max(np.abs(x)))
        if best is None or peak < best[0]:
            best = (peak, x, seed, grains, calibration)
        if peak <= ceiling:
            break
    peak, x, seed, grains, calibration = best
    guard = min(1., ceiling / peak)
    unlifted = (x * guard).astype(np.float32)
    multiplier = peak_multiplier(event_envelope(len(x), RATE, up, down))
    lifted = (unlifted * multiplier[:, None]).astype(np.float32)
    if not np.array_equal(lifted[multiplier == 1], unlifted[multiplier == 1]):
        raise ValueError('Quieter wind buildup changed')
    write_audio(lifted, target, 'flac')
    return {'start_seconds': start, 'end_seconds': start + duration, 'duration_seconds': duration,
            'fade_in_seconds': up, 'fade_out_seconds': down, 'seed': seed, 'grains': grains,
            'calibration_gain': calibration, 'linear_crest_guard': guard,
            'unlifted_peak': float(np.max(np.abs(unlifted))),
            'lifted_peak_before_encoding': float(np.max(np.abs(lifted))),
            'peak_region_max_multiplier': 1.1, 'quieter_buildup_exact': True,
            'file': target, 'frames': len(lifted)}


def run(root, out):
    root, out = root.resolve(), out.resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError('Use a fresh destination')
    prior = root / 'exports/sfx/snowline-18min-2026-11-03/v1'
    p = json.loads((prior / 'recipe.json').read_text(encoding='utf-8'))
    radio_parent = root / 'exports/sfx/snowline-receiver-2026-11-02/full-session-v1'
    r = json.loads((radio_parent / 'recipe.json').read_text(encoding='utf-8'))
    source_by_name = {e['file']: e for e in p['sources']}
    music = root / next(k for k in source_by_name if k.endswith('Below-the-Snowline-paired-loop-9min-v1.flac'))
    vent = root / next(k for k in source_by_name if k.endswith('Snowline-ventilation-9min-v2.flac'))
    wind_source = root / next(k for k in source_by_name if k.endswith('wind-soft-exterior-01.mp3'))
    sources = [(root / k, e['sha256']) for k, e in source_by_name.items()]
    for e in p['outputs']:
        sources.append((prior / e['file'], e['sha256']))
    for path, expected in sources:
        if file_hash(path) != expected:
            raise ValueError(f'Prior source changed: {path}')
    out.mkdir(parents=True, exist_ok=True)
    stems_dir = out / 'stems'
    assets = out / 'source-assets'
    for folder in [stems_dir, assets / 'radio', assets / 'wind', assets / 'creaks']:
        folder.mkdir(parents=True, exist_ok=True)
    print('Preparing14 existing receiver packets at unchanged per-event gain...', flush=True)
    packet_assets = []
    for i, e in enumerate(r['events']):
        source = radio_parent / e['packet_file']
        if file_hash(source) != e['packet_sha256']:
            raise ValueError('Original radio packet changed')
        x = decode(source) * r['radio_source_gain']
        target = assets / 'radio' / f'packet-{i + 1:02d}.flac'
        write_audio(x, target, 'flac')
        packet_assets.append({'file': target, 'frames': len(x), 'lead_seconds': e['lead_seconds'],
                              'source_phrase_sha256': e['source_sha256'],
                              'acknowledgement': e['acknowledgement'], 'original_packet_sha256': e['packet_sha256']})
    print('Raising existing creaks another10% (+0.83dB)...', flush=True)
    old_creaks = prior / 'Snowline-creaks-18min-v1.flac'
    new_prefix = assets / 'creaks' / 'opening18min-creaks-plus10.flac'
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-i', str(old_creaks),
                    '-af', 'volume=1.1', '-c:a', 'flac', '-sample_fmt', 's32', '-bits_per_raw_sample', '24',
                    '-n', str(new_prefix)], capture_output=True, check=True)
    creak_gain_check = verify_creak_gain(old_creaks, new_prefix)
    creak_assets = []
    for i, t in enumerate([91, 338]):
        x = decode(new_prefix, start=t, seconds=4)
        target = assets / 'creaks' / f'creak-{i + 1}.flac'
        write_audio(x, target, 'flac')
        creak_assets.append({'file': target, 'frames': len(x)})
    rng = np.random.default_rng(723031)
    radio_events = []
    voice_time = p['radio']['events'][-1]['voice_start_seconds']
    bag, recent = [], [2, 8]
    while True:
        voice_time += int(rng.integers(120, 181))
        if voice_time > SECONDS - 35:
            break
        if not bag:
            bag = rng.permutation(len(packet_assets)).tolist()
        choice = next(i for i, value in enumerate(bag) if value not in recent[-2:]) if any(value not in recent[-2:] for value in bag) else 0
        index = bag.pop(choice)
        recent.append(index)
        a = packet_assets[index]
        radio_events.append({**a, 'voice_start_seconds': voice_time,
                             'start_seconds': round((voice_time - a['lead_seconds']) * RATE) / RATE,
                             'end_seconds': round((voice_time - a['lead_seconds']) * RATE) / RATE + a['frames'] / RATE,
                             'source_gain_already_applied': r['radio_source_gain'], 'packet_index': index})
    radio_all = p['radio']['events'] + radio_events
    radio_intervals = np.diff([e['voice_start_seconds'] for e in radio_all])
    if not np.all((radio_intervals >= 120) & (radio_intervals <= 180)):
        raise ValueError('Radio intervals outside requested2-3minutes')
    rng = np.random.default_rng(723032)
    wind_plan = []
    cursor = p['wind']['events'][-1]['end_seconds']
    while True:
        start = int(cursor + rng.integers(22, 32))
        duration = min(int(rng.integers(49, 75)), SECONDS - 12 - start)
        up, down = int(rng.integers(10, 15)), int(rng.integers(15, 21))
        if duration < up + down + 8:
            break
        wind_plan.append((start, duration, up, down))
        cursor = start + duration
    rng = np.random.default_rng(723033)
    creak_events = []
    cursor = p['creaks']['events'][-1]['start_seconds']
    i = len(p['creaks']['events'])
    while True:
        cursor += int(rng.integers(230, 351))
        if cursor > SECONDS - 45:
            break
        a = creak_assets[i % 2]
        creak_events.append({**a, 'start_seconds': cursor, 'end_seconds': cursor + 4,
                             'position': 'right' if i % 2 == 0 else 'left'})
        i += 1
    print(f'Planned full session: {len(radio_all)} radio calls, {len(wind_plan) + 12} wind passages, {len(creak_events) + 4} creaks.', flush=True)
    source = decode(wind_source)
    wind_events = []
    for i, (s, d, up, down) in enumerate(wind_plan):
        target = assets / 'wind' / f'wind-{i + 13:03d}.flac'
        wind_events.append(make_wind_clip(source, s, d, up, down, i, p, target))
        if (i + 1) % 10 == 0 or i + 1 == len(wind_plan):
            print(f'New wind passages prepared: {i + 1}/{len(wind_plan)}', flush=True)
    del source
    wind_all = p['wind']['events'] + wind_events
    wind_gaps = [wind_all[i + 1]['start_seconds'] - wind_all[i]['end_seconds'] for i in range(len(wind_all) - 1)]
    if min(wind_gaps) < 22 or max(wind_gaps) > 31:
        raise ValueError('Wind gaps differ from current balance')
    paths = {name: stems_dir / f'Snowline-{name}-2h-v1.flac'
             for name in ['music', 'radio', 'wind', 'ventilation', 'creaks']}
    trace = {}
    plans = {}
    for name, source in [('music', music), ('ventilation', vent)]:
        print(f'Streaming two-hour {name} source...', flush=True)
        plans[name] = stream_flac(circular(source), paths[name])
    for name, prefix, events in [
        ('radio', prior / 'Snowline-radio-18min-v1.flac', radio_events),
        ('wind', prior / 'Snowline-wind-18min-v1.flac', wind_events),
        ('creaks', new_prefix, creak_events)]:
        print(f'Streaming full-session {name} arrangement...', flush=True)
        trace[name] = []
        plans[name] = stream_flac(sequence(prefix, events, trace[name]), paths[name])
    master = out / 'Below-the-Snowline-2-Hours-unfaded-master-v1.flac'
    ordered = [paths[name] for name in ['music', 'radio', 'wind', 'ventilation', 'creaks']]
    print('Mixing full two-hour lossless master...', flush=True)
    mix(ordered, master)
    listening = out / 'Below-the-Snowline-2-Hours-v1.mp3'
    gain = p['whole_listening_gain_db']
    print('Encoding two-hour listening copy with one20-second closing fade...', flush=True)
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-i', str(master),
                    '-af', f'volume={gain:.15g}dB,afade=t=out:st=7180:d=20',
                    '-c:a', 'libmp3lame', '-b:a', '192k', '-n', str(listening)],
                   capture_output=True, check=True)
    preview = out / 'Creak-plus10-percent-90s-check.mp3'
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-i', str(master), '-ss', '54', '-t', '90',
                    '-af', f'volume={gain:.15g}dB', '-c:a', 'libmp3lame', '-b:a', '192k', '-n', str(preview)],
                   capture_output=True, check=True)
    print('Verifying all345,600,000 frames of every stem and the full lossless mix...', flush=True)
    validation = validate_all(ordered, master, [plans[name] for name in ['music', 'radio', 'wind', 'ventilation', 'creaks']])
    validation['opening18min_creak_only_change'] = verify_prefix(
        prior / 'Snowline-18min-sparse-radio-stronger-wind-v1.flac', old_creaks, new_prefix, master)
    validation['creak_gain'] = creak_gain_check
    print('Decoding the complete MP3 and checking loudness...', flush=True)
    mp3_check = validate_file(listening, SECONDS)
    preview_check = validate_file(preview, 90)
    meter = out / 'meter'
    meter.mkdir()
    measured = loudness(listening, imageio_ffmpeg.get_ffmpeg_exe(), meter)
    for path, expected in sources:
        if file_hash(path) != expected:
            raise ValueError('Original source changed')
    def serialise(value):
        if isinstance(value, Path):
            return value.relative_to(root).as_posix()
        raise TypeError(type(value).__name__)
    outputs = [{'file': path.relative_to(out).as_posix(), 'bytes': path.stat().st_size,
                'sha256': file_hash(path), 'seconds': SECONDS}
               for path in ordered + [master, listening]]
    record = {'date': '2026-11-03', 'user_request': 'can the creaks be 10% lounder and can we make a full 2 hour mix',
              'seconds': SECONDS, 'extension_authorized_from18min': True, 'full_session_review': None,
              'sources': [{'file': path.relative_to(root).as_posix(), 'sha256': h} for path, h in sources],
              'music': {'nine_minute_source_repeated': True, 'full_repeats': 13, 'tail_seconds': 180, 'gain': 1},
              'ventilation': {'nine_minute_source_repeated': True, 'gain': 1},
              'radio': {'events': radio_all, 'count': len(radio_all), 'unique_phrase_sources_available': 14,
                        'voice_interval_min_max_seconds': [int(min(radio_intervals)), int(max(radio_intervals))],
                        'reused_existing_packets_in_varied_orders': True, 'same_per_event_gain': r['radio_source_gain'],
                        'whole_source_rms_normalized': False},
              'wind': {'events': wind_all, 'count': len(wind_all), 'off_gaps_min_max_seconds': [min(wind_gaps), max(wind_gaps)],
                       'coverage_seconds': sum(e['duration_seconds'] for e in wind_all),
                       'same18min_peak_processing_and_source': True, 'peak_region_multiplier': 1.1,
                       'one_original_recording': True, 'source_fragments_can_recur': True},
              'creaks': {'events': p['creaks']['events'] + creak_events, 'count': len(creak_events) + 4,
                         'additional_amplitude_multiplier_vs18min': 1.1,
                         'cumulative_multiplier_vs_first_supplied_audition': 1.21,
                         'additional_db': 20 * math.log10(1.1), 'one_original_supplied_take': True},
              'arrangement': {'first18minutes_preserved_except_creaks': True,
                              'full_two_hour_effect_schedule': True, 'composite18min_not_tiled': True},
              'streamed_stem_plans': plans, 'appended_event_frame_trace': trace,
              'validation': validation, 'mp3_check': mp3_check, 'preview_check': preview_check,
              'listening_loudness': measured, 'outputs': outputs,
              'delivery_processing': {'lossless_master': 'Unfaded, unity stems; use for assembly and apply opening/closing once.',
                                      'mp3': 'Same+0.4dB listening gain; no baked opening fade; one20s closing fade.',
                                      'listening_gain_db': gain, 'opening_fade_added': False, 'closing_fade_seconds': 20},
              'new_paid_calls': 0, 'assistant_listening': False, 'new_video_assembled': False,
              'current_accepted_preset_replaced': False, 'implementation_sha256': file_hash(Path(__file__))}
    (out / 'recipe.json').write_text(json.dumps(record, indent=2, default=serialise) + '\n', encoding='utf-8')
    def stamp(t):
        return f'{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}'
    cues = ['Below the Snowline — two-hour sound design', 'Times are from the full soundtrack.', '', 'RADIO VOICE STARTS']
    cues += [stamp(e['voice_start_seconds']) for e in radio_all]
    cues += ['', 'WIND PASSAGES (INCLUDING FADES)'] + [stamp(e['start_seconds']) + ' - ' + stamp(e['end_seconds']) for e in wind_all]
    cues += ['', 'CREAKS'] + [stamp(e['start_seconds']) for e in p['creaks']['events'] + creak_events]
    (out / 'cue-sheet.txt').write_text('\n'.join(cues) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(out.resolve()), 'seconds': SECONDS, 'radio_calls': len(radio_all),
                      'radio_interval_seconds': [int(min(radio_intervals)), int(max(radio_intervals))],
                      'wind_passages': len(wind_all), 'creaks': len(creak_events) + 4,
                      'loudness': measured, 'validation': validation}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    run(args.root.resolve(), args.out)
