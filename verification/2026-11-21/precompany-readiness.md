# Pre-company readiness assessment

**Status: `PRE_QUALIFICATION`.** This assessment runs offline local checks only and cannot approve company software or qualify a company host.

## Source revision

- Repository: https://github.com/kimhw8084/golden-agentic-engineering
- Branch: `main`
- Commit: `3d122d495e3c27e846fb32b944973d82649e81c6`
- Worktree clean: `True`
- `SHA256SUMS.txt` SHA-256: `1ecbce1e9cde703e03eb862fee4dd94982ba96115929b6257fe89e6261a0130f`

## Local checks

| Check | Result | Evidence |
|---|---|---|
| `source-worktree` | **PASS** | output SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `unit-tests` | **PASS** | tests=161, output SHA-256 `812f4b40ed82896baa2266eb07c476bfb7c83601e88c87fc33787fbb464cfd8d` |
| `bootstrap-rollback-tests` | **PASS** | tests=36, output SHA-256 `da65312a3442c876a7fdcb4746dcf73bc49a0f542ea8bc6ce47ed2c1dc8b54ab` |
| `manifest-validation` | **PASS** | output SHA-256 `c68d27bf777aaa4d47b2bfe6b2357e06288ef7e8dadf8968292c841cb1a0906c` |
| `source-checksums` | **PASS** | output SHA-256 `0d846752b35d82e49a0171ffa4c10a7b228f8fc2d9572732483aab2236759d8a` |
| `secret-scan` | **PASS** | output SHA-256 `c0747ed39d7833e6995ea2aa062323183986b3165c98ca6993c0fc234f3764b5` |
| `network-attempt-intercept` | **PASS** | output SHA-256 `f9002c41b079976f37c54cb7bba915c79ecb5043f3cf15c6964c36deaf1a308e` |
| `offline-fixtures` | **PASS** | fixture_cases=8, React=PASS, NiceGUI UI=PASS, output SHA-256 `dd6ac33d6ab7c317bc412ec15ec25a292856cbf40ffca4caef64da3d9edb3b63` |
| `golden-full-checks` | **PASS** | No output details |

## Golden full checks

| Project | State | Blocking rule IDs |
|---|---|---|
| `examples/python-app` | **NOT_QUALIFIED** | AI-001, API-001, DATA-001, DB-001, JOBS-001, MCP-001, OPS-001, PY-003, REL-001, SEC-001 |
| `examples/react-app` | **NOT_QUALIFIED** | AI-001, API-001, DATA-001, DB-001, JOBS-001, MCP-001, OPS-001, REL-001, SEC-001, UI-002 |
| `examples/nicegui-app` | **NOT_QUALIFIED** | AI-001, API-001, DATA-001, DB-001, JOBS-001, MCP-001, OPS-001, PY-003, REL-001, SEC-001, UI-002 |

## Offline assets and licenses

- Offline asset groups staged: 0/6.
- Offline state: `SOURCE_ONLY_NOT_OFFLINE_EXECUTABLE`.
- Source asset-manifest SHA-256: `945a830c896ed851ada9e9486a5e64824c52c57e7ad3d9427dcfc55a034de15e`.
- Company OSS clearance: `NOT_OBTAINED`.
- Missing **Python wheelhouse and dependency locks** (Company OSS/package owner): Select target Python ABI/OS/architecture; stage the approved complete wheel closure with hashes, SBOM, and license inventory.
- Missing **React npm lock and offline store** (Company OSS/package owner): Confirm company Node range, OS and architecture; choose active Vitest 4.1.12 or candidate Vitest 5.1.1 only after native compatibility and company OSS review. Review the active stackback notice gap or candidate three notice supplements. Complete company-native Windows/Linux fixture qualification, stage per-target npm caches and browser artifacts through the approved process, verify hashes, and complete company OSS clearance. Neither lock nor public npm audit establishes company approval.
- Missing **Playwright browser binaries** (Company browser/tooling owner): Stage matching, hash-verified, licensed browser binaries per supported Windows/Linux target.
- Missing **MCP Python SDK and transitive dependencies** (Company OSS/package owner): Confirm exact Windows/Linux OS, architecture, Python patch/ABI and glibc; independently review candidate licenses and vulnerabilities; import matching hash-locked archives through the approved process; run native offline install and pip check. Repeat MCP discovery/calls with the company OpenCode build. Company approval is not obtained.
- Missing **Company OpenCode and internal model evidence** (Company OpenCode owner): Supply the installed internal build/config summary; set OPENCODE_DISABLE_AUTOUPDATE=1 and OPENCODE_DISABLE_MODELS_FETCH=1 on the actual CLI/server process; disable or network-block the separate desktop updater if used; verify the project web tool denies; repeat synthetic skill/MCP calls on the company build; and run an approved internal model trial only after the Windows/Linux egress gate and attempt monitor are active.
- Missing **OS-enforced no-public-egress policy and attempt monitor** (Company security/network owner): Enforce host/network default-deny egress for OpenCode and children, allow approved intranet destinations only, and return monitored blocked-attempt evidence.

## Company-owned actions

- **P0 — Security/network:** Enforce default-deny public egress for OpenCode and every child process on managed Windows and Linux pilot hosts; allow only approved intranet/model/package endpoints. OpenCode v2.2.7 attempts the public `models.opencode.ai` catalog by default. Set `OPENCODE_DISABLE_AUTOUPDATE=1` and `OPENCODE_DISABLE_MODELS_FETCH=1` on the actual managed CLI/server process before a session; separately disable or block the desktop updater if used; monitor denied-attempt evidence. Evidence: Policy/version, approved host allowlist, a blocked injected connection attempt, the server's effective environment, and monitored zero-public-attempt evidence during the smoke run.
- **P0 — OpenCode owner:** Provide the exact internal OpenCode build and sanitized config format; keep `webfetch`/`websearch` denied; verify the Golden agent/skill/command adapter and repeat the tested synthetic MCP discovery/call on that build without exposing provider values. Evidence: Version/build, config-key summary, company skill and MCP discovery/call traces, effective server environment, permission behavior, and approved internal model identifier.
- **P0 — Pilot engineering lead:** Run matched plain-OpenCode versus Golden synthetic tasks after the egress gate; record independent acceptance, elapsed time, rework, latency and trusted runtime token/request events where available. Evidence: Reproducible task records. Otherwise retain `BLOCKED_COMPANY_RUNTIME`; no uplift claim.
- **P1 — CI/artifact owner:** Map Golden qualification and signed immutable bundle delivery onto existing company CI and artifact systems. Evidence: Existing pipeline/artifact identifiers and rollback/exception owners.
- **P1 — Windows/Linux pilot owners:** Run doctor/apply/rollback and no-AI/offline tests on the approved company images. Evidence: Sanitized results, per-target versions and asset hashes.
- **P2 — Team lead:** Review the qualification evidence and explicitly approve or reject a Golden release. Evidence: Human release decision; no automatic/model approval.

## Cross-platform execution

- Native host tested: `Darwin`.
- Windows: `NOT_RUN_WINDOWS_HOST_REQUIRED`.
- Linux: `NOT_RUN_LINUX_HOST_REQUIRED`.
- Scope: This assessment reports only the native host OS; macOS results do not qualify Windows or Linux..

## Limitations

- No OpenCode process or model was started by this command; no authentic company agent, skill, MCP, or benchmark trace was collected.
- The network probe blocks one CPython loopback connection before the socket operation. It does not measure public egress or monitor other processes.
- Secret scanning covers high-confidence patterns only; it does not prove that proprietary information is absent.
- Local synthetic results are unsigned and are not company approval, cross-platform qualification, or production authorization.
