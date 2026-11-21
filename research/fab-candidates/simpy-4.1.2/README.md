# SimPy 4.1.2 candidate evidence

**State: evaluation only; not company approved or selected for production.** This is one candidate for discrete-event queue/capacity simulation in the fab sampling exploration. It is not a forecasting model, fab model, or source of production decisions. The tracked original fab transfer ZIP remains unchanged; this folder records a separate bounded evaluation of the SimPy candidate.

## Pin and license

- Canonical upstream: [team-simpy/simpy on GitLab](https://gitlab.com/team-simpy/simpy), protected and verified `4.1.2` tag at commit `f43816490c6f76f336ad6e457d3cab9f386894af`.
- PyPI lists the project source as GitLab, identifies the release as MIT, and reports no provenance attestation for either 4.1.2 artifact. The tag page marks 4.1.2 protected and verified. Those facts do not prove that the PyPI files were built from that commit.
- Runtime package metadata declares no dependencies and Python `>=3.8`. Building from the source archive requires `setuptools>=64` and `setuptools_scm[toml]>=8.0`; those build dependencies and their dependency/license closure are not staged here.
- The universal wheel is 27,375 bytes, SHA-256 `43071f84b6512c9b4fcb33ef057f240ccb1d1f3b263f9b4f9229d072e310b372`. The source archive is 410,129 bytes, SHA-256 `76ef36b71e0436ba94e55febc001c78879e493a323f045bbcfbb0b216e9b1fbc`. The MIT license embedded in both has SHA-256 `5f09a7bdf08f239271b15df1cbe2ba7f62649f8b497988274626f48638b84802`.
- [`candidate.json`](candidate.json) is the machine-readable review; [`requirements.lock`](requirements.lock) pins the wheel hash. The actual binary artifacts used for the trial are outside Git and are not included in the company transfer package.

The original fab kit points to `simpx/simpy` on GitHub, which is a fork. The extracted working copy now points to canonical upstream GitLab. The original user archive at `offline/source-archives/fab_sampling_offline_port_kit_2026-11-20.zip` remains byte-for-byte preserved.

## Evidence run

The Golden trial script first verifies exact wheel and source archive hashes, package version/license/dependency metadata, the matching MIT license bytes, and archive paths/types. It imports the verified wheel directly without installing it, runs four synthetic jobs sharing a capacity-limited resource, and compares start, completion, wait and makespan against a fixed expected schedule for capacities one and two.

Recorded result: [verification/2026-11-21/simpy-capacity-candidate.json](../../../verification/2026-11-21/simpy-capacity-candidate.json). The synthetic contract passed on the local macOS arm64 runtime. The upstream `tests/` directory passed 141 tests with 10 benchmark tests deselected. The complete upstream pytest command passed 159, deselected 10, and repeatedly failed one timing-sensitive real-time documentation doctest (observed 0.11 seconds, expected 0.10 seconds). `pytest-benchmark` was not staged, causing unknown-marker warnings. No Windows/Linux native run, company OpenCode run, network-attempt monitor, fab data, or task-value comparison is claimed.

## Reproduce with staged artifacts

On an internet-connected staging computer, fetch only the two exact artifact files from the [PyPI 4.1.2 release page](https://pypi.org/project/simpy/4.1.2/) into a local directory. Verify their hashes against [`candidate.json`](candidate.json) before transfer. Do not run this fetch step on a company runtime. After the package owner authorizes import, copy the artifacts to a reviewed local path and execute:

```powershell
python scripts/run_simpy_candidate_trial.py --wheel C:\staging\simpy-4.1.2-py3-none-any.whl --sdist C:\staging\simpy-4.1.2.tar.gz --out C:\staging\simpy-trial.json
```

```bash
python scripts/run_simpy_candidate_trial.py --wheel /staging/simpy-4.1.2-py3-none-any.whl --sdist /staging/simpy-4.1.2.tar.gz --out /staging/simpy-trial.json
```

The command itself does not install SimPy, invoke a model, or contact a package index. It tests artifact integrity and a minimal API contract only; the host still needs the appropriate Python runtime. A separate GitHub-hosted workflow downloads the hash-locked universal wheel from PyPI and runs this smoke test on hosted Ubuntu/Windows; its result is still not company-native evidence. Company OSS clearance, source review, representative model validation, and comparisons with alternatives are still required.
