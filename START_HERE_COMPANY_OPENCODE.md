# Company OpenCode entry point

**State: `PRE_QUALIFICATION`.** Start with [`COMPANY_START_HERE.md`](COMPANY_START_HERE.md) for the two-command Windows/Linux doctor and reviewed-apply flow. Do not start OpenCode until the company security/network owner verifies default-deny public egress for OpenCode and child processes, with approved intranet/model endpoints only.

## One-time company baseline

After the no-egress gate is proven, inspect the actual installed OpenCode build, permissions, primary/specialist agents, lazy skill discovery, connected MCP servers/tools, and orchestration support. Files in this repository describe Golden's intended routes; they do not prove that an installed or approved capability exists. Record each as `AVAILABLE`, `APPROVED`, `COMPATIBLE`, and `TESTED` only when each claim has its own evidence. Reuse this baseline while the build, config, and permission scope stay unchanged.

For the design baseline, read `README.md`, `AGENTS.md`, `docs/ARCHITECTURE.md`, `docs/AGENTIC_FIRST_EVALUATION.md`, `docs/GOLDEN_CONTROL_SPEC.md`, and `docs/QUALIFICATION_MATRIX.md`. Inspect agent/skill names, then load only the `golden-routing` skill and task-selected skills. Open `research/capability-selection.json` only for relevant candidates; do not preload the full 64-item acquisition catalog or all 19 rule descriptors for routine work.

## Routine task behavior

When an engineer gives an objective:

1. Give the project-default `golden-engineer` agent the objective directly. A clear small fix stays direct with no route command or extra skill; for nontrivial work it matches one route and loads only a task skill that changes the method or reduces risk. Use `/golden-route` when you want to inspect a route explicitly.
2. Check whether the route's specialist or MCP is already installed, connected, approved, and materially useful. Add it only when its expected contribution exceeds handoff/setup cost. Do not connect or install a candidate as part of routine routing.
3. Use deterministic tools for reproducible acceptance checks. Do not default to CLI-only problem solving or force an irrelevant agent/MCP call. Compare a CLI or another agentic option only when both can perform the same task and the comparison can use identical acceptance criteria.
4. Keep the task small: read its code, relevant tests, and local instructions; implement directly; run the focused checks; report the result and missing evidence. No full capability inventory, benchmark, swarm, or approval ritual per task.

For an explicit tool-selection or pilot comparison, follow [`docs/AGENTIC_FIRST_EVALUATION.md`](docs/AGENTIC_FIRST_EVALUATION.md): exercise the best-fit agent/skill workflow, compare plausible alternatives on the same task, and record actual invocation provenance. If trusted runtime events are unavailable, mark the trace unavailable; do not infer tool use or invent time/token improvements. A CLI is preferred for an operation only when evidence shows it is the better fit.

## Boundaries

- Keep existing provider, model, authentication and permission settings unchanged.
- Do not enable external provider fallback, telemetry, online installers, public model/package/browser requests, or unapproved MCP servers.
- Golden Control covers standards, tools, distribution, qualification and onboarding. The existing team platform remains responsible for app hosting, feedback, and observability.
- Routine code edits and tests need no added Golden approval gate. Production operations, external imports, and formal Golden release approval remain with the authorized company owners.
- This repository and its synthetic fixtures are not company qualification evidence. Keep missing checks `NOT_RUN`; do not claim the starter is company-qualified or that its public candidates are approved.
