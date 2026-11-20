# Agentic-first tool evaluation

This starter evaluates how the installed company OpenCode can solve real work. It does not assume that AI agents, MCP, or command-line tools are universally best. The discovery order is deliberate: inspect and exercise the agentic capabilities first, then compare tools against the same task.

## Required evaluation order

1. **Define one representative task.** Write observable acceptance criteria and use an authorized fixture or synthetic data. Do not start by listing popular CLIs.
2. **Inventory installed agentic capabilities.** Inspect the actual primary and specialist agents, relevant skills, connected MCP servers/tools, available handoffs/orchestration features, and their permission scopes. A file in this repository or an upstream catalog is not proof the capability is installed or usable.
3. **Exercise the strongest suitable agentic workflow.** Use the primary agent with the relevant skill. Add a specialist agent when separate expertise materially helps; use a connected, approved MCP tool when the task needs that structured service capability. Capture actual calls and results. Do not replace an available, relevant agentic capability with a CLI list or an untested suggestion.
4. **Compare relevant CLI workflows on the same task.** Use the same starting state and acceptance criteria. Compare CLI-only and agentic-plus-CLI when both are plausible. Never select a CLI because it is familiar or present in `tools/candidates.json`; require evidence for the specific operation.
5. **Choose per capability and document why.** Select agentic, CLI, or hybrid behavior according to measured task outcomes. A common hybrid is an agent/skill for investigation and code changes, MCP for authorized structured service access, and a CLI for reproducible tests, builds, or linting. One category does not have to win the whole workflow.

If no relevant approved capability exists, is incompatible, or cannot be exercised safely, record the exact gap and the reason. Use the best available fallback without claiming the unavailable path was evaluated. Do not enable or install a new MCP server, public service, or unapproved package just to complete a comparison.

## Compare the workflows

Use the measures that matter to the task; do not collapse them into a single vague quality score:

- Acceptance criteria met, correctness, and independently reviewed quality.
- Successful use of intended agent, skill, and MCP capabilities; missed or misused tools.
- Rework, human interventions, and time to accepted outcome.
- Reproducibility and strength of deterministic evidence.
- Permission scope, data exposure, and policy compliance.
- Offline behavior, startup/latency, resource use, and maintenance cost where relevant.

The evaluation order is **agentic-first**, while the result is task-specific. A CLI becomes preferred for a particular operation only when the comparison shows it performs better on the criteria that matter. An agentic workflow is not successful merely because it used an agent, and an available agentic feature must not be ignored without a recorded reason.

## Record the result

For each representative task, keep a small evidence record:

| Field | Record |
|---|---|
| Task and fixture | Exact task, starting state, and data class |
| Acceptance criteria | Observable pass conditions, defined before the run |
| Capability inventory | Available agents, skills, MCP tools, relevant CLIs, and permission limits |
| Agentic run | Agent/skill/MCP actually invoked, results, missed tools, and gaps |
| CLI comparison | Command/tool actually run, or reason it was not relevant |
| Outcome | Criteria met, defects/rework, interventions, and elapsed time |
| Selection | Preferred capability per operation and evidence for the choice |
| Boundaries | Approval, offline, compatibility, and qualification limitations |

For release/security proof, deterministic checkers remain authoritative for their stated tests. Agentic workflows can plan, investigate, implement, operate approved integrations, and interpret evidence; they cannot turn an unexecuted check into PASS.
