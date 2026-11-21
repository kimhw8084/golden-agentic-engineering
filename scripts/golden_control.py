#!/usr/bin/env python3
"""Read-only, offline-first local dashboard for Golden installation/evidence status."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import shutil
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
CONTROL = ROOT / 'control'
GROUPS = ('agents', 'skills', 'commands')
CHECKSUM_SKIP_DIRS = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'dist', 'build', '.next', 'coverage'}
DOCS = {
    '/docs/COMPANY_START_HERE.md': 'COMPANY_START_HERE.md',
    '/docs/OPEN_ITEMS_FOR_COMPANY.md': 'OPEN_ITEMS_FOR_COMPANY.md',
    '/docs/START_HERE_COMPANY_OPENCODE.md': 'START_HERE_COMPANY_OPENCODE.md',
    '/docs/ARCHITECTURE.md': 'docs/ARCHITECTURE.md',
    '/docs/AGENTIC_FIRST_EVALUATION.md': 'docs/AGENTIC_FIRST_EVALUATION.md',
    '/docs/GOLDEN_CONTROL_SPEC.md': 'docs/GOLDEN_CONTROL_SPEC.md',
    '/docs/QUALIFICATION_MATRIX.md': 'docs/QUALIFICATION_MATRIX.md',
    '/docs/TOOL_ACQUISITION.md': 'docs/TOOL_ACQUISITION.md',
    '/docs/OPEN_CODE_COMPATIBILITY.md': 'docs/OPEN_CODE_COMPATIBILITY.md',
    '/docs/RESEARCH.md': 'research/README.md',
    '/docs/OFFLINE.md': 'offline/README.md',
}
WORKFLOWS = ROOT / 'workflows' / 'task-routing.json'


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_asset_counts() -> dict[str, int]:
    result = {}
    for group in GROUPS:
        base = ROOT / '.opencode' / group
        if group == 'skills':
            result[group] = sum(1 for path in base.glob('*/SKILL.md') if path.is_file())
        else:
            result[group] = sum(1 for path in base.rglob('*.md') if path.is_file())
    return result


def compare_installation(target: Path | None) -> dict:
    if target is None:
        return {'state': 'NOT_CHECKED', 'target_configured': False, 'groups': {},
                'same': None, 'missing': None, 'changed': None}
    if not target.is_dir():
        return {'state': 'TARGET_NOT_FOUND', 'target_configured': True, 'groups': {},
                'same': 0, 'missing': None, 'changed': None}

    groups = {}
    totals = {'same': 0, 'missing': 0, 'changed': 0}
    for group in GROUPS:
        source_root = ROOT / '.opencode' / group
        counts = {'same': 0, 'missing': 0, 'changed': 0}
        for source in sorted(source_root.rglob('*')):
            if not source.is_file():
                continue
            installed = target / group / source.relative_to(source_root)
            if not installed.is_file():
                counts['missing'] += 1
            elif digest(source) == digest(installed):
                counts['same'] += 1
            else:
                counts['changed'] += 1
        groups[group] = counts
        for key in totals:
            totals[key] += counts[key]

    state = 'IN_SYNC_WITH_CHECKOUT'
    if totals['changed']:
        state = 'LOCAL_CHANGES_NEED_REVIEW'
    elif totals['missing']:
        state = 'INSTALL_INCOMPLETE'
    return {'state': state, 'target_configured': True, 'groups': groups, **totals}


def checksum_status() -> dict:
    manifest = ROOT / 'SHA256SUMS.txt'
    checked = missing = altered = 0
    listed = set()
    if not manifest.is_file():
        return {'state': 'MISSING_MANIFEST', 'checked': 0, 'missing': 0, 'altered': 0, 'unlisted': 0}
    for line in manifest.read_text(encoding='utf-8').splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        expected, name = line.split('  ', 1)
        listed.add(name)
        path = ROOT / name
        if not path.is_file():
            missing += 1
            continue
        checked += 1
        if digest(path) != expected:
            altered += 1
    actual = set()
    for path in ROOT.rglob('*'):
        relative = path.relative_to(ROOT)
        if any(part in CHECKSUM_SKIP_DIRS for part in relative.parts):
            continue
        if path.is_file() and not path.is_symlink() and relative.as_posix() not in {'SHA256SUMS.txt', 'scripts/update_checksums.py'}:
            actual.add(relative.as_posix())
    unlisted = len(actual - listed)
    state = 'VERIFIED' if not missing and not altered and not unlisted else 'MISMATCH'
    return {'state': state, 'checked': checked, 'missing': missing, 'altered': altered, 'unlisted': unlisted}


def evidence_activity(directory: Path | None) -> dict:
    empty = {'status': 'NOT_CONNECTED', 'reports': None, 'fast': None, 'full': None,
             'release_qualified': None, 'not_qualified': None, 'last_report_utc': None,
             'partial': False}
    if directory is None:
        return empty
    if not directory.is_dir():
        return {**empty, 'status': 'DIRECTORY_NOT_FOUND'}

    reports = []
    partial = False
    for path in sorted(directory.glob('*.json')):
        if len(reports) == 1000:
            partial = True
            break
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, UnicodeError, ValueError):
            continue
        if isinstance(data, dict) and data.get('schema') == 'golden-evidence/v0.1':
            reports.append(data)

    modes = [data.get('mode') for data in reports]
    dates = [data.get('generated_at_utc') for data in reports if isinstance(data.get('generated_at_utc'), str)]
    return {
        'status': 'CONNECTED' if reports else 'NO_EVIDENCE_FILES',
        'reports': len(reports),
        'fast': modes.count('FAST'),
        'full': modes.count('FULL'),
        'release_qualified': sum(data.get('qualifies_release') is True for data in reports),
        'not_qualified': sum(data.get('qualifies_release') is False for data in reports),
        'last_report_utc': max(dates) if dates else None,
        'partial': partial,
    }


def project_agent_configuration() -> dict:
    """Report the checked-in default-agent declaration without implying runtime discovery."""
    config_path = ROOT / '.opencode' / 'opencode.json'
    try:
        config = json.loads(config_path.read_text(encoding='utf-8'))
    except (OSError, UnicodeError, ValueError):
        return {'status': 'UNKNOWN', 'agent': None, 'config_path': '.opencode/opencode.json',
                'runtime_selection': 'NOT_TESTED', 'evidence_scope': 'CHECKED_IN_CONFIG_ONLY'}
    if not isinstance(config, dict):
        status = 'INVALID_CONFIG'
        agent = None
    elif config.get('default_agent') != 'golden-engineer':
        status = 'NOT_GOLDEN_DEFAULT'
        agent = None
    else:
        agent_path = ROOT / '.opencode' / 'agents' / 'golden-engineer.md'
        try:
            source = agent_path.read_text(encoding='utf-8')
        except (OSError, UnicodeError):
            source = ''
        header = source.split('---', 2)
        is_primary = len(header) == 3 and any(line.strip() == 'mode: primary' for line in header[1].splitlines())
        status = 'CONFIGURED' if is_primary else 'INVALID_AGENT_REFERENCE'
        agent = 'golden-engineer' if is_primary else None
    return {'status': status, 'agent': agent, 'config_path': '.opencode/opencode.json',
            'runtime_selection': 'NOT_TESTED', 'evidence_scope': 'CHECKED_IN_CONFIG_ONLY'}


def git_status() -> dict:
    def run(*args: str) -> str | None:
        try:
            result = subprocess.run(['git', '-C', str(ROOT), *args], capture_output=True,
                                    text=True, timeout=4, check=False)
        except (OSError, subprocess.TimeoutExpired):
            return None
        return result.stdout.strip() if result.returncode == 0 else None

    branch = run('rev-parse', '--abbrev-ref', 'HEAD')
    commit = run('rev-parse', '--short', 'HEAD')
    changes = run('status', '--porcelain')
    if branch is None or commit is None or changes is None:
        return {'status': 'NOT_AVAILABLE', 'branch': None, 'commit': None, 'clean': None}
    counts = run('rev-list', '--left-right', '--count', '@{upstream}...HEAD')
    behind = ahead = None
    if counts:
        try:
            behind, ahead = (int(value) for value in counts.split())
        except (ValueError, TypeError):
            pass
    return {'status': 'AVAILABLE', 'branch': branch, 'commit': commit, 'clean': changes == '',
            'ahead': ahead, 'behind': behind}


def snapshot(target: Path | None, evidence_dir: Path | None) -> dict:
    minimum_python = 'UNKNOWN'
    try:
        release = json.loads((ROOT / 'standards' / 'release.json').read_text(encoding='utf-8'))
        version = release.get('version', 'UNKNOWN')
        qualification = release.get('status', 'UNKNOWN')
        minimum_python = release.get('minimum_python', 'UNKNOWN')
    except (OSError, ValueError):
        version, qualification = 'UNKNOWN', 'UNKNOWN'

    installation = compare_installation(target)
    activity = evidence_activity(evidence_dir)
    project_agent = project_agent_configuration()
    package = checksum_status()
    update_count = None if installation['missing'] is None else installation['missing'] + installation['changed']
    return {
        'generated_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'),
        'product': {'version': version, 'qualification': qualification, 'minimum_python': minimum_python},
        'repository': git_status(),
        'assets': source_asset_counts(),
        'project_agent': project_agent,
        'installation': installation,
        'updates': {
            'status': 'CHECKOUT_ONLY' if installation['target_configured'] else 'NOT_CHECKED',
            'available_from_checkout': update_count,
            'approved_release_feed': 'NOT_CONFIGURED',
        },
        'integrity': package,
        'activity': {
            'golden_evidence': activity,
            'agent_skill_mcp_usage': 'NOT_INSTRUMENTED',
            'invocation_trace': {'status': 'NOT_INSTRUMENTED', 'source': 'NONE',
                                 'provenance': 'UNAVAILABLE'},
            'telemetry_upload': 'OFF',
        },
        'runtime': {
            'python': sys.version.split()[0],
            'opencode_binary_detected': shutil.which('opencode') is not None,
            'company_agent_skill_mcp_inventory': 'NOT_RUN',
        },
        'progress': [
            {'title': 'Agentic-first workflow', 'status': 'IN_REPOSITORY',
             'detail': 'Project config selects the Golden primary in compatible builds; company runtime discovery and a real agentic run remain unverified.'},
            {'title': 'Local Golden Control', 'status': 'PROTOTYPE',
             'detail': 'Read-only local view compares assets and summarizes local Golden evidence.'},
            {'title': 'Company OpenCode compatibility', 'status': 'NOT_TESTED',
             'detail': 'Actual internal agent, skill, MCP, and permission behavior still needs a company-machine pilot.'},
            {'title': 'Approved release and update feed', 'status': 'NOT_CONFIGURED',
             'detail': 'No company artifact or release adapter is connected.'},
            {'title': 'Agent, skill, and MCP usage', 'status': 'NOT_INSTRUMENTED',
             'detail': 'No activity feed is connected; prompts and source content are not collected.'},
            {'title': 'Team qualification', 'status': 'NOT_APPROVED',
             'detail': 'Windows, internal CI, security, licensing, and team adoption remain unqualified.'},
        ],
        'release_note': 'A matching checkout does not prove that this version is a company-approved release.',
    }


class ControlHandler(BaseHTTPRequestHandler):
    target: Path | None = None
    evidence_dir: Path | None = None
    server_version = 'GoldenControl/0.1'
    sys_version = ''

    def end_headers(self) -> None:
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        super().end_headers()

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        if path == '/api/state':
            payload = json.dumps(snapshot(self.target, self.evidence_dir)).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        if path == '/api/workflows':
            try:
                payload = WORKFLOWS.read_bytes()
            except OSError:
                self.send_error(503)
                return
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        asset = {'/': 'index.html', '/index.html': 'index.html',
                 '/styles.css': 'styles.css', '/app.js': 'app.js',
                 '/workflows/task-routing.json': '../workflows/task-routing.json',
                 '/research/capability-selection.json': '../research/capability-selection.json'}.get(path)
        if asset:
            content_path = (CONTROL / asset).resolve()
            self._send_file(content_path, 'application/json' if asset.endswith('.json') else 'text/html' if asset.endswith('.html') else
                            'text/css' if asset.endswith('.css') else 'text/javascript')
            return
        if path in DOCS:
            self._send_file(ROOT / DOCS[path], 'text/plain')
            return
        self.send_error(404)

    def _send_file(self, path: Path, content_type: str) -> None:
        try:
            payload = path.read_bytes()
        except OSError:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header('Content-Type', f'{content_type}; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, _format: str, *_args: object) -> None:
        return


def main() -> int:
    parser = argparse.ArgumentParser(description='Serve the local, read-only Golden Control dashboard.')
    parser.add_argument('--target', type=Path, help='Existing OpenCode config directory to compare Golden assets with')
    parser.add_argument('--evidence-dir', type=Path, help='Local directory of Golden evidence JSON reports to summarize')
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error('--port must be between 1024 and 65535')

    ControlHandler.target = args.target.expanduser().resolve() if args.target else None
    ControlHandler.evidence_dir = args.evidence_dir.expanduser().resolve() if args.evidence_dir else None
    server = HTTPServer(('127.0.0.1', args.port), ControlHandler)
    print(f'Golden Control is local and read-only: http://127.0.0.1:{args.port}')
    print('Stop with Ctrl-C. No data is uploaded.')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
