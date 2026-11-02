"""Inspect candidate narrow tones, level motion and band-limited noise in a mix.

These are signal measurements and complementary filters, not semantic separation
of radio, speech, effects or music. No transcription or source classification.
"""
import argparse
import base64
import hashlib
import json
import subprocess
import webbrowser
from datetime import datetime, timezone
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from scipy import ndimage, signal

RATE = 16000
FFT = 8192
HOP = 2048
MIN_CONTRAST = 10.0
MIN_TRACK_SECONDS = 3.0


def spectrum(audio):
    frequencies, times, z = signal.stft(
        audio.T, RATE, nperseg=FFT, noverlap=FFT-HOP,
        boundary='zeros', padded=True,
    )
    power = np.mean(np.abs(z) ** 2, axis=0)
    return frequencies, times, z, power


def tone_candidates(frequencies, times, power, low=80, high=3500):
    """Link locally prominent spectral peaks; gaps terminate tracks.

    A detected ridge may be a musical partial, interference or another tone.
    Continuity is a heuristic and can swap between nearby simultaneous tones.
    """
    log_power = 10*np.log10(np.maximum(power, 1e-20))
    background = ndimage.median_filter(log_power, size=(65, 1), mode='reflect')
    contrast = log_power-background
    df = float(frequencies[1]-frequencies[0])
    dt = float(times[1]-times[0])
    active, finished = [], []
    for frame in range(len(times)):
        if times[frame] < .4 or times[frame] > times[-1]-.5:
            continue
        peaks, _ = signal.find_peaks(
            contrast[:, frame], height=MIN_CONTRAST, prominence=6, distance=3,
        )
        peaks = peaks[(frequencies[peaks] >= low) & (frequencies[peaks] <= high)]
        peaks = peaks[log_power[peaks, frame] > log_power[:, frame].max()-50]
        peaks = sorted(peaks, key=lambda p: -contrast[p, frame])[:24]
        available = set(range(len(active)))
        next_active = []
        for peak in peaks:
            freq = float(frequencies[peak])
            matches = [index for index in available
                       if abs(active[index]['hz'][-1]-freq) <= max(3*df, 180*dt, .04*freq)]
            if matches:
                index = min(matches, key=lambda i: abs(active[i]['hz'][-1]-freq))
                track = active[index]
                available.remove(index)
            else:
                track = {'frames': [], 'hz': [], 'contrast_db': [], 'spectral_db': []}
            # Parabolic interpolation of the local log-power maximum.
            left, centre, right = log_power[peak-1:peak+2, frame]
            denominator = left-2*centre+right
            offset = float(np.clip(.5*(left-right)/denominator, -.5, .5)) if abs(denominator)>1e-9 else 0.
            track['frames'].append(frame)
            track['hz'].append(freq+offset*df)
            track['contrast_db'].append(float(contrast[peak, frame]))
            track['spectral_db'].append(float(log_power[peak, frame]))
            next_active.append(track)
        finished.extend(active[i] for i in available)
        active = next_active
    finished.extend(active)
    retained = []
    for track in finished:
        if (len(track['frames'])-1)*dt < MIN_TRACK_SECONDS:
            continue
        hz = np.array(track['hz'])
        levels = np.array(track['spectral_db'])
        track.update({
            'start_seconds': float(times[track['frames'][0]]),
            'end_seconds': float(times[track['frames'][-1]]),
            'duration_seconds': float((len(hz)-1)*dt),
            'frequency_p5_p50_p95_hz': np.percentile(hz, [5, 50, 95]).tolist(),
            'level_p5_p95_span_db': float(np.percentile(levels, 95)-np.percentile(levels, 5)),
            'median_local_contrast_db': float(np.median(track['contrast_db'])),
            'frequency_span_over_four_bins': bool(np.percentile(hz, 95)-np.percentile(hz, 5) > 4*df),
        })
        retained.append(track)
    retained.sort(key=lambda x: -x['duration_seconds']*x['median_local_contrast_db'])
    for number, track in enumerate(retained, 1):
        track['id'] = number
    return retained, contrast


def modulation_candidates(envelope, sample_rate):
    """Candidate envelope rates, never a test for looping or voice activity."""
    x = signal.detrend(np.asarray(envelope, dtype=float))
    if len(x) < 40 or np.std(x) < 1e-10:
        return []
    # Reject tiny finite-window fluctuations in otherwise steady noise.
    if np.std(x)/max(float(np.mean(envelope)), 1e-12) < .06:
        return []
    f, p = signal.welch(x, sample_rate, nperseg=min(len(x), int(sample_rate*40)))
    selected = (f >= .05) & (f <= 2)
    f, p = f[selected], p[selected]
    if len(f) < 5:
        return []
    db = 10*np.log10(np.maximum(p, 1e-20))
    peaks, props = signal.find_peaks(db, prominence=6)
    ranked = sorted(zip(peaks, props['prominences']), key=lambda item: -p[item[0]])
    retained = []
    for i, prominence in ranked:
        fraction = float(p[max(0, i-1):i+2].sum()/max(float(p.sum()), 1e-20))
        if f[i]*len(x)/sample_rate < 6 or fraction < .2:
            continue
        # Require compatible phase and substantial sinusoidal level motion in
        # three disjoint sections. This is a conservative heuristic, not a
        # statistical proof of periodicity or a test for repeated audio.
        phases, explained, depth = [], [], []
        for indexes in np.array_split(np.arange(len(x)), 3):
            time = indexes/sample_rate
            local = np.asarray(envelope, dtype=float)[indexes]
            angle = 2*np.pi*f[i]*time
            design = np.column_stack([np.ones(len(time)), time-time.mean(),
                                      np.sin(angle), np.cos(angle)])
            coefficients = np.linalg.lstsq(design, local, rcond=None)[0]
            periodic = design[:, 2:]@coefficients[2:]
            detrended = signal.detrend(local)
            explained.append(float(np.var(periodic)/max(float(np.var(detrended)), 1e-20)))
            depth.append(float(np.linalg.norm(coefficients[2:])/max(float(local.mean()), 1e-12)))
            phases.append(float(np.arctan2(coefficients[3], coefficients[2])))
        coherence = float(abs(np.mean(np.exp(1j*np.array(phases)))))
        if min(explained) < .3 or min(depth) < .08 or coherence < .9:
            continue
        retained.append({'frequency_hz': float(f[i]), 'period_seconds': float(1/f[i]),
                         'prominence_db': float(prominence),
                         'near_peak_fraction_of_searched_modulation_power': fraction,
                         'three_section_phase_coherence': coherence,
                         'three_section_minimum_explained_variance_ratio': min(explained),
                         'three_section_minimum_amplitude_over_mean': min(depth)})
    return retained[:3]


def band_envelopes(audio):
    bands = [(40, 250), (250, 1000), (1000, 3500), (3500, 7500)]
    result = []
    block = RATE//10
    count = len(audio)//block
    for low, high in bands:
        sos = signal.butter(4, [low, high], fs=RATE, btype='bandpass', output='sos')
        filtered = signal.sosfiltfilt(sos, audio, axis=0)
        power = np.mean(filtered[:count*block].reshape(count, block, 2)**2, axis=(1, 2))
        rms = np.sqrt(power)
        levels = 10*np.log10(np.maximum(power, 1e-15))
        result.append({'band_hz': [low, high],
                       'one_tenth_second_rms_dbfs': levels.tolist(),
                       'rms_dbfs': float(10*np.log10(max(float(np.mean(filtered**2)), 1e-15))),
                       'level_p5_p50_p95_dbfs': np.percentile(levels, [5, 50, 95]).tolist(),
                       'envelope_rate_candidates_not_loop_or_speech_detection': modulation_candidates(rms, 10)})
    return result


def line_mask(frequencies, shape, tracks, selected_ids=None):
    """Complementary soft frequency masks around measured candidate tracks."""
    mask = np.zeros(shape, dtype=np.float32)
    sigma = max(6., float(frequencies[1]-frequencies[0])*2)
    for track in tracks:
        if selected_ids is not None and track['id'] not in selected_ids:
            continue
        frames = np.array(track['frames'])
        fade = np.minimum(1., np.minimum(np.arange(len(frames))+1, np.arange(len(frames), 0, -1))/4)
        values = np.exp(-.5*((frequencies[:, None]-np.array(track['hz'])[None, :])/sigma)**2)*fade
        mask[:, frames] = np.maximum(mask[:, frames], values)
    return mask


def reconstruct(z, mask, length):
    _, x = signal.istft(z*mask[None, :, :], RATE, nperseg=FFT,
                         noverlap=FFT-HOP, boundary=True)
    return x.T[:length].astype(np.float32)


def encode(audio, path):
    args = [imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-f', 'f32le',
            '-ar', str(RATE), '-ac', '2', '-i', 'pipe:0', '-c:a', 'libmp3lame',
            '-b:a', '128k', '-n', str(path)]
    subprocess.run(args, input=audio.astype('<f4').tobytes(), capture_output=True, check=True)
    raw = subprocess.check_output([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error',
                                   '-i', str(path), '-ar', str(RATE), '-ac', '2', '-f', 'f32le', 'pipe:1'])
    decoded = np.frombuffer(raw, '<f4').reshape(-1, 2)
    check = {'file': path.name, 'decoded_seconds': len(decoded)/RATE,
             'finite': bool(np.isfinite(decoded).all()),
             'sample_peak': float(np.max(np.abs(decoded))),
             'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    if not check['finite'] or check['sample_peak'] >= 1 or abs(len(decoded)-len(audio)) > RATE*.05:
        raise ValueError(f'Encoded audio failed validation: {check}')
    return check


def analyse(source, output, start, seconds, low, high):
    if not source.is_file():
        raise ValueError('Choose an existing local audio/video file.')
    if output.exists() and any(output.iterdir()):
        raise ValueError('Choose a new or empty output directory.')
    if start < 0 or not 8 <= seconds <= 600 or not 20 <= low < high <= 7500:
        raise ValueError('Need start >= 0, duration 8–600 seconds, and 20 <= low < high <= 7500 Hz.')
    command = [imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-i', str(source),
               '-ss', str(start), '-t', str(seconds), '-map', '0:a:0',
               '-ar', str(RATE), '-ac', '2', '-f', 'f32le', 'pipe:1']
    audio = np.frombuffer(subprocess.check_output(command), '<f4').reshape(-1, 2)
    if len(audio) < 8*RATE or not np.isfinite(audio).all():
        raise ValueError('The selected region needs at least eight seconds of finite decoded audio.')
    output.mkdir(parents=True, exist_ok=True)
    print('Measuring spectral peaks and their continuity...', flush=True)
    frequencies, times, z, power = spectrum(audio)
    tracks, contrast = tone_candidates(frequencies, times, power, low, high)
    # Keep all accepted candidates in JSON; filter only the eight strongest,
    # avoiding a claim that all tonal material or one real source was isolated.
    chosen = [track['id'] for track in tracks[:8]]
    mask = line_mask(frequencies, power.shape, tracks[:8])
    lines = reconstruct(z, mask, len(audio))
    reduced = reconstruct(z, 1-mask, len(audio))
    error = float(np.max(np.abs(lines+reduced-audio)))
    if error > 2e-6:
        raise ValueError(f'Complementary filters did not reconstruct the source: {error}')
    band = signal.sosfiltfilt(signal.butter(4, [250, 3500], fs=RATE,
                            btype='bandpass', output='sos'), audio, axis=0).astype(np.float32)
    variants = [('original', 'Original', audio), ('tracked-lines', 'Candidate narrow tones', lines),
                ('lines-reduced', 'Candidate tones reduced', reduced),
                ('radio-band', '250–3500 Hz inspection band', band)]
    clips, checks = [], []
    for key, label, samples in variants:
        name = f'{key}.mp3'
        checks.append(encode(samples, output/name))
        clip = {'id': key, 'label': label, 'file': name, 'gain_db': 0}
        if key != 'original':
            gain = max(0., min(12., 20*np.log10(.8/max(float(np.abs(samples).max()), 1e-12))))
            boosted = f'{key}-inspection-boost.mp3'
            checks.append(encode(samples*10**(gain/20), output/boosted))
            clip.update({'boosted_file': boosted, 'inspection_gain_db': float(gain)})
        clips.append(clip)
    envelopes = band_envelopes(audio)
    last_valid_frame = int(np.flatnonzero(times <= len(audio)/RATE)[-1])
    columns = np.linspace(0, last_valid_frame, min(last_valid_frame+1, 1200)).astype(int)
    view_hz = np.geomspace(40, 7500, 300)
    view_rows = np.clip(np.round(view_hz/(frequencies[1]-frequencies[0])).astype(int), 0, len(frequencies)-1)
    view = 10*np.log10(np.maximum(power[view_rows[:, None], columns[None, :]], 1e-20))
    upper = float(np.percentile(view, 99.5))
    pixels = np.clip((view-(upper-65))*255/65, 0, 255).astype(np.uint8)
    report = {
        'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'source': str(source.resolve()), 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'start_seconds_in_recording': start, 'decoded_seconds': len(audio)/RATE,
        'method': {'sample_rate_hz': RATE, 'fft_size': FFT, 'hop_samples': HOP,
                   'frequency_bin_hz': RATE/FFT, 'time_step_seconds': HOP/RATE,
                   'local_contrast_threshold_db': MIN_CONTRAST, 'contrast_median_width_bins': 65,
                   'minimum_candidate_seconds': MIN_TRACK_SECONDS, 'search_band_hz': [low, high],
                   'track_linking': 'greedy nearest eligible previous-frame peak; no gaps',
                   'filtered_candidate_ids': chosen,
                   'envelope_candidate_screen': '6+ cycles, prominence >=6 dB, near-peak power fraction >=.2; three disjoint-section sinusoid fits with phase coherence >=.9, each variance ratio >=.3 and amplitude/mean >=.08; heuristic only',
                   'filter_width_sigma_hz': max(6., RATE/FFT*2),
                   'maximum_complementary_reconstruction_error': error},
        'limitations': [
            'Candidate spectral ridges are not verified sound sources or fundamental pitch estimates.',
            'Musical notes/partials and non-musical tones can both appear in the tracks.',
            'Nearby tones can swap identities; ridge fragments do not prove whole sound-event duration.',
            'A moving noise filter can sound pitch-like without producing a retained narrow ridge.',
            'Band filtering does not isolate or prove speech, radio static or chatter; no transcription is attempted.',
            'Envelope rates are candidate level rhythms, not proof of repeated audio, syllables or an intentional oscillator.',
            'Same-gain filters preserve the source gain; boosted versions are inspection aids with disclosed gains.',
            '16 kHz analysis limits bandwidth to 8 kHz; only the selected recording window is analysed.',
            'Assistant has not listened. User sound descriptions are listening evidence, not verified physical provenance.',
        ],
        'tracks': tracks, 'band_envelopes': envelopes, 'clips': clips,
        'encoded_clip_validation': checks,
        'spectrogram': {'rows': len(view_hz), 'columns': len(columns),
                        'low_hz': 40, 'high_hz': 7500, 'range_db': 65,
                        'top_db_relative_to_stft_scaling': upper,
                        'pixels_base64': base64.b64encode(pixels.tobytes()).decode()},
        'references': ['https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.stft.html',
                       'https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html',
                       'https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.welch.html'],
    }
    (output/'analysis.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n', encoding='utf-8', newline='\n')
    template = Path(__file__).with_name('radio_texture_report.html').read_text(encoding='utf-8')
    embedded = json.dumps(report, separators=(',', ':'), allow_nan=False).replace('<', '\\u003c')
    (output/'inspect.html').write_text(template.replace('/*__REPORT__*/', embedded), encoding='utf-8', newline='\n')
    print(json.dumps({'report': str((output/'inspect.html').resolve()),
                      'retained_candidate_tracks': len(tracks), 'filtered_candidate_ids': chosen,
                      'reconstruction_error': error,
                      'longest_candidates': [{key: t[key] for key in ['id', 'start_seconds', 'end_seconds',
                          'frequency_p5_p50_p95_hz', 'level_p5_p95_span_db']} for t in tracks[:8]]}, indent=2))
    return output/'inspect.html'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', nargs='?', type=Path, help='Local audio/video; omit for file picker')
    parser.add_argument('--start', type=float, default=0, help='Seconds into the local recording')
    parser.add_argument('--seconds', type=float, default=60, help='Window length, 8–600 seconds')
    parser.add_argument('--low-hz', type=float, default=80)
    parser.add_argument('--high-hz', type=float, default=3500)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--open', action='store_true')
    args = parser.parse_args()
    if args.source is None:
        import tkinter as tk
        from tkinter.filedialog import askopenfilename
        from tkinter.simpledialog import askfloat
        root = tk.Tk()
        root.withdraw()
        choice = askopenfilename(title='Choose audio or video to inspect')
        if not choice:
            return
        args.source = Path(choice)
        start = askfloat('Recording region', 'Start time in seconds:', initialvalue=args.start, minvalue=0)
        if start is None:
            return
        seconds = askfloat('Recording region', 'Duration in seconds (8–600):', initialvalue=args.seconds, minvalue=8, maxvalue=600)
        root.destroy()
        if seconds is None:
            return
        args.start, args.seconds = start, seconds
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    output = args.out or Path(__file__).resolve().parents[1]/'exports/reference-analysis'/f'radio-texture-{stamp}'
    report = analyse(args.source, output, args.start, args.seconds, args.low_hz, args.high_hz)
    if args.open:
        webbrowser.open(report.resolve().as_uri())


if __name__ == '__main__':
    main()
