---
name: golden-code-audit
description: Audit all Golden rule dimensions with traceable deterministic evidence and candidate remediation
---

# Golden audit

Read the pinned project manifest, then run `python <GOLDEN_HOME>/scripts/golden.py check --fast --project <app>` during development, `--full` for qualification. Local or installed Golden command wrapper is optional.

Interpret statuses exactly:
- PASS: applicable test executed and succeeded
- FAIL: applicable test ran and detected violation
- NOT_APPLICABLE: specific profile/capability evidence justifies exclusion
- NOT_RUN: missing command/tool/environment or incomplete verification; never treat as PASS
- DEFERRED: deliberately skipped during fast evaluation; no release claim

Do not hide missing checks behind average quality scores. Identify source path, reproducible failure, test, severity and proposed repair. Application owners use OpenCode directly for normal code changes; Golden-originated remediation proposals go through existing Git review mechanism. Do not let an audit mutate the application.

Pilot implementation currently **trusts user-declared capabilities**; independent evidence validation and company exception approval are needed for production qualification.
