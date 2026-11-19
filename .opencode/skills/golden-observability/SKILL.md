---
name: golden-observability
description: Investigate existing Prometheus Grafana Splunk telemetry without building replacement monitoring backends
---

# Observability

Existing Prometheus/Grafana/Splunk perform monitoring/analysis/alerts. The separate internal team React platform supplies the unified display. Golden only defines instrumentation and validation standards.

Read-only analysis by default: health, latency, traffic, errors, database, jobs, logs, dependencies, AI tool operations and manufacturing signals. Confirm permissions per service; no hardcoded tokens.

Correlate evidence with code/config changes; make human confirm root cause, preserve confidence and missing data. Distinguish stale telemetry and upstream outages from zero errors. Plan for no-AI operations and incident replay benchmarking. Do not add a collector or standalone observability backend unless a verified gap justifies it.
