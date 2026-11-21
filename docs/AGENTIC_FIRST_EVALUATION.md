# Agentic-first tool evaluation

The primary OpenCode agent is the default reasoning and routing layer. Tool selection should improve delivery, not make engineers perform a capability audit on every small task. This document separates routine work from explicit capability evaluation and defines what counts as evidence that a tool was used.

## Routine delivery (default)

1. Use the primary agent and relevant project context.
2. For a nontrivial task, identify the matching workflow and invoke its named skill before choosing implementation tools. A clear one/few-file fix stays direct and skips route/skill work.
3. Check only the matching specialist and task-relevant MCP capabilities visible in the current runtime, including permissions. Use them when the route condition and task justify the handoff or structured service access; do not substitute a CLI for a relevant available capability out of habit.
4. Use deterministic checks for reproducible proof. Keep the recent runtime baseline; do not re-scan the full catalog.
5. Skip tool benchmarking and per-task invocation ledgers unless selection, performance, security, or release evidence is explicitly needed. State material limitations briefly.

This is agentic-first because the primary agent handles reasoning and task selection by default. The repository config selects `golden-engineer` as the project's default primary agent in OpenCode builds that support `default_agent`. For nontrivial work, it follows the declared order: classify the task, invoke its named skill, check only relevant current specialists/MCP and permissions, then choose implementation tools. A clear small fix stays direct. The repo-wide candidate comparison is in `research/capability-selection.json`; consult it for explicit selection work or when a task touches one of its capabilities, then inspect only the relevant live connection and candidate. This does not require extra calls just to demonstrate activity.

## Named skill candidate: diagram design

For technical diagrams, the docs route invokes Golden's existing `golden-docs` skill. It adapts a small MIT-attributed subset from [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design/tree/d74d8c2d0c78a9e1efd43137f6a9a51182a8b5f0): choose semantic pattern before layout, remove elements that do not carry meaning, and bound the overview's density. Golden keeps monochrome, accessible, version-controlled SVG/Mermaid and system fonts, with no style questionnaire, remote assets, or confirmation pause for ordinary authorized work. The full upstream skill has not been vendored or invoked; its network defaults, optional browser export, broad prompt surface and mixed asset licenses remain unqualified. See [`research/diagram-design-audit.md`](../research/diagram-design-audit.md). No matched diagram-quality/time comparison has run.

For React UI, Golden's `golden-react` already covers the company stack, offline dependency selection, interaction states, accessibility, and deterministic acceptance. A bounded audit of [`nextlevelbuilder/ui-ux-pro-max-skill`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/tree/2de1134dc4d1cfe112934611ae5803ae17a1bd7e) identified a useful three-layer design-token idea, now adapted into that existing skill. The upstream MIT-licensed collection also includes broad brand/image workflows, external image providers and CDN examples, npm/GitHub update paths, and unaudited dependencies, so it remains unvendored and unapproved. No matched design-quality/time/context test ran; see [`research/ui-ux-pro-max-audit.md`](../research/ui-ux-pro-max-audit.md). `vercel-labs/agent-skills` remains held pending license evidence. Anthropic's skill repository has per-skill licenses: selected skills such as `frontend-design`, `webapp-testing`, `mcp-builder`, and `skill-creator` have Apache-2.0 files, while `pdf` has restrictive service-agreement terms. Review the exact folder and license rather than generalizing across that repository. For live Grafana investigation, evaluate the official `grafana/mcp-grafana` server with a read-only allowlist against the existing command/API path on a matched task. It exposes write-capable operations and can return large context payloads, so it stays disabled until the company endpoint, credentials, tool permissions, dependency closure, and offline policy are reviewed. These are evaluation orderings, not measured performance winners.

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
