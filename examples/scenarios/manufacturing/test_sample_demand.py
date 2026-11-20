import json
from pathlib import Path
import unittest

from sample_demand import exact_known_wip_demand, naive_future_baseline

FIXTURE = Path(__file__).with_name('events.json')
DATA = json.loads(FIXTURE.read_text(encoding='utf-8'))


class SyntheticSamplingDemandTests(unittest.TestCase):
    def test_exact_rule_dedupes_and_handles_rework_split_hold_scrap_and_horizon_edge(self):
        result = exact_known_wip_demand(DATA['events'], DATA['as_of'], 7)
        self.assertEqual(result['known_wip_sample_count'], 8)
        self.assertEqual(result['eligible_visits'], 4)
        self.assertEqual(result['by_operation'], {'MET-01': 8})
        self.assertEqual(result['excluded'], {
            'observed_after_cutoff': 1,
            'outside_horizon': 4,
            'ineligible_state': 2,
        })

    def test_exact_counts_reconcile_across_horizons(self):
        seven = exact_known_wip_demand(DATA['events'], DATA['as_of'], 7)
        fifteen = exact_known_wip_demand(DATA['events'], DATA['as_of'], 15)
        thirty = exact_known_wip_demand(DATA['events'], DATA['as_of'], 30)
        self.assertEqual(seven['known_wip_sample_count'], 8)
        self.assertEqual(fifteen['known_wip_sample_count'], 11)
        self.assertEqual(thirty['known_wip_sample_count'], 14)
        self.assertLessEqual(seven['known_wip_sample_count'], fifteen['known_wip_sample_count'])
        self.assertLessEqual(fifteen['known_wip_sample_count'], thirty['known_wip_sample_count'])

    def test_future_baseline_uses_only_complete_as_of_days(self):
        result = naive_future_baseline(DATA['daily_history'], DATA['as_of'], 7)
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['observed_sample_count'], 28)
        self.assertEqual(result['daily_rate'], 4.0)
        self.assertEqual(result['future_sample_count_estimate'], 28.0)

    def test_missing_history_is_not_silently_treated_as_zero(self):
        incomplete = [row for row in DATA['daily_history'] if row['sample_date'] != '2026-11-16']
        result = naive_future_baseline(incomplete, DATA['as_of'], 7)
        self.assertEqual(result['status'], 'NOT_RUN')
        self.assertIn('missing is not treated as zero', result['reason'])

    def test_conflicting_duplicate_event_and_naive_time_are_rejected(self):
        altered = list(DATA['events'])
        duplicate = dict(altered[0]); duplicate['event_id'] = 'EV-001'; duplicate['wafer_count'] = 99
        altered.append(duplicate)
        with self.assertRaisesRegex(ValueError, 'conflicting content'):
            exact_known_wip_demand(altered, DATA['as_of'], 7)
        with self.assertRaisesRegex(ValueError, 'UTC offset'):
            exact_known_wip_demand(DATA['events'], '2026-11-20T00:00:00', 7)

    def test_unknown_states_and_invalid_sampling_interval_fail_closed(self):
        invalid_state = dict(DATA['events'][0], event_id='INVALID-STATE', state='UNKNOWN')
        with self.assertRaisesRegex(ValueError, 'Unknown synthetic visit state'):
            exact_known_wip_demand([invalid_state], DATA['as_of'], 7)
        invalid_interval = dict(DATA['events'][0], event_id='INVALID-INTERVAL', sample_every_wafers=0)
        with self.assertRaisesRegex(ValueError, 'positive integers'):
            exact_known_wip_demand([invalid_interval], DATA['as_of'], 7)


if __name__ == '__main__':
    unittest.main()
