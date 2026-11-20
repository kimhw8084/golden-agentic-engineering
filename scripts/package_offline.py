#!/usr/bin/env python3
"""Create and verify a source-only Golden transfer archive using Python stdlib."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
import subprocess
import sys
import tarfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
PREFIX = 'golden-agentic-engineering'
MANIFEST = f'{PREFIX}/golden-offline-manifest.json'
SECRET_PATTERNS = (
    re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    re.compile(r'\bgh[pousr]_[A-Za-z0-9]{30,}\b'),
    re.compile(r'\bAKIA[0-9A-Z]{16}\b'),
)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def git(root: Path, *args: str) -> str:
    result = subprocess.run(['git', '-C', str(root), *args], check=True, capture_output=True)
    return result.stdout.decode('utf-8', errors='strict')


def tracked_files(root: Path) -> list[Path]:
    raw = subprocess.run(['git', '-C', str(root), 'ls-files', '-z'], check=True, capture_output=True).stdout
    paths = [Path(os.fsdecode(item)) for item in raw.split(b'\0') if item]
    for path in paths:
        if path.is_absolute() or '..' in path.parts or '.git' in path.parts:
            raise ValueError(f'Unsafe tracked path: {path}')
        source = root / path
        if source.is_symlink() or not source.is_file():
            raise ValueError(f'Only regular tracked files can be packaged: {path}')
    return sorted(paths, key=lambda p: p.as_posix())


def check_clean(root: Path) -> None:
    if git(root, 'status', '--porcelain').strip():
        raise ValueError('Refusing to package a dirty or untracked worktree; commit or discard changes first.')


def check_sensitive(path: Path, data: bytes) -> None:
    text = data.decode('utf-8', errors='ignore')
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            raise ValueError(f'Possible secret material detected in {path.as_posix()}.')


def build_manifest(root: Path) -> dict:
    files = []
    for path in tracked_files(root):
        data = (root / path).read_bytes()
        check_sensitive(path, data)
        files.append({'path': path.as_posix(), 'size': len(data), 'sha256': sha_bytes(data)})
    assets_path = root / 'offline' / 'assets-manifest.json'
    missing_asset_rows = json.loads(assets_path.read_text(encoding='utf-8'))['assets'] if assets_path.is_file() else []
    return {
        'schema': 'golden-offline-bundle/v1',
        'source_commit': git(root, 'rev-parse', 'HEAD').strip(),
        'archive_prefix': PREFIX + '/',
        'contents_kind': 'source-only-no-dependencies',
        'required_network_at_runtime': False,
        'license_files': ['LICENSE'],
        'files': files,
        'missing_assets': missing_asset_rows,
        'qualification': 'TRANSFER_SOURCE_ONLY_NOT_OFFLINE_EXECUTABLE_OR_COMPANY_APPROVED',
    }


def create_bundle(root: Path, archive: Path) -> dict:
    root = root.resolve()
    check_clean(root)
    manifest = build_manifest(root)
    archive = archive.resolve()
    archive.parent.mkdir(parents=True, exist_ok=True)
    with archive.open('wb') as raw:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw, compresslevel=9, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode='w', format=tarfile.PAX_FORMAT) as tar:
                for entry in manifest['files']:
                    source = root / PurePosixPath(entry['path'])
                    info = tar.gettarinfo(str(source), arcname=f"{PREFIX}/{entry['path']}")
                    info.uid = info.gid = 0
                    info.uname = info.gname = ''
                    info.mtime = 0
                    info.mode = 0o644
                    with source.open('rb') as stream:
                        tar.addfile(info, stream)
                payload = json.dumps(manifest, indent=2, sort_keys=True).encode() + b'\n'
                import io
                info = tarfile.TarInfo(MANIFEST)
                info.size = len(payload)
                info.mode = 0o644
                info.uid = info.gid = info.mtime = 0
                tar.addfile(info, io.BytesIO(payload))
    digest = sha_file(archive)
    archive.with_suffix(archive.suffix + '.sha256').write_text(f'{digest}  {archive.name}\n', encoding='ascii')
    return manifest


def verify_bundle(archive_path: Path, sha256_file: Path | None = None) -> dict:
    archive_path = archive_path.resolve()
    checksum_path = sha256_file or archive_path.with_suffix(archive_path.suffix + '.sha256')
    expected = checksum_path.read_text(encoding='ascii').split()[0].lower()
    actual = sha_file(archive_path)
    if not re.fullmatch(r'[0-9a-f]{64}', expected) or expected != actual:
        raise ValueError('Archive checksum is missing or does not match.')
    with tarfile.open(archive_path, 'r:gz') as tar:
        members = tar.getmembers()
        if any(not (m.isfile() or m.isdir()) for m in members):
            raise ValueError('Archive contains a link or unsupported member type.')
        names = [PurePosixPath(m.name) for m in members]
        if any(p.is_absolute() or '..' in p.parts or not p.parts or p.parts[0] != PREFIX for p in names):
            raise ValueError('Archive contains an unsafe or out-of-prefix path.')
        if names.count(PurePosixPath(MANIFEST)) != 1:
            raise ValueError('Archive must contain exactly one bundle manifest.')
        stream = tar.extractfile(MANIFEST)
        if stream is None:
            raise ValueError('Bundle manifest cannot be read.')
        manifest = json.load(stream)
        if manifest.get('schema') != 'golden-offline-bundle/v1' or manifest.get('archive_prefix') != PREFIX + '/':
            raise ValueError('Unsupported bundle manifest.')
        declared = {f"{PREFIX}/{item['path']}": item for item in manifest.get('files', [])}
        actual_names = {p.as_posix() for p, m in zip(names, members) if m.isfile() and p.as_posix() != MANIFEST}
        if actual_names != set(declared):
            raise ValueError('Archive file inventory does not match its manifest.')
        for member in members:
            name = PurePosixPath(member.name).as_posix()
            if name == MANIFEST or not member.isfile():
                continue
            item = declared[name]
            stream = tar.extractfile(member)
            data = stream.read() if stream else b''
            if len(data) != item['size'] or sha_bytes(data) != item['sha256']:
                raise ValueError(f'Content digest mismatch: {name}')
            check_sensitive(PurePosixPath(item['path']), data)
        return manifest


def verify_extracted_tree(root: Path, manifest: dict) -> None:
    root = root.resolve()
    for item in manifest.get('files', []):
        rel = PurePosixPath(item['path'])
        if rel.is_absolute() or '..' in rel.parts:
            raise ValueError('Unsafe manifest path.')
        path = root.joinpath(*rel.parts)
        if path.is_symlink() or not path.is_file():
            raise ValueError(f'Missing or unsafe extracted file: {rel}')
        data = path.read_bytes()
        if len(data) != item['size'] or sha_bytes(data) != item['sha256']:
            raise ValueError(f'Extracted file digest mismatch: {rel}')


def main() -> int:
    parser = argparse.ArgumentParser(description='Offline source bundle packager/verifier. Uses no network.')
    sub = parser.add_subparsers(dest='action', required=True)
    create = sub.add_parser('create')
    create.add_argument('--repo', type=Path, default=ROOT)
    create.add_argument('--out', type=Path, required=True)
    verify = sub.add_parser('verify')
    verify.add_argument('archive', type=Path)
    args = parser.parse_args()
    try:
        if args.action == 'create':
            manifest = create_bundle(args.repo, args.out)
            print(f"Created source-only bundle for {manifest['source_commit']}; missing_assets={len(manifest['missing_assets'])}")
        else:
            manifest = verify_bundle(args.archive)
            print(f"Verified source-only bundle {manifest['source_commit']}; missing_assets={len(manifest['missing_assets'])}")
        return 0
    except (OSError, ValueError, subprocess.SubprocessError, json.JSONDecodeError, tarfile.TarError) as exc:
        print(f'Bundle error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
