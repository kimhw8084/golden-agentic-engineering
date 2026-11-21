---
name: golden-docs
description: Produce BKM SOP manuals PDF HTML diagrams and evidence-backed documentation updates
---

# Evidence-driven documentation

Sources of truth: approved specifications, actual code, executed tests (in that order of contract, implementation and proof). Each doc has owner, version, affected area, evidence references and reviewer.

Generate reviewable drafts automatically when code/standards changes affect content, but do not auto-publish. Output Markdown source, offline searchable HTML and professional PDF through approved offline toolchain. Presentation deliverables use standalone HTML/PDF; do not assume PPTX requirement.

## Diagram design

Use a visual only when it explains the relationships more clearly than prose or a table. Choose the semantic pattern first (ownership, sequence, lifecycle, trust boundary, data flow), then the layout that fits it. Cover architecture C4, data lineage, sequences, swimlanes, timelines, ERD, dependencies, SPC and scientific charts when a visual improves the task. Remove redundant nodes, edges and labels; keep an overview to about nine nodes and twelve connections, splitting larger systems into overview and detail diagrams.

Keep source editable in Git. Use Mermaid for simple text-diffable flows and native SVG for diagrams whose layout needs precise control. Include an accessible title and description, label connections, and use shape, line style and text as well as color to convey meaning. Follow Golden's strict monochrome system and approved design tokens.

Keep generation offline: system fonts only, no remote font imports, CDNs, external images or web onboarding. Use existing local renderer/browser assets only when already staged; do not install or download a renderer as part of the diagram task. Reuse repository design defaults without a style questionnaire or approval pause; ask only when a missing decision materially changes the result.

This compact method adapts selected diagram-design principles from [`cathrynlavery/diagram-design`](../../../research/diagram-design-audit.md). The upstream skill, scripts, icon collection and browser export stack are not vendored or invoked by Golden.

Prefer D2/Mermaid/Typst after offline binary/license qualification. Never claim diagram rendering or report PDF creation when tool not actually executed.
