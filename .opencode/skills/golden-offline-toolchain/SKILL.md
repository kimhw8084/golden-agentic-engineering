---
name: golden-offline-toolchain
description: Stage OSS source binaries dependencies and licenses through approved offline transfer
---

# Offline tools and OSS

The catalog is **unqualified**. Before import: verify a real use case, OSI license plus every dependency/asset, source release integrity, vulnerability database freshness, Windows/Linux platform, OS-specific binaries and reproducible operation without public internet.

On internet-connected staging machine, use `python scripts/fetch_sources.py` to create a source-only inventory with pinned commits, SHA256 and observed license artifacts. This does **not** stage complete runnable toolchains. Separately stage qualified binaries, node/npm caches, Python wheels, browser assets, vulnerability databases and notices under company transfer rules.

No `curl | sh`, `npx -y`, remote CDN, unpinned runtime download or OAuth/service dependency by default. Fail closed on missing dependencies. Reuse already-approved packages first.
