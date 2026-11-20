# Golden Control — team-facing operating cockpit

## Purpose

Golden Control gives the team one clear place to see the state of Golden itself: what is installed, what is current, what is proven, what people are using, what is still unknown, why the design exists, and what to do next. It is a first-class part of the team-ready Golden design, not an optional documentation browser.

The performance goal is the quickest **independently accepted** outcome with full required quality. Golden does not promise “fastest ever” without paired, representative measurements. It measures task success, correctness, rework, human interventions, and elapsed time, then selects agents, skills, MCP tools, CLI tools, or a hybrid per capability.

## UI areas

| Area | Team question it answers | Required evidence |
|---|---|---|
| Overview | Where are we, and what is the next best action? | Version, qualification, installed coverage, feed health, evidence freshness, open gaps |
| Installation | Which agents, skills, commands, and approved MCP capabilities are available on each supported environment? | Host/runtime identity, version, asset hashes, discovery results, permissions, conflicts, checked time |
| Updates | What is the latest approved release, who can update, and how do we roll back? | Internal release feed, current/target versions, package hashes, rollout status, rollback package |
| Usage & evidence | Which workflows help, and are they improving accepted outcomes? | Opt-in task class, selected capability, actual invocation, completion, test outcome, rework, time, independent acceptance |
| Design system | Why does Golden exist and what boundaries does it follow? | Architecture, decisions, standards, tool-selection policy, ownership and release model |
| Start here | What should a team member or owner do first? | Version-specific steps, exact commands, compatibility checks, pilot task, measures, escalation owner |

Every status needs a source and last-checked time. Distinguish `UNKNOWN`, `NOT_RUN`, `NOT_AVAILABLE`, `NOT_APPLICABLE`, `FAIL`, and actual zero. Never turn a missing collector into “0 installed,” “0 usage,” or “up to date.” Show which state is local, company-wide, or unqualified.

## Data and trust boundaries

1. **Local OpenCode adapter:** read-only checks for installed Golden files, hashes, runtime version, agent/skill discovery, connected MCP tool names, and permission scope. Do not expose provider secrets, environment values, prompts, or source content.
2. **Internal release adapter:** read approved versions and packages from the existing company artifact/release source. No public internet update checks. Verify signatures/hashes and preserve rollback information.
3. **Usage adapter:** optional, purpose-limited events through the existing company platform. Collect only the minimum fields needed to compare workflow performance. Never collect raw prompts, source code, credentials, or raw application feedback. The company must approve event fields, retention, access, and aggregation before enabling it.
4. **Existing company identity/platform:** host the team-facing UI through the platform and authentication already approved by the company. Golden Control does not create a parallel app registry, production dashboard, or observability backend.
5. **Deterministic proof:** checks remain independently executable and their output remains authoritative. The UI presents evidence and provenance; it does not upgrade unexecuted checks to PASS.

## Rollout sequence

1. **Local UI and honest adapters (current prototype):** run offline on localhost. Compare source files with an explicitly supplied OpenCode config directory and summarize explicitly supplied Golden evidence JSON files. Show company runtime discovery, approved release feed, and agent/skill/MCP usage as unconnected until real adapters exist.
2. **Company OpenCode compatibility:** inspect the installed internal version, agent/skill/MCP interfaces, permissions, and available event hooks. Test one representative workflow, exercise agents/skills/MCP first, then compare CLI and hybrid candidates on the same acceptance criteria.
3. **Installation/update integration:** connect read-only per-machine status and the approved internal artifact source. Test safe update and rollback on supported Windows/Linux configurations.
4. **Usage evidence:** agree on privacy-reviewed, opt-in, minimized events. Compare actual accepted outcomes; do not use raw token/call counts as a substitute for task quality.
5. **Team rollout:** deploy the control UI through the existing company platform with its authentication, role model, and audit rules. Add owners, freshness indicators, help paths, and a visible change/qualification log.

## Acceptance criteria for a team release

- A team member can immediately see the Golden design, current qualification state, next steps, and the owner for open work without reading the whole requirements draft.
- An authorized owner can see actual installations, agent/skill discovery, approved MCP availability, release/update status, and rollback state with evidence timestamps.
- The UI reports unknown or stale sources as such; it does not invent zeroes, qualification, or successful updates.
- The team can compare agentic, CLI, and hybrid workflows on matched tasks using acceptance, quality, rework, intervention, and time measures.
- Usage collection is disabled until company-approved event fields, access, and retention are configured; it never requires prompt or source capture.
- The application is accessible, responsive, and hosted/authenticated through the existing approved team platform. It does not take ownership of application hosting, raw feedback, or company observability.
- Windows, Linux, offline operation, compatibility, update, recovery, and role checks are independently verified before company-wide use.

## Current prototype limits

The local dashboard is read-only and offline. It can compare Golden agent/skill/command files in one explicitly supplied directory, inspect the local package checksum manifest and Git state, and aggregate summary fields from local Golden evidence reports. It does **not** inspect internal OpenCode agents or MCP connections, connect to a company release feed, collect AI/MCP usage, provide multi-machine installation inventory, authenticate team members, or establish company qualification. Those adapters require actual company environment evidence and approval.
