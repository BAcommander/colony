"""Crater Rim V3: retain V2 weather; add inhabited terrace details and a coupled practical."""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

import v2_renderer_snapshot as base

HERE, ROOT, PLAN_PATH = base.HERE, base.ROOT, base.PLAN_PATH
FFMPEG, sha, region, smooth = base.FFMPEG, base.sha, base.region, base.smooth
encode = base.encode


def poly(polygons, roi, feather=1.5, inset=0):
    # Inward supersampling keeps tiny emitters and people from turning into integer boxes.
    a, b, z, d = roi
    scale = 4
    m = np.zeros(((d-b)*scale, (z-a)*scale), np.uint8)
    for polygon in polygons:
        points = np.rint((np.float32(polygon)-np.float32([a, b]))*scale).astype(np.int32)
        cv2.fillPoly(m, [points], 1)
    dist = cv2.distanceTransform(np.pad(m, 1), cv2.DIST_L2, 5)[1:-1, 1:-1]/scale
    soft = smooth((dist-inset)/feather)
    return cv2.resize(soft, (z-a, d-b), interpolation=cv2.INTER_AREA)


def linear(rgb):
    x = rgb/255.
    return np.where(x <= .04045, x/12.92, ((x+.055)/1.055)**2.4)


def srgb(x):
    return 255*np.where(x <= .0031308, x*12.92, 1.055*np.maximum(x, 0)**(1/2.4)-.055)


class Scene(base.Scene):
    def __init__(self):
        super().__init__()
        self.v2_active = self.active.copy()
        self.rois['village'] = self.c['village']['roi']
        roi = self.rois['village']
        a, b, z, d = roi
        self.vy, self.vx = np.mgrid[b:d, a:z].astype(np.float32)
        self.plumes = []
        allowed = np.zeros((d-b, z-a), np.float32)
        for c in self.c['village']['plumes']:
            m = poly([c['polygon']], roi, 3)
            rng = np.random.default_rng(c['seed'])
            variations = rng.uniform(.75, 1.25, (round(self.duration/c['birth_interval']), 4))
            self.plumes.append((c, m, variations))
            allowed = np.maximum(allowed, m)
        self.walker_masks = []
        for c in self.c['village']['walkers']:
            route = np.float32(c['route'])
            low, high = route.min(axis=0), route.max(axis=0)
            rectangle = [[low[0]-7, low[1]-c['height']-3], [high[0]+7, low[1]-c['height']-3],
                         [high[0]+7, high[1]+4], [low[0]-7, high[1]+4]]
            m = poly([rectangle], roi, 1)
            occluder = poly(self.c['village']['walker_occluders'], roi, .5)
            m *= 1-occluder
            self.walker_masks.append(m)
            allowed = np.maximum(allowed, m)
        self.masks['village'] = allowed
        self.prepare_lamp()
        for name in ['village', 'lamp']:
            self.active[region(self.rois[name])] |= self.masks[name] > 0

    def prepare_lamp(self):
        c = self.c['lamp']
        roi = self.rois['lamp'] = c['roi']
        rgb = self.base[region(roi)].astype(np.float32)
        warm = smooth((rgb[..., 0]-rgb[..., 2]-8)/56)
        core = poly([c['core_polygon']], roi, 1.1)
        wall = poly([c['wall_polygon']], roi, 16)*warm*c['wall_contribution']
        desk = poly([c['desk_polygon']], roi, 10)*warm*c['desk_contribution']
        desk *= 1-poly([c['chair_blocker']], roi, 1.1)
        reflection = poly([c['reflection_polygon']], roi, 1.5)*warm*c['reflection_contribution']
        halo = cv2.GaussianBlur(core, (0, 0), 3)*warm*.6
        halo[halo < .002] = 0
        self.lamp_parts = {'core': core, 'wall': wall, 'desk': desk, 'reflection': reflection, 'shade_lip': halo}
        self.masks['lamp'] = np.maximum.reduce(list(self.lamp_parts.values()))

    def lamp_amount(self, t):
        amount = 0
        for e in self.c['lamp']['events']:
            age = (float(t)-e['time']) % self.duration
            length = e['rise']+e['hold']+e['fall']
            amount = max(amount, float(smooth(age/e['rise'])*smooth((length-age)/e['fall']))*e['depth'])
        return amount

    def lamp_pixels(self, rgb, t):
        amount = self.lamp_amount(t)
        if amount == 0:
            return rgb
        value = linear(rgb.astype(np.float32))*(1-amount*self.masks['lamp'][..., None])
        return np.clip(np.rint(srgb(value)), 0, 255).astype(np.uint8)

    def plume_pixels(self, t, c, m, variations):
        tau = np.zeros_like(self.vx)
        interval, lifetime = c['birth_interval'], c['life']
        latest = int(np.floor(t/interval))
        for born in range(latest-int(np.ceil(lifetime/interval)), latest+1):
            age = t-born*interval
            if age <= 0 or age >= lifetime:
                continue
            var = variations[born % len(variations)]
            fade = smooth(age/.45)*smooth((lifetime-age)/2.7)
            x = c['anchor'][0]+c['drift_speed']*age+1.2*np.sin(age*.8+var[1]*3)*smooth(age/2)
            y = c['anchor'][1]-c['rise_speed']*age
            dx = (self.vx-x)/(1.1+age*.7*var[2])
            dy = (self.vy-y)/(1.8+age*.85*var[3])
            body = np.exp(-.5*(dx*dx+dy*dy))
            texture = .78+.15*np.sin(dx*2.4+dy*1.9+var[0]*5)+.07*np.sin(dx*5-dy*3.1)
            tau += body*texture*fade*var[0]*c['strength']
        alpha = np.minimum(-np.expm1(-tau), .34)*m
        return alpha, np.float32(c['color'])

    def walkers(self, frame, t):
        roi = self.rois['village']
        a, b, z, d = roi
        scale = 4
        for c, mask in zip(self.c['village']['walkers'], self.walker_masks):
            age = (t-c['start_time']) % self.duration
            if age >= c['seconds']:
                continue
            fade = float(smooth(age/3)*smooth((c['seconds']-age)/3))
            progress = age/c['seconds']
            route = np.float32(c['route'])
            lengths = np.r_[0, np.cumsum(np.linalg.norm(np.diff(route, axis=0), axis=1))]
            x = float(np.interp(progress*lengths[-1], lengths, route[:, 0]))
            y = float(np.interp(progress*lengths[-1], lengths, route[:, 1]))
            height = c['height']
            step = np.sin(age*2*np.pi/1.25)
            canvas = np.zeros(((d-b)*scale, (z-a)*scale, 4), np.uint8)
            def point(px, py):
                return round((px-a)*scale), round((py-b)*scale)
            # Foot contact, small body/coat, head, and two alternating legs.
            cv2.ellipse(canvas, point(x+1.1, y+.2), (round(2.2*scale), round(.55*scale)), 0, 0, 360, (*c['color'], 55), -1, cv2.LINE_AA)
            cv2.line(canvas, point(x, y-height*.68), point(x, y-height*.28), (*c['clothes'], 255), round(1.3*scale), cv2.LINE_AA)
            cv2.circle(canvas, point(x, y-height*.90), round(.62*scale), (*c['color'], 255), -1, cv2.LINE_AA)
            for sign in [-1, 1]:
                cv2.line(canvas, point(x, y-height*.30), point(x+sign*.6*step, y), (*c['color'], 255), 2, cv2.LINE_AA)
            rgba = cv2.resize(canvas, (z-a, d-b), interpolation=cv2.INTER_AREA).astype(np.float32)
            alpha = rgba[..., 3]/255*fade*mask
            frame += (rgba[..., :3]-frame)*alpha[..., None]

    def village_pixels(self, rgb, t):
        frame = rgb.astype(np.float32)
        for c, m, variations in self.plumes:
            alpha, color = self.plume_pixels(t, c, m, variations)
            frame += (color-frame)*alpha[..., None]
        self.walkers(frame, t)
        return np.clip(np.rint(frame), 0, 255).astype(np.uint8)

    def frame(self, t, only=None):
        t = float(t) % self.duration
        frame = super().frame(t, only)
        if only in [None, 'village']:
            r = region(self.rois['village'])
            frame[r] = self.village_pixels(frame[r], t)
        if only in [None, 'lamp']:
            r = region(self.rois['lamp'])
            frame[r] = self.lamp_pixels(frame[r], t)
        return frame

    def fingerprint(self):
        return {**super().fingerprint(), str(Path(__file__).relative_to(ROOT)).replace('\\', '/'): sha(__file__)}


def samples(s):
    folder = HERE/'inspection'
    folder.mkdir(exist_ok=True)
    for name in ['lamp', 'village']:
        r = region(s.rois[name])
        pixels = s.base[r].astype(np.float32)
        pixels += (np.float32([255, 90, 70])-pixels)*s.masks[name][..., None]*.55
        Image.fromarray(np.uint8(np.clip(pixels, 0, 255))).resize((pixels.shape[1]*3, pixels.shape[0]*3)).save(folder/f'{name}-mask-detail.png')
    for t in [6, 14.20, 14.30, 14.62, 22, 40, 44.40, 52]:
        frame = s.frame(t)
        Image.fromarray(cv2.resize(frame, (1280, 720), interpolation=cv2.INTER_AREA)).save(folder/f'combined-{t:05.2f}s.png')
        for name in ['lamp', 'village']:
            crop = frame[region(s.rois[name])]
            Image.fromarray(crop).resize((crop.shape[1]*3, crop.shape[0]*3)).save(folder/f'{name}-{t:05.2f}s.png')
    print('Saved V3 source-scale masks and temporal samples', flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['samples', 'tests', 'full'])
    args = parser.parse_args()
    s = Scene()
    if args.stage == 'samples':
        samples(s)
    elif args.stage == 'tests':
        encode(s, HERE/'Crater-Rim-Survey-v3-village-10s.mp4', 10, only='village', start=5)
        encode(s, HERE/'Crater-Rim-Survey-v3-lamp-8s.mp4', 8, only='lamp', start=11)
    else:
        encode(s, HERE/'Crater-Rim-Survey-v3-60s-loop.mp4', 60)


if __name__ == '__main__':
    main()
