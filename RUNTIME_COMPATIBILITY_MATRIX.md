# Runtime compatibility matrix

**State: PRE_QUALIFICATION.** Public OpenCode V2 is the project configuration target. No company OpenCode build, model endpoint, or MCP server was available for this audit.

| Surface | Observed result | Qualification state |
|---|---|---|
| Local OpenCode CLI | Local binary reported V1 `1.3.9`. The Step A doctor intentionally does not execute OpenCode and reported its version as unknown from local package metadata. | Local host only; not a company version. |
| Project V2 configuration on local V1 CLI | The V1 CLI rejected the repo's `mcp.servers` shape as invalid. The V2 config was not changed. | `INCOMPATIBLE_LOCAL_V1`; this does not predict company behavior. |
| V1-compatible isolated synthetic provider | In a temporary repo/config, the CLI reached an OpenAI-compatible stub over loopback and advertised the built-in tools, including `skill`. The model response was scripted. | Transport and tool discovery partial pass; no model quality evidence. |
| Native skill execution | A scripted `golden-routing` skill call reached the V1 skill tool but failed when the hosted sandbox denied `posix_spawn` for its `rg` helper. No skill body was returned to the model. | `BLOCKED_SANDBOX_PROCESS_LAUNCH`; do not mark skill call successful. |
| Network behavior | OpenCode logged a `models.dev` fetch attempt. The isolated probe allowed only localhost networking and denied the public lookup. The first version command was not sandboxed and logged a failed fetch; subsequent OpenCode probes used default-deny Seatbelt. | Local observation only. Company Windows/Linux egress controls and endpoint attempt logs are still required. |
| Golden MCP fixture | JSON-RPC discovery, call, errors, injection-as-data, notifications, malformed parameters, and scope tests pass. The fixture is a local protocol test, not the official Python MCP SDK. | `SYNTHETIC_CONTRACT_TESTED`; authentic OpenCode MCP execution is `NOT_RUN`. |
| Browser and UI automation | React and NiceGUI local component/simulation checks pass. Playwright browser binaries are absent. | Browser journey and automated accessibility checks are `NOT_RUN`. |
| Windows and Linux | Hosted source CI has previously exercised source-level Windows/Linux Python jobs, but this task has not run the company doctor/apply flow or browser/package bundles on those targets. | Company OS qualification `NOT_RUN`. |

OpenCode documents V1-to-V2 migration as a breaking config transition: V1 uses a different MCP/config shape, while V2 supports `mcp.servers`; V2 also retains project `agents/`, `commands/`, and `skills/` discovery. The company's actual version and config format must be collected by its OpenCode owner before use. See the [official migration guide](https://opencode.ai/docs/migrate-v1/), [MCP configuration](https://opencode.ai/docs/mcp-servers/), [skills](https://opencode.ai/docs/skills/), and [CLI commands](https://opencode.ai/docs/cli/commands/).

## Test isolation

The synthetic provider ran from a clean Git archive under `/private/tmp`, with isolated XDG/OpenCode config and data directories, no credentials, update checks disabled, and a macOS Seatbelt profile that denied networking except loopback. OpenCode still logged its failed public catalog lookup. The sandbox could not start the bundled `rg` process required for skill loading. No company configuration, MCP endpoint, internal model, company source, or company data was used.

## Exact next evidence

The company OpenCode owner must return the installed version/build and sanitized config-format summary from an approved pilot host. Only after the security/network owner supplies default-deny public egress plus an attempt monitor may the owner run one representative synthetic agent/skill/MCP flow and return the real discovery/call trace with provenance. Never use the local scripted model response as evidence of company agent reasoning or performance.
