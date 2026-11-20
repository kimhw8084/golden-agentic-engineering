#!/usr/bin/env python3
"""Offline verification of pinned source clones; does not execute repo code."""
from pathlib import Path
import json, subprocess, sys
ROOT=Path(__file__).resolve().parent
manifest=json.loads((ROOT/'repos.json').read_text(encoding='utf-8'))['repositories']
lock_file=ROOT/'repos.lock.json'
if not lock_file.exists():sys.exit('MISSING repos.lock.json: run fetch_repos.py on internet staging PC first')
lock={x['repo']:x for x in json.loads(lock_file.read_text(encoding='utf-8'))['entries']}
failures=[]
for r in manifest:
 rec=lock.get(r['repo'])
 if not rec or rec['status']!='CLONED_PENDING_AUDIT':
  failures.append(r['repo']+': no complete clone');continue
 path=ROOT/'sources'/r['repo'].replace('/','__')
 if not path.is_dir() or not (path/'.git').exists():failures.append(r['repo']+': missing git source');continue
 result=subprocess.run(['git','-C',str(path),'rev-parse','HEAD'],capture_output=True,text=True)
 if result.returncode or result.stdout.strip()!=rec['sha']:failures.append(r['repo']+': SHA mismatch');continue
 if not rec.get('license_files'):failures.append(r['repo']+': no root license file; manual review required')
 print(f"verified source {r['repo']} @ {rec['sha'][:12]} [license review still required]")
print('Audits still required: source license contents, third-party/bundled datasets, dependencies, CVE scan, submodules, git LFS, telemetry, installers.')
if failures:
 print('\nBLOCKERS:');[print(' - '+v) for v in failures];sys.exit(2)
print('All 38 local Git commit IDs match the lock. This is NOT security/license approval.')
