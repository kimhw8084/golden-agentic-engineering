#!/usr/bin/env python3
"""Opt-in PUBLIC INTERNET staging of GitHub source snapshots; never run on company intranet.

Archives source only. Does NOT create offline executables or complete license/SBOM approvals.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAFE_REPO = re.compile(r'^https://github\.com/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+\.git$')


def hash_file(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def run(*args, cwd=None):
    proc = subprocess.run(list(args), cwd=cwd, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, text=True, timeout=900, check=False)
    if proc.returncode:
        raise RuntimeError(f'Command {args[0]!r} failed: {proc.stderr[-900:]}')
    return proc.stdout.strip()


def stage(item, out):
    url = item['repo']
    if not re.fullmatch(r'[a-z0-9_-]+', item['id']):
        raise ValueError('Invalid catalog id for filesystem-safe archive naming')
    if not SAFE_REPO.fullmatch(url):
        raise ValueError('Only explicitly catalogued github.com Git HTTPS URLs supported')
    with tempfile.TemporaryDirectory(prefix='golden-github-') as temp:
        cloned = Path(temp) / 'source'
        run('git', 'clone', '--quiet', '--depth', '1', url, str(cloned))
        sha = run('git', 'rev-parse', 'HEAD', cwd=cloned)
        files = run('git', 'ls-files', cwd=cloned).splitlines()
        license_candidates = sorted(p for p in files if p.split('/')[-1].lower().startswith(('license', 'licence', 'copying', 'notice')))
        output = out / f"{item['id']}-{sha[:12]}.zip"
        if output.exists():
            raise FileExistsError(f'Existing archive is never overwritten: {output}')
        run('git', 'archive', '--format=zip', f'--output={output}', 'HEAD', cwd=cloned)
        return {
            'id': item['id'], 'repository': url, 'resolved_commit': sha,
            'source_zip': output.name, 'sha256': hash_file(output),
            'bytes': output.stat().st_size, 'license_file_paths_observed': license_candidates,
            'license_spdx_verified': False, 'dependency_licenses_verified': False,
            'runtime_offline_verified': False, 'windows_verified': False, 'linux_verified': False,
            'approval_status': 'SOURCE_ARCHIVED_ONLY'
        }


def verify(lock_path, archive_dir):
    lock = json.loads(lock_path.read_text(encoding='utf-8'))
    fail = False
    for rec in lock['results']:
        if rec.get('approval_status') != 'SOURCE_ARCHIVED_ONLY':
            print(f"SKIP  {rec.get('id')}: no valid archive"); fail = True; continue
        path = archive_dir / rec['source_zip']
        ok = path.is_file() and hash_file(path) == rec['sha256']
        print(('PASS  ' if ok else 'FAIL  ') + rec['id'])
        fail = fail or not ok
    return 2 if fail else 0


def main():
    ap = argparse.ArgumentParser(description='Public-network source archive staging, not executable packaging.')
    ap.add_argument('--tier', choices=['pilot','extended','research','all'], default='pilot')
    ap.add_argument('--limit', type=int, default=0, help='Max candidates; 0 means all selected')
    ap.add_argument('--out', type=Path, default=Path('out/source-staging'))
    ap.add_argument('--apply', action='store_true', help='Explicitly permit public GitHub downloads')
    ap.add_argument('--verify', action='store_true', help='Offline verify prior lock instead of fetching')
    args = ap.parse_args()
    args.out = args.out.resolve()
    if args.verify:
        lock = args.out / 'sources.lock.json'
        if not lock.is_file():
            print('Missing lock:', lock); return 2
        return verify(lock, args.out)
    catalog = json.loads((ROOT / 'tools' / 'candidates.json').read_text(encoding='utf-8'))
    tiers = {'pilot': {'pilot'}, 'extended': {'pilot','extended'}, 'research': {'research'}, 'all': {'pilot','extended','research'}}[args.tier]
    selected = [v for v in catalog['candidates'] if v['tier'] in tiers]
    if args.limit < 0:
        ap.error('--limit must be nonnegative')
    if args.limit:
        selected = selected[:args.limit]
    print('PUBLIC INTERNET staging only; this DOES NOT stage binaries/deps or approve licenses.')
    print('Selected', len(selected), 'candidate source repositories:')
    for item in selected:
        print('  ',item['id'],item['repo'])
    if not args.apply:
        print('DRY RUN: add --apply on the internet-connected staging PC to clone source.')
        return 0
    if not shutil.which('git'):
        print('Git not found'); return 2
    args.out.mkdir(parents=True, exist_ok=True)
    if (args.out / 'sources.lock.json').exists():
        print('Lock already exists. Use new output directory; do not overwrite pinned staged sources.'); return 2
    results, problems = [], 0
    for item in selected:
        print('Fetching:', item['id'], flush=True)
        try:
            rec = stage(item, args.out)
            results.append(rec)
            print('  pinned', rec['resolved_commit'][:12])
        except Exception as exc:
            problems += 1
            print('  FAILED:', exc)
            results.append({'id': item['id'], 'approval_status': 'FAILED', 'error': str(exc)[:500]})
    lock = {'schema':'golden-source-lock/v0.1', 'source_only':True,
            'warning':'Cloned source archives do not include dependent binaries, complete npm/pip caches, browser downloads, vulnerability DBs, all licenses or company clearance.',
            'results':results}
    (args.out / 'sources.lock.json').write_text(json.dumps(lock, indent=2)+'\n', encoding='utf-8')
    print(f'Lock: {args.out / "sources.lock.json"}; failures: {problems}')
    return 2 if problems else 0


if __name__ == '__main__':
    raise SystemExit(main())
