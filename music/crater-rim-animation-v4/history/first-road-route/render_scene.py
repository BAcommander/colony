"""Crater Rim V4: pane-local sun glints, attached tower lights and two road passages."""
import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

import v3_renderer_snapshot as base

HERE, ROOT, PLAN_PATH = base.HERE, base.ROOT, base.PLAN_PATH
FFMPEG, sha, region, smooth = base.FFMPEG, base.sha, base.region, base.smooth
poly, linear, srgb, encode = base.poly, base.linear, base.srgb, base.encode


def envelope(t, start, rise, hold, fall, duration=60):
    age = (float(t)-start) % duration
    return float(smooth(age/rise)*smooth((rise+hold+fall-age)/fall))


def curve(points):
    p = np.float32(points)
    extended = np.concatenate([p[:1], p, p[-1:]])
    segments = []
    for i in range(len(p)-1):
        a, b, c, d = extended[i:i+4]
        t = np.linspace(0, 1, 80, endpoint=False, dtype=np.float32)[:, None]
        segment = .5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)
        segments.append(segment)
    result = np.concatenate([*segments, p[-1:]])
    length = np.r_[0, np.cumsum(np.linalg.norm(np.diff(result, axis=0), axis=1))]
    tangent = np.gradient(result, axis=0)
    tangent /= np.maximum(np.linalg.norm(tangent, axis=1, keepdims=True), 1e-8)
    return result, length, tangent


class Scene(base.Scene):
    def __init__(self):
        super().__init__()
        for name in ['village_lights', 'sun_glare', 'traffic']:
            self.rois[name] = self.c[name]['roi']
        self.light_fields = []
        a, b, z, d = self.rois['village_lights']
        y, x = np.mgrid[b:d, a:z].astype(np.float32)
        union = np.zeros_like(x)
        for c in self.c['village_lights']['beacons']:
            cx, cy = c['anchor']
            distance = np.hypot(x-cx, y-cy)
            core = np.exp(-.5*(distance/c['radius'])**2)
            halo = np.exp(-.5*(distance/self.c['village_lights']['halo_radius'])**2)
            field = np.maximum(core*.94, halo*self.c['village_lights']['halo_strength'])
            field[distance > 7] = 0
            self.light_fields.append((c, field))
            union = np.maximum(union, field)
        self.masks['village_lights'] = union
        a, b, z, d = self.rois['sun_glare']
        y, x = np.mgrid[b:d, a:z].astype(np.float32)
        c = self.c['sun_glare']
        field = np.zeros_like(x)
        for lobe in c['lobes']:
            cx, cy = lobe['center']
            rx, ry = lobe['radius']
            angle = np.deg2rad(lobe['angle'])
            u = (x-cx)*np.cos(angle)+(y-cy)*np.sin(angle)
            v = -(x-cx)*np.sin(angle)+(y-cy)*np.cos(angle)
            field += np.exp(-.5*((u/rx)**2+(v/ry)**2))*lobe['gain']
        glass = poly([c['glass_polygon']], self.rois['sun_glare'], 1.5)
        rgb = self.base[region(self.rois['sun_glare'])].astype(np.float32)
        lum = rgb@np.float32([.2126, .7152, .0722])
        low, high = c['frame_preservation_thresholds']
        field *= glass*(1-.85*smooth((lum-low)/(high-low)))
        field[field < .003] = 0
        self.masks['sun_glare'] = field
        c = self.c['traffic']
        road = poly([c['road_polygon']], self.rois['traffic'], .65)
        road *= 1-poly([c['ledge_blocker']], self.rois['traffic'], .5)
        self.masks['traffic'] = road
        self.road_curve, self.road_length, self.road_tangent = curve(c['route'])
        for name in ['village_lights', 'sun_glare', 'traffic']:
            self.active[region(self.rois[name])] |= self.masks[name] > 0

    def beacon_pixels(self, rgb, t):
        c = self.c['village_lights']
        frame = rgb.astype(np.float32)
        for beacon, field in self.light_fields:
            amount = max(envelope(t, start, c['rise'], c['hold'], c['fall']) for start in beacon['times'])
            alpha = field*amount
            frame += (np.float32(beacon['color'])-frame)*alpha[..., None]
        return np.clip(np.rint(frame), 0, 255).astype(np.uint8)

    def glare_amount(self, t):
        amount = max(envelope(t, e['time'], e['rise'], e['hold'], e['fall'])*e['strength'] for e in self.c['sun_glare']['events'])
        # Incoming light is weaker while the existing cloud shadow covers the glass.
        shadow = self.shadow_pixels(t)
        a, b, z, d = self.rois['shadows']
        local_shadow = float(shadow[426-b, 1400-a])
        return amount*(.45+.55*(1-np.clip(local_shadow/.30, 0, 1)))

    def glare_pixels(self, rgb, t):
        amount = self.glare_amount(t)
        if amount == 0:
            return rgb
        radiance = linear(rgb.astype(np.float32))
        radiance += self.masks['sun_glare'][..., None]*amount*linear(np.float32(self.c['sun_glare']['color']))
        return np.clip(np.rint(srgb(radiance)), 0, 255).astype(np.uint8)

    def vehicle_state(self, t, event):
        age = (float(t)-event['time']) % self.duration
        if age >= event['seconds']:
            return None
        progress = age/event['seconds']
        if event['reverse']:
            progress = 1-progress
        distance = progress*self.road_length[-1]
        center = np.array([np.interp(distance, self.road_length, self.road_curve[:, i]) for i in [0, 1]])
        tangent = np.array([np.interp(distance, self.road_length, self.road_tangent[:, i]) for i in [0, 1]])
        tangent /= np.linalg.norm(tangent)
        if event['reverse']:
            tangent *= -1
        near = float(smooth((center[1]-548)/96))
        far, close = self.c['traffic']['size_far'], self.c['traffic']['size_near']
        size = {key: far[key]+near*(close[key]-far[key]) for key in far}
        return center, tangent, size

    def traffic_pixels(self, rgb, t):
        roi = self.rois['traffic']
        a, b, z, d = roi
        scale = 6
        frame = rgb.astype(np.float32)
        for event in self.c['traffic']['events']:
            state = self.vehicle_state(t, event)
            if state is None:
                continue
            center, heading, size = state
            side = np.array([-heading[1], heading[0]])
            length, width, height = size['length'], size['width'], size['height']
            canvas = np.zeros(((d-b)*scale, (z-a)*scale, 4), np.uint8)
            def point(value):
                return tuple(np.rint((value-[a, b])*scale).astype(int))
            def quad(points, color):
                cv2.fillConvexPoly(canvas, np.int32([point(v) for v in points]), (*color, 255), cv2.LINE_AA)
            # The contact shadow and wheels establish that this is a solid vehicle on the road.
            cv2.ellipse(canvas, point(center+[1, .8]), (round(length*.65*scale), round(width*.58*scale)),
                        float(np.rad2deg(np.arctan2(heading[1], heading[0]))), 0, 360, (35, 32, 27, 77), -1, cv2.LINE_AA)
            corners = [center+heading*length*u+side*width*v for u, v in [(-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5)]]
            quad(corners, [56, 57, 49])
            raised = [v+[0, -height*.65] for v in corners]
            quad([corners[2], corners[3], raised[3], raised[2]], event['body_color'])
            quad(raised, event['roof_color'])
            cabin_center = center+heading*length*.13+[0, -height*.78]
            cabin = [cabin_center+heading*length*u+side*width*v for u, v in [(-.21, -.40), (.22, -.40), (.22, .40), (-.21, .40)]]
            quad(cabin, [63, 83, 81])
            for axle in [-.32, .32]:
                for flank in [-.51, .51]:
                    c = center+heading*length*axle+side*width*flank
                    cv2.circle(canvas, point(c), round(.48*scale), (44, 43, 36, 255), -1, cv2.LINE_AA)
            # Two small day-running lenses stay attached to the front corners.
            for flank in [-.34, .34]:
                c = center+heading*length*.48+side*width*flank+[0, -height*.45]
                cv2.circle(canvas, point(c), 2, (236, 226, 182, 255), -1, cv2.LINE_AA)
            rgba = cv2.resize(canvas, (z-a, d-b), interpolation=cv2.INTER_AREA).astype(np.float32)
            alpha = rgba[..., 3]/255*self.masks['traffic']
            frame += (rgba[..., :3]-frame)*alpha[..., None]
        return np.clip(np.rint(frame), 0, 255).astype(np.uint8)

    def frame(self, t, only=None):
        t = float(t) % self.duration
        frame = super().frame(t, only)
        for name, effect in [('village_lights', self.beacon_pixels), ('sun_glare', self.glare_pixels), ('traffic', self.traffic_pixels)]:
            if only in [None, name]:
                r = region(self.rois[name])
                frame[r] = effect(frame[r], t)
        return frame

    def fingerprint(self):
        return {**super().fingerprint(), str(Path(__file__).relative_to(ROOT)).replace('\\', '/'): sha(__file__)}


def samples(s):
    folder = HERE/'inspection'
    for name in ['village_lights', 'sun_glare', 'traffic']:
        r = region(s.rois[name])
        pixels = s.base[r].astype(np.float32)
        m = np.clip(s.masks[name]*3, 0, 1)
        pixels += (np.float32([255, 70, 90])-pixels)*m[..., None]*.6
        Image.fromarray(np.uint8(np.clip(pixels, 0, 255))).resize((pixels.shape[1]*4, pixels.shape[0]*4)).save(folder/f'{name}-mask.png')
    for t in [5, 10, 14.3, 19, 21.4, 25, 35, 44.4, 48.1, 52, 56]:
        frame = s.frame(t)
        Image.fromarray(cv2.resize(frame, (1280, 720), interpolation=cv2.INTER_AREA)).save(folder/f'combined-{t:05.2f}s.png')
        for name in ['traffic', 'sun_glare', 'village_lights']:
            crop = frame[region(s.rois[name])]
            Image.fromarray(crop).resize((crop.shape[1]*5, crop.shape[0]*5)).save(folder/f'{name}-{t:05.2f}s.png')
    print('Saved V4 native-source masks and temporal samples', flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['samples', 'test', 'full'])
    args = parser.parse_args()
    s = Scene()
    if args.stage == 'samples':
        samples(s)
    elif args.stage == 'test':
        encode(s, HERE/'Crater-Rim-Survey-v4-new-effects-10s.mp4', 10, start=15)
    else:
        encode(s, HERE/'Crater-Rim-Survey-v4-60s-loop.mp4', 60)


if __name__ == '__main__':
    main()
