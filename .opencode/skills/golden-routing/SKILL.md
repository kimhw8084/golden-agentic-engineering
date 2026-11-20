---
name: golden-routing
description: Discover, exercise and compare relevant agents, skills, MCP capabilities and CLI tools for implementation, audit, planning and evaluation
---

# Agentic-first capability selection

Choose tools by evidence, not by a CLI-first default. For each task:

1. Inspect the capabilities actually available in this OpenCode environment: primary/specialist agents, relevant skills, connected and authorized MCP servers/tools, and local deterministic tools.
2. Select and exercise the best-fit agentic workflow first: primary agent + relevant skill, plus a specialist agent or MCP tool when it adds task-relevant capability. Record actual invocations and results; do not claim a capability was used because it exists in a file or catalog.
3. Compare relevant CLI candidates on the same representative task and acceptance criteria. Prefer a CLI for a specific operation when it demonstrably improves correctness, reproducibility, latency, offline operation, or another stated requirement. Use a hybrid when agentic reasoning/service interaction and deterministic execution complement each other.
4. If a relevant agent, skill, or MCP capability is missing, incompatible, unauthorized, or unqualified, record that exact gap and use the best available fallback. Never install or enable an unapproved service to complete the comparison.

The evaluation order is agentic-first; the winner is task-specific. Do not invoke every available capability or create a swarm just to satisfy the order.

**Direct primary agent + relevant skill** is the lightest pattern for typical feature, fix and test tasks. The primary agent still discovers and exercises task-relevant agentic capabilities before selecting implementation tools. A specialist subagent is useful only when its distinct expertise improves the result enough to justify coordination.

**Sequential chain** for requirements → implementation → tests → documentation when later steps genuinely depend on completed earlier outputs. Pass only artifacts/paths and acceptance criteria, not entire conversation histories.

**Router** when a request clearly matches React, NiceGUI, Python/API, data analytics, documentation or incident categories. Load the matching skill and use its agent/MCP capabilities when relevant; do not preload all rules.

**Parallel independent exploration** when multiple genuinely separable alternatives need investigation and the cost is justified. No parallel edits to the same file.

**Orchestrator-worker** only for a large multi-module change with defined ownership boundaries and explicit integration tests. No open-ended swarms.

**Evaluator–optimizer** for high-risk, novel or failed work: execute deterministic test, inspect exact failure, repair bounded scope, rerun. Use a fixed iteration budget; do not claim success from a model judge.

Context hierarchy: AGENTS.md = stable universal contract; skill = task-specific procedure; project manifest = profile and capabilities; search/read files = facts for this task; agents = scoped reasoning; MCP = authorized structured service interaction; CLI = local or deterministic operation when it wins for that operation; deterministic tool output = test evidence. Minimize token/request count by not re-reading known unmodified files and not copying large log dumps.

Success = demonstrated task outcome, not number of agent calls.
