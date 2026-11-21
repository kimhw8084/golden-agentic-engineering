# Diagram-design source evaluation

**Decision:** adapt a small set of design methods into Golden's existing `golden-docs` skill; do not vendor or execute the upstream skill, scripts, templates, or icon assets. The existing diagram route already selects `golden-docs`, so this adds no agent call, separate skill load, installer, runtime dependency, or external network request.

## Source and integrity

- Repository: [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
- Reviewed commit: [`d74d8c2d0c78a9e1efd43137f6a9a51182a8b5f0`](https://github.com/cathrynlavery/diagram-design/tree/d74d8c2d0c78a9e1efd43137f6a9a51182a8b5f0)
- Advertised version at that commit: `2.6.168`; the skill metadata reports `2.6`.
- Downloaded archive SHA-256: `93f6634f9a1be43d6c70417e0d85c687b9e34d3f044660a9a3fce613c82524b9`.
- Root license: MIT, verified at the pinned commit. The exact license text is preserved in [`third_party/diagram-design/LICENSE`](../third_party/diagram-design/LICENSE). No upstream source file or asset is copied into this repository.
- The archive contained 833 entries (776 regular files; 33,375,228 uncompressed bytes). A static path/type check found no absolute or parent-traversal paths, links, or special files.

## Capability and risk review

The core skill advertises 51 visual types and requires loading a type reference, and sometimes a semantic-pattern reference, before drawing. It asks for a style choice on a project's first diagram and a pre-render user review unless standing instructions override it. Those steps may add context and interaction overhead; no task-time comparison was run.

The pinned privacy policy says the plugin has no server, account, analytics, or telemetry. Its default HTML/SVG templates and PNG export can request Google Fonts; URL onboarding can fetch web pages after confirmation. System-font and offline options are described, but were not executed here. PNG export requires Playwright and Chromium. The plugin manifest declares Read and Write capabilities.

The root [`THIRD_PARTY_LICENSES.md`](https://github.com/cathrynlavery/diagram-design/blob/d74d8c2d0c78a9e1efd43137f6a9a51182a8b5f0/THIRD_PARTY_LICENSES.md) documents Tabler (MIT), Simple Icons (CC0), log-z logos (MIT), Devicon (MIT), an Instrument Serif logo contribution (OFL), public-domain artwork, and product marks subject to trademark restrictions. This mixed asset inventory needs separate review and is not included in the Golden adaptation. Full transitive package and asset review was not performed.

A static scan covered 71 skill Markdown files and 8 Python helpers without executing them. The selected skill Markdown had no matches for the scan's limited prompt-injection phrase set; five phrase hits were in upstream import-verification test fixtures outside the skill tree. Several helpers read and write local files; the optional PNG exporter imports Playwright; import and export helpers were not functionally or adversarially tested. This is a bounded static check, not a full security audit.

## Golden adaptation

Golden keeps only these ideas, reworded for its own constraints: choose a semantic pattern before layout, remove unnecessary diagram elements, and bound an overview's density. Golden adds offline system fonts, editable Git sources, monochrome/accessible encoding, no web onboarding, and no confirmation ceremony for ordinary authorized work. Small fixes to one existing diagram remain direct; the normal technical-documentation route invokes `golden-docs`.

The upstream skill itself remains `EVALUATION_ONLY_NOT_APPROVED`. No upstream skill invocation, output-quality comparison, matched task-time trial, Windows/Linux run, Playwright export, or company OpenCode test is claimed. Company OSS/security review and a representative diagram-quality review remain prerequisites before company-wide use of any third-party asset or source component.
