# Public OSS acquisition without an intranet internet dependency

`tools/candidates.json` contains 63 public GitHub **candidate source repos**. IDs are for inventory only. License hints are deliberately unverified and cannot substitute for company legal review or dependency scanning.

## On a personal/approved public staging computer only

```bash
python scripts/fetch_sources.py --tier pilot --limit 5                 # dry run
python scripts/fetch_sources.py --tier pilot --limit 5 --apply --out out/sources-batch01
python scripts/fetch_sources.py --verify --out out/sources-batch01  # hash-check offline
```

Each acquisition outputs source ZIP snapshots plus `sources.lock.json` with exact Git commit and archive hash. The fetcher does **not** execute repository contents. It will not overwrite an existing lock. This source-only process can require meaningful bandwidth and disk, particularly for large repositories.

## What it does NOT provide

- Precompiled Windows/Linux binaries, supported CPU architectures, executable signing, or runtime compatibility.
- `npm`/`pnpm` store, Python wheelhouse, C/C++ native dependencies, DLL/SO/.NET runtimes.
- Playwright Chromium/Firefox/WebKit binaries, Typst fonts, browser assets, documentation themes.
- Offline vulnerability DB freshness, complete SBOM, transitive license evidence, company IP/OSS approval.
- Legal confirmation that a particular tag/asset and its dependencies are OSI-approved.
- Company-approved import of the source snapshots.

## Offline qualification checklist for EACH selected tool

1. Define concrete user value and benchmark alternative; prefer already approved package.
2. Pin exact upstream commit/release + checksums; confirm provenance and security advisories.
3. Independently verify source and binary licenses, embedded components, asset restrictions and third-party notices.
4. Inventory full dependency tree; stage exact binaries/wheels/npm cache and user assets for target OS.
5. Install/extract on isolated Windows and Linux test machines with **public network blocked**; no implicit remote install.
6. Run actual Golden CLI/skill integration smoke tests with the company internal OpenCode.
7. Run no-AI deterministic tests; measure latency, CPU/RAM and process startup.
8. Record company approval, owner, update/rollback/removal plan, version and evidence. Publish approved artifact to internal repository.

No `npx -y`, `curl | bash`, package installation against public registries or remote MCP URLs at company runtime. VULN data needs planned offline refresh, not a one-time snapshot claimed indefinitely current.

## Practical packaging direction

Immutable internal release artifact: `golden-<version>-<os>-<arch>` with `manifest.json`, notices, hashes, approved executable directory, wheelhouse/npm store/browser assets as applicable, standards source, scripts and smoke-test evidence. Release manifest should be produced by internal approved CI and independently validated before wider rollout. This starter does NOT implement that production packaging workflow.
