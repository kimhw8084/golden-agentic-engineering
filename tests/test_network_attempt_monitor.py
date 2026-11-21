import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('network_attempt_monitor', ROOT / 'scripts' / 'network_attempt_monitor.py')
monitor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(monitor)


class NetworkAttemptMonitorTests(unittest.TestCase):
    def test_loopback_socket_connect_call_is_observed_and_blocked_before_socket_operation(self):
        result = monitor.run_probe()
        self.assertEqual(result['attempts'], [['127.0.0.1', 9]])
        self.assertEqual(result['outcome'], 'blocked_before_socket_operation')


if __name__ == '__main__':
    unittest.main()
