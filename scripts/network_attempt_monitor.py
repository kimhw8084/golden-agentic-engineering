#!/usr/bin/env python3
"""Verify Python socket-attempt instrumentation blocks before connecting."""
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
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.1)
    sock.connect(("203.0.113.1", 443))
    outcome = "unexpectedly_connected"
except PermissionError:
    outcome = "blocked"
except OSError as exc:
    outcome = "blocked_by_local_environment"
    os_error_type = type(exc).__name__
finally:
    if "sock" in locals():
        sock.close()
print(json.dumps({"attempts": attempts, "outcome": outcome, "os_error_type": locals().get("os_error_type")}))
'''


def run_probe() -> dict:
    env = {'PYTHONNOUSERSITE': '1', 'PYTHONPATH': ''}
    # Windows needs its system root and temp paths for Winsock/runtime APIs.
    # Proxy variables are intentionally not inherited by this direct socket probe.
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
            'Expected at least one direct socket attempt observed and blocked by the audit hook; '
            f'observed={attempt_count} outcome={result.get("outcome", "missing")!r} '
            f'os_error_type={result.get("os_error_type", "none")!r}.'
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
