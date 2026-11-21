---
name: golden-offline-toolchain
description: Stage OSS source binaries dependencies and licenses through approved offline transfer
---

# Offline tools and OSS

The catalog is **unqualified**. Before import: verify a real use case, OSI license plus every dependency/asset, source release integrity, vulnerability database freshness, Windows/Linux platform, OS-specific binaries and reproducible operation without public internet.

On internet-connected staging machine, use `python scripts/fetch_sources.py` to create a source-only inventory with pinned commits, SHA256 and observed license artifacts. This does **not** stage complete runnable toolchains. Separately stage qualified binaries, node/npm caches, Python wheels, browser assets, vulnerability databases and notices under company transfer rules.

Use `python scripts/mcp_candidate_bundle.py` to validate and hash-lock an already-downloaded MCP SDK wheelhouse, produce embedded-license inventory and CycloneDX SBOM, and verify the deterministic archive. The current v2.3.0 candidates in `offline/mcp-sdk-candidate/` are not company-cleared; Windows/Linux native installs and the OpenCode MCP handshake are still unqualified.

OpenCode V2.2.7 attempted the public model catalog in a local probe unless `OPENCODE_DISABLE_MODELS_FETCH=1` was set. Require `OPENCODE_DISABLE_AUTOUPDATE=1` and `OPENCODE_DISABLE_MODELS_FETCH=1` on the actual OpenCode CLI/server process, keep project `webfetch`/`websearch` permissions denied, and still require the company's OS-enforced intranet-only allowlist and attempt monitor. These settings do not govern the separate desktop updater and are not a network boundary.

No `curl | sh`, `npx -y`, remote CDN, unpinned runtime download or OAuth/service dependency by default. Fail closed on missing dependencies. Reuse already-approved packages first.
