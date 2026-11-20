import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
BOOT_SPEC = importlib.util.spec_from_file_location('company_bootstrap', ROOT / 'scripts' / 'company_bootstrap.py')
bootstrap = importlib.util.module_from_spec(BOOT_SPEC)
BOOT_SPEC.loader.exec_module(bootstrap)
PACK_SPEC = importlib.util.spec_from_file_location('offline_packager', ROOT / 'scripts' / 'package_offline.py')
packager = importlib.util.module_from_spec(PACK_SPEC)
PACK_SPEC.loader.exec_module(packager)
SEC_SPEC = importlib.util.spec_from_file_location('security_scan', ROOT / 'scripts' / 'security_scan.py')
security_scan = importlib.util.module_from_spec(SEC_SPEC)
SEC_SPEC.loader.exec_module(security_scan)


class CompanyBootstrapTests(unittest.TestCase):
    def _runtime(self):
        return {
            'opencode': {'available': True, 'version': '2.4.0', 'version_source': 'test-fixture', 'sha256': 'a' * 64},
            'node': {'available': True, 'version': '20.0.0', 'version_source': 'test-fixture', 'sha256': 'b' * 64},
        }

    def _make_bundle(self, folder: Path) -> Path:
        repo = folder / 'repo'; repo.mkdir()
        (repo / '.opencode' / 'agents').mkdir(parents=True)
        (repo / '.opencode' / 'agents' / 'golden-example.md').write_text('agent fixture')
        (repo / 'LICENSE').write_text('MIT')
        subprocess.run(['git', '-C', str(repo), 'init', '-q'], check=True)
        subprocess.run(['git', '-C', str(repo), 'config', 'user.email', 'test@example.invalid'], check=True)
        subprocess.run(['git', '-C', str(repo), 'config', 'user.name', 'Bootstrap Test'], check=True)
        subprocess.run(['git', '-C', str(repo), 'add', '-A'], check=True)
        subprocess.run(['git', '-C', str(repo), 'commit', '-qm', 'fixture'], check=True)
        bundle = folder / 'source.tar.gz'
        packager.create_bundle(repo, bundle)
        return bundle

    def test_doctor_reads_only_config_key_names_and_changes_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            config = Path(d) / 'opencode.json'
            config.write_text(json.dumps({'provider': {'internal': {'options': {'apiKey': 'example-secret-value'}}}, 'model': 'internal/model'}))
            before = config.read_bytes()
            with patch.object(bootstrap, 'local_executable', side_effect=lambda name: self._runtime()[name]):
                with patch.object(bootstrap.subprocess, 'run', side_effect=AssertionError('doctor must not execute binaries')):
                    report = bootstrap.doctor(config=config)
            self.assertEqual(report['opencode_config']['provider_count'], 1)
            self.assertEqual(report['opencode_config']['mcp_server_count'], 0)
            self.assertNotIn('example-secret-value', json.dumps(report))
            self.assertEqual(config.read_bytes(), before)
            self.assertEqual(report['status'], 'NEEDS_APPROVED_ASSETS')
            self.assertEqual(report['machine']['opencode_compatibility'], 'PUBLIC_V2_CANDIDATE')
            self.assertTrue(report['review_diff']['files']['additions'])

    def test_doctor_marks_opaque_runtime_unknown_without_guessing(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.object(bootstrap, 'local_executable', return_value={
                'available': True, 'version': None, 'version_source': 'UNKNOWN_NO_LOCAL_VERSION_METADATA', 'sha256': 'a' * 64,
            }):
                report = bootstrap.doctor(config=Path(d) / 'opencode.json')
            self.assertEqual(report['status'], 'UNKNOWN')
            self.assertEqual(report['machine']['opencode_compatibility'], 'UNKNOWN')
            self.assertIn('no network calls', report['network_policy'])

    def test_runtime_version_is_read_from_matching_local_package_metadata(self):
        with tempfile.TemporaryDirectory() as d:
            package = Path(d) / 'node_modules' / '@opencode' / 'cli'
            binary = package / 'bin' / 'opencode'
            binary.parent.mkdir(parents=True); binary.write_text('fixture executable marker')
            (package / 'package.json').write_text(json.dumps({'name': '@opencode/cli', 'version': '2.7.1'}))
            self.assertEqual(bootstrap.version_from_local_metadata('opencode', binary), ('2.7.1', 'local-package-metadata'))
            (package / 'package.json').write_text(json.dumps({'name': 'unrelated-package', 'version': '99.0.0'}))
            self.assertEqual(bootstrap.version_from_local_metadata('opencode', binary)[0], None)

    def test_apply_requires_reviewed_doctor_and_preserves_config_then_rolls_back(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d); target = folder / 'opencode'
            target.mkdir()
            (target / 'opencode.json').write_text(json.dumps({'provider': {'internal': {'apiKey': 'keep'}}, 'model': 'internal/model'}))
            config = target / 'opencode.json'
            before = config.read_bytes()
            bundle = self._make_bundle(folder)
            with patch.object(bootstrap, 'local_executable', side_effect=lambda name: self._runtime()[name]):
                report = bootstrap.doctor(config=config)
            bootstrap.verify_doctor(report, report)
            current = report
            with patch.object(bootstrap, 'doctor', return_value=current):
                transaction = folder / 'transaction.json'
                result = bootstrap.apply_bundle(bundle, target, report, transaction)
            installed = target / 'agents' / 'golden-example.md'
            self.assertTrue(installed.is_file())
            self.assertEqual(result['smoke_test'], 'PASS')
            self.assertEqual(config.read_bytes(), before)
            self.assertEqual(bootstrap.rollback(transaction), 1)
            self.assertFalse(installed.exists())

    def test_apply_refuses_changed_file_conflict_before_writing(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d); target = folder / 'opencode'; target.mkdir()
            (target / 'agents').mkdir(); (target / 'agents' / 'golden-example.md').write_text('user content')
            config = target / 'opencode.json'; config.write_text('{}')
            bundle = self._make_bundle(folder)
            with patch.object(bootstrap, 'local_executable', side_effect=lambda name: self._runtime()[name]):
                report = bootstrap.doctor(config=config)
            with patch.object(bootstrap, 'doctor', return_value=report):
                with self.assertRaisesRegex(ValueError, 'Conflicting existing files'):
                    bootstrap.apply_bundle(bundle, target, report, folder / 'transaction.json')
            self.assertEqual((target / 'agents' / 'golden-example.md').read_text(), 'user content')

    def test_apply_refuses_existing_transaction_without_copying_assets(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d); target = folder / 'opencode'; target.mkdir()
            config = target / 'opencode.json'; config.write_text('{}')
            bundle = self._make_bundle(folder)
            with patch.object(bootstrap, 'local_executable', side_effect=lambda name: self._runtime()[name]):
                report = bootstrap.doctor(config=config)
            transaction = folder / 'transaction.json'; transaction.write_text('preserve')
            with patch.object(bootstrap, 'doctor', return_value=report):
                with self.assertRaisesRegex(ValueError, 'Transaction path already exists'):
                    bootstrap.apply_bundle(bundle, target, report, transaction)
            self.assertEqual(transaction.read_text(), 'preserve')
            self.assertFalse((target / 'agents').exists())

    def test_source_bundle_is_reproducible(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            first_repo_bundle = self._make_bundle(folder)
            repo = folder / 'repo'
            second = folder / 'second.tar.gz'
            packager.create_bundle(repo, second)
            self.assertEqual(packager.sha_file(first_repo_bundle), packager.sha_file(second))

    def test_doctor_rejects_symlinked_staged_asset(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d); assets = folder / 'assets'; assets.mkdir()
            outside = folder / 'outside.bin'; outside.write_bytes(b'not a staged asset')
            (assets / 'payload.bin').symlink_to(outside)
            manifest = folder / 'assets-manifest.json'
            rows = [{'name': name, 'status': 'NOT_STAGED'} for name in sorted(bootstrap.REQUIRED_ASSET_NAMES)]
            rows[0].update({'status': 'STAGED', 'path': 'payload.bin', 'sha256': bootstrap.hash_file(outside), 'license_review_status': 'APPROVED'})
            manifest.write_text(json.dumps({'schema': 'golden-offline-assets/v1', 'assets': rows}))
            verified, missing = bootstrap.inspect_assets(folder, manifest, assets)
            self.assertEqual(verified, [])
            self.assertIn('symlink', [item['reason'] for item in missing])

    def test_doctor_rejects_incomplete_asset_inventory(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d); manifest = folder / 'assets.json'; assets = folder / 'assets'; assets.mkdir()
            manifest.write_text(json.dumps({'schema': 'golden-offline-assets/v1', 'assets': []}))
            verified, missing = bootstrap.inspect_assets(folder, manifest, assets)
            self.assertEqual(verified, [])
            self.assertEqual(missing[0]['status'], 'UNKNOWN')

    def test_doctor_marks_symlinked_install_paths_as_conflicts(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d); target = folder / 'opencode'; external = folder / 'external'; external.mkdir()
            target.mkdir(); (target / 'agents').symlink_to(external, target_is_directory=True)
            diff = bootstrap.inspect_install_diff(ROOT, target)
            self.assertTrue(any(path.startswith('agents/') for path in diff['conflicts']))
            self.assertFalse(any(path.startswith('agents/') for path in diff['additions']))

    def test_rollback_rejects_intermediate_symlink_escape(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d); target = folder / 'opencode'; target.mkdir()
            outside = folder / 'outside'; outside.mkdir(); victim = outside / 'fixture.md'; victim.write_text('unchanged')
            (target / 'agents').mkdir(); (target / 'agents' / 'linked').symlink_to(outside, target_is_directory=True)
            transaction = folder / 'transaction.json'
            transaction.write_text(json.dumps({
                'schema': 'golden-bootstrap-transaction/v1',
                'mode': 'ADD_ONLY_ROLLBACK_REMOVES_UNCHANGED_CREATED_FILES',
                'target': str(target),
                'created_files': [{'path': 'agents/linked/fixture.md', 'sha256': bootstrap.hash_file(victim)}],
            }))
            with self.assertRaisesRegex(ValueError, 'symlink'):
                bootstrap.rollback(transaction)
            self.assertTrue(victim.is_file())


class SyntheticExampleTests(unittest.TestCase):
    def test_secret_scanner_reports_location_without_value(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'sample.py'
            sample_value = 'superSecret_' + 'ABC123456789'
            key_name = 'pass' + 'word'
            path.write_text(f"{key_name} = '{sample_value}'\n")
            findings = security_scan.scan_file(path, 'sample.py')
            self.assertEqual(findings, [{'file': 'sample.py', 'line': 1, 'kind': 'credential_assignment'}])
            safe = security_scan.scan_file(path, 'sample.py')
            self.assertNotIn(sample_value, json.dumps(safe))

    def test_security_scan_covers_untracked_hidden_files_without_emitting_values(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); hidden = root / '.opencode' / 'skills' / 'fixture'
            hidden.mkdir(parents=True)
            private_value = 'localTestCredential_' + 'ZXY123456789'
            (hidden / 'SKILL.md').write_text('api' + '_key = ' + repr(private_value) + '\n')
            (root / '.git').mkdir(); (root / '.git' / 'ignored.txt').write_text('password="' + private_value + '"')
            result = subprocess.run([sys.executable, '-S', str(ROOT / 'scripts' / 'security_scan.py'), '--repo', d],
                                    capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 2)
            self.assertIn('.opencode/skills/fixture/SKILL.md', result.stdout)
            self.assertNotIn('ignored.txt', result.stdout)
            self.assertNotIn(private_value, result.stdout)

    def test_api_sqlite_contract_and_incident_timeline(self):
        api_dir = ROOT / 'examples' / 'scenarios' / 'api_db'
        incident_dir = ROOT / 'examples' / 'scenarios' / 'incident'
        sys.path.insert(0, str(api_dir))
        try:
            from sample_store import add_sample, create_store
            store = create_store()
            try:
                self.assertEqual(add_sample(store, 'fixture', 1.5)['status'], 201)
            finally:
                store.close()
        finally:
            sys.path.remove(str(api_dir))
        sys.path.insert(0, str(incident_dir))
        try:
            from analyze import timeline
            self.assertEqual(len(timeline(incident_dir / 'events.jsonl')), 4)
        finally:
            sys.path.remove(str(incident_dir))

    def test_manufacturing_sampling_exact_counts_and_no_missing_as_zero(self):
        fixture_dir = ROOT / 'examples' / 'scenarios' / 'manufacturing'
        sys.path.insert(0, str(fixture_dir))
        try:
            from sample_demand import exact_known_wip_demand, naive_future_baseline
            data = json.loads((fixture_dir / 'events.json').read_text(encoding='utf-8'))
            self.assertEqual(exact_known_wip_demand(data['events'], data['as_of'], 7)['known_wip_sample_count'], 8)
            self.assertEqual(exact_known_wip_demand(data['events'], data['as_of'], 30)['known_wip_sample_count'], 14)
            complete = naive_future_baseline(data['daily_history'], data['as_of'], 7)
            self.assertEqual(complete['future_sample_count_estimate'], 28.0)
            incomplete = [row for row in data['daily_history'] if row['sample_date'] != '2026-11-16']
            self.assertEqual(naive_future_baseline(incomplete, data['as_of'], 7)['status'], 'NOT_RUN')
        finally:
            sys.path.remove(str(fixture_dir))


if __name__ == '__main__':
    unittest.main()
