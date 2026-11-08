"""Native Crater Rim V5, with a 60s weather clock and a 600s attention clock.

The frozen renderers and source pixels are unmodified. Each Scene is for one
worker: the clock context is mutable and deliberately not thread-shared.
weather_frame() returns cacheable uint8 RGB at 1672x941. apply_attention()
copies that array, leaves the cache untouched, and applies the three rare
layers in their original order. All other V5 motion keeps its original speed.
"""
from contextlib import contextmanager
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
SNAPSHOT = PACKAGE / 'source-snapshot'
FROZEN = SNAPSHOT / 'music/crater-rim-animation-v5'
WEATHER_PERIOD = 60.0
ATTENTION_PERIOD = 600.0
FPS = 30
PLAN = json.loads((FROZEN / 'long-version-plan.json').read_text(encoding='utf-8'))
SCHEDULE = PLAN['attention_events']
RETAINED_LAYERS = ('clouds', 'shadows', 'haze', 'survey', 'windows', 'village', 'village_lights')
ATTENTION_LAYERS = ('lamp', 'sun_glare', 'traffic')


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def _load_frozen():
    """Use original import names transiently, without altering frozen bytes."""
    names = ('dust_transport', 'periodic_transport', 'v2_renderer_snapshot',
             'v3_renderer_snapshot', 'render_scene')
    previous = {name: sys.modules.get(name) for name in names}
    search_path = sys.path.copy()
    try:
        for name in names:
            path = FROZEN / ('dependencies' if name in names[:2] else '') / (name + '.py')
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
        return sys.modules['render_scene']
    finally:
        sys.path[:] = search_path
        for name, module in previous.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module


v5 = _load_frozen()
region = v5.region


def phase(t, period):
    """Canonicalize actual 30fps frame times, avoiding modulo roundoff drift."""
    t = float(t)
    nearest = round(t * FPS)
    if abs(t * FPS - nearest) < 1e-8:
        return (nearest % round(period * FPS)) / FPS
    return t % period


class Scene(v5.Scene):
    weather_period = WEATHER_PERIOD
    attention_period = ATTENTION_PERIOD

    def __init__(self):
        super().__init__()
        assert self.duration == WEATHER_PERIOD
        self.schedule = SCHEDULE
        self.attention_time = 0.0
        self._attention_enabled = True
        self.lamp_events = []
        for cluster in SCHEDULE['lamp_clusters']:
            for index, offset in zip(cluster['source_event_indices'], cluster['relative_offsets']):
                self.lamp_events.append({**self.c['lamp']['events'][index],
                                         'time': cluster['start'] + offset,
                                         'source_event_index': index})
        self.glare_events = [{**self.c['sun_glare']['events'][entry['source_variant_index']],
                              'time': entry['start'], 'source_variant_index': entry['source_variant_index']}
                             for entry in SCHEDULE['greenhouse_glints']]
        self.traffic_events = [{**self.c['traffic']['events'][entry['source_variant_index']],
                                'time': entry['start'], 'source_variant_index': entry['source_variant_index']}
                               for entry in SCHEDULE['traffic_passages']]
        self.attention_mask = np.zeros_like(self.active)
        for name in ATTENTION_LAYERS:
            self.attention_mask[region(self.rois[name])] |= self.masks[name] > 0
        # In V5 the lamp is before beacons, glare and traffic. Moving it after
        # cached beacons is exact only when their actual supports are disjoint.
        lamp = np.zeros_like(self.active)
        beacon = np.zeros_like(self.active)
        lamp[region(self.rois['lamp'])] = self.masks['lamp'] > 0
        beacon[region(self.rois['village_lights'])] = self.masks['village_lights'] > 0
        self.cache_order_overlap_pixels = int(np.count_nonzero(lamp & beacon))
        assert self.cache_order_overlap_pixels == 0

    @contextmanager
    def _clock(self, absolute_t, enabled=True):
        previous = self.attention_time, self._attention_enabled
        self.attention_time = phase(absolute_t, ATTENTION_PERIOD)
        self._attention_enabled = enabled
        try:
            yield phase(absolute_t, WEATHER_PERIOD)
        finally:
            self.attention_time, self._attention_enabled = previous

    def _event_envelope(self, event, strength):
        age = (self.attention_time - event['time']) % ATTENTION_PERIOD
        length = event['rise'] + event['hold'] + event['fall']
        return float(v5.smooth(age / event['rise']) *
                     v5.smooth((length - age) / event['fall'])) * event[strength]

    def lamp_amount(self, t):
        if not self._attention_enabled:
            return 0.0
        # Frozen V3/V5 uses max(amount, envelope * depth). Match its actual
        # expression and measured peaks, rather than reinterpreting the config.
        return max(self._event_envelope(event, 'depth') for event in self.lamp_events)

    def glare_amount(self, t):
        if not self._attention_enabled:
            return 0.0
        amount = max(self._event_envelope(event, 'strength') for event in self.glare_events)
        if amount == 0:
            return 0.0
        shadow = self.shadow_pixels(t)
        a, b, _, _ = self.rois['shadows']
        local_shadow = float(shadow[426-b, 1400-a])
        return amount * (.45 + .55 * (1 - np.clip(local_shadow / .30, 0, 1)))

    def vehicle_state(self, t, event):
        if not self._attention_enabled:
            return None
        source_index = next(i for i, source in enumerate(self.c['traffic']['events']) if source is event)
        for scheduled in self.traffic_events:
            if scheduled['source_variant_index'] != source_index:
                continue
            age = (self.attention_time - scheduled['time']) % ATTENTION_PERIOD
            if age < scheduled['seconds']:
                # Original event-local age restores route, perspective and body
                # geometry. The explicit 600s gate prevents minute repetitions.
                return v5.Scene.vehicle_state(self, event['time'] + age, event)
        return None

    def attention_active(self, absolute_t):
        """Cheap scheduler gate for encode drivers; no shadow/texture rendering."""
        t = phase(absolute_t, ATTENTION_PERIOD)
        for events in (self.lamp_events, self.glare_events):
            for event in events:
                if (t-event['time']) % ATTENTION_PERIOD < event['rise']+event['hold']+event['fall']:
                    return True
        return any((t-event['time']) % ATTENTION_PERIOD < event['seconds'] for event in self.traffic_events)

    def frame(self, absolute_t, only=None):
        if only is not None and only not in RETAINED_LAYERS + ATTENTION_LAYERS:
            raise ValueError('Unknown layer: ' + str(only))
        with self._clock(absolute_t) as weather_t:
            return super().frame(weather_t, only)

    def weather_frame(self, t, only=None):
        """All seven retained V5 layers, with lamp/glare/traffic disabled."""
        if only is not None and only not in RETAINED_LAYERS:
            raise ValueError('Not a weather/retained layer: ' + str(only))
        with self._clock(t, enabled=False) as weather_t:
            return super().frame(weather_t, only)

    def apply_attention(self, native_weather, absolute_t):
        """Exact cache decomposition: uint8 RGB in, independent uint8 RGB out."""
        if native_weather.shape != self.base.shape or native_weather.dtype != np.uint8:
            raise ValueError('Expected native 941x1672x3 uint8 RGB weather frame')
        frame = native_weather.copy()
        with self._clock(absolute_t) as weather_t:
            for name, effect in (('lamp', self.lamp_pixels), ('sun_glare', self.glare_pixels),
                                 ('traffic', self.traffic_pixels)):
                r = region(self.rois[name])
                frame[r] = effect(frame[r], weather_t)
        return frame

    def fingerprint(self):
        manifest = json.loads((SNAPSHOT/'manifest.json').read_text(encoding='utf-8-sig'))
        return {**{entry['snapshot_path']: digest(PACKAGE/entry['snapshot_path'])
                   for entry in manifest['files']}, 'visual/long_scene.py': digest(__file__)}
