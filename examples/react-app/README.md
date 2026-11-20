# Synthetic React measurement review

A local-only React/TypeScript fixture with controlled form state, error and boundary behavior, keyboard-friendly labels, live status, and component/unit tests. Values and IDs are synthetic; no service or production write is present.

Direct dependency versions are exact in `package.json`; `package-lock.json` pins the transitive graph. The fixture uses Vite's built-in TSX transform and the `happy-dom` Vitest environment. Its current React test suite is runnable with a local npm cache and no lifecycle scripts:

```sh
npm ci --offline --ignore-scripts --no-audit --no-fund
npm run typecheck
npm run test
npm run build
```

These commands passed on macOS arm64 with Node 26.13.0 and npm 11.20.0. The test output includes six logic/component tests. A local in-app browser smoke also verified keyboard navigation/submission and the cleared-number validation alert on loopback. This is not an accessibility audit or Playwright automation. The lock has 132 package entries; 82 packages were installed and tested in this environment, while 50 optional OS/CPU variants were not staged. The per-machine inventory and CycloneDX file are [`research/react-macos-arm64-dependency-audit.json`](../../research/react-macos-arm64-dependency-audit.json) and [`research/react-macos-arm64.cdx.json`](../../research/react-macos-arm64.cdx.json).

The installed package metadata currently reports only MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause and ISC. Four installed packages lack a bundled license/notice text file; the inventory marks those gaps. This is not a complete source-license review or company clearance. Windows/Linux package stores, their separate inventories, browser binaries, and company import approval remain outstanding. Do not install or update dependencies from company runtime.
