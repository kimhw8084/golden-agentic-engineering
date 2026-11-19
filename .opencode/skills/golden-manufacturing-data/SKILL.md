---
name: golden-manufacturing-data
description: Analyze wafer lot equipment SPC metrology and test data with reproducible statistics
---

# Manufacturing analytics

1. Verify input schemas, units, date/timezone, wafer/lot/die identifiers, provenance, missingness and sampling methods.
2. Prefer approved deterministic tools such as DuckDB/Polars/Pandera. Model may choose an algorithm, but numerical calculations and validation must execute in code.
3. For SPC use established subgroup/control chart assumptions; do not conflate process-control limits and specifications. Clearly label baseline windows and changes.
4. For anomaly/changepoint/log-pattern detection, tools like PyOD/ruptures/Drain3 are candidates only. Evaluate on historical labeled incidents and quantify false alarms, misses and detection delay.
5. No manufacturing process decision, yield adjustment or production mutation without established human workflow.
6. Produce concise, traceable read-only findings with time windows, data scope, and reproducible query/script references.
