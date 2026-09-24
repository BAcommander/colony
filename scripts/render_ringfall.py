"""Render Ringfall's ten-second loop locally; no network or paid services.

Requires locally installed numpy, Pillow, OpenCV and imageio-ffmpeg.
Draft: python scripts/render_ringfall.py --stage preview --version v5-check
Final: python scripts/render_ringfall.py --stage final --version v5-approved
This renderer implements the v5 effects, not the planned v6 layers.
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
SIZE = (3840, 2160)
STEM = "ringfall-loop-v5-4k"
TAU = 2 * np.pi


class Ringfall:
    def __init__(self):
        self.base = np.array(Image.open(SOURCE).convert("RGB"))
        assert self.base.shape[:2] == (941, 1672), "Effect positions require this source size"
        self.active = np.zeros(self.base.shape[:2], dtype=bool)
        # Source-image pixel coordinates. These tight patches isolate the effects.
        self.steam_box = (202, 369, 302, 516)
        self.screen_box = (0, 445, 143, 609)
        self.beacon_box = (1431, 360, 1459, 388)
        for x0, y0, x1, y1 in [self.steam_box, self.screen_box, self.beacon_box]:
            self.active[y0:y1, x0:x1] = True

    @staticmethod
    def phase(t):
        return TAU * (float(t) % DURATION) / DURATION

    def steam(self, phase):
        x0, y0, x1, y1 = self.steam_box
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        height = (515 - yy) / 143.0
        h = np.clip(height, 0, 1)
        # Smooth vanishing opacity at the rim and top avoids discontinuities.
        envelope = np.power(np.maximum(0, np.sin(np.pi * h)), 1.35)
        envelope *= (height > 0) & (height < 1)
        alpha = np.zeros_like(h)
        for i in range(3):
            flow = TAU * (1.3 * h) - 2 * phase + i * 2.1
            centre = 250 + (1.4 + 14 * h) * np.sin(flow)
            centre += 5.0 * h * np.sin(TAU * 2.3 * h - 3 * phase + i)
            centre += (i - 1) * (1.2 + 3.8 * h)
            width = 1.15 + 4.0 * h + 0.9 * np.sin(flow + 1) ** 2
            ribbon = np.exp(-0.5 * ((xx - centre) / width) ** 2)
            density = 0.65 + 0.35 * np.sin(TAU * 2.4 * h - 3 * phase + i * 1.7)
            alpha += 0.19 * ribbon * density * envelope
        alpha = cv2.GaussianBlur(alpha, (0, 0), 0.85)
        alpha[:, :2] = 0
        alpha[:, -2:] = 0
        return np.clip(alpha, 0, 0.34)

    def frame(self, t, output_size=True):
        phase = self.phase(t)
        frame = self.base.copy()

        x0, y0, x1, y1 = self.steam_box
        alpha = self.steam(phase)[..., None]
        patch = frame[y0:y1, x0:x1].astype(np.float32)
        vapor = np.array([227, 220, 206], dtype=np.float32)
        frame[y0:y1, x0:x1] = np.rint(patch * (1 - alpha) + vapor * alpha).astype(np.uint8)

        # A perspective-clipped scan traverses the actual screen twice per loop.
        # It fades at the edges so its reset is invisible and never touches bezel.
        x0, y0, x1, y1 = self.screen_box
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        screen_mask = np.zeros((y1 - y0, x1 - x0), dtype=np.uint8)
        polygon = np.array([[0, 12], [101, 4], [132, 133], [0, 157]], dtype=np.int32)
        cv2.fillConvexPoly(screen_mask, polygon, 255)
        screen_mask = cv2.GaussianBlur(screen_mask.astype(np.float32) / 255, (0, 0), 0.7)
        v = (yy - (457 - 0.078 * xx)) / (144 - 0.17 * xx)
        scan_phase = (2 * phase / TAU) % 1.0
        distance = v - scan_phase
        edge = np.maximum(0, np.sin(np.pi * np.clip(v, 0, 1))) ** 1.5
        scan = (0.36 * np.exp(-0.5 * (distance / 0.0055) ** 2)
                + 0.065 * np.exp(-0.5 * (distance / 0.029) ** 2))
        scan *= edge * screen_mask
        patch = frame[y0:y1, x0:x1].astype(np.float32)
        scan_color = np.array([169, 209, 204], dtype=np.float32)
        patch = patch * (1 - scan[..., None]) + scan_color * scan[..., None]
        u = (xx - 97) / 26.0
        fade = np.sin(np.pi * np.clip(u, 0, 1)) ** 2
        baseline = 547 - 0.15 * (xx - 97)
        trace_y = baseline + 2.0 * np.sin(TAU * 1.5 * u - 2 * phase)
        trace_y += 0.8 * np.sin(TAU * 3 * u - 4 * phase)
        alpha = 0.65 * np.exp(-0.5 * ((yy - trace_y) / 0.6) ** 2) * fade
        alpha *= (u > 0) & (u < 1)
        amber = np.array([201, 166, 109], dtype=np.float32)
        frame[y0:y1, x0:x1] = np.rint(patch * (1 - alpha[..., None]) + amber * alpha[..., None]).astype(np.uint8)

        # A warm breathing beacon at an existing mast lamp, without scene relighting.
        x0, y0, x1, y1 = self.beacon_box
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        radius2 = (xx - 1444.8) ** 2 + (yy - 373.6) ** 2
        mask = np.exp(-0.5 * radius2 / 2.0 ** 2)
        halo = np.exp(-0.5 * radius2 / 4.0 ** 2)
        amount = 0.5 + 0.5 * np.sin(2 * phase - 0.5)
        patch = frame[y0:y1, x0:x1].astype(np.float32)
        patch *= 1 + (amount - 0.5) * 0.9 * mask[..., None]
        patch += (0.12 + 0.88 * amount) * (mask + 0.16 * halo)[..., None] * np.array([115, 75, 33])
        frame[y0:y1, x0:x1] = np.rint(np.clip(patch, 0, 255)).astype(np.uint8)

        if output_size:
            return cv2.resize(frame, SIZE, interpolation=cv2.INTER_LANCZOS4)
        return frame


def make_qa(anim):
    times = [0, 2, 4, 6, 8]
    rows = [((200, 365, 305, 535), "Mug steam"),
            ((0, 440, 145, 611), "Laptop scan"),
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
               "-metadata", f"title=Ambient Colony - Ringfall Observatory - {STEM}",
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
        "resolution_note": f"{width}x{height} export resampled from 1672x941 source; no claim of native 4K image detail",
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
        "effects": getattr(anim, "effect_descriptions", {"steam": "Taller, broader visible curling vapor; 5x ribbon opacity vs v4",
                    "laptop": "Perspective-clipped scan plus stronger telemetry, two cycles per loop",
                    "background": "Clearly visible smooth amber mast beacon, two cycles per loop"})
    }
    assert encoded_seam <= max(changes) * 1.5 + 0.02, "Encoded seam is an outlier"
    (OUTPUT / f"{STEM}-validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2), flush=True)


def main():
    global SIZE, STEM
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=["preview", "final"], default="preview",
                        help="Preview renders at 720p; final renders at 4K. Both use the same effects and timing.")
    parser.add_argument("--version", default="v5",
                        help="Descriptive output version. This remains the v5 effect implementation.")
    parser.add_argument("--qa-only", "--preview-only", dest="qa_only", action="store_true",
                        help="Generate temporal detail sheet and poster only, without a video.")
    parser.add_argument("--validate-only", type=Path,
                        help="Validate an existing export without rendering it; match its --stage.")
    args = parser.parse_args()
    if not args.version or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for c in args.version):
        parser.error("Use only letters, digits, hyphens and underscores in --version")
    SIZE = (1280, 720) if args.stage == "preview" else (3840, 2160)
    STEM = f"ringfall-{args.version}-{args.stage}"
    OUTPUT.mkdir(parents=True, exist_ok=True)
    anim = Ringfall()
    if args.validate_only:
        validate(anim, args.validate_only.resolve())
        return
    destination = OUTPUT / f"{STEM}.mp4"
    if not args.qa_only and destination.exists():
        raise FileExistsError(f"Preserve existing render: {destination}; use a new --version")
    make_qa(anim)
    if not args.qa_only:
        render(anim, destination)
        validate(anim, destination)


if __name__ == "__main__":
    main()
