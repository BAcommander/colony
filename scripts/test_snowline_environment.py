import unittest
import numpy as np
from build_snowline_environment import make_ventilation, WIND_EVENTS


class EnvironmentTests(unittest.TestCase):
    def test_room_air_headroom_band_and_boundary(self):
        x,record=make_ventilation(seconds=8)
        self.assertEqual(x.shape,(8*48000,2))
        self.assertTrue(np.isfinite(x).all())
        self.assertAlmostEqual(record['actual_rms_dbfs'],-48,places=4)
        self.assertLess(np.abs(x).max(),.1)
        power=np.abs(np.fft.rfft(x,axis=0))**2
        f=np.fft.rfftfreq(len(x),1/48000)
        self.assertLess(power[f<80].sum()/power.sum(),.01)
        self.assertLess(power[f>3000].sum()/power.sum(),.001)
        self.assertLess(record['seam_step'],record['ordinary_step_p99']*3)

    def test_wind_has_guarded_edges_and_separate_slow_passages(self):
        for left,right in zip(WIND_EVENTS,WIND_EVENTS[1:]):
            self.assertGreater(right[0]-(left[0]+left[1]),20)
        self.assertGreater(WIND_EVENTS[0][0],20)
        self.assertLess(WIND_EVENTS[-1][0]+WIND_EVENTS[-1][1],520)
        for start,duration,up,down,phase in WIND_EVENTS:
            self.assertLess(up+down,duration)
            self.assertGreater(phase,0)


if __name__=='__main__':unittest.main()
