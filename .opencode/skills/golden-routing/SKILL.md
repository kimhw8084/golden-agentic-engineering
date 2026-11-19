---
name: golden-routing
description: Select minimal agentic orchestration for implementation, audit, planning and independent evaluation
---

# Choose the smallest sufficient agentic pattern

**Direct single-agent** is the default for typical feature, fix and test tasks. One OpenCode engineer reads only the matching skills and runs deterministic tools. Do not spawn a subagent by default.

**Sequential chain** for requirements → implementation → tests → documentation when later steps genuinely depend on completed earlier outputs. Pass only artifacts/paths and acceptance criteria, not entire conversation histories.

**Router** when a request clearly matches React, NiceGUI, Python/API, data analytics, documentation or incident categories. Load only that skill; do not preload all rules.

**Parallel independent exploration** when multiple genuinely separable alternatives need investigation and the cost is justified. No parallel edits to the same file.

**Orchestrator-worker** only for a large multi-module change with defined ownership boundaries and explicit integration tests. No open-ended swarms.

**Evaluator–optimizer** for high-risk, novel or failed work: execute deterministic test, inspect exact failure, repair bounded scope, rerun. Use a fixed iteration budget; do not claim success from a model judge.

Context hierarchy: AGENTS.md = stable universal contract; skill = task-specific procedure; project manifest = profile and capabilities; search/read files = facts for this task; MCP = authorized external system calls; deterministic tool output = test evidence. Minimize token/request count by not re-reading known unmodified files and not copying large log dumps.

Success = demonstrated task outcome, not number of agent calls.
