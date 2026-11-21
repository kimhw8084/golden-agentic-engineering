# Golden Agentic Engineering System

**GitHub-ready starter · v0.1.0-dev · NOT company qualified · NOT a standards release**

A lightweight **OpenCode-first agentic engineering standards toolkit** for engineering teams. This repository contains functioning Python-standard-library verification scaffolding, OpenCode agents/skills/commands, a real candidate OSS manifest, opt-in public-source staging, and generic deployment guidance. It deliberately does **not** host engineering applications or replace existing CI, Git, artifact registry, monitoring, or logging systems.

The primary OpenCode agent is the default reasoning/routing layer. For nontrivial requests, match a route in [`workflows/task-routing.json`](workflows/task-routing.json), invoke its named Golden skill before choosing implementation tools, and check only the route-relevant agents and MCP capabilities visible in the current runtime. Do not skip an applicable skill or replace a relevant available agent/MCP with a CLI out of habit. Keep one/few-file fixes direct and lean; use deterministic tools for reproducible proof and compare alternatives only when they could perform the same operation. See [`research/capability-selection.json`](research/capability-selection.json) for pinned candidate evidence and [`docs/AGENTIC_FIRST_EVALUATION.md`](docs/AGENTIC_FIRST_EVALUATION.md) for the selection method. No performance winner is claimed without matched runtime evidence.

> **You can push this repository to GitHub now.** You cannot claim it or its OSS candidates are company-cleared or offline-runnable before internal qualification. No external dependencies are shipped by default.

## Fastest start from a phone

1. This repository is public. Do not add company data, credentials, internal hostnames, or proprietary implementation details.
2. Review [`COMPANY_START_HERE.md`](COMPANY_START_HERE.md) and transfer only approved source through the company import process.
3. On the work PC, run the doctor step before reviewing any apply diff. The doctor never executes OpenCode or contacts a network.

## What works without external packages today

```text
python -m unittest discover -s tests -v
python scripts/golden.py list
python scripts/golden.py doctor --project examples/python-app
python scripts/golden.py check --fast --project examples/python-app
python scripts/golden.py check --full --project examples/python-app --out out/evidence.json
python scripts/golden.py report --input out/evidence.json --project . --out out/evidence.html
python scripts/validate_manifests.py
python scripts/security_scan.py --history  # current files and complete reachable Git history
python scripts/network_attempt_monitor.py
python benchmarks/run_local_fixtures.py --out verification/local-fixtures.json
python scripts/package_offline.py create --out /approved/transfer/golden.tar.gz
python scripts/package_offline.py verify /approved/transfer/golden.tar.gz
python scripts/golden_control.py --target "<EXISTING_CONFIG_DIR>" --evidence-dir out
python scripts/fetch_sources.py --tier pilot --limit 3   # dry run only, no download
```

A full example evaluation is expected to **not** be release-qualified because most external checks are unconfigured. This is correct behavior, not a defect.

## Essential architecture

```text
             GOLDEN STANDARDS REPO (this repository)
   policies + profiles + rule catalog + skills + tool list
                         |
          lead-approved versioned release
                         |
        existing internal artifact repository
                   /              \
     developer local cache       existing CI
       | OpenCode agents + skills  | independent rules
       | approved MCP + selected CLIs | full release checks
       | direct Git commits        | evidence / exceptions
                   \              /
               app source repositories
                        |
            separate team application platform
      real applications, user feedback, observability UI
```

Golden Control is the team-facing operating cockpit for Golden installation, approved releases, usage/evidence, design rationale, progress, and onboarding. A local read-only prototype is included. It is not an application registry, production/deployment system, or raw observability store. Company-wide release and usage data require approved adapters in the existing team platform; unknown states must stay unknown.

## What's included

| Directory | What it contains |
|---|---|
| `.opencode/agents/` | Primary builder and scoped architecture, verification, docs, investigation roles |
| `.opencode/skills/` | 12 selectively loaded Golden workflows |
| `.opencode/commands/` | `/golden-build`, `/golden-audit`, `/golden-design`, `/golden-docs`, `/golden-triage`, `/golden-release`, `/golden-route` |
| `scripts/golden.py` | Working offline pilot rule evaluator, doctor, explanation and HTML evidence report |
| `scripts/golden_control.py` and `control/` | Local read-only operator dashboard for asset comparison, integrity, Golden evidence summaries, design, and onboarding |
| `standards/` | Version pin, 19 initial executable rule definitions (not the entire 151-requirement standard) |
| `tools/candidates.json` | Preserved 64 public GitHub source leads; not license approval |
| `research/capability-selection.json` | Pinned public capability candidates, observed license evidence, per-task rankings, and known gaps |
| [`fab_sampling_offline_port_kit/README.md`](fab_sampling_offline_port_kit/README.md) | Offline source-transfer guide and scripts; no fab data or downloaded source repositories bundled |
| `scripts/fetch_sources.py` | Public-network opt-in snapshot downloader/pinner; **source only** |
| `scripts/bootstrap_project.py` | Non-overwriting application manifest scaffold |
| `scripts/install_opencode.py` | Non-overwriting install of agent/skill/command files into chosen OpenCode config folder |
| `scripts/company_bootstrap.py` | Offline Step A doctor, reviewed add-only apply and hash-checked rollback |
| `scripts/golden_route.py` | Offline route resolver that checks references to installed Golden skills, agents, and configured MCP servers |
| `scripts/package_offline.py` | Clean-commit source-only archive with hidden assets, file hashes and external checksum |
| `workflows/task-routing.json` | 12 task routes with pattern, context, relevant skill/MCP, trust, fallback and acceptance |
| `research/capability-selection.json` | Candidate commits, observed license evidence, per-task decisions, and explicit unknowns |
| `research/react-license-supplements.json` | Three exact-commit React dependency notices, integrity hashes, and the unresolved archived `stackback` license action |
| `offline/` | Fail-closed policy template, Python attempt-monitor test scope, and missing staged assets |
| `examples/react-app/`, `examples/nicegui-app/` | Synthetic UI fixtures; React lock, partial macOS arm64 dependency audit, and hash-pinned supplemental license evidence are present; NiceGUI browserless UI simulation and local manual smoke are recorded. No transferable npm cache or Playwright browser binaries are staged |
| `docs/` | Architecture, phased company build plan, qualification criteria and draft requirements |
| `integrations/` | Vendor-neutral existing-CI and optional MCP configuration guidance |
| `tests/` and `examples/` | Real unit tests and minimal working sample |

## Tool selection

The project OpenCode config selects `golden-engineer` as the default primary agent on builds that support `default_agent`. Give it the objective directly: clear small fixes stay on the primary agent with no route command or extra skill; nontrivial work follows one route, invokes its named skill before tool selection, and checks only relevant specialist or already-connected approved MCP capabilities. The research registry ranks plausible candidates by task and separates public repositories from Golden-native/company capabilities. It is an evaluation baseline, not an installation list or performance result. Deterministic checks provide reproducible proof without replacing a useful agentic capability.

## Non-negotiable product behavior

- **Speed:** Authorized application owners direct OpenCode to edit/test/refactor/commit, including main when permitted. No Golden approvals per edit. CI deployment remains separate.
- **Consistency:** Apply a pinned Golden release, profile and reproducible rule set. Golden check logic must be deterministic and AI-independent.
- **Quality:** Every catalogued rule is assessed; applicable checks run; absent evidence is `NOT_RUN`, and inapplicability has an explicit basis. A fast check never pretends to be full release qualification.
- **Offline:** Company runtime uses only intranet, permitted internal AI, and approved offline dependencies. No public-net API, hidden downloads or mandatory paid accounts.
- **Human control:** Golden standard publication and production/irreversible operations require approval under existing company rules, not per-edit developer approval.
- **Clear ownership:** Golden Control shows Golden installation, releases, minimized usage/evidence, design and onboarding. Applications, hosting, raw feedback and production observability remain in the existing team platform.

## Current engineering truth

`v0.1.0-dev` is a **PRE_QUALIFICATION** pilot, not completed Golden. The local Golden Control prototype is read-only and does not connect to company installations, approved release feeds, or agent/MCP usage data. The 19 executable rule descriptors do not implement all 151 proposed requirements. The checker now refuses false capability declarations as non-applicability, allowlists a small set of deterministic test commands, omits raw command output, and replays project checks before rendering; imported JSON is not signed and does not prove execution authenticity. The company doctor never executes OpenCode; version metadata may be unavailable, and a public V2 candidate is not proof of internal compatibility. The transfer package contains only source, not locked dependencies, browsers, or approved model/runtime assets. Windows, company OpenCode, internal CI and task benchmarks remain **NOT_RUN**. See [`docs/QUALIFICATION_MATRIX.md`](docs/QUALIFICATION_MATRIX.md).

## Documentation

- [`docs/ARCHITECTURE_VIEW.html`](docs/ARCHITECTURE_VIEW.html) — self-contained visual system diagram (desktop/phone)
- [`docs/TOOL_BROWSER.html`](docs/TOOL_BROWSER.html) — offline searchable 64-source catalog
- [`COMPANY_START_HERE.md`](COMPANY_START_HERE.md) — exact offline doctor/apply steps for Windows and Linux
- [`PRECOMPANY_COMPLETION_REPORT.md`](PRECOMPANY_COMPLETION_REPORT.md) and [`PRECOMPANY_EVIDENCE.json`](PRECOMPANY_EVIDENCE.json) — executed checks, truthful blockers, and company handoff prompt
- [`RUNTIME_COMPATIBILITY_MATRIX.md`](RUNTIME_COMPATIBILITY_MATRIX.md) — local OpenCode probe versus company-only runtime requirements
- [`OFFLINE_ASSET_INVENTORY.json`](OFFLINE_ASSET_INVENTORY.json) and [`DEPENDENCY_LICENSE_REPORT.md`](DEPENDENCY_LICENSE_REPORT.md) — unstaged targets and unresolved review work
- [`COMPANY_ONLY_BLOCKERS.md`](COMPANY_ONLY_BLOCKERS.md) — exact owners and evidence needed for qualification
- [`START_HERE_COMPANY_OPENCODE.md`](START_HERE_COMPANY_OPENCODE.md) — historical runtime pilot prompt; follow the no-egress gate first
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — exact responsibilities and interfaces
- [`docs/FASTEST_IMPLEMENTATION.md`](docs/FASTEST_IMPLEMENTATION.md) — staged team adoption and acceptance
- [`docs/TOOL_ACQUISITION.md`](docs/TOOL_ACQUISITION.md) — license and offline source staging
- [`research/diagram-design-audit.md`](research/diagram-design-audit.md) — pinned GitHub skill audit and Golden's offline adaptation decision
- [`research/ui-ux-pro-max-audit.md`](research/ui-ux-pro-max-audit.md) — bounded React design-skill audit and offline adaptation decision
- [`docs/AGENTIC_FIRST_EVALUATION.md`](docs/AGENTIC_FIRST_EVALUATION.md) — compare agent/skill/MCP workflows with CLI candidates
- [`docs/GOLDEN_CONTROL_SPEC.md`](docs/GOLDEN_CONTROL_SPEC.md) — team UI, data boundaries, integration phases, and acceptance criteria
- [`docs/QUALIFICATION_MATRIX.md`](docs/QUALIFICATION_MATRIX.md) — real status vs intended features
- [`BUILD_VERIFICATION.md`](BUILD_VERIFICATION.md) — commands actually run and test artifacts
- [`docs/RELEASE_NOTES.md`](docs/RELEASE_NOTES.md) — this pre-qualification implementation and its limits
- [`docs/OPEN_CODE_COMPATIBILITY.md`](docs/OPEN_CODE_COMPATIBILITY.md) — V2 syntax and internal-version migration check
- [`docs/reference/README.md`](docs/reference/README.md) — private requirements deliberately excluded from GitHub package

**Source references:** [OpenCode agents](https://opencode.ai/docs/agents/), [skills](https://opencode.ai/docs/skills/), [commands](https://opencode.ai/docs/commands/), [MCP](https://opencode.ai/docs/mcp-servers/), [instructions](https://opencode.ai/docs/instructions/). Verify compatibility with the actual company version.
