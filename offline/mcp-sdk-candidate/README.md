# MCP Python SDK wheel candidate

**State: verified candidate only.** This is a staged, hash-locked package set for evaluating the official MCP Python SDK v2.3.0. It is not company-approved or qualified for the company's unknown Windows/Linux images. The generated wheel archives are kept outside this public Git repository; `candidate-manifest.json` records their names and hashes.

## Pin and review scope

- Upstream: [`modelcontextprotocol/python-sdk`](https://github.com/modelcontextprotocol/python-sdk), release [`v2.3.0`](https://github.com/modelcontextprotocol/python-sdk/releases/tag/v2.3.0), source commit `2118f14f8a19bc158d8a1cf90af58d85d187f849`.
- Package pin: `mcp==2.3.0`; candidate runtime is CPython 3.11.
- Candidate targets: macOS arm64, Windows AMD64, and Linux x86-64 with glibc 2.17 or newer.
- The generated inventories record package metadata, every wheel hash, embedded license-file hashes, dependency edges, and CycloneDX 1.5 SBOM components. Each dependency had at least one embedded license file in the staged wheels. Metadata and embedded files still require company OSS and vulnerability review; they are not legal approval.
- Windows and Linux are cross-platform wheel candidates created on macOS. Neither was installed or run on its native OS. The exact company OS build, Python patch version, ABI, and glibc remain unknown.

## Reproduce the candidate wheelhouses

Use an internet-connected staging host only. Pin the target tags to the actual company inventory before producing a company bundle. These sample commands use CPython 3.11 and do not install anything:

```sh
python -m pip download --only-binary=:all: --dest wheelhouse/macos-arm64 --implementation cp --python-version 311 --abi cp311 --platform macosx_11_0_arm64 mcp==2.3.0
python -m pip download --only-binary=:all: --dest wheelhouse/windows-amd64 --implementation cp --python-version 311 --abi cp311 --platform win_amd64 mcp==2.3.0 pywin32==311
python -m pip download --only-binary=:all: --dest wheelhouse/linux-x86_64 --implementation cp --python-version 311 --abi cp311 --platform manylinux2014_x86_64 --platform manylinux_2_17_x86_64 --platform manylinux_2_28_x86_64 mcp==2.3.0
```

Pip's cross-platform resolver omitted the Windows-only `pywin32` wheel in the first staging attempt, so include that explicit Windows pin. The helper also rejects a Windows wheelhouse without `pywin32` and rejects missing target-specific transitive dependencies.

Create and verify a bundle with the standard-library helper (it uses `pip`'s vendored packaging parser and makes no network request):

```sh
python scripts/mcp_candidate_bundle.py create --target macos-arm64-cp311 --wheel-dir wheelhouse/macos-arm64 --out-dir transfer/mcp
python scripts/mcp_candidate_bundle.py create --target windows-amd64-cp311 --wheel-dir wheelhouse/windows-amd64 --out-dir transfer/mcp
python scripts/mcp_candidate_bundle.py create --target linux-x86_64-glibc217-cp311 --wheel-dir wheelhouse/linux-x86_64 --out-dir transfer/mcp
python scripts/mcp_candidate_bundle.py verify transfer/mcp/macos-arm64-cp311.tar.gz
```

Each archive contains the complete `.whl` set, `requirements.lock` with SHA-256 hashes, `license-inventory.json`, `cyclonedx.cdx.json`, and a per-archive `manifest.json`. Transfer the archive and its adjacent `.sha256` through the approved internal import path. On the receiving host, verify before extracting and install only from the wheelhouse:

```sh
python scripts/mcp_candidate_bundle.py verify /approved-transfer/macos-arm64-cp311.tar.gz
python -m pip install --no-index --find-links ./macos-arm64-cp311/wheelhouse --require-hashes -r ./macos-arm64-cp311/requirements.lock
python -m pip check
```

Do not use these profile names until the company owner confirms the target really is CPython 3.11 on the listed OS/architecture. Match the company's exact OS, ABI, and glibc policy and rebuild when they differ.

## Observed installation evidence

The macOS arm64 candidate was installed from the local wheelhouse with `pip --no-index --require-hashes`; `pip check` passed and importing `MCPServer` reported `mcp==2.3.0` and `mcp-types==2.3.0`. The SDK-backed synthetic fixture passed a local stdio discovery and read-only tool call. The Windows and Linux packages were downloaded and structurally verified only.

The OpenCode v2.2.7 probe did **not** establish OpenCode-to-SDK MCP compatibility: the `2026-07-28` pin failed discovery because this SDK fixture did not offer the pinned protocol, and its legacy mode timed out. The actual company OpenCode build remains unknown. Continue using the repo's disabled-by-default JSON-RPC fixture for standard-library contract tests; do not enable the SDK server in company config based on this evidence.
