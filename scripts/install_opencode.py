#!/usr/bin/env python3
"""Opt-in, collision-safe OpenCode agent/skill/command installer (no config edits)."""
from __future__ import annotations
import argparse
import hashlib
import shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description='Preview/copy Golden assets to an explicit OpenCode config folder.')
    ap.add_argument('--target', type=Path, required=True, help='Existing OpenCode config directory (version-verified by engineer)')
    ap.add_argument('--apply', action='store_true', help='Create missing Golden assets; never overwrite changed files')
    args = ap.parse_args()
    target = args.target.expanduser().resolve()
    if not target.is_dir():
        ap.error('--target must already be an existing directory; no implicit config location assumptions')
    source = ROOT / '.opencode'
    conflicts=0; added=0; same=0
    for group in ('agents', 'skills', 'commands'):
        for src in sorted((source / group).rglob('*')):
            if not src.is_file():
                continue
            dst = target / group / src.relative_to(source / group)
            if dst.exists():
                if sha(src) == sha(dst):
                    print('UNCHANGED:', dst); same+=1
                else:
                    print('CONFLICT:', dst, '— manual version reconciliation required'); conflicts+=1
            elif args.apply:
                dst.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(src,dst); print('INSTALLED:', dst); added+=1
            else:
                print('WOULD INSTALL:', dst)
    print(f'Added={added}; same={same}; conflicts={conflicts}. OpenCode provider/model config and MCP remain untouched.')
    return 2 if conflicts else 0

if __name__ == '__main__':
    raise SystemExit(main())
