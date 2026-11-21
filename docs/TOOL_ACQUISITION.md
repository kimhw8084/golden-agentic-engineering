# Public OSS acquisition without an intranet internet dependency

`tools/candidates.json` contains 64 public GitHub **candidate source repos**, currently including one explicitly typed agent-skill source. IDs are for inventory only; this evolving lead list does not cover all relevant skills, agents, MCP servers, or requirements. License hints are deliberately unverified and cannot substitute for company legal review or dependency scanning.

## Agent-skill source currently in the pilot tier

[`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design) is an agent skill, not a CLI. A pinned-source evaluation found the upstream MIT license and useful visual-design methods, along with default Google Fonts requests, optional URL onboarding, a Read/Write plugin manifest, optional Playwright/Chromium export, and a mixed third-party icon/license inventory. Its broad core skill also includes a first-diagram style gate and a pre-render user-review step that may add task overhead. See the bounded source and archive audit in [`research/diagram-design-audit.md`](../research/diagram-design-audit.md).

Golden now adapts only the semantic-pattern-first, remove-redundant-elements, and bounded-density methods in the existing `golden-docs` skill. The docs/diagram route loads that skill; the method uses local system fonts, monochrome/accessibility rules, version-controlled Mermaid/SVG, and no external assets. The full upstream skill, scripts, templates, and icons are not vendored or invoked. Its candidate registry entry remains evaluation-only and unapproved; no matched output-quality/time test or company runtime trial exists. This is the chosen task path today, not a measured performance winner.

For React design, Golden also reviewed the pinned [`nextlevelbuilder/ui-ux-pro-max-skill`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/tree/2de1134dc4d1cfe112934611ae5803ae17a1bd7e). Its root MIT license is verified, and one reworded token-layering method now lives in the existing `golden-react` skill. The wide upstream collection includes image-provider, CDN, remote install/update, and data/helper workflows; dependencies and the full security surface are not audited, so Golden does not install or vendor it. See [`research/ui-ux-pro-max-audit.md`](../research/ui-ux-pro-max-audit.md). This adaptation has no matched quality/time/context evidence and is not company approval.

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

1. Define the task and its acceptance criteria. First inventory approved OpenCode agents, skills, and connected MCP tools; exercise the best-fit agentic workflow before acquiring another tool. Benchmark relevant CLI candidates against the same task. Prefer a CLI for a specific capability only when measured evidence shows it wins on the requirements that matter; choose a hybrid when it performs best end to end.
2. Pin exact upstream commit/release + checksums; confirm provenance and security advisories.
3. Independently verify source and binary licenses, embedded components, asset restrictions and third-party notices.
4. Inventory full dependency tree; stage exact binaries/wheels/npm cache and user assets for target OS.
5. Install/extract on isolated Windows and Linux test machines with **public network blocked**; no implicit remote install.
6. Run actual task-level agent, skill, and authorized MCP integration smoke tests with company internal OpenCode; compare selected CLI candidates on the same representative task and preserve traces/results.
7. Run no-AI deterministic tests; measure latency, CPU/RAM and process startup.
8. Record company approval, owner, update/rollback/removal plan, version and evidence. Publish approved artifact to internal repository.

No `npx -y`, `curl | bash`, package installation against public registries or remote MCP URLs at company runtime. VULN data needs planned offline refresh, not a one-time snapshot claimed indefinitely current.

## Practical packaging direction

Immutable internal release artifact: `golden-<version>-<os>-<arch>` with `manifest.json`, notices, hashes, approved executable directory, wheelhouse/npm store/browser assets as applicable, standards source, scripts and smoke-test evidence. Release manifest should be produced by internal approved CI and independently validated before wider rollout. This starter does NOT implement that production packaging workflow.
