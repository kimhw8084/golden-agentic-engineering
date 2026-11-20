---
name: golden-routing
description: Route tasks through the primary agent and relevant skills; evaluate agent, MCP and CLI options when the decision warrants it
---

# Agentic-first capability selection

Choose tools by evidence, not by a CLI-first default, while keeping selection overhead proportional to the task.

## Routine delivery (default)

1. Use the primary OpenCode agent for reasoning, routing, and integration.
2. Load one relevant skill when it materially applies. Reuse the recent runtime/capability baseline; do not re-scan every agent, skill, and MCP connection on every task.
3. Use a task-relevant approved MCP capability when the task needs its structured service access. Add a specialist only when expected quality or time savings exceed coordination cost.
4. Use deterministic CLI checks for reproducible proof. Do not benchmark alternative tools or create an invocation ledger for routine work.

## Capability evaluation (triggered)

Run the fuller comparison when the user asks which tool is fastest/best, an unfamiliar integration is central to the task, the runtime/config/permissions changed, or a release/pilot requires qualification. Inspect only the relevant live capabilities, define acceptance criteria, exercise the strongest suitable agentic path, and compare a CLI only when it is a plausible alternative for that operation. Use a hybrid where it wins. Record actual evidence and its provenance; a catalog entry or model self-report is not proof. If a capability is unavailable, incompatible, unauthorized, or unqualified, state that exact gap and use the best safe fallback. Never enable an unapproved service to complete a comparison.

The primary agentic layer is the default; additional capability discovery and measurement are triggered by actual uncertainty or a decision need. The winner is task-specific. Do not invoke every capability or create a swarm just to satisfy an order.

**Direct primary agent + relevant skill** is the lightest pattern for typical feature, fix and test tasks. A specialist subagent is useful only when its distinct expertise improves the result enough to justify coordination.

**Sequential chain** for requirements → implementation → tests → documentation when later steps genuinely depend on completed earlier outputs. Pass only artifacts/paths and acceptance criteria, not entire conversation histories.

**Router** when a request clearly matches React, NiceGUI, Python/API, data analytics, documentation or incident categories. Load the matching skill and use its agent/MCP capabilities when relevant; do not preload all rules.

**Parallel independent exploration** when multiple genuinely separable alternatives need investigation and the cost is justified. No parallel edits to the same file.

**Orchestrator-worker** only for a large multi-module change with defined ownership boundaries and explicit integration tests. No open-ended swarms.

**Evaluator–optimizer** for high-risk, novel or failed work: execute deterministic test, inspect exact failure, repair bounded scope, rerun. Use a fixed iteration budget; do not claim success from a model judge.

Context hierarchy: AGENTS.md = stable universal contract; skill = task-specific procedure; project manifest = profile and capabilities; search/read files = facts for this task; agents = scoped reasoning; MCP = authorized structured service interaction; CLI = local or deterministic operation when it wins for that operation; deterministic tool output = test evidence. Minimize token/request count by not re-reading known unmodified files and not copying large log dumps.

Success = independently accepted task outcome at appropriate cost, not number of agent calls, tools inspected, or trace rows produced.
