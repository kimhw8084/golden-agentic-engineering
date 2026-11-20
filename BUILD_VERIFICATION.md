# Build verification — 2026-11-20

**Repository state:** `PRE_QUALIFICATION`; no company approval is asserted.

**Environment:** macOS 25.6.0, arm64, Python 3.14.5. The local doctor found Git, Python, Node, and OpenCode executables, but no approved-inventory Node/OpenCode versions were supplied; compatibility therefore remains `UNKNOWN`. Six required offline assets are not staged.
**Runtime boundary:** these results cover this local checkout and synthetic fixtures only. They are not Windows, company OpenCode, internal model, firewall, hosted CI, or company network evidence.

## Tests and checks run

| Check | Result |
|---|---|
| `python3 -m unittest discover -s tests -v` | PASS — 33 tests, including bootstrap collision/rollback, source archive reproducibility, Golden Proof, local control-route handler, synthetic MCP, and Python attempt-monitor cases. |
| NiceGUI fixture: `python3 -m unittest discover -s tests -t . -v` from `examples/nicegui-app` | PASS — 3 pure-logic tests. NiceGUI itself and a browser were not started. |
| API/SQLite fixture: `python3 -m unittest discover -s . -v` from `examples/scenarios/api_db` | PASS — 2 contract tests. |
| Incident fixture: `python3 -m unittest discover -s . -v` from `examples/scenarios/incident` | PASS — 1 synthetic timeline test. |
| `python3 scripts/validate_manifests.py` | PASS — 19 pilot rule descriptors, 64 preserved public-source leads, 12 routes, 5 agents, 12 skills, 6 commands; capability registry also checks pinned sources, license evidence, decision fields, and route coverage. |
| `python3 scripts/security_scan.py` | PASS — 129 source files scanned; no high-confidence credential patterns; output does not include values. This pattern scan is not a complete secret audit. |
| `python3 scripts/network_attempt_monitor.py` | PASS — one simulated reserved-documentation-IP attempt was observed and blocked before OS socket connect by the Python audit hook. This does not test OS firewall, Node, browser, or OpenCode egress. |
| `node --check control/app.js` | PASS — JavaScript syntax. |
| `python3 scripts/golden.py check --fast --project examples/python-app` | PASS for executed fast checks; result is not release-qualified and retains `NOT_RUN` applicability gaps. |
| Golden full check on `examples/python-app` | Expected exit 2 — non-qualified. Nine blockers remain: `AI-001`, `API-001`, `DATA-001`, `DB-001`, `JOBS-001`, `MCP-001`, `OPS-001`, `PY-003`, `SEC-001`. Missing evidence is preserved as `NOT_RUN`; no exception was fabricated. |
| React `npm run typecheck`, `npm run test`, `npm run build` | NOT_RUN — scripts reached `tsc`, `vitest`, and `vite`, which are not installed. No npm install or network access was attempted; lockfile and offline npm store are absent. |
| Company doctor | `UNKNOWN` — no Node/OpenCode versions were provided from an approved software inventory; no settings changed and no network calls were made. |

The synthetic stdio MCP fixture's unit tests cover discovery/call shapes, scope, errors, inert injection-like data, and direct-handler timeout/cancellation cases. The fixture is disabled in OpenCode config. There is no SDK-backed protocol-conformance run or authentic OpenCode MCP trace. The local Golden Control route test calls the handler in memory; it does not launch a network server or qualify the UI in a browser.

## Recorded Golden evidence

- [`verification/2026-11-20/golden-fast-20261120.json`](verification/2026-11-20/golden-fast-20261120.json) — real `FAST` mode result; not a release claim.
- [`verification/2026-11-20/golden-full-20261120.json`](verification/2026-11-20/golden-full-20261120.json) — real `FULL` result with nine mandatory evidence blockers.
- [`verification/2026-11-20/golden-full-20261120.html`](verification/2026-11-20/golden-full-20261120.html) — rendered report from that full result.

These are local synthetic-project results. The JSON report checks consistency and hashes, but it is not digitally signed and does not authenticate its producer or prove that an OpenCode agent, skill, MCP, or CLI was invoked.

## Not tested / remaining limits

- Windows and a separate managed Linux host, including apply/rollback abuse cases.
- React dependency installation, TypeScript, component tests, build, or browser accessibility checks.
- NiceGUI runtime/UI behavior in a browser.
- Company OpenCode discovery, agent/skill use, internal model, connected MCPs, or invocation-event provenance.
- OS-enforced no-public-egress policy and attempt monitoring across OpenCode and all child processes.
- Complete third-party source/prompt-injection review, dependency license closure, SBOM, OSS clearance, and staged Windows/Linux executable assets.
- Paired agentic-vs-CLI or plain-OpenCode-vs-Golden measurements. No uplift, latency, token, request, or productivity claims are made.
- Hosted GitHub CI or any company CI/artifact/SSO integration.

See [`docs/QUALIFICATION_MATRIX.md`](docs/QUALIFICATION_MATRIX.md), [`offline/assets-manifest.json`](offline/assets-manifest.json), and [`OPEN_ITEMS_FOR_COMPANY.md`](OPEN_ITEMS_FOR_COMPANY.md) for the exact qualification gaps and owners.
