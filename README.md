# Golden Agentic Engineering System

**GitHub-ready starter · v0.1.0-dev · NOT company qualified · NOT a standards release**

A lightweight **OpenCode-first agentic engineering standards toolkit** for a 10-person team. This repository contains functioning Python-standard-library verification scaffolding, OpenCode agents/skills/commands, a real candidate OSS manifest, opt-in public-source staging, and company deployment instructions. It deliberately does **not** host company engineering applications or replace the existing CI, Git, artifact registry, Prometheus, Grafana or Splunk.

The primary OpenCode agent is the default reasoning/routing layer. For routine tasks, use only clearly relevant skills and already-known authorized integrations; broad inventories, benchmarks, and invocation ledgers are not required per task. Inspect live capabilities and compare agentic, MCP, CLI, or hybrid options when a selection decision, material uncertainty, changed runtime baseline, or qualification requires it. A CLI must demonstrate value for that operation. See [`docs/AGENTIC_FIRST_EVALUATION.md`](docs/AGENTIC_FIRST_EVALUATION.md).

> **You can push this repository to GitHub now.** You cannot claim it or its OSS candidates are company-cleared or offline-runnable before internal qualification. No external dependencies are shipped by default.

## Fastest start from a phone

1. Download the repository ZIP from ChatGPT and upload it to Codex.
2. Give Codex the exact prompt in [`CODEX_PUBLISH_PROMPT.md`](CODEX_PUBLISH_PROMPT.md). Choose a new **private** GitHub repository unless the information owner approves public publication. This starter includes project-specific requirements and internal workflow assumptions.
3. Review the created repository, then transfer only company-approved content through your approved import process.
4. On the work PC, open [`START_HERE_COMPANY_OPENCODE.md`](START_HERE_COMPANY_OPENCODE.md), paste the included prompt into the internal OpenCode, and let it inspect the local environment before making changes.

## What works without external packages today

```text
python -m unittest discover -s tests -v
python scripts/golden.py list
python scripts/golden.py doctor --project examples/python-app
python scripts/golden.py check --fast --project examples/python-app
python scripts/golden.py check --full --project examples/python-app --out out/evidence.json
python scripts/golden.py report --input out/evidence.json --out out/evidence.html
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
| `.opencode/commands/` | `/golden-build`, `/golden-audit`, `/golden-design`, `/golden-docs`, `/golden-triage`, `/golden-release` |
| `scripts/golden.py` | Working offline pilot rule evaluator, doctor, explanation and HTML evidence report |
| `scripts/golden_control.py` and `control/` | Local read-only operator dashboard for asset comparison, integrity, Golden evidence summaries, design, and onboarding |
| `standards/` | Version pin, 19 initial executable rule definitions (not the entire 151-requirement standard) |
| `tools/candidates.json` | 63 public GitHub source candidates, grouped by acquisition priority |
| `scripts/fetch_sources.py` | Public-network opt-in snapshot downloader/pinner; **source only** |
| `scripts/bootstrap_project.py` | Non-overwriting application manifest scaffold |
| `scripts/install_opencode.py` | Non-overwriting install of agent/skill/command files into chosen OpenCode config folder |
| `docs/` | Architecture, phased company build plan, qualification criteria and draft requirements |
| `integrations/` | Vendor-neutral existing-CI and optional MCP configuration guidance |
| `tests/` and `examples/` | Real unit tests and minimal working sample |

## Tool selection

For the initial company pilot, establish and reuse a baseline of actual available agents, skills, and approved MCP capabilities. On routine tasks, let the primary agent route to only relevant capabilities; run a comparison only when a CLI is a plausible alternative, the user asks for one, or qualification requires it. Select agentic, CLI, or hybrid capabilities by evidence, per operation. The candidate source catalog is not a capability ranking. See [`docs/AGENTIC_FIRST_EVALUATION.md`](docs/AGENTIC_FIRST_EVALUATION.md).

## Non-negotiable product behavior

- **Speed:** Authorized application owners direct OpenCode to edit/test/refactor/commit, including main when permitted. No Golden approvals per edit. CI deployment remains separate.
- **Consistency:** Apply a pinned Golden release, profile and reproducible rule set. Golden check logic must be deterministic and AI-independent.
- **Quality:** Every catalogued rule is assessed; applicable checks run; absent evidence is `NOT_RUN`, and inapplicability has an explicit basis. A fast check never pretends to be full release qualification.
- **Offline:** Company runtime uses only intranet, permitted internal AI, and approved offline dependencies. No public-net API, hidden downloads or mandatory paid accounts.
- **Human control:** Golden standard publication and production/irreversible operations require approval under existing company rules, not per-edit developer approval.
- **Clear ownership:** Golden Control shows Golden installation, releases, minimized usage/evidence, design and onboarding. Applications, hosting, raw feedback and production observability remain in the existing team platform.

## Current engineering truth

`v0.1.0-dev` is a functional **pilot foundation**, not completed Golden. The local Golden Control prototype is read-only and does not connect to company installations, approved release feeds, or agent/MCP usage data. The 19 rule descriptors are only initial enforcement scaffolding. Most full checks require configuration of approved external tools; no external executables are bundled. License hints are not verified. OpenCode files target public OpenCode V2 documentation (Nov 2026), not proven internal compatibility. Windows and internal CI tests have **NOT_RUN** status. See [`docs/QUALIFICATION_MATRIX.md`](docs/QUALIFICATION_MATRIX.md).

## Documentation

- [`docs/ARCHITECTURE_VIEW.html`](docs/ARCHITECTURE_VIEW.html) — self-contained visual system diagram (desktop/phone)
- [`docs/TOOL_BROWSER.html`](docs/TOOL_BROWSER.html) — offline searchable 63-source catalog
- [`START_HERE_COMPANY_OPENCODE.md`](START_HERE_COMPANY_OPENCODE.md) — what to do at work
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — exact responsibilities and interfaces
- [`docs/FASTEST_IMPLEMENTATION.md`](docs/FASTEST_IMPLEMENTATION.md) — staged team adoption and acceptance
- [`docs/TOOL_ACQUISITION.md`](docs/TOOL_ACQUISITION.md) — license and offline source staging
- [`docs/AGENTIC_FIRST_EVALUATION.md`](docs/AGENTIC_FIRST_EVALUATION.md) — compare agent/skill/MCP workflows with CLI candidates
- [`docs/GOLDEN_CONTROL_SPEC.md`](docs/GOLDEN_CONTROL_SPEC.md) — team UI, data boundaries, integration phases, and acceptance criteria
- [`docs/QUALIFICATION_MATRIX.md`](docs/QUALIFICATION_MATRIX.md) — real status vs intended features
- [`docs/OPEN_CODE_COMPATIBILITY.md`](docs/OPEN_CODE_COMPATIBILITY.md) — V2 syntax and internal-version migration check
- [`docs/reference/README.md`](docs/reference/README.md) — private requirements deliberately excluded from GitHub package

**Source references:** [OpenCode agents](https://opencode.ai/docs/agents/), [skills](https://opencode.ai/docs/skills/), [commands](https://opencode.ai/docs/commands/), [MCP](https://opencode.ai/docs/mcp-servers/), [instructions](https://opencode.ai/docs/instructions/). Verify compatibility with the actual company version.
