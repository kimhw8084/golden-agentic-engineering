# Pre-qualification implementation notes — 2026-11-20

**Version:** `v0.1.0-dev`

**State:** `PRE_QUALIFICATION`; this is not a company-qualified Golden release.

**Repository:** public GitHub source; visibility was not changed. No company secrets or proprietary implementation details were added.

## Implemented

- Selected `golden-engineer` as the project default OpenCode primary and made clear small fixes direct, without a mandatory route command or skill.
- Made the nontrivial task route actionable: OpenCode should invoke the route's named skill before choosing implementation tools, then check only relevant visible specialists/MCP and permissions. The route order is machine-readable and tested; small clear fixes remain direct. Company runtime skill invocation is still unverified.
- Added a truthful Golden Control status for the checked-in project default agent, separated from untested company runtime discovery and build compatibility.
- Preserved the 107 provisional decisions, 151 proposed requirements, 19 pilot rule descriptors, 64 source-catalog leads, and existing `.opencode` asset structure. The repository has 5 agents, 12 skills, and 7 commands.
- Added an executable OpenCode-native `/golden-route` command and an offline route resolver. It validates skill, agent, configured MCP, and candidate references before returning one task path; candidate MCPs remain disconnected and unapproved.
- Replayed Proof reports against the project and tightened route schemas, installer path checks, and symlink-safe rollback. Added synthetic fab sampling correctness tests for event deduplication, route/rework visits, observation cutoffs, horizons, and complete daily history.
- Added 12 machine-readable task routes and a pinned public capability selection registry with per-task decisions, exact source commits, license evidence, dependencies/platform/network/context/permission review status, and explicit unknowns. The research covers agent skills, OpenCode plugins, frameworks, MCP servers and tools, browser options, evaluation, and deterministic CLIs. Candidate entries are not company approvals or measured performance winners.
- Strengthened Golden Proof applicability, command provenance/allowlisting, evidence output minimization, manifest validation, and release blockers. Missing mandatory checks remain `NOT_RUN` or `DEFERRED`; report structure does not authenticate a producer.
- Added source-only offline packaging with hidden files, per-file digests, deterministic archive metadata, path checks, and an external archive checksum. It refuses a dirty checkout and does not claim to contain executable offline dependencies.
- Added the non-destructive company doctor and reviewed add-only apply/rollback path. It does not execute version commands, change OpenCode provider/model/auth settings, or make network calls. Compatibility, Windows/Linux behavior, company asset approval, and OS egress enforcement remain unqualified.
- Kept the company handoff to one doctor command and one reviewed apply command on Windows and Linux. Apply revalidates the archive and can create a missing config root after the doctor snapshot and explicit authorization pass; added a fresh-root rollback test.
- Exercised the real synthetic CLI doctor/apply path end to end, including missing-review refusal, config preservation, a fresh-doctor idempotent repeat, and rollback. Normalized config identity across filesystem path aliases after the test exposed a macOS `/var` versus `/private/var` false conflict.
- Updated doctor config discovery to the documented XDG user location on all platforms, added JSONC parsing and safe shape counts, and made simultaneous `.json`/`.jsonc` config files a review blocker.
- Hardened the semiconductor transfer kit: lock paths remain relative to the kit, source verification checks recorded paths and Git origins, and archive creation rejects symlinks and existing outputs. No repositories or wheels were downloaded.
- Made source selection explicit for the fab kit: fetches now require an exact repository list or named stage, and partial transfer archives verify each selected locked clone before packaging. Added nine tests, including a local-Git archive/extract/reverify round trip; no public source repositories or wheels were downloaded.
- Expanded capability research with a pinned ECC OpenCode plugin/hooks candidate. Its repo-level MIT license does not equal component approval; its beta hooks/build, dependency closure, permissions, prompt surface, offline behavior, and performance remain unqualified. The local task-scoped skills remain the current choice.
- Boundedly audited pinned `cathrynlavery/diagram-design` and adapted its semantic-pattern, deletion-first and density methods into the existing offline `golden-docs` skill. The full skill, scripts, templates, fonts and mixed-license icon assets remain unvendored and evaluation-only; no matched diagram-quality/time trial or company approval is claimed.
- Boundedly reviewed pinned `nextlevelbuilder/ui-ux-pro-max-skill` skill and CLI sources; adapted its token-layering idea into existing `golden-react`. The broad upstream package, online update paths, external-provider workflows, data and dependencies remain unvendored and unapproved. Added a typed candidate registry with a standard-library schema validator; no performance comparison or company OSS approval is claimed.
- Added a disabled synthetic stdio MCP fixture and contract cases; its direct-handler cancellation/timeout cases do not establish SDK or internal OpenCode conformance.
- Added synthetic React, NiceGUI logic/UI, API/SQLite, and incident fixtures. The locked React tree was installed from a local npm cache in offline mode and passed typecheck, six component/logic tests, and a Vite build on macOS arm64. NiceGUI's browserless UI simulation and a local manual browser smoke now pass; neither is cross-platform or formal accessibility qualification. Windows/Linux npm caches and browser binaries remain unstaged.
- Extended the local fixture harness with an explicit opt-in NiceGUI UI simulation. It uses only already-installed packages, records their versions and skipped test counts, and fails a requested run when dependencies are missing. React and NiceGUI smokes remain separate from company-runtime benchmarks.
- Connected the NiceGUI project's UI simulation to Golden Proof's `UI-001` allowlisted pytest command; missing pytest/NiceGUI dependencies stay `NOT_RUN`, and pytest plugin autoload/cache are disabled for the check. `UI-002` remains `NOT_RUN` without staged browser assets.
- Corrected the stale React benchmark status and linked local fixture/browser-smoke evidence. Automated Playwright journeys and formal accessibility audits remain unrun.
- Expanded the read-only Golden Control prototype with local task-routing status and honest installation/update/evidence limitations. It does not collect usage or invocation traces.
- Added expandable task-route detail panels for context, deterministic checks, conditional specialists, trust boundaries, no-AI fallback, outputs and MCP policy. A local browser smoke rendered all 12 cards and collapsed detail controls; expansion and company runtime integration remain unverified.
- Closed a Golden Proof scoping gap: profile exclusions now require a bounded, complete repository inventory, and unreadable paths, symlinks, ambiguous web sources or inventory limits keep rules at `NOT_RUN`. Added regression cases for manifest-profile spoofing and incomplete scans; the heuristic does not understand arbitrary application architecture.
- Refined public capability evidence: pinned Promptfoo 0.126.0's release/license and documented offline opt-outs with its upstream warning that they are not a firewall; clarified Grafana MCP query-tool write risk through datasource credentials. Both remain unapproved, unstaged evaluation candidates without a matched company task.
- Tightened the v2 company doctor asset gate: `STAGED` requires explicit per-platform/runtime target records and hashes for target payloads plus the appropriate source-lock/SBOM/license, runtime compatibility, or egress-policy/attempt evidence. OSS approval remains an unauthenticated declaration; the six checked-in asset groups remain `NOT_STAGED`, and Golden still does not enforce the host firewall.
- Kept the semiconductor sampling transfer kit generic and source-only. It contains no private dataset or company-specific schema.

## Verification

See [`../BUILD_VERIFICATION.md`](../BUILD_VERIFICATION.md) for current commands, test counts, generated evidence, and blockers. The full Python suite and offline React fixture pass locally. The full synthetic-project Golden check intentionally remains non-qualified. Windows/Linux, automated browser checks, internal OpenCode/model, authentic MCP trace, company network controls, third-party dependency approval, and performance comparisons remain `NOT_RUN` or blocked.

## Release limits

Do not label this build company-qualified, fully offline-executable, or production-ready. The team lead and company security/OSS owners must complete the internal checks and approve any later release. The public repository must remain free of company secrets and proprietary details.
