"""Source-bound Crater Rim minute: forward weather, terrain shade and survey telemetry."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

import cv2
import imageio_ffmpeg
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE / 'dependencies'))
from periodic_transport import PeriodicDust

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
PLAN_PATH = HERE / 'scene-plan.json'
cv2.setNumThreads(1)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def smooth(v):
    v = np.clip(v, 0, 1)
    return v*v*(3-2*v)


def region(roi):
    a, b, c, d = roi
    return np.s_[b:d, a:c]


def mask(polygons, roi, feather=4, inset=1):
    a, b, c, d = roi
    value = np.zeros((d-b, c-a), np.uint8)
    for polygon in polygons:
        cv2.fillPoly(value, [np.int32(polygon)-(a, b)], 1)
    distance = cv2.distanceTransform(np.pad(value, 1), cv2.DIST_L2, 5)[1:-1, 1:-1]
    return smooth((distance-inset)/feather).astype(np.float32)


def clearance(m):
    x = np.arange(m.shape[1])[None, :]
    left = np.maximum.accumulate(np.where(m, -1, x), axis=1)
    right = np.minimum.accumulate(np.where(m, m.shape[1], x)[:, ::-1], axis=1)[:, ::-1]
    return np.minimum(x-left, right-x).astype(np.float32)


class Scene:
    def __init__(self):
        self.c = json.loads(PLAN_PATH.read_text())
        self.duration = self.c['duration']
        path = ROOT / self.c['source']
        assert sha(path) == self.c['source_sha256']
        self.base = np.asarray(Image.open(path).convert('RGB'))
        self.h, self.w = self.base.shape[:2]
        assert [self.w, self.h] == self.c['source_dimensions']
        self.rois = {'clouds': self.c['sky_roi'], 'haze': self.c['haze_roi'],
                     'shadows': self.c['shadows']['roi'], 'survey': self.c['survey_display']['roi'],
                     'windows': [1290, 392, 1570, 478]}
        self.masks = {}
        roi = self.rois['clouds']
        self.sky_safe = mask(self.c['cloud_safe_polygons'], roi, .1, 0) > .99
        self.masks['clouds'] = mask(self.c['cloud_safe_polygons'], roi, 9, 3)
        self.sky_y, self.sky_x = np.indices(self.sky_safe.shape, dtype=np.float32)
        self.sky_source = self.base[region(roi)].astype(np.float32)
        self.sky_taper = smooth(clearance(self.sky_safe)/self.c['clouds']['edge_taper'])
        self.sky_phase = self.c['clouds']['depth_phase']*smooth(self.sky_y/150)
        roi = self.rois['haze']
        self.masks['haze'] = mask([self.c['basin_polygon']], roi, 14, 2)*mask(self.c['window_apertures'], roi, 6, 3)
        step = self.c['haze_sample_step']
        a, b, z, d = roi
        y, x = np.mgrid[b:d:step, a:z:step].astype(np.float32)
        self.haze = [PeriodicDust(x, y, c, self.duration) for c in self.c['haze_layers']]
        roi = self.rois['shadows']
        self.masks['shadows'] = mask(self.c['terrain_polygons'], roi, 6, 2)*mask(self.c['window_apertures'], roi, 6, 3)
        a, b, z, d = roi
        step = self.c['shadows']['sample_step']
        self.shadow_y, self.shadow_x = np.mgrid[b:d:step, a:z:step].astype(np.float32)
        self.prepare_display()
        self.masks['windows'] = mask([v['polygon'] for v in self.c['colony_windows']], self.rois['windows'], .8, 0)
        self.window_masks = [mask([v['polygon']], self.rois['windows'], .8, 0) for v in self.c['colony_windows']]
        self.active = np.zeros((self.h, self.w), bool)
        for name, m in self.masks.items():
            self.active[region(self.rois[name])] |= m > 0

    def prepare_display(self):
        c = self.c['survey_display']
        self.display_maps = {}
        a, b, z, d = c['roi']
        allowed = np.zeros((d-b, z-a), np.float32)
        for name in ['radar', 'telemetry', 'map']:
            quad = c[name+'_quad']
            h = cv2.getPerspectiveTransform(np.float32([[0, 0], [159, 0], [159, 159], [0, 159]]), np.float32(quad)-np.float32([a, b]))
            m = mask([quad], c['roi'], 1.5, .5)
            self.display_maps[name] = h, m
            allowed = np.maximum(allowed, m)
        self.masks['survey'] = allowed
        self.ui_y, self.ui_x = np.mgrid[:160, :160].astype(np.float32)
        dx, dy = self.ui_x-80, self.ui_y-80
        self.ui_radius = np.hypot(dx, dy)
        self.ui_angle = np.arctan2(dy, dx)

    def cloud_maps(self, t):
        c = self.c['clouds']
        for phase in c['phase_offsets']:
            age = (float(t)+phase+self.sky_phase) % self.duration
            weight = np.sin(np.pi*age/self.duration)**c['weight_power']
            mx = self.sky_x-self.sky_taper*c['speed']*(age-self.duration/2)
            yield mx.astype(np.float32), weight

    def cloud_pixels(self, t):
        total = np.zeros_like(self.sky_x)
        moving = np.zeros_like(self.sky_source)
        for mx, weight in self.cloud_maps(t):
            sample = cv2.remap(self.sky_source, mx, self.sky_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
            moving += sample*weight[..., None]
            total += weight
        moving /= total[..., None]
        return moving

    def haze_pixels(self, t):
        size = self.masks['haze'].shape[::-1]
        result = []
        for plume in self.haze:
            alpha, color = plume.density(t)
            result.append((cv2.resize(alpha, size, interpolation=cv2.INTER_LINEAR)*self.masks['haze'],
                           cv2.resize(color, size, interpolation=cv2.INTER_LINEAR)))
        return result

    def shadow_pixels(self, t):
        opacity = np.zeros_like(self.shadow_x)
        for plume in self.c['shadows']['plumes']:
            age = (float(t)+plume['phase']) % self.duration
            fade = smooth(age/16)*smooth((self.duration-age)/16)
            dx = (self.shadow_x-plume['x_at_midlife']-plume['speed']*(age-30))/plume['width']
            dy = (self.shadow_y-plume['y']-.04*plume['speed']*(age-30))/plume['height']
            # Broad scalloped edges, without a regular band or whole-frame exposure swing.
            shape = np.exp(-.5*(dx*dx+dy*dy))
            shape *= .82+.12*np.sin(dx*3.1+dy*2.7)+.06*np.sin(dx*7.1-dy*4.2)
            opacity += shape*fade*self.c['shadows']['strength']
        return cv2.resize(opacity, self.masks['shadows'].shape[::-1], interpolation=cv2.INTER_LINEAR)*self.masks['shadows']

    def survey_pixels(self, t):
        c = self.c['survey_display']
        fields = {}
        angle = 2*np.pi*(t/c['radar_period'])-np.pi/2
        behind = (angle-self.ui_angle) % (2*np.pi)
        tail = np.exp(-behind/.32)*(self.ui_radius < 67)*smooth((self.ui_radius-4)/7)
        line = np.exp(-(behind/.022)**2)*(self.ui_radius < 67)
        radar = (tail*.42+line*.65)[..., None]*np.float32(c['radar_peak'])
        for x, y in [(44, 61), (99, 39), (112, 111), (58, 119)]:
            point_angle = np.arctan2(y-80, x-80)
            age = ((angle-point_angle) % (2*np.pi))/(2*np.pi)*c['radar_period']
            light = np.exp(-age/1.8)
            spot = np.exp(-((self.ui_x-x)**2+(self.ui_y-y)**2)/4)
            radar += spot[..., None]*light*np.float32([108, 119, 99])
        fields['radar'] = radar
        # Existing graph remains visible: only a faint moving read head and four local peaks.
        x = (t % 12)/12*140+10
        trace = np.exp(-((self.ui_x-x)/2.0)**2)*smooth((self.ui_y-15)/15)*smooth((145-self.ui_y)/20)
        fields['telemetry'] = trace[..., None]*np.float32([25, 33, 26])
        chart = np.zeros((160, 160), np.float32)
        for i, cx in enumerate([32, 67, 103, 132]):
            y = 122-27*(.5+.5*np.sin(2*np.pi*t/(12 if i % 2 else 20)+i))
            chart += np.exp(-((self.ui_x-cx)/1.1)**2-((self.ui_y-y)/3)**2)
        fields['telemetry'] += chart[..., None]*np.float32([64, 72, 61])
        # A quiet survey target crossing the existing relief map, without replacing it.
        phi = 2*np.pi*t/c['map_period']
        tx, ty = 84+24*np.cos(phi), 83+14*np.sin(phi)
        ring = np.exp(-((np.hypot(self.ui_x-tx, self.ui_y-ty)-3)/.8)**2)
        fields['map'] = ring[..., None]*np.float32([38, 46, 37])
        a, b, z, d = c['roi']
        combined = np.zeros((d-b, z-a, 3), np.float32)
        for name, field in fields.items():
            h, m = self.display_maps[name]
            combined += cv2.warpPerspective(field, h, (z-a, d-b), flags=cv2.INTER_LINEAR)*m[..., None]
        return combined

    def window_pixels(self, t):
        result = np.zeros((*self.masks['windows'].shape, 3), np.float32)
        for entry, m in zip(self.c['colony_windows'], self.window_masks):
            local = (t+entry['phase']) % self.duration
            amount = 0
            for event in self.c['light_events']:
                age = (local-event['time']) % self.duration
                length = event['rise']+event['hold']+event['fall']
                amount += float(smooth(age/event['rise'])*smooth((length-age)/event['fall']))
            result += m[..., None]*min(amount, 1)*np.float32([35, 24, 10])
        return result

    def frame(self, t, only=None):
        t = float(t) % self.duration
        frame = self.base.copy()
        if only in [None, 'clouds']:
            pixels = self.sky_source+(self.cloud_pixels(t)-self.sky_source)*self.masks['clouds'][..., None]
            frame[region(self.rois['clouds'])] = np.clip(np.rint(pixels), 0, 255).astype(np.uint8)
        if only in [None, 'shadows']:
            r = region(self.rois['shadows'])
            frame[r] = np.rint(frame[r].astype(np.float32)*(1-self.shadow_pixels(t)[..., None])).astype(np.uint8)
        if only in [None, 'haze']:
            r = region(self.rois['haze'])
            pixels = frame[r].astype(np.float32)
            for alpha, color in self.haze_pixels(t):
                pixels += (color-pixels)*alpha[..., None]
            frame[r] = np.clip(np.rint(pixels), 0, 255).astype(np.uint8)
        if only in [None, 'survey', 'windows']:
            names = ['survey', 'windows'] if only is None else [only]
            for name in names:
                r = region(self.rois[name])
                addition = self.survey_pixels(t) if name == 'survey' else self.window_pixels(t)
                frame[r] = np.clip(np.rint(frame[r].astype(np.float32)+addition), 0, 255).astype(np.uint8)
        return frame

    def fingerprint(self):
        return {str(p.relative_to(ROOT)).replace('\\', '/'): sha(p) for p in
                [ROOT / self.c['source'], PLAN_PATH, Path(__file__), *sorted((HERE/'dependencies').glob('*.py'))]}


def encode(scene, path, seconds, only=None, start=0):
    path = Path(path)
    if path.exists():
        raise FileExistsError(path)
    partial = path.with_suffix('.partial.mp4')
    w, h = scene.c['preview_dimensions']
    fps = scene.c['fps']
    command = [FFMPEG, '-v', 'error', '-n', '-f', 'rawvideo', '-pixel_format', 'rgb24', '-s', f'{w}x{h}',
               '-r', str(fps), '-i', 'pipe:0', '-an', '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p',
               '-c:v', 'libx264', '-qp', '0', '-preset', 'veryfast', '-threads', '4', '-g', str(fps*5),
               '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
               '-movflags', '+faststart', str(partial)]
    protected = ~scene.active
    baseline = scene.base[protected]
    begun = time.monotonic()
    with subprocess.Popen(command, stdin=subprocess.PIPE) as process:
        try:
            for i in range(round(seconds*fps)):
                frame = scene.frame(start+i/fps, only)
                assert np.array_equal(frame[protected], baseline), (only, i)
                out = cv2.resize(frame, (w, h), interpolation=cv2.INTER_AREA)
                process.stdin.write(out.tobytes())
                if i % (fps*5) == 0:
                    print(f'{path.name}: {i/fps:.0f}/{seconds}s ({time.monotonic()-begun:.1f}s elapsed)', flush=True)
        finally:
            process.stdin.close()
        assert process.wait() == 0
    partial.rename(path)


def samples(scene):
    folder = HERE/'inspection'
    folder.mkdir(exist_ok=True)
    overlay = scene.base.copy().astype(np.float32)
    colors = {'clouds': [60, 180, 255], 'shadows': [190, 90, 255], 'haze': [255, 180, 50],
              'survey': [80, 255, 120], 'windows': [255, 100, 60]}
    for name, m in scene.masks.items():
        r = region(scene.rois[name])
        overlay[r] += (np.float32(colors[name])-overlay[r])*m[..., None]*.45
    Image.fromarray(np.uint8(np.clip(overlay, 0, 255))).save(folder/'mask-overlay.png')
    for t in [0, 8, 16, 28, 40, 52, 59+29/30]:
        frame = scene.frame(t)
        Image.fromarray(cv2.resize(frame, (1280, 720), interpolation=cv2.INTER_AREA)).save(folder/f'combined-{t:06.2f}s.png')
    print('Saved masks and temporal samples', flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['samples', 'test', 'full', 'isolated'])
    args = parser.parse_args()
    scene = Scene()
    if args.stage == 'samples':
        samples(scene)
    elif args.stage == 'test':
        encode(scene, HERE/'Crater-Rim-Survey-v2-motion-check-8s.mp4', 8, start=5)
    elif args.stage == 'full':
        encode(scene, HERE/'Crater-Rim-Survey-v2-60s-loop.mp4', scene.duration)
    else:
        for name in ['clouds', 'haze', 'shadows', 'survey']:
            encode(scene, HERE/f'Crater-Rim-Survey-v2-{name}-8s.mp4', 8, only=name, start=5)


if __name__ == '__main__':
    main()
