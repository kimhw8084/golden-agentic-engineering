# Offline bundle and no-egress staging

`python scripts/package_offline.py create --out /approved/transfer/golden.tar.gz` builds only from a clean Git worktree, packages only tracked regular files (including `.opencode/`), emits `golden.tar.gz.sha256`, and records per-file hashes. `python scripts/package_offline.py verify /approved/transfer/golden.tar.gz` checks the checksum, archive paths, file inventory, hashes, and high-confidence secret patterns.

This ZIP/TAR is **source-only, not an offline executable distribution**. `golden-offline-manifest.json` lists the absent platform-specific Python wheels, npm store/lock/license set, Playwright browser binaries, and actual company OpenCode/model compatibility evidence. The package contains no downloaded third-party candidate implementation or model.

## No-public-egress policy

`egress-policy.template.json` is a fail-closed policy shape with no default allowed hosts. It is not installed or enforced by Golden. The actual firewall must deny outbound traffic from OpenCode and child tools except a company-approved intranet allowlist; the company security owner must supply that list. Do not add a public model/package/browser-provider fallback. Windows Firewall/App Control and Linux nftables/host firewall need separate policy deployment and administrative review.

`python scripts/network_attempt_monitor.py` runs a local Python audit-hook probe against the reserved documentation IP `203.0.113.1` and blocks it before the OS socket connect. Its test asserts that the **attempt is observed and blocked**. This proves the Python instrumentation path only; it does not test a real OS firewall or monitor Node, browsers, OpenCode, or other child processes. A company test workstation with approved endpoint monitoring is still required.

## Staging recipes

1. On an approved connected staging host, select exact source commits and release tags from `research/capability-selection.json`; obtain original archives through the company OSS intake.
2. For each target OS and Python version, build a locked wheelhouse using the company-approved mirror, then emit SHA-256, SPDX/CycloneDX SBOM and complete license/NOTICE inventory. Keep Windows and Linux outputs separate.
3. For the React fixture, generate and review a complete npm lockfile and offline npm store from the approved registry; include every transitive license and notices. Do not use `npx` or `npm install` on the company runtime.
4. Stage Playwright's matching browser binaries per OS and verify their checksum and license. The current repository has none.
5. Transfer the bundle through the company's artifact process, verify the external checksum on receipt, and run `company_bootstrap.py doctor` before the reviewed apply step.

Exact hashes, lockfiles, wheels, npm store, SBOM, notices, browser binaries and approved endpoints are **not available in this repository**. Golden must remain `PRE_QUALIFICATION` until staged and checked.
