#!/usr/bin/env python3
"""Archive this kit (including cloned sources and wheelhouse if downloaded)."""
import argparse, hashlib, os, subprocess, sys, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent


def pack(target: Path, allow_incomplete: bool = False) -> str:
 target=target.expanduser().absolute()
 try:
  target.relative_to(ROOT)
 except ValueError:
  pass
 else:
  raise ValueError('Archive output must be outside the kit directory.')
 checksum_path=Path(str(target)+'.sha256')
 if target.exists() or target.is_symlink() or checksum_path.exists() or checksum_path.is_symlink():
  raise FileExistsError('Archive or checksum already exists; move it explicitly before packing again.')
 if not allow_incomplete:
  check=subprocess.run([sys.executable,str(ROOT/'verify_bundle.py')])
  if check.returncode:
   raise ValueError('Cannot pack all-repos bundle: verification failed. Use --allow-incomplete only for an explicitly incomplete transfer.')
 target.parent.mkdir(parents=True,exist_ok=True)
 ignored={'.venv','__pycache__','.pytest_cache','.mypy_cache','node_modules','.ruff_cache'}
 files=[]
 for path in sorted(ROOT.rglob('*')):
  if path.is_symlink():
   raise ValueError(f'Refusing to package symlink: {path.relative_to(ROOT)}')
  if not path.is_file() or any(part in ignored for part in path.relative_to(ROOT).parts):continue
  files.append(path)
 archive_created=False
 checksum_created=False
 try:
  with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=5,allowZip64=True) as z:
   archive_created=True
   for path in files:
    z.write(path,arcname=ROOT.name+'/'+str(path.relative_to(ROOT)))
  h=hashlib.sha256()
  with target.open('rb') as fd:
   for part in iter(lambda:fd.read(4*1024*1024),b''):h.update(part)
  with checksum_path.open('x',encoding='utf-8') as fd:
   checksum_created=True
   fd.write(h.hexdigest()+'  '+target.name+'\n')
 except Exception:
  if archive_created and target.is_file() and not target.is_symlink():
   target.unlink()
  if checksum_created and checksum_path.is_file() and not checksum_path.is_symlink():
   checksum_path.unlink()
  raise
 print(f'Archived: {target} ({target.stat().st_size/1024/1024:.1f} MiB)')
 print(f'SHA256: {h.hexdigest()}')
 return h.hexdigest()


def main() -> int:
 p=argparse.ArgumentParser()
 p.add_argument('--allow-incomplete',action='store_true',help='Allow a partial clone bundle for early evaluation')
 p.add_argument('--output',default=str(ROOT.parent/'fab_sampling_source_transfer.zip'),help='Archive output path (must not already exist)')
 a=p.parse_args()
 try:
  pack(Path(a.output),a.allow_incomplete)
 except (OSError,ValueError) as exc:
  print(f'FAILED: {exc}',file=sys.stderr)
  return 2
 return 0


if __name__=='__main__':
 raise SystemExit(main())
