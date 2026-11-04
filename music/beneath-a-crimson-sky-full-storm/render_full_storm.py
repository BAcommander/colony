"""Full-aperture dust and two sustained lightning sequences for Skies of Baal."""
import json
from pathlib import Path
import subprocess
import sys

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parent / "beneath-a-crimson-sky-persistent-storm"
sys.path.insert(0, str(PREVIOUS))
from render_visual import BASE, BASE_SHA, Effects as PreviousEffects, FF, FPS, FRAMES, HEIGHT, WIDTH, composite, decode, frame_bytes, gauss, sha, smooth

OUTPUT = HERE / "skies-of-baal-full-opening-storm-60s.mp4"
AUDIO = PREVIOUS / "storm-audition-mix.wav"
LEFT, RIGHT, BOTTOM = 182, 1280, 580
# The lower edge follows the steps in the parapet. The upper edge follows the
# underside of the terrace's woodwork, including its three hanging brackets.
OPENING = ((191, 85), (218, 78), (235, 58), (287, 53), (341, 46), (400, 39), (420, 42),
           (444, 57), (459, 52), (466, 34), (520, 26), (609, 20), (674, 12), (691, 32),
           (711, 34), (721, 11), (740, 0), (1279, 0), (1279, 574), (1214, 571),
           (1208, 556), (1182, 548), (1110, 542), (1077, 553), (1004, 548), (912, 541),
           (814, 532), (734, 522), (675, 519), (563, 499), (547, 495), (492, 492),
           (474, 501), (372, 494), (269, 488), (246, 472), (193, 470))

# Long branches begin in the right-hand cloud bank and reach the distant plain.
# The smaller earlier strikes are replaced at these two original thunder cues.
EVENTS = (
    (26.4, 3.1, (1145, 189), ((1145,189),(1141,209),(1132,221),(1138,233),(1131,254),
      (1140,265),(1134,282),(1148,299),(1145,316),(1135,331),(1140,347),(1127,362),
      (1129,378),(1123,390),(1124,411)),
     (((1138,233),(1125,242),(1106,249),(1102,267),(1081,276),(1077,289)),
      ((1148,299),(1157,304),(1166,325),(1181,332),(1185,348)),
      ((1135,331),(1116,337),(1109,354),(1096,360)))),
    (50.6, 3.4, (1101, 180), ((1101,180),(1094,199),(1100,211),(1091,224),(1098,242),
      (1093,255),(1102,274),(1116,284),(1113,299),(1129,310),(1140,330),(1152,341),
      (1149,359),(1160,378),(1155,388),(1158,421)),
     (((1098,242),(1075,250),(1068,264),(1048,272),(1045,285)),
      ((1116,284),(1139,283),(1151,295),(1172,300),(1180,313)),
      ((1152,341),(1170,350),(1180,366),(1191,365),(1203,379)))),
)


class FullStorm:
    def __init__(self):
        self.x, self.y = np.meshgrid(np.arange(LEFT, RIGHT, dtype=np.float32), np.arange(BOTTOM, dtype=np.float32))
        silhouette = np.zeros_like(self.x, dtype=np.uint8)
        poly = np.asarray(OPENING, np.int32) - (LEFT, 0)
        cv2.fillPoly(silhouette, [poly.astype(np.int32)], 1)
        distance = cv2.distanceTransform(silhouette, cv2.DIST_L2, 5)
        self.mask = smooth((distance - 1.5) / 7)
        # Work on a half-resolution volume and reconstruct at the opening.
        self.dx, self.dy = self.x[::2, ::2], self.y[::2, ::2]
        rng = np.random.default_rng(51771)
        self.maps = [rng.random((96, n), dtype=np.float32) for n in (48, 166, 420)]
        self.grains = rng.uniform(0, 1, (1250, 4)).astype(np.float32)
        self.forks = []
        for j, (_, _, cloud, trunk, forks) in enumerate(EVENTS):
            # Add irregular sub-jogs so the drawn path breaks at finer scales.
            def trace(points):
                pieces = []
                for (x, y), (x2, y2) in zip(points, points[1:]):
                    pieces.extend(((x, y), ((x+x2)*.5 + rng.uniform(-3, 3), (y+y2)*.5 + rng.uniform(-1, 1))))
                pieces.append(points[-1])
                return np.rint(np.asarray(pieces) - (LEFT, 0)).astype(np.int32)

            core = np.zeros_like(silhouette)
            for path, brightness in [(trunk, 255), *zip(forks, (188, 153, 139))]:
                cv2.polylines(core, [trace(path)], False, int(brightness), 1, cv2.LINE_AA)
            core = core.astype(np.float32) / 255
            cloud_x, cloud_y = cloud
            strike_x, strike_y = trunk[-1]
            cloud_glow = gauss((self.x-cloud_x)/96) * gauss((self.y-cloud_y-18)/61)
            ground_glow = gauss((self.x-strike_x)/57) * gauss((self.y-strike_y-1)/17)
            sky_depth = (.66 + .34*smooth((self.y - 186) / 105))
            core *= sky_depth
            broad = cv2.GaussianBlur(core, (0, 0), 8.5)
            halo = cv2.GaussianBlur(core, (0, 0), 2.0)
            self.forks.append((core, halo, broad, cloud_glow, ground_glow))

    def dust(self, t):
        t %= 60
        phase = t / 60
        angle = phase * 2*np.pi
        noise = np.zeros_like(self.dx)
        for field, width, height, weight, loops in zip(self.maps, (97, 29, 12), (64, 19, 7), (.49, .33, .18), (1, 2, 2)):
            u = self.dx / width - phase * loops * field.shape[1]
            v = self.dy / height + .55*np.sin(2*np.pi*u / 12 + angle) + .22*np.sin(2*np.pi*u / 5 - 3*angle)
            noise += weight * cv2.remap(field, u, v, cv2.INTER_CUBIC, borderMode=cv2.BORDER_WRAP)
        pulse = lambda centre, spread: gauss((((t-centre+30)%60)-30)/spread)
        strength = .75 + .18*pulse(19, 6) + .28*pulse(41, 7.4)
        streams = .82 + .18*np.sin(self.dy/49 + self.dx/440 - 3*angle) + .12*np.sin(self.dy/21 - self.dx/219 + 5*angle)
        dust = strength * (.085 + .38*smooth((noise-.19)/.65)*streams)
        dust *= .87 + .21*smooth((self.dy-84)/350)
        veil = cv2.resize(dust, (RIGHT-LEFT, BOTTOM), interpolation=cv2.INTER_LINEAR) * self.mask

        # Strong, fast, fine streaks occupy the whole aperture, with heavier grains near the wall.
        grit = np.zeros_like(veil, np.uint8)
        px = 130 + 1260*((self.grains[:, 0] + phase*(4+np.floor(self.grains[:, 2]*4))) % 1)
        py = 8 + 568*self.grains[:, 1] + 14*np.sin(px/90 + self.grains[:, 0]*8 - angle*3)
        for x, y, size, power in zip(px, py, self.grains[:, 2], self.grains[:, 3]):
            ix, iy = int(x)-LEFT, int(y)
            if not (10 <= ix < grit.shape[1] and 2 <= iy < grit.shape[0]-2 and self.mask[iy, ix] > .1):
                continue
            opacity = int((10+30*power)*strength*(.48+1.18*veil[iy, ix]))
            cv2.line(grit, (ix-(3+int(size*6)), iy-1), (ix, iy), opacity, 1, cv2.LINE_AA)
        return veil, grit.astype(np.float32) * (self.mask / 255)

    def lightning(self, t):
        for (at, length, *_), (core, halo, broad, cloud, ground) in zip(EVENTS, self.forks):
            elapsed = t-at
            if not at <= t < at + length:
                continue
            envelope = float(1-smooth((elapsed-length+.82)/.82))
            # A faint channel remains visible between distinct return strokes.
            pulse = .34 + .93*float(gauss((elapsed-.034)/.055))
            for delay, width, gain in ((.42,.077,.63), (1.12,.11,.47), (1.85,.12,.57), (2.46,.16,.35)):
                pulse += gain*float(gauss((elapsed-delay)/width))
            pulse *= envelope
            glow = pulse*(57*halo + 104*broad + 28*cloud + 18*ground)
            return pulse*core*self.mask, glow*self.mask
        return None

    def blend(self, base, veil, grit, strike):
        pixels = np.frombuffer(base, np.uint8).copy()
        ysize = WIDTH*HEIGHT
        usize = ysize + ysize//4
        planes = (pixels[:ysize].reshape(HEIGHT, WIDTH)[:BOTTOM, LEFT:RIGHT],
                  pixels[ysize:usize].reshape(HEIGHT//2, WIDTH//2)[:BOTTOM//2, LEFT//2:RIGHT//2],
                  pixels[usize:].reshape(HEIGHT//2, WIDTH//2)[:BOTTOM//2, LEFT//2:RIGHT//2])
        shrink = lambda v: v.reshape(v.shape[0]//2, 2, v.shape[1]//2, 2).mean(axis=(1,3))
        for i, plane in enumerate(planes):
            v, g = (veil, grit) if i == 0 else (shrink(veil), shrink(grit))
            col = plane.astype(np.float32)
            if strike is not None and i == 0:
                col += strike[1] * (1 + veil * .35)
            col += ((142, 115, 146)[i]-col)*v
            col += ((177, 113, 148)[i]-col)*g
            if strike is not None:
                line = strike[0] if i == 0 else shrink(strike[0])
                col += ((231, 128, 134)[i]-col) * np.clip(line, 0, .88) * (1-.52*v)
            plane[:] = np.clip(np.rint(col), 0, 255).astype(np.uint8)
        return pixels.tobytes()


def main(storm_factory=FullStorm, output=OUTPUT, audio_path=AUDIO, metadata=None):
    cv2.setNumThreads(1)
    assert sha(BASE) == BASE_SHA
    assert not output.exists()
    previous, storm = PreviousEffects(), storm_factory()
    for a, b in zip(storm.dust(0), storm.dust(60)):
        np.testing.assert_array_equal(a, b)
    partial = output.with_suffix(".partial.mp4")
    command = [FF, "-v", "error", "-n", "-f", "rawvideo", "-pix_fmt", "yuv420p", "-s", f"{WIDTH}x{HEIGHT}",
               "-r", str(FPS), "-colorspace", "bt709", "-color_range", "tv", "-i", "pipe:0", "-i", str(audio_path),
               "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264", "-threads", "4", "-preset", "veryfast", "-crf", "17",
               "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
               "-color_range", "tv", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", str(partial)]
    covered = []
    strike_frames = [0, 0]
    top = (storm.mask > .5) & (storm.y < 260)
    with decode(BASE) as source, subprocess.Popen(command, stdin=subprocess.PIPE) as writer:
        for index in range(FRAMES):
            t = index/FPS
            base = frame_bytes(source)
            assert len(base) == WIDTH*HEIGHT*3//2
            previous_veil, previous_grit = previous.sand(t)
            old_glow, old_line = previous.lighting(t)
            for at, _, *_ in EVENTS:
                if -.15 <= t-at <= .85:
                    old_line.fill(0)
                    old_glow *= .52
            lower = composite(base, previous_veil*.74, previous_grit*.67, old_glow, old_line)
            veil, grit = storm.dust(t)
            strike = storm.lightning(t)
            if strike is not None:
                strike_frames[int(t > 40)] += 1
            picture = storm.blend(lower, veil, grit, strike)
            if index % FPS == 0:
                covered.append(float(np.mean(veil[top] > .075)))
                luma = lambda raw: np.frombuffer(raw, np.uint8, count=WIDTH*HEIGHT).reshape(HEIGHT, WIDTH)
                np.testing.assert_array_equal(luma(picture)[:, :LEFT], luma(base)[:, :LEFT])
                np.testing.assert_array_equal(luma(picture)[BOTTOM:], luma(base)[BOTTOM:])
                np.testing.assert_array_equal(luma(picture)[:BOTTOM, LEFT:RIGHT][storm.mask == 0],
                                              luma(lower)[:BOTTOM, LEFT:RIGHT][storm.mask == 0])
            writer.stdin.write(picture)
        assert not frame_bytes(source) and source.wait() == 0
        writer.stdin.close()
        assert writer.wait() == 0
    finalize(partial, covered, strike_frames, output, audio_path, metadata)


def finalize(partial, covered, strike_frames, output=OUTPUT, audio_path=AUDIO, metadata=None):
    assert min(covered) > .80 and strike_frames == [93, 102]
    print("Encoded; checking all 1,800 frames and the effects track.", flush=True)
    with decode(partial) as result:
        for _ in range(FRAMES):
            assert len(frame_bytes(result)) == WIDTH*HEIGHT*3//2
        assert not frame_bytes(result) and result.wait() == 0
    raw = subprocess.check_output([FF, "-v", "error", "-i", str(partial), "-map", "0:a:0", "-f", "f32le", "pipe:1"])
    audio = np.frombuffer(raw, dtype="<f4").reshape(-1, 2)
    assert 2880000 <= len(audio) < 2881024 and np.isfinite(audio).all() and .15 < np.max(np.abs(audio)) < 1
    framehash = subprocess.check_output([FF, "-v", "error", "-i", str(partial), "-map", "0:v:0", "-f", "framehash", "-c", "copy", "pipe:1"], text=True)
    rows = [line.split(",") for line in framehash.splitlines() if line and not line.startswith("#")]
    # B-frames arrive in decode order; sort presentation times for the frame-grid check.
    pts = sorted(int(row[2]) for row in rows)
    assert len(pts) == FRAMES and pts == list(range(0, FRAMES*(pts[1]-pts[0]), pts[1]-pts[0]))
    partial.rename(output)
    report = {"sha256": sha(output), "bytes": output.stat().st_size, "source_sha256": BASE_SHA,
              "effects_audio_sha256": sha(audio_path), "frames": FRAMES, "fps": FPS, "dimensions": [WIDTH, HEIGHT],
              "all_frames_and_audio_decoded": True, "sequential_timestamps": True, "new_dust_loop_states_equal": True,
              "shelter_pixels_checked_before_encode": True, "minimum_upper_opening_share_above_7_5_percent_opacity": min(covered),
              "strike_starts_seconds": [event[0] for event in EVENTS], "strike_active_frames": strike_frames,
              "audio_peak_dbfs": round(float(20*np.log10(np.max(np.abs(audio)))), 2), "user_review": "pending"}
    report.update(metadata or {})
    (output.parent / "delivery.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
