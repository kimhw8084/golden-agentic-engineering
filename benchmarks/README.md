# Company task comparison protocol

The local fixtures and comparable acceptance commands are listed in [`cases.json`](cases.json). Run `python benchmarks/run_local_fixtures.py --out verification/local-fixtures.json` for an offline deterministic test harness. Copy [`record-template.json`](record-template.json) for each actual internal-runtime trial. There are no fabricated performance data or composite scores.

## Current evidence

The local harness runs Python fixture tests for a small fix, NiceGUI sample logic, API/SQLite, incident timeline, synthetic fab sampling, MCP protocol cases, and Golden Proof/routing. It records only test counts, process durations, and output hashes; it does not compare agents or claim task productivity. The React fixture is authored but its dependency lock/store is absent, and browser journey tests are blocked on staged Playwright binaries. No company OpenCode runtime or trusted invocation-event source is attached. Therefore every agentic-vs-CLI, plain-vs-Golden, token/request, end-to-end task time, and quality-uplift comparison is `BLOCKED_COMPANY_RUNTIME`.

## Trial method

1. Use the same task, input snapshot, and independent acceptance criteria for each strategy. Keep original Golden and refined Golden source revisions fixed.
2. Run plain OpenCode primary first, then the relevant Golden skill/agent/MCP path. Add specialists only when distinct work justifies coordination. Compare a CLI only when it can do the same operation.
3. Record accepted correctness/defects from executable tests and independent human review. Record wall time, human interruptions, rework, p50/p95 only when measured repeatedly, and tokens/requests only from a trusted runtime event source.
4. Do not use model-judged output as an acceptance oracle, add a composite score, infer tool invocation from Markdown, or claim Codex performance as company performance.
5. Preserve failures and blockers. Do not report a winner until the same criteria and runtime setup have been exercised repeatedly enough for the task's variability.

There is no runner for internal OpenCode because this environment cannot access or authenticate that company runtime. Local commands exercise the synthetic artifacts only and establish no Golden-vs-plain uplift.
