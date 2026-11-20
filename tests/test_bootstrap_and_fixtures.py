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
            with patch.object(bootstrap.shutil, 'which', side_effect=lambda name: '/fake/' + name):
                report = bootstrap.doctor(config=config, opencode_version='2.4.0', node_version='20.0.0')
            self.assertIn('internal', report['opencode_config']['provider_keys'])
            self.assertNotIn('example-secret-value', json.dumps(report))
            self.assertEqual(config.read_bytes(), before)
            self.assertEqual(report['status'], 'NEEDS_APPROVED_ASSETS')

    def test_apply_requires_reviewed_doctor_and_preserves_config_then_rolls_back(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d); target = folder / 'opencode'
            target.mkdir()
            (target / 'opencode.json').write_text(json.dumps({'provider': {'internal': {'apiKey': 'keep'}}, 'model': 'internal/model'}))
            config = target / 'opencode.json'
            before = config.read_bytes()
            bundle = self._make_bundle(folder)
            with patch.object(bootstrap.shutil, 'which', side_effect=lambda name: '/fake/' + name):
                report = bootstrap.doctor(config=config, opencode_version='2.4.0', node_version='20.0.0')
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
            with patch.object(bootstrap.shutil, 'which', side_effect=lambda name: '/fake/' + name):
                report = bootstrap.doctor(config=config, opencode_version='2.4.0', node_version='20.0.0')
            with patch.object(bootstrap, 'doctor', return_value=report):
                with self.assertRaisesRegex(ValueError, 'Conflicting existing files'):
                    bootstrap.apply_bundle(bundle, target, report, folder / 'transaction.json')
            self.assertEqual((target / 'agents' / 'golden-example.md').read_text(), 'user content')

    def test_apply_refuses_existing_transaction_without_copying_assets(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d); target = folder / 'opencode'; target.mkdir()
            config = target / 'opencode.json'; config.write_text('{}')
            bundle = self._make_bundle(folder)
            with patch.object(bootstrap.shutil, 'which', side_effect=lambda name: '/fake/' + name):
                report = bootstrap.doctor(config=config, opencode_version='2.4.0', node_version='20.0.0')
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

    def test_api_sqlite_contract_and_incident_timeline(self):
        api_dir = ROOT / 'examples' / 'scenarios' / 'api_db'
        incident_dir = ROOT / 'examples' / 'scenarios' / 'incident'
        sys.path.insert(0, str(api_dir))
        try:
            from sample_store import add_sample, create_store
            store = create_store()
            self.assertEqual(add_sample(store, 'fixture', 1.5)['status'], 201)
        finally:
            sys.path.remove(str(api_dir))
        sys.path.insert(0, str(incident_dir))
        try:
            from analyze import timeline
            self.assertEqual(len(timeline(incident_dir / 'events.jsonl')), 4)
        finally:
            sys.path.remove(str(incident_dir))


if __name__ == '__main__':
    unittest.main()
