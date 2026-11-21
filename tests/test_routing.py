import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('golden_route', ROOT / 'scripts' / 'golden_route.py')
golden_route = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(golden_route)


class TaskRoutingTests(unittest.TestCase):
    def test_runtime_resolves_only_selected_route_and_existing_skill(self):
        route = golden_route.route_for('browser-ui-verification')
        self.assertEqual(route['id'], 'browser-ui-verification')
        self.assertEqual({item['id'] for item in route['skills']}, {'golden-react', 'golden-nicegui'})
        self.assertEqual(route['mcp']['configured_for_route'], [])
        self.assertTrue(all((ROOT / item['path']).is_file() for item in route['skills']))
        self.assertEqual(route['mcp']['evaluation_candidates_only'], ['microsoft-playwright-mcp', 'chrome-devtools-mcp'])
        self.assertEqual(
            [item['id'] for item in route['capability_candidates']],
            ['vercel-agent-browser', 'microsoft-playwright-mcp', 'chrome-devtools-mcp',
             'browser-use', 'microsoft-playwright-python', 'microsoft-playwright-cli'],
        )
        self.assertTrue(route['capability_candidates'][0]['decision'].startswith(
            'EVALUATION_ONLY_POSSIBLE_AGENTIC_BROWSER_CANDIDATE'))
        self.assertEqual(route['capability_selection']['task'], 'local browser verification')
        self.assertIn('company-approved browser agent/MCP first', route['capability_selection']['current_choice'])
        self.assertIn('BLOCKED_COMPANY_RUNTIME_AND_BROWSER_ASSETS', route['capability_selection']['measurement'])

    def test_every_route_resolves_one_task_specific_capability_decision(self):
        data = json.loads((ROOT / 'workflows' / 'task-routing.json').read_text())
        decisions = {row['task'] for row in json.loads(
            (ROOT / 'research' / 'capability-selection.json').read_text())['task_decisions']}
        for row in data['workflows']:
            self.assertIn(row['selection_task'], decisions, row['id'])
            self.assertEqual(golden_route.route_for(row['id'])['capability_selection']['task'], row['selection_task'])

    def test_github_context_route_surfaces_only_the_disabled_internal_mcp_candidate(self):
        route = golden_route.route_for('golden-upstream-improvement')
        self.assertEqual(route['mcp']['configured_for_route'], [])
        self.assertEqual(route['mcp']['evaluation_candidates_only'], ['github-github-mcp-server'])
        candidate = next(item for item in route['capability_candidates']
                         if item['id'] == 'github-github-mcp-server')
        self.assertEqual(candidate['decision'], 'EVALUATION_CANDIDATE_READ_ONLY_INTERNAL_GHES_ONLY; NOT_STAGED_OR_APPROVED')
        self.assertIn('approved intranet GitHub Enterprise Server', route['mcp']['policy'])
        self.assertIn('read-only mode', route['capability_selection']['current_choice'])

    def test_github_enterprise_mcp_example_keeps_secret_external_and_server_disabled(self):
        config = json.loads((ROOT / 'integrations' / 'mcp' / 'github-enterprise-readonly.example.json').read_text())
        server = config['mcp']['servers']['github-enterprise-readonly']
        self.assertIs(server['disabled'], True)
        self.assertEqual(server['type'], 'local')
        self.assertEqual(server['command'][0], 'github-mcp-server')
        self.assertIn('--read-only', server['command'])
        self.assertIn('repos,issues,pull_requests,actions', server['command'])
        self.assertEqual(server['environment']['GITHUB_PERSONAL_ACCESS_TOKEN'], '{env:GITHUB_PERSONAL_ACCESS_TOKEN}')
        self.assertTrue(server['environment']['GITHUB_HOST'].endswith('.invalid'))

    def test_project_uses_golden_primary_and_small_fixes_skip_skill_loading(self):
        config = json.loads((ROOT / '.opencode' / 'opencode.json').read_text())
        agent = (ROOT / '.opencode' / 'agents' / 'golden-engineer.md').read_text()
        route = golden_route.route_for('small-fix')
        self.assertEqual(config['default_agent'], 'golden-engineer')
        self.assertIn('mode: primary', agent.split('---', 2)[1])
        self.assertEqual(route['primary_agent'], 'primary')
        self.assertEqual(route['skills'], [])

    def test_nontrivial_route_surfaces_skill_before_execution_tool_selection(self):
        route = golden_route.route_for('react-app-feature')
        self.assertEqual(route['skills'][0]['id'], 'golden-react')
        self.assertEqual(route['nontrivial_capability_order'], [
            'classify_task_and_risk', 'invoke_route_skill', 'check_relevant_agents_and_mcp',
            'choose_execution_tools', 'verify_deterministically',
        ])
        self.assertIn('one/few-file clear fixes', route['small_task_exception'])

    def test_project_default_agent_must_exist_and_be_primary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in ('workflows/task-routing.json', 'research/capability-selection.json', 'opencode.json'):
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, destination)
            shutil.copytree(ROOT / '.opencode', root / '.opencode')
            path = root / '.opencode' / 'opencode.json'
            config = json.loads(path.read_text())
            config['default_agent'] = 'missing-agent'
            path.write_text(json.dumps(config))
            self.assertTrue(any('default agent is missing locally' in error
                                for error in golden_route.validation_errors(root)))
            config['default_agent'] = 'golden-engineer'
            path.write_text(json.dumps(config))
            agent_path = root / '.opencode' / 'agents' / 'golden-engineer.md'
            agent_path.write_text(agent_path.read_text().replace('mode: primary', 'mode: subagent', 1))
            self.assertTrue(any('must declare mode: primary' in error
                                for error in golden_route.validation_errors(root)))

    def test_documentation_route_surfaces_diagram_design_as_unapproved_candidate(self):
        route = golden_route.route_for('technical-docs-sop-diagrams')
        self.assertEqual([item['id'] for item in route['skills']], ['golden-docs'])
        diagram = next(item for item in route['capability_candidates'] if item['id'] == 'cathrynlavery-diagram-design')
        self.assertEqual(diagram['owner_repo'], 'cathrynlavery/diagram-design')
        self.assertEqual(diagram['decision'], 'EVALUATION_ONLY_NOT_APPROVED')
        self.assertEqual(diagram['measured_evidence'], 'UNTESTED')

    def test_documentation_diagram_defaults_are_self_contained_and_offline(self):
        skill = (ROOT / '.opencode' / 'skills' / 'golden-docs' / 'SKILL.md').read_text()
        self.assertIn('cathrynlavery/diagram-design', skill)
        self.assertIn('system fonts only', skill)
        view = (ROOT / 'docs' / 'ARCHITECTURE_VIEW.html').read_text()
        self.assertIn('<html lang="en">', view)
        self.assertIn('<main>', view)
        self.assertNotRegex(view, r'''(?i)(?:src|href)\s*=\s*["'](?:https?:)?//|@import\s+url|url\(\s*["']?(?:https?:)?//|fonts\.googleapis\.com''')

    def test_react_route_loads_local_skill_with_approved_token_hierarchy(self):
        route = golden_route.route_for('react-app-feature')
        self.assertEqual([item['id'] for item in route['skills']], ['golden-react'])
        skill = (ROOT / '.opencode' / 'skills' / 'golden-react' / 'SKILL.md').read_text()
        self.assertIn('primitive values, purpose-based semantic names, and component aliases', skill)
        self.assertIn('Never run remote shadcn installers', skill)

    def test_every_route_reference_resolves_and_keeps_candidate_mcp_unapproved(self):
        self.assertEqual(golden_route.validation_errors(), [])
        rows = json.loads((ROOT / 'workflows' / 'task-routing.json').read_text())['workflows']
        self.assertEqual(len(rows), 12)
        self.assertTrue(all(row['mcp'] == [] for row in rows))

    def test_missing_skill_reference_fails_manifest_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in ('workflows/task-routing.json', 'research/capability-selection.json', 'opencode.json'):
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, destination)
            shutil.copytree(ROOT / '.opencode', root / '.opencode')
            path = root / 'workflows' / 'task-routing.json'
            data = json.loads(path.read_text())
            data['workflows'][1]['skills'] = ['missing-skill']
            path.write_text(json.dumps(data))
            errors = golden_route.validation_errors(root)
            self.assertTrue(any('skill reference is missing locally' in error for error in errors))

    def test_small_fix_rejects_unneeded_skill(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in ('workflows/task-routing.json', 'research/capability-selection.json', 'opencode.json'):
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, destination)
            shutil.copytree(ROOT / '.opencode', root / '.opencode')
            path = root / 'workflows' / 'task-routing.json'
            data = json.loads(path.read_text())
            data['workflows'][0]['skills'] = ['golden-routing']
            path.write_text(json.dumps(data))
            self.assertTrue(any('only small-fix may omit a skill' in error
                                for error in golden_route.validation_errors(root)))

    def test_unknown_route_fields_and_candidates_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in ('workflows/task-routing.json', 'research/capability-selection.json', 'opencode.json'):
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, destination)
            shutil.copytree(ROOT / '.opencode', root / '.opencode')
            path = root / 'workflows' / 'task-routing.json'
            data = json.loads(path.read_text())
            data['workflows'][0]['unreviewed_power'] = True
            data['workflows'][0]['capability_candidates'] = ['unregistered-tool']
            path.write_text(json.dumps(data))
            errors = golden_route.validation_errors(root)
            self.assertTrue(any('required route fields missing' in error for error in errors))
            self.assertTrue(any('capability_candidates' in error for error in errors))

    def test_unknown_task_selection_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in ('workflows/task-routing.json', 'research/capability-selection.json', 'opencode.json'):
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, destination)
            shutil.copytree(ROOT / '.opencode', root / '.opencode')
            path = root / 'workflows' / 'task-routing.json'
            data = json.loads(path.read_text())
            data['workflows'][0]['selection_task'] = 'missing decision'
            path.write_text(json.dumps(data))
            errors = golden_route.validation_errors(root)
            self.assertTrue(any('selection_task must resolve a complete capability decision' in error for error in errors))

    def test_non_object_manifest_roots_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in ('workflows/task-routing.json', 'research/capability-selection.json', 'opencode.json'):
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text('[]')
            config = root / '.opencode' / 'opencode.json'
            config.parent.mkdir(parents=True, exist_ok=True)
            config.write_text('{}')
            self.assertTrue(any('roots must be JSON objects' in error for error in golden_route.validation_errors(root)))


if __name__ == '__main__':
    unittest.main()
