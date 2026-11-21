# UI/UX Pro Max source evaluation

**Decision:** keep the upstream collection evaluation-only and unvendored. Adapt only a short design-token layering rule into Golden's existing `golden-react` skill. That route already loads the in-repository skill, so the adaptation adds no skill load, installer, runtime dependency, or network request.

## Source and scope

- Repository: [`nextlevelbuilder/ui-ux-pro-max-skill`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
- Reviewed source commit: [`2de1134dc4d1cfe112934611ae5803ae17a1bd7e`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/tree/2de1134dc4d1cfe112934611ae5803ae17a1bd7e)
- Root `LICENSE` and CLI `package.json` declare MIT. The root license is available at the [pinned commit](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/2de1134dc4d1cfe112934611ae5803ae17a1bd7e/LICENSE).
- Observed metadata: CLI package `2.5.0`; `.claude/skills/design/SKILL.md` metadata `2.1.0`; `.claude/skills/ui-styling/SKILL.md` metadata `1.0.0`. These are source metadata, not an independently verified signed release.
- Inspected at the pinned commit: root README and license; `design`, `design-system`, and `ui-styling` skill instructions; CLI `package.json`, lockfile header, entry point, `init`, `update`, `versions`, Python launcher, and asset-sync script. The complete repository, data/assets, transitive dependency license closure, and every helper were not reviewed.

## What fits Golden

The design-system skill describes primitive values → semantic purpose names → component aliases. Golden adapts that hierarchy as short guidance in the existing React skill. Golden already specifies the internal React/TypeScript/Tailwind/shadcn stack, approved offline package checks, strict monochrome, interaction states, keyboard access, and deterministic acceptance. No CLI, data file, visual asset, or upstream skill text was imported.

## Risks and limits

The collection spans product UI but also brand/logo work, slides, banners, social media, and image generation. Its instructions name Gemini, Atlas Cloud, MuAPI, and UberLLM providers; other references show web documentation, remote shadcn/Tailwind installs, a Chart.js CDN, and Pexels/Unsplash background fetching. Those workflows do not meet Golden's company no-public-egress rule and are excluded.

The CLI can generate files from bundled templates, but `versions` and `update` query GitHub; update can install the CLI through npm; and legacy ZIP installation downloads GitHub releases unless that mode's offline option is used. The CLI README describes `--offline` as a compatibility flag for bundled template installs. None of these claims establishes network isolation; no install, update, network-attempt, or egress test was run. The CLI declares dependencies on `chalk`, `commander`, `ora`, and `prompts`; the lockfile exists, but the full transitive dependency/NOTICE review was not performed.

The CLI supports project/global installation, force overwrite, and uninstall operations. The asset-sync script removes and recreates generated target directories. These behaviors were inspected statically and not executed. Windows/Linux compatibility, full prompt-injection and filesystem review, exact context cost, and task-level design quality/time remain untested.

The registry continues to mark the source `EVALUATION_CANDIDATE_ONLY`; MIT does not imply company clearance. No upstream skill invocation, output-quality comparison, matched time/context trial, or company OpenCode test is claimed. See the machine-readable [`capability-selection.json`](capability-selection.json) entry for the detailed evidence fields.
