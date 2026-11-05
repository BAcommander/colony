"""Prepare Snowline's full V6 audio once, with independent bounded-memory checks."""
from pathlib import Path
import hashlib
import json
import math
import shutil
import subprocess
import time
import numpy as np

H = Path(__file__).resolve().parent
R = H.parents[1]
CACHE = H / 'cache'
SOURCE_AUDIO = R / 'exports/13-below-the-snowline/audio-2h-v6/Below-the-Snowline-2-Hours-unfaded-master-v6.flac'
AUDIO = CACHE / 'Snowline-V6-2-Hours-assembly-audio.flac'
SOURCE_SHA256 = '6c46365081e88d55b198387ea0b53259b7a90b12181e279ddb6dc12e8f474257'
RATE, CHANNELS, SECONDS = 48000, 2, 7200
FRAMES = RATE * SECONDS
GAIN_DB, FADE_START, FADE_SECONDS = 0.4, 7180, 20
FF = shutil.which('ffmpeg') or 'ffmpeg'
PROBE = shutil.which('ffprobe') or 'ffprobe'


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(name, record):
    (H / name).write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')


def audio_info(path):
    data = json.loads(subprocess.check_output([PROBE, '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)]))
    stream = next(item for item in data['streams'] if item['codec_type'] == 'audio')
    assert int(stream['sample_rate']) == RATE and stream['channels'] == CHANNELS
    assert abs(float(data['format']['duration']) - SECONDS) < 1 / RATE
    return stream


def prepare():
    CACHE.mkdir(parents=True, exist_ok=True)
    print('Verifying the original unfaded V6 master SHA-256...', flush=True)
    assert digest(SOURCE_AUDIO) == SOURCE_SHA256, 'Unexpected source master'
    audio_info(SOURCE_AUDIO)
    filters = 'volume=0.4dB:precision=double,afade=t=out:st=7180:d=20:curve=tri'
    if AUDIO.exists():
        print('Existing assembly audio retained; independently verifying it.', flush=True)
        return filters
    print('Encoding +0.4dB and one 20-second closing fade; no opening fade...', flush=True)
    started = last = time.monotonic()
    with (CACHE / 'audio-preparation-encode.log').open('wb') as error:
        command = [FF, '-hide_banner', '-v', 'error', '-nostdin', '-n', '-i', str(SOURCE_AUDIO),
                   '-map', '0:a:0', '-af', filters, '-ar', str(RATE), '-ac', str(CHANNELS),
                   '-sample_fmt', 's32', '-bits_per_raw_sample', '24', '-c:a', 'flac', '-compression_level', '8',
                   '-progress', 'pipe:1', '-stats_period', '10', str(AUDIO)]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=error, text=True)
        for raw in process.stdout:
            key, _, value = raw.strip().partition('=')
            if key == 'out_time_us' and time.monotonic() - last >= 20:
                elapsed = time.monotonic() - started
                seconds = int(value) / 1e6
                print(f'Assembly audio encode {seconds / SECONDS:.1%}; elapsed {elapsed:.0f}s', flush=True)
                last = time.monotonic()
        assert process.wait() == 0, 'Audio encoding failed; retained log and partial output'
    return filters


def read_exact(stream, wanted):
    result = bytearray()
    while len(result) < wanted:
        piece = stream.read(wanted - len(result))
        if not piece:
            break
        result.extend(piece)
    return result


def verify(filters):
    info = audio_info(AUDIO)
    assert info['codec_name'] == 'flac' and int(info['bits_per_raw_sample']) == 24
    print('Comparing every prepared sample against independent gain/fade arithmetic...', flush=True)
    source_stat = SOURCE_AUDIO.stat()
    prepared_stat = AUDIO.stat()
    gain = 10 ** (GAIN_DB / 20)
    ramp_start, ramp_frames = FADE_START * RATE, FADE_SECONDS * RATE
    count = 0
    max_error = peak = source_peak = 0.0
    squared_error = squared_reference = 0.0
    windows = []
    with (CACHE / 'audio-preparation-source-decode.log').open('wb') as err_a, (CACHE / 'audio-preparation-output-decode.log').open('wb') as err_b:
        args = [FF, '-v', 'error', '-xerror', '-nostdin']
        tail = ['-map', '0:a:0', '-ac', '2', '-ar', '48000', '-f', 'f32le', 'pipe:1']
        a = subprocess.Popen(args + ['-i', str(SOURCE_AUDIO)] + tail, stdout=subprocess.PIPE, stderr=err_a)
        b = subprocess.Popen(args + ['-i', str(AUDIO)] + tail, stdout=subprocess.PIPE, stderr=err_b)
        try:
            for second in range(SECONDS):
                raw_a, raw_b = read_exact(a.stdout, RATE * 2 * 4), read_exact(b.stdout, RATE * 2 * 4)
                assert len(raw_a) == len(raw_b) == RATE * 2 * 4, (second, len(raw_a), len(raw_b))
                source = np.frombuffer(raw_a, dtype='<f4').reshape(-1, 2).astype(np.float64)
                actual = np.frombuffer(raw_b, dtype='<f4').reshape(-1, 2).astype(np.float64)
                assert np.isfinite(source).all() and np.isfinite(actual).all()
                expected = source * gain
                if second >= FADE_START:
                    sample = count + np.arange(RATE, dtype=np.float64)
                    envelope = np.clip((FRAMES - sample) / ramp_frames, 0, 1)
                    expected *= envelope[:, None]
                delta = actual - expected
                max_error = max(max_error, float(np.max(np.abs(delta))))
                peak = max(peak, float(np.max(np.abs(actual))))
                source_peak = max(source_peak, float(np.max(np.abs(source))))
                squared_error += float(np.sum(delta * delta))
                squared_reference += float(np.sum(expected * expected))
                count += RATE
                assert peak < 1 and max_error <= 1.1 / 8388608, (second, peak, max_error)
                if second in [0, 4, 5, 19, 20, 7179, 7180, 7190, 7199]:
                    windows.append({'second': second, 'expected_rms': float(np.sqrt(np.mean(expected * expected))),
                                    'prepared_rms': float(np.sqrt(np.mean(actual * actual))),
                                    'maximum_sample_error': float(np.max(np.abs(delta)))})
                if second % 900 == 899:
                    print(f'All-sample audio recipe check: {(second + 1) / 60:.0f}/120 minutes', flush=True)
            assert not a.stdout.read(1) and not b.stdout.read(1), 'Unexpected extra sample frames'
            assert a.wait() == b.wait() == 0 and count == FRAMES
        finally:
            for process in [a, b]:
                if process.poll() is None:
                    process.kill()
                    process.wait()
    assert SOURCE_AUDIO.stat().st_mtime_ns == source_stat.st_mtime_ns and SOURCE_AUDIO.stat().st_size == source_stat.st_size
    assert AUDIO.stat().st_mtime_ns == prepared_stat.st_mtime_ns and AUDIO.stat().st_size == prepared_stat.st_size
    assert digest(SOURCE_AUDIO) == SOURCE_SHA256
    record = {
        'status': 'passed',
        'source': {'path': str(SOURCE_AUDIO), 'bytes': source_stat.st_size, 'sha256': SOURCE_SHA256,
                   'kind': 'Original unity-gain, unfaded V6 master; all six existing layers already present'},
        'output': {'path': str(AUDIO), 'bytes': AUDIO.stat().st_size, 'sha256': digest(AUDIO),
                   'seconds': SECONDS, 'sample_frames': count, 'sample_rate': RATE, 'channels': CHANNELS,
                   'codec': 'flac', 'bits_per_sample': 24},
        'processing': {'gain_db': GAIN_DB, 'closing_fade_start_seconds': FADE_START,
                       'closing_fade_seconds': FADE_SECONDS, 'closing_curve': 'tri',
                       'opening_fade_applied': False, 'new_sfx_added': False,
                       'normalization_or_compression': False, 'ffmpeg_filter': filters},
        'verification': {'all_source_and_output_samples_decoded': True, 'finite': True, 'unclipped': True,
                         'reference': 'Independent numpy float64 multiplication of decoded original source by 10**(0.4/20), then sample-indexed linear closing envelope.',
                         'max_absolute_sample_error': max_error, 'tolerance': 1.1 / 8388608,
                         'quantization_snr_db': 10 * math.log10(squared_reference / max(squared_error, 1e-300)),
                         'prepared_peak_dbfs': 20 * math.log10(peak), 'source_peak_dbfs': 20 * math.log10(source_peak),
                         'bounded_processing_block_seconds': 1, 'source_hash_unchanged': True,
                         'diagnostic_windows': windows, 'assistant_listening_performed': False}}
    save('audio-preparation-validation.json', record)
    print(json.dumps({'status': 'passed', 'sample_frames': count, 'max_sample_error': max_error,
                      'prepared_peak_dbfs': record['verification']['prepared_peak_dbfs'],
                      'output': str(AUDIO)}, indent=2), flush=True)


if __name__ == '__main__':
    verify(prepare())
