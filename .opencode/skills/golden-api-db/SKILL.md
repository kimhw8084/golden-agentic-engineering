---
name: golden-api-db
description: Implement resilient Python FastAPI backend, SQLite persistence, API and messaging contracts
---

# APIs, databases and jobs

1. Confirm company FastAPI deployment capacity; prefer existing company-hosted approved services and do not publish new FastAPI apps without deployment capacity.
2. Use typed schemas, input validation, clear authorization boundaries, documented error response contracts, stable API evolution and idempotency for retried operations.
3. Begin with SQLite when suitable; evaluate actual concurrency patterns, cross-host access, backup/recovery, durability, data volume and support before choosing another DB. Evidence, not intuition, drives escalation.
4. For queues/schedulers/notifications use existing company services first; handle retries, duplicates, cancellation, delivery status and partial failure.
5. Use instrumentation conventions: ownership, trace/correlation IDs, metrics and structured logs, with secrets redacted.
6. Test migrations/recovery, API edge cases, concurrency and authorization with deterministic tools before release.
