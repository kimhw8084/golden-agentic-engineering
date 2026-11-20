# Open items for company qualification

These are company-only prerequisites. Repository implementation status and current evidence are in [`docs/QUALIFICATION_MATRIX.md`](docs/QUALIFICATION_MATRIX.md).

| Priority | Owner | Required action | Evidence to return |
|---|---|---|---|
| P0 | Security / network owner | Enforce default-deny public egress for OpenCode and every child process; allow only explicitly approved intranet/model/package endpoints. Provide endpoint-attempt monitoring on a Windows and Linux pilot host. | Policy/version, approved host allowlist, zero public attempts during approved smoke/evaluation tasks, and proof that an injected test attempt is observed and blocked. |
| P0 | OSS / package owner | Review selected candidate commits, dependencies, assets, licenses, NOTICE, SBOM, vulnerabilities and commercial-use terms; stage matching Windows/Linux wheels, npm lock/store and browser artifacts. | Signed/approved asset manifests, per-platform hashes, license evidence and source provenance. |
| P0 | OpenCode owner | Provide installed version from local software inventory; inspect config without exposing secrets; validate the V2 adapter, lazy skill discovery, permission behavior, MCP compatibility and internal model endpoint only after egress controls are verified. | Exact version/build, config shape summary, authentic discovery/call traces with provenance, and no public endpoint attempts. |
| P0 | Pilot engineering lead | Run representative synthetic tasks with identical acceptance criteria through plain OpenCode and Golden; record accepted result, elapsed time, human rework, latency/resources where available, and token/request counts only from trusted runtime events. | Reproducible trial record. If internal runtime is unavailable, retain `BLOCKED_COMPANY_RUNTIME`; do not use Codex or model self-judgment as company evidence. |
| P1 | Existing CI/artifact owner | Publish signed immutable Golden bundles, retain per-rule test artifacts, and expose the approved release feed using existing company services. Do not create a parallel artifact/observability platform. | Existing pipeline and artifact identifiers, approval/exception authority, rollback path. |
| P1 | Golden Control owner | Connect read-only approved installation and release status only if existing platform APIs support it. Keep runtime usage unknown unless a trusted event source exists. | Reviewed API contract and scope; no new event collector, usage store, or application registry. |
| P1 | Windows/Linux test owners | Execute the Python suite and bootstrap tests on each target OS; qualify installed OpenCode permissions and path/symlink behavior. | OS build, Python/Node versions, test output, and checked artifact hashes. |
| P2 | Team lead | Run one new and one existing application pilot, review the results and training path, and approve or reject a Golden release. | Human release decision; no automated or model-generated approval. |

No item above blocks ordinary local source edits or authorized repository commits. Company production changes and formal release approval remain with existing human owners.
