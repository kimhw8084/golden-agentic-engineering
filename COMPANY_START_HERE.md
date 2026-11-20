# Company start here

**Current state: PRE_QUALIFICATION.** This public repository contains no company data. Transfer it through the approved import path. Golden does not install packages, download models, enable an MCP server, edit provider settings, create a repository, or change company Git state.

## Step A — offline doctor / dry run

Run this with Python 3.10+ from the extracted Golden folder. It reads platform/runtime presence, the current OpenCode config key names, file permissions, and the source bundle manifest. It does **not** run `opencode`, `node`, `git`, package managers, or any network request. Supply the OpenCode version from the company's local software inventory; if not supplied or the executable is not discoverable, the result stays `UNKNOWN` and Step B is blocked.

### Windows PowerShell

```powershell
py -3 scripts\company_bootstrap.py doctor --opencode-version 2.4.0 --node-version 20.0.0 --out "$env:TEMP\golden-doctor.json" --config "$env:APPDATA\opencode\opencode.json"
py -3 scripts\package_offline.py verify "D:\approved-transfer\golden.tar.gz"
```

### Linux shell

```sh
python3 scripts/company_bootstrap.py doctor --opencode-version 2.4.0 --node-version 20.0.0 --out /tmp/golden-doctor.json --config "$HOME/.config/opencode/opencode.json"
python3 scripts/package_offline.py verify /approved-transfer/golden.tar.gz
```

Replace example versions and paths with values from your approved local inventory. Do not execute OpenCode just to fill in its version. Do not start OpenCode until its package/update behavior and all child tools have been checked for zero public-network attempts; the company network owner must provide default-deny egress and an attempt monitor first.

Example dry-run summary (illustrative only):

```text
UNKNOWN: OS=Windows Python=3.12.x Node=None OpenCode=None
No settings changed. Missing offline assets: 6
Review diff: {"would_copy": ["agents/", "skills/", "commands/"], "would_not_change": ["provider", "model", "authentication", "MCP configuration", "Git state"]}
```

The JSON result contains no provider values, tokens, or raw command output. Review its machine/config states, `offline_assets_missing`, and `review_diff`. `READY_TO_INTEGRATE` means the staged files and hashes passed this local preflight; it is not company approval or qualification.

## Step B — reviewed apply

Only after a person has reviewed Step A and the archive checksum/content, and the installed OpenCode version is a supported V2 candidate, run the add-only apply command below. This applies `.opencode/agents`, `.opencode/skills`, and `.opencode/commands`; it never copies `.opencode/opencode.json`, provider/model/auth settings, or MCP config. Existing changed files are conflicts; no file is overwritten. The transaction record allows rollback of only the unchanged files created by this transaction.

### Windows PowerShell

```powershell
py -3 scripts\company_bootstrap.py apply --doctor-result "$env:TEMP\golden-doctor.json" --bundle "D:\approved-transfer\golden.tar.gz" --target "$env:APPDATA\opencode" --transaction "$env:TEMP\golden-transaction.json" --authorize-reviewed-apply
```

### Linux shell

```sh
python3 scripts/company_bootstrap.py apply --doctor-result /tmp/golden-doctor.json --bundle /approved-transfer/golden.tar.gz --target "$HOME/.config/opencode" --transaction /tmp/golden-transaction.json --authorize-reviewed-apply
```

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
- A reviewed React lockfile/offline npm store and Playwright browsers; neither is present.
- A pinned, reviewed MCP Python SDK wheelhouse. The local MCP fixture is disabled and is not the SDK.
- Company default-deny egress policy and endpoint attempt-monitoring evidence.
- Internal OpenCode version/config compatibility test and authentic agent/skill/MCP call evidence after the egress gate is proven.
- Existing company Git/CI/artifact/SSO integration owners and qualification review; Golden must reuse those systems.

See [`OPEN_ITEMS_FOR_COMPANY.md`](OPEN_ITEMS_FOR_COMPANY.md) for owners and priorities. The team lead decides whether to issue any Golden release. Do not label this starter company-qualified.
