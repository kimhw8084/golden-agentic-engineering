# OpenCode public docs vs company version — mandatory compatibility check

This starter authors files using the currently published **OpenCode V2** conventions documented at:

- https://opencode.ai/docs/instructions/ — project/global `AGENTS.md`
- https://opencode.ai/docs/agents/ — `.opencode/agents/*.md`, subagent and primary modes, frontmatter permissions
- https://opencode.ai/docs/skills/ — `.opencode/skills/<name>/SKILL.md`, lazily discovered and loaded
- https://opencode.ai/docs/commands/ — `.opencode/commands/*.md` Markdown slash commands
- https://opencode.ai/docs/mcp-servers/ — optional `mcp.servers` objects and local stdio
- https://opencode.ai/docs/permissions/ — permissions/policies differ between V1/V2

The actual company's internal OpenCode version, provider and model must be inspected. **Do not replace company opencode.json**, do not assume V1 permission keys are supported, and do not enable an MCP or an internet provider based on a public example.

## Qualification exercise

1. Record `opencode --version`, documented `opencode --help`, agent/subagent inventory, skill discovery, connected MCP servers and tool lists, and available permissions/handoffs if supported. Avoid printing credentials. Record unavailable commands as NOT_AVAILABLE instead of assuming the feature is absent.
2. Open this repository and verify that its `AGENTS.md`, relevant `SKILL.md`, `/golden-design`, a specialist agent, and a task-relevant authorized MCP tool (if one is already connected) actually appear and function. Record exact capabilities that cannot be exercised and why.
3. Select a representative authorized fixture task. Run it through the best-fit agentic workflow first (agent + skill, adding a specialist or MCP tool when relevant). Compare an appropriate CLI-only or CLI-assisted workflow against the same acceptance criteria; preserve actual invocations, tool results, human interventions, elapsed time and rework. Choose tools per operation based on that evidence.
4. Confirm no public network call, unexpected downloads, extra approval prompts or discarded work. Verify model-unavailable fallback still executes `golden.py` and note which parts of the workflow need the model.
5. If company OpenCode format differs, translate only the adapter layer; preserve Golden semantics and deterministic gates. Store actual compatibility proof and adapter version.

## Avoid common agentic anti-patterns

- Never stuff full standards, every tool manual and all source into initial system prompt.
- No compulsory multi-agent workflow for a one-file fix; discover relevant capabilities, then use only what helps.
- Do not pre-rank CLI above agents, skills, or MCP. Do not assume any category wins; compare actual task outcomes and choose per capability.
- Do not have the agent grade its own outputs as evidence. Real executable tests and human task success are authoritative.
