#!/usr/bin/env python3
"""Offline SHA256 verification for the complete source tree."""
import hashlib
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from update_checksums import source_files


def main():
    manifest = ROOT / 'SHA256SUMS.txt'
    if not manifest.is_file():
        print('SHA256SUMS.txt not found'); return 2
    missing = []
    bad = []
    unexpected = []
    checked = 0
    listed = set()
    for line in manifest.read_text(encoding='utf-8').splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        expected, name = line.split('  ', 1)
        listed.add(name)
        path = ROOT / name
        if not path.is_file():
            missing.append(name); continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        checked += 1
        if actual != expected:
            bad.append(name)
    actual = {path.relative_to(ROOT).as_posix() for path in source_files()}
    unexpected = sorted(actual - listed)
    print(f'Checked={checked}; missing={len(missing)}; altered={len(bad)}; unlisted={len(unexpected)}')
    for name in missing: print('MISSING:', name)
    for name in bad: print('ALTERED:', name)
    for name in unexpected: print('UNLISTED:', name)
    return 2 if missing or bad or unexpected else 0

if __name__ == '__main__':
    raise SystemExit(main())
