#!/usr/bin/env python3
"""Run allowlisted project tests and emit a small machine-readable count.

The runner is part of Golden, not the project under test. It captures test
output and reports only counts so empty or all-skipped suites cannot be
mistaken for accepted test execution.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import unittest

MARKER = 'GOLDEN_TEST_RESULT='


class PytestCounts:
    def __init__(self) -> None:
        self.passed = 0
        self.skipped = 0
        self.failed = 0
        self.errors = 0

    def pytest_runtest_logreport(self, report) -> None:
        if report.when == 'call':
            if report.passed:
                self.passed += 1
            elif report.skipped:
                self.skipped += 1
            elif report.failed:
                self.failed += 1
        elif report.when in ('setup', 'teardown') and report.failed:
            self.errors += 1

    def pytest_collectreport(self, report) -> None:
        if report.failed:
            self.errors += 1


def emit(summary: dict, exit_code: int) -> int:
    print(MARKER + json.dumps(summary, sort_keys=True, separators=(',', ':')))
    return exit_code


def run_unittest() -> int:
    loader = unittest.TestLoader()
    try:
        suite = loader.discover('tests', pattern='test*.py')
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0, buffer=True).run(suite)
    except Exception:
        return emit({
            'framework': 'unittest', 'tests_run': 0, 'passed': 0,
            'skipped': 0, 'failed': 0, 'errors': 1, 'unexpected_successes': 0,
        }, 1)

    failed = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    expected_failures = len(result.expectedFailures)
    unexpected_successes = len(result.unexpectedSuccesses)
    passed = max(0, result.testsRun - failed - errors - skipped - expected_failures - unexpected_successes)
    summary = {
        'framework': 'unittest', 'tests_run': result.testsRun, 'passed': passed,
        'skipped': skipped, 'failed': failed, 'errors': errors,
        'unexpected_successes': unexpected_successes,
    }
    accepted = result.testsRun > 0 and passed > 0 and failed == 0 and errors == 0 and unexpected_successes == 0
    return emit(summary, 0 if accepted else 1)


def run_pytest() -> int:
    try:
        import pytest
    except ImportError:
        return emit({
            'framework': 'pytest', 'tests_run': 0, 'passed': 0,
            'skipped': 0, 'failed': 0, 'errors': 1,
        }, 1)

    counts = PytestCounts()
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            exit_code = int(pytest.main(['-q', '-p', 'no:cacheprovider'], plugins=[counts]))
    except Exception:
        return emit({
            'framework': 'pytest',
            'tests_run': counts.passed + counts.skipped + counts.failed + counts.errors,
            'skipped': counts.skipped, 'failed': counts.failed, 'errors': counts.errors + 1,
        }, 1)

    summary = {
        'framework': 'pytest', 'tests_run': counts.passed + counts.skipped + counts.failed + counts.errors,
        'passed': counts.passed,
        'skipped': counts.skipped, 'failed': counts.failed, 'errors': counts.errors,
        'pytest_exit_code': exit_code,
    }
    accepted = (exit_code == 0 and summary['tests_run'] > 0 and counts.passed > 0
                and counts.failed == 0 and counts.errors == 0)
    return emit(summary, 0 if accepted else (exit_code or 1))


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in ('unittest', 'pytest'):
        return 2
    project_root = os.getcwd()
    sys.path.insert(0, project_root)
    return run_unittest() if sys.argv[1] == 'unittest' else run_pytest()


if __name__ == '__main__':
    raise SystemExit(main())
