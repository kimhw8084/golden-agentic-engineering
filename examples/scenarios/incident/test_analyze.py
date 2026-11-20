import unittest
from pathlib import Path

from analyze import timeline


class IncidentTimelineTests(unittest.TestCase):
    def test_synthetic_events_sort_chronologically(self):
        events = timeline(Path(__file__).with_name('events.jsonl'))
        self.assertEqual(len(events), 4)
        self.assertEqual([event['timestamp'] for event in events], sorted(event['timestamp'] for event in events))
        self.assertEqual(events[1]['event'], 'timeout')


if __name__ == '__main__':
    unittest.main()
