import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "research/react-vitest-5.1.1-candidate"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ReactVitestCandidateTests(unittest.TestCase):
    def test_candidate_pins_and_local_test_evidence_match_artifacts(self):
        evidence_path = CANDIDATE / "qualification.json"
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        candidate_package = CANDIDATE / "package.json"
        candidate_lock = CANDIDATE / "package-lock.json"
        active_lock = ROOT / "examples/react-app/package-lock.json"
        package = json.loads(candidate_package.read_text(encoding="utf-8"))
        lock = json.loads(candidate_lock.read_text(encoding="utf-8"))
        active = json.loads(active_lock.read_text(encoding="utf-8"))
        active_packages = active["packages"]
        packages = lock["packages"]

        self.assertEqual(evidence["status"], "LOCAL_MACOS_PASS; COMPANY_NODE_TARGET_UNKNOWN; NOT_SELECTED")
        self.assertEqual(evidence["active_fixture"]["package_lock_sha256"], _sha256(active_lock))
        self.assertEqual(evidence["active_fixture"]["stackback_present"], "node_modules/stackback" in active["packages"])
        self.assertEqual(evidence["active_fixture"]["vitest_version"], active_packages["node_modules/vitest"]["version"])
        self.assertEqual(evidence["active_fixture"]["vite_version"], active_packages["node_modules/vite"]["version"])
        active_audit_path = ROOT / evidence["active_fixture"]["npm_audit_report"]
        self.assertEqual(evidence["active_fixture"]["npm_audit_report_sha256"], _sha256(active_audit_path))
        active_npm_audit = json.loads(active_audit_path.read_text(encoding="utf-8"))
        self.assertEqual(active_npm_audit["metadata"]["vulnerabilities"]["total"], 0)
        self.assertEqual(evidence["candidate"]["package_json_sha256"], _sha256(candidate_package))
        self.assertEqual(evidence["candidate"]["package_lock_sha256"], _sha256(candidate_lock))
        self.assertEqual(package["devDependencies"]["vitest"], "5.1.1")
        self.assertEqual(package["engines"]["node"], "^22.12.0 || ^24.0.0 || >=26.0.0")
        self.assertEqual(packages[""]["devDependencies"]["vitest"], "5.1.1")
        self.assertEqual(packages[""]["engines"]["node"], package["engines"]["node"])
        self.assertEqual(packages["node_modules/vitest"]["version"], "5.1.1")
        self.assertEqual(packages["node_modules/vitest"]["license"], "MIT")
        self.assertEqual(packages["node_modules/vite"]["version"], "7.3.8")
        self.assertEqual(packages["node_modules/why-is-node-running"]["version"], "3.2.1")
        self.assertEqual(packages["node_modules/why-is-node-running"]["license"], "MIT")
        self.assertNotIn("node_modules/stackback", packages)
        self.assertEqual(evidence["candidate"]["stackback_present"], False)
        self.assertEqual(evidence["candidate"]["registry_entries_missing_integrity"], 0)

        candidate_audit_path = ROOT / evidence["candidate"]["npm_audit_report"]
        self.assertEqual(evidence["candidate"]["npm_audit_report_sha256"], _sha256(candidate_audit_path))
        candidate_npm_audit = json.loads(candidate_audit_path.read_text(encoding="utf-8"))
        self.assertEqual(candidate_npm_audit["metadata"]["vulnerabilities"]["total"], 0)

        for field in ("dependency_audit", "sbom"):
            path = ROOT / evidence["candidate"][field]
            self.assertTrue(path.is_file())
            self.assertFalse(path.is_symlink())
            self.assertEqual(evidence["candidate"][field + "_sha256"], _sha256(path))

    def test_candidate_license_supplements_match_unchanged_package_integrities(self):
        lock = json.loads((CANDIDATE / "package-lock.json").read_text(encoding="utf-8"))
        audit = json.loads((CANDIDATE / "dependency-audit-macos-arm64.json").read_text(encoding="utf-8"))
        supplements = json.loads((ROOT / "research/react-license-supplements.json").read_text(encoding="utf-8"))
        audit_by_name = {row["name"]: row for row in audit["packages"]}

        self.assertEqual(audit["counts"]["locked_entries"], 123)
        self.assertEqual(audit["counts"]["installed_entries"], 73)
        self.assertEqual(audit["counts"]["not_staged_entries"], 50)
        self.assertEqual(audit["counts"]["license_files_missing"], 3)
        self.assertEqual(audit["counts"]["license_metadata_missing"], 0)
        self.assertEqual(audit["counts"]["non_osi_or_unknown_license_ids"], 0)
        self.assertEqual(len(supplements["notices"]), 3)
        for notice in supplements["notices"]:
            name = notice["package"]
            entry = lock["packages"]["node_modules/" + name]
            audited = audit_by_name[name]
            self.assertEqual(entry["version"], notice["version"])
            self.assertEqual(entry["integrity"], notice["npm_integrity"])
            self.assertEqual(audited["version"], notice["version"])
            self.assertEqual(audited["integrity"], notice["npm_integrity"])


if __name__ == "__main__":
    unittest.main()
