"""Animate the original portal texture inside the traced Gate Camp aperture."""
import hashlib
import json
from pathlib import Path
import subprocess

import cv2
import imageio_ffmpeg
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SETTINGS = HERE / "scene-plan.json"
PLAN = json.loads(SETTINGS.read_text(encoding="utf-8"))
OUTPUT = HERE / "Gate-Camp-portal-v1-8s.mp4"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def sha(path):
    with path.open("rb") as data:
        return hashlib.file_digest(data, "sha256").hexdigest()


def smooth(value):
    t = np.clip(value, 0, 1)
    return t*t*(3-2*t)


class Portal:
    def __init__(self, artwork):
        self.artwork = artwork
        left, top, right, bottom = PLAN["portal_roi"]
        self.region = np.s_[top:bottom, left:right]
        self.texture = artwork[self.region]
        self.aperture = np.zeros(self.texture.shape[:2], np.uint8)
        polygon = np.asarray(PLAN["aperture"], np.int32) - (left, top)
        cv2.fillPoly(self.aperture, [polygon.astype(np.int32)], 1)
        distance = cv2.distanceTransform(self.aperture, cv2.DIST_L2, 5)
        self.active = distance > PLAN["rim_inset_px"]
        self.alpha = smooth((distance-PLAN["rim_inset_px"])/PLAN["rim_feather_px"])
        self.taper = smooth((distance-PLAN["rim_inset_px"])/PLAN["warp_taper_px"])
        self.y, self.x = np.indices(distance.shape, dtype=np.float32)
        self.waves = []
        for wave in PLAN["waves"]:
            direction = np.deg2rad(wave["direction_degrees"])
            unit_x, unit_y = np.cos(direction), np.sin(direction)
            frequency = 2*np.pi/wave["wavelength_px"]
            phase = ((self.x*unit_x+self.y*unit_y)*frequency+wave["phase_radians"]).astype(np.float32)
            self.waves.append((phase, wave["speed_px_per_second"]*frequency,
                               float(unit_x*wave["displacement_px"]), float(unit_y*wave["displacement_px"])))

    def frame(self, t):
        drift_x, drift_y = PLAN["drift_px_per_second"]
        dx = np.full_like(self.x, drift_x*t)
        dy = np.full_like(self.y, drift_y*t)
        for phase, rate, x_amplitude, y_amplitude in self.waves:
            travel = np.sin(phase-rate*t)
            dx += travel*x_amplitude
            dy += travel*y_amplitude
        map_x, map_y = self.x-dx*self.taper, self.y-dy*self.taper
        x, y = map_x[self.active], map_y[self.active]
        for sx in (np.floor(x), np.ceil(x)):
            for sy in (np.floor(y), np.ceil(y)):
                assert np.all(sx >= 0) and np.all(sx < self.aperture.shape[1])
                assert np.all(sy >= 0) and np.all(sy < self.aperture.shape[0])
                assert np.all(self.aperture[sy.astype(np.int32),sx.astype(np.int32)])
        mx_y, mx_x = np.gradient(map_x)
        my_y, my_x = np.gradient(map_y)
        determinant = float(np.min(mx_x*my_y-mx_y*my_x))
        assert determinant > .25, determinant
        moved = cv2.remap(self.texture, map_x, map_y, cv2.INTER_LINEAR)
        patch = np.rint(self.texture+(moved.astype(np.float32)-self.texture)*self.alpha[...,None]).astype(np.uint8)
        assert np.array_equal(patch[~self.active], self.texture[~self.active])
        frame = self.artwork.copy()
        frame[self.region] = patch
        return frame, determinant


def main():
    cv2.setNumThreads(1)
    source = ROOT / PLAN["source"]
    assert sha(source) == PLAN["source_sha256"]
    partial = OUTPUT.with_suffix(".partial.mp4")
    if OUTPUT.exists() or partial.exists():
        raise FileExistsError("Choose a new output path for a revised preview")
    with Image.open(source) as image:
        assert list(image.size) == PLAN["source_dimensions"]
        portal = Portal(np.asarray(image.convert("RGB")))
    width, height = PLAN["preview_dimensions"]
    fps = PLAN["fps"]
    frame_count = fps*PLAN["preview_seconds"]
    command = [FFMPEG, "-v", "error", "-n", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{width}x{height}",
               "-r", str(fps), "-i", "pipe:0", "-an", "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
               "-c:v", "libx264", "-preset", "veryfast", "-threads", "4", "-crf", "17", "-colorspace", "bt709",
               "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv", "-movflags", "+faststart", str(partial)]
    minimum_determinant = 1.0
    with subprocess.Popen(command, stdin=subprocess.PIPE) as encoder:
        try:
            for frame_index in range(frame_count):
                frame, determinant = portal.frame(frame_index/fps)
                minimum_determinant = min(minimum_determinant, determinant)
                encoder.stdin.write(cv2.resize(frame,(width,height),interpolation=cv2.INTER_AREA).tobytes())
        finally:
            encoder.stdin.close()
        assert encoder.wait() == 0
    framehash = subprocess.check_output([FFMPEG,"-v","error","-i",str(partial),"-map","0","-f","framehash","pipe:1"],text=True)
    assert f"#dimensions 0: {width}x{height}" in framehash and f"#tb 0: 1/{fps}" in framehash
    assert "#media_type 0: video" in framehash and "audio" not in framehash
    rows = [line.split(",") for line in framehash.splitlines() if line and not line.startswith("#")]
    assert all(row[0].strip() == "0" for row in rows)
    assert [int(row[2]) for row in rows] == list(range(frame_count))
    assert len({row[-1] for row in rows}) == frame_count
    partial.rename(OUTPUT)
    report = {"path": OUTPUT.name, "sha256": sha(OUTPUT), "bytes": OUTPUT.stat().st_size,
              "source_sha256": sha(source), "settings_sha256": sha(SETTINGS), "renderer_sha256": sha(Path(__file__)),
              "decoded_frames": frame_count, "dimensions": [width,height], "fps": fps, "audio": False,
              "loop": False, "sequential_timestamps": True, "minimum_warp_jacobian": minimum_determinant,
              "active_source_taps_inside_aperture": True, "outside_mask_exact_before_resize_and_encode": True,
              "user_review": "pending"}
    (HERE / "delivery.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))


if __name__ == "__main__":
    main()
