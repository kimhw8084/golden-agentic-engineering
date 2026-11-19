---
name: golden-release
description: Prepare repeatable offline qualification and team rollout with evidence not AI self-grading
---

# Qualification and release

1. Golden source changes require lead approval. Owner must approve affected-repository full CI evaluation after approved Golden standards change.
2. Preserve immutable release ID, hashes, dependency/license evidence, OS qualification reports, rollback plan and last approved offline local release.
3. Execute all applicable independent full checks; do not hide NOT_RUN/FAIL. Company risk exceptions require documented authority and evidence.
4. Qualify at least one new and one existing real application, Windows/Linux independently, AI-off operation, OpenCode compatibility and two-engineer pilot.
5. Measure delivery speed, escaped defects, rework, requests/tokens, task success, adoption, maintainability, operational effort individually, never one aggregate score.
6. Publication requires team lead approval after documented testing. Routine dev commits to main remain allowed; approval is for Golden standard releases and company deployment, not each code edit.
