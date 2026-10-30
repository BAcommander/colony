"""Signal-level regression checks using known audio, not perceptual assertions."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np
import imageio_ffmpeg

spec = importlib.util.spec_from_file_location('ambient_analysis', Path(__file__).with_name('analyze_ambient_audio.py'))
audio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audio)


class SignalTests(unittest.TestCase):
    def test_opposite_stereo_does_not_cancel_spectral_analysis(self):
        t = np.arange(48000) / 48000
        tone = .1 * np.sin(2 * np.pi * 440 * t)
        f = audio.block_features(np.column_stack([tone, -tone]))
        self.assertGreater(f['bands'][2] / f['bands'].sum(), .95)
        self.assertAlmostEqual(f['cross'] / np.sqrt(f['left'] * f['right']), -1)
        self.assertAlmostEqual(f['side'] / (f['side'] + f['mid']), 1)
        self.assertAlmostEqual(audio.db(f['energy'] / 96000), -23.0103, places=3)

    def test_recurrence_finds_known_32_second_pattern(self):
        rng = np.random.default_rng(15)
        pattern = rng.uniform(.05, 1, (32, 6))
        candidates = audio.recurrence(np.tile(pattern, (6, 1)))
        self.assertIn(32, [c['lag_seconds'] for c in candidates])
        self.assertEqual(audio.recurrence(np.ones((180, 6))), [])

    def test_waveform_checks_confirm_real_repeat_and_reject_wrong_lag(self):
        rng = np.random.default_rng(7)
        pattern = rng.normal(0, .03, (40 * 8000, 2))
        samples = np.tile(pattern, (4, 1))
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'known-repeat.wav'
            with wave.open(str(target), 'wb') as wav:
                wav.setparams((2, 2, 8000, 0, 'NONE', 'not compressed'))
                wav.writeframes((samples * 32767).astype('<i2').tobytes())
            candidates = [{'lag_seconds': 40}, {'lag_seconds': 53}]
            audio.waveform_checks(target, imageio_ffmpeg.get_ffmpeg_exe(), candidates, 160)
            self.assertEqual(len(candidates[0]['waveform_checks']), 3)
            for check in candidates[0]['waveform_checks']:
                self.assertGreater(check['waveform_correlation'], .999)
                self.assertAlmostEqual(check['matched_lag_seconds'], 40, places=3)
            for check in candidates[1]['waveform_checks']:
                self.assertLess(check['waveform_correlation'], .1)

    def test_decode_partial_tail_mono_and_silence(self):
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for silent in [False, True]:
                target = root / ('silent.wav' if silent else 'tone.wav')
                t = np.arange(60000) / 48000
                x = np.zeros_like(t) if silent else .1 * np.sin(2 * np.pi * 997 * t)
                with wave.open(str(target), 'wb') as wav:
                    wav.setparams((1, 2, 48000, 0, 'NONE', 'not compressed'))
                    wav.writeframes((x * 32767).astype('<i2').tobytes())
                result = audio.scan_audio(target, ffmpeg, root)
                self.assertAlmostEqual(result['decoded_duration_seconds'], 1.25)
                self.assertEqual(len(result['timeline']), 2)
                self.assertAlmostEqual(result['timeline'][-1]['duration_seconds'], .25)
                if silent:
                    self.assertIsNone(result['stereo_correlation'])
                    self.assertEqual(result['recurrence_candidates'], [])
                else:
                    self.assertAlmostEqual(result['stereo_correlation'], 1)
                    self.assertAlmostEqual(result['side_energy_percent'], 0)
                    l = audio.loudness(target, ffmpeg, root)
                    self.assertAlmostEqual(l['true_peak_dbtp'], -20, delta=.2)
                    output = root / 'cli-report'
                    process = subprocess.run([sys.executable, str(Path(audio.__file__)), str(target), '--out', str(output)], capture_output=True)
                    self.assertEqual(process.returncode, 0, process.stderr.decode(errors='replace'))
                    report = json.loads((output / 'analysis.json').read_text(encoding='utf-8'))
                    self.assertAlmostEqual(report['measurements']['decoded_duration_seconds'], 1.25)
                    self.assertNotIn('__REPORT_JSON__', (output / 'report.html').read_text(encoding='utf-8'))
                    process = subprocess.run([sys.executable, str(Path(audio.__file__)), str(target), '--out', str(output)], capture_output=True)
                    self.assertNotEqual(process.returncode, 0, 'Must preserve earlier reports')


if __name__ == '__main__':
    unittest.main()
