#!/usr/bin/env python3
"""Verify a loopback socket.connect attempt is rejected by a Python audit hook."""
from __future__ import annotations

import json
import os
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
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect(("127.0.0.1", 9))
    outcome = "unexpectedly_allowed"
except PermissionError:
    outcome = "blocked_before_socket_operation"
except OSError as exc:
    outcome = "socket_operation_reached_" + type(exc).__name__
finally:
    sock.close()
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
    if (attempt_count != 1 or result.get('attempts') != [['127.0.0.1', 9]]
            or result.get('outcome') != 'blocked_before_socket_operation'):
        raise RuntimeError(
            'Expected one real loopback socket.connect call to be observed and blocked before the socket operation; '
            f'observed={attempt_count} outcome={result.get("outcome", "missing")!r} '
            'the probe never targets a public address.'
        )
    return result


def main() -> int:
    try:
        result = run_probe()
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError):
        print('NETWORK_ATTEMPT_MONITOR_FAIL')
        return 2
    print(f"NETWORK_LOOPBACK_AUDIT_INTERCEPT_PASS observed={len(result['attempts'])} blocked=true before_socket_operation=true public_network=false")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
