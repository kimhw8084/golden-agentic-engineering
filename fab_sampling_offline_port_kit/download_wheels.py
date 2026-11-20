#!/usr/bin/env python3
"""Network-connected staging machine only. Download, do not install packages."""
import argparse, hashlib, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser()
p.add_argument('--requirements',choices=['core','extended','heavy'],default='core')
a=p.parse_args()
req=ROOT/f'requirements_{a.requirements}.txt'
out=ROOT/'wheelhouse'/a.requirements
out.mkdir(parents=True,exist_ok=True)
cmd=[sys.executable,'-m','pip','download','--only-binary=:all:','--dest',str(out),'-r',str(req)]
print('RUNNING:', ' '.join(cmd),flush=True)
result=subprocess.run(cmd)
with (ROOT/'wheelhouse'/f'{a.requirements}_SHA256SUMS.txt').open('w',encoding='utf-8') as f:
 for wheel in sorted(out.iterdir()):
  if wheel.is_file():
   h=hashlib.sha256()
   with wheel.open('rb') as fd:
    for part in iter(lambda:fd.read(1024*1024),b''):h.update(part)
   f.write(f'{h.hexdigest()}  {wheel.name}\n')
if result.returncode:
 print('INCOMPLETE wheelhouse; inspect failures and target platform. DO NOT claim offline install readiness.',file=sys.stderr)
 raise SystemExit(result.returncode)
print('Downloaded candidate wheels; still verify ABI, transitive licenses, vulnerabilities, offline install, and resolved versions.')
