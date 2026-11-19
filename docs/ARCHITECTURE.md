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
       | on-demand specialists    | same pinned catalog
       | selective skills         | evidence per app/release
       | approved CLI tools       | company exceptions
       | approved MCP only        |
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

Golden Control = optional *read-only/useful editor* over standards/tool catalog.
It must not own the app registry, app compliance dashboard, application hosting,
observability data store, production actions or feedback raw-event storage.
```

### Internal boundaries

| Layer | Persisted source of truth | Runtime behavior | Failure mode |
|---|---|---|---|
| Golden Source | existing Git | Standards authoring/review/version control | Already installed pinned copies continue |
| Golden Release | existing artifact repository | Hash-qualified immutable package | Local approved last-known-good copy |
| OpenCode | existing company's internal model/runtime | Agent edits code and selectively calls skills/CLI/MCP | Manual engineer + local deterministic tools |
| Golden Proof | standalone local Python CLI and qualified OSS CLIs | Explicit rule applicability + evidence; no LLM | `NOT_RUN`, not fake PASS |
| Application CI | existing app CI and Git history | Full pre-release and owner-approved standards update scans | Blocks release or uses company-authorized evidence-backed exception |
| Team Platform | existing separately managed app platform | App hosting + observability single pane + raw feedback | Independent of Golden Control |

## 2. Agentic orchestration choice

**Default:** 1 primary engineer agent + relevant skill + direct CLI. Typical task should not incur subagent cost.

| Pattern | Trigger | Tools/actors | Why |
|---|---|---|---|
| Direct | Simple feature, bug, test | Golden engineer, CLI | Fewest requests/tokens |
| Router | Clearly separate React/NiceGUI/data task | Skill chosen from task type | Small context |
| Sequential | Requirements -> implementation -> verification -> draft docs | One agent, small artifacts between steps | Avoid speculation before code exists |
| Parallel | Multiple independent constrained investigations | At most necessary subagents | Save wall clock only if truly independent |
| Orchestrator-worker | Genuine multi-module task with distinct ownership | Scoped subagents | Explicit integration boundaries |
| Evaluator-optimizer | High-risk or repeated test failure | Deterministic tool -> bounded repair -> retest | Real proof, no AI self-scoring |

Avoid always-on agent swarms, open-ended loops and noisy MCP lists. Agent descriptions are not execution guarantees.

## 3. Context budget (what goes where)

- `AGENTS.md` (short): stable universal non-negotiables, company boundaries and fast commands.
- `.opencode/skills/<task>/SKILL.md`: only task-specific procedures. Loaded when relevant, not pre-injected wholesale.
- `standards/rules.json`: machine-checkable rule IDs, applicability and command mapping.
- `golden.project.json`: pinned version, explicit app profile/capability declarations and local commands.
- Source code / tests / existing docs: retrieve only relevant files via read/grep; do not put them into persistent prompt.
- MCP: typed access to authorized internal systems only when direct CLI is not sufficient.
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

No new background daemon is necessary. Golden Control UI is a later convenience layer.

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
4. **Golden Control:** future optional thin editor/search over standards/tools only.
5. **Golden Academy:** static guides, worked examples, objective real-app qualification exercises.

**Only one new runnable program is necessary for initial integration:** `scripts/golden.py` (plus existing approved CLI binaries). Do not build five independent services.
