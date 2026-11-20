# Fastest credible implementation sequence

**Goal:** Minimize requests/tokens, new services, maintenance and repeated setup while preserving reproducible test quality. No calendar-time guarantees are made. Treat each stage as a shippable qualification checkpoint, not a permission to deploy.

| Stage | Deliverable | Work done by | Gate to advance |
|---|---|---|---|
| 0 | Actual company OpenCode agent/skill/MCP capabilities, OS, Git/CI and OSS inventory | Internal OpenCode + owner | Evidence of version syntax, capability availability/permissions, approved runtime, no guessing |
| 1 | Golden pilot repo plus local Golden Control overview | Internal OpenCode | Python stdlib tests PASS; UI shows source-of-truth and honest unknown states; exact Golden root/version documented |
| 2 | One real React app + one NiceGUI/existing app adopt pinned Golden rules | App owners + OpenCode | Agentic-first workflow exercised and compared with relevant CLI options; fast checks measured; no per-edit approvals |
| 3 | Qualify minimal actual OSS tool winners | Company software clearance + owners | License/deps/binaries/security and offline runs proven per Windows/Linux |
| 4 | Wire company CI to same Golden rule catalog | Existing CI engineer | Full per-rule evidence, status distinction, existing company exception procedure |
| 5 | Implement missing rule coverage from 151 proposal requirements | Rule owners + verifier | Each mandatory rule maps to actual deterministic test or explicit NOT_RUN |
| 6 | Documentation/diagram/benchmark workflows + no-AI drills | Domain owners | Editable docs + executed outputs, offline/runtimes tested |
| 7 | Golden lead-approved v1 release, two-engineer pilot | Team lead and two pilot engineers | Real new/existing app, independently graded tests, measurable speed and quality |
| 8 | Team-wide Golden Control using the existing company platform | Existing platform owner + Golden lead | Approved identity, read-only installation/release adapters, optional aggregate usage view from the existing platform, rollback evidence; no Golden-side collector, app registry or observability store |

## Tool selection discipline

For the initial pilot, inventory approved OpenCode agents, skills, connected MCP servers/tools, and relevant orchestration features once for the verified runtime/config/permission baseline. Reuse that baseline for routine work until one of those inputs changes; do not repeat the full inventory per task. Exercise the best-fit agentic workflow on a representative task before comparing a CLI that is a plausible alternative for the same operation. Qualify **one winner per evaluated capability**, then compose the strongest agentic, MCP, and CLI parts into a hybrid where useful. A CLI is preferred for an operation only when evidence shows it wins that operation. The 63-source catalog is not a mandate to install 63 tools and does not describe the full agentic capability set. Candidate examples by function:

- Repository inspection: ripgrep, scc, ast-grep; one chosen structural approach.
- Python: Ruff, real app's existing pytest/unittest; optionally uv if approved.
- TypeScript: existing project tsc plus Vitest and Playwright with complete browser binaries.
- Policy: initial built-in rules; Conftest/OPA only when a real rule is difficult to express safely otherwise.
- Docs/diagrams: Typst + a single documentation framework + Mermaid/D2 as required.
- Data: DuckDB/Polars, then PyOD/ruptures/Drain3 only after proven real use cases.
- Supply chain: SBOM and secret detection, vulnerability scanner only with locally refreshed vulnerability DB.
- MCP: discover approved internal connections as part of initial capability selection; exercise task-relevant tools and compare the equivalent shell/SDK operation. Leave unqualified servers disabled.

## What to measure, separately

- Time from task start to independently accepted functioning outcome, including rework.
- Developer OpenCode requests/tokens and human interventions.
- Error count and escaped defects, test/recovery outcomes.
- Human task-success and UI usability in actual apps.
- CPU/RAM/latency for tools and applications under representative load.
- Cost of future maintenance, adoption, offline recovery.

No overall weighted score. A faster unsafe change is not a successful release; excessive verification overhead is not an acceptable productivity architecture.

## Self-service learning

Beginner uses `/golden-build` (primary-agent routing with only relevant skills and known integrations). Expert invokes relevant agents, skills, and approved MCP tools directly, then uses CLI for operations where it provides the best evidence or outcome. Both use the same pinned standards and skip repeated inventories/benchmarks on routine work. Independence is graded by independently completed real apps and reproducible acceptance, not watching tutorials.

## Stop conditions

Missing company authorization, unqualified external dependencies, unsupported internal OpenCode config, inability to reproduce applicable checks, fake non-applicability, or an application that cannot operate if AI/Golden Control is down. The team lead approves Golden tool/standards releases and company production authorization remains distinct.
