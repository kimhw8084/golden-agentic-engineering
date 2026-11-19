---
name: golden-nicegui
description: Build efficient lightweight internal NiceGUI Python apps under Golden engineering standards
---

# NiceGUI engineering

1. Choose NiceGUI for relatively lightweight tools under the actual company deployment arrangements, not because FastAPI is supposedly unlimited.
2. Inspect installed NiceGUI version and local import/package availability. Avoid new persistent services and remote CDN assets.
3. Apply the same monochrome tokens, predictable density, keyboard focus, complete component states and safe change/exit behaviors as React, while honoring actual NiceGUI capabilities.
4. Separate UI, domain logic, DB operations and business side effects. Prefer SQLite initially unless a documented workload fails a concrete criterion; test concurrency, durability, backups and multiuser requirements.
5. Use pytest/unittest and browser-level interaction tests when browser assets exist; make failures reproducible without LLM.
6. Update developer/operator docs as review drafts; do not assume compliance from screenshot appearance alone.
