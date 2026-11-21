#!/usr/bin/env python3
"""Verify explicitly staged source clones without executing repository code."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent


def _safe_source_path(root: Path, raw_path: object) -> Path | None:
    if not isinstance(raw_path, str) or not raw_path or '\\' in raw_path or ':' in raw_path or '\x00' in raw_path:
        return None
    relative = PurePosixPath(raw_path)
    if relative.is_absolute() or not relative.parts or any(part in {'', '.', '..'} for part in relative.parts):
        return None
    root_real = root.resolve(strict=True)
    path = root_real.joinpath(*relative.parts)
    cursor = root_real
    for part in relative.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            return None
    try:
        path.resolve(strict=True).relative_to(root_real)
    except (OSError, ValueError):
        return None
    return path


def verify(root: Path = ROOT, allow_incomplete: bool = False) -> tuple[list[str], list[str]]:
    """Return verified repository IDs and safe, value-free failure messages."""
    failures: list[str] = []
    try:
        manifest_data = json.loads((root / 'repos.json').read_text(encoding='utf-8'))
        lock_data = json.loads((root / 'repos.lock.json').read_text(encoding='utf-8'))
    except (OSError, UnicodeError, ValueError):
        return [], ['MISSING_OR_INVALID_MANIFEST_OR_LOCK']

    manifest = manifest_data.get('repositories') if isinstance(manifest_data, dict) else None
    entries = lock_data.get('entries') if isinstance(lock_data, dict) else None
    if not isinstance(manifest, list) or not manifest:
        return [], ['INVALID repos.json: repositories must be a nonempty list']
    if not isinstance(entries, list):
        return [], ['INVALID repos.lock.json: entries must be a list']
    if not all(isinstance(item, dict) and isinstance(item.get('repo'), str)
               and isinstance(item.get('url'), str) for item in manifest):
        return [], ['INVALID repos.json: every candidate needs repo and URL strings']

    manifest_by_name = {item['repo']: item for item in manifest}
    if len(manifest_by_name) != len(manifest):
        return [], ['INVALID repos.json: duplicate repository IDs']
    entry_names = [item.get('repo') if isinstance(item, dict) else None for item in entries]
    if any(not isinstance(name, str) for name in entry_names):
        return [], ['INVALID repos.lock.json: every entry needs a repository ID']
    if len(set(entry_names)) != len(entry_names):
        return [], ['INVALID repos.lock.json: duplicate repository IDs']
    unknown = sorted(set(entry_names) - set(manifest_by_name))
    if unknown:
        return [], ['INVALID repos.lock.json: contains repository IDs absent from repos.json']
    if not entries:
        return [], ['EMPTY repos.lock.json: stage at least one explicit repository before verification']

    omitted = set(manifest_by_name) - set(entry_names)
    if omitted and not allow_incomplete:
        failures.append(
            f'PARTIAL_LOCK: {len(omitted)} manifest candidates are omitted; '
            'use --allow-incomplete only for a deliberately selected subset.'
        )

    root_real = root.resolve(strict=True)
    verified: list[str] = []
    for rec in entries:
        name = rec['repo']
        candidate = manifest_by_name[name]
        if rec.get('status') != 'CLONED_PENDING_AUDIT':
            failures.append(name + ': no complete clone')
            continue
        if rec.get('url') != candidate['url']:
            failures.append(name + ': lock URL does not match manifest')
            continue
        raw_path = rec.get('path')
        relative = PurePosixPath(raw_path) if isinstance(raw_path, str) else PurePosixPath('/')
        if (not isinstance(raw_path, str) or not raw_path or '\\' in raw_path or ':' in raw_path
                or '\x00' in raw_path or relative.is_absolute() or not relative.parts
                or any(part in {'', '.', '..'} for part in relative.parts)):
            failures.append(name + ': invalid or unsafe lock path')
            continue
        path = _safe_source_path(root_real, raw_path)
        if path is None:
            failures.append(name + ': source path missing, symlinked, or escaping')
            continue
        git_dir = path / '.git'
        if not path.is_dir() or not git_dir.is_dir() or git_dir.is_symlink():
            failures.append(name + ': missing Git source')
            continue

        expected_sha = rec.get('sha')
        if not isinstance(expected_sha, str) or not re.fullmatch(r'[0-9a-fA-F]{40,64}', expected_sha):
            failures.append(name + ': invalid pinned SHA in lock')
            continue
        try:
            result = subprocess.run(['git', '-C', str(path), 'rev-parse', 'HEAD'],
                                    capture_output=True, text=True, timeout=10, check=False)
            origin = subprocess.run(['git', '-C', str(path), 'remote', 'get-url', 'origin'],
                                    capture_output=True, text=True, timeout=10, check=False)
        except (OSError, subprocess.SubprocessError):
            failures.append(name + ': Git verification command failed')
            continue
        expected_url = candidate['url'].rstrip('/').removesuffix('.git').lower()
        actual_url = origin.stdout.strip().rstrip('/').removesuffix('.git').lower()
        if result.returncode or result.stdout.strip() != expected_sha:
            failures.append(name + ': SHA mismatch')
            continue
        if origin.returncode or actual_url != expected_url:
            failures.append(name + ': origin URL mismatch')
            continue

        license_files = rec.get('license_files')
        if not isinstance(license_files, list) or not license_files:
            failures.append(name + ': no root license file; manual review required')
            continue
        safe_license_files = True
        for license_name in license_files:
            if (not isinstance(license_name, str) or PurePosixPath(license_name).name != license_name
                    or not license_name.lower().startswith(('license', 'licence', 'copying'))):
                safe_license_files = False
                break
            license_path = path / license_name
            if license_path.is_symlink() or not license_path.is_file():
                safe_license_files = False
                break
        if not safe_license_files:
            failures.append(name + ': recorded root license file is missing or unsafe')
            continue
        verified.append(name)

    return verified, failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--allow-incomplete', action='store_true',
                        help='Verify only repositories listed in the lock; does not imply license/security approval.')
    args = parser.parse_args()
    verified, failures = verify(allow_incomplete=args.allow_incomplete)
    if failures:
        print('BLOCKERS:')
        for failure in failures:
            print(' - ' + failure)
        return 2
    try:
        total = len(json.loads((ROOT / 'repos.json').read_text(encoding='utf-8'))['repositories'])
    except (OSError, ValueError, KeyError, TypeError):
        print('MISSING_OR_INVALID repos.json')
        return 2
    partial = len(verified) < total
    if partial and not args.allow_incomplete:
        print('BLOCKED: partial transfer requires --allow-incomplete')
        return 2
    for name in verified:
        print(f'verified source {name} [commit and origin match; license/security review still required]')
    if partial:
        print(f'Verified {len(verified)}/{total} manifest candidates in the explicitly locked subset.')
    else:
        print(f'All {len(verified)} manifest candidate commits and origins match the lock.')
    print('This is NOT security, license, data-rights, or company-transfer approval.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
