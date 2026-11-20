---
name: golden-feedback
description: Close usage-driven feedback loop without adding app analytics storage to Golden Control
---

# Improvement loop

The existing team platform owns app analytics/error aggregation and any approved instrumentation. Golden Control may read minimal aggregate metrics and optional explicit feedback summaries from that platform; Golden must not create an event collector or persist person-level activity. Golden receives only approved standards/tooling-relevant summaries.

Review by recurrence, task impact, reproducibility, and performance regression. Team lead decides priorities. Owner instructs OpenCode to implement, execute deterministic regression and UX tests, then release through existing company controls. Measure change against baseline; do not optimize only for click counts.
