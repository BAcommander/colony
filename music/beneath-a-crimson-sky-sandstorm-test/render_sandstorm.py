"""Composite one rolling sandstorm over the unchanged Crimson Sky V3 minute."""
import json
from pathlib import Path
import subprocess
import sys

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "beneath-a-crimson-sky-animation-v3"))
from render_dust_pass import FF, FPS, FRAMES, HEIGHT, WIDTH, decode, frame_bytes, sha, smooth

BASE = HERE.parent / "beneath-a-crimson-sky-animation-v3/beneath-a-crimson-sky-v3-dry-gusts-60s.mp4"
SOURCE_HASH = "599fdae025943ae836b5d6e60678207eb6c8b96f1aef41f7360667fcf0daa7e1"
OUTPUT = HERE / "beneath-a-crimson-sky-sandstorm-test-60s.mp4"
LEFT, TOP, RIGHT, BOTTOM = 584, 352, 1280, 578
REGION = (slice(TOP, BOTTOM), slice(LEFT, RIGHT))
PARAPET_X = (584, 640, 730, 810, 920, 1005, 1070, 1100, 1175, 1212, 1280)
PARAPET_Y = (504, 511, 522, 531, 543, 548, 553, 545, 547, 554, 575)
CLOSE_ROCKS = (
    ((1018, 517), (1055, 509), (1085, 512), (1106, 509), (1143, 525), (1176, 534), (1160, 542), (1020, 540)),
    ((1182, 506), (1205, 496), (1224, 484), (1251, 482), (1279, 491), (1279, 528), (1243, 526), (1210, 517)),
)
FAR_RUIN = ((926, 476), (950, 466), (959, 457), (977, 454), (982, 467), (996, 468), (1006, 484), (968, 490))


class Storm:
    def __init__(self):
        self.y, self.x = np.mgrid[TOP:BOTTOM, LEFT:RIGHT].astype(np.float32)
        parapet = np.interp(self.x, PARAPET_X, PARAPET_Y)
        cliff = np.interp(self.y, (352, 390, 420, 460, 505), (600, 610, 629, 651, 674))
        shelter = smooth((parapet - 5 - self.y) / 10)
        shelter *= smooth((self.x - cliff - 3) / 25)
        shelter *= smooth((self.y - 375) / 29)
        shelter *= self.around(CLOSE_ROCKS, 3, 7)
        self.mask = shelter.astype(np.float32)
        self.near_mask = self.mask * self.around((FAR_RUIN,), 1, 9)

        rng = np.random.default_rng(4040)
        self.fields = [rng.random((160, 256), dtype=np.float32) for _ in range(3)]
        self.grains = np.column_stack((rng.uniform(650, 1390, 300), rng.uniform(425, 568, 300),
                                      rng.uniform(0, 1, 300), rng.uniform(0.4, 1, 300)))

    def around(self, outlines, buffer, feather):
        silhouette = np.zeros(self.x.shape, dtype=np.uint8)
        points = [np.asarray(outline, dtype=np.int32) - (LEFT, TOP) for outline in outlines]
        cv2.fillPoly(silhouette, [p.astype(np.int32) for p in points], 1)
        return smooth((cv2.distanceTransform(1 - silhouette, cv2.DIST_L2, 5) - buffer) / feather)

    def texture(self, u, v):
        texture = np.zeros_like(self.x)
        for field, width, height, weight in zip(self.fields, (97, 39, 15), (24, 13, 5), (0.57, 0.30, 0.13)):
            texture += weight * cv2.remap(field, u / width + 91, v / height + 67, cv2.INTER_CUBIC,
                                          borderMode=cv2.BORDER_WRAP)
        return np.clip(texture, 0, 1)

    def layers(self, time):
        time %= 60
        if time <= 12 or time >= 51:
            return None
        age = time - 12
        envelope = float(smooth(age / 11) * smooth((51 - time) / 14))
        # The slower bank rises over the plain and keeps an uneven, advancing head.
        u = self.x - (592 + 19.2 * age)
        bank = 430 + 0.035 * (self.x - 780) + 5.5 * np.sin(u / 67) + 3.5 * np.sin(u / 25)
        v = self.y - bank
        eddies = self.texture(u - 2.1 * age, v + 3 * np.sin(u / 34))
        head = u + 20 * (eddies - 0.5) + 0.68 * (v + 10)
        profile = np.exp(-0.5 * ((u + 126) / 254) ** 2) * smooth((78 - head) / 129)
        profile *= np.exp(-0.5 * (v / 36) ** 2)
        veil = self.mask * envelope * 0.64 * profile * smooth((eddies + 0.15) / 0.86)

        # Two shallow streamers travel faster in front of the bank, under the parapet.
        skim = np.zeros_like(self.mask)
        for phase, gain in ((0, 1.0), (7.8, 0.67)):
            p = age - phase
            if p <= 0:
                continue
            near_u = self.x - (615 + 30.5 * p)
            near_v = self.y - (467 + 0.080 * (self.x - 690) + 6 * np.sin(near_u / 52 + phase))
            texture = self.texture(near_u + 79, near_v + 13)
            trail = np.exp(-0.5 * (((near_u + 56) / 151) ** 2 + (near_v / 17) ** 2))
            skim += gain * trail * smooth((texture - 0.18) / 0.65)
        skim *= self.near_mask * envelope * 0.40

        # A handful of small, soft traces become visible in the thicker part of the gust.
        grit = np.zeros(self.mask.shape, dtype=np.uint8)
        for x0, y0, variant, weight in self.grains:
            x = 632 + (x0 - 632 + age * (63 + variant * 38)) % 765
            y = y0 + 3.5 * np.sin(x / 72 + variant * 10) + 0.057 * (x - 900)
            ix, iy = int(x) - LEFT, int(y) - TOP
            if 5 <= ix < grit.shape[1] and 1 <= iy < grit.shape[0]:
                density = max(float(skim[iy, ix]), float(veil[iy, ix]) * 0.50)
                opacity = int(255 * density * weight * 0.80)
                if opacity >= 3:
                    cv2.line(grit, (ix - 1 - int(variant * 3), iy - int(variant > .7)),
                             (ix, iy), opacity, 1, cv2.LINE_AA)
        grit = grit.astype(np.float32) * (self.near_mask / 255)
        return (veil, skim, grit)


def blend(frame, layers):
    if layers is None:
        return frame
    flat = np.frombuffer(frame, dtype=np.uint8).copy()
    y_end = WIDTH * HEIGHT
    u_end = y_end + y_end // 4
    region_uv = (slice(TOP//2, BOTTOM//2), slice(LEFT//2, RIGHT//2))
    planes = (flat[:y_end].reshape(HEIGHT, WIDTH)[REGION],
              flat[y_end:u_end].reshape(HEIGHT//2, WIDTH//2)[region_uv],
              flat[u_end:].reshape(HEIGHT//2, WIDTH//2)[region_uv])
    for channel, plane in enumerate(planes):
        result = plane.astype(np.float32)
        for alpha, colour in zip(layers, ((116, 116, 146), (133, 112, 151), (161, 109, 152))):
            if channel:
                alpha = alpha.reshape(alpha.shape[0]//2, 2, alpha.shape[1]//2, 2).mean(axis=(1, 3))
            result += (colour[channel] - result) * alpha
        plane[:] = np.rint(result).astype(np.uint8)
    return flat.tobytes()


def main():
    cv2.setNumThreads(1)
    assert sha(BASE) == SOURCE_HASH and not OUTPUT.exists()
    storm = Storm()
    partial = OUTPUT.with_suffix(".partial.mp4")
    command = [FF, "-v", "error", "-n", "-f", "rawvideo", "-pix_fmt", "yuv420p", "-s", f"{WIDTH}x{HEIGHT}",
               "-r", str(FPS), "-colorspace", "bt709", "-color_range", "tv", "-i", "pipe:0", "-an", "-c:v",
               "libx264", "-preset", "ultrafast", "-qp", "0", "-pix_fmt", "yuv420p", "-colorspace", "bt709",
               "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv", "-movflags", "+faststart", str(partial)]
    with decode(BASE) as source, subprocess.Popen(command, stdin=subprocess.PIPE) as writer:
        for index in range(FRAMES):
            frame = frame_bytes(source)
            assert len(frame) == WIDTH * HEIGHT * 3 // 2
            writer.stdin.write(blend(frame, storm.layers(index / FPS)))
        assert not frame_bytes(source) and source.wait() == 0
        writer.stdin.close()
        assert writer.wait() == 0
    print("Encoded; checking all decoded frames and timestamps.", flush=True)

    changed = []
    clear_frames = 0
    with decode(BASE) as source, decode(partial) as actual:
        for index in range(FRAMES):
            before, after = frame_bytes(source), frame_bytes(actual)
            assert len(before) == len(after) == WIDTH * HEIGHT * 3 // 2
            layers = storm.layers(index / FPS)
            assert after == blend(before, layers), index
            if layers is None:
                assert before == after
                clear_frames += 1
            elif index % FPS == 0:
                def luma(frame):
                    return np.frombuffer(frame, dtype=np.uint8, count=WIDTH*HEIGHT).reshape(HEIGHT, WIDTH)[REGION].astype(np.int16)
                delta = np.abs(luma(before) - luma(after))
                assert not np.any(delta[storm.mask == 0])
                changed.append(int(np.count_nonzero(delta >= 4)))
        assert not frame_bytes(source) and not frame_bytes(actual) and source.wait() == actual.wait() == 0
    assert max(changed) > 15000 and clear_frames >= 600
    rows = subprocess.check_output([FF, "-v", "error", "-i", str(partial), "-map", "0", "-c", "copy", "-f", "framehash", "pipe:1"], text=True)
    packets = [[field.strip() for field in row.split(",")] for row in rows.splitlines() if row and not row.startswith("#")]
    assert len(packets) == FRAMES and all(row[0] == "0" for row in packets)
    pts = [int(row[2]) for row in packets]
    assert pts == list(range(0, FRAMES * (pts[1] - pts[0]), pts[1] - pts[0]))
    partial.rename(OUTPUT)
    report = {"source_sha256": SOURCE_HASH, "sha256": sha(OUTPUT), "bytes": OUTPUT.stat().st_size,
              "frames": FRAMES, "dimensions": [WIDTH, HEIGHT], "fps": FPS, "audio": False,
              "all_decoded_frames_match_composite": True, "sequential_video_timestamps": True,
              "shelter_mask_luma_protection_checked": True, "clear_source_frames_including_loop_boundary": clear_frames,
              "max_sampled_pixels_changed_by_four_luma_codes": max(changed), "user_review": "pending"}
    (HERE / "delivery.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
