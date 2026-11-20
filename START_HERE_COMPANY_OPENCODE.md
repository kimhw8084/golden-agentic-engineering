# On your work PC — start here

**Status: unqualified bootstrap.** Transfer only through company-approved channels, with appropriate source-code and OSS/security review. This repo is development guidance; it does not grant company permissions.

## Phase 0 — inspection first (copy into INTERNAL OpenCode)

> You are the implementation lead for our Golden Agentic Engineering System pilot. This is a standards/skills/tools verification toolkit with a first-class Golden Control UI; it is not the team's application-hosting platform. Read `AGENTS.md`, `README.md`, `docs/ARCHITECTURE.md`, `docs/FASTEST_IMPLEMENTATION.md`, `docs/QUALIFICATION_MATRIX.md`, `docs/AGENTIC_FIRST_EVALUATION.md`, `docs/GOLDEN_CONTROL_SPEC.md`, `docs/reference/README.md`, `standards/rules.json`, `.opencode/`, `control/`, `scripts/golden_control.py`, and the candidate OSS manifest. Do not blindly fetch public GitHub URLs from the intranet or change our existing OpenCode provider/model settings.
>
> First inspect the ACTUAL installed OpenCode version and inventory its primary/specialist agents, skills, connected MCP servers/tools, permissions, and orchestration/handoff features. Also inspect Python/Node/portable executable environment, Windows/Linux qualification targets, internal Git/CI/artifact arrangements, approved OSS availability, FastAPI deployment limits, and existing project conventions. Do not assume a capability exists because a file or catalog lists it.
>
> This is the one-time Phase 0 baseline for the installed version/configuration. Reuse it for routine tasks while version, configuration, and permission scope remain unchanged; do not repeat a full inventory or benchmark per task. For routine delivery, use the primary agent and only clearly relevant skills/known integrations. A separate capability comparison is needed only for a selection decision, material uncertainty, baseline change, or qualification requirement.
>
> For the initial representative authorized fixture task, define observable acceptance criteria. Exercise the best-fit agentic workflow first: primary agent plus relevant skill, adding a specialist or already-approved MCP tool only when its contribution justifies coordination. Compare a CLI only when it is a plausible alternative for that operation. Record the actual calls/results and elapsed time for this pilot. Choose per capability; a CLI must demonstrate that it outperforms the agentic option on the relevant criteria. A hybrid may be strongest. Do not enable/install unapproved services or force irrelevant MCP calls or agent swarms. Distinguish trusted runtime events from human observation or model self-report; if no runtime trace source exists, mark provenance unavailable and do not build a new collector. Follow [`docs/AGENTIC_FIRST_EVALUATION.md`](docs/AGENTIC_FIRST_EVALUATION.md).
>
> Produce a verified/unverified/blocked matrix and list the minimal pilot changes. Follow speed-first policy: no approval gates for routine developer edits, tests or authorized commits. Preserve production approval boundaries. After inspection, implement the smallest working pilot on one React and one NiceGUI/Python example, with independent no-AI checks and measured development speed. Do not claim tests you haven't executed, and obtain the company authorization required for software import or production operations.
>
> Golden Control is a required but bounded part of the team-ready design. Audit the existing dashboard before proposing changes; preserve and extend it only within its scope: Golden installation/configuration, releases, qualification evidence, design, progress and onboarding. It may show minimal aggregates from existing approved systems read-only; it must not grow an event collector, productivity dashboard, application registry, deployment controller, or observability store. Never fake installation, release, usage, or invocation provenance. Follow `docs/GOLDEN_CONTROL_SPEC.md` and keep application hosting/feedback in the existing team platform.

### One-time agentic-first evaluation for the initial pilot

Follow [`docs/AGENTIC_FIRST_EVALUATION.md`](docs/AGENTIC_FIRST_EVALUATION.md). During Phase 0, inspect the actual internal OpenCode installation for primary and specialist agents, skill discovery, connected MCP servers and tools, permissions, and orchestration/handoff features. Do not treat this repository's files or the CLI candidate catalog as proof that a capability is available. Record the baseline once for the verified runtime/configuration and refresh it only when the version, configuration, or permission scope changes; this is not a per-task checklist.

For the initial pilot's representative authorized fixture task, exercise the best-fit primary agent plus relevant skill first. Add a specialist agent or an already-approved MCP tool only when it is likely to materially help. Compare a CLI only if it is a plausible alternative for that operation. Record the actual calls/results and elapsed time for this benchmark, with provenance class if a trusted runtime event source exists. Choose the best-performing capability per operation; a CLI must demonstrate that it outperforms the agentic workflow on the relevant criteria. A hybrid may be strongest. Do not answer with a CLI-only recommendation without first evaluating relevant agentic capabilities. If a capability cannot be used, record whether it is unavailable, incompatible, unauthorized, or unqualified and why. Do not enable/install unapproved services or force irrelevant MCP calls or agent swarms. This benchmark is not repeated on routine tasks.

## Commands that already work with Python >=3.10

From Golden repository directory:

```sh
python -m unittest discover -s tests -v
python scripts/golden.py list
python scripts/golden.py check --fast --project examples/python-app
python scripts/golden.py check --full --project examples/python-app --out out/demo.evidence.json
python scripts/golden.py report --input out/demo.evidence.json --out out/demo.report.html
python scripts/golden_control.py --evidence-dir out
```

The full check is expected to return nonzero because it sees missing configured independent tools. **Do not waive it, suppress it or print a fake PASS.**

## Inspect OpenCode before copying agents globally

- Validate `.opencode/agents/*.md`, `skills/*/SKILL.md`, `commands/*.md`, and `.opencode/opencode.json` against **installed company OpenCode**. Public docs referenced in README target V2 and may not match internal version.
- Do NOT replace the existing provider/model configuration.
- If the format is compatible, use the dry-run installer with a specific already-existing OpenCode config directory: `python scripts/install_opencode.py --target <CONFIG_DIR>`. Then `--apply` after review. It never overwrites a conflicting file and never enables MCP.
- Use `python scripts/bootstrap_project.py --target <EXISTING_PROJECT_DIR> --name "Your App" --profile react` in dry-run mode; `--apply` only when the project owner agrees. Review declared capabilities and add actual test commands.
- For the initial pilot only, check relevant agent/skill discovery, approved MCP calls when useful, and `/golden-build` on a real small code change. Compare the agentic workflow with plausible CLI alternatives on the same acceptance criteria; record actual calls/results and provenance limits. Reuse this baseline for routine tasks.
- Open Golden Control with `python scripts/golden_control.py --target <EXISTING_CONFIG_DIR> --evidence-dir out`. Supply only a real existing config directory you have checked; verify displayed status against source files. Keep company-wide release/usage integrations marked unavailable until their approved sources are connected.

## Existing company Git/CI integration

The same pinned Golden version must be available locally and to CI. Fast checks should run locally/at commit; full evaluations on demand, before release, or after lead-approved standards changes **and application-owner CI approval**. Golden Control does not hold app compliance results. Production publication remains a separate existing company process.

## Import third-party tools, with approvals

On public staging PC: `python scripts/fetch_sources.py --tier pilot --limit 3` previews candidate GitHub sources. `--apply` downloads archives and creates source commit/hash lock. **Source archive does not contain complete offline executable installs.** Stage exactly qualified native binaries, Node/Python dependencies, Playwright browser binaries, vulnerability DBs and LICENSE/NOTICE files independently. Ask company security/license owner to clear the packages. Follow `docs/TOOL_ACQUISITION.md`.

## First real pilot finish line

- Internal OpenCode has proven actual agent/skill compatibility and task-relevant approved MCP calls where available, without replacing provider configuration; the workflow has been compared against CLI alternatives on the same task.
- One new app and one existing app both use the same pinned Golden profile, with no artificial edit gates.
- Fast checks measured, full checks enumerate every rule with PASS/FAIL/NOT_APPLICABLE/NOT_RUN evidence.
- Company CI runs the same deterministic checks independently and retains reports.
- Windows/Linux and AI-disabled tests are demonstrated; owner-approved exception mechanism is integrated.
- Team lead reviews testing and authorizes the next phase. **Do not claim team-ready before this.**
