import unittest
import numpy as np
from diagnose_ambient_texture import split_texture, RATE


class TextureTests(unittest.TestCase):
    def test_reconstruction_and_tone_routing(self):
        t=np.arange(3*RATE)/RATE
        x=.1*np.sin(2*np.pi*440*t)
        stereo=np.column_stack([x,-x]).astype(np.float32)
        parts,allocation,_=split_texture(stereo)
        self.assertLess(np.max(np.abs(sum(parts.values())-stereo)),2e-6)
        self.assertGreater(allocation['sustained'],.95)
        self.assertLess(abs(sum(allocation.values())-1),1e-5)
        self.assertTrue(np.allclose(parts['sustained'][:,0],-parts['sustained'][:,1],atol=1e-6))

    def test_noise_routes_to_uncertain_residual_without_source_claim(self):
        x=np.random.default_rng(3).normal(0,.03,(3*RATE,2)).astype(np.float32)
        parts,allocation,flatness=split_texture(x)
        self.assertLess(np.max(np.abs(sum(parts.values())-x)),2e-6)
        self.assertGreater(allocation['residual'],.4)
        self.assertTrue(all(np.isfinite(v).all() for v in parts.values()))
        self.assertGreater(flatness['500-2000Hz'][1],.3)


if __name__=='__main__':unittest.main()
