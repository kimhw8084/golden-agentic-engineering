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


if __name__ == '__main__':
    unittest.main()
