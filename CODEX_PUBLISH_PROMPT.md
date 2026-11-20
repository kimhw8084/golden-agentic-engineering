# Historical publish checklist for the public Golden repository

The repository `https://github.com/kimhw8084/golden-agentic-engineering` is already public. Preserve its visibility. Prepare the supplied Golden starter **without rewriting or inventing a replacement** and preserve dotfiles (especially `.opencode`).

1. Read `README.md`, `AGENTS.md`, `docs/ARCHITECTURE.md` and `COMPANY_START_HERE.md`.
2. Verify the offline Python suite and manifest/security checks. Run the `golden.py` demo and record the expected non-qualified FULL status.
3. Inspect for secrets, internal hostnames, credentials, identifying information, or proprietary code. Remove sensitive material before committing. Do not change repository visibility or add company data.
4. Initialize Git if needed, keep all files including `.opencode/`, and create a clean first commit. Do not add downloaded third-party source trees, company secrets, large binaries, or application data.
5. Push to the existing authorized repository only if GitHub access is available. Do not create a replacement repository or change visibility. Do not claim a push occurred unless remote confirms.
6. Do **not** replace the pinned tool catalog with `git submodule add` calls; source staging is intentional and opt-in. Do not trigger GitHub Actions or external downloads merely to publish.
7. Give a concise summary of tests, repository link if actually created, HEAD commit and remaining qualification gaps.

IMPORTANT: This is a **pilot starter**, not approved for company deployment; copyright/import, OSI-license and internal compatibility review are still required.
