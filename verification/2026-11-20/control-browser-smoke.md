# Golden Control browser smoke — 2026-11-20

**Scope:** Local read-only dashboard overview on the `e0466c6` checkout. The server was started on `127.0.0.1:8767` with the local `verification/2026-11-20` evidence directory. No installation target was supplied.

**Observed:** The overview rendered in the in-app browser and hydrated its local state. It showed version `0.1.0-dev`, qualification `PILOT UNQUALIFIED`, five agents, 12 skills, seven commands, seven local Golden reports, and 162 checksums matching. Installation remained `Not checked`, the approved update feed remained unconfigured, company agent/skill/MCP discovery remained unrun, and usage provenance remained `NOT INSTRUMENTED`.

**Limit:** This was a manual overview smoke, not automated browser coverage, a formal accessibility audit, an external-request capture, or company OpenCode evidence. The server bound to loopback and was stopped after inspection.

## Task-route follow-up

On the local revision containing the route-detail UI update, the task-routing view rendered 12 route cards, route skills/patterns and candidate notes. Every card displayed a collapsed `Full route details` control. The detail sections were not expanded during this smoke. This did not test company data, installation state, usage provenance or external-network behavior.

## Project-agent configuration follow-up

The local `#installation` page showed `GOLDEN PRIMARY CONFIGURED`, `golden-engineer`, and `.opencode/opencode.json`. The panel explicitly stated that this is checked-in project-config evidence only and that company OpenCode loading and compatibility are not tested. It did not inspect or display provider/auth settings. Company agent/skill/MCP discovery and usage provenance remained unknown.
