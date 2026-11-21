# Golden Agentic Engineering — concrete architecture

**Design status:** draft implementation proposal; 107 user decisions reconciled; company approval and full baseline sign-off remain separate. This repository provides a **working pilot scaffold**, not 151 completed rule implementations.

## 1. Control plane versus execution plane

```text
[Golden standards Git repository]
       |-- standards/rules.json, release.json, profiles
       |-- .opencode/{agents,skills,commands}
       |-- tools/candidates.json, docs, templates
       |
       +-- team-lead-approved release through existing CI
                           |
             [Internal artifact repository]
              |    pinned package + hashes + OSS clearance
              |                  |
       [Developer local cache]     [Existing app CI]
       |                           |
       | OpenCode primary agent    | same deterministic Golden rule runner
       | task-relevant specialists | same pinned catalog
       | selective skills         | evidence per app/release
       | approved MCP tools       | company exceptions
       | evidence-selected CLIs   |
       +------- normal Git -------+
                   |
           [Application repositories]
              direct commits to main allowed if owner authorized
              never auto-publish just because commit exists
                   |
           [Existing team application platform]
              real internal tools; unified observability React UI
              app usage feedback and improvements
                   |
             approved standards-relevant summaries
                   v
             [Team lead Golden standards improvement process]

Golden Control = the bounded operating cockpit for Golden's own installation, releases,
qualification evidence, design and onboarding. It can display minimal aggregate usage
evidence from the existing platform as a read-only view. It must surface source and
freshness for every status and show UNKNOWN when data is absent. It must not own an event
collector, productivity analytics, app registry, app compliance dashboard, application
hosting, production actions, or raw application feedback/observability storage. See
`docs/GOLDEN_CONTROL_SPEC.md`.
```

### Internal boundaries

| Layer | Persisted source of truth | Runtime behavior | Failure mode |
|---|---|---|---|
| Golden Source | existing Git | Standards authoring/review/version control | Already installed pinned copies continue |
| Golden Release | existing artifact repository | Hash-qualified immutable package | Local approved last-known-good copy |
| OpenCode | existing company's internal model/runtime | Agent edits code and selectively calls skills/CLI/MCP | Manual engineer + local deterministic tools |
| Golden Proof | standalone local Python CLI and qualified OSS CLIs | Explicit rule applicability + evidence; no LLM | `NOT_RUN`, not fake PASS |
| Golden Control | local read-only view, later approved company adapters | Golden installation, update, qualification, design and next-action status; optional aggregate evidence view | Explicit unknown/stale states; no collector or fabricated data |
| Application CI | existing app CI and Git history | Full pre-release and owner-approved standards update scans | Blocks release or uses company-authorized evidence-backed exception |
| Team Platform | existing separately managed app platform | App hosting + observability single pane + raw feedback | Independent of Golden Control |

## 2. Agentic-first capability and orchestration choice

**Default:** use the primary OpenCode agent for reasoning and routing. Keep discovery proportional: load only a relevant skill, reuse a recent runtime baseline, and use known approved MCP capabilities when the task needs them. Do not inventory every agent/MCP, benchmark alternatives, or keep a tool-call ledger for routine work. Add a specialist or MCP call when its expected benefit exceeds latency/coordination cost.

**Triggered evaluation:** inspect live capabilities when a non-obvious integration is central, the runtime/config/permissions changed, the user requests tool selection or performance measurement, or a pilot/release needs qualification. Exercise the strongest suitable agentic workflow before comparing a CLI that is a plausible alternative for that operation. Compare matched acceptance criteria and choose per capability. See `docs/AGENTIC_FIRST_EVALUATION.md`.

| Pattern | Trigger | Tools/actors | Why |
|---|---|---|---|
| Direct agentic | Simple feature, bug, or task with one clear owner | Primary agent + relevant skill; approved MCP when relevant | Exercise the best-fit agentic capability with low coordination cost |
| Router | Clear framework/domain specialization | Primary agent routes to relevant skill and specialist agent/MCP capability | Match expertise without preloading everything |
| Sequential | Requirements -> implementation -> tests -> documentation | Agent-led stages; CLI checks where they provide deterministic proof | Later steps depend on earlier evidence |
| Parallel | Multiple independent constrained investigations | Relevant specialist agents or MCP calls, only where useful | Save wall clock only when tasks are genuinely independent |
| Orchestrator-worker | Genuine multi-module change with distinct ownership | Primary orchestrator + scoped agents and approved tools | Explicit integration boundaries |
| Evaluator-optimizer | High-risk or repeated test failure | Agent interprets evidence and repairs; deterministic checker verifies | Real proof, no AI self-scoring |

Avoid always-on swarms, open-ended loops and irrelevant MCP calls. Agent descriptions are not execution guarantees; verify that the chosen agent/skill/MCP capability was actually invoked and contributed evidence.

## 3. Context budget (what goes where)

- `AGENTS.md` (short): stable universal non-negotiables, company boundaries and fast commands.
- `.opencode/skills/<task>/SKILL.md`: only task-specific procedures. Loaded when relevant, not pre-injected wholesale.
- `standards/rules.json`: machine-checkable rule IDs, applicability and command mapping.
- `golden.project.json`: pinned version, explicit app profile/capability declarations and local commands.
- Source code / tests / existing docs: retrieve only relevant files via read/grep; do not put them into persistent prompt.
- MCP: typed access to authorized internal systems; inspect live connections when the task requires a non-obvious integration or a selection evaluation. Compare a CLI for the same operation only when it is a plausible alternative.
- CLI: implementation, build, test, lint, or service operations when the candidate is approved and evidence shows it is the best fit for that operation.
- CI/evidence JSON: authoritative deterministic check outputs, linked to real files/versions. OpenCode tool-use claims need a separate trusted runtime event source; self-report or a hash of an agent-authored log does not prove invocation. AI can explain but never author fabricated verification status.

## 4. Contract between project, checker, and CI

Each app supplies `golden.project.json`:

```json
{
  "name": "actual-project-name",
  "golden_version": "0.1.0-dev",
  "profile": "react",
  "criticality": "workflow",
  "capabilities": {"ui": true, "api": true, "database": false},
  "commands": {
    "ts_typecheck": ["npm", "run", "typecheck", "--", "--offline"],
    "web_tests": ["npm", "run", "test:ci"]
  }
}
```

Commands above are **illustrative** and must be adapted to actual approved offline project scripts and package-manager options. Do not use `npm` install at check time.

Full check output uses `PASS`, `FAIL`, `NOT_APPLICABLE`, `NOT_RUN`. Fast-only runs add `DEFERRED`, which is not a release pass. Result includes Golden version, rule manifest SHA256, timestamp, execution duration and a short evidence excerpt. Original FAIL/NOT_RUN must remain visible even when a company exception exists. **The pilot engine does not implement exception grants**, so adding them is a pre-release work item.

### Applicability caveat

The pilot reads project-declared capabilities as scope hints, but a declared `false` no longer proves non-applicability: missing independent basis returns `NOT_RUN`. It does not independently inspect the entire project to validate positive declarations or prove that an omitted capability is absent. During company implementation, cross-check the actual code/framework/dependencies/endpoints and attach evidence before treating a rule as out of scope. If capability detection is uncertain, use `NOT_RUN`, not `NOT_APPLICABLE`.

### Fast vs full

- `--fast` checks manifest pin and Python AST, and other explicitly low-cost checks. Anything full-only is reported `DEFERRED`.
- `--full` assesses every rule; executes applicable checks; blocks when mandatory applicable check fails or is not runnable. Company exceptions are recorded in existing CI by authorized approvers, not silently added by Golden.
- No mandatory full check on every edit/commit. Full evaluation runs on demand, before release and after lead-approved Golden update **when app owner authorizes that CI run**.

## 5. Tool acquisition, caching and versioning

Public GitHub repo URLs are catalog entries, not runtime dependencies. Separate steps:

1. Public staging: checkout snapshots of desired candidates and lock Git commits, hash archives.
2. Procurement/security: verify exact OSI license and dependencies/assets, vulnerability data, commercial-use allowances, OS binaries, company clearance.
3. Offline staging: include appropriate executable archives, Python wheels, Node stores, browsers, vulnerability DB and fonts/assets as needed. Prove no public downloads while running.
4. Internal Git + existing artifact repository: publish immutable version with hashes, qualification results and rollback instructions.
5. Locally pin installed Golden version per project; engineers may use it offline even when central source is unavailable.

The current Golden Control UI is a localhost-only process with read-only file/evidence inputs. A team-wide deployment must use the existing company platform and approved adapters; it must not introduce a parallel app registry, telemetry backend, or public update service.

## 6. Real production boundaries

- OpenCode may autonomously modify authorized development files and commit to main; no Golden per-edit approvals.
- Production and irreversible operations remain human-controlled, per existing company policy.
- Git review mechanism for Golden-originated remediation proposals **does not constrain** ordinary owner-requested OpenCode edits.
- Existing company software may be proprietary. Newly imported Golden packages require OSI license and clearance.
- No aggregate engineering score; individual measured baselines and fail/pass/not-run results.
- Strict mono black/white/gray, even for alerts and scientific charts; use redundant shape/pattern/label semantics and test distinguishability.
- App feedback resides in existing team platform; Golden receives approved minimal standards-relevant summaries only.

## 7. Logical modules versus deployed components

1. **Golden Standard:** documents/rules/profiles in Git.
2. **Golden Workbench:** OpenCode agents/skills/commands and qualified CLI packages.
3. **Golden Proof:** local deterministic runner and existing CI, with evidence.
4. **Golden Control:** bounded team cockpit for Golden installation, approved releases, qualification evidence, design rationale, progress, and onboarding; optional aggregate evidence is read-only from the existing platform. No new collector, productivity dashboard, or event store.
5. **Golden Academy:** static guides, worked examples, objective real-app qualification exercises.

The starter now includes two dependency-free local programs: deterministic proof (`scripts/golden.py`) and a read-only control UI (`scripts/golden_control.py`). Company-wide status sources, authentication, and deployment must integrate with existing approved systems rather than become new standalone services.
