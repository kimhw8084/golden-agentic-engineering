import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('golden_pilot', ROOT / 'scripts' / 'golden.py')
golden = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(golden)
PACK_SPEC = importlib.util.spec_from_file_location('offline_packager', ROOT / 'scripts' / 'package_offline.py')
packager = importlib.util.module_from_spec(PACK_SPEC)
PACK_SPEC.loader.exec_module(packager)
EXAMPLE = ROOT / 'examples' / 'python-app'


def by_id(evidence, rule_id):
    return next(r for r in evidence['results'] if r['rule_id'] == rule_id)


class GoldenProofTests(unittest.TestCase):
    def test_fast_example_passes_and_defers_full(self):
        evidence = golden.run_check(EXAMPLE, full=False)
        self.assertEqual(by_id(evidence, 'GOLD-001')['status'], 'PASS')
        self.assertEqual(by_id(evidence, 'PY-001')['status'], 'PASS')
        self.assertEqual(by_id(evidence, 'PY-002')['status'], 'DEFERRED')
        self.assertFalse(evidence['qualifies_release'])
        self.assertFalse(evidence['blocking_rule_ids'])

    def test_full_example_blocks_missing_security_and_lint(self):
        evidence = golden.run_check(EXAMPLE, full=True)
        self.assertEqual(by_id(evidence, 'PY-002')['status'], 'PASS')
        self.assertEqual(by_id(evidence, 'SEC-001')['status'], 'NOT_RUN')
        self.assertEqual(by_id(evidence, 'PY-003')['status'], 'NOT_RUN')
        self.assertFalse(evidence['qualifies_release'])
        self.assertIn('SEC-001', evidence['blocking_rule_ids'])

    def test_nicegui_example_configures_allowlisted_ui_contracts(self):
        example = ROOT / 'examples' / 'nicegui-app'
        project, error = golden.load_manifest(example)
        self.assertIsNone(error)
        command = project['commands']['ui_contracts']
        self.assertTrue(golden.approved_command('ui_contracts', command)[0])

    def test_inapplicable_has_reason(self):
        data = golden.run_check(EXAMPLE, full=True)
        rule = by_id(data, 'WEB-001')
        self.assertEqual(rule['status'], 'NOT_APPLICABLE')
        self.assertIn('repository profile inventory sha256=', rule['evidence'])
        self.assertNotIn(str(EXAMPLE), rule['evidence'])

    def test_declared_python_profile_cannot_hide_react_repository_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(EXAMPLE, root, dirs_exist_ok=True)
            manifest_path = root / 'golden.project.json'
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            manifest['profile'] = 'python'
            manifest['capabilities']['ui'] = False
            manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
            (root / 'package.json').write_text(json.dumps({
                'dependencies': {'react': '19.2.0', 'react-dom': '19.2.0'}
            }), encoding='utf-8')
            (root / 'src').mkdir(exist_ok=True)
            (root / 'src' / 'App.tsx').write_text("import { createElement } from 'react';\n", encoding='utf-8')

            with patch.object(golden, 'external', return_value=('NOT_RUN', 'not executed in this test')):
                data = golden.run_check(root, full=True)

            self.assertEqual(by_id(data, 'WEB-001')['status'], 'NOT_RUN')
            self.assertEqual(by_id(data, 'WEB-002')['status'], 'NOT_RUN')
            self.assertEqual(by_id(data, 'UI-001')['status'], 'NOT_RUN')
            self.assertFalse(data['qualifies_release'])

    def test_unknown_profile_without_repository_markers_stays_not_run(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = json.loads((EXAMPLE / 'golden.project.json').read_text(encoding='utf-8'))
            manifest['profile'] = 'other'
            (root / 'golden.project.json').write_text(json.dumps(manifest), encoding='utf-8')

            data = golden.run_check(root, full=True)

            self.assertEqual(by_id(data, 'PY-001')['status'], 'NOT_RUN')
            self.assertEqual(by_id(data, 'WEB-001')['status'], 'NOT_RUN')
            self.assertFalse(data['qualifies_release'])

    def test_incomplete_profile_inventory_cannot_mark_a_rule_not_applicable(self):
        manifest = json.loads((EXAMPLE / 'golden.project.json').read_text(encoding='utf-8'))
        rule = next(r for r in golden.read_json(golden.RULES)['rules'] if r['id'] == 'WEB-001')
        with patch.object(golden, 'PROFILE_SCAN_MAX_ENTRIES', 0):
            evidence = golden.repository_profile_evidence(EXAMPLE)
        status, reason = golden.applicable(rule, manifest, evidence)
        self.assertFalse(evidence['complete'])
        self.assertEqual(status, 'NOT_RUN')
        self.assertIn('inventory is incomplete', reason)

    def test_unreadable_directory_cannot_be_omitted_from_profile_inventory(self):
        def walk_with_error(_root, *, followlinks, onerror):
            self.assertFalse(followlinks)
            onerror(PermissionError('synthetic unreadable directory'))
            return iter(())

        with patch.object(golden.os, 'walk', side_effect=walk_with_error):
            evidence = golden.repository_profile_evidence(EXAMPLE)

        self.assertFalse(evidence['complete'])

    def test_false_capability_does_not_prove_non_applicability(self):
        manifest = json.loads((EXAMPLE / 'golden.project.json').read_text())
        rule = next(r for r in golden.read_json(golden.RULES)['rules'] if r['id'] == 'API-001')
        status, reason = golden.applicable(rule, manifest)
        self.assertEqual(status, 'NOT_RUN')
        self.assertIn('false declarations alone', reason)

    def test_arbitrary_manifest_command_is_not_executed(self):
        project = {'commands': {'python_tests': ['python', '-c', 'print("should not run")']}}
        status, reason = golden.external('python_tests', EXAMPLE, project, 5)
        self.assertEqual(status, 'NOT_RUN')
        self.assertIn('allowlist', reason)

    def test_python_ui_contract_command_has_narrow_pytest_allowlist(self):
        approved = ['${PYTHON}', '-m', 'pytest', '-q']
        allowed, basis = golden.approved_command('ui_contracts', approved)
        self.assertTrue(allowed)
        self.assertIn('UI contract', basis)
        allowed, _ = golden.approved_command('ui_contracts', approved + ['-c', 'untrusted.ini'])
        self.assertFalse(allowed)

    def test_python_ui_contract_marks_missing_dependencies_not_run(self):
        project = {'profile': 'nicegui', 'commands': {'ui_contracts': ['${PYTHON}', '-m', 'pytest', '-q']}}
        with patch.object(
            golden.importlib.util, 'find_spec', side_effect=lambda name: object() if name == 'nicegui' else None
        ):
            with patch.object(golden.subprocess, 'run') as run:
                status, evidence = golden.external('ui_contracts', EXAMPLE, project, 5)
        self.assertEqual(status, 'NOT_RUN')
        self.assertIn('pytest', evidence)
        run.assert_not_called()

    def test_python_ui_contract_disables_pytest_plugins_and_cache(self):
        project = {'profile': 'nicegui', 'commands': {'ui_contracts': ['${PYTHON}', '-m', 'pytest', '-q']}}
        completed = subprocess.CompletedProcess([], 0, '4 passed in 1.0s', '')
        with patch.object(golden.importlib.util, 'find_spec', return_value=object()):
            with patch.object(golden.subprocess, 'run', return_value=completed) as run:
                status, evidence = golden.external('ui_contracts', EXAMPLE, project, 5)
        self.assertEqual(status, 'PASS')
        self.assertIn('output_sha256=', evidence)
        self.assertNotIn('4 passed', evidence)
        self.assertEqual(run.call_args.kwargs['env']['PYTEST_DISABLE_PLUGIN_AUTOLOAD'], '1')
        self.assertEqual(run.call_args.kwargs['env']['PYTEST_ADDOPTS'], '-p no:cacheprovider')
        self.assertFalse(run.call_args.kwargs.get('shell', False))

    def test_evidence_never_contains_raw_command_output(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'golden.project.json').write_text(json.dumps({
                **json.loads((EXAMPLE / 'golden.project.json').read_text()),
                'commands': {'python_tests': ['${PYTHON}', '-m', 'unittest', 'discover', '-s', 'tests', '-v']}
            }))
            # Run the allowlisted interpreter only against an empty local test folder.
            (root / 'tests').mkdir()
            data = golden.run_check(root, full=True)
            serialized = json.dumps(data)
            self.assertNotIn(str(root), serialized)
            self.assertNotIn('Traceback', serialized)

    def test_report_rejects_contradictory_pass_claim(self):
        data = golden.run_check(EXAMPLE, full=False)
        data['qualifies_release'] = True
        with self.assertRaises(ValueError):
            golden.validate_evidence(data, EXAMPLE)

    def test_report_rejects_fabricated_full_not_applicable_release(self):
        data = golden.run_check(EXAMPLE, full=True)
        for row in data['results']:
            row['status'] = 'NOT_APPLICABLE'
            row['evidence'] = 'Approved exception by a fabricated authority.'
        data['blocking_rule_ids'] = []
        data['qualifies_release'] = True
        with self.assertRaisesRegex(ValueError, 'fresh local replay'):
            golden.validate_evidence(data, EXAMPLE)

    def test_report_requires_project_for_imported_evidence(self):
        data = golden.run_check(EXAMPLE, full=False)
        with self.assertRaisesRegex(ValueError, 'without replaying'):
            golden.validate_evidence(data)

    def test_missing_manifest_never_fabricates_nonapplicable(self):
        with tempfile.TemporaryDirectory() as d:
            data = golden.run_check(Path(d), full=True)
            self.assertEqual(by_id(data, 'GOLD-001')['status'], 'FAIL')
            self.assertEqual(by_id(data, 'WEB-001')['status'], 'NOT_RUN')
            self.assertFalse(data['qualifies_release'])

    def test_manifest_rejects_wrong_release_pin(self):
        manifest = json.loads((EXAMPLE / 'golden.project.json').read_text())
        manifest['golden_version'] = 'unknown'
        err = golden.manifest_check(manifest, '0.1.0-dev')
        self.assertIn('does not match', err)

    def test_manifest_rejects_ill_typed_command(self):
        manifest = json.loads((EXAMPLE / 'golden.project.json').read_text())
        manifest['commands']['security_scan'] = 'curl http://bad.example/'
        self.assertIn('array', golden.manifest_check(manifest, '0.1.0-dev'))

    def test_path_python_alias_is_not_an_approved_command(self):
        status, reason = golden.external(
            'python_tests', EXAMPLE,
            {'commands': {'python_tests': ['python3', '-m', 'unittest', 'discover', '-s', 'tests', '-v']}},
            5,
        )
        self.assertEqual(status, 'NOT_RUN')
        self.assertIn('allowlist', reason)

    def test_unverified_low_criticality_does_not_make_recovery_na(self):
        manifest = json.loads((EXAMPLE / 'golden.project.json').read_text())
        rule = next(r for r in golden.read_json(golden.RULES)['rules'] if r['id'] == 'REL-001')
        status, reason = golden.applicable(rule, manifest)
        self.assertEqual(status, 'NOT_RUN')
        self.assertIn('owner applicability evidence', reason)

    def test_html_escaping(self):
        data = golden.run_check(EXAMPLE, full=False)
        data['project'] = '<script>alert(1)</script>'
        with self.assertRaisesRegex(ValueError, 'project label'):
            golden.render_report(data, EXAMPLE)
        data['project'] = 'local-project'
        output = golden.render_report(data, EXAMPLE)
        self.assertNotIn('<script>', output)
        self.assertIn('<!doctype html>', output)

    def test_own_sample_python_source_is_syntactically_valid(self):
        status, evidence = golden.builtin('py_syntax', EXAMPLE, {})
        self.assertEqual(status, 'PASS')
        self.assertIn('Python source', evidence)

    def test_dryrun_fetch_does_not_download_or_write(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'do-not-create'
            call = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'fetch_sources.py'),
                                  '--tier', 'pilot', '--limit', '1', '--out', str(out)],
                                  capture_output=True, text=True, check=False)
            self.assertEqual(call.returncode, 0, call.stderr)
            self.assertIn('DRY RUN', call.stdout)
            self.assertFalse(out.exists())

    def test_bootstrap_dryrun_does_not_write(self):
        with tempfile.TemporaryDirectory() as d:
            call = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'bootstrap_project.py'),
                                   '--target', d, '--name', 'test', '--profile', 'react'],
                                   capture_output=True, text=True)
            self.assertEqual(call.returncode, 0, call.stderr)
            self.assertFalse((Path(d) / 'golden.project.json').exists())

    def test_bootstrap_apply_never_overwrites(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            (target / 'AGENTS.md').write_text('keep these rules')
            call = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'bootstrap_project.py'),
                                   '--target', d, '--name', 'test', '--profile', 'react', '--apply'],
                                   capture_output=True, text=True)
            self.assertEqual(call.returncode, 0, call.stderr)
            self.assertEqual((target / 'AGENTS.md').read_text(), 'keep these rules')
            self.assertTrue((target / 'golden.project.json').exists())

    def test_install_opencode_dryrun_does_not_write(self):
        with tempfile.TemporaryDirectory() as d:
            call = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'install_opencode.py'),
                                   '--target', d], capture_output=True, text=True)
            self.assertEqual(call.returncode, 0, call.stderr)
            self.assertFalse((Path(d) / 'agents').exists())

    def test_rule_catalog_has_unique_ids(self):
        catalog = golden.read_json(golden.RULES)
        ids = [r['id'] for r in catalog['rules']]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 19)

    def test_tool_catalog_has_unique_ids(self):
        catalog = json.loads((ROOT / 'tools' / 'candidates.json').read_text())
        ids = [r['id'] for r in catalog['candidates']]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 64)
        diagram_skill = next(r for r in catalog['candidates'] if r['id'] == 'cathrynlavery--diagram-design')
        self.assertEqual(diagram_skill['candidate_type'], 'agent-skill')
        self.assertEqual(diagram_skill['category'], 'diagram')
        self.assertEqual(diagram_skill['review_status'], 'UNQUALIFIED_SOURCE_CANDIDATE')

    def test_offline_bundle_includes_hidden_assets_and_verifies_hashes(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d) / 'repo'; repo.mkdir()
            (repo / '.opencode' / 'skills' / 'sample').mkdir(parents=True)
            (repo / '.opencode' / 'skills' / 'sample' / 'SKILL.md').write_text('sample skill')
            (repo / 'LICENSE').write_text('MIT')
            (repo / 'offline').mkdir()
            (repo / 'offline' / 'assets-manifest.json').write_text(json.dumps({'assets': [{'name': 'fixture dependency', 'status': 'NOT_STAGED'}]}))
            subprocess.run(['git', '-C', str(repo), 'init', '-q'], check=True)
            subprocess.run(['git', '-C', str(repo), 'config', 'user.email', 'test@example.invalid'], check=True)
            subprocess.run(['git', '-C', str(repo), 'config', 'user.name', 'Offline Test'], check=True)
            subprocess.run(['git', '-C', str(repo), 'add', '-A'], check=True)
            subprocess.run(['git', '-C', str(repo), 'commit', '-qm', 'fixture'], check=True)
            archive = Path(d) / 'bundle.tar.gz'
            manifest = packager.create_bundle(repo, archive)
            self.assertIn('.opencode/skills/sample/SKILL.md', [f['path'] for f in manifest['files']])
            verified = packager.verify_bundle(archive)
            self.assertEqual(verified['qualification'], 'TRANSFER_SOURCE_ONLY_NOT_OFFLINE_EXECUTABLE_OR_COMPANY_APPROVED')
            self.assertTrue(verified['missing_assets'])

    def test_offline_bundle_refuses_dirty_tracked_files(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d); (repo / 'README.md').write_text('v1')
            subprocess.run(['git', '-C', str(repo), 'init', '-q'], check=True)
            subprocess.run(['git', '-C', str(repo), 'config', 'user.email', 'test@example.invalid'], check=True)
            subprocess.run(['git', '-C', str(repo), 'config', 'user.name', 'Offline Test'], check=True)
            subprocess.run(['git', '-C', str(repo), 'add', 'README.md'], check=True)
            subprocess.run(['git', '-C', str(repo), 'commit', '-qm', 'fixture'], check=True)
            (repo / 'README.md').write_text('changed')
            with self.assertRaises(ValueError):
                packager.create_bundle(repo, Path(d) / 'bundle.tar.gz')

if __name__ == '__main__':
    unittest.main()
