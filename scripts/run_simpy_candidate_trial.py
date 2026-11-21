#!/usr/bin/env python3
"""Run a hash-pinned SimPy capacity smoke test from locally staged artifacts.

The wheel is not installed. The script validates its release hash, metadata,
license file and archive paths before importing it directly from the wheel.
No network calls, fab data or model are used.
"""
from __future__ import annotations

import argparse
import email
import hashlib
import json
import platform
import stat
import sys
import tarfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

WHEEL_NAME = "simpy-4.1.2-py3-none-any.whl"
WHEEL_SHA256 = "43071f84b6512c9b4fcb33ef057f240ccb1d1f3b263f9b4f9229d072e310b372"
LICENSE_PATH = "simpy-4.1.2.dist-info/licenses/LICENSE.rst"
LICENSE_SHA256 = "5f09a7bdf08f239271b15df1cbe2ba7f62649f8b497988274626f48638b84802"
SDIST_NAME = "simpy-4.1.2.tar.gz"
SDIST_SHA256 = "76ef36b71e0436ba94e55febc001c78879e493a323f045bbcfbb0b216e9b1fbc"
SDIST_LICENSE_PATH = "simpy-4.1.2/LICENSE.rst"
JOBS = (("A", 0, 3), ("B", 0, 2), ("C", 1, 1), ("D", 2, 1))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inspect_wheel(path: Path) -> dict[str, Any]:
    if path.name != WHEEL_NAME or path.is_symlink() or not path.is_file():
        raise ValueError("Expected the ordinary SimPy 4.1.2 wheel file")
    wheel_hash = sha256_file(path)
    if wheel_hash != WHEEL_SHA256:
        raise ValueError("SimPy wheel SHA-256 does not match the reviewed release artifact")
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("Wheel has duplicate archive paths")
        for info in archive.infolist():
            member = PurePosixPath(info.filename)
            if member.is_absolute() or ".." in member.parts or "\\" in info.filename:
                raise ValueError("Wheel contains an unsafe archive path")
            if stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError("Wheel contains a symbolic link")
        metadata_paths = [name for name in names if name.endswith(".dist-info/METADATA")]
        if len(metadata_paths) != 1 or LICENSE_PATH not in names:
            raise ValueError("Wheel lacks a unique package metadata file or expected license file")
        metadata = email.message_from_bytes(archive.read(metadata_paths[0]))
        if (metadata.get("Name", "").lower() != "simpy"
                or metadata.get("Version") != "4.1.2"
                or metadata.get("License") != "MIT"
                or metadata.get("Requires-Python") != ">=3.8"
                or metadata.get_all("Requires-Dist")):
            raise ValueError("Wheel metadata differs from the reviewed SimPy candidate")
        license_hash = hashlib.sha256(archive.read(LICENSE_PATH)).hexdigest()
        if license_hash != LICENSE_SHA256:
            raise ValueError("Embedded MIT license SHA-256 does not match reviewed source")
    return {
        "name": metadata["Name"],
        "version": metadata["Version"],
        "license": metadata["License"],
        "requires_python": metadata["Requires-Python"],
        "runtime_dependencies": metadata.get_all("Requires-Dist", []),
        "wheel": path.name,
        "wheel_sha256": wheel_hash,
        "wheel_bytes": path.stat().st_size,
        "license_path": LICENSE_PATH,
        "license_sha256": license_hash,
        "archive_paths_checked": len(names),
    }


def inspect_source_archive(path: Path) -> dict[str, Any]:
    if path.name != SDIST_NAME or path.is_symlink() or not path.is_file():
        raise ValueError("Expected the ordinary SimPy 4.1.2 source archive")
    source_hash = sha256_file(path)
    if source_hash != SDIST_SHA256:
        raise ValueError("SimPy source SHA-256 does not match the reviewed release artifact")
    with tarfile.open(path, "r:gz") as archive:
        members = archive.getmembers()
        names = [member.name for member in members]
        if len(names) != len(set(names)):
            raise ValueError("Source archive has duplicate member paths")
        for member in members:
            path_parts = PurePosixPath(member.name)
            if (path_parts.is_absolute() or ".." in path_parts.parts or "\\" in member.name
                    or not (member.isfile() or member.isdir())):
                raise ValueError("Source archive contains an unsafe member")
        if SDIST_LICENSE_PATH not in names or "simpy-4.1.2/PKG-INFO" not in names:
            raise ValueError("Source archive lacks the expected license or package metadata")
        license_member = archive.extractfile(SDIST_LICENSE_PATH)
        metadata_member = archive.extractfile("simpy-4.1.2/PKG-INFO")
        if license_member is None or metadata_member is None:
            raise ValueError("Could not read the source license or package metadata")
        license_bytes = license_member.read()
        metadata = email.message_from_bytes(metadata_member.read())
        if hashlib.sha256(license_bytes).hexdigest() != LICENSE_SHA256:
            raise ValueError("Source MIT license hash differs from the reviewed wheel license")
        if (metadata.get("Name", "").lower() != "simpy"
                or metadata.get("Version") != "4.1.2"
                or metadata.get("License") != "MIT"
                or metadata.get("Requires-Python") not in {">=3.8", ">= 3.8"}
                or metadata.get_all("Requires-Dist")):
            raise ValueError("Source metadata differs from the reviewed SimPy candidate")
    return {
        "source_archive": path.name,
        "source_sha256": source_hash,
        "source_bytes": path.stat().st_size,
        "source_members_checked": len(members),
        "license_path": SDIST_LICENSE_PATH,
        "license_sha256": LICENSE_SHA256,
        "runtime_dependencies": metadata.get_all("Requires-Dist", []),
    }


def simulate_capacity(simpy: Any, capacity: int) -> list[dict[str, int | str]]:
    env = simpy.Environment()
    tool = simpy.Resource(env, capacity=capacity)
    completed: list[dict[str, int | str]] = []

    def process(job_id: str, arrival: int, service: int):
        yield env.timeout(arrival)
        with tool.request() as request:
            yield request
            started = int(env.now)
            yield env.timeout(service)
            completed.append({
                "job": job_id,
                "arrival": arrival,
                "start": started,
                "completion": int(env.now),
                "wait": started - arrival,
            })

    for job_id, arrival, service in JOBS:
        env.process(process(job_id, arrival, service))
    env.run()
    return sorted(completed, key=lambda row: str(row["job"]))


def run_trial(
    wheel: Path,
    sdist: Path | None = None,
    execution_scope: str = "local",
) -> dict[str, Any]:
    candidate = inspect_wheel(wheel)
    source = inspect_source_archive(sdist) if sdist is not None else None
    sys.path.insert(0, str(wheel.resolve()))
    import simpy  # Imported only after wheel identity and embedded license checks.

    if getattr(simpy, "__version__", None) != "4.1.2":
        raise ValueError("Imported SimPy version does not match the reviewed wheel")
    one_tool = simulate_capacity(simpy, capacity=1)
    two_tools = simulate_capacity(simpy, capacity=2)
    expected_one = [("A", 0, 3, 0), ("B", 3, 5, 3), ("C", 5, 6, 4), ("D", 6, 7, 4)]
    expected_two = [("A", 0, 3, 0), ("B", 0, 2, 0), ("C", 2, 3, 1), ("D", 3, 4, 1)]
    observed_one = [(row["job"], row["start"], row["completion"], row["wait"]) for row in one_tool]
    observed_two = [(row["job"], row["start"], row["completion"], row["wait"]) for row in two_tools]
    if observed_one != expected_one or observed_two != expected_two:
        raise ValueError("SimPy event schedule differs from the independent fixture oracle")
    return {
        "schema": "golden-fab-simpy-candidate-trial/v1",
        "status": "PASS_SYNTHETIC_DISCRETE_EVENT_CONTRACT",
        "qualification": "CANDIDATE_ONLY_NOT_COMPANY_APPROVED",
        "candidate": {
            **candidate,
            **(source or {}),
            "source": "https://pypi.org/project/simpy/4.1.2/",
            "source_repository": "https://gitlab.com/team-simpy/simpy",
            "source_commit": "f43816490c6f76f336ad6e457d3cab9f386894af",
            "license_source": "https://gitlab.com/team-simpy/simpy/-/blob/4.1.2/LICENSE.rst",
            "pypi_build_provenance": "NOT_PUBLISHED_FOR_4.1.2",
        },
        "environment": {
            "python": platform.python_version(),
            "os": platform.system(),
            "architecture": platform.machine(),
            "runtime_import_source": "hash-verified wheel path; package not installed",
        },
        "method": {
            "fixture": "four synthetic jobs share a finite-capacity processing resource",
            "jobs": [{"job": job, "arrival": arrival, "service": service}
                     for job, arrival, service in JOBS],
            "compared_capacities": [1, 2],
            "independent_oracle": "fixed expected start/completion/wait schedule",
        },
        "results": {
            "one_tool": {"jobs": one_tool, "makespan": max(int(row["completion"]) for row in one_tool)},
            "two_tools": {"jobs": two_tools, "makespan": max(int(row["completion"]) for row in two_tools)},
            "oracle_match": True,
        },
        "network_calls": False,
        "model_calls": False,
        "real_fab_data_or_accuracy_claim": False,
        "windows_linux_native_execution": (
            f"PASS_GITHUB_HOSTED_{platform.system().upper()}"
            if execution_scope == "github-hosted" and platform.system() in {"Windows", "Linux"}
            else "NOT_RUN"
        ),
        "company_oss_clearance": "NOT_OBTAINED",
        "source_archive_validation": "PASS" if source is not None else "NOT_RUN",
        "execution_scope": execution_scope,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", required=True, type=Path)
    parser.add_argument("--sdist", type=Path, help="Optional hash-verified upstream source archive")
    parser.add_argument("--execution-scope", choices=("local", "github-hosted"), default="local")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = run_trial(args.wheel, args.sdist, args.execution_scope)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{result['status']} wheel_sha256={result['candidate']['wheel_sha256']} out={args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
