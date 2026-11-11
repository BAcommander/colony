"""Continuous ten-minute storm bed for Beneath a Crimson Sky, in two variants.

dark: sheltered wind (two decorrelated layers) plus a continuous low grit floor.
open: dark plus a steady fine-sand hiss layer (1.5-7 kHz) taken from the same grit source.
Thunder is a separate sparse stem. No music. Nothing here repeats on a fixed period:
every layer is drawn as unequal overlapping sections from random source positions.
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from scipy.signal import butter, sosfilt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LIBRARY = ROOT / 'music/sfx-library/assets'
OUT = ROOT / 'exports/15-beneath-a-crimson-sky/storm-bed-v1'
FF = imageio_ffmpeg.get_ffmpeg_exe()
RATE = 48000
SECONDS = 600
N = SECONDS * RATE
SEED = 1511
HISS_BELOW_WIND_DB = 14.0      # open variant: hiss RMS relative to the wind layers
GRIT_BELOW_WIND_DB = 9.0
GUST_DB = 2.5                  # slow swell, plus/minus
BED_LISTEN_RMS_DBFS = -30.0    # same constant gain for both variants, set from the dark bed

spec = importlib.util.spec_from_file_location('design_sound', ROOT / 'music/beneath-a-crimson-sky-persistent-storm/design_sound.py')
design = importlib.util.module_from_spec(spec)
spec.loader.exec_module(design)


def decode(name):
    raw = subprocess.check_output([FF, '-v', 'error', '-i', str(LIBRARY / name), '-vn', '-ac', '2', '-ar', str(RATE), '-f', 'f32le', '-'])
    return np.frombuffer(raw, '<f4').reshape(-1, 2).astype(np.float32)


def band(data, lo, hi, order=3):
    return sosfilt(butter(order, [lo, hi], btype='bandpass', fs=RATE, output='sos'), data, axis=0).astype(np.float32)


def rms(x):
    return float(np.sqrt(np.mean(np.square(x, dtype=np.float64))))


def db(x):
    return 20 * np.log10(max(x, 1e-12))


def continuous(rng, source, seg_range, overlap_range, swap=False):
    """Equal-power overlapped sections from random source positions; unit RMS per section."""
    out = np.zeros((N, 2), np.float32)
    placed = []
    t = -int(overlap_range[1] * RATE)
    prev_overlap = int(rng.uniform(*overlap_range) * RATE)
    while t < N:
        length = min(int(rng.uniform(*seg_range) * RATE), len(source) - 1)
        next_overlap = int(rng.uniform(*overlap_range) * RATE)
        start = int(rng.integers(0, len(source) - length))
        seg = source[start:start + length].copy()
        if swap:
            seg = seg[:, ::-1]
        seg /= max(rms(seg), 1e-9)
        env = np.ones(length, np.float32)
        env[:prev_overlap] = np.sin(np.linspace(0, np.pi / 2, prev_overlap))
        env[-next_overlap:] = np.cos(np.linspace(0, np.pi / 2, next_overlap))
        seg *= env[:, None]
        a, b = max(t, 0), min(t + length, N)
        if b > a:
            out[a:b] += seg[a - t:b - t]
        placed.append((round(t / RATE, 2), round(length / RATE, 2), round(start / RATE, 2)))
        t += length - next_overlap
        prev_overlap = next_overlap
    return out, placed


def gust_curve(rng):
    tt = np.arange(N, dtype=np.float32) / RATE
    g = sum(w * np.sin(2 * np.pi * tt / p + rng.uniform(0, 2 * np.pi)) for p, w in ((47.0, .45), (83.0, .35), (131.0, .30)))
    return (g / np.max(np.abs(g))).astype(np.float32)


def write(name, audio, gain_db=0.0):
    data = (audio * 10 ** (gain_db / 20)).astype('<f4')
    assert np.isfinite(data).all() and float(np.max(np.abs(data))) < 1, name
    for ext, codec in (('.flac', ['-c:a', 'flac', '-sample_fmt', 's32']), ('.mp3', ['-c:a', 'libmp3lame', '-b:a', '192k'])):
        path = OUT / (name + ext)
        subprocess.run([FF, '-v', 'error', '-n', '-f', 'f32le', '-ar', str(RATE), '-ac', '2', '-i', '-', *codec, str(path)],
                       input=data.tobytes(), check=True)


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    rng = np.random.default_rng(SEED)
    wind_src, grit_src = decode('wind-soft-exterior-01.mp3'), decode('grit-mineral-soft-01.mp3')
    gust = gust_curve(rng)

    wind_a, plan_a = continuous(rng, band(wind_src, 70, 1810), (9, 14), (3.5, 5.3))
    wind_b, plan_b = continuous(rng, band(wind_src, 60, 700), (11, 17), (4.0, 6.0), swap=True)
    wind = wind_a + wind_b * 10 ** (-4 / 20)
    wind *= (0.020 / rms(wind))
    wind *= (10 ** (GUST_DB * gust / 20))[:, None]

    grit, plan_g = continuous(rng, band(grit_src, 165, 2360), (3.0, 6.0), (1.0, 2.0))
    grit *= rms(wind) * 10 ** (-GRIT_BELOW_WIND_DB / 20) / rms(grit)
    grit *= (10 ** (1.3 * GUST_DB * gust / 20))[:, None]

    hiss, plan_h = continuous(rng, band(grit_src, 1500, 7000, order=2), (3.5, 6.5), (1.2, 2.2), swap=True)
    hiss *= rms(wind) * 10 ** (-HISS_BELOW_WIND_DB / 20) / rms(hiss)
    hiss *= (10 ** (1.3 * GUST_DB * gust / 20))[:, None]

    dark = wind + grit
    openv = dark + hiss

    # Sparse distant thunder: unequal 110-230 s gaps, far and soft, separate stem.
    thunder = np.zeros((N, 2), np.float32)
    cues, t = [], rng.uniform(50, 90)
    while t < SECONDS - 20:
        distance, length = rng.uniform(.55, .8), rng.uniform(9, 12.5)
        event = design.thunder(rng, length, distance)
        level_db = rng.uniform(1.0, 4.0)     # peak 100 ms RMS relative to dark-bed RMS
        k = RATE // 10
        peak = max(rms(event[i:i + k]) for i in range(0, len(event) - k, k))
        event *= rms(dark) * 10 ** (level_db / 20) / peak
        a = int(t * RATE)
        b = min(a + len(event), N)
        thunder[a:b] += event[:b - a]
        cues.append({'start_s': round(t, 1), 'length_s': round(length, 1), 'distance': round(float(distance), 2), 'peak_above_bed_db': round(float(level_db), 1)})
        t += rng.uniform(110, 230)

    gain = BED_LISTEN_RMS_DBFS - db(rms(dark))
    write('storm-bed-dark-10min', dark, gain)
    write('storm-bed-open-10min', openv, gain)
    write('storm-bed-dark-with-thunder-10min', dark + thunder, gain)
    write('storm-bed-open-with-thunder-10min', openv + thunder, gain)
    write('thunder-stem-10min', thunder, gain)

    report = {
        'seed': SEED, 'seconds': SECONDS, 'rate': RATE, 'listening_gain_db': round(gain, 3),
        'sources': ['music/sfx-library/assets/wind-soft-exterior-01.mp3 (30 s)', 'music/sfx-library/assets/grit-mineral-soft-01.mp3 (12 s)',
                    'synthesized thunder from music/beneath-a-crimson-sky-persistent-storm/design_sound.py'],
        'settings': {'grit_below_wind_db': GRIT_BELOW_WIND_DB, 'hiss_below_wind_db': HISS_BELOW_WIND_DB, 'gust_db': GUST_DB,
                     'gust_periods_s': [47, 83, 131], 'wind_bands_hz': [[70, 1810], [60, 700]], 'grit_band_hz': [165, 2360], 'hiss_band_hz': [1500, 7000]},
        'section_counts': {'wind_a': len(plan_a), 'wind_b': len(plan_b), 'grit': len(plan_g), 'hiss': len(plan_h)},
        'rms_dbfs_after_gain': {'dark': round(db(rms(dark)) + gain, 2), 'open': round(db(rms(openv)) + gain, 2), 'thunder_stem': round(db(rms(thunder)) + gain, 2)},
        'peak_dbfs_after_gain': {'dark+thunder': round(db(float(np.max(np.abs(dark + thunder)))) + gain, 2), 'open+thunder': round(db(float(np.max(np.abs(openv + thunder)))) + gain, 2)},
        'thunder_cues': cues,
        'no_music': True, 'assistant_listened': False,
    }
    (HERE / 'bed-report.json').write_text(json.dumps(report, indent=1) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=1))


if __name__ == '__main__':
    sys.exit(main())
