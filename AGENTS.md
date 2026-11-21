# Golden Agentic Engineering — project instructions

This repository is a **Golden engineering toolchain**. It is not the company's application platform.

## Operating contract

- Work fast and make authorized source changes directly. Do **not** request a Golden approval for every edit, test, command or authorized commit to `main`.
- Never presume production/deployment rights. Existing company security and explicit human approval govern irreversible/production actions.
- Prefer adapting qualified public OSS tools over building replacements. New imports require company clearance, OSI licensing, dependency/license review and offline qualification.
- Keep Golden Control limited to standards, approved tooling, versioning and customization. Application hosting, observability UI and application feedback belong to the separate team platform.
- Make deterministic tools authoritative for PASS/FAIL. Never treat a model's confident prose as executed evidence.
- For a repository audit, assess **every** Golden rule: execute relevant checks; record `NOT_APPLICABLE` with a reason, `NOT_RUN` when evidence is missing, or `DEFERRED` in fast-only runs.
- Keep clear small tasks on the primary agent without opening the route manifest or loading an extra skill. For nontrivial or ambiguous tasks, route through `workflows/task-routing.json` and load only a task-relevant skill when it changes the method or reduces a concrete risk. Inspect only relevant, already-connected and approved specialists/MCP capabilities; do not skip one in favor of a CLI by habit. Use deterministic tools for proof or when matched evidence shows they fit better. For explicit tool-selection work, check `research/capability-selection.json`, inspect live compatibility/permissions, and compare plausible options on the same acceptance criteria. Keep discovery proportional; do not load every skill or invoke every tool as ceremony. Never claim unobserved tool use or performance.
- Build/packaging/CI must work offline with the model unavailable. No runtime public internet, telemetry uploads, or downloads.
- Reduce context use: read the smallest relevant `SKILL.md` and referenced policy; do not preload the entire requirements draft or tool catalog.

## Project structure

`standards/` is the draft normative rule catalog. `.opencode/agents/`, `.opencode/skills/`, and `.opencode/commands/` are OpenCode-facing assets. `scripts/golden.py` is a working **pilot** rule runner (stdlib Python >=3.10). `scripts/golden_control.py` serves the local, read-only Golden Control UI from `control/`; its company-wide inventory, release, and usage integrations are not implemented. `docs/AGENTIC_FIRST_EVALUATION.md` defines capability discovery and evidence-based tool selection, and `docs/GOLDEN_CONTROL_SPEC.md` defines the team cockpit and its phased company integration. `tools/candidates.json` is an acquisition candidate catalog, **not** a license or security approval.

## Local checks before proposing a Golden release

```bash
python -m unittest discover -s tests -v
python scripts/golden.py doctor --project examples/python-app
python scripts/golden.py check --fast --project examples/python-app
python scripts/golden.py list
```

For full evaluation, explicitly interpret `NOT_RUN` as a release blocker unless recorded company exception exists (not implemented in this pilot). Do not fabricate coverage.

## Instruction precedence

Most recent explicit team lead decision > approved internal Golden release > project-specific app contract > this development guidance. Company security and legal requirements always apply. Published Golden standards require explicit team lead approval.

## OpenCode version warning

The files in this repository target publicly documented OpenCode V2 paths and semantics as consulted Nov 2026. Your internal OpenCode may differ. Inspect its version/help/config behavior and adapt with tests before rolling out; do not overwrite internal provider/model settings.
