#!/usr/bin/env python3
"""Build an offline dependency inventory and CycloneDX SBOM from npm lock + modules."""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
import platform
import re
from pathlib import Path, PurePosixPath
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
OSI_LICENSE_IDS = frozenset({
    'MIT', 'MIT-0', 'Apache-2.0', 'BSD-2-Clause', 'BSD-3-Clause', 'ISC', 'BlueOak-1.0.0',
})
OSI_LICENSE_SOURCE = 'https://opensource.org/licenses'
LICENSE_FILE_RE = re.compile(r'^(license|licence|copying|notice)(\.|$)', re.IGNORECASE)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def license_declaration(package: dict) -> list[str]:
    value = package.get('license')
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict) and isinstance(value.get('type'), str):
        return [value['type']]
    entries = package.get('licenses')
    if isinstance(entries, list):
        return [item['type'] for item in entries if isinstance(item, dict) and isinstance(item.get('type'), str)]
    return []


def declared_license_ids(expressions: list[str]) -> list[str]:
    tokens = []
    for expression in expressions:
        tokens.extend(re.findall(r'[A-Za-z0-9][A-Za-z0-9.+-]*', expression))
    return sorted({token for token in tokens if token.upper() not in ('AND', 'OR', 'WITH', 'SEE', 'LICENSE')})


def package_purl(name: str, version: str) -> str:
    return f'pkg:npm/{quote(name, safe="/-._~")}@{quote(version, safe="-._~+")}'


def package_lock_key(package_path: str) -> str:
    return 'node_modules/' + package_path


def find_dependency_key(package_dir: Path, dependency: str, modules_root: Path, lock_packages: dict) -> str | None:
    dependency_parts = dependency.split('/')
    current = package_dir
    project_root = modules_root.parent.resolve()
    while True:
        candidate = current.joinpath('node_modules', *dependency_parts, 'package.json')
        if candidate.is_file() and not candidate.is_symlink():
            try:
                package_path = candidate.parent.resolve(strict=True).relative_to(modules_root.resolve(strict=True)).as_posix()
            except (OSError, ValueError):
                return None
            key = package_lock_key(package_path)
            if key in lock_packages:
                return key
        if current == project_root or current.parent == current:
            return None
        current = current.parent


def sri_checksum(integrity: str) -> dict | None:
    for item in integrity.split():
        if item.startswith('sha512-'):
            try:
                digest = base64.b64decode(item[7:], validate=True).hex()
                return {'alg': 'SHA-512', 'content': digest}
            except (ValueError, base64.binascii.Error):
                return None
    return None


def audit(lock_path: Path, modules_root: Path) -> tuple[dict, dict]:
    lock_path = lock_path.resolve(strict=True)
    modules_root = modules_root.resolve(strict=True)
    lock = json.loads(lock_path.read_text(encoding='utf-8'))
    lock_packages = lock.get('packages')
    if not isinstance(lock_packages, dict) or not isinstance(lock_packages.get(''), dict):
        raise ValueError('package-lock.json must use a packages map with a root entry')
    root_record = lock_packages['']
    records = []
    record_by_key = {}
    missing_lock_fields = []
    missing_installed = []
    for key, locked in sorted(lock_packages.items()):
        if not key:
            continue
        rel = PurePosixPath(key)
        if rel.is_absolute() or '..' in rel.parts or '\\' in key or '\x00' in key:
            raise ValueError(f'Unsafe package path in lock: {key}')
        if not key.startswith('node_modules/') or not isinstance(locked, dict):
            raise ValueError(f'Unsupported package-lock entry: {key}')
        package_dir = modules_root.joinpath(*rel.parts[1:])
        package_json = package_dir / 'package.json'
        staged = package_json.is_file() and not package_json.is_symlink()
        manifest = {}
        if staged:
            try:
                package_json.resolve(strict=True).relative_to(modules_root)
                manifest = json.loads(package_json.read_text(encoding='utf-8'))
            except (OSError, ValueError, json.JSONDecodeError):
                staged = False
                manifest = {}
        if not staged:
            missing_installed.append(key)
        path_parts = rel.parts
        last_modules = len(path_parts) - 1 - tuple(reversed(path_parts)).index('node_modules')
        package_parts = path_parts[last_modules + 1:]
        if not package_parts:
            raise ValueError(f'Package path has no package name: {key}')
        path_name = '/'.join(package_parts[:2]) if package_parts and package_parts[0].startswith('@') else package_parts[0]
        name = manifest.get('name') or locked.get('name') or path_name
        version = manifest.get('version') or locked.get('version')
        if not locked.get('resolved') or not locked.get('integrity') or not isinstance(version, str):
            missing_lock_fields.append(key)
        declarations = license_declaration(manifest) if staged else []
        license_ids = declared_license_ids(declarations)
        files = []
        if staged:
            for file in sorted(package_dir.iterdir()):
                if file.is_file() and not file.is_symlink() and LICENSE_FILE_RE.match(file.name):
                    files.append({'name': file.name, 'sha256': sha256_file(file)})
        unknown_ids = sorted(set(license_ids) - OSI_LICENSE_IDS)
        if not staged:
            status = 'UNSTAGED_PLATFORM_OR_OPTIONAL_PACKAGE'
        elif not declarations:
            status = 'LICENSE_METADATA_MISSING'
        elif unknown_ids:
            status = 'OSI_LICENSE_REVIEW_REQUIRED'
        elif not files:
            status = 'LICENSE_FILE_REVIEW_REQUIRED'
        else:
            status = 'OSI_LISTED_METADATA_AND_NOTICE_FILE_PRESENT; COMPANY_CLEARANCE_PENDING'
        record = {
            'lock_path': key,
            'name': name,
            'version': version,
            'resolved': locked.get('resolved'),
            'integrity': locked.get('integrity'),
            'optional': bool(locked.get('optional')),
            'os': locked.get('os'),
            'cpu': locked.get('cpu'),
            'installed_in_audit_environment': staged,
            'declared_license': declarations,
            'license_ids': license_ids,
            'license_files': files,
            'unknown_license_ids': unknown_ids,
            'review_status': status,
        }
        records.append(record)
        record_by_key[key] = {'record': record, 'manifest': manifest, 'dir': package_dir if staged else None}
    if missing_lock_fields:
        raise ValueError(f'{len(missing_lock_fields)} lock entries lack resolved URL, integrity, or version metadata')

    root_deps = {}
    for field in ('dependencies', 'devDependencies', 'optionalDependencies'):
        if isinstance(root_record.get(field), dict):
            root_deps.update(root_record[field])
    package_rows = [value['record'] for value in record_by_key.values()]
    installed_rows = [row for row in package_rows if row['installed_in_audit_environment']]
    missing_license = [row for row in installed_rows if not row['declared_license']]
    unknown_license = [row for row in installed_rows if row['unknown_license_ids']]
    root_dir = modules_root.parent
    root_ref = package_purl(root_record.get('name', 'unnamed'), root_record.get('version', '0.0.0'))
    component_map: dict[str, dict] = {}
    dependencies = []
    root_dep_refs = []
    for dep_name in sorted(root_deps):
        dep_key = find_dependency_key(root_dir, dep_name, modules_root, lock_packages)
        if dep_key and dep_key in record_by_key:
            ref = package_purl(record_by_key[dep_key]['record']['name'], record_by_key[dep_key]['record']['version'])
            root_dep_refs.append(ref)
    dependencies.append({'ref': root_ref, 'dependsOn': sorted(set(root_dep_refs))})
    for key, value in sorted(record_by_key.items()):
        record = value['record']
        if not record['installed_in_audit_environment']:
            continue
        ref = package_purl(record['name'], record['version'])
        checksum = sri_checksum(record['integrity'])
        if checksum is None:
            raise ValueError(f'Unsupported or malformed integrity value: {key}')
        component = {
            'type': 'library',
            'bom-ref': ref,
            'name': record['name'],
            'version': record['version'],
            'purl': ref,
            'scope': 'required',
            'hashes': [checksum],
            'licenses': [{'license': {'id': license_id}} for license_id in record['license_ids']],
            'externalReferences': [{'type': 'distribution', 'url': record['resolved']}],
            'properties': [
                {'name': 'golden:review-status', 'value': record['review_status']},
                {'name': 'golden:lock-path', 'value': key},
            ],
        }
        component_map[ref] = component
        child_refs = []
        manifest = value['manifest']
        package_dir = value['dir']
        child_names = {}
        for field in ('dependencies', 'optionalDependencies'):
            if isinstance(manifest.get(field), dict):
                child_names.update(manifest[field])
        for child_name in sorted(child_names):
            child_key = find_dependency_key(package_dir, child_name, modules_root, lock_packages)
            if child_key and child_key in record_by_key and record_by_key[child_key]['record']['installed_in_audit_environment']:
                child = record_by_key[child_key]['record']
                child_refs.append(package_purl(child['name'], child['version']))
        dependencies.append({'ref': ref, 'dependsOn': sorted(set(child_refs))})

    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    sbom = {
        'bomFormat': 'CycloneDX',
        'specVersion': '1.6',
        'version': 1,
        'metadata': {
            'timestamp': now,
            'tools': {'components': [{'type': 'application', 'name': 'Golden npm dependency audit', 'version': '0.1.0'}]},
            'component': {'type': 'application', 'bom-ref': root_ref, 'name': root_record.get('name', 'unnamed'),
                          'version': root_record.get('version', '0.0.0')},
            'properties': [
                {'name': 'golden:platform-scope', 'value': f'{platform.system()}-{platform.machine()}'},
                {'name': 'golden:license-status', 'value': 'INVENTORY_ONLY; COMPANY_CLEARANCE_PENDING'},
            ],
        },
        'components': sorted(component_map.values(), key=lambda item: item['purl']),
        'dependencies': sorted(dependencies, key=lambda item: item['ref']),
    }
    report = {
        'schema': 'golden-npm-dependency-audit/v1',
        'generated_at_utc': now,
        'environment': {'os': platform.system(), 'architecture': platform.machine()},
        'package_lock': {'path': 'package-lock.json', 'lockfile_version': lock.get('lockfileVersion'), 'sha256': sha256_file(lock_path)},
        'direct_dependencies': sorted(root_deps),
        'counts': {
            'locked_entries': len(records),
            'installed_entries': len(installed_rows),
            'not_staged_entries': len(missing_installed),
            'license_metadata_missing': len(missing_license),
            'non_osi_or_unknown_license_ids': len(unknown_license),
            'license_files_missing': sum(not row['license_files'] for row in installed_rows),
            'sbom_component_count': len(component_map),
        },
        'license_sources': {'osi_approved_license_list': OSI_LICENSE_SOURCE, 'package_declaration': 'installed package.json'},
        'status': 'INVENTORY_ONLY; TRANSITIVE AND PLATFORM LICENSE REVIEW AND COMPANY CLEARANCE PENDING',
        'packages': records,
    }
    return report, sbom


def main() -> int:
    parser = argparse.ArgumentParser(description='Offline npm lock, notice, and CycloneDX inventory; makes no network calls.')
    parser.add_argument('--lock', type=Path, default=ROOT / 'examples' / 'react-app' / 'package-lock.json')
    parser.add_argument('--node-modules', type=Path, default=ROOT / 'examples' / 'react-app' / 'node_modules')
    parser.add_argument('--report', type=Path, required=True, help='JSON lock/license inventory output')
    parser.add_argument('--sbom', type=Path, required=True, help='CycloneDX 1.6 JSON SBOM output')
    args = parser.parse_args()
    try:
        report, sbom = audit(args.lock, args.node_modules)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.sbom.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        args.sbom.write_text(json.dumps(sbom, indent=2) + '\n', encoding='utf-8')
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(f"NPM_AUDIT_INVENTORY_READY locked={report['counts']['locked_entries']} installed={report['counts']['installed_entries']} "
          f"unstaged={report['counts']['not_staged_entries']} license_file_gaps={report['counts']['license_files_missing']} "
          "company_clearance=pending")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
