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

1. Record `opencode --version`, documented `opencode --help`, `opencode agent list`, `opencode mcp list` if available. Avoid printing credentials.
2. Open this repository and verify that its `AGENTS.md`, one `SKILL.md`, one command `/golden-design` and one subagent actually appear and function.
3. Trigger one real source edit in an authorized fixture, run tests via CLI, commit in a disposable test Git repository under approved permissions.
4. Confirm no public network call, unexpected downloads, extra approval prompts or discarded work. Verify model-unavailable fallback still executes `golden.py`.
5. If company OpenCode format differs, translate only the adapter layer; preserve Golden semantics and deterministic gates. Store actual compatibility proof and adapter version.

## Avoid common agentic anti-patterns

- Never stuff full standards, every tool manual and all source into initial system prompt.
- No compulsory 5-agent workflow for a one-file fix.
- No assumption that MCP is faster/better than a CLI.
- Do not have the agent grade its own outputs as evidence. Real executable tests and human task success are authoritative.
