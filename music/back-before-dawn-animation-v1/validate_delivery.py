"""Independent native/encoded checks for the complete workshop review.

Run from the repository root using the pinned animation environment. This checks
technical delivery and motion boundaries; it does not confer artistic approval.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import platform
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
# Do not populate sys.modules['core'] with the older shared module before loading
# the renderer. That would bypass its scene-local frozen dependency import.
_core_spec = importlib.util.spec_from_file_location("workshop_review_core", HERE / "dependencies/core.py")
_core = importlib.util.module_from_spec(_core_spec)
_core_spec.loader.exec_module(_core)
FFMPEG, sha, roi_slice = _core.FFMPEG, _core.sha, _core.roi_slice

DEFAULT_MEDIA = HERE / "Back-Before-Dawn-v1-first-draft-120s.mp4"
PREVIEW_SIZE = (1280, 720)
RGB_TO_YUV = "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p"
YUV_TO_RGB = "scale=in_color_matrix=bt709:in_range=tv:out_range=full,format=rgb24"


def load_scene(attention_mode=None):
    spec = importlib.util.spec_from_file_location("workshop_review_scene", HERE / "render.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Scene(attention_mode) if attention_mode else module.Scene()


def framehash(path, filters=None, start=None, frames=None):
    command = [FFMPEG, "-v", "error"]
    if start is not None:
        command += ["-ss", f"{start:.9f}"]
    command += ["-i", str(path), "-map", "0:v:0"]
    if filters:
        command += ["-vf", filters]
    if frames is not None:
        command += ["-frames:v", str(frames)]
    command += ["-f", "framehash", "-"]
    text = subprocess.check_output(command, text=True)
    rows = [row.split(",") for row in text.splitlines() if row and not row.startswith("#")]
    return text, rows


def native_preview(scene, t, only=None):
    return cv2.resize(scene.frame(float(t), only=only), PREVIEW_SIZE, interpolation=cv2.INTER_AREA)


def control_yuv(scene, indices):
    rgb = b"".join(native_preview(scene, index / scene.fps).tobytes() for index in indices)
    command = [FFMPEG, "-v", "error", "-f", "rawvideo", "-pixel_format", "rgb24",
               "-s", "1280x720", "-r", str(scene.fps), "-i", "pipe:0", "-vf", RGB_TO_YUV,
               "-f", "rawvideo", "-pix_fmt", "yuv420p", "-"]
    return subprocess.check_output(command, input=rgb)


def read_rgb_frames(path, start, count, fps):
    command = [FFMPEG, "-v", "error", "-ss", f"{start:.9f}", "-i", str(path),
               "-frames:v", str(count), "-vf", YUV_TO_RGB, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.check_output(command)
    expected = count * 1280 * 720 * 3
    assert len(raw) == expected, (start, count, len(raw), expected)
    return np.frombuffer(raw, np.uint8).reshape(count, 720, 1280, 3)


def _small_masks(scene):
    yield "whole_composite", np.ones((720, 1280), bool)
    for name, mask in scene.masks.items():
        full = np.zeros(scene.base.shape[:2], np.uint8)
        full[roi_slice(scene.regions[name])] = np.uint8(np.asarray(mask) > 0)
        small = cv2.resize(full, PREVIEW_SIZE, interpolation=cv2.INTER_NEAREST) > 0
        if np.any(small):
            yield name, small


def _mae(a, b, mask):
    # Subtract after casting; uint8 subtraction would hide negative changes.
    return float(np.abs(a[mask].astype(np.float32) - b[mask].astype(np.float32)).mean())


def encoded_boundary(scene, before, after, label):
    """Compare a real join with all ordinary steps in adjacent seconds.

    Tiny emitter masks can see integer rain crossings; four arbitrary reference
    frames are not a useful baseline. The join is excluded from its own baseline.
    """
    records = []
    for name, mask in _small_masks(scene):
        join = _mae(before[-1], after[0], mask)
        ordinary = [_mae(a, b, mask) for block in [before, after] for a, b in zip(block[:-1], block[1:])]
        maximum = max(ordinary)
        limit = maximum * 1.7 + .3
        records.append({"region": name, "boundary": label, "join_rgb_mae": join,
                        "ordinary_steps": len(ordinary), "ordinary_max_rgb_mae": maximum,
                        "ordinary_p95_rgb_mae": float(np.percentile(ordinary, 95)),
                        "gate_rgb_mae": limit, "pass": bool(join <= limit)})
    return records


def _serializable(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(type(value).__name__)


def check_native(scene, duration):
    assert not getattr(scene, "assets_ready", []), ("required_assets_missing", scene.assets_ready)
    before = scene.input_hashes()
    assert not any(path.endswith("tree-clean-background.png") for path in before), "Rejected generated canopy backfill is still a runtime input"
    for obj in getattr(scene, "foliage", []):
        roi = obj["roi"] if isinstance(obj, dict) else obj.roi
        texture = obj["source"] if isinstance(obj, dict) else getattr(obj, "src", None)
        assert np.array_equal(texture, scene.base[roi_slice(roi)]), "Canopy motion does not use the unchanged original source texture"
    protected = ~scene.allowed
    # Independent source tracing caught rain on this small raised car fin after
    # the earlier broad footprint checks passed. Its complete contour must be
    # outside every runtime animation footprint, not merely quiet at one time.
    fin_polygon = [[929, 113], [944, 63], [975, 62], [971, 110]]
    fin_points = [(960, 68), (963, 70), (965, 72)]
    fin_mask = np.zeros(scene.base.shape[:2], np.uint8)
    cv2.fillPoly(fin_mask, [np.asarray(fin_polygon, np.int32)], 1)
    fin_mask = fin_mask > 0
    assert not np.any(scene.allowed[fin_mask]), "Raised hero fin overlaps a runtime animation footprint"
    assert all(not scene.allowed[y, x] for x, y in fin_points), "Raised hero fin test point is not protected"
    # Include the short practical peaks which a uniform half-second grid can miss.
    cue_times = []
    schedule = getattr(scene, "schedule", {})
    for start, _ in schedule.get("lamp_dips", []):
        cue_times += [start - .05, start + .10, start + .20, start + .45]
    cue_times += [start + 2 for start in schedule.get("panel_starts", [])]
    cue_times += [schedule["diagnostic_start"] + 1] if "diagnostic_start" in schedule else []
    states = sorted(set(float(t) for t in [*np.linspace(0, duration, 241), *cue_times] if 0 <= t <= duration))
    protected_changes = 0
    audit_states = []
    for t in states:
        frame = scene.frame(float(t))
        assert frame.dtype == np.uint8 and frame.shape == scene.base.shape
        changed = int(np.count_nonzero(np.any(frame != scene.base, axis=2) & protected))
        protected_changes = max(protected_changes, changed)
        assert changed == 0, ("protected_native_pixels", float(t), changed)
        assert np.array_equal(frame[fin_mask], scene.base[fin_mask]), ("raised_fin_polygon", float(t))
        assert all(np.array_equal(frame[y, x], scene.base[y, x]) for x, y in fin_points), ("raised_fin_points", float(t))
        if callable(getattr(scene, "audit", None)):
            audit = scene.audit(float(t))
            assert audit.get("required_assets_present", True), ("required_assets_missing", float(t))
            audit_states.append({"t": float(t), "result": audit})
    assert np.array_equal(scene.frame(0), scene.frame(duration)), "Native endpoint does not close"
    minute_pairs = []
    for t in range(0, 60, 3):
        delta = np.abs(scene.frame(t).astype(np.int16) - scene.frame(t + 60).astype(np.int16))
        if np.any(delta):
            minute_pairs.append({"first_minute_t": t, "second_minute_t": t + 60,
                                 "changed_native_pixels": int(np.count_nonzero(np.any(delta, axis=2)))})
    assert minute_pairs, "The proposed120s review is an exact copy of the first minute"
    phase_closure = []
    for name in getattr(scene, "effect_groups", []):
        first = scene.frame(0, only=[name])
        end = scene.frame(duration, only=[name])
        closed = bool(np.array_equal(first, end))
        assert closed, ("isolated_phase_closure", name)
        # Equality at the endpoint alone is insufficient, so retain real frame-step evidence.
        previous = scene.frame(duration - 1 / scene.fps, only=[name])
        following = scene.frame(1 / scene.fps, only=[name])
        phase_closure.append({"group": name, "endpoint_equal": closed,
                              "native_join_mae": float(np.abs(previous.astype(float)-first).mean()),
                              "native_first_ordinary_step_mae": float(np.abs(following.astype(float)-first).mean())})
    # These native source regions are deliberately independent of the renderer's
    # allowed union. A broad but misplaced weather mask could pass that union test.
    geometry_times = [0, 16, 27.5, 57, 60, 68, 94.3, 111]
    geometry_times += [start + 9.5 for start in schedule.get("passing_car_starts", [])]
    geometry_times = [t for t in geometry_times if t < duration]
    guards = []
    guards.append({"label": "foliage_uses_original_texture_without_generated_backfill",
                   "source_crops_exact": True, "generated_background_in_runtime_inputs": False,
                   "moving_regions": len(getattr(scene, "foliage", [])),
                   "inspection_limit": "This checks texture provenance; the material/edge appearance still requires native and full-speed visual review."})
    guards.append({"label": "raised_hero_fin_excluded_from_all_animation", "native_polygon": fin_polygon,
                   "native_test_points": fin_points, "polygon_pixels": int(np.count_nonzero(fin_mask)),
                   "outside_runtime_allowed_mask": True, "sampled_states": len(states),
                   "source_pixels_exact": True,
                   "coverage_note": "Every encoded native frame also checks this contour because it is outside the runtime allowed mask."})
    weather_groups = [name for name in ["rain", "road", "drips", "traffic", "foliage"]
                      if name in getattr(scene, "effect_groups", [])]
    for label, roi, groups in [
            ("hero_bonnet_interior_unchanged_by_weather", [260, 440, 650, 475], weather_groups),
            ("hero_near_wheel_unchanged_by_weather", [670, 660, 774, 790], weather_groups),
            ("hero_rear_quarter_excluded_from_exterior_weather", [1377, 408, 1446, 490], weather_groups),
            ("background_parked_car_body_excluded_from_water_warp", [1612, 254, 1670, 280], ["road"]),
            ("closed_bench_vessel_is_not_an_emitter", [416, 249, 443, 291], None)]:
        a, b, c, d = roi
        exact = all(np.array_equal(scene.frame(t, only=groups)[b:d, a:c], scene.base[b:d, a:c])
                    for t in geometry_times)
        assert exact, ("independent_source_geometry_guard", label)
        guards.append({"label": label, "native_roi_xyxy": roi, "isolated_groups": groups,
                       "sampled_times": geometry_times, "source_pixels_exact": True})
    assert scene.input_hashes() == before, "An input changed during validation"
    return {"attention_mode": getattr(scene, "mode", "review120"), "checked_duration_seconds": duration,
            "independent_native_protection_states": len(states), "protected_pixel_changes": protected_changes,
            "native_endpoint_identity": True, "differing_minute_pairs": minute_pairs,
            "isolated_phase_closure": phase_closure, "renderer_audit_states": audit_states,
            "independent_source_geometry_guards": guards,
            "input_hashes": before}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--media", type=Path, default=DEFAULT_MEDIA)
    parser.add_argument("--seconds", type=int)
    parser.add_argument("--attention-mode", choices=["review120", "production600"])
    parser.add_argument("--native-only", action="store_true")
    args = parser.parse_args()
    scene = load_scene(args.attention_mode)
    args.seconds = args.seconds or int(getattr(scene, "period", 120))
    native = check_native(scene, args.seconds)
    if args.native_only:
        result = {"status": "native_checks_passed_encoded_review_pending", **native}
        suffix = "-production600" if getattr(scene, "mode", "review120") == "production600" else ""
        (HERE / f"native-validation{suffix}.json").write_text(json.dumps(result, indent=2, default=_serializable) + "\n")
        print(json.dumps({"status": result["status"], "states": native["independent_native_protection_states"]}))
        return

    media = args.media.resolve()
    count = args.seconds * scene.fps
    text, rows = framehash(media)
    assert len(rows) == count
    assert [int(row[1]) for row in rows] == list(range(count)), "Nonsequential DTS"
    assert [int(row[2]) for row in rows] == list(range(count)), "Nonsequential PTS"
    assert all(int(row[3]) == 1 for row in rows)
    assert f"#tb 0: 1/{scene.fps}" in text and "#dimensions 0: 1280x720" in text
    metadata = subprocess.run([FFMPEG, "-hide_banner", "-i", str(media)], capture_output=True, text=True).stderr
    assert "yuv420p" in metadata and "bt709" in metadata and "tv" in metadata and "Audio:" not in metadata
    control_times = [3.5, 8, 14, 23.5, 36, 48, 59.9666667, 60, 60.0333333, 72, 84, 96, 108, 116]
    control_times += [start + .15 for start, _ in getattr(scene, "schedule", {}).get("lamp_dips", [])]
    indices = sorted(set([0, 1, count - 2, count - 1] + [round(t * scene.fps) for t in control_times]))
    indices = [index for index in indices if 0 <= index < count]
    raw = control_yuv(scene, indices)
    size = 1280 * 720 * 3 // 2
    assert len(raw) == size * len(indices)
    for i, index in enumerate(indices):
        assert hashlib.sha256(raw[i*size:(i+1)*size]).hexdigest() == rows[index][-1].strip(), ("native_yuv", index)

    first = read_rgb_frames(media, 0, scene.fps, scene.fps)
    last = read_rgb_frames(media, args.seconds - 1, scene.fps, scene.fps)
    boundaries = encoded_boundary(scene, last, first, "120_to_0")
    if args.seconds > 60:
        before_minute = read_rgb_frames(media, 59, scene.fps, scene.fps)
        after_minute = read_rgb_frames(media, 60, scene.fps, scene.fps)
        boundaries += encoded_boundary(scene, before_minute, after_minute, "59_60_internal_no_reset")
    failures = [record for record in boundaries if not record["pass"]]
    assert not failures, failures

    evidence = HERE / "evidence"
    evidence.mkdir(exist_ok=True)
    for t in [8, 23.5, 48, 60, 84, 108]:
        if t < args.seconds:
            index = round(t * scene.fps)
            rgb = read_rgb_frames(media, index / scene.fps, 1, scene.fps)[0]
            Image.fromarray(rgb).save(evidence / f"decoded-{index / scene.fps:06.2f}s.png")
    assert scene.input_hashes() == native["input_hashes"]
    result = {"status": "technical_checks_passed_user_visual_review_pending",
              "path": media.relative_to(ROOT).as_posix(), "sha256": sha(media), "bytes": media.stat().st_size,
              "seconds": args.seconds, "fps": scene.fps, "dimensions": [1280, 720], "audio": False,
              "decoded_frames": len(rows), "unique_decoded_frame_hashes": len(set(row[-1] for row in rows)),
              "explicit_bt709_tv": True, "native_yuv_exact_controls": indices,
              "source_protection_checked_every_frame_during_encode": True,
              **native, "regional_encoded_boundaries": boundaries,
              "runtime": {"python": platform.python_version(), "numpy": np.__version__, "opencv": cv2.__version__,
                          "ffmpeg": FFMPEG, "ffmpeg_sha256": sha(FFMPEG)},
              "validator_sha256": sha(Path(__file__)),
              "inspection_limit": "Technical delivery is checked independently; native/decoded still inspection and user full-speed artistic review remain distinct. No assistant continuous-playback approval is inferred."}
    (HERE / "delivery-validation.json").write_text(json.dumps(result, indent=2, default=_serializable) + "\n")
    summary = {key: result[key] for key in ["status", "path", "sha256", "seconds", "fps", "decoded_frames", "unique_decoded_frame_hashes"]}
    summary.update({"exact_controls": len(indices), "sampled_native_states": len(native["renderer_audit_states"])
                    or native["independent_native_protection_states"], "encoded_regional_boundaries": len(boundaries)})
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
