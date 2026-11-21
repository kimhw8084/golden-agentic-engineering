import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
SPEC = importlib.util.spec_from_file_location('validate_manifests', ROOT / 'scripts' / 'validate_manifests.py')
validate_manifests = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate_manifests)
REGISTRY = json.loads((ROOT / 'research' / 'capability-selection.json').read_text())
SCHEMA = json.loads((ROOT / 'schemas' / 'capability-selection.schema.json').read_text())


class CapabilitySchemaTests(unittest.TestCase):
    def test_registry_types_are_explicit_across_agentic_and_tool_classes(self):
        errors = validate_manifests.validate_capability_types(REGISTRY, SCHEMA)
        self.assertEqual(errors, [])
        kinds = {candidate['capability_type'] for candidate in REGISTRY['candidates']}
        self.assertTrue({'agent_skill', 'opencode_plugin', 'agent_workflow', 'agent_framework',
                         'mcp_server', 'mcp_sdk', 'browser_tool', 'evaluation_system',
                         'deterministic_cli'} <= kinds)

    def test_missing_capability_type_fails_closed(self):
        registry = copy.deepcopy(REGISTRY)
        del registry['candidates'][0]['capability_type']
        errors = validate_manifests.validate_capability_types(registry, SCHEMA)
        self.assertTrue(any('capability_type missing or invalid' in error for error in errors))

    def test_unknown_capability_type_fails_closed(self):
        registry = copy.deepcopy(REGISTRY)
        registry['candidates'][0]['capability_type'] = 'unreviewed_runtime'
        errors = validate_manifests.validate_capability_types(registry, SCHEMA)
        self.assertTrue(any('unknown capability_type' in error for error in errors))

    def test_registry_and_schema_identifiers_must_match(self):
        registry = copy.deepcopy(REGISTRY)
        registry['schema'] = 'golden-capability-selection/v999'
        errors = validate_manifests.validate_capability_types(registry, SCHEMA)
        self.assertTrue(any('does not match its JSON Schema' in error for error in errors))

    def test_schema_required_candidate_evidence_is_enforced(self):
        registry = copy.deepcopy(REGISTRY)
        del registry['candidates'][0]['license_evidence']
        errors = validate_manifests.validate_capability_types(registry, SCHEMA)
        self.assertTrue(any('license_evidence missing or invalid' in error for error in errors))

    def test_malformed_schema_bounds_fail_closed_without_crashing(self):
        schema = copy.deepcopy(SCHEMA)
        schema['properties']['candidates']['minItems'] = 'not-a-number'
        errors = validate_manifests.validate_capability_types(REGISTRY, schema)
        self.assertTrue(any('invalid root/candidate fields' in error for error in errors))


if __name__ == '__main__':
    unittest.main()
