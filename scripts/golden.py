#!/usr/bin/env python3
"""Golden Proof: dependency-free, offline evidence runner (pilot implementation).

No network, no model/API calls, no code modification. Python >=3.10.
Reports cannot substitute for company independent evaluation.
"""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import hashlib
import html
import importlib.util
import json
import math
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HOME = Path(__file__).resolve().parent.parent
RULES = HOME / 'standards' / 'rules.json'
VERSION = HOME / 'standards' / 'release.json'
SKIP = {'.git', '.venv', 'venv', '__pycache__', 'node_modules', 'dist', 'build', '.golden', '.next', 'coverage'}


def read_json(path: Path):
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_check(data: object, version: str):
    if not isinstance(data, dict):
        return 'Root must be a JSON object.'
    for key in ('name', 'profile', 'criticality', 'golden_version', 'capabilities', 'commands'):
        if key not in data:
            return f'Missing project field: {key}'
    if not isinstance(data['name'], str) or not data['name'].strip():
        return 'name must be nonempty string.'
    if data['profile'] not in ('react', 'nicegui', 'python', 'other'):
        return 'profile must be react, nicegui, python, or other.'
    if data['criticality'] not in ('simple', 'workflow', 'production-critical'):
        return 'Invalid criticality.'
    if data['golden_version'] != version:
        return 'golden_version does not match the pinned Golden release.'
    if not isinstance(data['capabilities'], dict) or any(not isinstance(v, bool) for v in data['capabilities'].values()):
        return 'capabilities must be an object of booleans.'
    if not isinstance(data['commands'], dict):
        return 'commands must be an object.'
    for key, command in data['commands'].items():
        if not isinstance(key, str) or not isinstance(command, list) or not command or not all(isinstance(v, str) and v for v in command):
            return 'A project command declaration is not a nonempty array of strings.'
    return None


def approved_command(key: str, command: list[str]) -> tuple[bool, str]:
    """Allow a small set of deterministic test invocations; never execute arbitrary project argv."""
    if not command or not all(isinstance(part, str) and part for part in command):
        return False, 'Command must be a nonempty string array.'
    executable = command[0].lower()
    args = command[1:]
    # Resolve Python through this already-running interpreter. PATH aliases can
    # point to user-controlled wrappers and are not valid provenance.
    py = executable == '${python}'
    npm = executable in ('npm', 'pnpm')
    if key == 'python_tests' and py:
        if args in (['-m', 'unittest', 'discover', '-s', 'tests', '-v'], ['-m', 'pytest', '-q']):
            return True, 'python test runner allowlist'
    if key == 'ui_contracts' and py and args == ['-m', 'pytest', '-q']:
        return True, 'Python UI contract test allowlist'
    if key == 'python_lint' and ((py and args == ['-m', 'ruff', 'check', '.']) or (executable == 'ruff' and args == ['check', '.'])):
        return True, 'Ruff lint allowlist'
    if key in ('ts_typecheck', 'web_tests', 'ui_contracts') and npm:
        if args in (['run', 'typecheck'], ['run', 'test'], ['test']):
            return True, 'Node package-script allowlist'
    if key == 'browser_tests' and py and args[:2] == ['-m', 'pytest']:
        return True, 'Python browser-test allowlist'
    if key == 'security_scan' and ((py and args[:2] == ['-m', 'bandit']) or executable == 'bandit'):
        return True, 'Bandit allowlist'
    return False, f'Command is outside the deterministic allowlist for {key!r}.'


def load_manifest(root: Path):
    path = root / 'golden.project.json'
    if not path.is_file():
        return {}, f'Missing {path.name}'
    try:
        return read_json(path), None
    except (OSError, ValueError) as exc:
        return {}, f'Cannot read golden.project.json: {exc}'


def applicable(rule: dict, project: dict) -> tuple[str, str]:
    profile = project['profile']
    profiles = rule.get('profiles', ['*'])
    if '*' not in profiles and profile not in profiles:
        return 'NOT_APPLICABLE', f'Profile {profile!r} not in {profiles!r}; based on the project profile manifest.'
    missing = [cap for cap in rule.get('capabilities', []) if project['capabilities'].get(cap) is not True]
    if missing:
        return 'NOT_RUN', f'Applicability evidence missing for capabilities {missing!r}; false declarations alone do not prove non-applicability.'
    levels = rule.get('criticality', ['*'])
    if '*' not in levels and project['criticality'] not in levels:
        return 'NOT_RUN', 'Criticality is below this rule scope; independent owner applicability evidence is missing.'
    return 'APPLICABLE', f"Profile={profile}; criticality={project['criticality']}; manifest fields matched rule requirements."


def python_sources(root: Path):
    count = 0
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(x for x in dirs if x not in SKIP)
        for name in sorted(files):
            if name.endswith('.py'):
                count += 1
                if count > 5000:
                    raise RuntimeError('More than 5000 Python files; full syntax scan not completed.')
                yield Path(current) / name


def builtin(handler: str, root: Path, manifest: dict) -> tuple[str, str]:
    if handler == 'manifest':
        return 'PASS', 'Project manifest validated and version pin matches Golden release.'
    if handler == 'readme':
        return ('PASS', 'README.md exists.') if (root / 'README.md').is_file() else ('FAIL', 'Missing project README.md.')
    if handler == 'py_syntax':
        files = list(python_sources(root))
        if not files:
            return 'FAIL', 'Python-profile project contains no .py source files.'
        errors = []
        for p in files:
            try:
                ast.parse(p.read_text(encoding='utf-8-sig'), filename=str(p))
            except (SyntaxError, UnicodeError, OSError) as exc:
                file_id = hashlib.sha256(p.relative_to(root).as_posix().encode()).hexdigest()[:12]
                if isinstance(exc, SyntaxError):
                    errors.append(f'file_id={file_id}: syntax error at line {exc.lineno or 0}')
                else:
                    errors.append(f'file_id={file_id}: source unreadable or invalid UTF-8')
        return ('FAIL', '; '.join(errors[:8])) if errors else ('PASS', f'AST-parsed {len(files)} Python source files.')
    if handler == 'git':
        try:
            p = subprocess.run(['git', '-C', str(root), 'rev-parse', '--is-inside-work-tree'], capture_output=True, text=True, timeout=6, check=False)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return 'NOT_RUN', 'Git executable unavailable or timed out.'
        return ('PASS', 'Git worktree detected.') if p.returncode == 0 and p.stdout.strip() == 'true' else ('FAIL', 'Not a Git worktree.')
    return 'NOT_RUN', f'Unknown built-in check {handler!r}.'


def external(key: str, root: Path, project: dict, timeout: int) -> tuple[str, str]:
    cmd = project['commands'].get(key)
    if not cmd:
        return 'NOT_RUN', f'No approved command configured for {key!r}; a PASS is not claimed.'
    allowed, basis = approved_command(key, cmd)
    if not allowed:
        return 'NOT_RUN', basis
    if cmd[0] == '${PYTHON}' and cmd[1:3] == ['-m', 'pytest']:
        required_modules = ['pytest']
        if key == 'ui_contracts' and project.get('profile') == 'nicegui':
            required_modules.append('nicegui')
        missing = [name for name in required_modules if importlib.util.find_spec(name) is None]
        if missing:
            return 'NOT_RUN', f"Python test dependency unavailable: {', '.join(missing)}; check not executed."
    command_hash = hashlib.sha256(json.dumps(cmd, separators=(',', ':')).encode()).hexdigest()
    program = sys.executable if cmd[0] == '${PYTHON}' else cmd[0]
    resolved_program = shutil.which(program)
    if not resolved_program:
        return 'NOT_RUN', f'Executable unavailable: {program}.'
    try:
        executable_path = Path(resolved_program).resolve()
        if not executable_path.is_file() or executable_path.is_symlink():
            return 'NOT_RUN', 'Resolved command is not a regular executable file.'
        executable_sha256 = hashlib.sha256(executable_path.read_bytes()).hexdigest()
        safe_env = {}
        for name in ('PATH', 'SYSTEMROOT', 'WINDIR', 'PATHEXT', 'HOME', 'USERPROFILE', 'TMP', 'TEMP', 'TMPDIR', 'LANG', 'LC_ALL'):
            if name in os.environ:
                safe_env[name] = os.environ[name]
        safe_env.update({
            'PYTHONNOUSERSITE': '1', 'PYTHONDONTWRITEBYTECODE': '1',
            'PIP_NO_INDEX': '1', 'PIP_DISABLE_PIP_VERSION_CHECK': '1', 'UV_OFFLINE': '1',
            'npm_config_offline': 'true', 'npm_config_audit': 'false', 'npm_config_fund': 'false',
            'npm_config_update_notifier': 'false', 'PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD': '1',
            'NEXT_TELEMETRY_DISABLED': '1', 'DO_NOT_TRACK': '1', 'OTEL_SDK_DISABLED': 'true',
            'HF_HUB_OFFLINE': '1', 'TRANSFORMERS_OFFLINE': '1',
            'NO_PROXY': '*', 'no_proxy': '*',
        })
        if cmd[0] == '${PYTHON}' and cmd[1:3] == ['-m', 'pytest']:
            safe_env.update({'PYTEST_DISABLE_PLUGIN_AUTOLOAD': '1', 'PYTEST_ADDOPTS': '-p no:cacheprovider'})
        safe_cmd = [str(executable_path), *cmd[1:]]
        p = subprocess.run(safe_cmd, cwd=root, env=safe_env, capture_output=True, text=True,
                           timeout=min(max(timeout, 1), 600), shell=False, check=False)
        output = ((p.stdout or '') + '\n' + (p.stderr or '')).strip()
        output_hash = hashlib.sha256(output.encode('utf-8', errors='replace')).hexdigest()
        # Never persist raw command output; it may contain credentials, source or internal paths.
        return ('PASS' if p.returncode == 0 else 'FAIL'), f'Exit={p.returncode}; {basis}; argv_sha256={command_hash}; executable_sha256={executable_sha256}; output_bytes={len(output.encode("utf-8", errors="replace"))}; output_sha256={output_hash}'
    except subprocess.TimeoutExpired:
        return 'NOT_RUN', f'Command timed out after {timeout}s; not counted as PASS.'
    except OSError as exc:
        return 'NOT_RUN', 'Could not launch allowlisted check; local error details omitted.'


def run_check(root: Path, full: bool):
    spec = read_json(RULES)
    release = read_json(VERSION)
    project, loading_error = load_manifest(root)
    schema_error = loading_error or manifest_check(project, release['version'])
    results = []
    for rule in spec['rules']:
        start = time.perf_counter()
        if rule['id'] == 'GOLD-001':
            result, evidence = ('FAIL', schema_error) if schema_error else ('PASS', 'Manifest schema and release pin validated.')
        elif schema_error:
            result, evidence = 'NOT_RUN', 'Project manifest invalid; applicability cannot be inferred safely.'
        else:
            applicability, basis = applicable(rule, project)
            if applicability != 'APPLICABLE':
                result, evidence = applicability, basis
            elif not full and rule['stage'] != 'fast':
                result, evidence = 'DEFERRED', 'Full-only check deferred; fast result is not release qualification.'
            elif rule['kind'] == 'builtin':
                try:
                    result, evidence = builtin(rule['handler'], root, project)
                except (OSError, RuntimeError) as exc:
                    result, evidence = 'NOT_RUN', str(exc)
            elif rule['kind'] == 'command':
                result, evidence = external(rule['command_key'], root, project, rule.get('timeout_seconds', 90))
            else:
                result, evidence = 'NOT_RUN', 'Unknown rule kind.'
        results.append({'rule_id': rule['id'], 'title': rule['title'], 'status': result,
                        'mandatory': rule.get('mandatory', True), 'stage': rule['stage'],
                        'evidence': evidence, 'duration_ms': round((time.perf_counter() - start) * 1000, 2)})
    blocked = sorted(r['rule_id'] for r in results if full and r['mandatory'] and r['status'] in ('FAIL', 'NOT_RUN', 'DEFERRED'))
    evidence = {
        'schema': 'golden-evidence/v0.1', 'generated_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'golden_version': release['version'], 'rules_sha256': digest(RULES),
        'project_manifest_sha256': digest(root / 'golden.project.json') if (root / 'golden.project.json').is_file() else None,
        # Project names and checkout paths can contain customer or company details.
        'project': 'local-project',
        'mode': 'FULL' if full else 'FAST', 'qualifies_release': bool(full and not blocked),
        'blocking_rule_ids': blocked, 'rules_count': len(results), 'results': results,
        'disclaimer': 'Local deterministic evidence only. No human/company sign-off implied.'
    }
    return evidence


def render_report(data: dict, project_root: Path) -> str:
    # Imported JSON is never the authority for PASS or release qualification.
    # Replay against the explicitly supplied local project and render the fresh result.
    data = validate_evidence(data, project_root)
    rows = []
    for r in data['results']:
        cells = [r['rule_id'], r['status'], r['title'], r['evidence'], f"{r['duration_ms']} ms"]
        rows.append('<tr>' + ''.join('<td>' + html.escape(str(c)) + '</td>' for c in cells) + '</tr>')
    title = html.escape(str(data.get('project', 'Golden evidence')))
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Golden evidence</title><style>
    body{font:14px/1.5 system-ui,Arial;background:#fff;color:#111;margin:0 auto;padding:24px;max-width:1400px}
    h1{font-size:25px} .meta{color:#555}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #ccc;text-align:left;padding:9px;vertical-align:top}td{overflow-wrap:anywhere} th{background:#eee} .status{font-weight:700} .warn{border:2px solid #333;padding:12px} @media(max-width:700px){body{padding:12px;font-size:12px}td,th{padding:5px}}
    </style><h1>Golden Proof — ''' + title + '''</h1><p class="meta">Mode: ''' + html.escape(data['mode']) + ''' · Golden: ''' + html.escape(str(data['golden_version'])) + ''' · Evidence UTC: ''' + html.escape(data['generated_at_utc']) + '''</p><p class="warn">''' + ('Current local checks were replayed; company owner approval is still separate.' if data['qualifies_release'] else 'NOT RELEASE-QUALIFIED — failed, unrun or deferred checks may exist.') + '''</p><p class="meta">This report was generated from a fresh local replay. It does not imply company qualification or human approval.</p><table><thead><tr><th>ID</th><th>Status</th><th>Rule</th><th>Evidence</th><th>Duration</th></tr></thead><tbody>''' + '\n'.join(rows) + '''</tbody></table><p class="meta">Standalone report. No external assets, no server.</p></html>'''


def main():
    parser = argparse.ArgumentParser(description='Offline Golden Proof runner; no AI or remote services.')
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('doctor', 'check'):
        p = sub.add_parser(name)
        p.add_argument('--project', type=Path, default=Path.cwd())
        if name == 'check':
            mode = p.add_mutually_exclusive_group(required=True)
            mode.add_argument('--fast', action='store_true')
            mode.add_argument('--full', action='store_true')
            p.add_argument('--out', type=Path, help='Optional local JSON evidence path')
    p = sub.add_parser('explain'); p.add_argument('rule_id')
    p = sub.add_parser('report'); p.add_argument('--input', type=Path, required=True); p.add_argument('--project', type=Path, required=True, help='Project to re-run; imported evidence is never trusted as execution proof'); p.add_argument('--out', type=Path, required=True)
    sub.add_parser('list')
    args = parser.parse_args()
    if args.command == 'list':
        for r in read_json(RULES)['rules']:
            print(f"{r['id']}  {r['stage']:<4} {r['title']}")
        return 0
    if args.command == 'explain':
        matches = [r for r in read_json(RULES)['rules'] if r['id'] == args.rule_id]
        if not matches:
            print('Unknown rule ID', file=sys.stderr); return 2
        print(json.dumps(matches[0], indent=2)); return 0
    if args.command == 'doctor':
        root = args.project.resolve(); data, error = load_manifest(root)
        release = read_json(VERSION)
        reason = error or manifest_check(data, release['version'])
        print('Golden version:', release['version']); print('Python:', sys.version.split()[0]); print('Project: local project')
        print('Manifest:', 'FAIL: ' + reason if reason else 'PASS')
        print('Git:', shutil.which('git') or 'NOT_INSTALLED')
        if not reason:
            for name, cmd in sorted(data['commands'].items()):
                program = sys.executable if cmd[0] == '${PYTHON}' else cmd[0]
                print(f'Command {name}:', 'CONFIGURED' if shutil.which(program) or (root / program).is_file() else 'EXECUTABLE_NOT_FOUND')
        return 2 if reason else 0
    if args.command == 'check':
        root = args.project.resolve()
        data = run_check(root, full=args.full)
        for result in data['results']:
            print(f"{result['status']:<15} {result['rule_id']:<12} {result['evidence'][:140]}")
        print(f"Mode: {data['mode']} | release-qualified: {data['qualifies_release']} | blocked: {data['blocking_rule_ids']}")
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
            print('Evidence:', args.out)
        return 2 if data['blocking_rule_ids'] else 0
    if args.command == 'report':
        try:
            data = read_json(args.input)
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(render_report(data, args.project), encoding='utf-8')
            print('HTML report:', args.out)
            return 0
        except (OSError, ValueError, KeyError) as exc:
            print(str(exc), file=sys.stderr); return 2
    return 2


def validate_evidence(data: object, project_root: Path | None = None) -> dict:
    """Require a current local replay before accepting any imported PASS or qualification claim."""
    if not isinstance(data, dict) or data.get('schema') != 'golden-evidence/v0.1':
        raise ValueError('Unsupported Golden evidence schema.')
    expected_fields = {
        'schema', 'generated_at_utc', 'golden_version', 'rules_sha256',
        'project_manifest_sha256', 'project', 'mode', 'qualifies_release',
        'blocking_rule_ids', 'rules_count', 'results', 'disclaimer',
    }
    if set(data) != expected_fields:
        raise ValueError('Evidence fields are incomplete or contain an unsupported exception/provenance claim.')
    if data.get('mode') not in ('FAST', 'FULL') or not isinstance(data.get('results'), list):
        raise ValueError('Evidence mode/results are invalid.')
    release = read_json(VERSION)
    catalog = read_json(RULES)['rules']
    expected_rules = {row['id']: row['mandatory'] for row in catalog}
    if data.get('golden_version') != release['version'] or data.get('rules_sha256') != digest(RULES):
        raise ValueError('Evidence release/rule catalog pin is stale or invalid.')
    valid = {'PASS', 'FAIL', 'NOT_RUN', 'NOT_APPLICABLE', 'DEFERRED'}
    seen = set()
    if data.get('rules_count') != len(catalog) or not isinstance(data.get('project'), str) or data.get('project') != 'local-project':
        raise ValueError('Evidence project label or rule count is invalid.')
    for row in data['results']:
        if not isinstance(row, dict) or row.get('status') not in valid or not isinstance(row.get('rule_id'), str):
            raise ValueError('Evidence contains an invalid result row or status.')
        if set(row) != {'rule_id', 'title', 'status', 'mandatory', 'stage', 'evidence', 'duration_ms'}:
            raise ValueError('Evidence row contains unsupported fields.')
        if row['rule_id'] in seen:
            raise ValueError('Evidence contains duplicate rule IDs.')
        seen.add(row['rule_id'])
        if not isinstance(row.get('mandatory'), bool) or not isinstance(row.get('evidence'), str):
            raise ValueError('Evidence row is missing mandatory status/evidence fields.')
        rule = next((item for item in catalog if item['id'] == row['rule_id']), None)
        if rule is None or row['mandatory'] != expected_rules[row['rule_id']] or row.get('title') != rule['title'] or row.get('stage') != rule['stage']:
            raise ValueError('Evidence rule identity/mandatory status does not match the release catalog.')
        if (not isinstance(row.get('duration_ms'), (int, float)) or not math.isfinite(row['duration_ms'])
                or row['duration_ms'] < 0 or row['duration_ms'] > 3_600_000):
            raise ValueError('Evidence duration is invalid.')
        if len(row['evidence']) > 4096:
            raise ValueError('Evidence text exceeds the safe report limit.')
    if seen != set(expected_rules):
        raise ValueError('Evidence does not preserve every rule in the release catalog.')
    blocked = sorted(row['rule_id'] for row in data['results'] if data['mode'] == 'FULL' and row['mandatory'] and row['status'] in ('FAIL', 'NOT_RUN', 'DEFERRED'))
    if data.get('blocking_rule_ids') != blocked:
        raise ValueError('Evidence blocker list does not match rule statuses.')
    expected = data['mode'] == 'FULL' and not blocked
    if data.get('qualifies_release') is not expected:
        raise ValueError('Evidence release claim contradicts recorded statuses.')
    if project_root is None:
        raise ValueError('Imported evidence cannot be accepted without replaying checks against --project.')
    root = Path(project_root).resolve()
    fresh = run_check(root, full=data['mode'] == 'FULL')
    if data.get('project_manifest_sha256') != fresh.get('project_manifest_sha256'):
        raise ValueError('Project manifest has changed since evidence was generated; use the fresh local run.')
    saved_rows = {row['rule_id']: row for row in data['results']}
    for row in fresh['results']:
        old = saved_rows[row['rule_id']]
        if any(old[key] != row[key] for key in ('title', 'status', 'mandatory', 'stage')):
            raise ValueError(f"Imported status for {row['rule_id']} does not match a fresh local replay.")
    if data.get('blocking_rule_ids') != fresh['blocking_rule_ids'] or data.get('qualifies_release') != fresh['qualifies_release']:
        raise ValueError('Imported release claim does not match a fresh local replay.')
    return fresh


if __name__ == '__main__':
    raise SystemExit(main())
