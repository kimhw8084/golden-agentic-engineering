---
description: Route and execute an engineering objective through the smallest relevant Golden agentic workflow
---
Route this objective using the task table in the `golden-routing` skill. If this checkout includes `workflows/task-routing.json` and `scripts/golden_route.py`, use the local resolver to validate and print the selected route. An installed global command may not have that repository checkout, so use the skill's compact route table directly in that case; routing must still work without launching another process.

$ARGUMENTS

Select one workflow ID and follow only that route. Use the primary OpenCode agent and load its relevant installed skill. Add a listed specialist only when its stated condition materially applies and work is independent. Capability and MCP candidates are research leads, not approval or installation: use an already-connected company MCP only when the current runtime confirms it is approved. Use deterministic tools for reproducible checks and the route's no-AI fallback when the model or agentic services are unavailable.

Start implementation after routing. Do not stop at a plan, load every skill, add ceremony to a small task, or ask for routine approval. Preserve unrelated working code. Report the executed checks, actual acceptance result, and remaining blockers.
