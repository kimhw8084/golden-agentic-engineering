# Agentic-first tool evaluation

The primary OpenCode agent is the default reasoning and routing layer. Tool selection should improve delivery, not make engineers perform a capability audit on every small task. This document separates routine work from explicit capability evaluation and defines what counts as evidence that a tool was used.

## Routine delivery (default)

1. Use the primary agent and the relevant project context.
2. Load a skill when it materially helps with the task; do not enumerate or preload the skill catalog.
3. Use an already-known, authorized MCP capability when the task needs its structured service access. Inspect live connections only when an unfamiliar or changed integration is material.
4. Use deterministic checks for reproducible proof. Add a specialist agent only when expected quality or time savings justify coordination.
5. Skip tool benchmarking, broad capability inventories, and per-task invocation ledgers. State any material limitation briefly.

This is agentic-first because the primary agent handles reasoning and routing by default. For each routed job, select its relevant local skill and any approved specialist/MCP that materially improves the result before choosing deterministic tools. The repo-wide candidate comparison is in `research/capability-selection.json`; consult it for explicit selection work or when a task touches one of its capabilities, then inspect only the relevant live connection and candidate. This does not require extra calls just to demonstrate activity.

## Named skill candidate: diagram design

For polished diagrams, evaluate the [`diagram-design` agent skill](https://github.com/cathrynlavery/diagram-design) before reaching for a CLI renderer. Its upstream README documents a manual copy or symlink into OpenCode's `.opencode/skills/diagram-design` directory; the skill is not installed or verified in the target company environment by this repository. It generates HTML/SVG without a text-diffable source, so keep Mermaid or D2 for diagrams that need routine Git diffs. Default Google Fonts can be disabled with system-font mode for offline use. Treat it as an unqualified candidate until the target OpenCode compatibility, policy, privacy, dependency, and offline checks pass.

For React visual design, `nextlevelbuilder/ui-ux-pro-max-skill` is the first external skill candidate in the selection registry because its inspected source commit contains an MIT license and a searchable design workflow. The complete skill, helper scripts, dependency closure, prompt-injection surface, and network behavior still need review; Golden does not vendor it. `vercel-labs/agent-skills` remains held pending license evidence. Anthropic's skill repository has per-skill licenses: selected skills such as `frontend-design`, `webapp-testing`, `mcp-builder`, and `skill-creator` have Apache-2.0 files, while `pdf` has restrictive service-agreement terms. Review the exact folder and license rather than generalizing across that repository. For live Grafana investigation, evaluate the official `grafana/mcp-grafana` server with a read-only allowlist against the existing command/API path on a matched task. It exposes write-capable operations and can return large context payloads, so it stays disabled until the company endpoint, credentials, tool permissions, dependency closure, and offline policy are reviewed. These are evaluation orderings, not measured performance winners.

## Trigger a capability evaluation when

- The user asks which approach is fastest or best, or requests a performance comparison.
- An unfamiliar agent, skill, MCP integration, or permission boundary is central to the task.
- The OpenCode version, configuration, available tools, or permissions changed since the last verified baseline.
- A pilot or release qualification requires evidence for the chosen capability.

For that evaluation, scope runtime discovery to the operation under consideration. Define a representative authorized task and acceptance criteria first. Exercise the strongest suitable agentic workflow (primary agent plus relevant skill; specialist or approved MCP when useful). Compare a CLI only if it is a plausible alternative for that operation. Use matched inputs and criteria. Choose per operation based on accepted outcome, correctness, rework, intervention, elapsed time, reliability, permissions, offline needs, and maintenance cost. A hybrid may win. The repository review is a targeted, pinned-source evaluation of the leading plausible candidates found for its workflows; it does not claim to enumerate every public GitHub project.

If a capability is unavailable, incompatible, unauthorized, or unqualified, record that exact gap and use the best safe fallback. A candidate catalog is not proof of availability, quality, or approval. Do not enable an unapproved service for comparison.

## Invocation evidence and provenance

Golden's deterministic check evidence (`golden-evidence/v0.1`) proves only the checks it actually ran. It is not an OpenCode agent/skill/MCP/CLI invocation trace. Keep these evidence types separate.

Classify invocation claims as follows:

| Provenance | What it establishes | How to report it |
|---|---|---|
| Runtime-sourced event | A trusted OpenCode host/runtime source recorded a specific invocation and outcome | May count as an observed invocation after source, identity/scope, integrity, and timestamp are checked |
| Human/operator observation | A person directly observed a call or result, but no verifiable runtime event is available | Report as observed/self-attested; do not present as a machine-verified trace or usage count |
| Model/operator self-report | An agent says it used a capability without a supporting event | Treat as an unverified claim; never count it as instrumented usage or benchmark proof |
| Catalog/config presence | A capability is listed in files or settings | Establishes configuration intent only, not discovery, invocation, permission success, or outcome |

A future approved runtime adapter should preserve, at minimum, the source system and collector version, event ID, pseudonymous session/task reference, timestamp, capability identifier and type, policy/permission outcome, result category, and elapsed time. An optional artifact digest may link deterministic output. Verify events using the source platform's integrity and access controls; hashing an agent-authored report alone does not establish provenance. Do not collect prompts, model responses, source text, credentials, or raw command output.

No suitable company runtime trace source is connected in this starter. Until one is verified, report invocation telemetry as `NOT_INSTRUMENTED` or `TRACE_UNAVAILABLE`; do not infer counts from repository files or model prose. Comparative conclusions based only on self-report remain provisional.

## Evaluation record (only for triggered evaluations)

| Field | Record |
|---|---|
| Task and fixture | Exact task, starting state, and data class |
| Acceptance criteria | Observable pass conditions defined before the run |
| Relevant capability baseline | OpenCode version/config identity, only the agents/skills/MCP/CLIs relevant to the operation, permission limits, and when checked |
| Agentic run | Agent/skill/MCP actually exercised and outcome, with provenance class and source event reference when available |
| CLI comparison | CLI actually run only when plausible; otherwise a short reason it was not relevant |
| Outcome | Criteria met, defects/rework, human intervention, elapsed time, and independent acceptance |
| Selection | Preferred capability per operation and evidence for that choice |
| Boundaries | Approval, offline, compatibility, privacy, and qualification limits |

Deterministic checkers remain authoritative for their stated checks. Agentic workflows can plan, investigate, implement, operate approved integrations, and interpret evidence; they cannot turn an unexecuted check into PASS or a self-report into a verified tool trace.
