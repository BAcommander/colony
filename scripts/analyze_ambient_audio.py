"""Local ambient reference analyser. Measurements are not a listening verdict."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import math
import os
import re
import subprocess
import sys
import urllib.request
from urllib.parse import quote
from pathlib import Path

import imageio_ffmpeg
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RATE = 48000
EDGES = [0, 80, 250, 1000, 4000, 12000, 24001]
BANDS = ['Below 80 Hz', '80–250 Hz', '250 Hz–1 kHz', '1–4 kHz', '4–12 kHz', '12–24 kHz']
LIMITS = [
    'Signal measurements only; no assistant listening or instrument/vocal identification.',
    'Spectral energy percentages are not perceived loudness percentages.',
    'RMS is an unweighted level measure; LUFS/LRA/true peak are measured separately by FFmpeg.',
    'Recurrence suggests similar patterns, not proven loops; stationary drones can look repetitive.',
    'Change markers identify places to audition, not confirmed musical transitions.',
    'Analysis cannot establish why a listener enjoys a track or predict retention/CTR.',
]


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')


def hash_file(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def db(value, multiplier=10):
    return float(multiplier * np.log10(max(float(value), 1e-15)))


def block_features(x, rate=RATE):
    """Stereo power avoids cancellation of opposite-polarity channels."""
    if not len(x) or not np.isfinite(x).all():
        raise ValueError('Audio contains no samples or contains non-finite samples')
    x = x.astype(np.float64)
    n = min(8192, len(x))
    window = np.hanning(n) if n > 2 else np.ones(n)
    spectra = []
    for start in range(0, len(x) - n + 1, max(n // 2, 1)):
        a = np.abs(np.fft.rfft(x[start:start + n] * window[:, None], axis=0)) ** 2
        a[1:-1] *= 2  # one-sided energy weights
        spectra.append(a.mean(axis=1) / max(float((window ** 2).sum()), 1e-15))
    power = np.mean(spectra, axis=0)
    freq = np.fft.rfftfreq(n, 1 / rate)
    bands = np.array([power[(freq >= lo) & (freq < hi)].sum() for lo, hi in zip(EDGES[:-1], EDGES[1:])])
    total = float(power.sum())
    l, r = x[:, 0], x[:, 1]
    return {
        'samples': len(x), 'energy': float((x ** 2).sum()),
        'peak': float(np.abs(x).max()), 'bands': bands,
        'centroid_hz': float(np.dot(freq, power) / total) if total > 1e-15 else None,
        'cross': float(np.dot(l, r)), 'left': float(np.dot(l, l)), 'right': float(np.dot(r, r)),
        'side': float(((l - r) ** 2).sum() / 4),
        'mid': float(((l + r) ** 2).sum() / 4),
    }


def recurrence(features, minimum=30):
    """Unbiased multiband feature autocorrelation, limited to half the excerpt."""
    f = np.log10(np.asarray(features) + 1e-15)
    if len(f) < 2 * minimum + 4:
        return []
    std = f.std(axis=0)
    active = std > 1e-5
    if not active.any():
        return []
    z = (f[:, active] - f[:, active].mean(axis=0)) / std[active]
    n = len(z)
    size = 1 << (2 * n - 1).bit_length()
    fft = np.fft.rfft(z, size, axis=0)
    ac = np.fft.irfft(fft * fft.conj(), size, axis=0)[:n].mean(axis=1) / np.arange(n, 0, -1)
    peaks = [i for i in range(minimum, n // 2) if ac[i] > ac[i - 1] and ac[i] >= ac[i + 1] and ac[i] > .15]
    chosen = []
    for i in sorted(peaks, key=lambda j: ac[j], reverse=True):
        if all(abs(i - c['lag_seconds']) > 5 for c in chosen):
            chosen.append({'lag_seconds': i, 'feature_autocorrelation': round(float(ac[i]), 4),
                           'overlap_seconds': n - i, 'status': 'candidate; audition required'})
        if len(chosen) == 5:
            break
    return chosen


def scan_audio(source, ffmpeg, out):
    rows, raw_bands = [], []
    sums = dict(samples=0, energy=0., cross=0., left=0., right=0., side=0., mid=0.)
    peak, spectral = 0., np.zeros(len(BANDS))
    with (out / 'decode-log.txt').open('wb') as log:
        proc = subprocess.Popen([ffmpeg, '-v', 'error', '-i', str(source), '-map', '0:a:0',
                                 '-vn', '-ar', str(RATE), '-ac', '2', '-f', 'f32le', 'pipe:1'],
                                stdout=subprocess.PIPE, stderr=log)
        try:
            while True:
                raw = proc.stdout.read(RATE * 8)
                if not raw:
                    break
                if len(raw) % 8:
                    raise ValueError('Incomplete decoded stereo sample')
                x = np.frombuffer(raw, '<f4').reshape(-1, 2)
                f = block_features(x)
                for k in sums:
                    sums[k] += f[k]
                peak = max(peak, f['peak'])
                weight = len(x) / RATE
                spectral += f['bands'] * weight
                raw_bands.append(f['bands'])
                denominator = math.sqrt(f['left'] * f['right'])
                rows.append({'start_seconds': (sums['samples'] - len(x)) / RATE,
                             'duration_seconds': weight,
                             'rms_dbfs': db(f['energy'] / (len(x) * 2)),
                             'peak_dbfs': db(f['peak'], 20),
                             'centroid_hz': f['centroid_hz'],
                             'correlation': f['cross'] / denominator if denominator > 1e-15 else None,
                             'band_percent': (100 * f['bands'] / max(f['bands'].sum(), 1e-15)).tolist()})
                if len(rows) % 300 == 0:
                    print(f'Analysed {len(rows) // 60} minutes', flush=True)
            code = proc.wait()
            if code:
                raise RuntimeError(f'FFmpeg decode failed ({code}); see {out / "decode-log.txt"}')
        finally:
            proc.stdout.close()
            if proc.poll() is None:
                proc.kill()
                proc.wait()
    if not rows:
        raise ValueError('No audio decoded')
    levels = np.array([r['rms_dbfs'] for r in rows])
    weights = np.array([r['duration_seconds'] for r in rows])
    order = np.argsort(levels)
    percentiles = np.interp([.05, .5, .95], (np.cumsum(weights[order]) - .5 * weights[order]) / weights.sum(), levels[order])
    denom = math.sqrt(sums['left'] * sums['right'])
    spatial = sums['side'] + sums['mid']
    # Five-second timbral and RMS differences flag useful audition locations.
    changes = []
    for i in range(5, len(rows)):
        a, b = np.array(rows[i]['band_percent']), np.array(rows[i - 5]['band_percent'])
        score = float(np.abs(a - b).sum() / 100 + abs(levels[i] - levels[i - 5]) / 12)
        changes.append((score, i))
    selected = []
    for score, i in sorted(changes, reverse=True):
        if all(abs(i - s['time_seconds']) >= 30 for s in selected):
            selected.append({'time_seconds': i, 'change_score': round(score, 3)})
        if len(selected) >= 8:
            break
    return {'decoded_duration_seconds': sums['samples'] / RATE,
            'analysis_sample_rate': RATE, 'analysis_channels': 2,
            'overall_rms_dbfs': db(sums['energy'] / (sums['samples'] * 2)),
            'sample_peak_dbfs': db(peak, 20), 'rms_dbfs_p5_p50_p95': percentiles.tolist(),
            'rms_p95_minus_p5_db': float(percentiles[2] - percentiles[0]),
            'band_energy_percent': dict(zip(BANDS, (100 * spectral / max(spectral.sum(), 1e-15)).tolist())),
            'stereo_correlation': sums['cross'] / denom if denom > 1e-15 else None,
            'side_energy_percent': 100 * sums['side'] / spatial if spatial > 1e-15 else None,
            'recurrence_candidates': recurrence(raw_bands[:-1] if rows[-1]['duration_seconds'] < 1 else raw_bands),
            'audition_markers': sorted(selected, key=lambda r: r['time_seconds']), 'timeline': rows}


def loudness(source, ffmpeg, out):
    log_path = out / 'loudness-log.txt'
    with log_path.open('wb') as log:
        result = subprocess.run([ffmpeg, '-hide_banner', '-nostats', '-i', str(source), '-map', '0:a:0',
                                 '-vn', '-af', 'ebur128=peak=true:framelog=verbose', '-f', 'null', '-'],
                                stdout=subprocess.DEVNULL, stderr=log)
    if result.returncode:
        raise RuntimeError(f'Loudness analysis failed; see {log_path}')
    summary = log_path.read_text(errors='replace').rsplit('Summary:', 1)[-1]
    fields = {}
    for name, pattern in [('integrated_lufs', r'\bI:\s*([-+\w.]+) LUFS'),
                          ('loudness_range_lu', r'\bLRA:\s*([-+\w.]+) LU'),
                          ('true_peak_dbtp', r'\bPeak:\s*([-+\w.]+) dBFS')]:
        m = re.search(pattern, summary)
        if not m:
            raise RuntimeError(f'Could not parse {name}; see {log_path}')
        value = float(m[1])
        fields[name] = value if math.isfinite(value) else None
    return fields


def waveform_checks(source, ffmpeg, candidates, duration):
    """Check top feature lags against actual stereo samples at three locations."""
    rate, window, margin = 8000, 8, 3

    def excerpt(start, length):
        r = subprocess.run([ffmpeg, '-v', 'error', '-ss', str(start), '-i', str(source), '-t', str(length),
                            '-ar', str(rate), '-ac', '2', '-f', 'f32le', 'pipe:1'], capture_output=True, check=True)
        return np.frombuffer(r.stdout, '<f4').reshape(-1, 2).astype(np.float64)

    for candidate in candidates[:3]:
        lag = candidate['lag_seconds']
        available = duration - lag - window - margin - 1
        if available < margin + 1:
            continue
        checks = []
        for start in np.linspace(margin + 1, available, 3):
            x, y = excerpt(start, window), excerpt(start + lag - margin, window + 2 * margin)
            n = len(x)
            x -= x.mean(axis=0)
            energy = float((x ** 2).sum())
            if len(y) < n or energy < 1e-12:
                continue
            size = 1 << (len(x) + len(y) - 1).bit_length()
            cross = np.fft.irfft(np.fft.rfft(y, size, axis=0) * np.fft.rfft(x, size, axis=0).conj(), size, axis=0)[:len(y) - n + 1].sum(axis=1)
            sums = np.vstack([np.zeros((1, 2)), np.cumsum(y, axis=0)])
            squares = np.vstack([np.zeros((1, 2)), np.cumsum(y ** 2, axis=0)])
            variance = (squares[n:] - squares[:-n] - (sums[n:] - sums[:-n]) ** 2 / n).sum(axis=1)
            correlation = cross / np.sqrt(energy * np.maximum(variance, 1e-20))
            index = int(np.argmax(correlation))
            checks.append({'start_seconds': round(float(start), 3),
                           'matched_lag_seconds': round(lag - margin + index / rate, 5),
                           'waveform_correlation': round(float(np.clip(correlation[index], -1, 1)), 5)})
        candidate['waveform_checks'] = checks
        candidate['status'] = 'sampled waveform similarity only; review listening and timing before claiming a full loop'
    return candidates


def acquire(url, out, ffmpeg, seconds):
    try:
        import yt_dlp
    except ImportError as error:
        raise RuntimeError('URL input needs yt-dlp. Use the local audio-analysis environment or supply a local file.') from error
    with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True, 'noplaylist': True,
                          'format': 'bestaudio/best', 'socket_timeout': 20, 'retries': 1}) as y:
        try:
            info = y.extract_info(url, download=False)
        except yt_dlp.utils.DownloadError as error:
            raise RuntimeError('Could not access URL audio. Supply a local audio/video file. ' + str(error)) from error
        meta = {k: info.get(k) for k in ['id', 'title', 'channel', 'webpage_url', 'duration', 'is_live', 'live_status', 'format_id']}
        meta['retrieved_at_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
        if info.get('is_live'):
            if info.get('protocol') not in ('m3u8', 'm3u8_native'):
                raise RuntimeError('Live input has no available HLS audio. Supply a local recording.')
            request = urllib.request.Request(info['url'], headers=info.get('http_headers', {}))
            with urllib.request.urlopen(request, timeout=20) as response:
                playlist = response.read().decode('utf-8')
            durations = [float(line.split(':')[1].split(',')[0]) for line in playlist.splitlines() if line.startswith('#EXTINF:')]
            if sum(durations) < seconds + 15:
                raise RuntimeError('Not enough public DVR history for a bounded fast sample; supply a local recording.')
            tail, count = 0., 0
            for duration in reversed(durations):
                tail += duration
                count += 1
                if tail >= seconds + 15:
                    break
            source = out / 'reference-sample.m4a'
            print(f'Capturing {seconds:g}s from public DVR (~{tail:g}s behind live edge)', flush=True)
            with (out / 'capture-log.txt').open('wb') as log:
                r = subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'warning', '-live_start_index', str(-count),
                                    '-i', info['url'], '-t', str(seconds), '-vn', '-c:a', 'copy', '-n', str(source)],
                                   stdout=subprocess.DEVNULL, stderr=log, timeout=max(120, seconds + 60))
            if r.returncode:
                raise RuntimeError('DVR capture failed; see capture-log.txt. Supply a local file instead.')
            meta.update(scope='bounded live DVR excerpt; not the whole stream', requested_sample_seconds=seconds,
                        approximate_start_seconds_behind_live=tail, live_start_index=-count)
        else:
            y.params.update(outtmpl=str(out / 'reference.%(ext)s'), continuedl=False, nopart=False)
            try:
                y.download([url])
            except yt_dlp.utils.DownloadError as error:
                raise RuntimeError('Audio download failed. Supply a local audio/video file. ' + str(error)) from error
            sources = [p for p in out.glob('reference.*') if p.suffix not in ('.part', '.ytdl', '.json')]
            if len(sources) != 1:
                raise RuntimeError('Could not identify downloaded audio file')
            source = sources[0]
            meta['scope'] = 'downloaded audio rendition; not necessarily original master quality'
    write_json(out / 'source-metadata.json', meta)
    return source, meta


def render(report, output, source):
    template = Path(__file__).with_name('ambient_audio_report.html').read_text(encoding='utf-8')
    data = json.dumps(report, ensure_ascii=False, allow_nan=False).replace('<', '\\u003c')
    try:
        audio_uri = quote(Path(os.path.relpath(source, output.parent)).as_posix(), safe='/:')
    except ValueError:  # separate Windows volumes
        audio_uri = source.as_uri()
    content = template.replace('__REPORT_JSON__', data).replace('__AUDIO_URI__', html.escape(audio_uri, quote=True))
    output.write_text(content, encoding='utf-8')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', nargs='?', help='Local audio/video file or public YouTube URL; omit for a file picker')
    parser.add_argument('--out', type=Path, help='New output directory; existing nonempty directories are rejected')
    parser.add_argument('--live-seconds', type=float, default=300, help='Bounded DVR sample for live URLs (default 300)')
    parser.add_argument('--metadata', type=Path, help='Existing capture provenance JSON for a local recording')
    parser.add_argument('--ffmpeg', default=imageio_ffmpeg.get_ffmpeg_exe())
    parser.add_argument('--open', action='store_true', help='Open HTML report in default browser after success')
    args = parser.parse_args(argv)
    try:
        if not args.source:
            import tkinter as tk
            from tkinter.filedialog import askopenfilename
            app = tk.Tk(); app.withdraw()
            args.source = askopenfilename(title='Choose ambient audio or video')
            app.destroy()
            if not args.source:
                return 0
        if not math.isfinite(args.live_seconds) or args.live_seconds < 10 or args.live_seconds > 3600:
            raise ValueError('--live-seconds must be between 10 and 3600')
        stamp = dt.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        out = (args.out or ROOT / 'exports' / 'reference-analysis' / stamp).resolve()
        if out.exists() and any(out.iterdir()):
            raise ValueError('Output directory must be new or empty to preserve earlier results')
        out.mkdir(parents=True, exist_ok=True)
        if args.source.startswith(('https://', 'http://')):
            source, metadata = acquire(args.source, out, args.ffmpeg, args.live_seconds)
        else:
            source = Path(args.source).resolve(strict=True)
            metadata = json.loads(args.metadata.read_text(encoding='utf-8')) if args.metadata else {'scope': 'supplied local file'}
        print('Scanning audio levels, spectrum and stereo…', flush=True)
        measurements = scan_audio(source, args.ffmpeg, out)
        if measurements['recurrence_candidates']:
            print('Checking candidate repeats against stereo waveforms…', flush=True)
            waveform_checks(source, args.ffmpeg, measurements['recurrence_candidates'], measurements['decoded_duration_seconds'])
        print('Measuring integrated LUFS, loudness range and true peak…', flush=True)
        measurements.update(loudness(source, args.ffmpeg, out))
        if measurements['sample_peak_dbfs'] <= -150:
            measurements.update(integrated_lufs=None, loudness_range_lu=None, true_peak_dbtp=None)
        report = {'schema_version': 1, 'title': metadata.get('title') or source.stem,
                  'created_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
                  'source': {'path': str(source), 'sha256': hash_file(source), 'bytes': source.stat().st_size,
                             'metadata': metadata},
                  'method': {'resolution_seconds': 1, 'spectrum': 'Hann-window stereo power, 8192 samples / 50% overlap, resampled 48 kHz',
                             'loudness': 'FFmpeg ebur128 true peak', 'script_sha256': hash_file(Path(__file__)),
                             'numpy_version': np.__version__,
                             'ffmpeg_version': subprocess.check_output([args.ffmpeg, '-version'], text=True).splitlines()[0]},
                  'limitations': LIMITS, 'measurements': measurements}
        write_json(out / 'analysis.json', report)
        render(report, out / 'report.html', source)
        print(f'Report: {out / "report.html"}', flush=True)
        if args.open:
            import webbrowser
            webbrowser.open((out / 'report.html').as_uri())
        return 0
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f'Analysis failed: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
