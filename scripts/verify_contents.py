#!/usr/bin/env python3
"""Offline SHA256 verification for the original starter ZIP contents."""
import hashlib
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent


def main():
    manifest = ROOT / 'SHA256SUMS.txt'
    if not manifest.is_file():
        print('SHA256SUMS.txt not found'); return 2
    missing = []
    bad = []
    checked = 0
    for line in manifest.read_text(encoding='utf-8').splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        expected, name = line.split('  ', 1)
        path = ROOT / name
        if not path.is_file():
            missing.append(name); continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        checked += 1
        if actual != expected:
            bad.append(name)
    print(f'Checked={checked}; missing={len(missing)}; altered={len(bad)}')
    for name in missing: print('MISSING:', name)
    for name in bad: print('ALTERED:', name)
    return 2 if missing or bad else 0

if __name__ == '__main__':
    raise SystemExit(main())
