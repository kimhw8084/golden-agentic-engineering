import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('synthetic_mcp_fixture', ROOT / 'integrations' / 'mcp' / 'synthetic_fixture.py')
fixture = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fixture)


class SyntheticMCPFixtureTests(unittest.TestCase):
    def test_discovery_and_read_only_tool_call(self):
        init = fixture.handle({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {'protocolVersion': '2025-11-25'}})
        self.assertEqual(init['result']['capabilities'], {'tools': {}})
        unsupported = fixture.handle({'jsonrpc': '2.0', 'id': 99, 'method': 'initialize', 'params': {'protocolVersion': '2026-07-28'}})
        self.assertEqual(unsupported['error']['code'], -32602)
        tools = fixture.handle({'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'})['result']['tools']
        self.assertEqual([t['name'] for t in tools], ['read_synthetic_sample'])
        result = fixture.handle({'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call', 'params': {'name': 'read_synthetic_sample', 'arguments': {'fixture_id': 'fixture-001'}}})
        self.assertEqual(result['result']['structuredContent']['value'], 12.5)
        self.assertTrue(tools[0]['annotations']['readOnlyHint'])

    def test_scope_errors_injection_payload_is_data(self):
        result = fixture.handle({'jsonrpc': '2.0', 'id': 4, 'method': 'tools/call', 'params': {'name': 'read_synthetic_sample', 'arguments': {'fixture_id': 'fixture-001', 'path': '../../secret'}}})
        self.assertEqual(result['error']['code'], -32602)
        result = fixture.handle({'jsonrpc': '2.0', 'id': 5, 'method': 'tools/call', 'params': {'name': 'read_synthetic_sample', 'arguments': {'fixture_id': 'fixture-001'}}})
        note = result['result']['structuredContent']['untrusted_note']
        self.assertIn('Ignore previous directions', note)
        self.assertEqual(fixture.INJECTION_SAMPLE, note)

    def test_error_timeout_cancellation_and_unavailable(self):
        request = {'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call', 'params': {'name': 'read_synthetic_sample', 'arguments': {'fixture_id': 'fixture-001'}}}
        self.assertEqual(fixture.handle(request, unavailable=True)['result']['isError'], True)
        self.assertEqual(fixture.handle(request, cancelled=True)['error']['code'], -32800)
        self.assertEqual(fixture.handle(request, timeout=True)['error']['code'], -32001)
        self.assertEqual(fixture.handle({'jsonrpc': '2.0', 'id': 1, 'method': 'unknown'})['error']['code'], -32601)

    def test_stdio_is_local_json_lines_only(self):
        proc = subprocess.run([sys.executable, str(ROOT / 'integrations' / 'mcp' / 'synthetic_fixture.py')], input='{"jsonrpc":"2.0","id":1,"method":"tools/list"}\n', text=True, capture_output=True, timeout=3, check=True)
        self.assertEqual(json.loads(proc.stdout)['result']['tools'][0]['name'], 'read_synthetic_sample')
        self.assertEqual(proc.stderr, '')


if __name__ == '__main__':
    unittest.main()
