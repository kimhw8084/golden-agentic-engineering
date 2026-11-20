# OpenCode public docs vs company version — mandatory compatibility check

This starter authors files using the currently published **OpenCode V2** conventions documented at:

- https://opencode.ai/docs/instructions/ — project/global `AGENTS.md`
- https://opencode.ai/docs/agents/ — `.opencode/agents/*.md`, subagent and primary modes, frontmatter permissions
- https://opencode.ai/docs/skills/ — `.opencode/skills/<name>/SKILL.md`, lazily discovered and loaded
- https://opencode.ai/docs/commands/ — `.opencode/commands/*.md` Markdown slash commands
- https://opencode.ai/docs/mcp-servers/ — optional `mcp.servers` objects and local stdio
- https://opencode.ai/docs/permissions/ — permissions/policies differ between V1/V2

The actual company's internal OpenCode version, provider and model must be inspected. **Do not replace company opencode.json**, do not assume V1 permission keys are supported, and do not enable an MCP or an internet provider based on a public example.

## Offline-first qualification exercise

1. Run [`COMPANY_START_HERE.md`](../COMPANY_START_HERE.md) Step A and verify the offline doctor output. Obtain Python/Node/OpenCode versions from approved local inventory; the doctor never executes version flags. Mark unknown versions UNKNOWN.
2. Before starting OpenCode, the company security/network owner must verify a default-deny public-egress policy and attempt monitoring for OpenCode and all children. Golden's Python audit-hook probe is not proof of OS-level enforcement.
3. Only after the zero-public-attempt gate is established, use the company's approved method to inspect the OpenCode build, agent/subagent inventory, skill discovery, connected MCP servers/tools, permissions, and handoff features. Avoid credentials and preserve config. If any invocation causes a public endpoint attempt, stop and report it; do not proceed to a task trial.
4. Verify this repository's AGENTS.md, one relevant SKILL.md, `/golden-design`, a specialist agent, and an already-approved task-relevant MCP tool where applicable. Never enable the local synthetic fixture in the company config as part of this check.
5. Select a representative authorized synthetic task. Run best-fit primary agent + relevant skill first, add a specialist/MCP only if useful, and compare a CLI only when plausible for the same operation. Preserve real results, human interventions, elapsed time, rework, and trusted token/request events where available.
6. Confirm no network attempt, unexpected download, extra approval prompt, or discarded work. Verify deterministic/model-off behavior. If the company format differs, adapt only the config adapter and preserve provider/model/auth settings.

## Avoid common agentic anti-patterns

- Never stuff full standards, every tool manual and all source into initial system prompt.
- No compulsory multi-agent workflow for a one-file fix; discover relevant capabilities, then use only what helps.
- Do not pre-rank CLI above agents, skills, or MCP. Do not assume any category wins; compare actual task outcomes and choose per capability.
- Do not have the agent grade its own outputs as evidence. Real executable tests and human task success are authoritative.
