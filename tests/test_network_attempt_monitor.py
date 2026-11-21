import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('network_attempt_monitor', ROOT / 'scripts' / 'network_attempt_monitor.py')
monitor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(monitor)


class NetworkAttemptMonitorTests(unittest.TestCase):
    def test_synthetic_socket_connect_audit_event_is_observed_and_blocked(self):
        result = monitor.run_probe()
        self.assertGreaterEqual(len(result['attempts']), 1)
        self.assertEqual(result['outcome'], 'blocked')


if __name__ == '__main__':
    unittest.main()
