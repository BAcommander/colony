"""Uniform deeper texture/pace metrics for 30-minute passages. Signal measurements, not listening."""
import json, subprocess, sys
from pathlib import Path
import numpy as np
import imageio_ffmpeg
from scipy import signal, ndimage

FF = imageio_ffmpeg.get_ffmpeg_exe()
R = 16000
FFT, HOP = 2048, 512
ROOT = Path(r'C:\Colony')
E = ROOT / 'exports'
TRACKS = [
    ('SIGNAL STATION', E / 'reference-analysis/signal-station-2026-11-11-30min/reference-sample.m4a', 0),
    ('WINTER WATCH', E / 'reference-analysis/winter-watch-30min-v1/reference-sample.m4a', 0),
    ('Snowline V6', E / '13-below-the-snowline/audio-2h-v6/Below-the-Snowline-2-Hours-v6.mp3', 120),
    ('Rainline', E / 'reference-analysis/comparison-2026-10-30/rainline/published-passage.m4a', 0),
    ('Shoreless', E / 'reference-analysis/comparison-2026-10-30/shoreless/published-passage.m4a', 0),
    ('Basalt', E / 'reference-analysis/comparison-2026-10-30/basalt/published-passage.m4a', 0),
    ('Ringfall', E / 'reference-analysis/comparison-2026-10-30/ringfall/published-passage.m4a', 0),
    ('Spirewatch', E / 'reference-analysis/comparison-2026-10-30/spirewatch/published-passage.m4a', 0),
]


def load(path, start):
    cmd = [FF, '-v', 'error', '-ss', str(start), '-t', '1800', '-i', str(path), '-ac', '2', '-ar', str(R), '-f', 'f32le', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)


def db(x):
    return 10 * np.log10(np.maximum(x, 1e-20))


def analyse(audio):
    freq = np.fft.rfftfreq(FFT, 1 / R)
    alloc = np.zeros(3)
    band_edges = [(40, 160), (160, 500), (500, 2000), (2000, 8000)]
    flat = {b: [] for b in band_edges}
    chroma_frames, harm_flux, frames_power = [], [], []
    hf_env, mid_env, tot_env = [], [], []
    midband = (freq >= 300) & (freq < 6000)
    hf = (freq >= 2000) & (freq < 8000)
    cf = (freq >= 65) & (freq < 1050)
    pitch = np.round(12 * np.log2(freq[cf] / 440.0)).astype(int) % 12
    chunk = R * 300
    for s in range(0, len(audio), chunk):
        a = audio[s:s + chunk]
        if len(a) < R * 20:
            break
        _, _, z = signal.stft(a.T, R, nperseg=FFT, noverlap=FFT - HOP, boundary=None, padded=False)
        p = np.mean(np.abs(z) ** 2, axis=0)
        mag = np.sqrt(p)
        h = ndimage.median_filter(mag, size=(1, 31), mode='reflect') ** 2
        v = ndimage.median_filter(mag, size=(31, 1), mode='reflect') ** 2
        hm = h / np.maximum(h + 4 * v, 1e-20)
        pm = v / np.maximum(v + 4 * h, 1e-20)
        rm = 1 - hm - pm
        alloc += [(p * hm).sum(), (p * rm).sum(), (p * pm).sum()]
        for lo, hi in band_edges:
            b = p[(freq >= lo) & (freq < hi)]
            flat[(lo, hi)].append(np.exp(np.mean(np.log(np.maximum(b, 1e-20)), axis=0)) / np.maximum(b.mean(axis=0), 1e-20))
        hp = p * hm
        c = np.zeros((12, p.shape[1]))
        for k in range(12):
            c[k] = hp[cf][pitch == k].sum(axis=0)
        chroma_frames.append(c)
        hmid = np.sqrt(hp[(freq >= 200) & (freq < 2000)])
        harm_flux.append(np.maximum(np.diff(hmid, axis=1), 0).sum(axis=0) / np.maximum(hmid[:, 1:].sum(axis=0), 1e-12))
        hf_env.append(p[hf].sum(axis=0)); mid_env.append(p[midband].sum(axis=0)); tot_env.append(p.sum(axis=0))
    fps = R / HOP
    cat = lambda xs: np.concatenate(xs, axis=-1)
    hf_env, mid_env, tot_env = cat(hf_env), cat(mid_env), cat(tot_env)
    chroma = cat(chroma_frames)
    out = {}
    alloc /= alloc.sum()
    out['sustained_tonal_pct'], out['noise_residual_pct'], out['transient_pct'] = [round(100 * x, 2) for x in alloc]
    for (lo, hi), vals in flat.items():
        out[f'flatness_{lo}_{hi}'] = round(float(np.median(cat(vals))), 4)

    def sec(env, n=1.0):
        k = int(round(fps * n)); m = len(env) // k
        return env[:m * k].reshape(m, k).mean(axis=1)
    # Continuous high-band bed: level relative to total and its steadiness
    hf1, tot1 = db(sec(hf_env)), db(sec(tot_env))
    out['hf_2to8k_minus_total_db'] = round(float(np.median(hf1 - tot1)), 2)
    out['hf_2to8k_1s_p5_p95_spread_db'] = round(float(np.percentile(hf1, 95) - np.percentile(hf1, 5)), 2)
    # Level movement
    out['total_1s_median_abs_step_db'] = round(float(np.median(np.abs(np.diff(tot1)))), 3)
    t30 = db(sec(tot_env, 30))
    out['total_30s_p5_p95_spread_db'] = round(float(np.percentile(t30, 95) - np.percentile(t30, 5)), 2)
    # Salient events: 100 ms midband level rising >= 6 dB above trailing 10 s median
    k = max(1, int(round(fps * 0.1)))
    m = len(mid_env) // k
    e = db(mid_env[:m * k].reshape(m, k).mean(axis=1))
    base = ndimage.median_filter(e, size=101, mode='nearest', origin=50)  # trailing ~10 s
    for thr in (6, 10):
        above = (e - base) >= thr
        onsets = int(np.sum(above[1:] & ~above[:-1]))
        out[f'events_per_min_{thr}db'] = round(onsets / (m * 0.1 / 60), 2)
    out['pct_time_6db_above_recent'] = round(100 * float(np.mean((e - base) >= 6)), 2)
    # Harmonic pace
    k2 = int(round(fps * 2)); m2 = chroma.shape[1] // k2
    c2 = chroma[:, :m2 * k2].reshape(12, m2, k2).mean(axis=2)
    c2n = c2 / np.maximum(np.linalg.norm(c2, axis=0), 1e-20)
    for lag_s in (10, 60):
        L = lag_s // 2
        out[f'chroma_cosine_distance_{lag_s}s'] = round(float(np.median(1 - np.sum(c2n[:, L:] * c2n[:, :-L], axis=0))), 4)
    share = c2.sum(axis=1) / c2.sum()
    names = 'A A# B C C# D D# E F F# G G#'.split()
    order = np.argsort(share)[::-1]
    out['top_pitch_classes'] = [(names[i], round(100 * float(share[i]), 1)) for i in order[:4]]
    dom = np.argmax(c2, axis=0)
    out['dominant_pitch_class_changes_per_min'] = round(float(np.sum(dom[1:] != dom[:-1])) / (m2 * 2 / 60), 2)
    out['time_share_of_most_common_dominant_pct'] = round(100 * float(np.max(np.bincount(dom, minlength=12)) / len(dom)), 1)
    out['harmonic_onset_flux_median'] = round(float(np.median(cat(harm_flux))), 4)
    out['harmonic_onset_flux_p95'] = round(float(np.percentile(cat(harm_flux), 95)), 4)
    return out


def main():
    """Usage: compare_texture_pace.py OUT.json [name=path[@start_seconds] ...]
    With no name=path arguments the built-in reference set is analysed."""
    tracks = TRACKS
    if len(sys.argv) > 2:
        tracks = []
        for item in sys.argv[2:]:
            name, rest = item.split('=', 1)
            path, _, start = rest.partition('@')
            tracks.append((name, Path(path), float(start or 0)))
    results = {}
    for name, path, start in tracks:
        if not path.exists():
            print('missing', name, file=sys.stderr); continue
        a = load(path, start)
        results[name] = {'seconds': round(len(a) / R, 1), **analyse(a)}
        print(name, 'done', flush=True)
    Path(sys.argv[1]).write_text(json.dumps(results, indent=1))
    keys = [k for k in next(iter(results.values())) if k != 'top_pitch_classes']
    print(f"{'':38}" + ''.join(f'{n[:11]:>12}' for n in results))
    for k in keys:
        print(f'{k:38}' + ''.join(f'{results[n][k]:>12}' for n in results))
    for n in results:
        print(n, results[n]['top_pitch_classes'])


if __name__ == '__main__':
    main()
