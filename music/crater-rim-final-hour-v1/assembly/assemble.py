"""Final Crater Rim hour using the frozen actual Colony v3 export engine."""
from pathlib import Path
import argparse
import dataclasses
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
H = Path(__file__).resolve().parent
R = H.parents[2]
ENGINE = H / "engine"
CACHE = R / ".local/crater-rim-final-hour-v1/assembly"
DEFAULT_MASTER = R / "exports/14-crater-rim-survey/production-v1/Crater-Rim-Survey-clean-600s-4K.mp4"
DEFAULT_VALIDATION = H.parent / "visual/master-validation.json"
AUDIO = R / "exports/14-crater-rim-survey/audio-1h-v1/Crater-Rim-Survey-1-Hour-music-and-SFX-v1.flac"
AUDIO_SHA256 = "333c0fe1b94ac899d0fa6a91ed009c693de312c791913a838662bf7433b5c994"
OUTPUT = R / "exports/14-crater-rim-survey/Crater-Rim-Survey-1-Hour-4K-v1.mp4"
TITLE = "Crater Rim Survey"
SECONDS, UNIT, FPS, FRAMES, UNIT_FRAMES = 3600, 600, 30, 108000, 18000
sys.path.insert(0, str(ENGINE))
if shutil.which("ffmpeg"):
    os.environ["IMAGEIO_FFMPEG_EXE"] = shutil.which("ffmpeg")
from colony import render, intro as opening
from colony.intro import IntroSettings
from app import exporter

FF = render.get_ffmpeg_path()
PROBE = shutil.which("ffprobe") or exporter.get_ffprobe_path()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(name, value):
    path = H / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def run(args):
    return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)


def probe(path):
    return json.loads(run([PROBE, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]).stdout)


def check_video_stream(data, seconds):
    streams = [stream for stream in data["streams"] if stream["codec_type"] == "video"]
    require(len(streams) == 1, "Expected one video stream")
    stream = streams[0]
    require((stream["width"], stream["height"], stream["r_frame_rate"]) == (3840, 2160, "30/1"), "Wrong dimensions/rate")
    require(stream["codec_name"] == "h264" and stream["pix_fmt"] == "yuv420p" and stream["has_b_frames"] == 0, "Unexpected codec/pixel format/B-frames")
    require(int(stream["nb_frames"]) == seconds * FPS and abs(float(stream["duration"]) - seconds) < 1e-6, "Wrong frame count/duration")
    require(stream["color_range"] == "tv" and all(stream[key] == "bt709" for key in ("color_space", "color_transfer", "color_primaries")), "Wrong colour metadata")
    return stream


def verify_engine():
    manifest = json.loads((H / "engine-manifest.json").read_text(encoding="utf-8"))
    for row in manifest["files"]:
        path = H / row["path"]
        require(path.stat().st_size == row["bytes"] and digest(path) == row["sha256"], "Frozen dependency changed: " + str(path))
    require(Path(render.__file__).resolve() == (ENGINE / "colony/render.py").resolve(), "Wrong Colony renderer imported")
    require(Path(opening.__file__).resolve() == (ENGINE / "colony/intro.py").resolve() and opening.VERSION == 3, "Wrong intro implementation")
    require(Path(exporter.__file__).resolve() == (ENGINE / "app/exporter.py").resolve(), "Wrong exporter imported")
    return manifest


def expected_audio_graph(first_input=0):
    return opening.audio_graph(render.build_audio_graph([0.0], 0, first_input=first_input), IntroSettings(TITLE, True))


def packet_rows(path, evidence_path=None):
    result = run([FF, "-v", "error", "-i", str(path), "-map", "0:v:0", "-c:v", "copy", "-f", "framehash", "-hash", "sha256", "pipe:1"])
    require(not result.stderr, "Packet-read errors: " + str(path))
    text = result.stdout.decode()
    if evidence_path:
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(text, encoding="utf-8")
    return [line.split(",")[-1].strip() for line in text.splitlines() if line and not line.startswith("#")]


def prepare_source_parts(master, master_hash):
    CACHE.mkdir(parents=True, exist_ok=True)
    parts = [(0, 60, CACHE / "clean-000-060.mp4"), (60, 540, CACHE / "clean-060-600.mp4")]
    hashes = packet_rows(master, H / "evidence/master-video-packets.sha256")
    require(len(hashes) == UNIT_FRAMES, "Master packet count mismatch")
    rows = []
    for start, duration, path in parts:
        if not path.exists():
            run([FF, "-v", "error", "-nostdin", "-n", "-ss", str(start), "-i", str(master), "-t", str(duration),
                 "-map", "0:v:0", "-an", "-c:v", "copy", "-movflags", "+faststart", str(path)])
        check_video_stream(probe(path), duration)
        copied = packet_rows(path)
        require(copied == hashes[start * FPS:(start + duration) * FPS], "Copied source-part packet mismatch: " + str(path))
        rows.append({"path": str(path), "start_seconds": start, "seconds": duration, "frames": len(copied),
                     "sha256": digest(path), "every_packet_matches_master": True})
    save("source-parts-validation.json", {"status": "passed", "master": str(master), "master_sha256": master_hash,
                                          "method": "Exact keyframe stream-copy split; no picture encoding", "parts": rows})
    return [path for _, _, path in parts]


def preflight(master, validation_path):
    engine = verify_engine()
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    require(validation["status"] == "passed", "Master validation has not passed")
    require(Path(validation["output"]).resolve() == master.resolve(), "Master validation points to another output")
    require(validation["seconds"] == UNIT and validation["dimensions"] == [3840, 2160] and validation["fps"] == FPS,
            "Master validation contract mismatch")
    master_hash = digest(master)
    require(master_hash == validation["sha256"], "Validated master fingerprint mismatch")
    check_video_stream(probe(master), UNIT)
    require(digest(AUDIO) == AUDIO_SHA256, "Approved audio fingerprint mismatch")
    audio_probe = probe(AUDIO)
    audio_stream = next(stream for stream in audio_probe["streams"] if stream["codec_type"] == "audio")
    require(audio_stream["codec_name"] == "flac" and audio_stream["sample_rate"] == "48000" and audio_stream["channels"] == 2,
            "Approved audio stream properties changed")
    require(abs(float(audio_stream["duration"]) - SECONDS) < 1e-6, "Approved audio duration changed")
    expected_size = master.stat().st_size * 6 + 100 * 1024 ** 2
    require(shutil.disk_usage(OUTPUT.parent).free > 2 * expected_size + 2 * master.stat().st_size + 2 * 1024 ** 3,
            "Insufficient room for final file, faststart work and source-parts cache")
    result = {"status": "passed", "master": str(master), "master_sha256": master_hash,
              "master_validation": str(validation_path), "audio": str(AUDIO), "audio_sha256": AUDIO_SHA256,
              "expected_seconds": SECONDS, "expected_frames": FRAMES, "engine_files_verified": len(engine["files"]),
              "ffmpeg": FF, "ffprobe": PROBE, "ffmpeg_version": run([FF, "-version"]).stdout.decode().splitlines()[0]}
    save("preflight-validation.json", result)
    return validation, result


def assemble(master, validation_path):
    require(not OUTPUT.exists(), "Preserve existing final output; inspect it instead of overwriting")
    validation, checked = preflight(master, validation_path)
    first, remainder = prepare_source_parts(master, validation["sha256"])
    # Route actual Colony temporary concat/log/encode work to this job's cache.
    tempfile.tempdir = str(CACHE)
    info = render.probe_video(FF, str(master))
    render._prepared = render.Prepared(str(CACHE), render._file_key(str(master)), info,
                                       render.color_tags_for(info), str(master), float(UNIT), info)
    render.LOOP_CRF = 0
    render.LOOP_PRESET = "veryfast"
    original_args = render._loop_encode_args

    def lossless_args(color):
        args = original_args(color)
        position = args.index("-crf")
        args[position:position + 2] = ["-qp", "0"]
        return args + ["-g", "60", "-keyint_min", "60", "-sc_threshold", "0", "-bsf:v",
                       "h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1:video_full_range_flag=0"]

    render._loop_encode_args = lossless_args
    original_opening_entries = render.opening_entries

    def opening_entries(ffmpeg, prepared, entries, settings, report):
        require(all(Path(path).resolve() == master.resolve() for path in entries), "Unexpected clean playlist")
        first_info = render.probe_video(ffmpeg, str(first))
        short_prepared = dataclasses.replace(prepared, loop_path=str(first), loop_duration=60.0, loop=first_info)
        branded = original_opening_entries(ffmpeg, short_prepared, [str(first)], settings, report)
        require(len(branded) == 1, "Unexpected opening segment count")
        expanded = branded + [str(remainder)] + entries[1:]
        save("assembly-playlist.json", {"entries": expanded, "source_phase": "0-60 intro,60-600 untouched,then complete600s units",
                                        "opening_unit": branded[0], "source_first60": str(first), "source_remainder540": str(remainder),
                                        "output_limit_seconds": SECONDS})
        return expanded

    render.opening_entries = opening_entries
    intro = IntroSettings(TITLE, fade_audio=True)
    settings = {**checked, "title": TITLE, "output": str(OUTPUT), "native_source_dimensions": [1672, 941],
                "opening": intro.record(), "opening_encoder": {"qp": 0, "preset": "veryfast", "gop": 60, "b_frames": 0},
                "audio_processing": {"gain_db": 0, "match_loudness": False, "additional_sfx": None,
                                     "crossfade_seconds": 0, "new_closing_fade": False,
                                     "existing_closing_fade": "Approved source's20s closing fade retained unchanged",
                                     "only_new_envelope": "Silence until5s, half-sine entrance5-20s, once",
                                     "actual_colony_graph_input0": expected_audio_graph()},
                "clean_master_repeats": 6, "first60_only_reencoded_for_intro": True,
                "installed_application_modified": False}
    save("assembly-settings.json", settings)
    previous = [-1, 0, "Starting"]

    def status(message):
        previous[2] = message
        previous[0] = -1
        print(message, flush=True)
        save("assembly-progress.json", {"stage": message, "utc_epoch": time.time()})

    def progress(fraction, eta):
        percent, now = int(fraction * 100), time.monotonic()
        if percent >= previous[0] + 5 or now - previous[1] > 25:
            item = {"stage": previous[2], "stage_progress_percent": percent, "stage_eta_seconds": eta, "utc_epoch": time.time()}
            print(json.dumps(item), flush=True)
            save("assembly-progress.json", item)
            previous[:2] = [percent, now]

    result = render.render(str(master), [str(AUDIO)], str(OUTPUT), crossfade=0,
                           overlay_mode=render.OVERLAY_OFF, match_loudness=False, full_decode=True,
                           overwrite=False, sfx=None, intro=intro, on_status=status, on_progress=progress)
    require(result.output == str(OUTPUT) and result.verified and all(check.ok for check in result.checks), "Colony output verification failed")
    require(result.duration == SECONDS and (result.width, result.height, result.fps) == (3840, 2160, FPS), "Wrong final duration/properties")
    require(result.gains_db == [0] and result.crossfade == 0 and not result.overlay_times, "Unexpected gain/playlist/overlay")
    require(result.manifest, "Colony did not write its manifest")
    shutil.copy2(result.manifest, H / "colony-export.json")
    require(digest(master) == validation["sha256"] and digest(AUDIO) == AUDIO_SHA256, "Source changed during assembly")
    save("assembly-result.json", {"status": "passed", "output": str(OUTPUT), "bytes": OUTPUT.stat().st_size,
                                  "duration_seconds": result.duration, "dimensions": [result.width, result.height], "fps": result.fps,
                                  "colony_full_decode_passed": True, "checks": [vars(check) for check in result.checks],
                                  "source_hashes_unchanged": True, "next": "Run verify_final.py for complete packet/timestamp/AAC checks"})
    print("Actual Colony assembly/full decode complete; independent verification next", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--master", type=Path, default=DEFAULT_MASTER)
    parser.add_argument("--master-validation", type=Path, default=DEFAULT_VALIDATION)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    if args.preflight_only:
        preflight(args.master.resolve(), args.master_validation.resolve())
    else:
        assemble(args.master.resolve(), args.master_validation.resolve())
