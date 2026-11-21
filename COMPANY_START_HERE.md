# Company start here

**Current state: PRE_QUALIFICATION.** This public repository contains no company data. Transfer it through the approved import path. Golden does not install packages, download models, enable an MCP server, edit provider settings, create a repository, or change company Git state.

## Source-side pre-company assessment

Run the local deterministic assessment from a clean, full Git checkout to record the checked-out commit, source checksums, tests, offline React install, synthetic fixtures, network-hook probe, asset/license gaps, Golden full-check blockers, and required company-owner actions. It writes JSON and Markdown reports. A complete local run exits `2` with `PRE_QUALIFICATION`; exit `3` means a local check failed, the worktree is dirty, or evidence is incomplete. Package managers run in offline mode. The assessment does not start OpenCode or a model and does not replace company egress controls.

### Windows PowerShell

```powershell
py -3 scripts\precompany_readiness.py --out "$env:TEMP\golden-readiness.json" --report "$env:TEMP\golden-readiness.md"
```

### Linux shell

```sh
python3 scripts/precompany_readiness.py --out /tmp/golden-readiness.json --report /tmp/golden-readiness.md
```

## Local runtime evidence (2026-11-21)

The local OpenCode binary reports V1 `1.3.9`; it is not the company's runtime. An official checksum-verified OpenCode V2 `2.2.7` binary was also tested in an isolated temporary project under a macOS Seatbelt profile that allowed loopback only. With a local custom provider and no catalog-fetch-disable environment, it attempted `GET https://models.opencode.ai/experimental/v2.0/api.json`; the sandbox denied the request. Repeating with `OPENCODE_DISABLE_MODELS_FETCH=1` produced no catalog-fetch log event. The OpenCode project config now denies `webfetch` and `websearch`; the V2 probe confirmed they were absent from the model tool list. The probe also set `OPENCODE_DISABLE_AUTOUPDATE=1`, but did not separately capture updater traffic. Neither environment setting nor project permissions replace company egress enforcement or attempt monitoring.

The V2 probe successfully loaded `golden-routing` through the native OpenCode `skill` tool using a scripted loopback model. After correcting the test timeout to the documented millisecond units, OpenCode v2.2.7 completed MCP discovery and a read-only call against the staged official Python SDK fixture in both automatic and pinned `2026-07-28` protocol modes. It also fell back from `server/discover` to legacy initialization and completed a call against Golden's standard-library fixture in automatic mode. The scripted model is not evidence of model reasoning or injection resistance. These local macOS traces do not qualify the company's build or Windows/Linux hosts. The older local V1 CLI rejected the V2 MCP config, and its earlier skill subprocess probe was blocked by the hosted sandbox. See [`RUNTIME_COMPATIBILITY_MATRIX.md`](RUNTIME_COMPATIBILITY_MATRIX.md) and [`offline/mcp-sdk-candidate/README.md`](offline/mcp-sdk-candidate/README.md).

### Before starting a company OpenCode process

The company OpenCode owner must set `OPENCODE_DISABLE_AUTOUPDATE=1` and `OPENCODE_DISABLE_MODELS_FETCH=1` on the **actual server process** and confirm both are inherited by standalone CLI runs. The catalog setting is identified by an OpenCode maintainer in [issue #34730](https://github.com/anomalyco/opencode/issues/34730); the update setting is described in [OpenCode's environment-variable guidance](https://github.com/anomalyco/opencode/issues/55308) and [global update configuration](https://opencode.ai/docs/config/). If the company uses a managed background service, setting variables only in a client shell is not enough; update the approved service environment and restart it under the company's change process. The project config also denies public webfetch and websearch. OpenCode's desktop updater has a separate update path; if the desktop app is used, the company owner must disable or network-block that updater separately. These application settings are not a verified network boundary; the security/network owner must deploy a default-deny intranet-only egress policy for OpenCode and all child processes and verify attempts with its monitor before any company task runs.

Standalone CLI launch examples after the company owners have verified the egress gate:

```powershell
$env:OPENCODE_DISABLE_AUTOUPDATE = "1"
$env:OPENCODE_DISABLE_MODELS_FETCH = "1"
opencode --standalone
```

```sh
OPENCODE_DISABLE_AUTOUPDATE=1 OPENCODE_DISABLE_MODELS_FETCH=1 opencode --standalone
```

Do not use the local runtime probe as a substitute for the company's monitored pilot.

Do not run OpenCode for a company task until the company security/network owner has enforced and monitored default-deny public egress for it and every child process. A logged failed lookup does not prove that a different host or build is blocked.

## Step A — offline doctor / dry run

The supported handoff is one command here and one reviewed apply command in Step B. Apply rechecks the approved source archive's checksum and file hashes.

Run this with Python 3.10+ from the extracted Golden folder. It reads platform/runtime presence, the current OpenCode config format and safe structure counts, file permissions, and the source bundle manifest. It accepts JSON and JSONC (comments and trailing commas) and flags simultaneous `opencode.json` and `opencode.jsonc` files for review. It does **not** run `opencode`, `node`, `git`, package managers, or any network request. It reads OpenCode/Node versions only from matching local package metadata or a managed-install version path; if it cannot identify a version, the result stays `UNKNOWN` and Step B is blocked.

The default user config lookup follows [OpenCode's documented global config location](https://opencode.ai/docs/config/): `~/.config/opencode/opencode.json` or `.jsonc`, with `XDG_CONFIG_HOME` honored when set.

### Windows PowerShell

```powershell
py -3 scripts\company_bootstrap.py doctor --out "$env:TEMP\golden-doctor.json"
```

### Linux shell

```sh
python3 scripts/company_bootstrap.py doctor --out /tmp/golden-doctor.json
```

Replace example paths with your approved transfer/config paths. Step B verifies the archive checksum and contents before applying. Do not execute OpenCode just to fill in its version. Do not start OpenCode until its package/update behavior and all child tools have been checked for zero public-network attempts; the company network owner must provide default-deny egress and an attempt monitor first.

Example dry-run summary (from a unit-tested synthetic runtime fixture; it does not qualify a company host):

```text
UNKNOWN: OS=Windows Python=3.12.x Node=None OpenCode=None
No settings changed. Missing offline assets: 6
Review diff: {"would_copy": ["agents/", "skills/", "commands/"], "would_not_change": ["provider", "model", "authentication", "MCP configuration", "Git state"]}
```

The JSON result contains no provider values, tokens, or raw command output. Review its machine/config states, `offline_assets_missing`, and `review_diff`. `READY_TO_INTEGRATE` means local runtime metadata matched a public V2 candidate and staged file hashes passed this preflight; this is not an internal OpenCode compatibility test, company approval, or qualification. The company OpenCode owner must verify behavior before rollout.

## Step B — reviewed apply

Only after a person has reviewed Step A and the archive checksum/content, and the company OpenCode owner confirms the installed build is compatible, run the add-only apply command below. Apply rechecks the archive checksum, paths and file hashes. The doctor reads local package metadata or managed-install paths and does not execute OpenCode or Node. If it cannot identify a version, it returns `UNKNOWN`; use an approved company inventory or compatible packaged runtime before applying. This applies `.opencode/agents`, `.opencode/skills`, and `.opencode/commands`; it never copies `.opencode/opencode.json`, provider/model/auth settings, or MCP config. Existing changed files are conflicts; no file is overwritten. Apply safely creates a missing OpenCode config directory after the reviewed doctor result and explicit authorization pass. The transaction record allows rollback of only the unchanged files created by this transaction.

### Windows PowerShell

```powershell
py -3 scripts\company_bootstrap.py apply --doctor-result "$env:TEMP\golden-doctor.json" --bundle "D:\approved-transfer\golden.tar.gz" --transaction "$env:TEMP\golden-transaction.json" --authorize-reviewed-apply
```

### Linux shell

```sh
python3 scripts/company_bootstrap.py apply --doctor-result /tmp/golden-doctor.json --bundle /approved-transfer/golden.tar.gz --transaction /tmp/golden-transaction.json --authorize-reviewed-apply
```

The apply command defaults to the same OpenCode config root used by doctor. If Step A used a custom `--config` path, pass the matching `--target` directory explicitly.

The `--authorize-reviewed-apply` flag is the explicit Step B action. Run `rollback` only if you want to remove files added by that transaction. Rollback refuses files that changed after apply. The apply path smoke-tests a synthetic manifest in a temporary directory; it does not start OpenCode or deploy an application.

### Optional rollback

Run this only if you choose to undo a reviewed apply. It removes only unchanged files recorded by that transaction.

```powershell
py -3 scripts\company_bootstrap.py rollback --transaction "$env:TEMP\golden-transaction.json"
```

```sh
python3 scripts/company_bootstrap.py rollback --transaction /tmp/golden-transaction.json
```

## What is still needed

- Approved Windows and Linux dependency/browser bundles with hashes, license/NOTICE, and SBOM.
- The active React fixture now pins Vitest 4.1.12 and Vite 7.3.8; its local offline install, typecheck, tests, build and public npm audit pass. It still contains `stackback@0.0.2` with a missing bundled MIT text. A separate Vitest 5.1.1/Vite 7.3.8 candidate removes `stackback`, passes its local offline-cache test and has a clean public npm audit, but requires Node `^22.12.0 || ^24.0.0 || >=26.0.0`; the company Node target is unknown, so the candidate remains unselected. Neither lock includes a transferable npm cache. Company license clearance, target-specific Windows/Linux package stores and Playwright browsers still need review/staging. See [`DEPENDENCY_LICENSE_REPORT.md`](DEPENDENCY_LICENSE_REPORT.md).
- A pinned, reviewed MCP Python SDK wheelhouse. The local MCP fixture is disabled and is not the SDK.
- Company default-deny egress policy and endpoint attempt-monitoring evidence.
- Internal OpenCode version/config compatibility test and authentic agent/skill/MCP call evidence after the egress gate is proven.
- Existing company Git/CI/artifact/SSO integration owners and qualification review; Golden must reuse those systems.

See [`OPEN_ITEMS_FOR_COMPANY.md`](OPEN_ITEMS_FOR_COMPANY.md) for owners and priorities. The team lead decides whether to issue any Golden release. Do not label this starter company-qualified.
