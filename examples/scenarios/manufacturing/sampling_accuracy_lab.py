"""Small, deterministic sampling-method comparison using synthetic fixtures only.

The lab uses Python's standard library so it can run without AI, package installs,
or network access. It is a correctness/demo harness, not a fab model or an accuracy
claim. Every forecast is fitted using training rows only; the held-out tail is used
only for scoring.
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Sequence

from sample_demand import exact_known_wip_demand

FIXTURE_PATH = Path(__file__).with_name("events.json")
TRAIN_DAYS = 84
EVALUATION_DAYS = 28
SERIES_DAYS = TRAIN_DAYS + EVALUATION_DAYS
RANDOM_SEED = 20261121


def synthetic_daily_counts(days: int = SERIES_DAYS) -> list[int]:
    """Generate a fixed series with weekly seasonality, trend, and small variation."""
    weekday_effect = (0, 2, 1, 3, 0, -1, -2)
    return [
        max(0, 8 + weekday_effect[index % 7] + index // 28 + (index * 11 % 5) - 2)
        for index in range(days)
    ]


def synthetic_orders(days: int = SERIES_DAYS) -> list[dict[str, int]]:
    """Create synthetic placed orders with known eventual arrival lag and demand."""
    return [
        {
            "order_day": day,
            "lead_days": 1 + (day * 5 % 7),
            "demand_units": 1 + (day * 3 % 4),
        }
        for day in range(days)
    ]


def actual_arrivals(orders: Sequence[dict[str, int]], start: int, horizon: int) -> list[int]:
    totals = [0] * horizon
    for order in orders:
        arrival_day = order["order_day"] + order["lead_days"]
        offset = arrival_day - start
        if 0 <= offset < horizon:
            totals[offset] += order["demand_units"]
    return totals


def forecast_arrivals_from_training(
    observed_orders: Sequence[dict[str, int]], start: int, horizon: int
) -> list[float]:
    """Convolve weekday order-rate estimates with an empirical lead-time profile."""
    if not observed_orders or horizon < 1:
        raise ValueError("Training orders and a positive forecast horizon are required.")
    lead_counts = [0] * 8
    weekday_units: list[list[int]] = [[] for _ in range(7)]
    for row in observed_orders:
        lead = row["lead_days"]
        day = row["order_day"]
        units = row["demand_units"]
        if type(lead) is not int or not 1 <= lead <= 7:
            raise ValueError("lead_days must be between 1 and 7.")
        if type(day) is not int or day < 0 or type(units) is not int or units <= 0:
            raise ValueError("Training orders have invalid day or demand units.")
        lead_counts[lead] += 1
        weekday_units[day % 7].append(units)
    total_leads = sum(lead_counts)
    lead_probability = [count / total_leads for count in lead_counts]
    weekday_mean = [
        sum(values) / len(values) if values else sum(row["demand_units"] for row in observed_orders) / len(observed_orders)
        for values in weekday_units
    ]
    predictions = []
    for target_day in range(start, start + horizon):
        expected = 0.0
        for lead in range(1, 8):
            expected += weekday_mean[(target_day - lead) % 7] * lead_probability[lead]
        predictions.append(expected)
    return predictions


def _features(index: int, origin: int) -> list[float]:
    return [1.0, index / max(1, origin), *[1.0 if index % 7 == day else 0.0 for day in range(1, 7)]]


def _solve_ridge(rows: Sequence[Sequence[float]], values: Sequence[float], penalty: float = 1e-6) -> list[float]:
    """Solve the tiny normal equations with pivoted elimination (no dependencies)."""
    width = len(rows[0])
    matrix = [[sum(row[i] * row[j] for row in rows) for j in range(width)] for i in range(width)]
    target = [sum(row[i] * value for row, value in zip(rows, values)) for i in range(width)]
    for i in range(1, width):
        matrix[i][i] += penalty
    for column in range(width):
        pivot = max(range(column, width), key=lambda row: abs(matrix[row][column]))
        if abs(matrix[pivot][column]) < 1e-12:
            raise ValueError("Training design matrix is singular.")
        matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
        target[column], target[pivot] = target[pivot], target[column]
        scale = matrix[column][column]
        matrix[column] = [entry / scale for entry in matrix[column]]
        target[column] /= scale
        for row in range(width):
            if row == column:
                continue
            factor = matrix[row][column]
            matrix[row] = [left - factor * right for left, right in zip(matrix[row], matrix[column])]
            target[row] -= factor * target[column]
    return target


def forecast_seasonal_naive(history: Sequence[int], horizon: int) -> list[float]:
    if len(history) < 7 or horizon < 1:
        raise ValueError("At least seven training rows and a positive horizon are required.")
    return [float(history[-7 + offset % 7]) for offset in range(horizon)]


def forecast_tabular_ridge(history: Sequence[int], horizon: int) -> list[float]:
    """Fit a small ridge regression on trend and weekday features using training only."""
    if len(history) < 14 or horizon < 1:
        raise ValueError("At least fourteen training rows and a positive horizon are required.")
    rows = [_features(index, len(history)) for index in range(len(history))]
    coefficients = _solve_ridge(rows, [float(value) for value in history])
    return [
        max(0.0, sum(a * b for a, b in zip(_features(index, len(history)), coefficients)))
        for index in range(len(history), len(history) + horizon)
    ]


def _poisson(rng: random.Random, mean: float) -> int:
    if mean <= 0:
        return 0
    threshold = math.exp(-mean)
    product = 1.0
    count = 0
    while product > threshold:
        count += 1
        product *= rng.random()
    return count - 1


def simulate_poisson(history: Sequence[int], horizon: int, simulations: int = 1000) -> dict:
    """Return daily Monte Carlo means and central 90% intervals by weekday."""
    if len(history) < 7 or horizon < 1 or simulations < 100:
        raise ValueError("Need seven training rows, a positive horizon, and >=100 simulations.")
    groups = [[value for i, value in enumerate(history) if i % 7 == day] for day in range(7)]
    means = [sum(group) / len(group) for group in groups]
    rng = random.Random(RANDOM_SEED)
    daily = []
    for offset in range(horizon):
        mean = means[(len(history) + offset) % 7]
        draws = sorted(_poisson(rng, mean) for _ in range(simulations))
        daily.append({
            "mean": sum(draws) / simulations,
            "lower_90": float(draws[max(0, math.floor(simulations * 0.05) - 1)]),
            "upper_90": float(draws[min(simulations - 1, math.ceil(simulations * 0.95) - 1)]),
        })
    return {"seed": RANDOM_SEED, "simulations_per_day": simulations, "daily": daily}


def conformal_seasonal_interval(history: Sequence[int], horizon: int, coverage: float = 0.9) -> dict:
    """Calibrate absolute seasonal-naive residuals on training rows only."""
    if len(history) < 14 or horizon < 1 or not 0.5 <= coverage < 1:
        raise ValueError("Need fourteen rows, a positive horizon, and coverage in [0.5, 1).")
    residuals = sorted(abs(history[index] - history[index - 7]) for index in range(7, len(history)))
    rank = min(len(residuals) - 1, math.ceil((len(residuals) + 1) * coverage) - 1)
    radius = residuals[rank]
    center = forecast_seasonal_naive(history, horizon)
    return {
        "coverage_target": coverage,
        "calibration_rows": len(residuals),
        "absolute_residual_radius": radius,
        "daily": [{"lower": max(0.0, value - radius), "upper": value + radius} for value in center],
    }


def _metrics(actual: Sequence[int], predicted: Sequence[float]) -> dict[str, float]:
    if len(actual) != len(predicted) or not actual:
        raise ValueError("Actual and predicted arrays must have the same positive length.")
    errors = [prediction - observed for observed, prediction in zip(actual, predicted)]
    return {
        "mae": round(sum(abs(error) for error in errors) / len(errors), 6),
        "rmse": round(math.sqrt(sum(error * error for error in errors) / len(errors)), 6),
        "observations": len(actual),
    }


def run_lab() -> dict:
    """Evaluate deterministic rules and simple challengers on frozen synthetic splits."""
    series = synthetic_daily_counts()
    train = series[:TRAIN_DAYS]
    actual = series[TRAIN_DAYS:]
    horizon = len(actual)

    seasonal = forecast_seasonal_naive(train, horizon)
    tabular = forecast_tabular_ridge(train, horizon)
    simulation = simulate_poisson(train, horizon)
    uncertainty = conformal_seasonal_interval(train, horizon)

    orders = synthetic_orders()
    known_arrivals = [
        row for row in orders
        if row["order_day"] + row["lead_days"] < TRAIN_DAYS
    ]
    arrival_actual = actual_arrivals(orders, TRAIN_DAYS, EVALUATION_DAYS)
    arrival_prediction = forecast_arrivals_from_training(known_arrivals, TRAIN_DAYS, EVALUATION_DAYS)

    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    exact_rule = exact_known_wip_demand(fixture["events"], fixture["as_of"], 7)
    simulation_daily = simulation["daily"]
    simulation_actual_coverage = sum(
        int(row["lower_90"] <= observed <= row["upper_90"])
        for row, observed in zip(simulation_daily, actual)
    ) / horizon
    interval_daily = uncertainty["daily"]
    conformal_coverage = sum(
        int(row["lower"] <= observed <= row["upper"])
        for row, observed in zip(interval_daily, actual)
    ) / horizon

    return {
        "schema": "golden-synthetic-sampling-lab/v1",
        "qualification": "SYNTHETIC_METHOD_COMPARISON_ONLY",
        "real_world_accuracy_claim": False,
        "dependencies": "Python standard library only; no AI or network required",
        "split": {"training_days": TRAIN_DAYS, "held_out_days": EVALUATION_DAYS, "future_rows_used_for_fit": 0},
        "deterministic_sampling_rule": {
            "status": exact_rule["status"],
            "known_wip_sample_count": exact_rule["known_wip_sample_count"],
            "expected_fixture_count": 8,
            "matches_expected": exact_rule["known_wip_sample_count"] == 8,
            "source": exact_rule["source"],
        },
        "arrival_time_empirical_lead": {
            "training_orders": len(known_arrivals),
            "metrics": _metrics(arrival_actual, arrival_prediction),
            "actual": arrival_actual,
            "predicted": [round(value, 6) for value in arrival_prediction],
        },
        "tabular_ml_ridge": {
            "description": "Standard-library ridge regression using trend and weekday features",
            "metrics": _metrics(actual, tabular),
            "actual": actual,
            "predicted": [round(value, 6) for value in tabular],
        },
        "forecast_seasonal_naive": {
            "description": "Repeat the last observed seven-day profile",
            "metrics": _metrics(actual, seasonal),
            "actual": actual,
            "predicted": [round(value, 6) for value in seasonal],
        },
        "discrete_poisson_simulation": {
            "description": "Seeded weekday-specific Poisson draws; intervals are not calibrated confidence guarantees",
            "metrics": _metrics(actual, [row["mean"] for row in simulation_daily]),
            "interval_coverage_90": round(simulation_actual_coverage, 6),
            "intervals_are_empirical_only": True,
            **simulation,
        },
        "conformal_uncertainty": {
            "description": "Absolute seasonal-naive residual radius calibrated on the training rows",
            "coverage_target": uncertainty["coverage_target"],
            "empirical_heldout_coverage": round(conformal_coverage, 6),
            "intervals_are_empirical_only": True,
            "calibration_rows": uncertainty["calibration_rows"],
            "daily": uncertainty["daily"],
        },
    }


def main() -> int:
    print(json.dumps(run_lab(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
