# Dependency and license review

**State: evaluation evidence only. Company OSS clearance has not been granted.** Upstream source license metadata is not a substitute for license text, dependency review, artifact provenance, or company approval.

## React fixture

- `examples/react-app/package-lock.json` pins 132 packages for the audited macOS arm64 install. The current install, TypeScript check, six Vitest tests, and build pass with npm offline mode.
- The audit has metadata and notice evidence for 78 packages. Fifty OS/optional package variants are not staged for Windows/Linux. Four package license-text gaps were found; three have supplemental notices pinned to exact upstream commits. All four npm tarballs still omit the license file.
- The remaining unresolved dependency is `stackback@0.0.2`, a dev-only transitive dependency through `vitest@4.0.8` → `why-is-node-running@2.3.0` → `stackback@0.0.2`. Its package metadata declares MIT, but the source archive examined for the existing audit lacks authoritative license text. Do not infer approval from the metadata. The dependency may be removed only after a lockfile change passes the fixture checks and license review.
- Current evidence lives in `research/react-macos-arm64-dependency-audit.json`, `research/react-license-supplements.json`, `research/react-macos-arm64-licenses/`, and `research/react-macos-arm64.cdx.json`. It is not a complete Windows/Linux or company-approved SBOM.

## Python and MCP

- The synthetic examples use the Python standard library for core correctness tests. Optional NiceGUI and other installed packages are used only by their explicitly requested UI simulation tests.
- No official `modelcontextprotocol/python-sdk` release or transitive wheelhouse is pinned or staged. The repository's small synthetic stdio fixture does not count as the SDK and is not a substitute for SDK conformance evidence.
- The `fab_sampling_offline_port_kit/requirements_*.txt` files are broad candidate lists, not a resolver-produced, hash-pinned closure. They have no downloaded wheelhouse, complete SBOM, or per-target license inventory.

## Fab-source candidates

`fab_sampling_offline_port_kit/repos.json` names 38 candidate repositories. All remain candidate-only: no repositories, submodules, LFS objects, datasets, models, or wheels were downloaded. The kit correctly warns about data/model rights and flags redistribution/license review for SMT2020-related candidates and the NIST custom notice. The source list is not a transfer approval.

## Required owner actions

1. The OSS/package owner selects the exact company Python, Node, Windows/Linux OS, architecture, and browser versions.
2. Resolve the `stackback@0.0.2` license-text gap or remove the dependency through a tested lock update.
3. Stage exact target-specific Python wheels, npm cache and browser binaries; record source lock, hashes, full dependency closure, SBOM, and licenses/NOTICE.
4. Review each source, dependency, bundled asset, model and dataset under company policy and record an attributable approval.
5. Keep platform assets separate, transfer them through the approved internal artifact path, and rerun local verification offline on both target OSes.

Until those actions are complete, the repository remains source-only and all third-party candidate selections remain unapproved.
