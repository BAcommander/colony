"""Measure hypothetical overlap envelopes in memory; writes no audio."""
from pathlib import Path
import json
import subprocess
import numpy as np

ROOT = Path(__file__).resolve().parent
SOURCES = {
    "room": ("C:/Users/jazzs/Downloads/Survey_Room_at_First_Light_2026-11-07T160457.mp4", -6.3),
    "basin": ("C:/Users/jazzs/Downloads/First_Light_Basin_2026-11-07T160457.mp4", -5.9),
}
SR = 48000
def decode(src, start, duration):
    result = subprocess.run(["ffmpeg", "-v", "error", "-nostdin", "-ss", str(start), "-i", src, "-t", str(duration), "-map", "0:a:0", "-f", "f32le", "-"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    assert not result.stderr
    data = np.frombuffer(result.stdout, dtype="<f4").reshape(-1, 2).astype(np.float64)
    assert len(data) == round(duration * SR)
    return data
def db(x):
    return float(20 * np.log10(max(float(x), 1e-15)))
buffers = {}
for key, (path, gain) in SOURCES.items():
    buffers[key] = {"head": decode(path, 4, 46) * 10 ** (gain / 20), "tail": decode(path, 248, 46) * 10 ** (gain / 20)}
results = []
for left, right in (("room", "basin"), ("basin", "room")):
    for seconds in (20, 24, 30, 36):
        count = seconds * SR
        a = buffers[left]["tail"][-count:]
        b = buffers[right]["head"][:count]
        phase = np.linspace(0, np.pi / 2, count, endpoint=True)[:, None]
        blend = a * np.cos(phase) + b * np.sin(phase)
        before = buffers[left]["tail"][-count - 10 * SR:-count]
        after = buffers[right]["head"][count:count + 10 * SR]
        mix = np.concatenate((before, blend, after))
        levels = [db(np.sqrt(np.mean(mix[i:i + SR] ** 2))) for i in range(0, len(mix), SR)]
        local = levels[10:10 + seconds]
        outside_median = float(np.median(levels[:10] + levels[-10:]))
        result = {"direction": left + "-to-" + right, "overlap_seconds": seconds,
                  "outgoing_source_window": [294 - seconds, 294], "incoming_source_window": [4, 4 + seconds],
                  "equal_power_curves": "cos/sin, endpoints included", "gain_db": {left: SOURCES[left][1], right: SOURCES[right][1]},
                  "overlap_correlation": float(np.corrcoef(a.ravel(), b.ravel())[0, 1]),
                  "sample_peak_dbfs": db(np.max(np.abs(mix))),
                  "overlap_rms_min_dbfs": min(local), "overlap_rms_max_dbfs": max(local),
                  "overlap_rms_median_dbfs": float(np.median(local)),
                  "neighbor_10s_median_dbfs": outside_median,
                  "overlap_quietest_minus_neighbor_median_db": min(local) - outside_median,
                  "maximum_adjacent_1s_rms_change_db": float(np.max(np.abs(np.diff(levels)))),
                  "one_second_levels_including_10s_handles_dbfs": levels}
        results.append(result)
        print(json.dumps({k: v for k, v in result.items() if not isinstance(v, list)}))
(ROOT / "join-candidate-measurements.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
