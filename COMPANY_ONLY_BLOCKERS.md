# Company-only qualification blockers

**Overall state: `PRE_QUALIFICATION`.** No blocker below can be closed by editing this public repository or by using Codex's model as a proxy for company OpenCode.

| Priority | Owner | Exact action needed | Evidence to return |
|---|---|---|---|
| P0 | Security/network | Enforce default-deny public egress for OpenCode and every child process on a managed Windows and Linux pilot host. Allow only approved intranet/model/package endpoints. | Policy/version, approved host allowlist, a blocked injected connection attempt, and monitored zero-public-attempt evidence during the smoke run. |
| P0 | OSS/package | Select company Windows/Linux OS, architecture, Python/Node/browser versions; decide whether `stackback@0.0.2`'s verified MIT declaration is acceptable without a bundled MIT notice while preserving its embedded V8 BSD notice, or require tested removal/replacement; stage exact wheel/npm/browser/MCP SDK dependency closures and license/NOTICE/SBOM/hash records. | Per-target asset manifests and attributable company OSS approval. |
| P0 | OpenCode owner | Provide the exact internal OpenCode build and sanitized config format; verify the Golden agent/skill/command adapter without exposing provider values. | Version/build, config-key summary, native discovery and call traces, permission behavior, and approved internal model identifier. |
| P0 | Pilot engineering lead | Run matched plain-OpenCode versus Golden synthetic tasks after the egress gate; record independent acceptance, elapsed time, rework, latency and trusted runtime token/request events where available. | Reproducible task records. Otherwise retain `BLOCKED_COMPANY_RUNTIME`; no uplift claim. |
| P1 | CI/artifact owner | Map Golden qualification and signed immutable bundle delivery onto existing company CI and artifact systems. | Existing pipeline/artifact identifiers and rollback/exception owners. |
| P1 | Windows/Linux pilot owners | Run doctor/apply/rollback and no-AI/offline tests on the approved company images. | Sanitized results, per-target versions and asset hashes. |
| P2 | Team lead | Review the qualification evidence and explicitly approve or reject a Golden release. | Human release decision; no automatic/model approval. |

See [`OPEN_ITEMS_FOR_COMPANY.md`](OPEN_ITEMS_FOR_COMPANY.md) for the longer evidence matrix and [`COMPANY_START_HERE.md`](COMPANY_START_HERE.md) for the exact Windows and Linux Step A/Step B commands. `READY_FOR_COMPANY_QUALIFICATION` is not supported yet.
