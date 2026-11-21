#!/usr/bin/env python3
"""Validate pinned supplemental license evidence for the React dependency audit."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse


EXPECTED_NOTICE_PACKAGES = {
    "@esbuild/darwin-arm64",
    "@rollup/rollup-darwin-arm64",
    "css.escape",
}
EXPECTED_UNRESOLVED_PACKAGES = {"stackback"}
EXPECTED_MISSING_TARBALL_NOTICES = EXPECTED_NOTICE_PACKAGES | EXPECTED_UNRESOLVED_PACKAGES
EXPECTED_SOURCE_PINS = {
    "@esbuild/darwin-arm64": (
        "https://github.com/evanw/esbuild", "v0.28.2",
        "609683d892977362a0f99026cb74b96263d728a9", "LICENSE.md",
    ),
    "@rollup/rollup-darwin-arm64": (
        "https://github.com/rollup/rollup", "v4.68.7",
        "dd75c77b718581406bd6886f84dfdf2ebf50c5e7", "LICENSE.md",
    ),
    "css.escape": (
        "https://github.com/mathiasbynens/CSS.escape", "v1.5.1",
        "b036d330b93f58b1bc87f1097fdc822da58e090f", "LICENSE-MIT.txt",
    ),
}
EXPECTED_STACKBACK_SOURCE_COMMIT = "24d55717e16f1bb2109e848ea2b3a90ea900ddb5"
EXPECTED_STACKBACK_SOURCE_BLOBS = {
    "package.json": "3e8b7b2c023d3535e0869b0959616cda4d654fc8",
    "index.js": "8b87042343d7e6fc238075138f72f4ff3fa58d5e",
    "formatstack.js": "d64307d210dd134dff936607480695b86f3b6776",
    "README.md": "fb6bde7486827b31d96cd2bfc1f96fd945bbf011",
    "test.js": "212b414ab496cf76d2a6977bd935ce714508482f",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_NORMALIZATION = "Hash UTF-8 notice bytes after converting CRLF to LF; reject other carriage returns."
COPY_TRANSFORM = "Preserved words and punctuation; removed trailing whitespace and extra final blank lines from the upstream text."


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(root: Path) -> list[str]:
    """Return evidence or integrity errors without making network calls."""
    errors: list[str] = []
    manifest_path = root / "research/react-license-supplements.json"
    try:
        manifest = _read_json(manifest_path)
        audit = _read_json(root / "research/react-macos-arm64-dependency-audit.json")
        lock = _read_json(root / "examples/react-app/package-lock.json")
    except (OSError, ValueError) as exc:
        return [f"React license supplement evidence unreadable ({type(exc).__name__})"]

    if not isinstance(manifest, dict) or manifest.get("schema") != "golden-react-package-license-supplements/v1":
        return ["React license supplement manifest has an unsupported schema"]
    if manifest.get("status") != "SUPPLEMENTAL_UPSTREAM_NOTICES; PACKAGE_TARBALL_NOTICE_GAPS_AND_COMPANY_CLEARANCE_REMAIN":
        errors.append("React license supplement status must retain the package-tarball and company-clearance gaps")
    if manifest.get("sha256_normalization") != SHA256_NORMALIZATION:
        errors.append("React license supplement must state its cross-platform SHA-256 newline normalization")

    audit_ref = manifest.get("source_package_audit")
    if not isinstance(audit_ref, dict):
        errors.append("React license supplement must identify its package audit and lock")
        audit_ref = {}
    audit_rows = audit.get("packages") if isinstance(audit, dict) else None
    audit_by_name = {row.get("name"): row for row in audit_rows if isinstance(row, dict)} if isinstance(audit_rows, list) else {}
    lock_rows = lock.get("packages") if isinstance(lock, dict) else None
    if not isinstance(lock_rows, dict):
        lock_rows = {}
    try:
        # Read only the known repo lock path. Never follow a path supplied by JSON.
        lock_path = root / "examples/react-app/package-lock.json"
        lock_digest = hashlib.sha256(lock_path.read_bytes()).hexdigest()
    except (OSError, TypeError):
        lock_digest = None
    audit_lock = audit.get("package_lock") if isinstance(audit, dict) else None
    audit_lock_digest = audit_lock.get("sha256") if isinstance(audit_lock, dict) else None
    if (audit_ref.get("path") != "research/react-macos-arm64-dependency-audit.json"
            or audit_ref.get("package_lock_path") != "examples/react-app/package-lock.json"
            or not isinstance(audit_ref.get("package_lock_sha256"), str)
            or audit_ref.get("package_lock_sha256") != lock_digest
            or not isinstance(audit, dict)
            or audit_lock_digest != lock_digest):
        errors.append("React license supplement source lock/audit reference or SHA-256 does not match")

    notices = manifest.get("notices")
    if not isinstance(notices, list) or len(notices) != len(EXPECTED_NOTICE_PACKAGES):
        errors.append("React license supplement must contain exactly three upstream notices")
        notices = []
    notice_names = [row.get("package") for row in notices if isinstance(row, dict)]
    if set(notice_names) != EXPECTED_NOTICE_PACKAGES or len(notice_names) != len(notices):
        errors.append("React license supplement package set must be the three pinned upstream notices")

    for row in notices:
        if not isinstance(row, dict):
            continue
        name = row.get("package")
        package_audit = audit_by_name.get(name)
        lock_entry = lock_rows.get(f"node_modules/{name}")
        if not isinstance(package_audit, dict) or not isinstance(lock_entry, dict):
            errors.append(f"React license supplement {name}: package is absent from audit or lock")
            continue
        if (row.get("version") != package_audit.get("version")
                or row.get("version") != lock_entry.get("version")
                or row.get("npm_integrity") != package_audit.get("integrity")
                or row.get("npm_integrity") != lock_entry.get("integrity")
                or package_audit.get("license_ids") != ["MIT"]
                or package_audit.get("license_files") != []
                or row.get("license_id") != "MIT"
                or row.get("package_tarball_notice_present") is not False):
            errors.append(f"React license supplement {name}: package, MIT declaration, or tarball-gap evidence does not match")
        commit = row.get("source_commit")
        tag = row.get("source_tag")
        repository = row.get("source_repository")
        source_path = row.get("source_path")
        source_url = row.get("source_url")
        relative = row.get("file")
        digest = row.get("sha256")
        expected_source = EXPECTED_SOURCE_PINS.get(name)
        if (not isinstance(commit, str) or not COMMIT_RE.fullmatch(commit)
                or row.get("copy_transform") != COPY_TRANSFORM
                or tag != f"v{row.get('version')}"
                or expected_source is None
                or (repository, tag, commit, source_path) != expected_source
                or not isinstance(repository, str) or not repository.startswith("https://github.com/")
                or not isinstance(source_path, str) or not source_path or "/" in source_path
                or source_url != f"{repository}/blob/{commit}/{source_path}"
                or not isinstance(relative, str) or not relative or "\\" in relative
                or Path(relative).is_absolute() or ".." in Path(relative).parts
                or not isinstance(digest, str) or not SHA256_RE.fullmatch(digest)):
            errors.append(f"React license supplement {name}: unsafe path or incomplete source/version pin")
            continue
        if urlparse(repository).netloc != "github.com":
            errors.append(f"React license supplement {name}: upstream repository must be public GitHub")
        artifact = root / relative
        current = root
        symlinked = False
        for part in Path(relative).parts:
            current = current / part
            if current.is_symlink():
                symlinked = True
                break
        try:
            raw = artifact.read_bytes() if artifact.is_file() and not symlinked else None
            normalized = raw.replace(bytes((13, 10)), bytes((10,))) if raw is not None else None
            actual = (hashlib.sha256(normalized).hexdigest()
                      if normalized is not None and bytes((13,)) not in normalized else None)
        except OSError:
            actual = None
        if actual != digest:
            errors.append(f"React license supplement {name}: copied notice missing or SHA-256 mismatch")

    unresolved = manifest.get("unresolved")
    if not isinstance(unresolved, list) or len(unresolved) != len(EXPECTED_UNRESOLVED_PACKAGES):
        errors.append("React license supplement must identify the unresolved stackback package")
        unresolved = []
    unresolved_names = [row.get("package") for row in unresolved if isinstance(row, dict)]
    if set(unresolved_names) != EXPECTED_UNRESOLVED_PACKAGES or len(unresolved_names) != len(unresolved):
        errors.append("React license supplement unresolved set must contain only stackback")
    for row in unresolved:
        if not isinstance(row, dict):
            continue
        name = row.get("package")
        package_audit = audit_by_name.get(name)
        lock_entry = lock_rows.get(f"node_modules/{name}")
        embedded_notice = row.get("embedded_notice")
        if (name != "stackback" or row.get("status") != "NOTICE_TEXT_UNRESOLVED"
                or row.get("repository_archived") is not True
                or row.get("declared_license") != "MIT"
                or row.get("license_declaration_verified") is not True
                or row.get("source_commit") != EXPECTED_STACKBACK_SOURCE_COMMIT
                or row.get("source_file_blobs") != EXPECTED_STACKBACK_SOURCE_BLOBS
                or row.get("local_installed_source_matches_pinned_blobs") is not True
                or row.get("root_license_file") != "NOT_FOUND_AT_PINNED_REVISION"
                or not isinstance(embedded_notice, dict)
                or embedded_notice.get("path") != "formatstack.js"
                or embedded_notice.get("license") != "BSD-3-Clause"
                or embedded_notice.get("status") != "FULL_NOTICE_PRESENT_IN_SOURCE_FILE"
                or row.get("file") is not None or row.get("sha256") is not None
                or not row.get("evidence_note") or not row.get("required_action")
                or not isinstance(package_audit, dict) or not isinstance(lock_entry, dict)
                or row.get("version") != package_audit.get("version")
                or row.get("version") != lock_entry.get("version")
                or row.get("npm_integrity") != package_audit.get("integrity")
                or row.get("npm_integrity") != lock_entry.get("integrity")
                or package_audit.get("license_ids") != ["MIT"]
                or package_audit.get("license_files") != []):
            errors.append("React license supplement stackback evidence must remain unresolved and match the audited locked package")

    missing = {
        row.get("name") for row in audit_by_name.values()
        if row.get("installed_in_audit_environment") is True and row.get("license_files") == []
    }
    counts = manifest.get("counts")
    audit_counts = audit.get("counts") if isinstance(audit, dict) else None
    missing_count = audit_counts.get("license_files_missing") if isinstance(audit_counts, dict) else None
    if (missing != EXPECTED_MISSING_TARBALL_NOTICES
            or not isinstance(counts, dict)
            or counts.get("supplemented_upstream_notices") != 3
            or counts.get("unresolved_packages") != 1
            or counts.get("npm_tarballs_missing_license_files") != 4
            or missing_count != 4):
        errors.append("React license supplement counts must preserve three supplements, one unresolved package, and four missing tarball files")
    return errors
