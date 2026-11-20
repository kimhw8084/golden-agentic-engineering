# Offline Fab Sampling Prediction — OpenCode Repo Transfer Kit

**As of 2026-11-20.** 38 open-source repositories, exact owner/repo names, with full offline-first transfer procedures and a one-shot evaluation task for a local OpenCode environment. No fab data, application code, models, wheels or Git repositories have been downloaded into this starter kit. It is a *staging kit*, not a completed offline install.

## On the INTERNET-CONNECTED PC (NOT the fab work PC)

Prerequisites: Python 3.10+ and Git, corporate authorization to transfer open-source code. Choose an OS/CPU/Python matching the work PC for binary wheel preparation.

```bash
python fetch_repos.py --stage all
python verify_bundle.py
python download_wheels.py --requirements core
# Do NOT download extended/heavy until OpenCode has a reason to test them.
python pack_transfer.py
```

`fetch_repos.py` downloads all 38 repository source trees with shallow Git history and writes `repos.lock.json` containing exact commit SHAs. It does not clone submodules, fetch Git LFS objects, or download SMT2020 (or any other external data). **Check for missing submodules/LFS/datasets before declaring any repo testable.** A failed clone is never silently marked complete.

`download_wheels.py` downloads, but does **not install**, Python binary wheels and their dependencies for the selected requirement set. Ensure matched OS/architecture/Python ABI. Some source-only, GPU, Rust, C++, Oracle and SQL Server dependencies need separate approved artifacts. You can test source code with preinstalled work PC packages before making a wheelhouse.

`verify_wheelhouse.py` can verify the staged wheel hashes after transport.

`pack_transfer.py` packages sources, commit lock, the instructions and any downloaded wheelhouse as `fab_sampling_source_transfer.zip` next to this directory, with a `.sha256` hash. Scan and approve both archive and dependencies in accordance with work-PC policy.

## On the OFFLINE work PC

1. Verify transfer SHA256 and approved artifact provenance.
2. Extract the full source archive to a **read-only external-reference** directory. Do not overwrite existing fab prediction code.
3. Run `python verify_bundle.py` to check the Git SHA pins.
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
- `fetch_repos.py` — deterministic one-command source clone and Git pin capture.
- `verify_bundle.py` — local source consistency check.
- `requirements_*.txt` — controlled offline binary dependency candidates.
- `download_wheels.py` — staged download + wheel SHA256 checksums.
- `verify_wheelhouse.py` — verify binary SHA256 checksums locally.
- `pack_transfer.py` — source and binary archive builder.
- `OPENCODE_TASK.md` — high-rigor agent mission, success criteria and deliverables.
- `SCORECARD.md` — tests, output gates and ranking.
