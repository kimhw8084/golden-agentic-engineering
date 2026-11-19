# Tools — comprehensive candidate list, deliberately not a mass-install plan

The machine-readable `candidates.json` contains **63 candidate public GitHub repos**, grouped into `pilot`, `extended` and `research` tiers. `license_hint_unverified` is only a search lead, not a legal statement or qualified source version. All new imports must pass company OSS/IP clearance, including dependencies/assets and commercial-use constraints.

**Use one proven tool for a need, not several overlapping replacements.** Pilot tier is for evaluation, not simultaneous installation. Begin with approved installed tools; prefer CLI; add skills where instructions are needed; MCP only when an authorized service genuinely benefits from typed access.

`python scripts/fetch_sources.py --tier pilot` previews URLs. The downloader with `--apply` is for approved public internet staging computers only; it clones sources and hashes them. Source snapshots alone are **not** an offline executable bundle.
