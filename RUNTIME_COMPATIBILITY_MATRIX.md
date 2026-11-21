# Runtime compatibility matrix

**State: `PRE_QUALIFICATION`.** The local probes test public OpenCode releases and synthetic fixtures only. No company OpenCode build, internal model, or company MCP server was available.

| Surface | Observed result | Qualification state |
|---|---|---|
| Local OpenCode V1 CLI | Installed binary reported `1.3.9`; the Step A doctor intentionally does not execute OpenCode and reported the company version as unknown. | Local host only; not a company version. |
| Verified public OpenCode V2 candidate | Official v2.2.7 release binary checksum verified against its release SHA256SUMS. The repo's hidden agent/skill files loaded from a temporary project. | V2 candidate, not the company runtime. |
| Project V2 config on local V1 CLI | V1 rejected the repo's `mcp.servers` configuration shape. | `INCOMPATIBLE_LOCAL_V1`; this does not predict company behavior. |
| Native OpenCode skill | A scripted loopback model called the V2 `skill` tool with `id: golden-routing`; OpenCode returned the actual skill body. | `PASS_LOCAL_SCRIPTED_SKILL`; no model reasoning or quality claim. |
| Public web tools | With project permissions denying `webfetch` and `websearch`, those actions were absent from the V2 model tool list. | Project-level deny observed on OpenCode v2.2.7; not an OS network control. |
| Public model catalog | Without an environment setting, OpenCode v2.2.7 attempted `GET https://models.opencode.ai/experimental/v2.0/api.json` even with a configured loopback model; Seatbelt denied it. With `OPENCODE_DISABLE_MODELS_FETCH=1`, no catalog-fetch event appeared in the captured OpenCode logs. | Local observation only. The company server process must use the setting and the network owner must monitor attempts. |
| CLI/server update checks | The isolated probe environment set `OPENCODE_DISABLE_AUTOUPDATE=1`, but updater traffic was not separately instrumented. OpenCode's config docs place `update: "disable"` in global configuration and state that project-level values are ignored. | Require the environment setting for the CLI/server and network monitoring. Desktop updater behavior is separate and must be independently disabled or network-blocked. |
| Official MCP Python SDK | Pinned `mcp==2.3.0` SDK stdio client discovered the SDK-backed synthetic tool and read the fixed sample; macOS arm64 offline install and `pip check` passed. | `PASS_LOCAL_SDK_STDIO`; not OpenCode compatibility, Windows/Linux installation, or company approval. |
| OpenCode MCP against official SDK | OpenCode v2.2.7 did not expose the SDK fixture's tool. Pin mode `2026-07-28` rejected the server because it did not offer the required `server/discover` pin; legacy mode timed out. | `FAILED_LOCAL_MCP_HANDSHAKE`; needs protocol/version investigation. |
| OpenCode MCP control against existing fixture | The same temporary project/config timed out with the repo's original synthetic stdio fixture in legacy mode. | `FAILED_LOCAL_CONTROL_HANDSHAKE`; the MCP integration path remains unresolved, not an SDK-only conclusion. |
| Python/JSON-RPC synthetic MCP tests | Discovery, read-only call, scope rejection, injected text as data, notification, malformed input, timeout/cancellation and unavailable-service contracts pass. | `PASS_SYNTHETIC_CONTRACT`; not an authentic OpenCode call. |
| Browser and UI automation | React and NiceGUI local component/simulation checks pass. Playwright browser binaries are absent. | Browser journey and automated accessibility checks are `NOT_RUN`. |
| Windows and Linux | Candidate wheel tags are recorded, but native MCP install, browser, bootstrap/apply, egress, and company runtime tests were not run on those OSes. | Company OS qualification `NOT_RUN`. |

OpenCode's [V1-to-V2 guide](https://opencode.ai/docs/migrate-v1/) documents the config transition; V2 supports native `mcp.servers`, project agents and skills. The [permissions guide](https://opencode.ai/docs/permissions/) defines `webfetch`/`websearch` actions and ordered `deny` rules. The local catalog-disable setting `OPENCODE_DISABLE_MODELS_FETCH=1` is identified by an OpenCode maintainer in [issue #34730](https://github.com/anomalyco/opencode/issues/34730). OpenCode's [global update setting](https://opencode.ai/docs/config/) says project-level update values are ignored; the `OPENCODE_DISABLE_AUTOUPDATE` variable is described in [OpenCode's environment guidance](https://github.com/anomalyco/opencode/issues/55308). The [MCP configuration](https://opencode.ai/docs/mcp-servers/) documents legacy and modern protocol negotiation; its selected mode must be checked against the company's exact build.

## Test isolation

The V2 runtime probes used an isolated temporary project, OpenCode data/config directories, no credentials, a deterministic loopback-only OpenAI-compatible stub, and a macOS Seatbelt profile that permitted loopback service traffic and denied all other networking. The stub scripted the `skill` call and final answer; it did not judge behavior. In the run without `OPENCODE_DISABLE_MODELS_FETCH=1`, OpenCode logged the denied catalog lookup. With the variable set, that log event was absent. This log check is not packet capture or company endpoint-monitor evidence.

The MCP SDK itself passed a direct local stdio test under the same loopback-only policy. OpenCode's SDK and control-fixture connections failed as recorded above. No company config, MCP endpoint, internal model, company source, or company data was used.

## Exact next evidence

The company OpenCode owner must return the installed version/build and sanitized config-format summary. Before any pilot session, set `OPENCODE_DISABLE_AUTOUPDATE=1` and `OPENCODE_DISABLE_MODELS_FETCH=1` on the actual CLI/server process, keep project web tools denied, and have the security/network owner enforce and monitor intranet-only egress for OpenCode and every child process. If the company uses OpenCode desktop, disable or network-block its separate updater. Then resolve the company's MCP protocol compatibility and return an attributable discovery/call trace. Pilot performance evidence still requires matched company OpenCode tasks; no uplift claim is supported by this scripted local model.
