import unittest
import numpy as np
from build_snowline_radio_session import schedule


class SessionScheduleTests(unittest.TestCase):
    def test_unique_deterministic_irregular_schedule_with_guarded_edges(self):
        durations=np.linspace(3.3,6.7,14).tolist()
        events=schedule(durations)
        self.assertEqual(events,schedule(durations))
        self.assertEqual(len({e['voice_index'] for e in events}),14)
        gaps=[]
        for left,right in zip(events,events[1:]):
            end=left['open_seconds']+left['lead_seconds']+left['voice_seconds']+left['tail_seconds']+.08
            self.assertGreater(right['open_seconds']-end,14)
            gaps.append(right['open_seconds']-end)
        self.assertGreater(np.std(gaps),8)
        self.assertGreater(events[0]['open_seconds'],20)
        last=events[-1]
        self.assertLess(last['open_seconds']+last['voice_seconds']+last['lead_seconds']+last['tail_seconds'],520)

    def test_other_seed_changes_event_order(self):
        lengths=[4.]*14
        a,b=schedule(lengths,1),schedule(lengths,2)
        self.assertNotEqual([e['voice_index'] for e in a],[e['voice_index'] for e in b])


if __name__=='__main__':unittest.main()
