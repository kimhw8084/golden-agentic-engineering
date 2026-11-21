import importlib.util
import io
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('golden_control', ROOT / 'scripts' / 'golden_control.py')
control = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(control)


class GoldenControlUITests(unittest.TestCase):
    def test_project_agent_status_is_config_evidence_not_runtime_proof(self):
        status = control.project_agent_configuration()
        self.assertEqual(status, {
            'status': 'CONFIGURED', 'agent': 'golden-engineer',
            'config_path': '.opencode/opencode.json', 'runtime_selection': 'NOT_TESTED',
            'evidence_scope': 'CHECKED_IN_CONFIG_ONLY',
        })

    def test_local_page_and_task_route_api_are_served(self):
        class Request:
            def __init__(self, path):
                self.path = path
                self.wfile = io.BytesIO()
                self.response = None
                self.headers = {}

            def send_response(self, status):
                self.response = status

            def send_header(self, name, value):
                self.headers[name] = value

            def end_headers(self):
                pass

            def _send_file(self, path, content_type):
                self.response = 200
                self.content_type = content_type
                self.wfile.write(path.read_bytes())

            def send_error(self, status):
                self.response = status

        page = Request('/')
        control.ControlHandler.do_GET(page)
        self.assertEqual(page.response, 200)
        self.assertIn('TASK ROUTING', page.wfile.getvalue().decode('utf-8'))
        self.assertIn('COMPANY_START_HERE.md', page.wfile.getvalue().decode('utf-8'))
        self.assertIn('PROJECT CONFIGURATION', page.wfile.getvalue().decode('utf-8'))
        self.assertIn('projectAgentStatus', page.wfile.getvalue().decode('utf-8'))
        app = (ROOT / 'control' / 'app.js').read_text(encoding='utf-8')
        self.assertIn('Capability candidates require separate review', app)
        self.assertIn('Full route details', app)
        self.assertIn('No-AI fallback', app)
        self.assertIn('Conditional specialists', app)
        self.assertIn('item.resolved_primary_agent', app)
        self.assertIn('build version and company compatibility are unknown', app)
        self.assertIn('OPENCODE PATH', page.wfile.getvalue().decode('utf-8'))
        self.assertIn('capability-selection.json', page.wfile.getvalue().decode('utf-8'))
        self.assertIn('capabilitySearch', page.wfile.getvalue().decode('utf-8'))
        self.assertIn('capabilityTypeFilter', page.wfile.getvalue().decode('utf-8'))
        self.assertIn('aria-live="polite"', page.wfile.getvalue().decode('utf-8'))
        self.assertIn('NOT APPROVED', page.wfile.getvalue().decode('utf-8'))
        self.assertIn('No public endpoint is contacted by this explorer', page.wfile.getvalue().decode('utf-8'))
        self.assertIn("fetch('/research/capability-selection.json'", app)
        self.assertIn('renderCapabilities', app)
        self.assertIn('Measured evidence', app)
        self.assertNotIn('innerHTML', app)
        styles = (ROOT / 'control' / 'styles.css').read_text(encoding='utf-8')
        self.assertIn('.panel .panel-link+.panel-link', styles)

        workflows = Request('/api/workflows')
        control.ControlHandler.do_GET(workflows)
        self.assertEqual(workflows.response, 200)
        payload = json.loads(workflows.wfile.getvalue())
        self.assertEqual(payload['schema'], 'golden-task-routing/v2')
        self.assertEqual(len(payload['workflows']), 12)
        docs_route = next(row for row in payload['workflows'] if row['id'] == 'technical-docs-sop-diagrams')
        self.assertEqual(docs_route['primary_agent'], 'primary')
        self.assertEqual(docs_route['resolved_primary_agent'], 'golden-engineer')
        self.assertEqual(docs_route['capability_candidates'], [
            'cathrynlavery-diagram-design', 'existing-markdown-svg-mermaid'])
        for field in ('context', 'deterministic_tools', 'specialists', 'trust', 'no_ai', 'outputs', 'mcp_policy'):
            self.assertIn(field, docs_route)

        capabilities = Request('/research/capability-selection.json')
        control.ControlHandler.do_GET(capabilities)
        self.assertEqual(capabilities.response, 200)
        registry = json.loads(capabilities.wfile.getvalue())
        self.assertEqual(len(registry['candidates']), 35)
        self.assertEqual(len(registry['task_decisions']), 18)
        self.assertIn('vercel-agent-browser', {row['id'] for row in registry['candidates']})
        self.assertIn('chrome-devtools-mcp', {row['id'] for row in registry['candidates']})
        self.assertIn('browser-use', {row['id'] for row in registry['candidates']})
        self.assertIn('inspect-ai', {row['id'] for row in registry['candidates']})
        self.assertIn('github-github-mcp-server', {row['id'] for row in registry['candidates']})
        self.assertIn('shadcn-ui-agent-skill', {row['id'] for row in registry['candidates']})
        self.assertIn('shadcn-ui-mcp-server', {row['id'] for row in registry['candidates']})
        required_evidence = {
            'capability_type', 'owner_repo', 'commit', 'license', 'license_evidence',
            'transitive_dependencies', 'windows_linux', 'offline_telemetry',
            'context_cost', 'permissions', 'prompt_injection_security',
            'measured_evidence', 'decision',
        }
        self.assertTrue(all(required_evidence.issubset(row) for row in registry['candidates']))
        diagram = next(row for row in registry['candidates'] if row['id'] == 'cathrynlavery-diagram-design')
        self.assertEqual(diagram['decision'], 'EVALUATION_ONLY_NOT_APPROVED')


if __name__ == '__main__':
    unittest.main()
