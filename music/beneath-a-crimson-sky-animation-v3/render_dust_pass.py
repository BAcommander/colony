"""Add a terrain-masked dry gust layer to the exact Crimson Sky V2 preview."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

import cv2
import imageio_ffmpeg
import numpy as np


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "beneath-a-crimson-sky-animation-v2/beneath-a-crimson-sky-v2-preview-60s.mp4"
BASE_SHA256 = "0587d9d7d81e0d23b113448de22f6b0cd913cc622e23cba7d23c192f1468c87f"
OUTPUT = HERE / "beneath-a-crimson-sky-v3-dry-gusts-60s.mp4"
WIDTH, HEIGHT, FPS = 1280, 720, 30
SECONDS = 60
FRAMES = SECONDS * FPS
ROI = (656, 420, 1280, 582)
# Start, lifetime, initial screen position, path slope, speed, spread and opacity.
GUSTS = (
    (3.0, 21.5, 703, 475, 0.085, 7.5, 58, 8.0, 0.32),
    (24.5, 20.0, 825, 494, 0.097, 8.2, 68, 7.3, 0.26),
    (48.5, 19.0, 1020, 517, 0.10, 7.2, 60, 7.0, 0.30),
)
PARAPET_X = (656, 730, 810, 920, 1005, 1070, 1120, 1175, 1215, 1280)
PARAPET_Y = (514, 522, 531, 543, 548, 553, 550, 556, 573, 578)
RUINS_AND_ROCKS = (
    ((906, 462), (949, 458), (961, 451), (989, 449), (1012, 468), (1030, 489), (977, 491), (927, 487)),
    ((1010, 523), (1050, 509), (1080, 510), (1115, 506), (1143, 520), (1172, 523), (1192, 536), (1030, 541)),
    ((1193, 542), (1211, 526), (1251, 522), (1279, 531), (1279, 563), (1212, 561)),
)
FF = imageio_ffmpeg.get_ffmpeg_exe()


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def smooth(value):
    clipped = np.clip(value, 0, 1)
    return clipped * clipped * (3 - 2 * clipped)


class Dust:
    def __init__(self):
        left, top, right, bottom = ROI
        self.y, self.x = np.mgrid[top:bottom, left:right].astype(np.float32)
        parapet = np.interp(self.x, PARAPET_X, PARAPET_Y)
        mask = smooth((parapet - 7 - self.y) / 14)
        mask *= smooth((self.x - 680) / 57)
        mask *= smooth((self.y - 431) / 23)
        for outline in RUINS_AND_ROCKS:
            silhouette = np.zeros(mask.shape, dtype=np.uint8)
            points = np.asarray(outline, dtype=np.int32) - (left, top)
            cv2.fillPoly(silhouette, [points.astype(np.int32)], 1)
            distance = cv2.distanceTransform(1 - silhouette, cv2.DIST_L2, 5)
            mask *= smooth((distance - 2) / 9)
        self.mask = mask.astype(np.float32)

    def opacity(self, time):
        alpha = np.zeros_like(self.mask)
        for number, (start, length, x0, y0, slope, speed, width, height, gain) in enumerate(GUSTS):
            age = (time - start) % SECONDS
            if age >= length:
                continue
            envelope = float(smooth(age / 4.2) * smooth((length - age) / 6.5))
            centre = x0 + speed * age
            u = self.x - centre
            ground = y0 + slope * (self.x - x0) + 3.2 * np.sin(u / 36 + number)
            v = self.y - ground
            body = np.exp(-0.5 * ((u / width) ** 2 + (v / height) ** 2))
            tail = np.exp(-0.5 * (((u + 38) / (width * 1.18)) ** 2 + ((v + 6) / (height * 1.48)) ** 2))
            grain = 0.74 + 0.13 * np.sin(u / 19 + v / 5) + 0.09 * np.sin(u / 8 - v / 4.3)
            alpha += envelope * gain * (0.72 * body + 0.28 * tail) * grain
        alpha *= self.mask
        alpha[alpha < 0.003] = 0
        return np.clip(alpha, 0, 0.28)


def decode(path):
    return subprocess.Popen([FF, "-v", "error", "-i", str(path), "-map", "0:v:0",
                             "-f", "rawvideo", "-pix_fmt", "yuv420p", "pipe:1"], stdout=subprocess.PIPE)


def frame_bytes(process):
    return process.stdout.read(WIDTH * HEIGHT * 3 // 2)


def blend(frame, alpha):
    flat = np.frombuffer(frame, dtype=np.uint8).copy()
    y_end = WIDTH * HEIGHT
    u_end = y_end + y_end // 4
    x1, y1, x2, y2 = ROI
    chroma_alpha = alpha.reshape(alpha.shape[0] // 2, 2, alpha.shape[1] // 2, 2).mean(axis=(1, 3))
    planes = (flat[:y_end].reshape(HEIGHT, WIDTH)[y1:y2, x1:x2],
              flat[y_end:u_end].reshape(HEIGHT // 2, WIDTH // 2)[y1//2:y2//2, x1//2:x2//2],
              flat[u_end:].reshape(HEIGHT // 2, WIDTH // 2)[y1//2:y2//2, x1//2:x2//2])
    # Muted, warm mineral dust in the base video's limited-range BT.709 space.
    for plane, opacity, dust_colour in zip(planes, (alpha, chroma_alpha, chroma_alpha), (136, 114, 145)):
        plane[:] = np.rint(plane + (dust_colour - plane.astype(np.float32)) * opacity).astype(np.uint8)
    return flat.tobytes()


def render(dust):
    assert sha(BASE) == BASE_SHA256 and not OUTPUT.exists()
    partial = OUTPUT.with_name(OUTPUT.stem + ".partial.mp4")
    assert not partial.exists()
    command = [FF, "-v", "error", "-n", "-f", "rawvideo", "-pix_fmt", "yuv420p",
               "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS), "-colorspace", "bt709",
               "-color_range", "tv", "-i", "pipe:0", "-an",
               "-c:v", "libx264", "-preset", "ultrafast", "-qp", "0", "-pix_fmt", "yuv420p",
               "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
               "-color_range", "tv", "-movflags", "+faststart", str(partial)]
    with decode(BASE) as source, subprocess.Popen(command, stdin=subprocess.PIPE) as writer:
        for index in range(FRAMES):
            frame = frame_bytes(source)
            assert len(frame) == WIDTH * HEIGHT * 3 // 2
            writer.stdin.write(blend(frame, dust.opacity(index / FPS)))
        assert not frame_bytes(source) and source.wait() == 0
        writer.stdin.close()
        assert writer.wait() == 0
    return partial


def validate(dust, rendered):
    np.testing.assert_array_equal(dust.opacity(0), dust.opacity(SECONDS))
    max_luma_delta = 0
    visible_counts = []
    y_end = WIDTH * HEIGHT
    x1, y1, x2, y2 = ROI
    with decode(BASE) as source, decode(rendered) as result:
        for index in range(FRAMES):
            original, actual = frame_bytes(source), frame_bytes(result)
            assert len(original) == len(actual) == WIDTH * HEIGHT * 3 // 2
            alpha = dust.opacity(index / FPS)
            assert actual == blend(original, alpha), f"Decoded mismatch at frame {index}"
            if index % FPS == 0:
                a = np.frombuffer(original[:y_end], dtype=np.uint8).reshape(HEIGHT, WIDTH)[y1:y2, x1:x2]
                b = np.frombuffer(actual[:y_end], dtype=np.uint8).reshape(HEIGHT, WIDTH)[y1:y2, x1:x2]
                delta = np.abs(a.astype(np.int16) - b)
                assert not np.any(delta[dust.mask == 0])
                max_luma_delta = max(max_luma_delta, int(delta.max()))
                visible_counts.append(int((delta >= 4).sum()))
        assert not frame_bytes(source) and not frame_bytes(result)
        assert source.wait() == result.wait() == 0
    assert max_luma_delta >= 8 and max(visible_counts) > 400
    step = 1 / FPS
    local_steps = [float(np.abs(dust.opacity(t + step) - dust.opacity(t)).mean())
                   for t in (-3 * step, -2 * step, -step, 0, step, 2 * step)]
    assert local_steps[2] <= max(local_steps[:2] + local_steps[3:]) * 1.1 + 1e-6
    # Verify encoded frame timestamps as well as full pixel identity.
    hashes = subprocess.check_output([FF, "-v", "error", "-i", str(rendered), "-map", "0",
                                      "-c", "copy", "-f", "framehash", "pipe:1"], text=True)
    rows = [re.split(r"\s*,\s*", line.strip()) for line in hashes.splitlines() if line and not line.startswith("#")]
    assert len(rows) == FRAMES and all(row[0] == "0" for row in rows)
    pts = [int(row[2]) for row in rows]
    stride = pts[1] - pts[0]
    assert stride > 0 and pts == list(range(0, FRAMES * stride, stride))
    return {"frames": FRAMES, "seconds": SECONDS, "fps": FPS, "dimensions": [WIDTH, HEIGHT], "audio": False,
            "all_decoded_frames_match_expected_overlay": True, "sequential_video_timestamps": True,
            "unchanged_outside_overlay": True, "terrain_mask_protection_checked": True,
            "periodic_opacity": True, "dust_join_step_mean_opacity": local_steps[2],
            "max_luma_code_change": max_luma_delta, "max_sampled_pixels_changed_by_four_codes": max(visible_counts)}


if __name__ == "__main__":
    dust = Dust()
    partial = render(dust)
    print("Encoded. Verifying every decoded frame and the loop boundary.", flush=True)
    report = validate(dust, partial)
    partial.rename(OUTPUT)
    report.update({"source_sha256": BASE_SHA256, "sha256": sha(OUTPUT), "bytes": OUTPUT.stat().st_size,
                   "user_review": "pending"})
    (HERE / "delivery-v3.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
