import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

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

    def test_inapplicable_has_reason(self):
        data = golden.run_check(EXAMPLE, full=True)
        rule = by_id(data, 'WEB-001')
        self.assertEqual(rule['status'], 'NOT_APPLICABLE')
        self.assertIn('Profile', rule['evidence'])

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
