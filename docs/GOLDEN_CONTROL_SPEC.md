# Golden Control — team-facing operating cockpit

## Purpose

Golden Control gives the team one clear place to see the state of Golden itself: what is installed, what is current, what is proven, what people are using, what is still unknown, why the design exists, and what to do next. It is a first-class part of the team-ready Golden design, not an optional documentation browser.

The performance goal is the quickest **independently accepted** outcome with full required quality. Golden does not promise “fastest ever” without paired, representative measurements. Tool comparisons happen for explicit selection decisions and pilots, not as a ritual on every task.

## Scope test

Golden Control operates Golden itself: approved Golden versions, installation/configuration status, release/update state, Golden qualification evidence, design decisions, and onboarding. It may display minimal aggregate adoption or evaluation evidence only when the existing company platform already owns that data and the source is approved. Golden Control is a read-only consumer of that source; it does not create the collection pipeline.

For every proposed feature, answer:

1. Does it directly help an owner administer or understand Golden?
2. Can it read from an existing approved system of record, with provenance and freshness?
3. Can it remain read-only and avoid collecting raw prompts, source code, credentials, or per-person productivity scores?

If not, leave the state visibly unavailable or link to the system that owns it. Do not add a new database, event collector, app registry, observability service, deployment control, or broad productivity analytics to Golden Control.

## UI areas

| Area | Team question it answers | Required evidence |
|---|---|---|
| Overview | Where are we, and what is the next best action? | Version, qualification, installed coverage, feed health, evidence freshness, open gaps |
| Installation | Which agents, skills, commands, and approved MCP capabilities are available on each supported environment? | Host/runtime identity, version, asset hashes, discovery results, permissions, conflicts, checked time |
| Updates | What is the latest approved release, who can update, and how do we roll back? | Internal release feed, current/target versions, package hashes, rollout status, rollback package |
| Usage & evidence | What approved aggregate Golden adoption/evaluation evidence exists? | Existing platform summary, defined aggregation, provenance level, source and freshness; no person-level productivity tracking |
| Design system | Why does Golden exist and what boundaries does it follow? | Architecture, decisions, standards, tool-selection policy, ownership and release model |
| Start here | What should a team member or owner do first? | Version-specific steps, exact commands, compatibility checks, pilot task, measures, escalation owner |

Every status needs a source and last-checked time. Distinguish `UNKNOWN`, `NOT_RUN`, `NOT_AVAILABLE`, `NOT_APPLICABLE`, `FAIL`, and actual zero. Never turn a missing source into “0 installed,” “0 usage,” or “up to date.” Show whether a state is local, company-wide, or unqualified. A model-authored statement that a tool was used is not an invocation trace.

## Data and trust boundaries

1. **Local OpenCode adapter:** read-only checks for installed Golden files, hashes, runtime version, agent/skill discovery, connected MCP tool names, and permission scope. Do not expose provider secrets, environment values, prompts, or source content.
2. **Internal release adapter:** read approved versions and packages from the existing company artifact/release source. No public internet update checks. Verify signatures/hashes and preserve rollback information.
3. **Usage/evaluation view:** read-only display of minimal aggregate evidence already collected by an approved existing company platform. Golden Control owns no collector, event database, or background instrumentation. The source platform must approve fields, retention, access, integrity, and aggregation. Never expose raw prompts, source code, credentials, raw application feedback, or person-level productivity scores.
4. **Existing company identity/platform:** host the team-facing UI through the platform and authentication already approved by the company. Golden Control does not create a parallel app registry, production dashboard, or observability backend.
5. **Deterministic proof and trace provenance:** checks remain independently executable and their output remains authoritative. A tool invocation is considered instrumented only when a trusted runtime event source provides verifiable provenance. Self-report can be labeled as such but cannot become a verified trace or usage count. The UI presents evidence and provenance; it does not upgrade unexecuted checks to PASS.

## Rollout sequence

1. **Local UI and honest adapters (current prototype):** run offline on localhost. Compare source files with an explicitly supplied OpenCode config directory and summarize explicitly supplied Golden evidence JSON files. Show company runtime discovery, approved release feed, and agent/skill/MCP usage as unconnected until real adapters exist.
2. **Company OpenCode compatibility:** inspect the installed internal version, agent/skill/MCP interfaces, permissions, and available event hooks. Test one representative workflow, exercise agents/skills/MCP first, then compare CLI and hybrid candidates on the same acceptance criteria.
3. **Installation/update integration:** connect read-only per-machine status and the approved internal artifact source. Test safe update and rollback on supported Windows/Linux configurations.
4. **Usage evidence:** only display privacy-reviewed aggregate measures that the existing platform already owns. Do not add Golden-side instrumentation. Compare accepted outcomes in scoped pilots; raw call/token counts are not task quality.
5. **Team rollout:** deploy the control UI through the existing company platform with its authentication, role model, and audit rules. Add owners, freshness indicators, help paths, and a visible change/qualification log.

## Acceptance criteria for a team release

- A team member can immediately see the Golden design, current qualification state, next steps, and the owner for open work without reading the whole requirements draft.
- An authorized owner can see actual Golden installations, compatible agent/skill discovery, approved MCP availability metadata, release/update status, and rollback state with source evidence and timestamps.
- The UI reports unknown or stale sources as such; it does not invent zeroes, qualification, or successful updates.
- The team can compare agentic, CLI, and hybrid workflows on matched tasks using acceptance, quality, rework, intervention, and time measures.
- Usage is a read-only aggregate view from the existing approved platform. Golden Control adds no collector or per-person productivity score; displayed invocation claims show their provenance class.
- The application is accessible, responsive, and hosted/authenticated through the existing approved team platform. It does not take ownership of application hosting, raw feedback, or company observability.
- Windows, Linux, offline operation, compatibility, update, recovery, and role checks are independently verified before company-wide use.

## Current prototype limits

The local dashboard is read-only and offline. It can compare Golden agent/skill/command files in one explicitly supplied directory, inspect the local package checksum manifest and Git state, and aggregate summary fields from local Golden evidence reports. It does **not** inspect internal OpenCode agents or MCP connections, verify tool invocation traces, connect to a company release feed, collect AI/MCP usage, provide multi-machine installation inventory, authenticate team members, or establish company qualification. Those read-only adapters require actual company environment evidence and approval; the existing platform must remain the system of record for usage data.
