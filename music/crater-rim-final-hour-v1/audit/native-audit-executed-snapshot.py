"""Independent original-V5 recipe, event-clock and 4K colour audit.

Writes only this audit directory. No long video encoding. The reference loads
the original V5 outside the production snapshot and remaps its actual output.
"""
import argparse
from contextlib import contextmanager
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
JOB = HERE.parent
ROOT = JOB.parents[1]
ORIGINAL = ROOT/'music/crater-rim-animation-v5'
FPS, PERIOD = 30, 600
FFMPEG = shutil.which('ffmpeg')
MASTER = ROOT/'exports/14-crater-rim-survey/production-v1/Crater-Rim-Survey-clean-600s-4K.mp4'
ATTENTION = ('lamp', 'sun_glare', 'traffic')
RETAINED = ('clouds', 'haze', 'shadows', 'survey', 'windows', 'village', 'village_lights')


def digest(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def save(name, value):
    (HERE/name).write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def original_renderer():
    names = ('dust_transport', 'periodic_transport', 'v2_renderer_snapshot', 'v3_renderer_snapshot', 'render_scene')
    previous = {name: sys.modules.get(name) for name in names}
    paths = sys.path.copy()
    try:
        for name in names:
            path = ORIGINAL/('dependencies' if name in names[:2] else '')/(name+'.py')
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
        return sys.modules['render_scene']
    finally:
        sys.path[:] = paths
        for name, old in previous.items():
            if old is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = old


def phase(t, period):
    nearest = round(t*FPS)
    return (nearest % (period*FPS))/FPS if abs(t*FPS-nearest) < 1e-8 else t % period


def smooth(x):
    x = min(1., max(0., float(x)))
    return x*x*(3-2*x)


class Reference:
    def __init__(self):
        self.plan = json.loads((ORIGINAL/'long-version-plan.json').read_text(encoding='utf-8'))
        self.config = json.loads((ORIGINAL/'scene-plan.json').read_text(encoding='utf-8'))
        self.module = original_renderer()
        self.scene = self.module.Scene()
        self.original_lamp = self.scene.lamp_amount
        self.original_vehicle = self.scene.vehicle_state
        self.events = {'lamp': [], 'sun_glare': [], 'traffic': []}
        for cluster in self.plan['attention_events']['lamp_clusters']:
            for source, offset in zip(cluster['source_event_indices'], cluster['relative_offsets']):
                self.events['lamp'].append({'start': cluster['start']+offset, 'source': source})
        for key, label in [('greenhouse_glints', 'sun_glare'), ('traffic_passages', 'traffic')]:
            self.events[label] = [{'start': e['start'], 'source': e['source_variant_index']}
                                  for e in self.plan['attention_events'][key]]

    def length(self, name, entry):
        e = self.config[name]['events'][entry['source']]
        return e['seconds'] if name == 'traffic' else e['rise']+e['hold']+e['fall']

    def active(self, name, t):
        p = phase(t, PERIOD)
        return [(entry, p-entry['start']) for entry in self.events[name]
                if 0 <= p-entry['start'] < self.length(name, entry)]

    def lamp(self, t):
        # Probe the actual untouched V5 method rather than reinterpreting its
        # expression or relying on the production renderer's envelopes.
        return max([self.original_lamp(self.config['lamp']['events'][e['source']]['time']+age)
                    for e, age in self.active('lamp', t)] or [0.])

    def glare(self, t, shadow=True):
        values = []
        for entry, age in self.active('sun_glare', t):
            e = self.config['sun_glare']['events'][entry['source']]
            values.append(smooth(age/e['rise'])*smooth((self.length('sun_glare', entry)-age)/e['fall'])*e['strength'])
        amount = max(values or [0.])
        if amount and shadow:
            field = self.scene.shadow_pixels(phase(t, 60))
            x, y, _, _ = self.scene.rois['shadows']
            local = float(field[426-y, 1400-x])
            # Frozen V5's np.clip returns a NumPy float64 scalar. Preserve
            # that dtype: NumPy 2 promotes mask multiplication differently
            # for a Python float even when its numeric value is identical.
            amount *= .45+.55*(1-np.clip(local/.30, 0, 1))
        return amount

    def vehicle(self, t, source_index):
        matches = [(e, age) for e, age in self.active('traffic', t) if e['source'] == source_index]
        if not matches:
            return None
        assert len(matches) == 1
        event = self.scene.c['traffic']['events'][source_index]
        return self.original_vehicle(event['time']+matches[0][1], event)

    @contextmanager
    def at(self, t, weather=False):
        s = self.scene
        previous = s.lamp_amount, s.glare_amount, s.vehicle_state
        s.lamp_amount = lambda _: 0. if weather else self.lamp(t)
        s.glare_amount = lambda _: 0. if weather else self.glare(t)
        s.vehicle_state = lambda _, event: None if weather else self.vehicle(t, next(i for i, e in enumerate(s.c['traffic']['events']) if e is event))
        try:
            yield s
        finally:
            s.lamp_amount, s.glare_amount, s.vehicle_state = previous

    def frame(self, t, only=None, weather=False):
        with self.at(t, weather):
            return self.scene.frame(phase(t, 60), only)

    def indices(self):
        points = {0, 1, 17998, 17999}
        for minute in range(1, 10):
            points.update(minute*1800+j for j in (-2, -1, 0, 1))
        for name, entries in self.events.items():
            for entry in entries:
                e = self.config[name]['events'][entry['source']]
                start, length = entry['start'], self.length(name, entry)
                peak = length/2 if name == 'traffic' else e['rise']+e['hold']/2
                for t in (start, start+peak, start+length):
                    k = round(t*FPS)
                    points.update(j for j in (k-1, k, k+1) if 0 <= j < PERIOD*FPS)
        for minute in range(10):
            for old in (14.3, 14.6333333333333, 44.4, 20., 48., 10., 40.):
                t = minute*60+old
                if not any(self.active(name, t) for name in ATTENTION):
                    points.add(round(t*FPS))
        return sorted(points)


def runs(values):
    a = np.asarray(values, bool)
    starts = np.flatnonzero(a & ~np.r_[False, a[:-1]])
    ends = np.flatnonzero(a & ~np.r_[a[1:], False])+1
    return [[int(a), int(b)] for a, b in zip(starts, ends)]


def check_vehicle(a, b, label):
    if a is None or b is None:
        assert a is None and b is None, label
    else:
        assert np.allclose(a[0], b[0], atol=1e-10, rtol=0), label
        assert np.allclose(a[1], b[1], atol=1e-10, rtol=0), label
        assert a[2].keys() == b[2].keys(), label
        assert all(abs(a[2][key]-b[2][key]) < 1e-10 for key in a[2]), label


def event_audit(scene, ref):
    observed = {name: [] for name in ATTENTION}
    errors = {'lamp': 0., 'sun_glare': 0.}
    original = scene.shadow_pixels
    zero_shadow = np.zeros(scene.masks['shadows'].shape, np.float32)
    scene.shadow_pixels = lambda _: zero_shadow
    try:
        for index in range(PERIOD*FPS):
            t = index/FPS
            with scene._clock(t) as wt:
                for name, actual, expected in [('lamp', scene.lamp_amount(wt), ref.lamp(t)),
                                               ('sun_glare', scene.glare_amount(wt), ref.glare(t, False))]:
                    errors[name] = max(errors[name], abs(actual-expected))
                    assert abs(actual-expected) < 1e-9, (name, t, actual, expected)
                    observed[name].append(actual > 1e-12)
                traffic = False
                for j, event in enumerate(scene.c['traffic']['events']):
                    actual = scene.vehicle_state(wt, event)
                    check_vehicle(actual, ref.vehicle(t, j), ('vehicle', index, j))
                    traffic |= actual is not None
                observed['traffic'].append(traffic)
                assert scene.attention_active(t) == any(ref.active(name, t) for name in ATTENTION), ('gate', t)
    finally:
        scene.shadow_pixels = original
    intervals = {name: runs(values) for name, values in observed.items()}
    assert {name: len(v) for name, v in intervals.items()} == {'lamp': 3, 'sun_glare': 3, 'traffic': 4}
    shadow_times = []
    for entry in ref.events['sun_glare']:
        e = ref.config['sun_glare']['events'][entry['source']]
        for age in (1/FPS, e['rise'], e['rise']+e['hold']/2, ref.length('sun_glare', entry)-1/FPS):
            t = entry['start']+age
            with scene._clock(t) as wt:
                assert abs(scene.glare_amount(wt)-ref.glare(t)) < 1e-9, ('true shadow', t)
            shadow_times.append(t)
    return {'ticks_checked': 18000, 'maximum_envelope_error': errors,
            'active_frame_intervals_end_exclusive': intervals, 'lamp_clusters': 2,
            'all_vehicle_local_route_heading_perspective_exact': True,
            'old_minute_events_absent_outside_schedule': True, 'cache_gate_exact': True,
            'true_weather_shadow_times': shadow_times}


def native_audit(scene, ref):
    assert scene.duration == ref.scene.duration == 60
    assert scene.base.shape == (941, 1672, 3)
    assert np.array_equal(scene.base, ref.scene.base)
    for name in scene.masks:
        assert scene.rois[name] == ref.scene.rois[name], name
        assert np.array_equal(scene.masks[name], ref.scene.masks[name]), name
    assert np.array_equal(scene.active, ref.scene.active)
    sky = scene.masks['clouds'] > 0
    yy = scene.sky_y[sky].astype(int)
    adjacent = sky[:, :-1] & sky[:, 1:]
    minimum_jacobian = 1.
    for t in np.arange(0, 60, .125):
        for mx, weight in scene.cloud_maps(t):
            left, right = np.floor(mx[sky]).astype(int), np.ceil(mx[sky]).astype(int)
            assert left.min() >= 0 and right.max() < scene.sky_safe.shape[1]
            assert np.all(scene.sky_safe[yy, left]) and np.all(scene.sky_safe[yy, right]), ('sky taps', t)
            minimum_jacobian = min(minimum_jacobian, float(np.diff(mx, axis=1)[adjacent].min()))
    assert minimum_jacobian > .25
    hashes = {}
    for name, expected in ref.plan['baseline']['reference_inputs'].items():
        actual = digest(ROOT/name)
        assert actual == expected, ('V5 changed', name)
        hashes[name] = actual
    events = event_audit(scene, ref)
    print('All 18,000 scheduler ticks and original source inputs pass', flush=True)
    indices, details = ref.indices(), []
    for j, index in enumerate(indices):
        t = index/FPS
        expected, actual = ref.frame(t), scene.frame(t)
        assert np.array_equal(actual, expected), ('native reference', index, int(np.max(np.abs(actual.astype(int)-expected))))
        assert np.array_equal(actual[~scene.active], scene.base[~scene.active]), ('protected', index)
        weather = scene.weather_frame(t)
        before = hashlib.sha256(weather).hexdigest()
        composed = scene.apply_attention(weather, t)
        assert hashlib.sha256(weather).hexdigest() == before, ('cache mutated', index)
        assert np.array_equal(composed, expected), ('cache decomposition', index)
        assert np.array_equal(weather, ref.frame(t, weather=True)), ('retained weather', index)
        details.append({'frame': index, 'seconds': t, 'rgb_sha256': hashlib.sha256(actual).hexdigest()})
        if j % 25 == 0:
            print(f'Native controls {j+1}/{len(indices)}', flush=True)
    isolated_times = [0, 14.3, 48.5, 60, 87.3666666667, 238.1, 397.8, 599.9666666667]
    for t in isolated_times:
        for name in RETAINED:
            assert np.array_equal(scene.frame(t, name), ref.frame(t, name)), (name, t)
    periodic = [0, 1, 1500, 2621, 7160, 11935, 17999]
    for index in periodic:
        assert np.array_equal(scene.frame(index/FPS), scene.frame(index/FPS+PERIOD)), ('period', index)
    seams = {}
    for name in list(scene.masks)+['combined']:
        mask = scene.active if name == 'combined' else scene.masks[name] > 0
        values = []
        for t in (PERIOD-2/FPS, PERIOD-1/FPS, 0, 1/FPS):
            frame = scene.frame(t, None if name == 'combined' else name)
            if name != 'combined':
                frame = frame[ref.module.region(scene.rois[name])]
            values.append(frame[mask].astype(np.float32))
        left, seam, right = [float(np.abs(values[i+1]-values[i]).mean()) for i in range(3)]
        assert seam <= max(left, right)*1.5+.025, (name, seam, left, right)
        seams[name] = {'native_rgb_seam_mae': seam, 'neighbor_mae': [left, right]}
    report = {'status': 'passed', 'seconds': 600, 'fps': 30, 'native_dimensions': [1672, 941],
              'original_input_hashes': hashes, 'renderer_sha256': digest(JOB/'visual/long_scene.py'),
              'audit_script_sha256': digest(__file__), 'events': events, 'native_controls': details,
              'sky_source_safety': {'map_states': 480, 'all_bilinear_taps_inside_safe_sky': True,
                                    'minimum_horizontal_jacobian': minimum_jacobian},
              'all_controls_match_independently_remapped_original_v5': True,
              'protected_native_pixels_exact': True, 'cache_inputs_immutable': True,
              'all_cache_composites_exact': True, 'all_retained_weather_frames_exact': True,
              'retained_isolated_layer_times': isolated_times, 'exact_600s_period_indices': periodic,
              'regional_600s_seam': seams,
              'limits': 'Numerical native/scheduler audit; no continuous playback or artistic approval inferred.'}
    save('native-validation.json', report)
    return report


def yuv_reference(ref, index):
    rgb = ref.frame(index/FPS)
    return subprocess.check_output([FFMPEG, '-v', 'error', '-f', 'rawvideo', '-pixel_format', 'rgb24',
        '-video_size', '1672x941', '-framerate', '30', '-i', 'pipe:0', '-frames:v', '1',
        '-vf', 'scale=3840:2160:flags=lanczos:in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p',
        '-f', 'rawvideo', '-pix_fmt', 'yuv420p', 'pipe:1'], input=rgb.tobytes())


def decoded_audit(scene, ref, master):
    native = json.loads((HERE/'native-validation.json').read_text(encoding='utf-8'))
    assert native['status'] == 'passed'
    assert native['renderer_sha256'] == digest(JOB/'visual/long_scene.py')
    indices = [entry['frame'] for entry in native['native_controls']]
    controls = {}
    for j, index in enumerate(indices):
        controls[index] = hashlib.sha256(yuv_reference(ref, index)).hexdigest()
        if j % 25 == 0:
            print(f'Independent 4K colour references {j+1}/{len(indices)}', flush=True)
    select = '+'.join(f'eq(n\\,{i})' for i in indices)
    size = 3840*2160*3//2
    cmd = [FFMPEG, '-v', 'error', '-i', str(master), '-vf', 'select='+select,
           '-fps_mode', 'passthrough', '-an', '-pix_fmt', 'yuv420p', '-f', 'rawvideo', 'pipe:1']
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    passed = []
    try:
        for index in indices:
            data = process.stdout.read(size)
            assert len(data) == size, ('short decoded frame', index, len(data))
            actual = hashlib.sha256(data).hexdigest()
            assert actual == controls[index], ('encoded/native YUV mismatch', index, actual, controls[index])
            passed.append(index)
        assert not process.stdout.read(1), 'Unexpected additional selected frames'
        errors = process.stderr.read().decode('utf-8', errors='replace')
        assert process.wait() == 0, errors
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
    still_indices = [0, 1560, 1800, 2621, 5950, 7220, 10670, 11935, 14320, 15500, 17999]
    tiles = []
    for index in still_indices:
        # Seek to an exact integral-second GOP position, then count frames;
        # avoids rounding a fractional timestamp to the following picture.
        seek_frame = (index//60)*60
        raw = subprocess.check_output([FFMPEG, '-v', 'error', '-ss', str(seek_frame/FPS), '-i', str(master),
            '-vf', f'select=eq(n\\,{index-seek_frame}),scale=in_color_matrix=bt709:in_range=tv:out_range=pc', '-frames:v', '1',
            '-pix_fmt', 'rgb24', '-f', 'rawvideo', 'pipe:1'])
        assert len(raw) == 3840*2160*3
        im = Image.fromarray(np.frombuffer(raw, np.uint8).reshape(2160, 3840, 3))
        im.thumbnail((960, 540))
        tile = Image.new('RGB', (960, 565), '#181818')
        tile.paste(im, (0, 25))
        ImageDraw.Draw(tile).text((10, 5), f'Actual 4K decoded frame {index} / {index/FPS:.3f}s', fill='white')
        tiles.append(tile)
    sheet = Image.new('RGB', (1920, ((len(tiles)+1)//2)*565), '#181818')
    for j, tile in enumerate(tiles):
        sheet.paste(tile, ((j%2)*960, (j//2)*565))
    sheet.save(HERE/'decoded-controls-contact-sheet.jpg', quality=92)
    report = {'status': 'passed', 'master': str(master), 'master_sha256': digest(master),
              'dimensions': [3840, 2160], 'conversion': 'FFmpeg Lanczos native RGB to 4K BT.709/TV yuv420p',
              'ffmpeg_version': subprocess.check_output([FFMPEG, '-version'], text=True).splitlines()[0],
              'renderer_sha256': digest(JOB/'visual/long_scene.py'), 'audit_script_sha256': digest(__file__),
              'native_validation_sha256': digest(HERE/'native-validation.json'),
              'all_selected_actual_decoded_frames_pixel_exact_yuv': True, 'control_indices': passed,
              'controls_yuv_sha256': controls, 'contact_sheet': 'decoded-controls-contact-sheet.jpg',
              'limits': 'Actual decoded stills prepared for inspection; this record alone does not assert inspection or continuous playback. Full frame/timestamp checks belong to assembly validator.'}
    save('decoded-colour-validation.json', report)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['native', 'decoded'])
    parser.add_argument('--master', type=Path, default=MASTER)
    args = parser.parse_args()
    ref = Reference()
    long = load(JOB/'visual/long_scene.py', 'crater_long_audit_target')
    scene = long.Scene()
    report = native_audit(scene, ref) if args.stage == 'native' else decoded_audit(scene, ref, args.master)
    print(json.dumps({'status': report['status'], 'stage': args.stage}), flush=True)


if __name__ == '__main__':
    main()
