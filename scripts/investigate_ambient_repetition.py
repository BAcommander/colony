"""Whole-excerpt stereo autocorrelation plus sampled full-band waveform checks."""
import argparse
import json
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np

from analyze_ambient_audio import waveform_checks, hash_file, write_json


def investigate(source, output):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    rate = 2000
    raw = subprocess.check_output([ffmpeg, '-v', 'error', '-i', str(source), '-ar', str(rate),
                                   '-ac', '2', '-f', 'f32le', 'pipe:1'])
    audio = np.frombuffer(raw, '<f4').reshape(-1, 2).astype(np.float64)
    audio -= audio.mean(axis=0)
    n = len(audio)
    size = 1 << (2 * n - 1).bit_length()
    transformed = np.fft.rfft(audio, size, axis=0)
    ac = np.fft.irfft(transformed * transformed.conj(), size, axis=0)[:max(0, n - 120 * rate)].sum(axis=1)
    energy = np.r_[0, np.cumsum((audio * audio).sum(axis=1))]
    lags = np.arange(len(ac))
    ac /= np.maximum(np.sqrt(energy[n - lags] * (energy[n] - energy[lags])), 1e-20)
    peaks = []
    for lo in range(30 * rate, len(ac), rate):
        index = lo + int(np.argmax(ac[lo:lo + rate]))
        peaks.append((float(ac[index]), index / rate))
    chosen = []
    for score, time in sorted(peaks, reverse=True):
        if all(abs(time - c['lag_seconds']) > 8 for c in chosen):
            chosen.append({'lag_seconds': time, 'whole_excerpt_waveform_correlation_0_1khz': score})
        if len(chosen) == 8:
            break
    # Check these independently of the earlier six-band feature candidates.
    for offset in range(0, len(chosen), 3):
        waveform_checks(source, ffmpeg, chosen[offset:offset + 3], n / rate)
    result = {'source': str(source.resolve()), 'source_sha256': hash_file(source),
              'duration_seconds': n / rate,
              'method': 'Whole-excerpt stereo waveform autocorrelation at 2 kHz / 0–1 kHz, 30 seconds up to duration minus 120 seconds; at least two minutes overlap, normalized by overlapping window energies. Top lags checked at three locations using 8 kHz stereo waveforms and ±3s alignment.',
              'limitations': 'Not every band/component, time stretch or longer recurrence is tested. Weak results do not prove absence of loops. Decoder/channel correlation does not identify instruments.',
              'candidates': chosen}
    write_json(output, result)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    investigate(args.source, args.output)
