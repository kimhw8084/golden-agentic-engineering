# Qualification and truth-in-status matrix — starter v0.1.0-dev

| Claim | Current state | Evidence / next requirement |
|---|---|---|
| Original Golden Python pilot checker exists | IMPLEMENTED | `scripts/golden.py` |
| 19 executable rule descriptors and applicability | IMPLEMENTED (pilot) | `standards/rules.json`; profiles derived from declarations only |
| Fast checker and full per-rule enumeration | IMPLEMENTED (pilot) | Python tests and sample run; full blocks without tooling |
| Evidence JSON + standalone HTML report | IMPLEMENTED (pilot) | Python tests |
| OpenCode agent/skill/command files written | FILES PRESENT | Actual internal OpenCode V2 compatibility **NOT TESTED** |
| 63 GitHub source candidates indexed | FILES PRESENT | Licensing, source snapshots and dependency review **NOT DONE** |
| Source clone/pin/hash script | IMPLEMENTED, dry-run tested | Real public Git downloads **NOT TESTED IN THIS ENV** |
| Qualified offline tool binaries/wheels/browsers | NOT PROVIDED | Stage separately after company approval |
| Complete 151 proposed requirements enforceable | NOT DONE | 19 rule descriptors are a starter, not 151 verified contracts |
| Independent profile/capability discovery | NOT DONE | Current manifest declarations may be inaccurate; verify before release |
| Company risk-exception workflow | NOT DONE | Integrate with existing company authority, preserve original result |
| Actual Windows + Linux end-to-end | NOT TESTED | Linux container Python pilot executed; Windows must be tested |
| Actual company OpenCode + internal model | NOT TESTED | Inspect internal version/config; prove relevant agent/skill/MCP use and compare CLI workflows on the same task |
| Agentic-first tool selection | NOT TESTED | Run representative task-level comparisons; record actual agent, skill, MCP and CLI invocations, results, latency and rework |
| Company CI integration | DESIGN ONLY | Existing CI owner builds trigger and evidence storage |
| Golden Control portal | INTENTIONALLY NOT BUILT | Optional, standards-only, after workflow qualification |
| Bundled MCP example server | INTENTIONALLY DISABLED | Example remains off pending server/SDK/permission/offline qualification; inspect and exercise approved MCP servers already connected to company OpenCode |
| Monitoring single-pane React UI | OUT OF SCOPE | Owned by separate team platform |
| Lead-approved Golden release | NOT APPROVED | Tests + documented evidence + team lead sign-off |
| Team adoption and independent proficiency | NOT TESTED | New + existing app pilot, two engineers, independent checks |

## Full pilot evaluator limitations

- Local Python checker trusts app's `capabilities` declarations for applicability. **Not enough to establish real non-applicability.**
- External test commands are set by a repository manifest and are **trusted local code** executed under current user's permissions; they are not sandboxed, signed or validated against an allowlist. Internal release qualification must address provenance/permissions.
- Timeouts, captured test excerpts, line-level links and exception authorities are initial placeholders. Avoid storing secrets in evidence.
- Version pin compares text to the installed Golden release but is not a signed artifact integrity check. Do not mistake this for production-grade tamper resistance.
- Demo isn't a real React/NiceGUI manufacturing app, and does not qualify existing application pipelines.
