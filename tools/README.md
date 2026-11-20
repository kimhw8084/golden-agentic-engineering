# Tools — comprehensive candidate list, deliberately not a mass-install plan

The machine-readable `candidates.json` contains **63 candidate public GitHub repos**, grouped into `pilot`, `extended` and `research` tiers. `license_hint_unverified` is only a search lead, not a legal statement or qualified source version. All new imports must pass company OSS/IP clearance, including dependencies/assets and commercial-use constraints.

**Select by task evidence, not by tool category.** Pilot tier is for evaluation, not simultaneous installation. Begin by discovering approved OpenCode agents, relevant skills, and connected MCP capabilities; exercise the best-fit agentic workflow. Compare CLI candidates against that workflow for the same task, and prefer a CLI for a specific operation only when it performs better on the stated acceptance criteria. A hybrid may be best: agent/skill for reasoning, MCP for structured service access, CLI for deterministic local operations and checks.

`tools/candidates.json` lists public source repositories for possible tools. It is not a complete inventory of agentic capabilities and it is not a ranked list. Do not use it as a substitute for inspecting the capabilities of the actual company OpenCode installation.

`python scripts/fetch_sources.py --tier pilot` previews URLs. The downloader with `--apply` is for approved public internet staging computers only; it clones sources and hashes them. Source snapshots alone are **not** an offline executable bundle.
