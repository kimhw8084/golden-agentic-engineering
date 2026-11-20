# Company task comparison protocol

The local fixtures and comparable acceptance commands are listed in [`cases.json`](cases.json). Copy [`record-template.json`](record-template.json) for each actual run. This directory records a **protocol only**; it contains no fabricated performance data and no composite score.

## Current evidence

Python fixtures cover a small fix, NiceGUI sample logic, API/SQLite contract, incident timeline, and synthetic MCP protocol cases. The React fixture is authored but its dependency lock/store and browsers are absent. No company OpenCode runtime or trusted invocation-event source is attached. Therefore every agentic-vs-CLI, plain-vs-Golden, token/request, elapsed-time, and quality-uplift comparison is `BLOCKED_COMPANY_RUNTIME`.

## Trial method

1. Use the same task, input snapshot, and independent acceptance criteria for each strategy. Keep original Golden and refined Golden source revisions fixed.
2. Run plain OpenCode primary first, then the relevant Golden skill/agent/MCP path. Add specialists only when distinct work justifies coordination. Compare a CLI only when it can do the same operation.
3. Record accepted correctness/defects from executable tests and independent human review. Record wall time, human interruptions, rework, p50/p95 only when measured repeatedly, and tokens/requests only from a trusted runtime event source.
4. Do not use model-judged output as an acceptance oracle, add a composite score, infer tool invocation from Markdown, or claim Codex performance as company performance.
5. Preserve failures and blockers. Do not report a winner until the same criteria and runtime setup have been exercised repeatedly enough for the task's variability.

There is no runner for internal OpenCode because this environment cannot access or authenticate that company runtime. Local commands exercise the synthetic artifacts only and establish no Golden-vs-plain uplift.
