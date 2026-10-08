"""Coherent, textured ground gusts with optical extinction and forward advection."""
import cv2
import numpy as np

class DustTransport:
    def __init__(self, x, y, config, duration):
        self.x, self.y, self.c, self.duration = x, y, config, duration
        self.x0, self.y0 = float(x.min()), float(y.min())
        self.padding = 700
        height, width = x.shape
        rng = np.random.default_rng(config['seed'])
        # Multiscale structure travels with each gust, rather than modulating a fixed ribbon.
        shape = (height + 180, width + 2*self.padding)
        field = np.zeros(shape, np.float32)
        for cells, weight in [((9, 30), .52), ((24, 80), .30), ((55, 190), .18)]:
            coarse = rng.random(cells, dtype=np.float32)
            field += cv2.resize(coarse, (shape[1], shape[0]), interpolation=cv2.INTER_CUBIC)*weight
        self.field = np.clip(field, 0, 1)
        self.local_x = x - self.x0 + self.padding
        self.local_y = y - self.y0 + 90

    def density(self, t, prototype):
        total = np.zeros_like(self.x)
        highlight = np.zeros_like(self.x)
        c = self.c
        entries=[(index,gust,t,1.0) for index,gust in enumerate(c['gusts'])]
        if prototype:
            for arrival in c.get('incoming_gusts',[]):
                elapsed=t-arrival['start']
                if elapsed <= 0:continue
                fade=np.clip(elapsed/arrival['fade_in'],0,1)
                fade=fade*fade*(3-2*fade)
                entries.append((arrival['texture_index'],arrival['gust'],elapsed,fade))
        for index, gust, local_t, incoming_fade in entries:
            age = (t/c['lifetime'] + gust['phase']) % 1
            elapsed = local_t if prototype else (age-.5)*c['lifetime']
            fade = incoming_fade if prototype else np.sin(np.pi*age)**2
            travel = c['speed']*elapsed
            dx = self.x - (gust['x'] + travel)
            center_y = gust['y'] + gust['route_slope']*travel
            dy = self.y - center_y
            bend = gust['height']*.22*np.sin(dx/gust['width']*3 + index)
            noise = cv2.remap(self.field,
                (self.local_x-travel+index*93).astype(np.float32),
                (self.local_y-gust['route_slope']*travel+5*np.sin(t*.5+index)).astype(np.float32),
                cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
            # Offset lobes create broken billowing edges, not a smooth smoke stripe.
            body = np.zeros_like(dx)
            for ox, oy, radius, gain in [(-.65,.13,.65,.58),(-.10,-.05,.78,1),(.60,-.17,.58,.68)]:
                u = (dx/gust['width']-ox)/radius
                v = ((dy-bend)/gust['height']-oy)/(radius*.9)
                body += np.exp(-.5*(u*u+v*v))*gain
            texture = np.clip((noise-.24)*2.5, .025, 1.6)
            density = body*texture*gust['strength']*fade
            total += density
            highlight += density*noise
        alpha = np.minimum(1-np.exp(-total*c['optical_depth']), c['max_opacity'])
        lighting = .85+.22*highlight/np.maximum(total,1e-5)
        color = np.array(c['color'],np.float32)*lighting[...,None]
        return alpha.astype(np.float32), np.clip(color,0,255)
