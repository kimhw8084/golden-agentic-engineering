# Fastest credible implementation sequence

**Goal:** Minimize requests/tokens, new services, maintenance and repeated setup while preserving reproducible test quality. No calendar-time guarantees are made. Treat each stage as a shippable qualification checkpoint, not a permission to deploy.

| Stage | Deliverable | Work done by | Gate to advance |
|---|---|---|---|
| 0 | Actual company OpenCode, OS, Git/CI and OSS inventory | Internal OpenCode + owner | Evidence of version syntax/approved runtime, no guessing |
| 1 | Golden pilot repo imported with versions and tests | Internal OpenCode | Python stdlib tests PASS; exact Golden root/version documented |
| 2 | One real React app + one NiceGUI/existing app adopt pinned Golden rules | App owners + OpenCode | Direct development works, fast checks measured, no per-edit approvals |
| 3 | Qualify minimal actual OSS tool winners | Company software clearance + owners | License/deps/binaries/security and offline runs proven per Windows/Linux |
| 4 | Wire company CI to same Golden rule catalog | Existing CI engineer | Full per-rule evidence, status distinction, existing company exception procedure |
| 5 | Implement missing rule coverage from 151 proposal requirements | Rule owners + verifier | Each mandatory rule maps to actual deterministic test or explicit NOT_RUN |
| 6 | Documentation/diagram/benchmark workflows + no-AI drills | Domain owners | Editable docs + executed outputs, offline/runtimes tested |
| 7 | Golden lead-approved v1 release, two-engineer pilot | Team lead and two pilot engineers | Real new/existing app, independently graded tests, measurable speed and quality |
| 8 | Optional Golden Control lightweight standards UI | Only if measured need | Zero app hosting/registry/compliance ownership, no new runtime dependency |

## Tool selection discipline

Start from tools already approved. Then qualify **one winner per function** and add specialized candidates only when pilot tasks require them. The 63-source catalog is not a mandate to install 63 tools. Candidate examples by function:

- Repository inspection: ripgrep, scc, ast-grep; one chosen structural approach.
- Python: Ruff, real app's existing pytest/unittest; optionally uv if approved.
- TypeScript: existing project tsc plus Vitest and Playwright with complete browser binaries.
- Policy: initial built-in rules; Conftest/OPA only when a real rule is difficult to express safely otherwise.
- Docs/diagrams: Typst + a single documentation framework + Mermaid/D2 as required.
- Data: DuckDB/Polars, then PyOD/ruptures/Drain3 only after proven real use cases.
- Supply chain: SBOM and secret detection, vulnerability scanner only with locally refreshed vulnerability DB.
- MCP: no default. Enable approved internal connection when shell/SDK is materially worse.

## What to measure, separately

- Time from task start to independently accepted functioning outcome, including rework.
- Developer OpenCode requests/tokens and human interventions.
- Error count and escaped defects, test/recovery outcomes.
- Human task-success and UI usability in actual apps.
- CPU/RAM/latency for tools and applications under representative load.
- Cost of future maintenance, adoption, offline recovery.

No overall weighted score. A faster unsafe change is not a successful release; excessive verification overhead is not an acceptable productivity architecture.

## Self-service learning

Beginner uses `/golden-build` (guided skill routing). Expert invokes direct commands/skills and tool CLI. Both use same pinned standards. Independence is graded by independently completed real apps and reproducible acceptance, not watching tutorials.

## Stop conditions

Missing company authorization, unqualified external dependencies, unsupported internal OpenCode config, inability to reproduce applicable checks, fake non-applicability, or an application that cannot operate if AI/Golden Control is down. The team lead approves Golden tool/standards releases and company production authorization remains distinct.
