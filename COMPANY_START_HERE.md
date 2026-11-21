# Company start here

**Current state: PRE_QUALIFICATION.** This public repository contains no company data. Transfer it through the approved import path. Golden does not install packages, download models, enable an MCP server, edit provider settings, create a repository, or change company Git state.

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
- The React fixture has a transitive lock and a tested macOS arm64 setup. It does not include an offline npm cache in the transfer bundle; Windows/Linux variants, four missing license text files, company license clearance, and Playwright browsers still need review/staging.
- A pinned, reviewed MCP Python SDK wheelhouse. The local MCP fixture is disabled and is not the SDK.
- Company default-deny egress policy and endpoint attempt-monitoring evidence.
- Internal OpenCode version/config compatibility test and authentic agent/skill/MCP call evidence after the egress gate is proven.
- Existing company Git/CI/artifact/SSO integration owners and qualification review; Golden must reuse those systems.

See [`OPEN_ITEMS_FOR_COMPANY.md`](OPEN_ITEMS_FOR_COMPANY.md) for owners and priorities. The team lead decides whether to issue any Golden release. Do not label this starter company-qualified.
