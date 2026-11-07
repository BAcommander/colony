"""Read-only measurements of the two original Crater Rim music exports."""
from pathlib import Path
import concurrent.futures
import hashlib
import json
import math
import re
import subprocess
import numpy as np

OUT = Path(__file__).resolve().parent
SOURCES = {
    "survey-room": Path("C:/Users/jazzs/Downloads/Survey_Room_at_First_Light_2026-11-07T160457.mp4"),
    "first-light-basin": Path("C:/Users/jazzs/Downloads/First_Light_Basin_2026-11-07T160457.mp4"),
}

def db(value):
    return 20 * math.log10(max(float(value), 1e-15))

def run(args):
    return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

def meter(src, start=None, duration=None):
    cmd = ["ffmpeg", "-hide_banner", "-nostdin"]
    if start is not None:
        cmd += ["-ss", str(start)]
    cmd += ["-i", str(src)]
    if duration is not None:
        cmd += ["-t", str(duration)]
    cmd += ["-map", "0:a:0", "-af", "loudnorm=I=-23:TP=-1:LRA=11:print_format=json", "-f", "null", "-"]
    result = run(cmd)
    log = result.stderr.decode("utf-8", "replace")
    data = json.loads(re.findall(r'\{[^{}]*"input_i"[^{}]*\}', log, re.S)[-1])
    return data, log

def analyze(item):
    key, src = item
    probe = json.loads(run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(src)]).stdout)
    (OUT / (key + "-probe.json")).write_text(json.dumps(probe, indent=2), encoding="utf-8")
    audio = next(s for s in probe["streams"] if s["codec_type"] == "audio")
    rate, channels = int(audio["sample_rate"]), int(audio["channels"])
    command = ["ffmpeg", "-v", "error", "-nostdin", "-i", str(src), "-map", "0:a:0", "-f", "f32le", "-acodec", "pcm_f32le", "-"]
    decoded = run(command)
    (OUT / (key + "-decode.log")).write_bytes(decoded.stderr)
    pcm = np.frombuffer(decoded.stdout, dtype="<f4").reshape(-1, channels)
    assert np.isfinite(pcm).all(), "Nonfinite decoded samples"
    rows = []
    for step in (1, .25):
        hop = round(rate * step)
        group = []
        for i in range(0, len(pcm), hop):
            chunk = pcm[i:i + hop].astype(np.float64)
            group.append({"start_seconds": i / rate, "duration_seconds": len(chunk) / rate,
                          "rms_dbfs": db(np.sqrt(np.mean(chunk * chunk))),
                          "peak_dbfs": db(np.max(np.abs(chunk)))})
        if step == 1:
            rows = group
        (OUT / (key + ("-one-second-levels.json" if step == 1 else "-quarter-second-levels.json"))).write_text(json.dumps(group, indent=2), encoding="utf-8")
    full, full_log = meter(src)
    interior, interior_log = meter(src, 20, 260)
    (OUT / (key + "-full-loudness.log")).write_text(full_log, encoding="utf-8")
    (OUT / (key + "-interior-loudness.log")).write_text(interior_log, encoding="utf-8")
    data = {
        "source": str(src), "bytes": src.stat().st_size,
        "sha256": hashlib.file_digest(src.open("rb"), "sha256").hexdigest(),
        "audio_stream_duration_seconds": float(audio["duration"]),
        "decoded_sample_frames": len(pcm), "decoded_duration_seconds": len(pcm) / rate,
        "sample_rate": rate, "channels": channels,
        "full_decode_exit": 0, "full_decode_error_log_empty": not bool(decoded.stderr),
        "all_samples_finite": True, "sample_peak_dbfs": db(np.max(np.abs(pcm))),
        "full_meter": full, "interior_20_to_280_seconds_meter": interior,
        "fixed_gain_to_minus23_lufs_full_db": -23 - float(full["input_i"]),
        "fixed_gain_to_minus23_lufs_interior_db": -23 - float(interior["input_i"]),
        "one_second_rms_median_interior_dbfs": float(np.median([r["rms_dbfs"] for r in rows[20:280]])),
        "head_25_seconds": rows[:25], "tail_35_seconds": rows[-35:],
        "inspection_scope": "Full numerical audio decode and measurements; no listening or artistic approval.",
    }
    (OUT / (key + "-analysis.json")).write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        values = list(pool.map(analyze, SOURCES.items()))
    (OUT / "original-source-analysis.json").write_text(json.dumps(values, indent=2), encoding="utf-8")
    for value in values:
        print(json.dumps(value, indent=2))
