#!/usr/bin/env python3
"""Run deterministic local fixtures; React is optional and uses npm's offline cache."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CASES = [
    ('python-small-fix', 'examples/python-app', 'examples/python-app/tests'),
    ('nicegui-logic', 'examples/nicegui-app', 'examples/nicegui-app/tests'),
    ('api-sqlite-contract', '.', 'examples/scenarios/api_db'),
    ('incident-timeline', '.', 'examples/scenarios/incident'),
    ('manufacturing-sampling', '.', 'examples/scenarios/manufacturing'),
    ('mcp-synthetic-contract', '.', 'tests', 'test_mcp_fixture.py'),
    ('golden-proof', '.', 'tests', 'test_golden.py'),
    ('golden-routing', '.', 'tests', 'test_routing.py'),
]


def run_case(case: tuple[str, ...]) -> dict:
    case_id, working_directory, tests_directory, *pattern = case
    test_path = ROOT / tests_directory
    selected_pattern = pattern[0] if pattern else 'test_*.py'
    command = [sys.executable, '-S', '-m', 'unittest', 'discover', '-s', str(test_path), '-p', selected_pattern, '-q']
    env = {
        'PATH': os.environ.get('PATH', ''),
        'PYTHONNOUSERSITE': '1',
        'PYTHONDONTWRITEBYTECODE': '1',
        'PIP_NO_INDEX': '1',
        'UV_OFFLINE': '1',
        'npm_config_offline': 'true',
        'HF_HUB_OFFLINE': '1',
        'HF_HUB_DISABLE_TELEMETRY': '1',
        'DO_NOT_TRACK': '1',
    }
    started = time.perf_counter()
    try:
        result = subprocess.run(command, cwd=ROOT / working_directory, env=env,
                                capture_output=True, text=True, timeout=90, check=False)
        duration = time.perf_counter() - started
        summary = result.stdout + '\n' + result.stderr
        found = re.search(r'Ran (\d+) tests?', summary)
        skipped_match = re.search(r'OK \(skipped=(\d+)\)', summary)
        skipped = int(skipped_match.group(1)) if skipped_match else 0
        return {
            'id': case_id,
            'status': 'PASS' if result.returncode == 0 and found else 'FAIL',
            'tests_run': int(found.group(1)) if found else None,
            'tests_skipped': skipped,
            'tests_passed': max(0, int(found.group(1)) - skipped) if found else None,
            'elapsed_seconds': round(duration, 6),
            'command': ['python', '-S', '-m', 'unittest', 'discover', '-s', tests_directory,
                        '-p', selected_pattern, '-q'],
            'output_sha256': hashlib.sha256(summary.encode('utf-8', errors='replace')).hexdigest(),
        }
    except subprocess.TimeoutExpired:
        return {'id': case_id, 'status': 'TIMEOUT', 'tests_run': None, 'tests_passed': None,
                'tests_skipped': None, 'elapsed_seconds': 90.0,
                'command': ['python', '-S', '-m', 'unittest', 'discover', '-s', tests_directory,
                            '-p', selected_pattern, '-q'],
                'output_sha256': None}


def run_react() -> dict:
    package = ROOT / 'examples' / 'react-app'
    if not (package / 'package-lock.json').is_file():
        return {'status': 'BLOCKED_MISSING_LOCKFILE', 'required_action': 'Add and review the exact React lockfile.'}
    npm = shutil.which('npm')
    if not npm:
        return {'status': 'NOT_RUN_NPM_UNAVAILABLE', 'required_action': 'Run with an approved local Node/npm installation.'}
    commands = [
        ['ci', '--offline', '--ignore-scripts', '--no-audit', '--no-fund'],
        ['run', 'typecheck'],
        ['run', 'test'],
        ['run', 'build'],
    ]
    env = {
        'PATH': os.environ.get('PATH', ''),
        'PYTHONNOUSERSITE': '1',
        'npm_config_offline': 'true',
        'npm_config_fetch_retries': '0',
        'npm_config_fund': 'false',
        'npm_config_audit': 'false',
        'npm_config_update_notifier': 'false',
        'DO_NOT_TRACK': '1',
    }
    started = time.perf_counter()
    output_parts = []
    completed = []
    for args in commands:
        try:
            result = subprocess.run([npm, '--prefix', 'examples/react-app', *args],
                                    cwd=ROOT, env=env, capture_output=True, text=True,
                                    timeout=180, check=False)
        except subprocess.TimeoutExpired:
            return {'status': 'TIMEOUT', 'commands': completed + [args],
                    'elapsed_seconds': round(time.perf_counter() - started, 6)}
        output = result.stdout + '\n' + result.stderr
        output_parts.append(output)
        completed.append({'args': args, 'exit_code': result.returncode})
        if result.returncode:
            state = 'BLOCKED_OFFLINE_DEPENDENCIES' if args[0] == 'ci' else 'FAIL'
            return {'status': state, 'commands': completed,
                    'elapsed_seconds': round(time.perf_counter() - started, 6),
                    'output_sha256': hashlib.sha256(''.join(output_parts).encode('utf-8', errors='replace')).hexdigest()}
    summary = ''.join(output_parts)
    plain_summary = re.sub(r'\x1b\[[0-9;]*m', '', summary)
    match = re.search(r'Tests\s+(\d+)\s+passed', plain_summary, flags=re.IGNORECASE)
    return {'status': 'PASS', 'tests_run': int(match.group(1)) if match else None,
            'commands': completed, 'elapsed_seconds': round(time.perf_counter() - started, 6),
            'output_sha256': hashlib.sha256(summary.encode('utf-8', errors='replace')).hexdigest()}


def run_nicegui_ui() -> dict:
    missing = [name for name in ('nicegui', 'pytest') if importlib.util.find_spec(name) is None]
    if missing:
        return {'status': 'NOT_RUN_DEPENDENCIES_UNAVAILABLE', 'missing': missing,
                'required_action': 'Stage approved NiceGUI and pytest packages before requesting the UI simulation.'}
    versions = {}
    for name in ('nicegui', 'pytest'):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = 'UNKNOWN'

    command = [sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', 'tests/test_ui.py']
    env = {
        'PATH': os.environ.get('PATH', ''),
        'PYTHONNOUSERSITE': '1',
        'PYTEST_DISABLE_PLUGIN_AUTOLOAD': '1',
        'PYTEST_ADDOPTS': '',
        'PIP_NO_INDEX': '1',
        'UV_OFFLINE': '1',
        'DO_NOT_TRACK': '1',
    }
    started = time.perf_counter()
    try:
        result = subprocess.run(command, cwd=ROOT / 'examples' / 'nicegui-app', env=env,
                                capture_output=True, text=True, timeout=90, check=False)
    except subprocess.TimeoutExpired:
        return {'status': 'TIMEOUT', 'tests_run': None, 'elapsed_seconds': 90.0,
                'command': ['python', '-m', 'pytest', '-q', '-p', 'no:cacheprovider', 'tests/test_ui.py'],
                'output_sha256': None}
    summary = result.stdout + '\n' + result.stderr
    match = re.search(r'\b(\d+) passed\b', summary)
    passed = int(match.group(1)) if match else 0
    return {
        'status': 'PASS' if result.returncode == 0 and passed > 0 else 'FAIL',
        'tests_run': passed if passed else None,
        'versions': versions,
        'elapsed_seconds': round(time.perf_counter() - started, 6),
        'command': ['python', '-m', 'pytest', '-q', '-p', 'no:cacheprovider', 'tests/test_ui.py'],
        'output_sha256': hashlib.sha256(summary.encode('utf-8', errors='replace')).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='Optional JSON result path; no test logs are saved.')
    parser.add_argument('--include-react', action='store_true',
                        help='Run the React fixture using npm ci and npm scripts in offline mode.')
    parser.add_argument('--include-nicegui-ui', action='store_true',
                        help='Run the NiceGUI user_simulation test with already-installed packages; no browser or install is used.')
    args = parser.parse_args()
    react = run_react() if args.include_react else {
        'status': 'NOT_RUN_NOT_REQUESTED',
        'required_action': 'Pass --include-react to install from the local npm cache and run React checks offline.',
    }
    nicegui_ui = run_nicegui_ui() if args.include_nicegui_ui else {
        'status': 'NOT_RUN_NOT_REQUESTED',
        'required_action': 'Pass --include-nicegui-ui to run the in-process NiceGUI UI test with already-installed packages.',
    }
    report = {
        'schema': 'golden-local-fixture-run/v1',
        'generated_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'environment': {'os': platform.system(), 'architecture': platform.machine(),
                        'python': platform.python_version()},
        'network_policy': 'No fixture calls public services. Python unit tests run with site imports disabled; optional NiceGUI simulation uses in-process ASGI transport; optional React installation is forced offline. No model, browser, or provider is started.',
        'cases': [run_case(case) for case in CASES],
        'react': react,
        'nicegui_ui': nicegui_ui,
        'browser': {'status': 'NOT_RUN_PLAYWRIGHT_ASSETS_NOT_STAGED',
                    'required_action': 'Stage approved Playwright browser binaries before UI journey/accessibility tests.'},
        'scope': 'Local deterministic fixture tests only; optional React scripts are forced offline. Not an agent comparison, company OpenCode run, or productivity benchmark.',
    }
    cases_pass = all(row['status'] == 'PASS' for row in report['cases'])
    react_pass = not args.include_react or react.get('status') == 'PASS'
    nicegui_ui_pass = not args.include_nicegui_ui or nicegui_ui.get('status') == 'PASS'
    report['status'] = 'PASS' if cases_pass and react_pass and nicegui_ui_pass else 'FAIL'
    text = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding='utf-8')
    for row in report['cases']:
        count = row['tests_run'] if row['tests_run'] is not None else 'unknown'
        print(f"{row['status']} {row['id']} tests={count} elapsed_seconds={row['elapsed_seconds']:.6f}")
    react_tests = f" tests={report['react']['tests_run']}" if report['react'].get('tests_run') is not None else ''
    nicegui_tests = f" tests={report['nicegui_ui']['tests_run']}" if report['nicegui_ui'].get('tests_run') is not None else ''
    print(f"{report['status']} local fixture run; React={report['react']['status']}{react_tests}; NiceGUI_UI={report['nicegui_ui']['status']}{nicegui_tests}; browser={report['browser']['status']}; company runtime remains untested")
    return 0 if report['status'] == 'PASS' else 2


if __name__ == '__main__':
    raise SystemExit(main())
