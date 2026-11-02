import unittest

import numpy as np

from analyze_radio_texture import (RATE, band_envelopes, line_mask, reconstruct,
                                   spectrum, tone_candidates)


class RadioTextureTests(unittest.TestCase):
    def measure(self, x):
        f, t, z, p = spectrum(x)
        tracks, _ = tone_candidates(f, t, p, 250, 2000)
        return f, t, z, p, tracks

    def test_rising_and_falling_tone_in_noise(self):
        t = np.arange(18*RATE)/RATE
        expected = 800+180*np.sin(2*np.pi*t/8)
        tone = .06*np.sin(np.cumsum(expected)*2*np.pi/RATE)
        x = np.column_stack([tone, tone])
        x += np.random.default_rng(9).normal(0, .015, x.shape)
        _, times, _, _, tracks = self.measure(x.astype(np.float32))
        self.assertTrue(tracks)
        best = max(tracks, key=lambda tr: tr['duration_seconds'])
        self.assertGreater(best['duration_seconds'], 14)
        target = 800+180*np.sin(2*np.pi*times[best['frames']]/8)
        self.assertLess(np.percentile(np.abs(target-best['hz']), 95), 6)
        self.assertTrue(best['frequency_span_over_four_bins'])

    def test_amplitude_motion_is_not_reported_as_pitch_motion(self):
        t = np.arange(24*RATE)/RATE
        tone = .06*(1+.65*np.sin(2*np.pi*t/4))*np.sin(2*np.pi*700*t)
        x = np.column_stack([tone, -tone]).astype(np.float32)
        f, _, z, p, tracks = self.measure(x)
        best = tracks[0]
        span = best['frequency_p5_p50_p95_hz']
        self.assertLess(span[2]-span[0], 2)
        self.assertFalse(best['frequency_span_over_four_bins'])
        self.assertGreater(best['level_p5_p95_span_db'], 10)
        bands = band_envelopes(x)
        candidates = bands[1]['envelope_rate_candidates_not_loop_or_speech_detection']
        self.assertTrue(any(abs(c['frequency_hz']-.25)<.05 for c in candidates))
        mask = line_mask(f, p.shape, tracks)
        lines, rest = reconstruct(z, mask, len(x)), reconstruct(z, 1-mask, len(x))
        self.assertLess(np.max(np.abs(lines+rest-x)), 2e-6)
        self.assertTrue(np.allclose(lines[:, 0], -lines[:, 1], atol=1e-6))

    def test_broadband_noise_does_not_force_a_continuous_tone(self):
        x = np.random.default_rng(4).normal(0, .03, (15*RATE, 2)).astype(np.float32)
        _, _, _, _, tracks = self.measure(x)
        self.assertEqual(tracks, [])
        for band in band_envelopes(x):
            self.assertEqual(band['envelope_rate_candidates_not_loop_or_speech_detection'], [])


if __name__ == '__main__':
    unittest.main()
