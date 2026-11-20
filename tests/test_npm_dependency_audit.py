import base64
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('npm_dependency_audit', ROOT / 'scripts' / 'npm_dependency_audit.py')
audit_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit_module)


class NpmDependencyAuditTests(unittest.TestCase):
    def _fixture(self, folder: Path, license_id='MIT'):
        modules = folder / 'node_modules'
        package = modules / 'left-pad'
        package.mkdir(parents=True)
        (package / 'package.json').write_text(json.dumps({
            'name': 'left-pad', 'version': '1.0.0', 'license': license_id,
        }))
        (package / 'LICENSE').write_text('Example license notice\n')
        integrity = 'sha512-' + base64.b64encode(b'fixture-package-integrity').decode()
        lock = {
            'name': 'synthetic-root', 'version': '1.0.0', 'lockfileVersion': 3,
            'packages': {
                '': {'name': 'synthetic-root', 'version': '1.0.0', 'dependencies': {'left-pad': '1.0.0'}},
                'node_modules/left-pad': {
                    'version': '1.0.0', 'resolved': 'https://registry.npmjs.org/left-pad/-/left-pad-1.0.0.tgz',
                    'integrity': integrity,
                },
                'node_modules/@esbuild/win32-x64': {
                    'version': '0.25.12', 'resolved': 'https://registry.npmjs.org/@esbuild/win32-x64/-/win32-x64-0.25.12.tgz',
                    'integrity': integrity, 'optional': True, 'os': ['win32'], 'cpu': ['x64'],
                },
            },
        }
        lock_path = folder / 'package-lock.json'
        lock_path.write_text(json.dumps(lock))
        return lock_path, modules

    def test_inventory_and_sbom_cover_only_installed_locked_packages(self):
        with tempfile.TemporaryDirectory() as d:
            lock, modules = self._fixture(Path(d))
            report, sbom = audit_module.audit(lock, modules)
            self.assertEqual(report['counts']['locked_entries'], 2)
            self.assertEqual(report['counts']['installed_entries'], 1)
            self.assertEqual(report['counts']['not_staged_entries'], 1)
            unstaged = next(row for row in report['packages'] if row['name'] == '@esbuild/win32-x64')
            self.assertEqual(unstaged['review_status'], 'UNSTAGED_PLATFORM_OR_OPTIONAL_PACKAGE')
            self.assertEqual(len(sbom['components']), 1)
            self.assertEqual(sbom['components'][0]['licenses'], [{'license': {'id': 'MIT'}}])
            refs = [item['ref'] for item in sbom['dependencies']]
            self.assertEqual(len(refs), len(set(refs)))

    def test_non_osi_license_metadata_is_marked_for_review(self):
        with tempfile.TemporaryDirectory() as d:
            lock, modules = self._fixture(Path(d), license_id='CC0-1.0')
            report, _ = audit_module.audit(lock, modules)
            installed = next(row for row in report['packages'] if row['installed_in_audit_environment'])
            self.assertEqual(installed['unknown_license_ids'], ['CC0-1.0'])
            self.assertEqual(installed['review_status'], 'OSI_LICENSE_REVIEW_REQUIRED')

    def test_audit_rejects_path_traversal_lock_entry(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            lock, modules = self._fixture(folder)
            payload = json.loads(lock.read_text())
            payload['packages']['node_modules/../../escape'] = payload['packages'].pop('node_modules/left-pad')
            lock.write_text(json.dumps(payload))
            with self.assertRaisesRegex(ValueError, 'Unsafe package path'):
                audit_module.audit(lock, modules)


if __name__ == '__main__':
    unittest.main()
