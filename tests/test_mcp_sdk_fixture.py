import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SDK_AVAILABLE = importlib.util.find_spec("mcp") is not None and importlib.util.find_spec("mcp_types") is not None


@unittest.skipUnless(SDK_AVAILABLE, "optional official MCP Python SDK v2 candidate is not installed")
class MCPSDKFixtureTests(unittest.TestCase):
    def test_stdio_discovery_and_read_only_sample_call(self):
        from mcp.client.session import ClientSession
        from mcp.client.stdio import StdioServerParameters, stdio_client
        import anyio

        async def exercise():
            params = StdioServerParameters(command=sys.executable, args=[str(ROOT / "integrations" / "mcp" / "sdk_synthetic_fixture.py")], cwd=str(ROOT))
            async with stdio_client(params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    initialized = await session.initialize()
                    tools = await session.list_tools()
                    sample = await session.call_tool("read_synthetic_sample", {"fixture_id": "fixture-001"})
                    bad_scope = await session.call_tool("read_synthetic_sample", {"fixture_id": "other"})
            return initialized, tools, sample, bad_scope

        initialized, tools, sample, bad_scope = anyio.run(exercise)
        self.assertEqual(initialized.server_info.name, "golden-synthetic-sdk-fixture")
        self.assertEqual([tool.name for tool in tools.tools], ["read_synthetic_sample"])
        self.assertTrue(tools.tools[0].annotations.read_only_hint)
        self.assertFalse(tools.tools[0].annotations.open_world_hint)
        self.assertEqual(sample.structured_content["value"], 12.5)
        self.assertIn("Ignore previous directions", sample.structured_content["untrusted_note"])
        self.assertTrue(bad_scope.is_error)


if __name__ == "__main__":
    unittest.main()
