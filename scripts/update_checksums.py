#!/usr/bin/env python3
"""Regenerate source SHA256SUMS; excludes only itself, the manifest, and runtime output."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'dist', 'build', '.next', 'coverage', 'out'}
EXCLUDED = {'SHA256SUMS.txt', 'scripts/update_checksums.py'}


def source_files() -> list[Path]:
    paths = []
    for path in ROOT.rglob('*'):
        relative = path.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        if path.is_file() and not path.is_symlink() and relative.as_posix() not in EXCLUDED:
            paths.append(path)
    return sorted(paths, key=lambda p: p.relative_to(ROOT).as_posix())


def write_manifest() -> int:
    rows = ['# SHA256 for all source files; excludes this manifest, this writer, Git metadata and ignored runtime output.']
    for path in source_files():
        rel = path.relative_to(ROOT).as_posix()
        rows.append(f'{hashlib.sha256(path.read_bytes()).hexdigest()}  {rel}')
    (ROOT / 'SHA256SUMS.txt').write_text('\n'.join(rows) + '\n', encoding='utf-8')
    return len(rows) - 1


if __name__ == '__main__':
    print(f'Updated SHA256SUMS.txt entries={write_manifest()}')
