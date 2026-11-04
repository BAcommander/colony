"""Render and verify the Crater Rim clouds and basin haze motion audition."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import cv2
import imageio_ffmpeg
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TRANSPORT = ROOT / "music/saltline-animation-v1/dust_transport.py"
sys.path.insert(0, str(TRANSPORT.parent))
from dust_transport import DustTransport

PLAN_PATH = HERE / "scene-plan.json"
PLAN = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
FPS = PLAN["fps"]
SECONDS = PLAN["preview_seconds"]
SIZE = tuple(PLAN["preview_dimensions"])
OUTPUTS = {"combined": "Crater-Rim-Survey-clouds-and-haze-v1-8s.mp4",
           "clouds": "Crater-Rim-Survey-clouds-isolated-v1-8s.mp4",
           "haze": "Crater-Rim-Survey-haze-isolated-v1-8s.mp4"}


def sha(path):
    with path.open("rb") as data:
        return hashlib.file_digest(data, "sha256").hexdigest()


def smooth(value):
    fraction = np.clip(value, 0, 1)
    return fraction*fraction*(3-2*fraction)


def shape(polygons, roi):
    left, top, right, bottom = roi
    mask = np.zeros((bottom-top, right-left), np.uint8)
    for polygon in polygons:
        points = np.asarray(polygon, np.int32) - (left, top)
        cv2.fillPoly(mask, [points.astype(np.int32)], 1)
    return mask


def distance(mask):
    padded = np.pad(mask, 1)
    return cv2.distanceTransform(padded, cv2.DIST_L2, 5)[1:-1, 1:-1]


def horizontal_clearance(mask):
    # The warp samples the same source row, so use the local run in that row.
    # Safe cloud runs are split at the edges of glass, rings and mountains.
    x = np.arange(mask.shape[1], dtype=np.int32)[None, :]
    left = np.maximum.accumulate(np.where(mask, -1, x), axis=1)
    right = np.minimum.accumulate(np.where(mask, mask.shape[1], x)[:, ::-1], axis=1)[:, ::-1]
    return np.minimum(x-left, right-x).astype(np.float32)


def region(roi):
    left, top, right, bottom = roi
    return np.s_[top:bottom, left:right]


class Scene:
    def __init__(self, source):
        self.source = source
        self.sky_region = region(PLAN["sky_roi"])
        self.sky_pixels = source[self.sky_region]
        self.sky_safe = shape(PLAN["cloud_safe_polygons"], PLAN["sky_roi"])
        self.sky_alpha = smooth((distance(self.sky_safe)-2)/8)
        self.clearance = smooth(horizontal_clearance(self.sky_safe)/PLAN["cloud_edge_taper_px"])
        self.sky_y, self.sky_x = np.indices(self.sky_safe.shape, dtype=np.float32)
        self.basin_region = region(PLAN["haze_roi"])
        basin = shape([PLAN["basin_polygon"]], PLAN["haze_roi"])
        glass = shape(PLAN["window_apertures"], PLAN["haze_roi"])
        self.basin_alpha = smooth((distance(basin)-2)/12)*smooth((distance(glass)-3)/6)
        left, top, right, bottom = PLAN["haze_roi"]
        y, x = np.mgrid[top:bottom, left:right].astype(np.float32)
        self.haze_layers = [DustTransport(x, y, layer, SECONDS) for layer in PLAN["haze_layers"]]

    def cloud_map(self, seconds):
        return self.sky_x - self.clearance*(PLAN["cloud_speed_px_per_second"]*seconds)

    def check_cloud_map(self, seconds):
        sample_x = self.cloud_map(seconds)
        rows = self.sky_y[self.sky_alpha > 0].astype(np.int32)
        x = sample_x[self.sky_alpha > 0]
        left = np.floor(x).astype(np.int32)
        right = np.ceil(x).astype(np.int32)
        assert np.all(left >= 0) and np.all(right < self.sky_safe.shape[1])
        assert np.all(self.sky_safe[rows, left]) and np.all(self.sky_safe[rows, right])
        minimum_slope = float(np.diff(sample_x, axis=1).min())
        assert minimum_slope > .25, minimum_slope
        return minimum_slope

    def clouds(self, frame, seconds):
        moving = cv2.remap(self.sky_pixels, self.cloud_map(seconds), self.sky_y, cv2.INTER_LINEAR)
        pixels = frame[self.sky_region]
        pixels[:] = np.rint(pixels+(moving.astype(np.float32)-pixels)*self.sky_alpha[..., None]).astype(np.uint8)

    def haze(self, frame, seconds):
        pixels = frame[self.basin_region].astype(np.float32)
        for effect in self.haze_layers:
            alpha, colour = effect.density(seconds, prototype=True)
            opacity = alpha*self.basin_alpha
            pixels += (colour-pixels)*opacity[..., None]
        frame[self.basin_region] = np.rint(pixels).astype(np.uint8)

    def protection(self, mode):
        allowed = np.zeros(self.source.shape[:2], dtype=bool)
        if mode != "haze":
            allowed[self.sky_region] |= self.sky_alpha > 0
        if mode != "clouds":
            allowed[self.basin_region] |= self.basin_alpha > 0
        return ~allowed


def encode(scene, mode, target):
    width, height = SIZE
    partial = target.with_suffix(".partial.mp4")
    if target.exists() or partial.exists():
        raise FileExistsError(f"Choose a fresh output directory for {target.name}")
    command = [FFMPEG, "-v", "error", "-n", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{width}x{height}",
               "-r", str(FPS), "-i", "pipe:0", "-an", "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
               "-c:v", "libx264", "-preset", "veryfast", "-threads", "4", "-crf", "17", "-colorspace", "bt709",
               "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv", "-movflags", "+faststart", str(partial)]
    protected = scene.protection(mode)
    baseline = scene.source[protected]
    with subprocess.Popen(command, stdin=subprocess.PIPE) as writer:
        try:
            for index in range(SECONDS*FPS):
                seconds = index/FPS
                frame = scene.source.copy()
                if mode != "haze":
                    scene.clouds(frame, seconds)
                if mode != "clouds":
                    scene.haze(frame, seconds)
                assert np.array_equal(frame[protected], baseline), (mode, index)
                writer.stdin.write(cv2.resize(frame, SIZE, interpolation=cv2.INTER_AREA).tobytes())
        finally:
            writer.stdin.close()
        assert writer.wait() == 0
    report = verify(partial)
    partial.rename(target)
    return {"path": target.name, "bytes": target.stat().st_size, "sha256": sha(target),
            "protected_pixels_exact_before_resize_and_encode": True, **report}


def verify(path):
    framehash = subprocess.check_output([FFMPEG, "-v", "error", "-i", str(path), "-map", "0", "-f", "framehash", "pipe:1"], text=True)
    assert "#dimensions 0: 1280x720" in framehash
    assert "#tb 0: 1/30" in framehash
    assert "#media_type 0: video" in framehash and "audio" not in framehash
    rows = [line.split(",") for line in framehash.splitlines() if line and not line.startswith("#")]
    assert all(row[0].strip() == "0" for row in rows)
    assert [int(row[2]) for row in rows] == list(range(SECONDS*FPS))
    assert len(set(row[-1] for row in rows)) > SECONDS*FPS*.90
    return {"decoded_frames": len(rows), "sequential_timestamps": True, "audio": False}


def main():
    cv2.setNumThreads(1)
    source_path = ROOT / PLAN["source"]
    assert sha(source_path) == PLAN["source_sha256"]
    with Image.open(source_path) as image:
        assert image.size == tuple(PLAN["source_dimensions"])
        scene = Scene(np.asarray(image.convert("RGB")))
    slope = min(scene.check_cloud_map(t/FPS) for t in range(SECONDS*FPS))
    clips = {}
    for mode, filename in OUTPUTS.items():
        clips[mode] = encode(scene, mode, HERE / filename)
        print(f"Verified {filename}", flush=True)
    report = {"source_sha256": PLAN["source_sha256"], "settings_sha256": sha(PLAN_PATH),
              "renderer_sha256": sha(Path(__file__)), "transport_dependency_sha256": sha(TRANSPORT),
              "minimum_horizontal_cloud_map_slope": slope, "all_active_cloud_source_taps_inside_safe_sky": True,
              "preview_seconds": SECONDS, "fps": FPS, "dimensions": SIZE, "loop": False,
              "clips": clips, "user_review": "pending"}
    (HERE / "delivery.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
