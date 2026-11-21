import hashlib
import json
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(relative):
    return json.loads((ROOT / relative).read_text(encoding='utf-8'))


class PrecompanyEvidenceTests(unittest.TestCase):
    def test_evidence_preserves_nonqualified_full_check_statuses(self):
        evidence = load('PRECOMPANY_EVIDENCE.json')
        self.assertEqual(evidence['status'], 'PRE_QUALIFICATION')
        self.assertEqual(evidence['qualification']['performance_uplift_claim'], 'NONE')
        checks = evidence['tests']['golden_full_release_checks']
        self.assertEqual(len(checks), 3)
        for check in checks:
            self.assertEqual(check['status'], 'NOT_QUALIFIED')
            self.assertTrue(check['blocking_rule_ids'])
            self.assertTrue((ROOT / check['evidence']).is_file())

    def test_offline_inventory_matches_authoritative_asset_manifest(self):
        inventory = load('OFFLINE_ASSET_INVENTORY.json')
        manifest_path = ROOT / inventory['source_manifest']['path']
        self.assertEqual(
            hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
            inventory['source_manifest']['sha256'],
        )
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        self.assertEqual(
            [(item['name'], item['status']) for item in inventory['assets']],
            [(item['name'], item['status']) for item in manifest['assets']],
        )
        self.assertEqual(inventory['staged_asset_groups'], 0)

    def test_fab_inventory_matches_candidate_manifest_without_claiming_staging(self):
        inventory = load('OFFLINE_ASSET_INVENTORY.json')['fab_sampling_transfer_kit']
        manifest_path = ROOT / inventory['manifest']
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        self.assertEqual(len(manifest['repositories']), inventory['candidate_repository_count'])
        self.assertEqual(
            hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
            inventory['manifest_sha256'],
        )
        self.assertEqual(inventory['source_repositories_staged'], 0)
        self.assertEqual(inventory['status'], 'CANDIDATE_LIST_ONLY')

    def test_original_fab_archive_is_hash_pinned_and_complete(self):
        archive = load('OFFLINE_ASSET_INVENTORY.json')['fab_sampling_transfer_kit']['source_archive']
        path = ROOT / archive['path']
        self.assertEqual(path.stat().st_size, archive['bytes'])
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), archive['sha256'])
        self.assertTrue(archive['original_preserved_byte_for_byte'])
        with zipfile.ZipFile(path) as bundle:
            files = [name for name in bundle.namelist() if not name.endswith('/')]
        self.assertEqual(len(files), archive['source_files'])

    def test_simpy_candidate_evidence_is_hash_pinned_and_not_qualified(self):
        candidate = load('research/fab-candidates/simpy-4.1.2/candidate.json')
        registry = load('research/capability-selection.json')
        self.assertEqual(candidate['status'], 'EVALUATION_ONLY_NOT_APPROVED')
        self.assertFalse(candidate['external_artifact_staged_in_repository'])
        self.assertEqual(candidate['license'], 'MIT')
        self.assertEqual(candidate['test_results']['native_windows_linux'], 'NOT_RUN')
        self.assertEqual(candidate['test_results']['company_runtime_or_clearance'], 'NOT_RUN')
        self.assertEqual(candidate['test_results']['upstream_tests_directory'].split(';')[1].strip(), '141 passed')
        self.assertIn('0.11s versus expected 0.10s', candidate['test_results']['upstream_full_pytest'])
        self.assertIn('repeated with the same timing-sensitive failure', candidate['test_results']['upstream_full_pytest'])
        capability = next(row for row in registry['candidates'] if row['id'] == 'simpy-discrete-event-simulator')
        self.assertEqual(capability['decision'], 'EVALUATION_ONLY_NOT_APPROVED; NOT_STAGED_AS_COMPANY_ASSET')
        decision = next(row for row in registry['task_decisions'] if row['task'] == 'fab discrete-event capacity simulation')
        self.assertEqual(decision['current_choice'], 'Keep the existing Python standard-library baseline; run SimPy only as an isolated candidate comparison after company OSS clearance')


if __name__ == '__main__':
    unittest.main()
