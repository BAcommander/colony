"""Render Ringfall's ten-second loop locally; no network or paid services.

Requires locally installed numpy, Pillow, OpenCV and imageio-ffmpeg.
Run: python scripts/render_ringfall.py
All effects are periodic at ten seconds; the source plate is never overwritten.
"""

from pathlib import Path
import argparse
import hashlib
import json
import subprocess

import cv2
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "creative/ringfall/04-laptop-refined.png"
OUTPUT = ROOT / "creative/ringfall/animation"
DURATION = 10
FPS = 30
SIZE = (1920, 1080)
STEM = "ringfall-loop-v4"
TAU = 2 * np.pi


class Ringfall:
    def __init__(self):
        self.base = np.array(Image.open(SOURCE).convert("RGB"))
        assert self.base.shape[:2] == (941, 1672), "Effect positions require this source size"
        self.active = np.zeros(self.base.shape[:2], dtype=bool)
        # Source-image pixel coordinates. These tight patches isolate the effects.
        self.steam_box = (216, 420, 287, 516)
        self.screen_box = (92, 533, 131, 553)
        self.beacon_box = (1438, 367, 1452, 381)
        for x0, y0, x1, y1 in [self.steam_box, self.screen_box, self.beacon_box]:
            self.active[y0:y1, x0:x1] = True

    @staticmethod
    def phase(t):
        return TAU * (float(t) % DURATION) / DURATION

    def steam(self, phase):
        x0, y0, x1, y1 = self.steam_box
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        height = (515 - yy) / 91.0
        h = np.clip(height, 0, 1)
        # Smooth vanishing opacity at the rim and top avoids discontinuities.
        envelope = np.power(np.maximum(0, np.sin(np.pi * h)), 1.35)
        envelope *= (height > 0) & (height < 1)
        alpha = np.zeros_like(h)
        for i in range(3):
            flow = TAU * (1.65 * h) - phase + i * 2.1
            centre = 250 + (1.5 + 5.5 * h) * np.sin(flow)
            centre += 2.3 * h * np.sin(TAU * 3.1 * h - 2 * phase + i)
            centre += (i - 1) * (1.2 + 2.8 * h)
            width = 0.75 + 2.5 * h + 0.6 * np.sin(flow + 1) ** 2
            ribbon = np.exp(-0.5 * ((xx - centre) / width) ** 2)
            density = 0.6 + 0.4 * np.sin(TAU * 2.4 * h - 2 * phase + i * 1.7)
            alpha += 0.038 * ribbon * density * envelope
        alpha = cv2.GaussianBlur(alpha, (0, 0), 0.7)
        alpha[:, :2] = 0
        alpha[:, -2:] = 0
        return np.clip(alpha, 0, 0.09)

    def frame(self, t, output_size=True):
        phase = self.phase(t)
        frame = self.base.copy()

        x0, y0, x1, y1 = self.steam_box
        alpha = self.steam(phase)[..., None]
        patch = frame[y0:y1, x0:x1].astype(np.float32)
        vapor = np.array([227, 220, 206], dtype=np.float32)
        frame[y0:y1, x0:x1] = np.rint(patch * (1 - alpha) + vapor * alpha).astype(np.uint8)

        # A small soft amber telemetry waveform fitted to the existing display.
        # It runs continuously in one direction; phase is periodic, not ping-pong.
        x0, y0, x1, y1 = self.screen_box
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        u = (xx - 97) / 26.0
        fade = np.sin(np.pi * np.clip(u, 0, 1)) ** 2
        baseline = 547 - 0.15 * (xx - 97)
        trace_y = baseline + 1.0 * np.sin(TAU * 1.5 * u - phase)
        trace_y += 0.55 * np.sin(TAU * 3 * u - 2 * phase)
        alpha = 0.33 * np.exp(-0.5 * ((yy - trace_y) / 0.48) ** 2) * fade
        alpha *= (u > 0) & (u < 1)
        patch = frame[y0:y1, x0:x1].astype(np.float32)
        amber = np.array([165, 140, 95], dtype=np.float32)
        frame[y0:y1, x0:x1] = np.rint(patch * (1 - alpha[..., None]) + amber * alpha[..., None]).astype(np.uint8)

        # Modulate only an existing tiny mast lamp, with no new halo or spill.
        x0, y0, x1, y1 = self.beacon_box
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        mask = np.exp(-0.5 * (((xx - 1444.8) / 1.6) ** 2 + ((yy - 373.6) / 1.6) ** 2))
        amount = 0.21 * np.sin(phase - 0.5)
        patch = frame[y0:y1, x0:x1].astype(np.float32)
        patch *= 1 + amount * mask[..., None]
        frame[y0:y1, x0:x1] = np.rint(np.clip(patch, 0, 255)).astype(np.uint8)

        if output_size:
            return cv2.resize(frame, SIZE, interpolation=cv2.INTER_LANCZOS4)
        return frame


def make_qa(anim):
    times = [0, 2, 4, 6, 8]
    rows = [((207, 414, 297, 535), "Mug steam"),
            ((75, 518, 145, 561), "Laptop telemetry"),
            ((1424, 353, 1467, 398), "Distant mast light")]
    tile_w, tile_h = 260, 260
    sheet = Image.new("RGB", (tile_w * len(times), tile_h * len(rows)), (19, 23, 29))
    draw = ImageDraw.Draw(sheet)
    for row, (box, label) in enumerate(rows):
        for col, t in enumerate(times):
            crop = Image.fromarray(anim.frame(t, False)).crop(box)
            crop.thumbnail((240, 220), Image.Resampling.LANCZOS)
            # Enlarge small crops intentionally for QA inspection.
            scale = min(240 / crop.width, 220 / crop.height)
            crop = crop.resize((round(crop.width * scale), round(crop.height * scale)), Image.Resampling.LANCZOS)
            px = col * tile_w + (tile_w - crop.width) // 2
            py = row * tile_h + 25
            sheet.paste(crop, (px, py))
            draw.text((col * tile_w + 12, row * tile_h + 7), f"{label} | {t}s", fill="white")
    sheet.save(OUTPUT / f"{STEM}-detail-check.png")
    Image.fromarray(anim.frame(2)).save(OUTPUT / f"{STEM}-poster.png")


def render(anim, destination):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
               "-f", "rawvideo", "-vcodec", "rawvideo", "-pix_fmt", "rgb24",
               "-s", f"{SIZE[0]}x{SIZE[1]}", "-r", str(FPS), "-i", "-",
               "-an", "-c:v", "libx264", "-preset", "slow", "-qp", "0",
               "-x264-params", "aq-mode=0:mbtree=0:psy=0",
               "-pix_fmt", "yuv420p", "-color_primaries", "bt709",
               "-color_trc", "bt709", "-colorspace", "bt709",
               "-vf", "scale=in_range=full:out_range=tv:out_color_matrix=bt709",
               "-movflags", "+faststart", "-g", "300", "-bf", "0",
               "-metadata", "title=Ambient Colony - Ringfall Observatory - Local Loop v4",
               str(destination)]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    try:
        for index in range(DURATION * FPS):
            process.stdin.write(anim.frame(index / FPS).tobytes())
            if index % 60 == 0:
                print(f"Rendered {index}/{DURATION * FPS} frames", flush=True)
    finally:
        process.stdin.close()
    if process.wait() != 0:
        raise RuntimeError("FFmpeg render failed")


def validate(anim, destination):
    a = anim.frame(0, False)
    b = anim.frame(10, False)
    outside = ~anim.active
    assert np.array_equal(a, b), "Analytic loop endpoint mismatch"
    for t in [0, 1.37, 4.2, 8.8, 10]:
        assert np.array_equal(anim.frame(t, False)[outside], anim.base[outside]), "Static plate changed"
    # Measure differences on active pixels, not diluted by the static image.
    def diff(x, y):
        return float(np.abs(x.astype(np.float32) - y.astype(np.float32)).mean())
    analytic_changes = []
    previous = anim.frame(0, False)[anim.active]
    for i in range(1, FPS * DURATION):
        current = anim.frame(i / FPS, False)[anim.active]
        analytic_changes.append(diff(current, previous))
        previous = current
    seam = diff(previous, a[anim.active])
    assert seam <= max(analytic_changes) * 1.25 + 0.001, "Unexpected analytic seam jump"

    capture = cv2.VideoCapture(str(destination))
    fps = capture.get(cv2.CAP_PROP_FPS)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    active = cv2.resize(anim.active.astype(np.uint8), SIZE, interpolation=cv2.INTER_NEAREST).astype(bool)
    active = cv2.dilate(active.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
    first = last = None
    changes = []
    count = 0
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        current = frame[active]
        if first is None:
            first = current.copy()
        if last is not None:
            changes.append(diff(current, last))
        last = current
        count += 1
    capture.release()
    assert count == FPS * DURATION and fps == FPS and (width, height) == SIZE
    encoded_seam = diff(last, first)
    report = {
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "output": str(destination.relative_to(ROOT)),
        "method": "Local Python/OpenCV compositing, FFmpeg H.264; no network or paid service",
        "source_dimensions": [1672, 941],
        "output_dimensions": [width, height],
        "resolution_note": "Source gently resampled to 1920x1080; not native 4K",
        "fps": fps, "frames": count, "duration_seconds": count / fps,
        "audio": False,
        "periodic_endpoint_pixels_identical": bool(np.array_equal(a, b)),
        "uncompressed_static_plate_unchanged": True,
        "analytic_active_pixel_mean_abs_step": float(np.mean(analytic_changes)),
        "analytic_active_pixel_max_mean_abs_step": float(max(analytic_changes)),
        "analytic_active_pixel_seam_mean_abs_step": seam,
        "encoded_active_pixel_mean_abs_step": float(np.mean(changes)),
        "encoded_active_pixel_max_mean_abs_step": float(max(changes)),
        "encoded_active_pixel_seam_mean_abs_step": encoded_seam,
        "encoding": "H.264 QP0 lossless coding after RGB to YUV420 conversion; preserves tiny effects without temporal quantization drift",
        "note": "The last-to-first transition is checked numerically. Player buffering is separate from media continuity. H.264 quantization can introduce small differences.",
        "effects": {"steam": "Three soft periodically advected ribbons above mug",
                    "laptop": "Small dim amber telemetry waveform",
                    "background": "Existing mast lamp modulated by a ten-second sine"}
    }
    assert encoded_seam <= max(changes) * 1.5 + 0.02, "Encoded seam is an outlier"
    (OUTPUT / f"{STEM}-validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview-only", action="store_true")
    args = parser.parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    anim = Ringfall()
    make_qa(anim)
    if not args.preview_only:
        destination = OUTPUT / f"{STEM}.mp4"
        if destination.exists():
            raise FileExistsError(f"Preserve existing render: {destination}; use a new version filename")
        render(anim, destination)
        validate(anim, destination)


if __name__ == "__main__":
    main()
