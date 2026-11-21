# Company task comparison protocol

The local fixtures and comparable acceptance commands are listed in [`cases.json`](cases.json). Run `python benchmarks/run_local_fixtures.py --out verification/local-fixtures.json` for Python-only offline checks. Add `--include-nicegui-ui` to run the in-process NiceGUI UI simulation with already-installed NiceGUI and pytest; it performs no install and launches no browser. Add `--include-react` to install the exact lockfile from the local npm cache with offline mode and lifecycle scripts disabled, then run typecheck, component tests and build. Copy [`record-template.json`](record-template.json) for each actual internal-runtime trial. There are no fabricated performance data or composite scores.

## Current evidence

The harness runs Python fixture tests for a small fix, NiceGUI sample logic, API/SQLite, incident timeline, synthetic fab sampling, MCP protocol cases, and Golden Proof/routing. Its optional NiceGUI path runs the UI simulation only when the packages are already installed; its optional React path uses npm's local cache in offline mode. It records test counts, skips, installed UI-test package versions, process durations and output hashes; it does not compare agents or claim task productivity. The current React result is a local macOS arm64 fixture pass, not Windows/Linux offline readiness. Local React and NiceGUI browser smoke observations are linked from [`cases.json`](cases.json); automated Playwright journeys and formal accessibility audits remain unrun because browser binaries are not staged. No company OpenCode runtime or trusted invocation-event source is attached. Therefore every agentic-vs-CLI, plain-vs-Golden, token/request, end-to-end task time, and quality-uplift comparison is `BLOCKED_COMPANY_RUNTIME`.

## Trial method

1. Use the same task, input snapshot, and independent acceptance criteria for each strategy. Keep original Golden and refined Golden source revisions fixed.
2. Run plain OpenCode primary first, then the relevant Golden skill/agent/MCP path. Add specialists only when distinct work justifies coordination. Compare a CLI only when it can do the same operation.
3. Record accepted correctness/defects from executable tests and independent human review. Record wall time, human interruptions, rework, p50/p95 only when measured repeatedly, and tokens/requests only from a trusted runtime event source.
4. Do not use model-judged output as an acceptance oracle, add a composite score, infer tool invocation from Markdown, or claim Codex performance as company performance.
5. Preserve failures and blockers. Do not report a winner until the same criteria and runtime setup have been exercised repeatedly enough for the task's variability.

There is no runner for internal OpenCode because this environment cannot access or authenticate that company runtime. Local commands exercise the synthetic artifacts only and establish no Golden-vs-plain uplift.
