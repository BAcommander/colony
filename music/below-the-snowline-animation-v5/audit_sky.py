"""Independent source-footprint and continuity audit for the V5 sky replacement.

Tests the actual backward maps and rendered pixels rather than matching a second
copy of the renderer's formula. It does not establish artistic approval.
"""
from pathlib import Path
import json
import hashlib
import time
import cv2
import numpy as np
from PIL import Image, ImageDraw
import render_v5 as renderer

H = Path(__file__).resolve().parent


def fingerprint(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    started = time.time()
    scene = renderer.Scene()
    a, b, z, d = scene.skyroi
    alpha = scene.sky[b:d, a:z]
    contributing = alpha > 1e-5
    safe = getattr(scene, 'cloud_safe', None)
    if safe is None:
        safe = scene.poly(scene.g['cloud_safe_polygon'], 0)
    safe = np.asarray(safe > 0, np.uint8)
    distance = cv2.distanceTransform(safe, cv2.DIST_L2, 5)
    eroded = distance > 2.0
    height, width = safe.shape
    times = set(np.arange(0, 120.001, .5).tolist())
    for boundary in [20, 40, 60, 80, 100]:
        times.update([boundary - 1/30, boundary, boundary + 1/30])
    times.update([7, 19, 31, 45, 48, 59, 73, 91, 95, 109, 119.9])
    minimum_jacobian = float('inf')
    minimum_source_clearance = float('inf')
    maximum_frame_map_motion = 0.0
    violations = []
    samples = []

    for t in sorted(times):
        mx, my = scene.cloud_maps(t)
        assert mx.shape == alpha.shape and my.shape == alpha.shape
        assert np.isfinite(mx).all() and np.isfinite(my).all()
        mx_dy, mx_dx = np.gradient(mx.astype(np.float64))
        my_dy, my_dx = np.gradient(my.astype(np.float64))
        jacobian = mx_dx * my_dy - mx_dy * my_dx
        local_min = float(jacobian.min())
        minimum_jacobian = min(minimum_jacobian, local_min)
        if local_min <= .3:
            violations.append({'time': t, 'kind': 'map_fold_or_compression', 'minimum_jacobian': local_min})

        x0 = np.floor(mx).astype(np.int32)
        y0 = np.floor(my).astype(np.int32)
        fx, fy = mx-x0, my-y0
        corner_weights = [(0, 0, (1-fx)*(1-fy)), (1, 0, fx*(1-fy)),
                          (0, 1, (1-fx)*fy), (1, 1, fx*fy)]
        bad_count = 0
        local_clearance = float('inf')
        for ox, oy, weight in corner_weights:
            used = contributing & (weight > 1e-6)
            xs, ys = (x0+ox)[used], (y0+oy)[used]
            inside = (xs >= 0) & (xs < width) & (ys >= 0) & (ys < height)
            bad_count += int(np.count_nonzero(~inside))
            xs, ys = xs[inside], ys[inside]
            if len(xs):
                bad_count += int(np.count_nonzero(~eroded[ys, xs]))
                local_clearance = min(local_clearance, float(distance[ys, xs].min()))
        minimum_source_clearance = min(minimum_source_clearance, local_clearance)
        if bad_count:
            violations.append({'time': t, 'kind': 'unsafe_bilinear_source_corner',
                               'corner_count': bad_count, 'minimum_distance': local_clearance})

        nx, ny = scene.cloud_maps(t + 1/30)
        frame_motion = float(np.hypot(nx-mx, ny-my).max())
        maximum_frame_map_motion = max(maximum_frame_map_motion, frame_motion)
        if frame_motion > .15:
            violations.append({'time': t, 'kind': 'abrupt_frame_map_motion', 'pixels': frame_motion})
        samples.append({'time_seconds': t, 'minimum_jacobian': local_min,
                        'minimum_source_clearance_pixels': local_clearance,
                        'maximum_next_frame_map_displacement': frame_motion})

    review_times = [0, 20, 35, 48, 70, 95, 119.9]
    cache = H/'cache/sky-audit'
    cache.mkdir(parents=True, exist_ok=True)
    frozen = scene.sky == 0
    region = (535, 20, 1190, 190)
    crop_width, crop_height = region[2]-region[0], region[3]-region[1]
    sheet = Image.new('RGB', (crop_width*2, (crop_height+22)*4), (20, 22, 25))
    rendered_changes = []
    for n, t in enumerate(review_times):
        frame = scene.base.astype(np.float32)
        returned = scene.sky_layer(frame, t)
        if returned is not None:
            frame = returned
        assert np.array_equal(frame[frozen], scene.base[frozen]), ('protected pixels', t)
        change = float(np.abs(frame[scene.sky>.5]-scene.base[scene.sky>.5]).mean())
        rendered_changes.append({'time_seconds': t, 'sky_mean_change': change})
        im = Image.fromarray(np.uint8(np.rint(np.clip(frame, 0, 255))))
        crop = im.crop(region)
        crop.save(cache/f'cloud-bank-{t:06.2f}.png')
        x, y = n % 2 * crop_width, n // 2 * (crop_height+22)
        sheet.paste(crop, (x, y+22))
        ImageDraw.Draw(sheet).text((x+8, y+5), f'Isolated sky, t={t:g}s', fill='white')
        if t == 48:
            delta = np.clip(128+(frame-scene.base.astype(np.float32))*6, 0, 255).astype(np.uint8)
            Image.fromarray(delta).save(cache/'sky-difference-48s-amplified.png')
    sheet.save(cache/'temporal-cloud-bank.png')
    assert max(x['sky_mean_change'] for x in rendered_changes) > .1, 'Sky is static'

    report = {'scope': 'Independent V5 sky-warp audit; renderer material and hardware changes are outside this audit',
              'status': 'passed' if not violations else 'failed',
              'map_sample_count': len(times),
              'coverage': 'Half-second map samples over 0–120s plus both sides of all five encoded-section boundaries',
              'minimum_backward_map_jacobian': minimum_jacobian,
              'required_jacobian_minimum': .3,
              'source_footprint': 'Every contributing bilinear neighbour must remain in the conservative polygon eroded by >2 output pixels; zero-weight neighbours excluded',
              'minimum_source_corner_clearance_pixels': minimum_source_clearance,
              'maximum_sampled_one_frame_map_motion_pixels': maximum_frame_map_motion,
              'isolated_cloud_pixels_outside_fixed_mask_exact': True,
              'isolated_visual_review_files': 'cache/sky-audit/',
              'rendered_changes': rendered_changes,
              'violations': violations,
              'samples': samples,
              'seconds_to_audit': round(time.time()-started, 2),
              'fingerprints': {name: fingerprint(H/name) for name in ['render_v5.py', 'geometry-v5.json', 'source.png']},
              'limits': 'Sampled geometric/sampling continuity and isolated stills; not user artistic approval or continuous playback.'}
    (H/'repair-validation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({key: report[key] for key in ['status', 'map_sample_count', 'minimum_backward_map_jacobian',
                  'minimum_source_corner_clearance_pixels', 'maximum_sampled_one_frame_map_motion_pixels', 'seconds_to_audit']}), flush=True)
    assert not violations, violations[:5]


if __name__ == '__main__':
    main()
