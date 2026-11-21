# stackback 0.0.2 source and license audit

**State: MIT declaration verified; standalone MIT notice text remains unresolved.** This evidence is not company OSS approval.

## Locked package

- Dependency path: `vitest@4.0.8` → `why-is-node-running@2.3.0` → `stackback@0.0.2` (dev-only).
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

The checked-in fixture uses Vitest 4.0.8, whose lock requests `why-is-node-running@^2.3.0`, leading to stackback. Upstream Vitest 5.1.1 at commit [`8b0ca603a8342aff1851a37ce0c0ae8cf4fa6b56`](https://github.com/vitest-dev/vitest/commit/8b0ca603a8342aff1851a37ce0c0ae8cf4fa6b56) pins `why-is-node-running@3.2.1`; its package manifest declares MIT and has no runtime dependencies. The pinned [`why-is-node-running v3.2.1` manifest](https://github.com/mafintosh/why-is-node-running/blob/v3.2.1/package.json) requires Node `>=20.11`. This dependency path removes stackback. However Vitest 5.1.1 requires Node `^22.12.0 || ^24.0.0 || >=26.0.0`. The company Node target is unknown, and no lockfile update, offline install, or fixture test for this candidate was run. Do not upgrade solely to clear the notice gap.

## Remaining action

The company OSS reviewer must decide whether the exact MIT package declaration is acceptable without a bundled standalone MIT notice, confirm the embedded V8 BSD notice is preserved, or require a tested dependency removal/replacement. Company clearance, Windows/Linux npm caches, and a complete target-specific license/SBOM review remain outstanding.
