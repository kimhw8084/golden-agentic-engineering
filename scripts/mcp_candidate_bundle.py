#!/usr/bin/env python3
"""Build and verify hash-pinned MCP SDK wheel candidate bundles offline.

Downloading is deliberately separate. Run pip download on an approved internet-
connected staging host, then use this script to validate, inventory and package
the local wheels. It never contacts a network or installs a package.
"""
from __future__ import annotations

import argparse
import email
import gzip
import hashlib
import json
import os
import re
import shutil
import stat
import tarfile
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

try:
    from pip._vendor.packaging.requirements import Requirement
    from pip._vendor.packaging.utils import canonicalize_name, parse_wheel_filename
    from pip._vendor.packaging.version import Version
except ImportError as exc:  # pragma: no cover - environment dependent
    raise SystemExit("This staging helper needs Python with pip's vendored packaging library.") from exc


SDK_VERSION = "2.3.0"
SDK_REPOSITORY = "https://github.com/modelcontextprotocol/python-sdk"
SDK_COMMIT = "2118f14f8a19bc158d8a1cf90af58d85d187f849"
TARGETS: dict[str, dict[str, Any]] = {
    "macos-arm64-cp311": {
        "os": "macOS", "architecture": "arm64", "python": "3.11",
        "sys_platform": "darwin", "platform_system": "Darwin", "platform_machine": "arm64",
        "accepted_platforms": ("any", "macosx_11_0_arm64", "macosx_11_0_universal2"),
    },
    "windows-amd64-cp311": {
        "os": "Windows", "architecture": "AMD64", "python": "3.11",
        "sys_platform": "win32", "platform_system": "Windows", "platform_machine": "AMD64",
        "accepted_platforms": ("any", "win_amd64"),
    },
    "linux-x86_64-glibc217-cp311": {
        "os": "Linux (glibc >= 2.17 / manylinux2014)", "architecture": "x86_64", "python": "3.11",
        "sys_platform": "linux", "platform_system": "Linux", "platform_machine": "x86_64",
        "accepted_platforms": ("any", "manylinux2014_x86_64", "manylinux_2_17_x86_64"),
    },
}
GENERATOR = "Golden MCP candidate bundle helper"
GENERATOR_VERSION = "1.0"
MAX_ARCHIVE_BYTES = 512 * 1024 * 1024


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalized(name: str) -> str:
    return canonicalize_name(name)


def safe_member(name: str) -> bool:
    member = PurePosixPath(name)
    return bool(name) and not member.is_absolute() and ".." not in member.parts and "\\" not in name


def _wheel_metadata(path: Path) -> dict[str, Any]:
    try:
        filename_name, filename_version, _build, tags = parse_wheel_filename(path.name)
        with zipfile.ZipFile(path) as wheel:
            names = wheel.namelist()
            if len(names) != len(set(names)):
                raise ValueError(f"Duplicate member in wheel: {path.name}")
            for info in wheel.infolist():
                if not safe_member(info.filename):
                    raise ValueError(f"Unsafe wheel member in {path.name}: {info.filename}")
                mode = info.external_attr >> 16
                if stat.S_ISLNK(mode):
                    raise ValueError(f"Symlink member in wheel: {path.name}:{info.filename}")
            metadata_names = [name for name in names if name.endswith(".dist-info/METADATA")]
            if len(metadata_names) != 1:
                raise ValueError(f"Expected one METADATA file in {path.name}")
            metadata = email.message_from_bytes(wheel.read(metadata_names[0]))
            name = metadata.get("Name")
            version = metadata.get("Version")
            if not name or not version:
                raise ValueError(f"Missing package name/version in {path.name}")
            if normalized(name) != normalized(str(filename_name)) or Version(version) != filename_version:
                raise ValueError(f"Wheel filename and METADATA disagree: {path.name}")
            license_paths = sorted(
                item for item in names
                if item.lower().endswith(("license", "license.txt", "license.md", "copying", "notice"))
                or "/.dist-info/licenses/" in f"/{item.lower()}"
            )
            license_files = [
                {"path": item, "sha256": sha256_bytes(wheel.read(item))}
                for item in license_paths
            ]
            sources = []
            for value in metadata.get_all("Project-URL", []):
                label, separator, url = value.partition(",")
                if separator and url.strip().startswith(("https://", "http://")):
                    sources.append({"label": label.strip(), "url": url.strip()})
            homepage = metadata.get("Home-page")
            if homepage and homepage.startswith(("https://", "http://")):
                sources.append({"label": "Home-page", "url": homepage})
            return {
                "name": name,
                "normalized_name": normalized(name),
                "version": version,
                "wheel": path.name,
                "wheel_sha256": sha256_file(path),
                "wheel_bytes": path.stat().st_size,
                "requires_dist": metadata.get_all("Requires-Dist", []),
                "license": metadata.get("License"),
                "license_expression": metadata.get("License-Expression"),
                "license_classifiers": [x for x in metadata.get_all("Classifier", []) if x.startswith("License ::")],
                "bundled_license_files": license_files,
                "source_references": sources,
                "tags": sorted(str(tag) for tag in tags),
            }
    except (OSError, zipfile.BadZipFile, ValueError) as exc:
        raise ValueError(f"Invalid wheel {path.name}: {exc}") from exc


def _check_platform(package: dict[str, Any], target: dict[str, Any]) -> None:
    accepted = target["accepted_platforms"]
    if not any(tag.rsplit("-", 1)[-1] in accepted for tag in package["tags"]):
        raise ValueError(f"Wheel {package['wheel']} is incompatible with target {target['name']}")
    if not any(tag.startswith("py3-none-") or tag.startswith("cp311-") for tag in package["tags"]):
        raise ValueError(f"Wheel {package['wheel']} does not target CPython 3.11 or pure Python")


def _dependency_closure(packages: dict[str, dict[str, Any]], target: dict[str, Any]) -> dict[str, list[str]]:
    environment = {
        "python_version": "3.11",
        "python_full_version": "3.11.0",
        "implementation_name": "cpython",
        "platform_python_implementation": "CPython",
        "sys_platform": target["sys_platform"],
        "platform_system": target["platform_system"],
        "platform_machine": target["platform_machine"],
    }
    root = normalized("mcp")
    if root not in packages or packages[root]["version"] != SDK_VERSION:
        raise ValueError(f"Wheelhouse must include mcp=={SDK_VERSION}")

    requested_extras: dict[str, set[str]] = {root: {""}}
    queue: list[tuple[str, str]] = [(root, "")]
    visited: set[tuple[str, str]] = set()
    dependencies: dict[str, set[str]] = {name: set() for name in packages}
    while queue:
        parent, extra = queue.pop(0)
        if (parent, extra) in visited:
            continue
        visited.add((parent, extra))
        package = packages[parent]
        for raw in package["requires_dist"]:
            requirement = Requirement(raw)
            if requirement.marker is not None:
                marker_environment = dict(environment, extra=extra)
                if not requirement.marker.evaluate(marker_environment):
                    continue
            child = normalized(requirement.name)
            if child not in packages:
                raise ValueError(f"Incomplete {target['name']} closure: {package['name']} requires missing {raw}")
            installed = Version(packages[child]["version"])
            if requirement.specifier and not requirement.specifier.contains(installed, prereleases=True):
                raise ValueError(f"Version mismatch for {raw}: staged {packages[child]['version']}")
            dependencies[parent].add(child)
            extras = set(requirement.extras) or {""}
            known = requested_extras.setdefault(child, set())
            for child_extra in extras - known:
                known.add(child_extra)
                queue.append((child, child_extra))
    return {name: sorted(edges) for name, edges in sorted(dependencies.items())}


def inspect_wheelhouse(wheel_dir: Path, target_name: str) -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, list[str]]]:
    if target_name not in TARGETS:
        raise ValueError(f"Unknown target: {target_name}")
    if not wheel_dir.is_dir() or wheel_dir.is_symlink():
        raise ValueError("Wheelhouse must be an ordinary directory")
    wheel_paths = sorted(wheel_dir.glob("*.whl"))
    if not wheel_paths:
        raise ValueError("Wheelhouse contains no wheels")
    if any(path.is_symlink() or not path.is_file() for path in wheel_paths):
        raise ValueError("Wheelhouse must contain only regular wheel files")

    target = dict(TARGETS[target_name], name=target_name)
    packages: dict[str, dict[str, Any]] = {}
    for path in wheel_paths:
        package = _wheel_metadata(path)
        _check_platform(package, target)
        key = package["normalized_name"]
        if key in packages:
            raise ValueError(f"Multiple versions of {package['name']} in wheelhouse")
        packages[key] = package

    if target_name == "windows-amd64-cp311" and normalized("pywin32") not in packages:
        raise ValueError("Windows MCP SDK closure is missing its pywin32 dependency")
    dependencies = _dependency_closure(packages, target)
    summary = {
        "name": target_name,
        "operating_system": target["os"],
        "architecture": target["architecture"],
        "python": target["python"],
        "compatibility": "CANDIDATE_ONLY_COMPANY_TARGET_UNKNOWN",
        "sdk": {"name": "mcp", "version": SDK_VERSION, "repository": SDK_REPOSITORY, "commit": SDK_COMMIT},
        "wheel_count": len(packages),
        "total_wheel_bytes": sum(package["wheel_bytes"] for package in packages.values()),
        "dependency_count": sum(len(edges) for edges in dependencies.values()),
        "company_oss_approval": "NOT_OBTAINED",
        "offline_install_test": "NOT_RUN_FOR_THIS_TARGET",
    }
    return summary, packages, dependencies


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _cyclonedx(summary: dict[str, Any], packages: dict[str, dict[str, Any]], dependencies: dict[str, list[str]]) -> dict[str, Any]:
    components = []
    for name, package in sorted(packages.items()):
        component: dict[str, Any] = {
            "type": "library",
            "name": package["name"],
            "version": package["version"],
            "purl": f"pkg:pypi/{package['normalized_name']}@{package['version']}",
            "bom-ref": f"pkg:pypi/{package['normalized_name']}@{package['version']}",
            "hashes": [{"alg": "SHA-256", "content": package["wheel_sha256"]}],
            "properties": [
                {"name": "golden:wheel", "value": package["wheel"]},
                {"name": "golden:license_metadata", "value": package["license"] or package["license_expression"] or "UNDECLARED"},
                {"name": "golden:bundled_license_file_count", "value": str(len(package["bundled_license_files"]))},
            ],
        }
        if package["license_expression"]:
            component["licenses"] = [{"expression": package["license_expression"]}]
        elif package["license"]:
            component["licenses"] = [{"license": {"name": package["license"]}}]
        if package["source_references"]:
            component["externalReferences"] = [
                {"type": "website", "url": reference["url"], "comment": reference["label"]}
                for reference in package["source_references"]
            ]
        components.append(component)
    edges = [
        {"ref": f"pkg:pypi/{name}@{packages[name]['version']}",
         "dependsOn": [f"pkg:pypi/{child}@{packages[child]['version']}" for child in children]}
        for name, children in sorted(dependencies.items())
    ]
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {"tools": [{"vendor": "Golden Agentic Engineering", "name": GENERATOR, "version": GENERATOR_VERSION}],
                     "component": {"type": "application", "name": "golden-mcp-sdk-candidate", "version": SDK_VERSION}},
        "components": components,
        "dependencies": edges,
    }


def _build_directory(wheel_dir: Path, target_name: str, output_dir: Path) -> Path:
    summary, packages, dependencies = inspect_wheelhouse(wheel_dir, target_name)
    root = output_dir / target_name
    if root.exists():
        raise FileExistsError(f"Refusing to overwrite existing candidate directory: {root}")
    wheels_dir = root / "wheelhouse"
    wheels_dir.mkdir(parents=True, exist_ok=False)
    for package in packages.values():
        shutil.copyfile(wheel_dir / package["wheel"], wheels_dir / package["wheel"])

    lock_lines = [
        f"{packages[name]['name']}=={packages[name]['version']} --hash=sha256:{packages[name]['wheel_sha256']}"
        for name in sorted(packages)
    ]
    (root / "requirements.lock").write_text("\n".join(lock_lines) + "\n", encoding="utf-8")
    inventory = {
        "schema": "golden-license-inventory/v1",
        "scope": "wheel METADATA declarations and license files physically embedded in each wheel; not legal review or company approval",
        "target": summary,
        "packages": [packages[name] for name in sorted(packages)],
    }
    _write_json(root / "license-inventory.json", inventory)
    _write_json(root / "cyclonedx.cdx.json", _cyclonedx(summary, packages, dependencies))
    files = []
    for path in sorted(p for p in root.rglob("*") if p.is_file() and p.name != "manifest.json"):
        files.append({"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    manifest = {
        "schema": "golden-mcp-wheel-candidate/v1",
        "target": summary,
        "source": {"index": "https://pypi.org/project/mcp/2.3.0/", "repository": SDK_REPOSITORY, "commit": SDK_COMMIT},
        "files": files,
        "limitations": [
            "Candidate target profile only; company OS, architecture, Python patch/ABI and glibc version remain unknown.",
            "No company OSS/security clearance is represented.",
            "Windows and Linux wheel candidates were not installed or executed on their native operating systems.",
            "SBOM/license fields derive from wheel metadata and embedded wheel files; independent legal and vulnerability review remain required.",
        ],
    }
    _write_json(root / "manifest.json", manifest)
    return root


def _archive_tree(root: Path, archive_path: Path) -> None:
    if archive_path.exists() or archive_path.with_suffix(archive_path.suffix + ".sha256").exists():
        raise FileExistsError(f"Refusing to overwrite candidate archive: {archive_path}")
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with archive_path.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
                for path in sorted(root.rglob("*")):
                    relative = path.relative_to(root.parent).as_posix()
                    info = tarfile.TarInfo(relative + ("/" if path.is_dir() else ""))
                    info.uid = 0
                    info.gid = 0
                    info.uname = ""
                    info.gname = ""
                    info.mtime = 0
                    info.mode = 0o755 if path.is_dir() else 0o644
                    if path.is_dir():
                        info.type = tarfile.DIRTYPE
                        archive.addfile(info)
                    else:
                        info.size = path.stat().st_size
                        with path.open("rb") as stream:
                            archive.addfile(info, stream)
    digest = sha256_file(archive_path)
    archive_path.with_suffix(archive_path.suffix + ".sha256").write_text(
        f"{digest}  {archive_path.name}\n", encoding="ascii"
    )


def create_candidate(wheel_dir: Path, target_name: str, output_dir: Path) -> Path:
    root = _build_directory(wheel_dir.resolve(), target_name, output_dir.resolve())
    archive_path = output_dir.resolve() / f"{target_name}.tar.gz"
    _archive_tree(root, archive_path)
    return archive_path


def verify_candidate(archive_path: Path) -> dict[str, Any]:
    archive_path = archive_path.resolve()
    checksum_path = archive_path.with_suffix(archive_path.suffix + ".sha256")
    if not archive_path.is_file() or archive_path.is_symlink() or not checksum_path.is_file():
        raise ValueError("Candidate archive and adjacent .sha256 sidecar are required")
    expected = checksum_path.read_text(encoding="ascii").split()[0]
    actual = sha256_file(archive_path)
    sidecar = checksum_path.read_text(encoding="ascii").strip()
    if not re.fullmatch(rf"{re.escape(expected)}  {re.escape(archive_path.name)}", sidecar):
        raise ValueError("Candidate checksum sidecar format or filename mismatch")
    if not re.fullmatch(r"[0-9a-f]{64}", expected) or expected != actual:
        raise ValueError("Candidate archive SHA-256 mismatch")
    if archive_path.stat().st_size > MAX_ARCHIVE_BYTES:
        raise ValueError("Candidate archive exceeds size limit")
    try:
        with tarfile.open(archive_path, "r:gz") as archive:
            members = archive.getmembers()
            if not members or len(members) != len({member.name for member in members}):
                raise ValueError("Empty archive or duplicate paths")
            for member in members:
                if not safe_member(member.name.rstrip("/")) or not (member.isfile() or member.isdir()):
                    raise ValueError(f"Unsafe archive member: {member.name}")
                if member.size > MAX_ARCHIVE_BYTES:
                    raise ValueError(f"Archive member exceeds size limit: {member.name}")
            manifests = [member for member in members if member.name.endswith("/manifest.json")]
            if len(manifests) != 1:
                raise ValueError("Expected one candidate manifest")
            manifest_member = manifests[0]
            manifest = json.load(archive.extractfile(manifest_member))
            if manifest.get("schema") != "golden-mcp-wheel-candidate/v1":
                raise ValueError("Unexpected candidate manifest schema")
            prefix = manifest_member.name.rsplit("/", 1)[0] + "/"
            if any(not member.name.startswith(prefix) for member in members):
                raise ValueError("Candidate archive contains paths outside its manifest root")
            expected_files = {entry["path"]: entry for entry in manifest.get("files", [])}
            actual_files = {member.name[len(prefix):]: member for member in members
                            if member.isfile() and member.name.startswith(prefix) and member.name != manifest_member.name}
            if set(expected_files) != set(actual_files):
                raise ValueError("Candidate archive contents do not match its manifest")
            if sum(member.size for member in members if member.isfile()) > MAX_ARCHIVE_BYTES:
                raise ValueError("Candidate archive expands beyond size limit")
            for path, entry in expected_files.items():
                stream = archive.extractfile(actual_files[path])
                digest = hashlib.sha256()
                size = 0
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    size += len(block)
                    digest.update(block)
                if size != entry.get("bytes") or digest.hexdigest() != entry.get("sha256"):
                    raise ValueError(f"Candidate content hash mismatch: {path}")
            target = manifest.get("target", {})
            if target.get("sdk", {}).get("version") != SDK_VERSION or target.get("company_oss_approval") != "NOT_OBTAINED":
                raise ValueError("Candidate manifest overstates approval or changes the SDK pin")
            return {"status": "VERIFIED_CANDIDATE_ONLY", "target": target.get("name"),
                    "files": len(expected_files), "sha256": actual, "bytes": archive_path.stat().st_size}
    except (OSError, tarfile.TarError, json.JSONDecodeError, AttributeError) as exc:
        raise ValueError(f"Invalid candidate archive: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("create", help="create a bundle from an already-downloaded wheelhouse")
    build.add_argument("--target", choices=sorted(TARGETS), required=True)
    build.add_argument("--wheel-dir", type=Path, required=True)
    build.add_argument("--out-dir", type=Path, required=True)
    verify = subparsers.add_parser("verify", help="verify a candidate archive and all contained hashes")
    verify.add_argument("archive", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "create":
            result = create_candidate(args.wheel_dir, args.target, args.out_dir)
            verified = verify_candidate(result)
            print(json.dumps({"archive": str(result), **verified}, sort_keys=True))
        else:
            print(json.dumps(verify_candidate(args.archive), sort_keys=True))
    except (FileExistsError, OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(2, f"candidate bundle error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
