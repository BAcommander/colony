"""Add persistent dust outside the opening and cloud lightning to the prior storm test."""
import json
from pathlib import Path
import subprocess
import sys

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "beneath-a-crimson-sky-animation-v3"))
from render_dust_pass import FF, FPS, FRAMES, HEIGHT, WIDTH, decode, frame_bytes, sha, smooth

BASE = HERE.parent / "beneath-a-crimson-sky-sandstorm-test/beneath-a-crimson-sky-sandstorm-test-60s.mp4"
BASE_SHA = "0073af717e57b3f59cd4a05af24cbf790c5caaf1123f0ce99e743dd99ecbd53e"
OUT = HERE / "persistent-storm-silent.mp4"
X0, Y0, X1, Y1 = 182, 86, 1280, 580
# Time, cloud centre, horizontal/vertical reach, diffuse brightness, return stroke, and visible channel.
FLASHES = ((16.7, 1090, 274, 143, 47, 36, .23, False),
           (26.4, 1155, 312, 141, 36, 46, .46, True),
           (43.8, 956, 302, 142, 44, 40, .18, False),
           (50.6, 1098, 288, 136, 39, 37, .39, True))


def gauss(x):
    return np.exp(-0.5 * x*x)


class Effects:
    def __init__(self):
        self.y, self.x = np.mgrid[Y0:Y1, X0:X1].astype(np.float32)
        edge_x = (182, 193, 224, 274, 340, 475, 480, 551, 675, 824, 1000, 1070, 1074, 1092, 1175, 1207, 1213, 1280)
        edge_y = (470, 470, 472, 489, 491, 501, 496, 492, 518, 535, 547, 553, 552, 542, 547, 553, 572, 575)
        wall = np.interp(self.x, edge_x, edge_y)
        self.wall = wall.astype(np.float32)
        self.mask = (smooth((self.wall - self.y - 4) / 11) * smooth((self.x - 187) / 46) *
                     smooth((self.y - 331) / 69)).astype(np.float32)
        self.near = np.s_[386-Y0:, :]
        rng = np.random.default_rng(40509)
        self.noises = (rng.random((80, 66), dtype=np.float32), rng.random((96, 184), dtype=np.float32),
                       rng.random((108, 360), dtype=np.float32))
        self.grit = np.column_stack((rng.uniform(0, 1, 860), rng.uniform(0, 1, 860),
                                     rng.uniform(0, 1, 860), rng.uniform(0, 1, 860)))
        self.light_shapes = []
        for index, (_, cx, cy, rx, ry, _, _, visible) in enumerate(FLASHES):
            u = self.x - cx
            v = self.y - cy
            glow = gauss(u / rx) * gauss((v + 7 * np.sin(u / 54 + index)) / ry)
            glow *= smooth((self.y - 174) / 65) * smooth((370 - self.y) / 48) * smooth((self.x - 909) / 74)
            path = np.zeros(self.x.shape, np.uint8)
            if visible:
                # Thin, partly buried segments, below the cloud deck and away from the moon.
                offsets = [(8, -17), (3, -9), (9, -3), (1, 2), (0, 11), (-9, 17), (-13, 25), (-22, 31)]
                lines = (offsets, [offsets[3], (-9, 5), (-12, 13), (-23, 18)],
                         [offsets[5], (-1, 19), (3, 27)])
                for segment, opacity in zip(lines, (220, 146, 118)):
                    coords = np.asarray([(cx+a-X0, cy+b-Y0) for a, b in segment], dtype=np.int32)
                    cv2.polylines(path, [coords], False, opacity, 1, cv2.LINE_AA)
                path = path.astype(np.float32) / 255
                path *= np.clip(.55 + .35*np.sin(self.x / 7 + self.y / 8), .20, .95)
            self.light_shapes.append((glow.astype(np.float32), path))

    def sand(self, t):
        t %= 60
        phase = t / 60
        x, y, wall = self.x[self.near], self.y[self.near], self.wall[self.near]
        low_mask = self.mask[self.near]
        first = gauss((((t - 19.5 + 30) % 60) - 30) / 6.7)
        second = gauss((((t - 41.5 + 30) % 60) - 30) / 8.1)
        strength = .52 + .27 * first + .32 * second
        turbulence = np.zeros_like(x)
        for i, (field, scale, yscale, weight, wraps) in enumerate(zip(
                self.noises, (73, 24, 14), (21, 11, 5.2), (.51, .32, .17), (1, 1, 2))):
            u = x / scale - phase * field.shape[1] * wraps
            v = y / yscale + .64 * np.sin(u * (0.42 + i*.08) + phase * 2*np.pi)
            turbulence += weight * cv2.remap(field, u, v, cv2.INTER_CUBIC, borderMode=cv2.BORDER_WRAP)
        flow = wall - y
        waviness = np.sin(x / 116 - phase * 8*np.pi) * 12 + np.sin(x / 41 - phase * 20*np.pi) * 4
        ribbons = .78 * gauss((flow - 22 - waviness) / 14) + .58 * gauss((flow - 69 + waviness*.7) / 20)
        lifting = .52 * gauss((flow - 91 - 11*np.sin(x/94 - phase * 10*np.pi)) / 32)
        dust = (low_mask * strength * np.clip((turbulence - .16) / .75, 0, 1)**1.45 *
                (ribbons + lifting * (.32 + .68*smooth((x - 702) / 520))))
        veil = np.zeros_like(self.mask)
        veil[self.near] = np.clip(dust, 0, .51)

        grit = np.zeros(self.mask.shape, dtype=np.uint8)
        # Renew beyond both sides of the window. Integer wraps per minute close the loop.
        px = 132 + 1258 * ((self.grit[:, 0] + phase * (3 + np.floor(self.grit[:, 2]*4))) % 1)
        py = (365 + 185*self.grit[:, 1] + .038*(px - 700) +
              8*np.sin(px/61 + self.grit[:, 0]*13 - phase*8*np.pi))
        for sx, sy, size, power in zip(px, py, self.grit[:, 2], self.grit[:, 3]):
            ix, iy = int(sx)-X0, int(sy)-Y0
            if not (8 <= ix < grit.shape[1] and 2 <= iy < grit.shape[0]-2):
                continue
            mask = float(self.mask[iy, ix])
            if mask < .02:
                continue
            opacity = int(255 * mask * strength * (.04 + .21*power) * (.48 + float(veil[iy, ix])))
            if opacity >= 4:
                length = 2 + int(5*size)
                cv2.line(grit, (ix-length, iy-1), (ix, iy), opacity, 1, cv2.LINE_AA)
        return veil, grit.astype(np.float32) * (self.mask / 255)

    def lighting(self, t):
        glow = np.zeros_like(self.mask)
        channel = np.zeros_like(self.mask)
        for event, (shape, path) in zip(FLASHES, self.light_shapes):
            dt = t - event[0]
            if not -.15 <= dt <= .85:
                continue
            first = float(gauss((dt - .027) / .040))
            repeat = event[6] * float(gauss((dt - .19) / .059))
            tail = float(smooth(dt / .055) * (1 - smooth((dt - .08) / .64))) * .19
            glow += event[5] * (first + repeat + tail) * shape
            channel += (first + repeat * .51) * path
        return glow, channel


def composite(frame, veil, grit, glow, channel):
    values = np.frombuffer(frame, np.uint8).copy()
    ysize = WIDTH*HEIGHT
    usize = ysize + ysize//4
    planes = (values[:ysize].reshape(HEIGHT, WIDTH)[Y0:Y1, X0:X1],
              values[ysize:usize].reshape(HEIGHT//2, WIDTH//2)[Y0//2:Y1//2, X0//2:X1//2],
              values[usize:].reshape(HEIGHT//2, WIDTH//2)[Y0//2:Y1//2, X0//2:X1//2])
    for i, plane in enumerate(planes):
        col = plane.astype(np.float32)
        shrink = lambda v: v.reshape(v.shape[0]//2, 2, v.shape[1]//2, 2).mean(axis=(1, 3)) if i else v
        col += shrink(glow) * (1, .16, -.12)[i]
        col += ((201, 129, 136)[i] - col) * shrink(channel) * .81
        col += ((135, 116, 146)[i] - col) * shrink(veil)
        col += ((171, 111, 148)[i] - col) * shrink(grit)
        plane[:] = np.clip(np.rint(col), 0, 255).astype(np.uint8)
    return values.tobytes()


def main():
    cv2.setNumThreads(1)
    assert sha(BASE) == BASE_SHA and not OUT.exists()
    fx = Effects()
    for beginning, end in zip(fx.sand(0), fx.sand(60)):
        np.testing.assert_array_equal(beginning, end)
    path = OUT.with_suffix(".partial.mp4")
    command = [FF, "-v", "error", "-n", "-f", "rawvideo", "-pix_fmt", "yuv420p", "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS),
               "-colorspace", "bt709", "-color_range", "tv", "-i", "pipe:0", "-an", "-c:v", "libx264", "-preset", "ultrafast",
               "-qp", "0", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
               "-color_range", "tv", "-movflags", "+faststart", str(path)]
    import hashlib
    expected = []
    coverage = []
    with decode(BASE) as source, subprocess.Popen(command, stdin=subprocess.PIPE) as writer:
        for i in range(FRAMES):
            base = frame_bytes(source)
            assert len(base) == WIDTH*HEIGHT*3//2
            t = i/FPS
            veil, grit = fx.sand(t)
            frame = composite(base, veil, grit, *fx.lighting(t))
            if i % FPS == 0:
                coverage.append(int((veil > .12).sum()))
                y = np.frombuffer(frame, np.uint8, count=WIDTH*HEIGHT).reshape(HEIGHT, WIDTH)
                orig = np.frombuffer(base, np.uint8, count=WIDTH*HEIGHT).reshape(HEIGHT, WIDTH)
                np.testing.assert_array_equal(y[:, :X0], orig[:, :X0])
                np.testing.assert_array_equal(y[Y1:], orig[Y1:])
                np.testing.assert_array_equal(y[370:Y1, X0:X1][fx.mask[370-Y0:] == 0],
                                              orig[370:Y1, X0:X1][fx.mask[370-Y0:] == 0])
            expected.append(hashlib.blake2b(frame, digest_size=16).digest())
            writer.stdin.write(frame)
        assert not frame_bytes(source) and source.wait() == 0
        writer.stdin.close()
        assert writer.wait() == 0
    assert min(coverage) > 1500
    with decode(path) as result:
        for i, fingerprint in enumerate(expected):
            assert hashlib.blake2b(frame_bytes(result), digest_size=16).digest() == fingerprint, i
        assert not frame_bytes(result) and result.wait() == 0
    path.rename(OUT)
    report = {"source_sha256": BASE_SHA, "video_sha256": sha(OUT), "frames": FRAMES, "dimensions": [WIDTH, HEIGHT], "fps": FPS,
              "all_frames_verified": True, "storm_loop_states_equal": True, "sampled_shelter_pixels_unchanged": True,
              "minimum_sampled_pixels_above_12_percent_veil": min(coverage), "maximum_sampled_pixels_above_12_percent_veil": max(coverage),
              "new_flash_seconds": [event[0] for event in FLASHES], "new_visible_channel_seconds": [e[0] for e in FLASHES if e[-1]]}
    (HERE / "visual-checks.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
