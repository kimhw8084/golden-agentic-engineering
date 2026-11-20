#!/usr/bin/env python3
"""Offline, non-destructive company doctor/apply/rollback for Golden OpenCode assets."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
REQUIRED_ASSET_NAMES = frozenset({
    'Python wheelhouse and dependency locks',
    'React npm lock and offline store',
    'Playwright browser binaries',
    'MCP Python SDK and transitive dependencies',
    'Company OpenCode and internal model evidence',
    'OS-enforced no-public-egress policy and attempt monitor',
})
sys.path.insert(0, str(ROOT / 'scripts'))
import package_offline  # noqa: E402


def hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_real_directory(path: Path, boundary: Path | None = None) -> None:
    """Create a directory chain without following symlinks or escaping an optional root."""
    path = Path(os.path.abspath(path.expanduser()))
    if boundary is None:
        cursor = Path(path.anchor)
        for part in path.parts[1:]:
            cursor = cursor / part
            if cursor.is_symlink():
                raise ValueError('Directory path contains a symlink.')
            if cursor.exists():
                if not cursor.is_dir():
                    raise ValueError('Directory path contains a non-directory component.')
            else:
                cursor.mkdir()
                if cursor.is_symlink() or not cursor.is_dir():
                    raise ValueError('Directory creation did not produce a real directory.')
        return
    boundary = Path(os.path.abspath(boundary.expanduser()))
    if path != boundary and boundary not in path.parents:
        raise ValueError('Directory path escapes its allowed root.')
    ensure_real_directory(boundary)
    if boundary.is_symlink() or not boundary.is_dir():
        raise ValueError('Allowed root is not a real directory.')
    cursor = boundary
    relative = path.relative_to(boundary)
    for part in relative.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError('Directory path contains a symlink.')
        if cursor.exists():
            if not cursor.is_dir():
                raise ValueError('Directory path contains a non-directory component.')
        else:
            cursor.mkdir()


def version_from_local_metadata(program: str, executable: Path) -> tuple[str | None, str]:
    """Read version metadata without launching a binary or making network requests."""
    if program == 'node':
        for part in reversed(executable.parts):
            match = re.fullmatch(r'v?(\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.-]+)?)', part)
            if match:
                return match[1], 'managed-install-path'
    accepted_names = {
        'opencode': {'@opencode/cli', '@opencode-ai/cli', 'opencode'},
        'node': {'node', 'node-bin-setup', 'nodejs-bin'},
    }.get(program, set())
    for parent in list(executable.parents)[:8]:
        metadata = parent / 'package.json'
        try:
            if not metadata.is_file() or metadata.stat().st_size > 256_000:
                continue
            record = json.loads(metadata.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            continue
        version = record.get('version') if isinstance(record, dict) else None
        name = record.get('name') if isinstance(record, dict) else None
        if name in accepted_names and isinstance(version, str) and re.fullmatch(r'\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.-]+)?', version):
            return version, 'local-package-metadata'
    return None, 'UNKNOWN_NO_LOCAL_VERSION_METADATA'


def local_executable(program: str) -> dict:
    """Inspect a locally installed executable by path and bytes only; never invoke it."""
    location = shutil.which(program)
    if not location:
        return {'available': False, 'version': None, 'version_source': 'NOT_INSTALLED', 'sha256': None}
    try:
        executable = Path(location).resolve(strict=True)
        if not executable.is_file():
            return {'available': True, 'version': None, 'version_source': 'INVALID_EXECUTABLE_PATH', 'sha256': None}
        fingerprint = hash_file(executable)
        version, source = version_from_local_metadata(program, executable)
        return {'available': True, 'version': version, 'version_source': source, 'sha256': fingerprint}
    except OSError:
        return {'available': True, 'version': None, 'version_source': 'EXECUTABLE_UNREADABLE', 'sha256': None}


def config_path() -> Path:
    if os.name == 'nt':
        base = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
    else:
        base = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config'))
    return base / 'opencode' / 'opencode.json'


def inspect_config(path: Path) -> dict:
    if not path.exists():
        return {'state': 'MISSING', 'provider_count': 0, 'model_key_present': False, 'mcp_server_count': 0}
    if path.is_symlink() or not path.is_file():
        return {'state': 'UNSAFE_PATH', 'provider_count': 0, 'model_key_present': False, 'mcp_server_count': 0}
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {'state': 'UNREADABLE_OR_INVALID', 'provider_count': 0, 'model_key_present': False, 'mcp_server_count': 0}
    if not isinstance(data, dict):
        return {'state': 'INVALID_SHAPE', 'provider_count': 0, 'model_key_present': False, 'mcp_server_count': 0}
    providers = data.get('provider') if isinstance(data.get('provider'), dict) else {}
    mcp = data.get('mcp') if isinstance(data.get('mcp'), dict) else {}
    servers = mcp.get('servers') if isinstance(mcp.get('servers'), dict) else {}
    return {
        'state': 'READABLE',
        'provider_count': len(providers),
        'model_key_present': 'model' in data,
        'mcp_server_count': len(servers),
    }


def config_path_label(path: Path) -> tuple[str, str]:
    resolved = path.expanduser().absolute()
    identity = hash_bytes(str(resolved).encode('utf-8', errors='replace'))
    try:
        label = '~/' + resolved.relative_to(Path.home().resolve()).as_posix()
    except ValueError:
        appdata = os.environ.get('APPDATA')
        try:
            label = '%APPDATA%/' + resolved.relative_to(Path(appdata).resolve()).as_posix() if appdata else 'CUSTOM_CONFIG_PATH'
        except ValueError:
            label = 'CUSTOM_CONFIG_PATH'
    return label, identity


def inspect_assets(repo: Path, manifest_path: Path | None, assets_root: Path | None) -> tuple[list[dict], list[dict]]:
    path = Path(os.path.abspath((manifest_path or (repo / 'offline' / 'assets-manifest.json')).expanduser()))
    root = Path(os.path.abspath((assets_root or path.parent).expanduser()))
    try:
        if path.is_symlink() or root.is_symlink() or not path.is_file() or not root.is_dir():
            raise ValueError('unsafe manifest or asset root')
        path = path.resolve(strict=True)
        root = root.resolve(strict=True)
        manifest = json.loads(path.read_text(encoding='utf-8'))
        records = manifest['assets']
        if manifest.get('schema') != 'golden-offline-assets/v1' or not isinstance(records, list):
            raise ValueError('invalid asset manifest shape')
        names = [item.get('name') for item in records if isinstance(item, dict)]
        if (len(names) != len(records) or any(not isinstance(name, str) for name in names)
                or len(names) != len(set(names))
                or not REQUIRED_ASSET_NAMES <= set(names)):
            raise ValueError('required offline asset inventory is incomplete or duplicated')
    except (OSError, ValueError, KeyError, TypeError):
        return [], [{'name': 'offline assets manifest', 'status': 'UNKNOWN', 'reason': 'missing-or-invalid'}]
    observed = []
    missing = []
    for item in records:
        if not isinstance(item, dict):
            missing.append({'name': 'offline asset entry', 'status': 'INVALID', 'reason': 'invalid-record'})
            continue
        name = str(item.get('name', 'unnamed asset'))
        if item.get('status') != 'STAGED':
            missing.append({'name': name, 'status': 'NOT_STAGED', 'reason': 'manifest-status'})
            continue
        rel = PurePosixPath(str(item.get('path', '')))
        if not rel.parts or rel.is_absolute() or '..' in rel.parts:
            missing.append({'name': name, 'status': 'INVALID', 'reason': 'unsafe-path'})
            continue
        artifact = root.joinpath(*rel.parts)
        if root not in artifact.parents or any(part.is_symlink() for part in [artifact, *artifact.parents] if part != root):
            missing.append({'name': name, 'status': 'INVALID', 'reason': 'symlink'})
            continue
        if not artifact.is_file() or not isinstance(item.get('sha256'), str) or hash_file(artifact) != item['sha256'].lower():
            missing.append({'name': name, 'status': 'INVALID', 'reason': 'missing-or-hash-mismatch'})
            continue
        if item.get('license_review_status') != 'APPROVED':
            missing.append({'name': name, 'status': 'NEEDS_LICENSE_REVIEW', 'reason': 'license-review-not-approved'})
            continue
        observed.append({'name': name, 'status': 'STAGED_AND_HASH_VERIFIED', 'sha256': item['sha256']})
    return observed, missing


def inspect_install_diff(repo: Path, target: Path) -> dict:
    additions: list[str] = []
    unchanged: list[str] = []
    conflicts: list[str] = []
    if target.is_symlink():
        return {'additions': [], 'already_matches': [], 'conflicts': ['target/ (symlink)']}
    source_root = repo / '.opencode'
    for category in ('agents', 'skills', 'commands'):
        source = source_root / category
        if not source.is_dir():
            conflicts.append(f'{category}/ (source missing)')
            continue
        for item in sorted(source.rglob('*')):
            if not item.is_file():
                continue
            relative = item.relative_to(source_root)
            destination = target / relative
            label = relative.as_posix()
            cursor = destination
            symlinked = False
            while cursor != target:
                if cursor.is_symlink():
                    symlinked = True
                    break
                cursor = cursor.parent
            if symlinked:
                conflicts.append(label)
            elif not destination.exists():
                additions.append(label)
            elif destination.is_file() and hash_file(destination) == hash_file(item):
                unchanged.append(label)
            else:
                conflicts.append(label)
    return {'additions': additions, 'already_matches': unchanged, 'conflicts': conflicts}


def doctor(repo: Path = ROOT, config: Path | None = None, assets_manifest: Path | None = None,
           assets_root: Path | None = None) -> dict:
    config = (config or config_path()).expanduser().absolute()
    config_label, config_identity = config_path_label(config)
    runtime = {'python': {'available': True, 'version': sys.version.split()[0], 'version_source': 'running-interpreter'},
               'node': local_executable('node'), 'opencode': local_executable('opencode')}
    opencode = runtime['opencode']['version']
    node = runtime['node']['version']
    compatibility = 'UNKNOWN'
    if opencode:
        match = re.fullmatch(r'(\d+)\.(\d+)\.(\d+)(?:[-+][A-Za-z0-9.-]+)?', opencode)
        if match:
            major = int(match[1])
            compatibility = 'PUBLIC_V2_CANDIDATE' if major == 2 else 'UNSUPPORTED_MAJOR_VERSION'
    verified_assets, missing = inspect_assets(repo, assets_manifest, assets_root)
    install_diff = inspect_install_diff(repo, config.parent)
    status = 'INCOMPATIBLE' if compatibility == 'UNSUPPORTED_MAJOR_VERSION' else (
        'INCOMPATIBLE' if install_diff['conflicts'] else
        'UNKNOWN' if compatibility == 'UNKNOWN' or not node or any(asset['status'] == 'UNKNOWN' for asset in missing) else
        'NEEDS_APPROVED_ASSETS' if missing else 'READY_TO_INTEGRATE')
    config_report = inspect_config(config)
    if config_report['state'] in ('UNSAFE_PATH', 'UNREADABLE_OR_INVALID', 'INVALID_SHAPE'):
        status = 'INCOMPATIBLE'
    report = {
        'schema': 'golden-company-doctor/v1',
        'generated_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'machine': {'os': platform.system(), 'release': platform.release(), 'architecture': platform.machine(),
                    'python': runtime['python']['version'], 'node': node, 'opencode': opencode,
                    'opencode_compatibility': compatibility,
                    'executables': runtime},
        'opencode_config_path': config_label,
        'opencode_config_path_sha256': config_identity,
        'opencode_config': config_report,
        'identified_tools': {name: shutil.which(name) is not None for name in ('git', 'python', 'node', 'opencode')},
        'project_environment': {'git_metadata_present': (repo / '.git').exists(),
                                'github_ci_config_present': (repo / '.github' / 'workflows').is_dir(),
                                'ci_environment_detected': 'CI' in os.environ or 'GITHUB_ACTIONS' in os.environ,
                                'known_artifact_path_variable_names_present': [name for name in ('ARTIFACTORY_HOME', 'NEXUS_HOME', 'CI_PROJECT_DIR') if name in os.environ]},
        'filesystem': {'repo_readable': os.access(repo, os.R_OK), 'config_parent_exists': config.parent.is_dir(),
                       'config_parent_writable': config.parent.is_dir() and os.access(config.parent, os.W_OK)},
        'install_diff': install_diff,
        'offline_assets_verified': verified_assets,
        'offline_assets_missing': missing,
        'status': status,
        'review_diff': {'files': install_diff,
                        'would_copy': ['agents/', 'skills/', 'commands/'],
                        'would_not_change': ['provider', 'model', 'authentication', 'MCP configuration', 'Git state']},
        'network_policy': 'Doctor launched no executable and made no network calls. OpenCode/Node versions came only from matching local package metadata or managed-install paths; host firewall enforcement is not observed.',
    }
    canonical = json.dumps(report, sort_keys=True, separators=(',', ':')).encode()
    report['doctor_result_sha256'] = hash_bytes(canonical)
    return report


def verify_doctor(report: dict, current: dict) -> None:
    supplied = report.get('doctor_result_sha256')
    copy = dict(report); copy.pop('doctor_result_sha256', None)
    if supplied != hash_bytes(json.dumps(copy, sort_keys=True, separators=(',', ':')).encode()):
        raise ValueError('Doctor result digest is invalid; rerun Step A.')
    if report.get('schema') != 'golden-company-doctor/v1' or report.get('status') not in ('READY_TO_INTEGRATE', 'NEEDS_APPROVED_ASSETS'):
        raise ValueError('Doctor result does not permit asset integration.')
    stable_report = dict(report); stable_report.pop('generated_at_utc', None); stable_report.pop('doctor_result_sha256', None)
    stable_current = dict(current); stable_current.pop('generated_at_utc', None); stable_current.pop('doctor_result_sha256', None)
    if stable_report != stable_current:
        raise ValueError('Company runtime, config, staged assets, or installation diff changed since doctor; rerun Step A.')


def bundle_assets(archive: Path) -> tuple[dict, dict[str, bytes]]:
    manifest = package_offline.verify_bundle(archive)
    import tarfile
    contents: dict[str, bytes] = {}
    with tarfile.open(archive, 'r:gz') as tar:
        for item in manifest['files']:
            rel = PurePosixPath(item['path'])
            if rel.parts[:1] != ('.opencode',) or rel.parts[1:2] not in (('agents',), ('skills',), ('commands',)):
                continue
            member = tar.getmember(f"{package_offline.PREFIX}/{item['path']}")
            stream = tar.extractfile(member)
            if stream is None:
                raise ValueError(f"Bundle asset unavailable: {item['path']}")
            contents[rel.as_posix()] = stream.read()
    return manifest, contents


def apply_bundle(archive: Path, target: Path, report: dict, transaction_path: Path) -> dict:
    target = target.expanduser()
    if target.is_symlink() or not target.is_dir():
        raise ValueError('Target must be an existing real directory.')
    target = target.resolve(strict=True)
    ensure_real_directory(target)
    transaction_path = Path(os.path.abspath(transaction_path.expanduser()))
    if transaction_path.parent.is_symlink() or not transaction_path.parent.is_dir():
        raise ValueError('Transaction parent must be an existing real directory.')
    if transaction_path.is_symlink() or transaction_path.exists():
        raise ValueError('Transaction path already exists; choose a new path.')
    transaction_path = transaction_path.parent.resolve(strict=True) / transaction_path.name
    if transaction_path.is_symlink() or transaction_path.exists():
        raise ValueError('Transaction path already exists; choose a new path.')
    current = doctor(config=target / 'opencode.json')
    verify_doctor(report, current)
    if current['machine']['opencode_compatibility'] != 'PUBLIC_V2_CANDIDATE':
        raise ValueError('Installed OpenCode compatibility is unknown or unsupported; do not apply.')
    manifest, assets = bundle_assets(archive)
    additions = []
    conflicts = []
    for rel, data in assets.items():
        dest = target / rel.split('/', 1)[1]
        cursor = target
        for part in PurePosixPath(rel.split('/', 1)[1]).parts[:-1]:
            cursor = cursor / part
            if cursor.is_symlink():
                raise ValueError(f'Symlink directory blocked: {cursor.name}')
        if dest.exists() or dest.is_symlink():
            if dest.is_symlink() or not dest.is_file() or hash_bytes(dest.read_bytes()) != hash_bytes(data):
                conflicts.append(dest.name)
        else:
            additions.append((dest, data, rel))
    if conflicts:
        raise ValueError(f'Conflicting existing files; no files changed: {conflicts}')
    created: list[tuple[Path, str]] = []
    transaction_created = False
    try:
        for dest, data, rel in additions:
            ensure_real_directory(dest.parent, target)
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0)
            descriptor = os.open(dest, flags, 0o644)
            created.append((dest, hash_bytes(data)))
            with os.fdopen(descriptor, 'wb') as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
        with tempfile.TemporaryDirectory(prefix='golden-smoke-') as tmp:
            smoke = Path(tmp)
            (smoke / 'golden.project.json').write_text(json.dumps({
                'name': 'golden-bootstrap-smoke', 'profile': 'python', 'criticality': 'simple',
                'golden_version': json.loads((ROOT / 'standards' / 'release.json').read_text())['version'],
                'capabilities': {}, 'commands': {},
            }), encoding='utf-8')
            result = subprocess.run([sys.executable, '-S', str(ROOT / 'scripts' / 'golden.py'), 'doctor', '--project', str(smoke)],
                                    capture_output=True, text=True, timeout=10, check=False,
                                    env={'PATH': os.environ.get('PATH', ''), 'PYTHONNOUSERSITE': '1', 'PIP_NO_INDEX': '1', 'UV_OFFLINE': '1', 'npm_config_offline': 'true'})
            if result.returncode != 0 or 'Manifest: PASS' not in result.stdout:
                raise ValueError('Synthetic project smoke test failed.')
        transaction = {'schema': 'golden-bootstrap-transaction/v1', 'bundle_sha256': hash_file(archive),
                       'target': str(target), 'created_files': [{'path': p.relative_to(target).as_posix(), 'sha256': digest} for p, digest in created],
                       'mode': 'ADD_ONLY_ROLLBACK_REMOVES_UNCHANGED_CREATED_FILES'}
        if transaction_path.parent.is_symlink() or not transaction_path.parent.is_dir():
            raise ValueError('Transaction parent changed during apply.')
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0)
        descriptor = os.open(transaction_path, flags, 0o600)
        transaction_created = True
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write((json.dumps(transaction, indent=2) + '\n').encode())
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        if transaction_created:
            try:
                transaction_path.unlink()
            except OSError:
                pass
        for path, expected_hash in reversed(created):
            try:
                if not path.is_symlink() and path.is_file() and hash_file(path) == expected_hash:
                    path.unlink()
            except OSError:
                pass
        raise
    return {'added': len(created), 'unchanged': len(assets) - len(created), 'transaction': str(transaction_path),
            'bundle_qualification': manifest['qualification'], 'smoke_test': 'PASS'}


def rollback(transaction_path: Path) -> int:
    transaction_path = Path(os.path.abspath(transaction_path.expanduser()))
    if transaction_path.is_symlink() or not transaction_path.is_file():
        raise ValueError('Rollback transaction path is unsafe.')
    transaction_path = transaction_path.resolve(strict=True)
    data = json.loads(transaction_path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or data.get('schema') != 'golden-bootstrap-transaction/v1' or data.get('mode') != 'ADD_ONLY_ROLLBACK_REMOVES_UNCHANGED_CREATED_FILES':
        raise ValueError('Unsupported transaction record.')
    target_path = Path(os.path.abspath(Path(data.get('target', '')).expanduser()))
    if target_path.is_symlink() or not target_path.is_dir():
        raise ValueError('Rollback target must be an existing real directory.')
    target = target_path.resolve(strict=True)
    removed = 0
    created_files = data.get('created_files')
    if not isinstance(created_files, list):
        raise ValueError('Invalid rollback file list.')
    for item in created_files:
        if not isinstance(item, dict) or not isinstance(item.get('path'), str) or not isinstance(item.get('sha256'), str):
            raise ValueError('Invalid rollback file record.')
        raw_path = item['path']
        rel = PurePosixPath(raw_path)
        if ('\\' in raw_path or rel.as_posix() != raw_path or rel.is_absolute() or '..' in rel.parts
                or not rel.parts or rel.parts[0] not in ('agents', 'skills', 'commands')
                or len(item['sha256']) != 64 or any(char not in '0123456789abcdef' for char in item['sha256'].lower())):
            raise ValueError('Unsafe rollback path.')
        path = target.joinpath(*rel.parts)
        cursor = path
        while cursor != target:
            if cursor.is_symlink():
                raise ValueError(f'Rollback refused symlink: {rel}')
            cursor = cursor.parent
        if cursor != target or target.is_symlink():
            raise ValueError(f'Rollback refused symlink: {rel}')
        if not path.exists():
            continue
        if not path.is_file() or hash_bytes(path.read_bytes()) != item['sha256']:
            raise ValueError(f'Rollback refused modified file: {rel}')
        path.unlink(); removed += 1
    return removed


def main() -> int:
    parser = argparse.ArgumentParser(description='Offline OpenCode doctor/apply/rollback. No provider settings are modified.')
    sub = parser.add_subparsers(dest='action', required=True)
    p = sub.add_parser('doctor'); p.add_argument('--repo', type=Path, default=ROOT); p.add_argument('--out', type=Path, required=True); p.add_argument('--config', type=Path); p.add_argument('--assets-manifest', type=Path, help='Optional company-local staged-asset manifest.'); p.add_argument('--assets-root', type=Path, help='Root for verifying staged asset hashes.')
    p = sub.add_parser('apply'); p.add_argument('--doctor-result', type=Path, required=True); p.add_argument('--bundle', type=Path, required=True); p.add_argument('--target', type=Path, required=True); p.add_argument('--transaction', type=Path, required=True); p.add_argument('--authorize-reviewed-apply', action='store_true')
    p = sub.add_parser('rollback'); p.add_argument('--transaction', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.action == 'doctor':
            result = doctor(args.repo, args.config, args.assets_manifest, args.assets_root)
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
            print(f"{result['status']}: OS={result['machine']['os']} Python={result['machine']['python']} Node={result['machine']['node']} OpenCode={result['machine']['opencode']}")
            print('No settings changed. Missing offline assets:', len(result['offline_assets_missing']))
            print('Review diff:', json.dumps(result['review_diff'], sort_keys=True))
        elif args.action == 'apply':
            if not args.authorize_reviewed_apply:
                raise ValueError('Step B requires --authorize-reviewed-apply after reviewing the doctor result and bundle.')
            report = json.loads(args.doctor_result.read_text(encoding='utf-8'))
            print(json.dumps(apply_bundle(args.bundle, args.target, report, args.transaction), indent=2))
        else:
            print(f"Removed unchanged files: {rollback(args.transaction)}")
        return 0
    except (OSError, ValueError, KeyError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        print(f'Bootstrap error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
