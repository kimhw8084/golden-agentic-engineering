# Private requirements are deliberately NOT bundled into the GitHub starter

The detailed original organization-specific survey (107 decisions, 151 proposed requirements) and old architecture notes were removed from the publishable starter to avoid accidentally uploading internal context to an external GitHub repository.

When company policy authorizes their transfer, place approved local copies under `docs/local-only/` inside your internal Golden checkout. That directory is ignored by Git. Use them to complete internal requirements traceability, but **do not push private company context to a personal/public repository**.

The generalized design decisions needed to operate this starter are summarized in `docs/DECISION_LOG.md`. The starter is independently runnable without the full private documents.
