# Pre-qualification implementation notes — 2026-11-20

**Version:** `v0.1.0-dev`

**State:** `PRE_QUALIFICATION`; this is not a company-qualified Golden release.

**Repository:** public GitHub source; visibility was not changed. No company secrets or proprietary implementation details were added.

## Implemented

- Preserved the 107 provisional decisions, 151 proposed requirements, 19 pilot rule descriptors, 64 source-catalog leads, and existing `.opencode` asset structure. The repository has 5 agents, 12 skills, and 7 commands.
- Added an executable OpenCode-native `/golden-route` command and an offline route resolver. It validates skill, agent, configured MCP, and candidate references before returning one task path; candidate MCPs remain disconnected and unapproved.
- Replayed Proof reports against the project and tightened route schemas, installer path checks, and symlink-safe rollback. Added synthetic fab sampling correctness tests for event deduplication, route/rework visits, observation cutoffs, horizons, and complete daily history.
- Added 12 machine-readable task routes and a pinned public capability selection registry with per-task decisions, exact source commits, license evidence, dependencies/platform/network/context/permission review status, and explicit unknowns. The research covers agent skills, OpenCode plugins, frameworks, MCP servers and tools, browser options, evaluation, and deterministic CLIs. Candidate entries are not company approvals or measured performance winners.
- Strengthened Golden Proof applicability, command provenance/allowlisting, evidence output minimization, manifest validation, and release blockers. Missing mandatory checks remain `NOT_RUN` or `DEFERRED`; report structure does not authenticate a producer.
- Added source-only offline packaging with hidden files, per-file digests, deterministic archive metadata, path checks, and an external archive checksum. It refuses a dirty checkout and does not claim to contain executable offline dependencies.
- Added the non-destructive company doctor and reviewed add-only apply/rollback path. It does not execute version commands, change OpenCode provider/model/auth settings, or make network calls. Compatibility, Windows/Linux behavior, company asset approval, and OS egress enforcement remain unqualified.
- Added a disabled synthetic stdio MCP fixture and contract cases; its direct-handler cancellation/timeout cases do not establish SDK or internal OpenCode conformance.
- Added synthetic React, NiceGUI logic, API/SQLite, and incident fixtures. React dependencies and browsers are not staged; NiceGUI UI runtime is not launched.
- Expanded the read-only Golden Control prototype with local task-routing status and honest installation/update/evidence limitations. It does not collect usage or invocation traces.
- Kept the semiconductor sampling transfer kit generic and source-only. It contains no private dataset or company-specific schema.

## Verification

See [`../BUILD_VERIFICATION.md`](../BUILD_VERIFICATION.md) for commands, test counts, generated evidence, and blockers. The available Python suite passes. The full synthetic-project Golden check intentionally remains non-qualified. React scripts could not run because their local dependencies are absent. Windows/Linux, internal OpenCode/model, MCP trace, company network controls, third-party dependency approval, and performance comparisons remain `NOT_RUN` or blocked.

## Release limits

Do not label this build company-qualified, fully offline-executable, or production-ready. The team lead and company security/OSS owners must complete the internal checks and approve any later release. The public repository must remain free of company secrets and proprietary details.
