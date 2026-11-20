#!/usr/bin/env python3
"""Offline binary-wheel integrity checks against the staging machine's SHA-256 list."""
from pathlib import Path
import argparse, hashlib, sys
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser()
p.add_argument('--requirements',choices=['core','extended','heavy'],default='core')
a=p.parse_args()
hashes=ROOT/'wheelhouse'/f'{a.requirements}_SHA256SUMS.txt'
if not hashes.is_file():sys.exit(f'No wheelhouse checksum list: {hashes}')
errors=[]
for line in hashes.read_text(encoding='utf-8').splitlines():
    if not line.strip():continue
    expected,name=line.split('  ',1)
    path=ROOT/'wheelhouse'/a.requirements/name
    if not path.is_file():errors.append('MISSING: '+name);continue
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    if h.hexdigest()!=expected:errors.append('SHA256 mismatch: '+name)
    else:print('OK: '+name)
if errors:
    print('\n'.join(errors),file=sys.stderr)
    sys.exit(2)
print('Downloaded wheel bytes match staging hashes. Does NOT establish license/security/ABI suitability or complete installability.')
