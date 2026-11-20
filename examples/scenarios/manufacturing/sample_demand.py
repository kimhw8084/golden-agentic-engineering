"""Synthetic, offline fab-sampling correctness fixture; contains no fab data."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import json
from typing import Iterable

UTC = timezone.utc
ELIGIBLE_STATES = {'READY', 'QUEUED', 'IN_PROCESS', 'REWORK'}
EXCLUDED_STATES = {'HOLD', 'SCRAPPED', 'CANCELLED'}


def utc_timestamp(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError('Timestamp must be an ISO-8601 string.')
    normalized = value[:-1] + '+00:00' if value.endswith('Z') else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError('Timestamp must include a UTC offset.')
    return parsed.astimezone(UTC)


def _sample_count(row: dict) -> int:
    wafers = row.get('wafer_count')
    interval = row.get('sample_every_wafers')
    if type(wafers) is not int or wafers <= 0 or type(interval) is not int or interval <= 0:
        raise ValueError('wafer_count and sample_every_wafers must be positive integers.')
    return (wafers + interval - 1) // interval


def exact_known_wip_demand(events: Iterable[dict], as_of: str, horizon_days: int) -> dict:
    """Apply an explicit synthetic interval policy to known eligible visits only."""
    cutoff = utc_timestamp(as_of)
    if type(horizon_days) is not int or not 1 <= horizon_days <= 365:
        raise ValueError('horizon_days must be between 1 and 365.')
    end = cutoff + timedelta(days=horizon_days)
    seen_event_ids: dict[str, str] = {}
    visits: dict[tuple[str, str, str, str], tuple[int, str]] = {}
    excluded = {'observed_after_cutoff': 0, 'outside_horizon': 0, 'ineligible_state': 0}

    for row in events:
        if not isinstance(row, dict):
            raise ValueError('Every event must be an object.')
        event_id = row.get('event_id')
        if not isinstance(event_id, str) or not event_id:
            raise ValueError('Every event requires an event_id.')
        canonical = json.dumps(row, sort_keys=True, separators=(',', ':'))
        if event_id in seen_event_ids:
            if seen_event_ids[event_id] != canonical:
                raise ValueError('Duplicate event_id has conflicting content.')
            continue
        seen_event_ids[event_id] = canonical
        observed = utc_timestamp(row.get('observed_at'))
        scheduled = utc_timestamp(row.get('scheduled_at'))
        if observed > cutoff:
            excluded['observed_after_cutoff'] += 1
            continue
        if scheduled <= cutoff or scheduled > end:
            excluded['outside_horizon'] += 1
            continue
        state = row.get('state')
        if state not in ELIGIBLE_STATES:
            if state not in EXCLUDED_STATES:
                raise ValueError('Unknown synthetic visit state.')
            excluded['ineligible_state'] += 1
            continue
        identity = (row.get('lot_id'), row.get('operation'), row.get('route_revision'), row.get('visit_id'))
        if any(not isinstance(value, str) or not value for value in identity):
            raise ValueError('Eligible visits require lot, operation, route revision, and visit IDs.')
        count = _sample_count(row)
        record = (count, canonical)
        if identity in visits:
            if visits[identity][1] != canonical:
                raise ValueError('A repeated visit has conflicting content.')
            continue
        visits[identity] = record

    by_operation: dict[str, int] = {}
    for identity, (count, _) in visits.items():
        operation = identity[1]
        by_operation[operation] = by_operation.get(operation, 0) + count
    return {
        'status': 'PASS',
        'as_of_utc': cutoff.isoformat().replace('+00:00', 'Z'),
        'horizon_days': horizon_days,
        'known_wip_sample_count': sum(count for count, _ in visits.values()),
        'eligible_visits': len(visits),
        'by_operation': dict(sorted(by_operation.items())),
        'excluded': excluded,
        'source': 'SYNTHETIC_FIXED_RULES_ONLY',
    }


def naive_future_baseline(daily_history: Iterable[dict], as_of: str, horizon_days: int,
                          lookback_days: int = 7) -> dict:
    """Return a seasonal-naive count only when every required as-of day is present."""
    cutoff = utc_timestamp(as_of)
    if type(horizon_days) is not int or not 1 <= horizon_days <= 365:
        raise ValueError('horizon_days must be between 1 and 365.')
    if type(lookback_days) is not int or not 1 <= lookback_days <= 90:
        raise ValueError('lookback_days must be between 1 and 90.')
    expected_days = {cutoff.date() - timedelta(days=offset) for offset in range(1, lookback_days + 1)}
    records: dict[date, int] = {}
    for row in daily_history:
        if not isinstance(row, dict):
            raise ValueError('Every history row must be an object.')
        sample_day = date.fromisoformat(row.get('sample_date', ''))
        observed = utc_timestamp(row.get('observed_at'))
        count = row.get('sample_count')
        if type(count) is not int or count < 0:
            raise ValueError('sample_count must be a nonnegative integer.')
        if sample_day >= cutoff.date() or observed > cutoff:
            continue
        if sample_day in records and records[sample_day] != count:
            raise ValueError('A historical day has conflicting counts.')
        records[sample_day] = count
    if set(records) & expected_days != expected_days:
        return {
            'status': 'NOT_RUN',
            'reason': 'Required complete as-of daily history is missing; missing is not treated as zero.',
            'lookback_days': lookback_days,
            'source': 'SYNTHETIC_FIXED_BASELINE_ONLY',
        }
    actual = sum(records[day] for day in expected_days)
    daily_rate = actual / lookback_days
    return {
        'status': 'PASS',
        'as_of_utc': cutoff.isoformat().replace('+00:00', 'Z'),
        'lookback_days': lookback_days,
        'observed_sample_count': actual,
        'daily_rate': daily_rate,
        'horizon_days': horizon_days,
        'future_sample_count_estimate': daily_rate * horizon_days,
        'source': 'SYNTHETIC_SEASONAL_NAIVE_NOT_A_PERFORMANCE_CLAIM',
    }
