"""Build actual-video detail clips and an exact end-to-start review for scene18."""
from pathlib import Path
import argparse
import json
import subprocess

from validate_delivery import DEFAULT_MEDIA, FFMPEG, HERE, ROOT, framehash, load_scene, sha

DEFAULT_SPECS = [
    {"label": "Cabin-circuits-and-light", "start": 8, "seconds": 20, "roi": [910, 288, 1235, 620]},
    {"label": "Workbench-scope-and-lamp", "start": 20, "seconds": 18, "roi": [60, 0, 525, 390]},
    {"label": "Exterior-rain-and-reflections", "start": 32, "seconds": 18, "roi": [1230, 180, 1672, 705]},
    {"label": "Car-metal-and-practicals", "start": 72, "seconds": 18, "roi": [35, 290, 970, 685]},
]


def encode(command, target):
    assert not target.exists(), f"Preserve the current review; choose a new output: {target}"
    subprocess.run(command + [str(target)], check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--media", type=Path, default=DEFAULT_MEDIA)
    parser.add_argument("--seconds", type=int, default=120)
    parser.add_argument("--spec-json", type=Path)
    parser.add_argument("--suffix", default="")
    args = parser.parse_args()
    media = args.media.resolve()
    scene = load_scene()
    fps = scene.fps
    specs = json.loads(args.spec_json.read_text()) if args.spec_json else getattr(scene, "review_details", DEFAULT_SPECS)
    _, original_rows = framehash(media)
    assert len(original_rows) == args.seconds * fps
    source_sha = sha(media)
    encoding = ["-an", "-c:v", "libx264", "-qp", "0", "-preset", "veryfast", "-threads", "3",
                "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                "-color_range", "tv", "-movflags", "+faststart"]
    reviews = []
    native_h, native_w = scene.base.shape[:2]
    for spec in specs:
        label, start, seconds, roi = (spec[k] for k in ["label", "start", "seconds", "roi"])
        assert 0 <= start and start + seconds <= args.seconds
        a, b, c, d = roi
        assert 0 <= a < c <= native_w and 0 <= b < d <= native_h
        x = round(a * 1280 / native_w) // 2 * 2
        y = round(b * 720 / native_h) // 2 * 2
        w = round((c-a) * 1280 / native_w) // 2 * 2
        h = round((d-b) * 720 / native_h) // 2 * 2
        filters = f"crop={w}:{h}:{x}:{y},scale=iw*2:ih*2:flags=lanczos"
        target = HERE / f"Back-Before-Dawn-{label}-detail{args.suffix}.mp4"
        command = [FFMPEG, "-v", "error", "-n", "-ss", str(start), "-i", str(media),
                   "-t", str(seconds), "-vf", filters] + encoding
        encode(command, target)
        _, rows = framehash(target)
        assert len(rows) == round(seconds * fps)
        for control in [0, round(seconds * fps) // 2, round(seconds * fps) - 1]:
            _, expected = framehash(media, filters, start=start + control/fps, frames=1)
            assert rows[control][-1].strip() == expected[0][-1].strip(), (label, control)
        reviews.append({"path": target.name, "sha256": sha(target), "bytes": target.stat().st_size,
                        "source_sha256": source_sha, "scene_start_seconds": start, "seconds": seconds,
                        "fps": fps, "decoded_frames": len(rows), "encoded_crop_xywh": [x, y, w, h],
                        "native_crop_xyxy": roi, "display_scale": 2, "source_transform_controls": 3,
                        "speed_or_effect_strength_altered": False})
        print(f"Verified detail: {label}", flush=True)

    # A concat input references the source twice; no full repeated source copy is written.
    listing = HERE / f"loop-review-input{args.suffix}.txt"
    listing.write_text(f"file '{media.name}'\nfile '{media.name}'\n")
    target = HERE / f"Back-Before-Dawn-loop-join-10s{args.suffix}.mp4"
    encode([FFMPEG, "-v", "error", "-n", "-f", "concat", "-safe", "0", "-i", str(listing),
            "-ss", str(args.seconds - 5), "-t", "10"] + encoding, target)
    _, rows = framehash(target)
    expected = original_rows[(args.seconds-5)*fps:] + original_rows[:5*fps]
    assert len(rows) == 10 * fps
    assert [r[-1].strip() for r in rows] == [r[-1].strip() for r in expected], "Join pictures do not match source"
    reviews.append({"path": target.name, "sha256": sha(target), "bytes": target.stat().st_size,
                    "source_sha256": source_sha, "seconds": 10, "decoded_frames": len(rows),
                    "exact_encoded_picture_sequence": f"scene{args.seconds-5}–{args.seconds}, then0–5",
                    "all_decoded_yuv_hashes_match_source": True})
    result = {"source": media.relative_to(ROOT).as_posix(), "source_sha256": source_sha,
              "script_sha256": sha(Path(__file__)), "reviews": reviews}
    (HERE / f"detail-review-validation{args.suffix}.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": "details_and_join_verified", "reviews": len(reviews), "source_sha256": source_sha}))


if __name__ == "__main__":
    main()
