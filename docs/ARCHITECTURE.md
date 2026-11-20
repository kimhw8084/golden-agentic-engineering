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

Golden Control = the team-facing operating cockpit for Golden installation, releases,
usage/evidence, design, qualification progress, and onboarding. It must surface source
and freshness for every status and show UNKNOWN when data is absent. It must not own
the app registry, app compliance dashboard, application hosting, production actions,
or raw application feedback/observability storage. See `docs/GOLDEN_CONTROL_SPEC.md`.
```

### Internal boundaries

| Layer | Persisted source of truth | Runtime behavior | Failure mode |
|---|---|---|---|
| Golden Source | existing Git | Standards authoring/review/version control | Already installed pinned copies continue |
| Golden Release | existing artifact repository | Hash-qualified immutable package | Local approved last-known-good copy |
| OpenCode | existing company's internal model/runtime | Agent edits code and selectively calls skills/CLI/MCP | Manual engineer + local deterministic tools |
| Golden Proof | standalone local Python CLI and qualified OSS CLIs | Explicit rule applicability + evidence; no LLM | `NOT_RUN`, not fake PASS |
| Golden Control | local read-only view, later approved company adapters | Installation, update, usage/evidence, design and next-action status | Explicit unknown/stale states; no fabricated data |
| Application CI | existing app CI and Git history | Full pre-release and owner-approved standards update scans | Blocks release or uses company-authorized evidence-backed exception |
| Team Platform | existing separately managed app platform | App hosting + observability single pane + raw feedback | Independent of Golden Control |

## 2. Agentic-first capability and orchestration choice

**Required order:** inspect the actual approved agent, skill, and MCP capabilities first; exercise the best-fit agentic workflow on the task; then compare relevant CLI candidates on the same acceptance criteria. Select by evidence for each capability. A CLI is preferred for a specific operation only when it performs better on the requirements that matter. Combine agents/skills/MCP with deterministic CLIs when that produces the strongest end-to-end result. Do not call irrelevant tools or force extra agents.

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
- MCP: typed access to authorized internal systems; discover and exercise relevant connected tools during capability selection. Compare a CLI for the same operation when useful.
- CLI: implementation, build, test, lint, or service operations when the candidate is approved and evidence shows it is the best fit for that operation.
- CI/evidence JSON: authoritative check outputs, linked to real files/versions. AI can explain but never author fabricated verification status.

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

The pilot **trusts the project-declared capabilities**. That does not satisfy the intended production requirement to independently prove non-applicability. During company implementation, cross-check the actual code/framework/dependencies/endpoints, and attach evidence. If capability detection is uncertain, use `NOT_RUN`, not `NOT_APPLICABLE`.

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
4. **Golden Control:** first-class team cockpit for Golden installation, approved releases, minimized usage/evidence, design rationale, progress, and onboarding.
5. **Golden Academy:** static guides, worked examples, objective real-app qualification exercises.

The starter now includes two dependency-free local programs: deterministic proof (`scripts/golden.py`) and a read-only control UI (`scripts/golden_control.py`). Company-wide status sources, authentication, and deployment must integrate with existing approved systems rather than become new standalone services.
