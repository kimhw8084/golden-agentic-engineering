# Build verification — 2026-11-20

**Repository state:** `PRE_QUALIFICATION`; no company approval or qualification is asserted.

**Environment:** macOS 25.6.0 arm64; Python 3.11.7 for the latest repository and fixture runs; local NiceGUI 3.15.0; Node 26.13.0, npm 11.20.0. The local OpenCode path/version metadata is incomplete, so compatibility is `UNKNOWN`. Six required company/offline assets remain unstaged.

**Runtime boundary:** Results cover this checkout and synthetic fixtures. GitHub-hosted source CI passed on Ubuntu and Windows Server 2025 with Python 3.10, 3.11, and 3.14 (run [#14](https://github.com/kimhw8084/golden-agentic-engineering/actions/runs/44852954221), commit `e0466c6`). Neither this matrix nor the loopback audit-hook test qualifies company-managed hosts, company OpenCode, the internal model, firewall policy, or company network behavior.

## Tests and checks run

| Check | Result |
|---|---|
| [GitHub Actions source qualification matrix](https://github.com/kimhw8084/golden-agentic-engineering/actions/runs/44852954221) | PASS — run #14 at `e0466c6`; six jobs on Ubuntu and Windows Server 2025 × Python 3.10/3.11/3.14. Each ran the repository unit suite, route/manifest validation, credential-pattern scan, and Golden fast checks. Hosted runners are not company or air-gap evidence. |
| `python -m unittest discover -s tests -v` | PASS — 76 repository tests. Covers bootstrap doctor/apply/repeat/rollback, default config-root selection and safe fresh-root creation, staged asset evidence, npm audit safeguards, offline React/NiceGUI fixture runners and skip reporting, benchmark case/status validation, transfer-kit path/origin/symlink/overwrite checks, Golden Proof, routing, MCP fixture, security scanner, loopback Python audit-hook interception, and synthetic scenarios. |
| `examples/nicegui-app`: `python -m unittest discover -s tests -v` | PASS — 3 standard-library logic tests; the NiceGUI UI simulation is skipped outside pytest. |
| `examples/nicegui-app`: `pytest -q tests/test_ui.py` | PASS — NiceGUI `user_simulation` exercised required-field validation, ACCEPT and REVIEW states, duplicate-ID rejection, summary counts, and clearing. No browser process is required. |
| `python benchmarks/run_local_fixtures.py --include-react --include-nicegui-ui --out verification/2026-11-20/local-fixtures.json` | PASS — 48 Python fixture cases discovered (47 passed; one optional UI test skipped in the site-isolated unittest run), one NiceGUI `user_simulation` test passed with NiceGUI 3.15.0/pytest 8.4.2, and six React logic/component tests. React `npm ci` ran with `--offline --ignore-scripts --no-audit --no-fund`, then typecheck, Vitest, and Vite build. Playwright automation remains unrun. This is not an agent or productivity comparison. |
| React `npm ci --offline --ignore-scripts --no-audit --no-fund` | PASS — 82 packages installed from the local npm cache on macOS arm64; no lifecycle scripts. |
| React `npm run typecheck`, `npm run test`, `npm run build` | PASS — TypeScript clean; six tests across two files; Vite transformed 30 modules. |
| `python3 scripts/npm_dependency_audit.py --report research/react-macos-arm64-dependency-audit.json --sbom research/react-macos-arm64.cdx.json` | PASS — lock has 132 entries; 82 installed and included in CycloneDX; 50 platform variants are not staged. License metadata: zero missing and zero unknown/non-OSI IDs in the installed set; four installed packages have no bundled license text. Company clearance is pending. |
| Local browser smoke on `http://127.0.0.1:5173/` | PASS — in-app browser rendered labeled controls, keyboard Tab/Enter submission produced an ACCEPT result, and clearing the numeric field showed “Measured value is required.” The app served on loopback. This is manual UI evidence, not Playwright automation or a formal accessibility audit. See [the observation](verification/2026-11-20/react-browser-smoke.md). |
| Local browser smoke on `http://127.0.0.1:8080/` | PASS — in-app browser checked required-field validation, ACCEPT and REVIEW results, duplicate-ID rejection without changing counts, and clear/reset behavior. This manual smoke is separate from the pytest simulation; it is not Playwright automation or a formal accessibility audit. See [the observation](verification/2026-11-20/nicegui-browser-smoke.md). |
| Golden Control local browser smoke | PASS — the overview rendered and showed local checkout/status values while leaving company installation, update feed, and agent/MCP usage unknown. See [the observation](verification/2026-11-20/control-browser-smoke.md). |
| Bootstrap transaction tests (included above) | PASS — synthetic CLI doctor → reviewed apply → repeat apply → rollback preserved provider/model settings; fresh config-root creation, invalid-archive no-write behavior, JSONC shape-only reading, and symlink/path rejection passed. |
| `python scripts/validate_manifests.py` | PASS — 19 rule descriptors, 64 preserved public-source leads, 12 workflows, 5 agents, 12 skills, 7 commands, 27 capability candidates, 17 task decisions, and six benchmark cases with repository evidence references. Hash-checked partial React evidence does not upgrade its asset status from `NOT_STAGED`. |
| `python scripts/security_scan.py` | PASS — 164 files scanned; no high-confidence credential patterns found and no values emitted. This is not a complete secret or proprietary-code review. |
| `python3 scripts/network_attempt_monitor.py` | PASS — an actual Python `socket.connect` call to `127.0.0.1:9` was observed and rejected by the audit hook before the socket operation proceeded; no public address was targeted. This verifies only this CPython call path, not hostile-code containment, child-process monitoring, or OS firewall behavior. |
| `node --check control/app.js` | PASS — JavaScript syntax. |
| `python3 scripts/golden_route.py --task-id technical-docs-sop-diagrams` | PASS — resolves the docs skill, lists `cathrynlavery/diagram-design` as evaluation-only, and names local Markdown/SVG/Mermaid fallback. No third-party tool was installed or invoked. |
| `python3 scripts/golden.py doctor --project examples/python-app` | PASS — project manifest valid and local Python test command configured. |
| `python3 scripts/golden.py check --fast --project examples/python-app` | Executed checks pass; release qualification is false. Missing applicability evidence stays `NOT_RUN`. |
| `python3 scripts/golden.py check --full --project examples/python-app` | Completed, non-qualified (exit 2) — ten blockers: `AI-001`, `API-001`, `DATA-001`, `DB-001`, `JOBS-001`, `MCP-001`, `OPS-001`, `PY-003`, `REL-001`, `SEC-001`. No missing evidence was changed to PASS or an exception. |
| `python3 scripts/golden.py check --full --project examples/nicegui-app --out verification/2026-11-20/nicegui-full-current.json` | Completed, non-qualified (exit 2) — `UI-001` passed through the constrained pytest runner; `UI-002` remained `NOT_RUN` because browser automation is unstaged. Eleven mandatory evidence blockers remain. [Fresh-replay HTML report](verification/2026-11-20/nicegui-full-current.html) generated successfully. |
| `python3 scripts/golden.py report --input verification/2026-11-20/golden-full-current.json --project examples/python-app --out verification/2026-11-20/golden-full-current.html` | PASS — report generated by replaying checks against the project. |
| `python3 scripts/company_bootstrap.py doctor --out /private/tmp/golden-doctor-current.json` | Local inspection only; company assets and runtime compatibility remain unknown. No settings changed. |

The synthetic stdio MCP fixture remains disabled in OpenCode configuration. It tests discovery/call shapes, scope, errors, injection-like input as inert data, direct-handler timeout/cancellation, and JSON-lines framing. It is not SDK-backed protocol conformance and provides no authentic OpenCode invocation trace. Golden Control's route test calls its handler in memory.

## Recorded evidence

- [Local fixture run](verification/2026-11-20/local-fixtures.json) — Python/React checks, durations and output hashes.
- [FAST Golden result](verification/2026-11-20/golden-fast-current.json) — not release-qualified.
- [FULL Golden result](verification/2026-11-20/golden-full-current.json) and [HTML report](verification/2026-11-20/golden-full-current.html) — ten mandatory evidence blockers.
- [React dependency inventory](research/react-macos-arm64-dependency-audit.json) and [CycloneDX SBOM](research/react-macos-arm64.cdx.json) — macOS arm64 installed subset only.

JSON evidence is unsigned and cannot authenticate who ran a check or prove that an OpenCode agent, skill, MCP, or CLI was invoked.

## Not tested / remaining limits

- Company-managed Windows/Linux hosts; platform-specific Node/npm caches, and apply/rollback qualification against actual company OpenCode installations.
- Playwright browser automation and a formal accessibility audit. NiceGUI UI simulation and local manual browser smoke were run on this workstation only.
- Company OpenCode discovery, agent/skill use, internal model, connected MCPs, or invocation-event provenance.
- OS-enforced no-public-egress policy and attempt monitoring across OpenCode and all child processes.
- Full dependency/source license closure, the four missing npm license texts, company OSS clearance, and staged Windows/Linux executable assets.
- Paired agentic-vs-CLI or plain-OpenCode-vs-Golden measurements. No uplift, latency, token, request, or productivity claims are made.
- Company CI/artifact/SSO integration.

See [the qualification matrix](docs/QUALIFICATION_MATRIX.md), [offline asset manifest](offline/assets-manifest.json), and [company open items](OPEN_ITEMS_FOR_COMPANY.md) for current gaps and owners.
