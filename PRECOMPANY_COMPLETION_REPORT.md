# Pre-company completion report

**Release state: `PRE_QUALIFICATION`.** This report records source-side work and evidence available on 2026-11-21. It does not qualify a company workstation, approve third-party software, or authorize production use.

## Completed and verified

- Preserved the existing OpenCode project structure, including all `.opencode/agents`, `.opencode/skills`, and `.opencode/commands`. The company bootstrap remains add-only and does not copy project provider/model/auth or MCP configuration.
- Kept the repo's 12 routed workflows, 5 agents, 12 skills, 7 commands, 19 pilot rule descriptors, 34 typed capability candidates, 17 task-level capability decisions, and 64 original source-candidate baseline. The earlier 107 decisions remain provisional; 151 requirements remain proposals, not executable checks.
- Kept the upstream `cathrynlavery/diagram-design` repository represented by its bounded audit and attributed offline documentation method. It remains an evaluation source, not an approved or performance-qualified tool.
- Ran 155 Python tests: 154 passed, one optional-SDK test skipped under the default interpreter, and zero failed. The SDK-backed fixture also passed in the offline SDK virtual environment. Manifest validation, tracked-content checksums, local React, NiceGUI, API/SQLite, incident, manufacturing, routing, proof and synthetic MCP fixtures, offline React install/typecheck/tests/build, network-hook check, and secret-pattern scan passed. Exact scan scope and runtime evidence are recorded in [`PRECOMPANY_EVIDENCE.json`](PRECOMPANY_EVIDENCE.json) and [`verification/2026-11-21/`](verification/2026-11-21/).
- Ran Golden full checks against each Python, React, and NiceGUI example. Their statuses are preserved in the evidence files; all three remain non-qualified because required checks and independent applicability evidence are missing.
- Ran the local doctor without changing settings. On this non-company host it returned `UNKNOWN`, with six offline asset groups missing. This is not company readiness evidence.
- Audited the fab sampling transfer kit: all 38 repositories remain candidates; no repository source, wheelhouse, model, or dataset was staged.
- Added `scripts/precompany_readiness.py`, a one-command offline assessment that reruns the local test, manifest, checksum, secret-pattern, network-hook, rollback, React/NiceGUI fixture, and Golden full-check paths. It emits JSON and Markdown outside the source tree by default and remains fail-closed at `PRE_QUALIFICATION` until company-owned evidence is supplied.

## Findings that block qualification

- The installed local OpenCode V1 binary is not the V2-shaped target used by this repo. It rejects the repo's `mcp.servers` configuration. A temporary V1-compatible test configuration reached a local-only synthetic provider and exposed the `skill` tool, but the skill call failed when the host sandbox blocked the `rg` subprocess. No authentic company model, skill completion, specialist handoff, or MCP call was observed.
- A checksum-verified public OpenCode V2.2.7 candidate was tested with a scripted loopback provider. Without `OPENCODE_DISABLE_MODELS_FETCH=1`, its logs showed an attempted public model catalog fetch; macOS Seatbelt denied non-loopback networking. With the variable set, no catalog-fetch event appeared in captured logs. The project denies `webfetch` and `websearch`, and the V2 probe confirmed those tools were absent. The probe environment also set `OPENCODE_DISABLE_AUTOUPDATE=1`, but updater traffic was not separately monitored. These local observations are not packet capture and do not replace the company's Windows/Linux firewall policy or endpoint attempt monitoring.
- The React lock has one remaining `stackback@0.0.2` MIT notice-text gap. Its exact upstream declaration and source hashes are now recorded, along with its embedded V8 BSD notice. A Vitest 5 update may remove this dependency but raises the Node minimum to 22.12 and has not been tested. Company OSS review remains outstanding.
- The repository is a source bundle, not an offline executable distribution. A hash-locked official MCP SDK v2.3.0 candidate set was staged outside Git for macOS arm64, Windows AMD64, and Linux x86-64/glibc 2.17. Only the macOS wheels were installed and tested offline; the Windows/Linux sets are cross-target candidates. The OpenCode v2.2.7 MCP handshake failed against both the SDK server and the existing synthetic server. Company-approved Python dependencies, Windows/Linux npm caches, Playwright browsers, company runtime compatibility evidence, and OS-enforced egress evidence remain unavailable.
- The local benchmark harness measures deterministic fixture checks, not accepted agent task results. Plain OpenCode versus Golden quality, time, rework, latency, and trusted token/request comparisons are `BLOCKED_COMPANY_RUNTIME`.

## Repository and release boundary

The repository remains public at [github.com/kimhw8084/golden-agentic-engineering](https://github.com/kimhw8084/golden-agentic-engineering); this work does not change its visibility. Keep company code, names, endpoints, credentials, data, and runtime traces out of this repository. The report and checker artifacts contain only synthetic/local evidence. Golden Control remains a read-only tooling and qualification cockpit; the existing company application platform retains hosting, feedback, and observability ownership.

Use the two Windows/Linux Step A and reviewed Step B commands in [`COMPANY_START_HERE.md`](COMPANY_START_HERE.md). Do not mark the starter company-qualified until the blockers in [`COMPANY_ONLY_BLOCKERS.md`](COMPANY_ONLY_BLOCKERS.md) are closed and the team lead records the release decision.

## Immediate company customization prompt

> On an approved Windows or Linux pilot workstation, first run only the Golden Step A doctor command. Do not start OpenCode or change any settings. Return the sanitized doctor JSON plus the company software inventory's exact OpenCode build/version, config format, Python/Node/OS/architecture targets, approved internal model identifier, and the security owner's default-deny egress/attempt-monitor evidence. Do not include endpoints with credentials, secrets, company source, or user data. Stop if any field is unknown; identify its owner and the single exact action needed.
