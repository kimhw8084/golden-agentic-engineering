#!/usr/bin/env python3
"""Run deterministic local acceptance fixtures without third-party installs or network."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import re
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
        return {
            'id': case_id,
            'status': 'PASS' if result.returncode == 0 and found else 'FAIL',
            'tests_run': int(found.group(1)) if found else None,
            'elapsed_seconds': round(duration, 6),
            'command': ['python', '-S', '-m', 'unittest', 'discover', '-s', tests_directory,
                        '-p', selected_pattern, '-q'],
            'output_sha256': hashlib.sha256(summary.encode('utf-8', errors='replace')).hexdigest(),
        }
    except subprocess.TimeoutExpired:
        return {'id': case_id, 'status': 'TIMEOUT', 'tests_run': None, 'elapsed_seconds': 90.0,
                'command': ['python', '-S', '-m', 'unittest', 'discover', '-s', tests_directory,
                            '-p', selected_pattern, '-q'],
                'output_sha256': None}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='Optional JSON result path; no test logs are saved.')
    args = parser.parse_args()
    report = {
        'schema': 'golden-local-fixture-run/v1',
        'generated_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'environment': {'os': platform.system(), 'architecture': platform.machine(),
                        'python': platform.python_version()},
        'network_policy': 'No package manager or network-capable application is launched by this harness; all test processes use offline-related environment flags.',
        'cases': [run_case(case) for case in CASES],
        'react': {'status': 'BLOCKED_MISSING_LOCKFILE_AND_OFFLINE_STORE',
                  'required_action': 'Stage an approved dependency lock and npm offline store before running React scripts.'},
        'browser': {'status': 'BLOCKED_MISSING_BROWSER_ASSETS',
                    'required_action': 'Stage approved Playwright browser binaries before UI journey/accessibility tests.'},
        'scope': 'Local deterministic fixture tests only; not an agent comparison, company OpenCode run, or productivity benchmark.',
    }
    report['status'] = 'PASS' if all(row['status'] == 'PASS' for row in report['cases']) else 'FAIL'
    text = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding='utf-8')
    for row in report['cases']:
        count = row['tests_run'] if row['tests_run'] is not None else 'unknown'
        print(f"{row['status']} {row['id']} tests={count} elapsed_seconds={row['elapsed_seconds']:.6f}")
    print(f"{report['status']} local fixture run; React={report['react']['status']}; browser={report['browser']['status']}; company runtime remains untested")
    return 0 if report['status'] == 'PASS' else 2


if __name__ == '__main__':
    raise SystemExit(main())
