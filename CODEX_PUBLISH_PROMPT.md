# Copy this prompt into Codex after attaching the Golden ZIP

You are preparing an existing complete repository for GitHub, **not rewriting or inventing a replacement**. Extract the attached Golden_Agentic_Engineering_GitHub_Starter_v0.1.zip without losing dotfiles (especially `.opencode`).

1. Read `README.md`, `AGENTS.md`, `docs/ARCHITECTURE.md` and `START_HERE_COMPANY_OPENCODE.md`.
2. Verify `python -m unittest discover -s tests -v` succeeds. Run the offline `golden.py` demo and record the expected non-qualified FULL status. Validate JSON manifests.
3. Inspect for accidental private secrets, internal hostnames, credentials, user identifying information or proprietary code. The proposed workflows may contain organization-specific context: **do not make the repository public by default**. If an approved private repository is available, use it; otherwise prepare local Git commits and tell me what permission/connection is missing.
4. Initialize Git if needed, keep all files including `.opencode/`, and create a clean first commit. Do not add downloaded third-party source trees, company secrets, large binaries, or application data.
5. If GitHub tools/credentials are connected and I have authorized the target, create/use a **private** repository named `golden-agentic-engineering` (or the name I specify) and push the files. Otherwise give me an exact manual push sequence. Do not claim a push occurred unless remote confirms.
6. Do **not** replace the pinned tool catalog with `git submodule add` calls; source staging is intentional and opt-in. Do not trigger GitHub Actions or external downloads merely to publish.
7. Give a concise summary of tests, repository link if actually created, HEAD commit and remaining qualification gaps.

IMPORTANT: This is a **pilot starter**, not approved for company deployment; copyright/import, OSI-license and internal compatibility review are still required.
