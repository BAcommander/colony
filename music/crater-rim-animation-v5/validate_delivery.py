"""Independent source-safety, loop-step, decoded-picture and repeat validation."""
import json
from pathlib import Path
import subprocess

import cv2
import numpy as np
from PIL import Image

from render_scene import HERE, ROOT, FFMPEG, PLAN_PATH, Scene, region, sha


def save(name, value):
    (HERE/name).write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')


def analytic(scene):
    active = scene.masks['clouds'] > 0
    yy = scene.sky_y[active].astype(int)
    valid = scene.sky_safe
    minimum = 1
    # Both extremal transport and all local reset neighborhoods, not only endpoint identity.
    for t in np.arange(0, 60, .125):
        for mx, weight in scene.cloud_maps(t):
            left = np.floor(mx[active]).astype(int)
            right = np.ceil(mx[active]).astype(int)
            assert left.min() >= 0 and right.max() < valid.shape[1]
            assert np.all(valid[yy, left]) and np.all(valid[yy, right]), t
            jacobian = np.diff(mx, axis=1)
            local = active[:, :-1] & active[:, 1:]
            minimum = min(minimum, float(jacobian[local].min()))
    assert minimum > .25, minimum
    layers = {}
    for name in scene.masks:
        r = region(scene.rois[name])
        m = scene.masks[name] > 0
        def state(t):
            return scene.frame(t, name)[r][m].astype(np.float32)
        a, b, c, d = [state(t) for t in [-2/30, -1/30, 0, 1/30]]
        seam = float(np.abs(c-b).mean())
        neighbors = [float(np.abs(b-a).mean()), float(np.abs(d-c).mean())]
        # Quantization can move a one-code-value crossing by a frame.
        assert seam <= max(neighbors)*1.5+.025, (name, seam, neighbors)
        exact_period = True
        for t in [0, .1, 7.375, 19.1, 38.8, 59.9]:
            assert np.array_equal(state(t), state(t+60)), (name, t)
        coverage = {}
        for start in [0, 20, 40]:
            x, y = state(start), state(start+8)
            coverage[str(start)] = {'mean_rgb_change_8s': float(np.abs(y-x).mean()),
                                    'pixels_changed_above_2': int(np.any(np.abs(y-x) > 2, axis=1).sum())}
        layers[name] = {'periodic': exact_period, 'native_seam_mae': seam,
                        'neighbor_step_mae': neighbors, 'motion_coverage': coverage}
    for t in [0, .5, 8, 16, 20, 28, 40, 52, 59+29/30]:
        frame = scene.frame(t)
        assert np.array_equal(frame[~scene.active], scene.base[~scene.active]), t
    assert not np.array_equal(scene.frame(0), scene.frame(20))
    assert not np.array_equal(scene.frame(20), scene.frame(40))
    return {'cloud_map_states': 480, 'minimum_active_horizontal_jacobian': minimum,
            'all_bilinear_source_taps_inside_safe_sky': True,
            'protected_native_pixels_exact': True, 'layers': layers,
            'distinct_0_20_40_second_states': True}


def framehash(path, count):
    result = subprocess.check_output([FFMPEG, '-v', 'error', '-i', str(path), '-map', '0', '-f', 'framehash', '-'], text=True)
    assert '#dimensions 0: 1280x720' in result
    assert '#tb 0: 1/30' in result
    assert '#media_type 0: video' in result and 'audio' not in result
    rows = [s.split(',') for s in result.splitlines() if s and not s.startswith('#')]
    assert len(rows) == count, (path, len(rows), count)
    assert [int(s[2]) for s in rows] == list(range(count))
    return [s[-1].strip() for s in rows]


def yuv_controls(scene, indices):
    rgb = b''.join(cv2.resize(scene.frame(i/30), (1280, 720), interpolation=cv2.INTER_AREA).tobytes() for i in indices)
    command = [FFMPEG, '-v', 'error', '-f', 'rawvideo', '-pixel_format', 'rgb24', '-s', '1280x720', '-r', '30',
               '-i', 'pipe:0', '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p',
               '-f', 'rawvideo', '-pix_fmt', 'yuv420p', 'pipe:1']
    raw = subprocess.check_output(command, input=rgb)
    size = 1280*720*3//2
    assert len(raw) == size*len(indices)
    return {index: raw[j*size:(j+1)*size] for j, index in enumerate(indices)}


def encoded_audit(scene, path):
    width, height = 1280, 720
    size = width*height*3//2
    masks = {}
    for name, m in scene.masks.items():
        full = np.zeros((scene.h, scene.w), np.uint8)
        full[region(scene.rois[name])] = m > 0
        masks[name] = cv2.resize(full, (width, height), interpolation=cv2.INTER_NEAREST) > 0
    masks['combined'] = np.logical_or.reduce(list(masks.values()))
    histories = {name: [] for name in masks}
    controls = yuv_controls(scene, [0, 1, 239, 240, 429, 438, 570, 642, 840, 1200, 1332, 1443, 1560, 1798, 1799])
    command = [FFMPEG, '-v', 'error', '-i', str(path), '-f', 'rawvideo', '-pix_fmt', 'yuv420p', 'pipe:1']
    first = previous = None
    count = 0
    with subprocess.Popen(command, stdout=subprocess.PIPE) as decoder:
        while True:
            raw = decoder.stdout.read(size)
            if not raw:
                break
            assert len(raw) == size
            if count in controls:
                assert raw == controls[count], ('encoded/direct mismatch', count)
            picture = np.frombuffer(raw[:width*height], np.uint8).reshape(height, width).astype(np.float32)
            if first is None:
                first = picture.copy()
            if previous is not None:
                delta = np.abs(picture-previous)
                for name, m in masks.items():
                    histories[name].append(float(delta[m].mean()))
            previous = picture
            count += 1
        assert decoder.wait() == 0
    assert count == 1800
    result = {}
    for name, m in masks.items():
        seam = float(np.abs(first-previous)[m].mean())
        values = np.asarray(histories[name])
        near = max(values[0], values[-1])
        assert seam <= near*1.5+.025, (name, seam, near)
        assert seam <= float(values.max())*1.5+.025
        result[name] = {'seam_luma_mae': seam, 'nearby_step_max': float(near),
                        'normal_step_p99': float(np.quantile(values, .99)), 'normal_step_max': float(values.max())}
    return {'decoded_frames': count, 'direct_native_to_encoded_yuv_controls': sorted(controls),
            'all_direct_controls_pixel_exact': True, 'regional_seams': result}


def repeat(path):
    target = HERE/'Crater-Rim-Survey-v5-3-loops-180s.mp4'
    if not target.exists():
        subprocess.run([FFMPEG, '-v', 'error', '-n', '-stream_loop', '2', '-i', str(path), '-map', '0:v', '-an',
                        '-c', 'copy', '-movflags', '+faststart', str(target)], check=True)
    return target


def main():
    scene = Scene()
    print('Checking source sampling, native protection and per-layer loop steps', flush=True)
    native = analytic(scene)
    save('analytic-validation.json', native)
    path = HERE/'Crater-Rim-Survey-v5-60s-loop.mp4'
    print('Checking all decoded minute pictures and timestamps', flush=True)
    hashes = framehash(path, 1800)
    decoded = encoded_audit(scene, path)
    print('Building/checking three exact encoded repetitions', flush=True)
    repeated = repeat(path)
    repeats = framehash(repeated, 5400)
    assert repeats == hashes*3
    # Colour-aware inspection material, decoded from the actual delivered file.
    inspect = HERE/'inspection'
    for t in [0, 7.97, 14.3, 19.8, 21.8, 28, 44.4, 48.5, 52, 59+29/30]:
        i = round(t*30)
        data = subprocess.check_output([FFMPEG, '-v', 'error', '-i', str(path), '-vf', f'select=eq(n\\,{i}),scale=in_color_matrix=bt709:in_range=tv:out_range=pc',
                                        '-frames:v', '1', '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'])
        assert len(data) == 1280*720*3
        Image.fromarray(np.frombuffer(data, np.uint8).reshape(720, 1280, 3)).save(inspect/f'decoded-{t:06.2f}s.png')
    report = {'version': 5, 'date': '2026-11-05', 'source_dimensions': [scene.w, scene.h],
              'dimensions': [1280, 720], 'duration_seconds': 60, 'fps': 30, 'audio': False,
              'encoding': 'H.264 QP0, YUV420p BT.709 TV; source frames downsampled to 720p',
              'frozen_inputs': scene.fingerprint(), 'analytic': native, 'decoded': decoded,
              'three_repeat_review': {'duration_seconds': 180, 'decoded_frames': 5400,
                                      'sequential_timestamps': True, 'all_decoded_repetitions_exact': True},
              'outputs': [{'path': p.name, 'bytes': p.stat().st_size, 'sha256': sha(p)} for p in [path, repeated]],
              'review_limits': 'Native/mask/colour-correct decoded temporal stills inspected; no assistant continuous playback verdict. User artistic review pending.',
              'status': 'complete minute review candidate, not an approved 4K or full-length production master'}
    save('delivery.json', report)
    print(json.dumps({'outputs': report['outputs'], 'all_checks_passed': True}), flush=True)


if __name__ == '__main__':
    main()
