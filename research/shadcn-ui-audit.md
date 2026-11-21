# shadcn skill and MCP candidate audit

**Observed:** 2026-11-21  
**Pinned source:** [`shadcn-ui/ui`](https://github.com/shadcn-ui/ui/tree/45bbf9ba23c9c0f63d38887947e5fb06f59c7da3), commit `45bbf9ba23c9c0f63d38887947e5fb06f59c7da3` (main commit observed 2026-11-20).  
**Decision:** Relevant evaluation candidates for the company's React/TypeScript/Tailwind/shadcn route; neither is staged, copied, enabled, approved, or measured as a winner.

## Skill

The upstream [`skills/shadcn/SKILL.md`](https://github.com/shadcn-ui/ui/blob/45bbf9ba23c9c0f63d38887947e5fb06f59c7da3/skills/shadcn/SKILL.md) provides project-aware shadcn guidance, component patterns, examples, and design-system instructions. The pinned [`shadcn` package manifest](https://github.com/shadcn-ui/ui/blob/45bbf9ba23c9c0f63d38887947e5fb06f59c7da3/packages/shadcn/package.json) reports version 4.23.0 and MIT; the root [`LICENSE.md`](https://github.com/shadcn-ui/ui/blob/45bbf9ba23c9c0f63d38887947e5fb06f59c7da3/LICENSE.md) is MIT.

The skill is not safe to use as written in a no-public-egress environment. Its front matter grants shell commands for `npx shadcn@latest`, `pnpm dlx shadcn@latest`, and `bunx --bun shadcn@latest`, and it includes dynamic context that invokes `npx shadcn@latest info --json`. Do not install or import that permission block. Golden's existing `golden-react` skill remains the default. A future adaptation would need a selected-file license review, removal of installer/dynamic shell commands, and a focused context-value trial.

## MCP server

The pinned [`packages/shadcn/src/mcp/index.ts`](https://github.com/shadcn-ui/ui/blob/45bbf9ba23c9c0f63d38887947e5fb06f59c7da3/packages/shadcn/src/mcp/index.ts) registers seven tools:

- Registry listing, fuzzy search, item viewing, and examples: `get_project_registries`, `list_items_in_registries`, `search_items_in_registries`, `view_items_in_registries`, and `get_item_examples_from_registries`.
- `get_add_command_for_items` returns a CLI command string; it does not itself write project files. A separate shell/tool action could execute that string, so keep shell execution under developer review.
- `get_audit_checklist` returns a post-change checklist.

The official [MCP guide](https://github.com/shadcn-ui/ui/blob/45bbf9ba23c9c0f63d38887947e5fb06f59c7da3/apps/v4/content/docs/%28root%29/mcp.mdx) describes public, private, and third-party registries. Registry results can contain arbitrary source code and dependency recommendations. Evaluate only a pinned, pre-staged package against an explicitly approved intranet registry, with list/search/view/examples tools allowed and `get_add_command_for_items` disabled. Do not use `npx`, `pnpm dlx`, `bunx`, `@latest`, or public registries at company runtime.

The package declares 32 direct dependencies, including `@modelcontextprotocol/server`, the `@shadcn/registry` workspace, Zod, Execa, and Undici; the package metadata requires Node.js >=20.18.1. The transitive license/NOTICE closure, workspace build, target binaries, Windows/Linux behavior, MCP permission surface, registry endpoint behavior, offline operation, and egress attempts were not audited or tested. The server reports MCP version 1.0.0 at this commit; no signed release was verified.

## Route decision

Keep the current Golden React skill, local components, and deterministic tests as the default. Add the upstream skill and MCP to the route's evaluation candidates because they match the company's shadcn stack. Only consider MCP registry discovery when the team can stage a pinned build and confirm that every request goes to an approved internal registry; no public endpoint or installer fallback is allowed. No candidate was installed or invoked, no company OpenCode call trace exists, and no matched task comparison has run.
