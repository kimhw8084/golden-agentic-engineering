# Offline Fab Sampling Prediction — OpenCode Repo Transfer Kit

**As of 2026-11-20.** 38 open-source repositories, exact owner/repo names, with full offline-first transfer procedures and a one-shot evaluation task for a local OpenCode environment. No fab data, application code, models, wheels or Git repositories have been downloaded into this starter kit. It is a *staging kit*, not a completed offline install.

The original user-supplied archive is preserved byte-for-byte at [`offline/source-archives/fab_sampling_offline_port_kit_2026-11-20.zip`](../offline/source-archives/fab_sampling_offline_port_kit_2026-11-20.zip) (SHA-256 `0d8e88391f4a885897e4c498730cb36972f07d20f3678a3950e89d106d32272d`, 20,292 bytes). The extracted folder is the working copy; selected instructions and manifests have been hardened since extraction, including a correction from the SimPy GitHub fork to its canonical upstream GitLab project. The archive contains the kit procedures and candidate manifest, not candidate repository clones or offline dependency assets.

## On the INTERNET-CONNECTED PC (NOT the fab work PC)

Prerequisites: Python 3.10+ and Git, corporate authorization to transfer open-source code. Choose an OS/CPU/Python matching the work PC for binary wheel preparation.

```bash
# After the source owner selects and approves exact candidates from REPOS.md:
python fetch_repos.py --repo tobymao/sqlglot --repo unionai-oss/pandera
python verify_bundle.py --allow-incomplete
python pack_transfer.py --allow-incomplete
```

`fetch_repos.py --output` accepts a staging directory only when it remains inside this kit; the lock records a kit-relative path so it contains no staging-PC absolute path and the verifier checks that exact location. The verifier also checks each Git origin against the manifest. `pack_transfer.py --output PATH` can choose an archive destination outside the kit. It refuses to overwrite an archive/checksum and refuses to package symlinks.

`fetch_repos.py` requires an explicit `--stage` or repeated exact `--repo OWNER/REPO` selection; it never defaults to all 38 candidates. `--stage all` remains available only as an explicit full-scope request. It downloads selected source trees with shallow Git history and records exact commit SHAs and Git origins in `repos.lock.json`. A partial lock is accepted only by `verify_bundle.py --allow-incomplete`; that mode verifies every selected clone and refuses unknown lock entries, while the default requires all manifest candidates. The packer runs the matching verifier even for a partial transfer. This verifies local source identity only; it is not license, security, or company-transfer approval. The fetcher does not clone submodules, fetch Git LFS objects, or download SMT2020 (or any other external data). **Check for missing submodules/LFS/datasets before declaring any repo testable.** A failed clone is never silently marked complete.

`download_wheels.py` downloads, but does **not install**, Python binary wheels and their dependencies for the selected requirement set. Ensure matched OS/architecture/Python ABI. Some source-only, GPU, Rust, C++, Oracle and SQL Server dependencies need separate approved artifacts. You can test source code with preinstalled work PC packages before making a wheelhouse.

The checked-in `requirements_core.txt` is a broad candidate list, not a dependency closure derived from the exact `--repo` subset. Review and reduce it for the selected sources, target ABI and company-approved packages before running `python download_wheels.py --requirements core`; do not download it by habit. The kit does not yet emit a complete resolved, hash-pinned dependency lock or SBOM for downloaded wheels.

`verify_wheelhouse.py` can verify the staged wheel hashes after transport.

`pack_transfer.py` packages sources, commit lock, the instructions and any downloaded wheelhouse as `fab_sampling_source_transfer.zip` next to this directory, with a `.sha256` hash. The default requires a full 38-repository verification; `--allow-incomplete` explicitly permits a partial evaluation archive only after verifying all selected source identities. Scan and approve both archive and dependencies in accordance with work-PC policy.

## On the OFFLINE work PC

1. Verify transfer SHA256 and approved artifact provenance.
2. Extract the full source archive to a **read-only external-reference** directory. Do not overwrite existing fab prediction code.
3. Run `python verify_bundle.py --allow-incomplete` to verify the explicitly locked subset's Git SHA and origins. Omit the flag only when all 38 manifest entries were staged and approved for transfer.
4. Prior to installing, check all source licenses, bundled data licenses, dependencies and system-native libraries. **No auto-pip, auto-git, auto-model download, or unapproved execution.**
5. If `wheelhouse/core/` is complete for your target and approved, use an isolated Python environment, e.g.:
   `python -m pip install --no-index --find-links ./wheelhouse/core -r requirements_core.txt`
   If resolver or ABI fails, stop and rebuild the wheelhouse on an appropriate staging OS; do not silently fall back online.
6. Give OpenCode the complete content of `OPENCODE_TASK.md`, and point it to: (a) current real fab algorithm/logic codebase; (b) source reference directory; (c) read-only valid historical snapshots if available.
7. Keep production environment untouched. All changes remain in a separate evaluation branch/sandbox until approved.

## Evaluation philosophy

- Never replace exact route, sampling-rule or metrology calculations with an ML guess.
- Measure whether each library improves historical, time-respecting replay under true as-of-time availability.
- Source code license is **not** a blanket grant to bundled datasets, models, third-party assets or dependencies.
- Fab simulation examples use abstractions. Compare against real lot states and actual metrology arrivals before claiming accuracy.
- Never connect to external servers from work PC; enforce network restriction, not merely prompt requests.

## Files

- `REPOS.md` — ranked, clickable full list of all 38 source repositories.
- `clone_urls.txt` — exact Git URLs, one per line.
- `repos.json` — machine-readable manifest.
- `fetch_repos.py` — explicitly selected source clones and Git pin capture; no default bulk download.
- `verify_bundle.py` — local source consistency check.
- `requirements_*.txt` — controlled offline binary dependency candidates.
- `download_wheels.py` — staged download + wheel SHA256 checksums.
- `verify_wheelhouse.py` — verify binary SHA256 checksums locally.
- `pack_transfer.py` — source and binary archive builder.
- `OPENCODE_TASK.md` — high-rigor agent mission, success criteria and deliverables.
- `SCORECARD.md` — tests, output gates and ranking.
