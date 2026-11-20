# Holdout-based ROI Scorecard

A candidate is not accepted merely because it runs or improves training-set accuracy. A result is **unverified** unless measured with a frozen, as-of historical test and an adequate number of meaningful independent periods.

## Must-report metrics (each at 7, 15 and 30 days plus optional long-range)

- Historical as-of snapshot completeness, leakage-test pass/fail and exact rule replay discrepancy count.
- Sampled wafers: WAPE (when denominator > 0), MAE, weighted MAE, signed bias, quantile loss.
- Lot/tool/op arrival timestamps: pinball and absolute timing error, censoring calibration and temporal coherence.
- Tool group and fab aggregation: reconciliation violations, missed peaks, under/overprediction frequencies.
- Capacity: throughput, recipe-equivalent metrology hours, utilization and shortage event precision/recall/lead time.
- Uncertainty: 80%/95% empirical coverage, widths, performance under drift.
- Runtime, peak RAM, offline binary size, dependency complexity, licenses, required code changes and failure modes.

## Fair comparisons

1. Frozen existing fab logic (no changes) vs each candidate addition.
2. Models with the same features and the same as-of cutoff before comparing model types.
3. Model with/without new source tables, new timing signals, anomaly features, survival features and simulation.
4. Rolling origin splits, final unseen holdout, multiple operating regimes, no random shuffle.
5. Zero-demand / rare-product / new-operation / rework and hold cases are scored separately.
6. No deployment until output contract is stable, no leakage and no regression on critical tool groups.

## Decision classification

- **ACCEPT**: independent holdout improvement + operational usefulness + reproducible offline + cleared license.
- **CONDITIONAL**: improvement plausible but needs targeted data/risk review.
- **REJECT**: worse holdout, leakage, unjustified dependencies or unsafe offline behavior.
- **REFERENCE ONLY**: useful ideas but unsuitable direct installation.
- **UNTESTED**: required data/runtime unavailable. Never re-label as successful.

Any quoted percentage gain requires measured before/after result with identical data and splits, plus uncertainty. No invented ROI estimates.
