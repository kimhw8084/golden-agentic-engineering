# stackback 0.0.2 source and license audit

**State: MIT declaration verified; standalone MIT notice text remains unresolved.** This evidence is not company OSS approval.

## Locked package

- Current active dependency path: `vitest@4.1.12` → `why-is-node-running@2.3.0` → `stackback@0.0.2` (dev-only). The package chain was first audited while Vitest 4.0.8 was active; the current lock still pins the same `why-is-node-running` and `stackback` versions and integrities.
- `package-lock.json` integrity: `sha512-1XMJE5fQo1jGH6Y/7ebnwPOBEkIEnT4QF32d5R1+VXdXveM0IBMJt8zfaxX1P3QhVwrYe+576+jkANtSS2mBbw==`.
- The lock, installed `package.json`, archived upstream `package.json`, and npm's package record declare MIT.

## Upstream source match

The source repository named by the package metadata is `shtylman/node-stackback`; GitHub now serves the archived repository as [`defunctzombie/node-stackback`](https://github.com/defunctzombie/node-stackback). Its `master` head was pinned for this audit to commit [`24d55717e16f1bb2109e848ea2b3a90ea900ddb5`](https://github.com/defunctzombie/node-stackback/commit/24d55717e16f1bb2109e848ea2b3a90ea900ddb5). The source package identifies itself as version `0.0.2`.

The Git blob SHA-1 values for five files in the installed package match the pinned upstream files:

| File | Git blob SHA-1 | Evidence |
|---|---|---|
| `package.json` | `3e8b7b2c023d3535e0869b0959616cda4d654fc8` | Declares version 0.0.2, author Roman Shtylman, and MIT. |
| `index.js` | `8b87042343d7e6fc238075138f72f4ff3fa58d5e` | Matches pinned upstream source. |
| `formatstack.js` | `d64307d210dd134dff936607480695b86f3b6776` | Matches pinned source and contains the V8 BSD notice described below. |
| `README.md` | `fb6bde7486827b31d96cd2bfc1f96fd945bbf011` | Matches pinned upstream documentation. |
| `test.js` | `212b414ab496cf76d2a6977bd935ce714508482f` | Matches pinned upstream test file. |

The upstream root has no `LICENSE` file at that revision. No standalone MIT license text or copyright notice was present in the inspected package files, so none was reconstructed or invented. npm's record for [stackback 0.0.2](https://www.npmjs.com/package/stackback/v/0.0.2) independently shows the MIT identifier; that metadata does not supply a missing notice text.

`formatstack.js` includes the complete BSD-3-Clause notice for V8 project authors (copyright 2012). That notice is part of the source file and must remain intact. This embedded BSD notice is separate from the package-level MIT declaration.

## Replacement candidate reviewed, not selected

The active fixture now uses Vitest 4.1.12, whose lock still requests `why-is-node-running@^2.3.0`, leading to stackback. This Vitest update and Vite 7.3.8 also close the critical/moderate Vitest and high Vite findings reported for the old lock; both the active lock and separate candidate report zero vulnerabilities in public npm audit data as of 2026-11-21. A tested Vitest 5.1.1/Vite 7.3.8 candidate lock is preserved under `research/react-vitest-5.1.1-candidate/`; it pins `why-is-node-running@3.2.1` and removes stackback. The candidate passed offline-cache install, typecheck, six tests, build and npm audit locally. It requires Node `^22.12.0 || ^24.0.0 || >=26.0.0`; the company Node target is unknown, so it is not selected. A hosted Windows/Ubuntu matrix passed for active Node 20.19.0 and candidate Node 22.12.0 (run [#1](https://github.com/kimhw8084/golden-agentic-engineering/actions/runs/44930658112)); company runtime and OSS clearance remain unverified.

## Remaining action

The company OSS reviewer must decide whether the exact MIT package declaration is acceptable without a bundled standalone MIT notice, confirm the embedded V8 BSD notice is preserved, or require a tested dependency removal/replacement. Company clearance, Windows/Linux npm caches, and a complete target-specific license/SBOM review remain outstanding.
