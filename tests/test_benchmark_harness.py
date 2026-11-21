from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'golden_local_fixtures', ROOT / 'benchmarks' / 'run_local_fixtures.py'
)
assert SPEC and SPEC.loader
HARNESS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HARNESS)


class ReactHarnessTests(unittest.TestCase):
    def test_react_runner_forces_offline_install_and_runs_all_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            lock = root / 'examples' / 'react-app' / 'package-lock.json'
            lock.parent.mkdir(parents=True)
            lock.write_text(json.dumps({'lockfileVersion': 3}))
            responses = [
                subprocess.CompletedProcess([], 0, '', ''),
                subprocess.CompletedProcess([], 0, '', ''),
                subprocess.CompletedProcess([], 0, '', '\x1b[2m Tests \x1b[0m\x1b[1m6 passed\x1b[0m (6)'),
                subprocess.CompletedProcess([], 0, '', ''),
            ]
            with patch.object(HARNESS, 'ROOT', root):
                with patch.object(HARNESS.shutil, 'which', return_value='/usr/bin/npm'):
                    with patch.object(HARNESS.subprocess, 'run', side_effect=responses) as run:
                        result = HARNESS.run_react()
            self.assertEqual(result['status'], 'PASS')
            self.assertEqual(result['tests_run'], 6)
            self.assertEqual(run.call_count, 4)
            install = run.call_args_list[0]
            self.assertIn('--offline', install.args[0])
            self.assertIn('--ignore-scripts', install.args[0])
            self.assertFalse(install.kwargs.get('shell', False))
            self.assertEqual(install.kwargs['env']['npm_config_offline'], 'true')

    def test_react_runner_does_not_claim_missing_lock_as_a_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(HARNESS, 'ROOT', Path(directory)):
                result = HARNESS.run_react()
        self.assertEqual(result['status'], 'BLOCKED_MISSING_LOCKFILE')

    def test_nicegui_ui_runner_uses_only_installed_offline_pytest(self):
        completed = subprocess.CompletedProcess(
            [], 0, '.                                                                        [100%]\n1 passed in 0.5s\n', ''
        )
        with patch.object(HARNESS, 'ROOT', Path('/synthetic/golden')):
            with patch.object(HARNESS.importlib.util, 'find_spec', return_value=object()):
                with patch.object(HARNESS.importlib.metadata, 'version', side_effect=lambda name: {'nicegui': '3.15.0', 'pytest': '8.4.2'}[name]):
                    with patch.object(HARNESS.subprocess, 'run', return_value=completed) as run:
                        result = HARNESS.run_nicegui_ui()
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['tests_run'], 1)
        self.assertEqual(result['versions'], {'nicegui': '3.15.0', 'pytest': '8.4.2'})
        command = run.call_args.args[0]
        self.assertIn('-m', command)
        self.assertIn('pytest', command)
        self.assertIn('tests/test_ui.py', command)
        self.assertEqual(run.call_args.kwargs['env']['PYTEST_DISABLE_PLUGIN_AUTOLOAD'], '1')
        self.assertEqual(run.call_args.kwargs['env']['PIP_NO_INDEX'], '1')
        self.assertFalse(run.call_args.kwargs.get('shell', False))

    def test_nicegui_ui_runner_reports_missing_packages_without_installing(self):
        with patch.object(HARNESS.importlib.util, 'find_spec', side_effect=lambda name: None if name == 'pytest' else object()):
            with patch.object(HARNESS.subprocess, 'run') as run:
                result = HARNESS.run_nicegui_ui()
        self.assertEqual(result['status'], 'NOT_RUN_DEPENDENCIES_UNAVAILABLE')
        self.assertEqual(result['missing'], ['pytest'])
        run.assert_not_called()

    def test_python_runner_reports_optional_skips_separately(self):
        completed = subprocess.CompletedProcess(
            [], 0, '', 'Ran 4 tests in 0.1s\n\nOK (skipped=1)\n'
        )
        with patch.object(HARNESS, 'ROOT', Path('/synthetic/golden')):
            with patch.object(HARNESS.subprocess, 'run', return_value=completed):
                result = HARNESS.run_case(('nicegui-logic', 'examples/nicegui-app', 'examples/nicegui-app/tests'))
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['tests_run'], 4)
        self.assertEqual(result['tests_passed'], 3)
        self.assertEqual(result['tests_skipped'], 1)


class BenchmarkCaseManifestTests(unittest.TestCase):
    def test_case_statuses_match_committed_local_evidence(self):
        cases = json.loads((ROOT / 'benchmarks' / 'cases.json').read_text(encoding='utf-8'))
        tasks = {task['id']: task for task in cases['tasks']}

        self.assertEqual(cases['status'], 'LOCAL_FIXTURES_EXECUTED_COMPANY_RUNTIME_COMPARISON_BLOCKED')
        self.assertEqual(tasks['react-feature']['local_fixture_status'], 'PASS_MACOS_ARM64')
        self.assertIn('local-fixtures.json#/react', tasks['react-feature']['evidence'][0])
        self.assertEqual(tasks['browser-verification']['local_fixture_status'], 'PARTIAL_MANUAL_REACT_AND_NICEGUI_SMOKES')
        self.assertEqual(tasks['browser-verification']['automated_browser_status'], 'NOT_RUN_PLAYWRIGHT_ASSETS_NOT_STAGED')
        self.assertTrue(all((ROOT / evidence).is_file() for evidence in tasks['browser-verification']['evidence']))
        self.assertEqual(tasks['nicegui-api-db']['ui_simulation_status'], 'PASS')
        self.assertTrue(any(reference.endswith('#/nicegui_ui') for reference in tasks['nicegui-api-db']['evidence']))
        local_fixtures = json.loads((ROOT / 'verification' / '2026-11-20' / 'local-fixtures.json').read_text())
        self.assertEqual(local_fixtures['nicegui_ui']['status'], 'PASS')
        self.assertEqual(local_fixtures['nicegui_ui']['tests_run'], 1)


if __name__ == '__main__':
    unittest.main()
