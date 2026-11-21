#!/usr/bin/env python3
"""Verify Python socket-attempt instrumentation blocks before connecting."""
from __future__ import annotations

import json
import subprocess
import sys

PROBE = r'''
import json, socket, sys
attempts = []
def audit(event, args):
    if event == "socket.connect":
        attempts.append(args[1])
        raise PermissionError("blocked by test audit hook")
sys.addaudithook(audit)
try:
    socket.create_connection(("203.0.113.1", 443), timeout=0.1)
    outcome = "unexpectedly_connected"
except PermissionError:
    outcome = "blocked"
except OSError as exc:
    outcome = "blocked_by_local_environment"
print(json.dumps({"attempts": attempts, "outcome": outcome}))
'''


def run_probe() -> dict:
    child = subprocess.run([sys.executable, '-S', '-c', PROBE], capture_output=True, text=True, timeout=3, check=False,
                           env={'PATH': '', 'PYTHONNOUSERSITE': '1', 'PYTHONPATH': ''})
    if child.returncode != 0:
        raise RuntimeError('Probe subprocess failed; output omitted.')
    result = json.loads(child.stdout)
    attempt_count = len(result.get('attempts', []))
    if attempt_count < 1 or result.get('outcome') != 'blocked':
        raise RuntimeError(
            'Expected at least one audit-hook-observed attempt blocked before connect; '
            f'observed={attempt_count} outcome={result.get("outcome", "missing")!r}.'
        )
    return result


def main() -> int:
    try:
        result = run_probe()
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError):
        print('NETWORK_ATTEMPT_MONITOR_FAIL')
        return 2
    print(f"NETWORK_ATTEMPT_MONITOR_PASS observed={len(result['attempts'])} blocked_before_os_connect=true destination=reserved-documentation-ip")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
