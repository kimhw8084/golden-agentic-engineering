import unittest
from unittest.mock import patch

from scripts.precompany_readiness import (
    classify_full_check,
    local_assessment_state,
    parse_company_actions,
    parse_unittest_summary,
    render_markdown,
    safe_environment,
)


class PrecompanyReadinessTests(unittest.TestCase):
    def test_unittest_summary_counts_passes_skips_and_failures(self):
        self.assertEqual(
            parse_unittest_summary("Ran 14 tests in 0.2s\n\nOK (skipped=2)\n"),
            {"tests_run": 14, "tests_skipped": 2, "tests_failed": 0, "summary_found": True},
        )
        failed = parse_unittest_summary("Ran 3 tests in 0.1s\n\nFAILED (failures=1, errors=1)\n")
        self.assertEqual(failed["tests_failed"], 2)
        self.assertFalse(parse_unittest_summary("no test output")['summary_found'])

    def test_full_check_preserves_nonqualified_status_and_blockers(self):
        evidence = {
            "mode": "FULL",
            "rules_count": 19,
            "results": [{"rule_id": f"R-{index:02}", "status": "NOT_RUN", "mandatory": True}
                        for index in range(19)],
            "qualifies_release": False,
            "blocking_rule_ids": ["AI-001", "MCP-001"],
        }
        result = classify_full_check(2, evidence)
        self.assertEqual(result["status"], "NOT_QUALIFIED")
        self.assertEqual(result["blocking_rule_ids"], ["AI-001", "MCP-001"])
        self.assertEqual(len(result["rule_statuses"]), 19)
        self.assertEqual(classify_full_check(0, evidence)["status"], "RUNNER_ERROR")
        self.assertEqual(classify_full_check(2, None)["status"], "RUNNER_ERROR")

    def test_company_actions_keep_owner_priority_and_evidence(self):
        source = """| Priority | Owner | Exact action needed | Evidence to return |
|---|---|---|---|
| P0 | Security | Enforce blocked egress | Policy and attempt evidence |
| P1 | CI owner | Map existing pipeline | Pipeline identifier |
"""
        self.assertEqual(parse_company_actions(source), [
            {"priority": "P0", "owner": "Security", "action": "Enforce blocked egress",
             "evidence_needed": "Policy and attempt evidence"},
            {"priority": "P1", "owner": "CI owner", "action": "Map existing pipeline",
             "evidence_needed": "Pipeline identifier"},
        ])

    def test_successful_local_checks_never_claim_company_qualification(self):
        required = {
            "source-worktree", "unit-tests", "manifest-validation", "source-checksums", "secret-scan",
            "network-attempt-intercept", "offline-fixtures", "bootstrap-rollback-tests", "golden-full-checks",
        }
        checks = [{"id": check_id, "status": "PASS"} for check_id in required]
        self.assertEqual(local_assessment_state(checks), "PRE_QUALIFICATION")
        checks[0]["status"] = "FAIL"
        self.assertEqual(local_assessment_state(checks), "ASSESSMENT_INCOMPLETE")

    def test_markdown_names_cross_platform_gaps_and_unsigned_scope(self):
        report = {
            "status": "PRE_QUALIFICATION",
            "repository": {"url": "https://example.invalid/repo"},
            "source": {"branch": "main", "commit": "abc", "worktree_clean": True},
            "checks": [],
            "full_project_checks": [],
            "assets": {"staged_groups": 0, "required_groups": 6, "qualification": "SOURCE_ONLY",
                       "source_manifest": {"sha256": "abc"}, "missing_groups": []},
            "dependencies": {"company_oss_clearance": "NOT_OBTAINED"},
            "company_actions": [],
            "cross_platform": {"host_os": "Darwin", "windows": "NOT_RUN_WINDOWS_HOST_REQUIRED",
                               "linux": "NOT_RUN_LINUX_HOST_REQUIRED", "scope": "native host only"},
        }
        text = render_markdown(report)
        self.assertIn("Windows: `NOT_RUN_WINDOWS_HOST_REQUIRED`", text)
        self.assertIn("Linux: `NOT_RUN_LINUX_HOST_REQUIRED`", text)
        self.assertIn("Local synthetic results are unsigned", text)

    def test_assessment_drops_credentials_from_child_environment(self):
        with patch.dict("os.environ", {
            "OPENAI_API_KEY": "secret-value",
            "GITHUB_TOKEN": "another-secret",
            "PATH": "/bin",
        }, clear=True):
            env = safe_environment()
        self.assertEqual(env["PATH"], "/bin")
        self.assertNotIn("OPENAI_API_KEY", env)
        self.assertNotIn("GITHUB_TOKEN", env)
        self.assertEqual(env["npm_config_offline"], "true")
        self.assertEqual(env["PIP_NO_INDEX"], "1")


if __name__ == "__main__":
    unittest.main()
