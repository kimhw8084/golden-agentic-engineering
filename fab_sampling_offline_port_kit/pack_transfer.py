#!/usr/bin/env python3
"""Archive this kit (including cloned sources and wheelhouse if downloaded)."""
import argparse, hashlib, subprocess, sys, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser()
p.add_argument('--allow-incomplete',action='store_true',help='Allow a partial clone bundle for early evaluation')
a=p.parse_args()
if not a.allow_incomplete:
 check=subprocess.run([sys.executable,str(ROOT/'verify_bundle.py')])
 if check.returncode:sys.exit('Cannot pack all-repos bundle: verification failed. Run --allow-incomplete for an explicitly incomplete transfer.')
target=ROOT.parent/'fab_sampling_source_transfer.zip'
if target.exists():target.unlink()
ignored={'.venv','__pycache__','.pytest_cache','.mypy_cache','node_modules','.ruff_cache'}
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=5,allowZip64=True) as z:
 for path in ROOT.rglob('*'):
  if not path.is_file() or any(part in ignored for part in path.relative_to(ROOT).parts):continue
  z.write(path,arcname=ROOT.name+'/'+str(path.relative_to(ROOT)))
h=hashlib.sha256()
with target.open('rb') as fd:
 for part in iter(lambda:fd.read(4*1024*1024),b''):h.update(part)
(target.with_suffix('.zip.sha256')).write_text(h.hexdigest()+'  '+target.name+'\n',encoding='utf-8')
print(f'Archived: {target} ({target.stat().st_size/1024/1024:.1f} MiB)')
print(f'SHA256: {h.hexdigest()}')
