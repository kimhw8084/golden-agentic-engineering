#!/usr/bin/env python3
"""Offline verification of pinned source clones; does not execute repo code."""
from pathlib import Path, PurePosixPath
import json, re, subprocess, sys

ROOT = Path(__file__).resolve().parent


def verify(root: Path = ROOT) -> tuple[list[str], list[str]]:
    manifest = json.loads((root / 'repos.json').read_text(encoding='utf-8'))['repositories']
    lock_file = root / 'repos.lock.json'
    if not lock_file.is_file():
        return [], ['MISSING repos.lock.json: run fetch_repos.py on internet staging PC first']
    lock_data = json.loads(lock_file.read_text(encoding='utf-8'))
    entries = lock_data.get('entries') if isinstance(lock_data, dict) else None
    if not isinstance(entries, list):
        return [], ['INVALID repos.lock.json: entries must be a list']
    lock = {x.get('repo'): x for x in entries if isinstance(x, dict) and isinstance(x.get('repo'), str)}
    failures = []
    verified = []
    for repo in manifest:
        name = repo['repo']
        rec = lock.get(name)
        if not rec or rec.get('status') != 'CLONED_PENDING_AUDIT':
            failures.append(name + ': no complete clone')
            continue
        raw_path = rec.get('path')
        relative = PurePosixPath(raw_path) if isinstance(raw_path, str) else PurePosixPath('/')
        if (not relative.parts or relative.is_absolute() or '..' in relative.parts
                or '\\' in raw_path or ':' in raw_path or '\x00' in raw_path):
            failures.append(name + ': invalid or unsafe lock path')
            continue
        root_real = root.resolve(strict=True)
        path = root_real.joinpath(*relative.parts)
        cursor = root_real
        has_symlink = False
        for part in relative.parts:
            cursor = cursor / part
            if cursor.is_symlink():
                has_symlink = True
                break
        if has_symlink:
            failures.append(name + ': symlink in source path')
            continue
        try:
            path.resolve(strict=True).relative_to(root_real)
        except (OSError, ValueError):
            failures.append(name + ': source path escapes kit or is missing')
            continue
        if not path.is_dir() or not (path / '.git').is_dir() or (path / '.git').is_symlink():
            failures.append(name + ': missing Git source')
            continue
        expected_sha = rec.get('sha')
        if not isinstance(expected_sha, str) or not re.fullmatch(r'[0-9a-fA-F]{40,64}', expected_sha):
            failures.append(name + ': invalid pinned SHA in lock')
            continue
        result = subprocess.run(['git', '-C', str(path), 'rev-parse', 'HEAD'], capture_output=True, text=True)
        origin = subprocess.run(['git', '-C', str(path), 'remote', 'get-url', 'origin'], capture_output=True, text=True)
        expected_url = repo['url'].rstrip('/').removesuffix('.git').lower()
        actual_url = origin.stdout.strip().rstrip('/').removesuffix('.git').lower()
        if result.returncode or result.stdout.strip() != expected_sha:
            failures.append(name + ': SHA mismatch')
            continue
        if origin.returncode or actual_url != expected_url:
            failures.append(name + ': origin URL mismatch')
            continue
        if not rec.get('license_files'):
            failures.append(name + ': no root license file; manual review required')
            continue
        verified.append(name)
        print(f"verified source {name} @ {expected_sha[:12]} [license review still required]")
    return verified, failures


def main() -> int:
    verified, failures = verify()
    if not (ROOT / 'repos.lock.json').is_file():
        print(failures[0])
        return 2
    print('Audits still required: source license contents, third-party/bundled datasets, dependencies, CVE scan, submodules, git LFS, telemetry, installers.')
    if failures:
        print('\nBLOCKERS:')
        for failure in failures:
            print(' - ' + failure)
        return 2
    print(f'All {len(verified)} local Git commit IDs and origins match the lock. This is NOT security/license approval.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
