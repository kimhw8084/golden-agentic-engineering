import sys
import unittest
from pathlib import Path

MANUFACTURING = Path(__file__).resolve().parents[1] / "examples" / "scenarios" / "manufacturing"
sys.path.insert(0, str(MANUFACTURING))

from sampling_accuracy_lab import (  # noqa: E402
    EVALUATION_DAYS,
    TRAIN_DAYS,
    conformal_seasonal_interval,
    forecast_arrivals_from_training,
    forecast_seasonal_naive,
    forecast_tabular_ridge,
    run_lab,
    simulate_poisson,
    synthetic_daily_counts,
    synthetic_orders,
)


class SyntheticSamplingAccuracyLabTests(unittest.TestCase):
    def test_lab_compares_requested_method_families_with_frozen_holdout(self):
        result = run_lab()
        self.assertEqual(result["qualification"], "SYNTHETIC_METHOD_COMPARISON_ONLY")
        self.assertFalse(result["real_world_accuracy_claim"])
        self.assertEqual(result["split"], {
            "training_days": TRAIN_DAYS,
            "held_out_days": EVALUATION_DAYS,
            "future_rows_used_for_fit": 0,
        })
        self.assertTrue(result["deterministic_sampling_rule"]["matches_expected"])
        self.assertEqual(result["arrival_time_empirical_lead"]["metrics"]["observations"], EVALUATION_DAYS)
        self.assertEqual(result["tabular_ml_ridge"]["metrics"]["observations"], EVALUATION_DAYS)
        self.assertEqual(result["forecast_seasonal_naive"]["metrics"]["observations"], EVALUATION_DAYS)
        self.assertEqual(result["discrete_poisson_simulation"]["metrics"]["observations"], EVALUATION_DAYS)
        self.assertEqual(result["conformal_uncertainty"]["calibration_rows"], TRAIN_DAYS - 7)

    def test_forecasts_use_only_training_rows_and_repeat_deterministically(self):
        training = synthetic_daily_counts()[:TRAIN_DAYS]
        first = forecast_tabular_ridge(training, EVALUATION_DAYS)
        second = forecast_tabular_ridge(training, EVALUATION_DAYS)
        self.assertEqual(first, second)
        self.assertEqual(len(forecast_seasonal_naive(training, EVALUATION_DAYS)), EVALUATION_DAYS)
        self.assertEqual(simulate_poisson(training, EVALUATION_DAYS), simulate_poisson(training, EVALUATION_DAYS))
        self.assertEqual(conformal_seasonal_interval(training, EVALUATION_DAYS), conformal_seasonal_interval(training, EVALUATION_DAYS))

    def test_arrival_model_uses_completed_pre_cutoff_orders_only(self):
        cutoff = TRAIN_DAYS
        known = [row for row in synthetic_orders() if row["order_day"] + row["lead_days"] < cutoff]
        forecast = forecast_arrivals_from_training(known, cutoff, EVALUATION_DAYS)
        self.assertEqual(len(forecast), EVALUATION_DAYS)
        self.assertTrue(all(value >= 0 for value in forecast))
        with self.assertRaisesRegex(ValueError, "Training orders"):
            forecast_arrivals_from_training([], cutoff, EVALUATION_DAYS)


if __name__ == "__main__":
    unittest.main()
