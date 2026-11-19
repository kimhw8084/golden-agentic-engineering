# On your work PC — start here

**Status: unqualified bootstrap.** Transfer only through company-approved channels, with appropriate source-code and OSS/security review. This repo is development guidance; it does not grant company permissions.

## Phase 0 — inspection first (copy into INTERNAL OpenCode)

> You are the implementation lead for our Golden Agentic Engineering System pilot. This is a standards/skills/tools verification toolkit, NOT the team's application-hosting platform. Read `AGENTS.md`, `README.md`, `docs/ARCHITECTURE.md`, `docs/FASTEST_IMPLEMENTATION.md`, `docs/QUALIFICATION_MATRIX.md`, `docs/reference/README.md`, `standards/rules.json`, `.opencode/` and the candidate OSS manifest. Do not blindly fetch public GitHub URLs from the intranet or change our existing OpenCode provider/model settings. First inspect the ACTUAL installed OpenCode version/agent/skill/command/MCP syntax, Python/Node/portable executable environment, Windows/Linux qualification targets, internal Git/CI/artifact arrangements, approved OSS availability, FastAPI deployment limits and existing project conventions. Produce a verified/unverified/blocked matrix; list the minimal pilot changes. Follow speed-first policy: no approval gates for routine developer edits, tests or authorized commits. Preserve production approval boundaries. After inspection, implement the smallest working pilot on one React and one NiceGUI/Python example, with independent no-AI checks and measured development speed. Do not claim tests you haven't executed, and obtain the company authorization required for software import or production operations.

## Commands that already work with Python >=3.10

From Golden repository directory:

```sh
python -m unittest discover -s tests -v
python scripts/golden.py list
python scripts/golden.py check --fast --project examples/python-app
python scripts/golden.py check --full --project examples/python-app --out out/demo.evidence.json
python scripts/golden.py report --input out/demo.evidence.json --out out/demo.report.html
```

The full check is expected to return nonzero because it sees missing configured independent tools. **Do not waive it, suppress it or print a fake PASS.**

## Inspect OpenCode before copying agents globally

- Validate `.opencode/agents/*.md`, `skills/*/SKILL.md`, `commands/*.md`, and `.opencode/opencode.json` against **installed company OpenCode**. Public docs referenced in README target V2 and may not match internal version.
- Do NOT replace the existing provider/model configuration.
- If the format is compatible, use the dry-run installer with a specific already-existing OpenCode config directory: `python scripts/install_opencode.py --target <CONFIG_DIR>`. Then `--apply` after review. It never overwrites a conflicting file and never enables MCP.
- Use `python scripts/bootstrap_project.py --target <EXISTING_PROJECT_DIR> --name "Your App" --profile react` in dry-run mode; `--apply` only when the project owner agrees. Review declared capabilities and add actual test commands.
- Check that agent names, skill discovery and `/golden-build` work on your internal model with a real small code change.

## Existing company Git/CI integration

The same pinned Golden version must be available locally and to CI. Fast checks should run locally/at commit; full evaluations on demand, before release, or after lead-approved standards changes **and application-owner CI approval**. Golden Control does not hold app compliance results. Production publication remains a separate existing company process.

## Import third-party tools, with approvals

On public staging PC: `python scripts/fetch_sources.py --tier pilot --limit 3` previews candidate GitHub sources. `--apply` downloads archives and creates source commit/hash lock. **Source archive does not contain complete offline executable installs.** Stage exactly qualified native binaries, Node/Python dependencies, Playwright browser binaries, vulnerability DBs and LICENSE/NOTICE files independently. Ask company security/license owner to clear the packages. Follow `docs/TOOL_ACQUISITION.md`.

## First real pilot finish line

- Internal OpenCode has proven actual skills/agent compatibility, without replacing provider configuration.
- One new app and one existing app both use the same pinned Golden profile, with no artificial edit gates.
- Fast checks measured, full checks enumerate every rule with PASS/FAIL/NOT_APPLICABLE/NOT_RUN evidence.
- Company CI runs the same deterministic checks independently and retains reports.
- Windows/Linux and AI-disabled tests are demonstrated; owner-approved exception mechanism is integrated.
- Team lead reviews testing and authorizes the next phase. **Do not claim team-ready before this.**
