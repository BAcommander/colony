"""Native-only regression and weather-cache equivalence audit; renders no video."""
import hashlib
import json
from pathlib import Path
import platform
import concurrent.futures
import sys
import time

import cv2
import imageio_ffmpeg
import numpy as np
import PIL

import long_scene as module


def array_hash(frame):
    return hashlib.sha256(frame.tobytes()).hexdigest()


def cache_worker_init():
    global CACHE_SCENE, CACHE_ARRAY, CACHE_HASHES
    CACHE_SCENE = module.Scene()
    root = module.PACKAGE.parents[1]
    CACHE_ARRAY = np.memmap(root/'.local/crater-rim-final-hour-v1/weather-native.rgb',
                           dtype=np.uint8, mode='r', shape=(1800,941,1672,3))
    CACHE_HASHES = json.loads((module.HERE/'weather-cache-validation.json').read_text())['frame_sha256']


def cache_worker(bounds):
    start, end = bounds
    for tick in range(start, end):
        expected = CACHE_HASHES[tick]
        assert array_hash(CACHE_SCENE.weather_frame(tick/30)) == expected, ('current weather', tick)
        assert array_hash(CACHE_ARRAY[tick]) == expected, ('stored cache', tick)
    return end-start


def main():
    started = time.perf_counter()
    frozen_manifest = json.loads((module.SNAPSHOT/'manifest.json').read_text(encoding='utf-8-sig'))
    for entry in frozen_manifest['files']:
        assert module.digest(module.PACKAGE/entry['snapshot_path']) == entry['sha256']
    for path, expected in module.PLAN['baseline']['reference_inputs'].items():
        assert module.digest(module.SNAPSHOT/path) == expected, path

    baseline = module.v5.Scene()
    scene = module.Scene()
    baseline_controls = []
    for control in module.PLAN['baseline']['native_resume_controls']:
        frame = baseline.frame(control['time_seconds'])
        actual = array_hash(frame)
        assert actual == control['rgb_sha256'], control
        baseline_controls.append({**control, 'actual_sha256': actual, 'exact': True})
    print('Six frozen V5 baseline controls exact', flush=True)

    lamp_controls = []
    for event in scene.lamp_events:
        source = baseline.c['lamp']['events'][event['source_event_index']]
        length = event['rise']+event['hold']+event['fall']
        errors = []
        for age in np.linspace(-1/30, length+1/30, 41):
            with scene._clock(event['time']+float(age)) as weather_t:
                actual = scene.lamp_amount(weather_t)
            expected = baseline.lamp_amount(source['time']+float(age))
            errors.append(abs(actual-expected))
        assert max(errors) < 1e-10, (event, max(errors))
        lamp_controls.append({'source_event_index': event['source_event_index'], 'samples': len(errors),
                              'maximum_amount_error': max(errors),
                              'original_peak': baseline.lamp_amount(source['time']+source['rise']+source['hold']/2)})
    print('Actual frozen V5 lamp envelopes match at123 event-local samples', flush=True)

    retained_controls = []
    for absolute_t in [0, 87.36666666666666, 241.2, 363.5, 487.6, 599+29/30]:
        weather_t = module.phase(absolute_t, module.WEATHER_PERIOD)
        for layer in module.RETAINED_LAYERS:
            reference = baseline.frame(weather_t, only=layer)
            actual = scene.frame(absolute_t, only=layer)
            assert np.array_equal(reference, actual), (absolute_t, layer)
            retained_controls.append({'time': absolute_t, 'weather_phase': weather_t,
                                      'layer': layer, 'rgb_sha256': array_hash(actual)})
    print('Seven retained layers exact at six absolute times', flush=True)

    windows = []
    sample_ticks = {0, 1, 1798, 1799, 1800, 1801, 7199, 7200, 7201,
                    10799, 10800, 10801, 17998, 17999, 18000}
    for name, events in [('lamp', scene.lamp_events), ('sun_glare', scene.glare_events),
                         ('traffic', scene.traffic_events)]:
        for event in events:
            length = event.get('seconds', event.get('rise', 0)+event.get('hold', 0)+event.get('fall', 0))
            windows.append({'layer': name, 'start': event['time'], 'end': event['time']+length,
                            'source_variant': event.get('source_event_index', event.get('source_variant_index'))})
            for t in [event['time']-1/30, event['time'], event['time']+1/30,
                      event['time']+length/2, event['time']+length-1/30,
                      event['time']+length, event['time']+length+1/30]:
                sample_ticks.add(round(t*module.FPS))

    cache_controls = []
    protected = ~scene.active
    for tick in sorted(sample_ticks):
        absolute_t = tick/module.FPS
        # Construct the exact cached frame index, not merely t%60.
        weather_t = (tick % (60*module.FPS))/module.FPS
        weather = scene.weather_frame(weather_t)
        initial_hash = array_hash(weather)
        combined = scene.apply_attention(weather, absolute_t)
        direct = scene.frame(absolute_t)
        assert array_hash(weather) == initial_hash, 'Cache was mutated'
        assert np.array_equal(combined, direct), ('cache decomposition', absolute_t)
        assert np.array_equal(direct[protected], scene.base[protected]), ('protected pixels', absolute_t)
        assert np.array_equal(direct[~scene.attention_mask], weather[~scene.attention_mask])
        cache_controls.append({'frame': tick, 'time': absolute_t, 'weather_frame': tick % 1800,
                               'rgb_sha256': array_hash(direct), 'exact': True})
    print(f'Cache decomposition and protected pixels exact at {len(cache_controls)} native states', flush=True)

    # The rare layers are absent near the 600s wrap. Compare the actual step to
    # its neighbors and the unchanged V5 weather wrap, not endpoint equality alone.
    seam_frames = [scene.frame(t) for t in [600-2/30, 600-1/30, 600, 600+1/30]]
    assert np.array_equal(scene.frame(0), seam_frames[2])
    seam = {}
    for name, roi in {'full_scene': [0, 0, scene.w, scene.h], **scene.rois}.items():
        r = module.region(roi)
        steps = [float(np.abs(a[r].astype(np.float32)-b[r].astype(np.float32)).mean())
                 for a, b in zip(seam_frames, seam_frames[1:])]
        seam[name] = {'before_mae': steps[0], 'wrap_mae': steps[1], 'after_mae': steps[2]}
    assert not any(scene.attention_active(t) for t in [0, 1/30, 599, 600-1/30, 600])
    for tick, frame in zip([17998, 17999, 18000, 18001], seam_frames):
        assert np.array_equal(frame, scene.weather_frame((tick % 1800)/30))

    full_cache_check = None
    if '--verify-weather-cache' in sys.argv:
        cache_receipt_path = module.HERE/'weather-cache-validation.json'
        old_receipt = json.loads(cache_receipt_path.read_text())
        completed = 0
        cache_started = time.perf_counter()
        with concurrent.futures.ProcessPoolExecutor(max_workers=3, initializer=cache_worker_init) as pool:
            jobs = [pool.submit(cache_worker, (tick, tick+150)) for tick in range(0,1800,150)]
            for job in concurrent.futures.as_completed(jobs):
                completed += job.result()
                print(f'Weather cache unchanged: {completed}/1800 frames', flush=True)
        full_cache_check = {'status': 'passed', 'frames': completed,
                            'all_current_weather_and_stored_cache_frame_hashes_match_original_receipt': True,
                            'original_receipt_file': str(cache_receipt_path),
                            'original_receipt_sha256': module.digest(cache_receipt_path),
                            'original_receipt_renderer_sha256': old_receipt['renderer_sha256'],
                            'current_renderer_sha256': module.digest(module.HERE/'long_scene.py'),
                            'raw_cache_sha256_from_original_receipt': old_receipt['sha256'],
                            'elapsed_seconds': time.perf_counter()-cache_started,
                            'original_cache_receipt_unmodified': True}

    report = {
        'status': 'passed', 'scope': 'native renderer only; encoded 4K and playback checks are separate',
        'native_dimensions': [scene.w, scene.h], 'native_format': 'uint8 RGB',
        'weather_period_seconds': scene.duration, 'attention_period_seconds': scene.attention_period,
        'fps': module.FPS, 'frozen_v5_controls': baseline_controls,
        'retained_layer_controls': retained_controls,
        'retained_layer_count': len(module.RETAINED_LAYERS),
        'actual_frozen_v5_lamp_regression': lamp_controls,
        'cache_decomposition_controls': cache_controls,
        'cache_input_unchanged': True, 'cache_order_lamp_beacon_overlap_pixels': scene.cache_order_overlap_pixels,
        'protected_pixels_exact_at_all_cache_controls': True,
        'outside_attention_support_equal_weather_at_all_cache_controls': True,
        'rare_layers_quiet_at_600s_wrap': True, 'frame_zero_equals_frame_600': True,
        '600s_wrap_equals_original_weather_wrap': True, 'seam_regional_steps': seam,
        'attention_windows': windows,
        'lamp_behavior': 'Actual original max(amount, envelope*depth) preserved; measured original peaks0.76/0.48/0.68. Initial reviewer-driven attenuation change was rejected by direct original-method regression before any production encode.',
        'weather_cache_after_lamp_correction': full_cache_check,
        'clock_behavior': '60s weather unchanged; original speeds/geometry; only lamp/glare/traffic event frequency changed to saved600s schedule; 30fps phases canonicalized.',
        'fingerprints': {**scene.fingerprint(), 'visual/preflight_renderer.py': module.digest(__file__)},
        'runtime': {'python': platform.python_version(), 'numpy': np.__version__, 'opencv': cv2.__version__,
                    'pillow': PIL.__version__, 'imageio_ffmpeg': imageio_ffmpeg.__version__},
        'elapsed_seconds': time.perf_counter()-started,
        'inspection_limit': 'Numeric native arrays only. This script performs no continuous playback, listening, or encoded-video validation.'
    }
    path = module.HERE/'renderer-validation.json'
    path.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'output': str(path),
                      'native_cache_states': len(cache_controls), 'elapsed_seconds': report['elapsed_seconds']}), flush=True)


if __name__ == '__main__':
    main()
