#!/usr/bin/env python3
"""Verify the Python socket.connect audit hook rejects a synthetic event."""
from __future__ import annotations

import json
import os
import subprocess
import sys

PROBE = r'''
import json, sys
attempts = []
def audit(event, args):
    if event == "socket.connect":
        attempts.append(args[1])
        raise PermissionError("blocked by test audit hook")
sys.addaudithook(audit)
try:
    sys.audit("socket.connect", object(), ("203.0.113.1", 443))
    outcome = "unexpectedly_allowed"
except PermissionError:
    outcome = "blocked"
print(json.dumps({"attempts": attempts, "outcome": outcome}))
'''


def run_probe() -> dict:
    env = {'PYTHONNOUSERSITE': '1', 'PYTHONPATH': ''}
    # Python 3.10 on Windows needs these OS paths even though the probe is isolated.
    for key in ('SYSTEMROOT', 'WINDIR', 'TEMP', 'TMP'):
        value = os.environ.get(key)
        if value:
            env[key] = value
    child = subprocess.run([sys.executable, '-S', '-c', PROBE], capture_output=True, text=True, timeout=3, check=False,
                           env=env)
    if child.returncode != 0:
        raise RuntimeError('Probe subprocess failed; output omitted.')
    result = json.loads(child.stdout)
    attempt_count = len(result.get('attempts', []))
    if attempt_count < 1 or result.get('outcome') != 'blocked':
        raise RuntimeError(
            'Expected a synthetic socket.connect audit event to be observed and blocked; '
            f'observed={attempt_count} outcome={result.get("outcome", "missing")!r} '
            'no socket operation is performed by this probe.'
        )
    return result


def main() -> int:
    try:
        result = run_probe()
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError):
        print('NETWORK_ATTEMPT_MONITOR_FAIL')
        return 2
    print(f"NETWORK_AUDIT_HOOK_PASS observed={len(result['attempts'])} blocked=true synthetic_event=true no_socket_operation=true")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
