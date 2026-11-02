import unittest
import numpy as np
from generate_receiver_texture import make_receiver


class ReceiverTextureTests(unittest.TestCase):
    def test_deterministic_original_layers_and_carrier_closure(self):
        a, info = make_receiver(11, 13, rate=12000)
        b, _ = make_receiver(11, 13, rate=12000)
        c, _ = make_receiver(11, 14, rate=12000)
        self.assertTrue(all(np.array_equal(a[k], b[k]) for k in a))
        self.assertFalse(np.array_equal(a['static'], c['static']))
        self.assertLess(info['carrier_cycle_closure_error'], 1e-7)
        total = sum(a.values())
        self.assertEqual(total.shape, (132000, 2))
        self.assertTrue(np.isfinite(total).all())
        self.assertLess(np.abs(total).max(), .8)
        step = np.abs(total[0]-total[-1]).max()
        self.assertLess(step, 3*np.percentile(np.abs(np.diff(total, axis=0)), 99))

    def test_static_band_and_independent_activity(self):
        stems, _ = make_receiver(11, 42, rate=16000)
        power = np.abs(np.fft.rfft(stems['static'], axis=0))**2
        f = np.fft.rfftfreq(len(stems['static']), 1/16000)
        self.assertLess(power[f>6000].sum()/power.sum(), .005)
        self.assertGreater(np.std(stems['nonverbal-activity']), 0)
        self.assertGreater(np.corrcoef(stems['static'].T)[0, 1], .9)


if __name__ == '__main__':
    unittest.main()
