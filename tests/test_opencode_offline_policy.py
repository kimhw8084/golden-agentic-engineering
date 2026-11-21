import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class OpenCodeOfflinePolicyTests(unittest.TestCase):
    def test_project_configs_deny_public_web_tools_and_keep_mcp_disabled(self):
        for relative in ("opencode.json", ".opencode/opencode.json"):
            config = json.loads((ROOT / relative).read_text(encoding="utf-8"))
            denied = {(item.get("action"), item.get("resource"), item.get("effect"))
                      for item in config.get("permissions", [])}
            self.assertIn(("webfetch", "*", "deny"), denied, relative)
            self.assertIn(("websearch", "*", "deny"), denied, relative)
            servers = config.get("mcp", {}).get("servers", {})
            self.assertIs(servers["golden-synthetic-readonly"]["disabled"], True, relative)

    def test_egress_template_requires_catalog_disable_and_default_deny(self):
        template = json.loads((ROOT / "offline/egress-policy.template.json").read_text(encoding="utf-8"))
        self.assertEqual(template["enforcement"], "DEFAULT_DENY")
        self.assertEqual(template["allowed_destinations"], [])
        variables = template["required_opencode_environment"]["variables"]
        self.assertEqual(variables["OPENCODE_DISABLE_AUTOUPDATE"], "1")
        self.assertEqual(variables["OPENCODE_DISABLE_MODELS_FETCH"], "1")
        self.assertEqual(template["status"], "TEMPLATE_ONLY_NOT_APPLIED")


if __name__ == "__main__":
    unittest.main()
