# Offline bundle and no-egress staging

`python scripts/package_offline.py create --out /approved/transfer/golden.tar.gz` builds only from a clean Git worktree, packages only tracked regular files (including `.opencode/`), emits `golden.tar.gz.sha256`, and records per-file hashes. `python scripts/package_offline.py verify /approved/transfer/golden.tar.gz` checks the checksum, archive paths, file inventory, hashes, and high-confidence secret patterns.

This ZIP/TAR is **source-only, not an offline executable distribution**. It includes the React fixture's exact npm lock, a macOS arm64 dependency/license inventory, and a CycloneDX SBOM, but no transferable npm cache. The required-asset manifest still lists Windows/Linux npm assets, per-platform Python wheels, Playwright browser binaries, MCP SDK assets, and actual company OpenCode/model compatibility evidence as unstaged. The package contains no company data or model.

## No-public-egress policy

`egress-policy.template.json` is a fail-closed policy shape with no default allowed hosts. It is not installed or enforced by Golden. The actual firewall must deny outbound traffic from OpenCode and child tools except a company-approved intranet allowlist; the company security owner must supply that list. Do not add a public model/package/browser-provider fallback. Windows Firewall/App Control and Linux nftables/host firewall need separate policy deployment and administrative review.

`python scripts/network_attempt_monitor.py` dispatches a synthetic Python `socket.connect` audit event with the reserved documentation IP `203.0.113.1`; the hook must observe and reject it. It creates no socket and performs no network operation. This tests the Python audit-hook path only; it does not show that a real socket operation or OS firewall is monitored, and it does not monitor Node, browsers, OpenCode, or other child processes. A company test workstation with approved endpoint monitoring is still required.

## Staging recipes

1. On an approved connected staging host, select exact source commits and release tags from `research/capability-selection.json`; obtain original archives through the company OSS intake.
2. For each target OS and Python version, build a locked wheelhouse using the company-approved mirror, then emit SHA-256, SPDX/CycloneDX SBOM and complete license/NOTICE inventory. Keep Windows and Linux outputs separate.
3. For the React fixture, stage the locked npm cache separately for each target OS/architecture from the approved registry. From the Golden repository root, install only from that cache and run its checks:

   ```sh
   npm --prefix examples/react-app ci --offline --ignore-scripts --no-audit --no-fund
   npm --prefix examples/react-app run typecheck
   npm --prefix examples/react-app run test
   npm --prefix examples/react-app run build
   python scripts/npm_dependency_audit.py --report out/react-dependencies.json --sbom out/react-dependencies.cdx.json
   ```

   Do not use `npx` or an online `npm install` on company runtime. The last command records the dependencies installed for the current platform; run it separately on each OS/architecture.
4. Review all license IDs and notices before approval. Current macOS arm64 inventory shows four packages without bundled license text; the source-license notices must be supplied or cleared by the company OSS owner. The checked-in audit is evidence, not approval.
5. Stage Playwright's matching browser binaries per OS and verify their checksum and license. The current repository has none.
6. Transfer the bundle through the company's artifact process, verify the external checksum on receipt, and run `company_bootstrap.py doctor` before the reviewed apply step.

Windows/Linux npm caches, Python wheels, browser binaries, approved notices, company endpoints, and OS egress evidence are **not available in this repository**. The checked-in React lock/SBOM does not make the bundle offline-executable. Golden must remain `PRE_QUALIFICATION` until all required assets are staged and checked.
