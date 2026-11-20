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
import json
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
        return f"golden_version mismatch: expected pinned {version!r}, found {data['golden_version']!r}."
    if not isinstance(data['capabilities'], dict) or any(not isinstance(v, bool) for v in data['capabilities'].values()):
        return 'capabilities must be an object of booleans.'
    if not isinstance(data['commands'], dict):
        return 'commands must be an object.'
    for key, command in data['commands'].items():
        if not isinstance(key, str) or not isinstance(command, list) or not command or not all(isinstance(v, str) and v for v in command):
            return f'commands.{key} must be a nonempty array of strings.'
    return None


def approved_command(key: str, command: list[str]) -> tuple[bool, str]:
    """Allow a small set of deterministic test invocations; never execute arbitrary project argv."""
    if not command or not all(isinstance(part, str) and part for part in command):
        return False, 'Command must be a nonempty string array.'
    executable = command[0].lower()
    args = command[1:]
    py = executable in ('${python}', 'python', 'python3', 'py')
    npm = executable in ('npm', 'pnpm')
    if key == 'python_tests' and py:
        if args in (['-m', 'unittest', 'discover', '-s', 'tests', '-v'], ['-m', 'pytest', '-q']):
            return True, 'python test runner allowlist'
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
        return 'NOT_APPLICABLE', f"Criticality {project['criticality']!r} not in {levels!r}; based on the project manifest."
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
                errors.append(f'{p.relative_to(root)}: {exc}')
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
    command_hash = hashlib.sha256(json.dumps(cmd, separators=(',', ':')).encode()).hexdigest()
    program = cmd[0]
    if program == '${PYTHON}':
        cmd = [sys.executable] + cmd[1:]
        program = cmd[0]
    if not shutil.which(program):
        return 'NOT_RUN', f'Executable unavailable: {program}.'
    try:
        p = subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=min(max(timeout, 1), 600), shell=False, check=False)
        output = ((p.stdout or '') + '\n' + (p.stderr or '')).strip()
        output_hash = hashlib.sha256(output.encode('utf-8', errors='replace')).hexdigest()
        # Never persist raw command output; it may contain credentials, source or internal paths.
        return ('PASS' if p.returncode == 0 else 'FAIL'), f'Exit={p.returncode}; {basis}; argv_sha256={command_hash}; output_bytes={len(output.encode("utf-8", errors="replace"))}; output_sha256={output_hash}'
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
        'project': project.get('name') or root.name,
        'mode': 'FULL' if full else 'FAST', 'qualifies_release': bool(full and not blocked),
        'blocking_rule_ids': blocked, 'rules_count': len(results), 'results': results,
        'disclaimer': 'Local deterministic evidence only. No human/company sign-off implied.'
    }
    return evidence


def render_report(data: dict) -> str:
    validate_evidence(data)
    rows = []
    for r in data['results']:
        cells = [r['rule_id'], r['status'], r['title'], r['evidence'], f"{r['duration_ms']} ms"]
        rows.append('<tr>' + ''.join('<td>' + html.escape(str(c)) + '</td>' for c in cells) + '</tr>')
    title = html.escape(str(data.get('project', 'Golden evidence')))
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Golden evidence</title><style>
    body{font:14px/1.5 system-ui,Arial;background:#fff;color:#111;margin:0 auto;padding:24px;max-width:1400px}
    h1{font-size:25px} .meta{color:#555}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #ccc;text-align:left;padding:9px;vertical-align:top}td{overflow-wrap:anywhere} th{background:#eee} .status{font-weight:700} .warn{border:2px solid #333;padding:12px} @media(max-width:700px){body{padding:12px;font-size:12px}td,th{padding:5px}}
    </style><h1>Golden Proof — ''' + title + '''</h1><p class="meta">Mode: ''' + html.escape(data['mode']) + ''' · Golden: ''' + html.escape(str(data['golden_version'])) + ''' · Evidence UTC: ''' + html.escape(data['generated_at_utc']) + '''</p><p class="warn">''' + ('Candidate local checks complete; still needs owner/company approval.' if data['qualifies_release'] else 'NOT RELEASE-QUALIFIED — failed, unrun or deferred checks may exist.') + '''</p><p class="meta">Imported JSON and this HTML are not signed. The renderer checks structure and consistency, not execution authenticity. Re-run checks locally before relying on results.</p><table><thead><tr><th>ID</th><th>Status</th><th>Rule</th><th>Evidence</th><th>Duration</th></tr></thead><tbody>''' + '\n'.join(rows) + '''</tbody></table><p class="meta">Standalone report. No external assets, no server.</p></html>'''


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
    p = sub.add_parser('report'); p.add_argument('--input', type=Path, required=True); p.add_argument('--out', type=Path, required=True)
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
        print('Golden version:', release['version']); print('Python:', sys.version.split()[0]); print('Project:', root.name)
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
            validate_evidence(data)
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(render_report(data), encoding='utf-8')
            print('HTML report:', args.out)
            return 0
        except (OSError, ValueError, KeyError) as exc:
            print(str(exc), file=sys.stderr); return 2
    return 2


def validate_evidence(data: object) -> None:
    """Reject malformed or internally contradictory imported evidence; this is not a signature check."""
    if not isinstance(data, dict) or data.get('schema') != 'golden-evidence/v0.1':
        raise ValueError('Unsupported Golden evidence schema.')
    if data.get('mode') not in ('FAST', 'FULL') or not isinstance(data.get('results'), list):
        raise ValueError('Evidence mode/results are invalid.')
    release = read_json(VERSION)
    catalog = read_json(RULES)['rules']
    expected_rules = {row['id']: row['mandatory'] for row in catalog}
    if data.get('golden_version') != release['version'] or data.get('rules_sha256') != digest(RULES):
        raise ValueError('Evidence release/rule catalog pin is stale or invalid.')
    valid = {'PASS', 'FAIL', 'NOT_RUN', 'NOT_APPLICABLE', 'DEFERRED'}
    seen = set()
    for row in data['results']:
        if not isinstance(row, dict) or row.get('status') not in valid or not isinstance(row.get('rule_id'), str):
            raise ValueError('Evidence contains an invalid result row or status.')
        if row['rule_id'] in seen:
            raise ValueError('Evidence contains duplicate rule IDs.')
        seen.add(row['rule_id'])
        if not isinstance(row.get('mandatory'), bool) or not isinstance(row.get('evidence'), str):
            raise ValueError('Evidence row is missing mandatory status/evidence fields.')
        if row['rule_id'] not in expected_rules or row['mandatory'] != expected_rules[row['rule_id']]:
            raise ValueError('Evidence rule identity/mandatory status does not match the release catalog.')
    if seen != set(expected_rules):
        raise ValueError('Evidence does not preserve every rule in the release catalog.')
    blocked = sorted(row['rule_id'] for row in data['results'] if data['mode'] == 'FULL' and row['mandatory'] and row['status'] in ('FAIL', 'NOT_RUN', 'DEFERRED'))
    if data.get('blocking_rule_ids') != blocked:
        raise ValueError('Evidence blocker list does not match rule statuses.')
    expected = data['mode'] == 'FULL' and not blocked
    if data.get('qualifies_release') is not expected:
        raise ValueError('Evidence release claim contradicts recorded statuses.')


if __name__ == '__main__':
    raise SystemExit(main())
