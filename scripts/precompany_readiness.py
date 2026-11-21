#!/usr/bin/env python3
"""Run local pre-company checks and emit a fail-closed readiness report.

This command never starts OpenCode, calls a model, or uses a public service. Npm
and Python package acquisition are forced offline. A successful local assessment
is still PRE_QUALIFICATION until company-owned evidence is supplied.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = (
    "examples/python-app",
    "examples/react-app",
    "examples/nicegui-app",
)
OFFLINE_ENV = {
    "PYTHONNOUSERSITE": "1",
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHONUTF8": "1",
    "PIP_NO_INDEX": "1",
    "UV_OFFLINE": "1",
    "npm_config_offline": "true",
    "npm_config_fetch_retries": "0",
    "npm_config_audit": "false",
    "npm_config_fund": "false",
    "npm_config_update_notifier": "false",
    "HF_HUB_OFFLINE": "1",
    "HF_HUB_DISABLE_TELEMETRY": "1",
    "DO_NOT_TRACK": "1",
    "GIT_TERMINAL_PROMPT": "0",
    "GIT_CONFIG_NOSYSTEM": "1",
}
ENV_ALLOWLIST = (
    "PATH", "HOME", "USERPROFILE", "SYSTEMROOT", "WINDIR", "TEMP", "TMP",
    "APPDATA", "LOCALAPPDATA",
)


def safe_environment() -> dict[str, str]:
    """Keep normal tool paths/cache locations while dropping credential env vars."""
    result = {key: os.environ[key] for key in ENV_ALLOWLIST if os.environ.get(key)}
    result.update(OFFLINE_ENV)
    return result


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object")
    return value


def run_process(check_id: str, display_command: str, argv: list[str], *,
                timeout: int = 180, cwd: Path = ROOT) -> dict:
    """Capture only process metadata and an output digest; never persist raw logs."""
    started = time.perf_counter()
    try:
        result = subprocess.run(
            argv, cwd=cwd, env=safe_environment(), capture_output=True,
            text=True, encoding="utf-8", errors="replace", timeout=timeout,
            check=False,
        )
        output = result.stdout + "\n" + result.stderr
        return {
            "id": check_id,
            "command": display_command,
            "exit_code": result.returncode,
            "elapsed_seconds": round(time.perf_counter() - started, 6),
            "output_bytes": len(output.encode("utf-8")),
            "output_sha256": sha256(output.encode("utf-8")),
            "status": "EXECUTED",
            "_captured_output": output,
        }
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout or ""
        err = exc.stderr or ""
        if isinstance(out, bytes):
            out = out.decode("utf-8", errors="replace")
        if isinstance(err, bytes):
            err = err.decode("utf-8", errors="replace")
        output = out + "\n" + err
        return {
            "id": check_id,
            "command": display_command,
            "exit_code": None,
            "elapsed_seconds": round(time.perf_counter() - started, 6),
            "output_bytes": len(output.encode("utf-8")),
            "output_sha256": sha256(output.encode("utf-8")),
            "status": "TIMEOUT",
            "_captured_output": output,
        }
    except (OSError, ValueError) as exc:
        return {
            "id": check_id,
            "command": display_command,
            "exit_code": None,
            "elapsed_seconds": round(time.perf_counter() - started, 6),
            "output_bytes": 0,
            "output_sha256": None,
            "status": "NOT_RUN",
            "error_type": type(exc).__name__,
        }


def parse_unittest_summary(output: str) -> dict:
    ran = re.search(r"Ran (\d+) tests?", output)
    skipped = re.search(r"OK \(skipped=(\d+)\)", output)
    failed = re.search(r"FAILED \(failures=(\d+)(?:, errors=(\d+))?\)", output)
    return {
        "tests_run": int(ran.group(1)) if ran else None,
        "tests_skipped": int(skipped.group(1)) if skipped else 0,
        "tests_failed": (int(failed.group(1)) + int(failed.group(2) or 0)) if failed else 0,
        "summary_found": ran is not None,
    }


def parse_company_actions(markdown: str) -> list[dict[str, str]]:
    """Read the owner/action/evidence columns from the checked-in blocker table."""
    actions = []
    for line in markdown.splitlines():
        if not line.startswith("| P"):
            continue
        columns = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(columns) == 4 and columns[0] in {"P0", "P1", "P2"}:
            actions.append({
                "priority": columns[0],
                "owner": columns[1],
                "action": columns[2],
                "evidence_needed": columns[3],
            })
    return actions


def classify_full_check(exit_code: int | None, evidence: dict | None) -> dict:
    """Keep non-qualification distinct from a runner failure or a pass."""
    rows = evidence.get("results") if isinstance(evidence, dict) else None
    valid_rows = (isinstance(rows, list) and len(rows) == 19
                  and all(isinstance(row, dict) and isinstance(row.get("rule_id"), str)
                          and isinstance(row.get("status"), str) for row in rows)
                  and len({row["rule_id"] for row in rows}) == len(rows))
    statuses = ([{"rule_id": row["rule_id"], "status": row["status"],
                  "mandatory": row.get("mandatory")} for row in rows] if valid_rows else [])
    if (isinstance(evidence, dict) and evidence.get("mode") == "FULL"
            and evidence.get("rules_count") == 19 and valid_rows
            and evidence.get("qualifies_release") is False
            and isinstance(evidence.get("blocking_rule_ids"), list)
            and evidence["blocking_rule_ids"] and exit_code == 2):
        return {
            "status": "NOT_QUALIFIED",
            "qualifies_release": False,
            "blocking_rule_ids": evidence["blocking_rule_ids"],
            "rule_statuses": statuses,
        }
    if (isinstance(evidence, dict) and evidence.get("mode") == "FULL"
            and evidence.get("rules_count") == 19 and valid_rows
            and evidence.get("qualifies_release") is True and exit_code == 0):
        return {"status": "QUALIFIED_LOCAL_FIXTURE", "qualifies_release": True,
                "blocking_rule_ids": [], "rule_statuses": statuses}
    return {"status": "RUNNER_ERROR", "qualifies_release": False,
            "blocking_rule_ids": []}


def local_assessment_state(checks: list[dict]) -> str:
    required = {"source-worktree", "unit-tests", "manifest-validation", "source-checksums",
                "secret-scan", "network-attempt-intercept", "offline-fixtures",
                "bootstrap-rollback-tests", "golden-full-checks"}
    by_id = {check.get("id"): check for check in checks}
    if any(by_id.get(check_id, {}).get("status") != "PASS" for check_id in required):
        return "ASSESSMENT_INCOMPLETE"
    # This tool intentionally cannot grant company qualification.
    return "PRE_QUALIFICATION"


def _git_value(*args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), *args], env=safe_environment(),
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=10, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def source_identity() -> dict:
    commit = _git_value("rev-parse", "HEAD")
    branch = _git_value("branch", "--show-current")
    status = _git_value("status", "--porcelain")
    try:
        checksums_digest = sha256((ROOT / "SHA256SUMS.txt").read_bytes())
    except OSError:
        checksums_digest = None
    return {
        "commit": commit,
        "branch": branch or "DETACHED_OR_UNKNOWN",
        "worktree_clean": status == "",
        "changed_path_count": len(status.splitlines()) if status else 0,
        "sha256sums_manifest_sha256": checksums_digest,
    }


def _evidence_check(process: dict, *, passed: bool, detail: dict | None = None) -> dict:
    result = dict(process)
    result.pop("_captured_output", None)
    result["status"] = "PASS" if passed else "FAIL"
    if detail:
        result.update(detail)
    return result


def _parse_json_if_file(path: Path) -> dict | None:
    try:
        return read_json(path)
    except (OSError, ValueError):
        return None


def collect_local_checks(temp: Path) -> tuple[list[dict], dict]:
    checks: list[dict] = []

    git_status = _git_value("status", "--porcelain")
    checks.append({
        "id": "source-worktree",
        "command": "git status --porcelain (must be empty)",
        "status": "PASS" if git_status == "" else "FAIL",
        "exit_code": 0 if git_status is not None else None,
        "changed_path_count": len(git_status.splitlines()) if git_status else 0,
        "output_sha256": sha256((git_status or "").encode("utf-8")) if git_status is not None else None,
    })

    def capture(check_id: str, display: str, argv: list[str], timeout: int = 180) -> tuple[dict, str]:
        process = run_process(check_id, display, argv, timeout=timeout)
        output = process.pop("_captured_output", "")
        return process, output

    unit_argv = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"]
    unit_process, unit_output = capture("unit-tests", "python -m unittest discover -s tests -q", unit_argv, 240)
    unit_summary = parse_unittest_summary(unit_output)
    checks.append(_evidence_check(
        unit_process,
        passed=unit_process.get("exit_code") == 0 and unit_summary["summary_found"]
        and unit_summary["tests_failed"] == 0,
        detail=unit_summary,
    ))

    rollback_argv = [sys.executable, "-m", "unittest", "discover", "-s", "tests",
                     "-p", "test_bootstrap_and_fixtures.py", "-q"]
    rollback_process, rollback_output = capture(
        "bootstrap-rollback-tests",
        "python -m unittest discover -s tests -p test_bootstrap_and_fixtures.py -q",
        rollback_argv, 180,
    )
    rollback_summary = parse_unittest_summary(rollback_output)
    checks.append(_evidence_check(
        rollback_process,
        passed=rollback_process.get("exit_code") == 0 and rollback_summary["summary_found"]
        and rollback_summary["tests_failed"] == 0,
        detail={**rollback_summary, "scope": "Synthetic bootstrap apply/rollback tests; not company rollback evidence."},
    ))

    manifest_argv = [sys.executable, "scripts/validate_manifests.py"]
    manifest_process, manifest_output = capture("manifest-validation", "python scripts/validate_manifests.py", manifest_argv, 90)
    checks.append(_evidence_check(
        manifest_process,
        passed=manifest_process.get("exit_code") == 0 and "MANIFEST_VALIDATION_PASS" in manifest_output,
    ))

    checksum_argv = [sys.executable, "scripts/verify_contents.py"]
    checksum_process, checksum_output = capture("source-checksums", "python scripts/verify_contents.py", checksum_argv, 90)
    checks.append(_evidence_check(
        checksum_process,
        passed=checksum_process.get("exit_code") == 0
        and re.search(r"missing=0; altered=0; unlisted=0", checksum_output) is not None,
    ))

    security_argv = [sys.executable, "scripts/security_scan.py", "--repo", str(ROOT), "--history"]
    security_process, security_output = capture(
        "secret-scan", "python scripts/security_scan.py --repo . --history", security_argv, 180,
    )
    scan_match = re.search(r"SECRET_PATTERN_SCAN_PASS scanned_files=(\d+)(?: scanned_history_blobs=(\d+))?", security_output)
    checks.append(_evidence_check(
        security_process,
        passed=security_process.get("exit_code") == 0 and scan_match is not None,
        detail={"scanned_files": int(scan_match.group(1)) if scan_match else None,
                "reachable_git_blobs": int(scan_match.group(2)) if scan_match and scan_match.group(2) else None,
                "scope": "High-confidence patterns only; not proof that proprietary material is absent."},
    ))

    network_argv = [sys.executable, "scripts/network_attempt_monitor.py"]
    network_process, network_output = capture(
        "network-attempt-intercept", "python scripts/network_attempt_monitor.py", network_argv, 15,
    )
    checks.append(_evidence_check(
        network_process,
        passed=network_process.get("exit_code") == 0 and "NETWORK_LOOPBACK_AUDIT_INTERCEPT_PASS" in network_output,
        detail={"scope": "One CPython loopback connect is blocked before socket operation; not OS firewall or child-process monitoring."},
    ))

    fixture_path = temp / "local-fixtures.json"
    fixture_argv = [sys.executable, "benchmarks/run_local_fixtures.py", "--out", str(fixture_path),
                    "--include-react", "--include-nicegui-ui"]
    fixture_process = run_process(
        "offline-fixtures",
        "python benchmarks/run_local_fixtures.py --include-react --include-nicegui-ui",
        fixture_argv, timeout=360,
    )
    fixture_data = _parse_json_if_file(fixture_path)
    fixture_cases = fixture_data.get("cases", []) if fixture_data else []
    case_tests = sum(row.get("tests_run") or 0 for row in fixture_cases if isinstance(row, dict))
    react = fixture_data.get("react", {}) if fixture_data else {}
    nicegui = fixture_data.get("nicegui_ui", {}) if fixture_data else {}
    fixture_pass = (fixture_process.get("exit_code") == 0 and fixture_data is not None
                    and fixture_data.get("status") == "PASS"
                    and all(row.get("status") == "PASS" for row in fixture_cases if isinstance(row, dict)))
    checks.append(_evidence_check(
        fixture_process, passed=fixture_pass,
        detail={"fixture_cases": len(fixture_cases), "python_fixture_tests": case_tests,
                "react_status": react.get("status", "NOT_RUN"),
                "react_tests": react.get("tests_run"),
                "nicegui_ui_status": nicegui.get("status", "NOT_RUN"),
                "nicegui_ui_tests": nicegui.get("tests_run"),
                "browser_status": (fixture_data.get("browser", {}).get("status", "NOT_RUN")
                                   if fixture_data else "NOT_RUN"),
                "scope": fixture_data.get("scope") if fixture_data else "Fixture report was not produced."},
    ))

    full_checks = []
    for project in PROJECTS:
        evidence_path = temp / (Path(project).name + "-full.json")
        display = f"python scripts/golden.py check --full --project {project}"
        argv = [sys.executable, "scripts/golden.py", "check", "--full", "--project", project,
                "--out", str(evidence_path)]
        process = run_process(f"golden-full-{Path(project).name}", display, argv, timeout=240)
        evidence = _parse_json_if_file(evidence_path)
        outcome = classify_full_check(process.get("exit_code"), evidence)
        rule_status_counts = {}
        for rule in outcome.get("rule_statuses", []):
            status = rule["status"]
            rule_status_counts[status] = rule_status_counts.get(status, 0) + 1
        full_checks.append({
            **outcome,
            "project": project,
            "rules_count": evidence.get("rules_count") if evidence else None,
            "rule_status_counts": rule_status_counts,
            "output_sha256": process.get("output_sha256"),
            "elapsed_seconds": process.get("elapsed_seconds"),
        })
    full_checks_valid = (len(full_checks) == len(PROJECTS)
                         and all(row.get("status") in {"NOT_QUALIFIED", "QUALIFIED_LOCAL_FIXTURE"}
                                 for row in full_checks))
    checks.append({
        "id": "golden-full-checks",
        "command": "python scripts/golden.py check --full on Python, React, and NiceGUI fixtures",
        "status": "PASS" if full_checks_valid else "FAIL",
        "exit_code": 0 if full_checks_valid else None,
        "projects_run": len(full_checks),
        "not_qualified_projects": sum(row.get("status") == "NOT_QUALIFIED" for row in full_checks),
        "runner_errors": sum(row.get("status") == "RUNNER_ERROR" for row in full_checks),
    })
    return checks, {"golden_full_checks": full_checks, "fixture_report_sha256": sha256(fixture_path.read_bytes()) if fixture_path.is_file() else None}


def collect_state(root: Path, checks: list[dict], full_results: dict) -> dict:
    base = read_json(root / "PRECOMPANY_EVIDENCE.json")
    inventory = read_json(root / "OFFLINE_ASSET_INVENTORY.json")
    lock_audit = read_json(root / "research/react-macos-arm64-dependency-audit.json")
    license_report = read_json(root / "research/react-license-supplements.json")
    blockers_text = (root / "COMPANY_ONLY_BLOCKERS.md").read_text(encoding="utf-8")
    assets = inventory.get("assets", [])
    staged = [item for item in assets if item.get("status") == "STAGED"]
    missing = [item for item in assets if item.get("status") != "STAGED"]
    unresolved = license_report.get("unresolved", [])
    return {
        "repository": base.get("repository", {}),
        "source": source_identity(),
        "assets": {
            "qualification": inventory.get("overall_status"),
            "source_manifest": inventory.get("source_manifest", {}),
            "required_groups": len(assets),
            "staged_groups": len(staged),
            "missing_groups": [{"name": row.get("name"), "owner": row.get("owner"),
                                "required_action": row.get("required_action")} for row in missing],
            "required_company_targets": inventory.get("required_company_targets", {}),
            "fab_sampling": inventory.get("fab_sampling_transfer_kit", {}),
        },
        "dependencies": {
            "react_locked_entries": lock_audit.get("counts", {}).get("locked_entries"),
            "react_packages_without_tarball_license_files": lock_audit.get("counts", {}).get("license_files_missing"),
            "unresolved_license_packages": [
                {"package": row.get("package"), "version": row.get("version"),
                 "status": row.get("status"),
                 "license_declaration_verified": row.get("license_declaration_verified", False),
                 "source_repository": row.get("source_repository"),
                 "source_commit": row.get("source_commit"),
                 "embedded_notice": row.get("embedded_notice"),
                 "required_action": row.get("required_action")}
                for row in unresolved if isinstance(row, dict)
            ],
            "company_oss_clearance": "NOT_OBTAINED",
        },
        "runtime": {
            "local_probe": base.get("runtime_probe", {}),
            "company_internal_model_or_mcp": "NOT_RUN",
            "company_agent_benchmark": "BLOCKED_COMPANY_RUNTIME",
        },
        "cross_platform": {
            "host_os": platform.system(),
            "windows": "TESTED_ON_HOST" if platform.system() == "Windows" else "NOT_RUN_WINDOWS_HOST_REQUIRED",
            "linux": "TESTED_ON_HOST" if platform.system() == "Linux" else "NOT_RUN_LINUX_HOST_REQUIRED",
            "scope": "This assessment reports only the native host OS; macOS results do not qualify Windows or Linux.",
        },
        "rollback_recovery": {
            "synthetic_tests": next((row for row in checks if row.get("id") == "bootstrap-rollback-tests"), {}),
            "company_rollback_drill": "NOT_RUN",
        },
        "full_project_checks": full_results["golden_full_checks"],
        "local_fixture_report_sha256": full_results.get("fixture_report_sha256"),
        "company_actions": parse_company_actions(blockers_text),
        "qualification_record": base.get("qualification", {}),
    }


def render_markdown(report: dict) -> str:
    source = report.get("source", {})
    lines = [
        "# Pre-company readiness assessment",
        "",
        f"**Status: `{report['status']}`.** This assessment runs offline local checks only and cannot approve company software or qualify a company host.",
        "",
        "## Source revision",
        "",
        f"- Repository: {report.get('repository', {}).get('url', 'unknown')}",
        f"- Branch: `{source.get('branch', 'unknown')}`",
        f"- Commit: `{source.get('commit', 'unknown')}`",
        f"- Worktree clean: `{source.get('worktree_clean')}`",
        f"- `SHA256SUMS.txt` SHA-256: `{source.get('sha256sums_manifest_sha256', 'unknown')}`",
        "",
        "## Local checks",
        "",
        "| Check | Result | Evidence |",
        "|---|---|---|",
    ]
    for check in report.get("checks", []):
        details = []
        if check.get("tests_run") is not None:
            details.append(f"tests={check['tests_run']}")
        if check.get("fixture_cases") is not None:
            details.append(f"fixture_cases={check['fixture_cases']}")
        if check.get("react_status"):
            details.append(f"React={check['react_status']}")
        if check.get("nicegui_ui_status"):
            details.append(f"NiceGUI UI={check['nicegui_ui_status']}")
        if check.get("output_sha256"):
            details.append(f"output SHA-256 `{check['output_sha256']}`")
        lines.append(f"| `{check.get('id')}` | **{check.get('status')}** | {', '.join(details) or 'No output details'} |")
    lines += ["", "## Golden full checks", "", "| Project | State | Blocking rule IDs |", "|---|---|---|"]
    for item in report.get("full_project_checks", []):
        rules = ", ".join(item.get("blocking_rule_ids", [])) or "—"
        lines.append(f"| `{item.get('project')}` | **{item.get('status')}** | {rules} |")
    assets = report.get("assets", {})
    cross_platform = report.get("cross_platform", {})
    lines += [
        "", "## Offline assets and licenses", "",
        f"- Offline asset groups staged: {assets.get('staged_groups', 0)}/{assets.get('required_groups', 0)}.",
        f"- Offline state: `{assets.get('qualification', 'UNKNOWN')}`.",
        f"- Source asset-manifest SHA-256: `{assets.get('source_manifest', {}).get('sha256', 'unknown')}`.",
        f"- Company OSS clearance: `{report.get('dependencies', {}).get('company_oss_clearance', 'UNKNOWN')}`.",
    ]
    for item in assets.get("missing_groups", []):
        lines.append(f"- Missing **{item.get('name')}** ({item.get('owner')}): {item.get('required_action')}")
    lines += ["", "## Company-owned actions", ""]
    for action in report.get("company_actions", []):
        lines.append(f"- **{action['priority']} — {action['owner']}:** {action['action']} Evidence: {action['evidence_needed']}")
    lines += [
        "", "## Cross-platform execution", "",
        f"- Native host tested: `{cross_platform.get('host_os', 'UNKNOWN')}`.",
        f"- Windows: `{cross_platform.get('windows', 'UNKNOWN')}`.",
        f"- Linux: `{cross_platform.get('linux', 'UNKNOWN')}`.",
        f"- Scope: {cross_platform.get('scope', 'Unknown')}.",
        "", "## Limitations", "",
        "- No OpenCode process or model was started by this command; no authentic company agent, skill, MCP, or benchmark trace was collected.",
        "- The network probe blocks one CPython loopback connection before the socket operation. It does not measure public egress or monitor other processes.",
        "- Secret scanning covers high-confidence patterns only; it does not prove that proprietary information is absent.",
        "- Local synthetic results are unsigned and are not company approval, cross-platform qualification, or production authorization.",
        "",
    ]
    return "\n".join(lines)


def make_report(root: Path = ROOT) -> dict:
    with tempfile.TemporaryDirectory(prefix="golden-precompany-") as directory:
        temp = Path(directory)
        checks, full_results = collect_local_checks(temp)
        state = collect_state(root, checks, full_results)
        status = local_assessment_state(checks)
        if not state.get("source", {}).get("worktree_clean"):
            for check in checks:
                if check.get("id") == "source-worktree":
                    check["status"] = "FAIL"
                    break
            status = "ASSESSMENT_INCOMPLETE"
        critical_failures = [row.get("id") for row in checks if row.get("status") != "PASS"]
        return {
            "schema": "golden-precompany-readiness/v1",
            "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "status": status,
            "status_explanation": (
                "ASSESSMENT_INCOMPLETE means one or more local checks did not produce valid PASS evidence. "
                "PRE_QUALIFICATION means local checks ran, while company-owned requirements remain unverified."
            ),
            "environment": {"os": platform.system(), "architecture": platform.machine(),
                            "python": platform.python_version()},
            "repository": state.pop("repository"),
            "source": state.pop("source"),
            "checks": checks,
            "local_check_failures": critical_failures,
            "full_project_checks": state.pop("full_project_checks"),
            "network_policy": {
                "tool_env_forces_offline_package_operations": True,
                "this_command_attempted_public_network": False,
                "attempt_monitor_scope": "One CPython loopback connect only; not OS firewall or child-process monitoring.",
            },
            **state,
        }


def _default_paths() -> tuple[Path, Path]:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = Path(tempfile.gettempdir()) / f"golden-precompany-readiness-{stamp}-{os.getpid()}"
    return base.with_suffix(".json"), base.with_suffix(".md")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="Machine-readable JSON output (default: unique temp path).")
    parser.add_argument("--report", type=Path, help="Human-readable Markdown output (default: matching temp path).")
    args = parser.parse_args()
    default_json, default_markdown = _default_paths()
    json_path = args.out or default_json
    markdown_path = args.report or (args.out.with_suffix(".md") if args.out else default_markdown)
    try:
        root_path = ROOT.resolve()
        resolved_outputs = [json_path.resolve(), markdown_path.resolve()]
        if (resolved_outputs[0] == resolved_outputs[1]
                or any(path == root_path or root_path in path.parents for path in resolved_outputs)):
            raise ValueError("Assessment reports must use distinct paths outside the source tree.")
        report = make_report()
        json_text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
        markdown_text = render_markdown(report)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json_text, encoding="utf-8")
        markdown_path.write_text(markdown_text, encoding="utf-8")
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"PRECOMPANY_ASSESSMENT_ERROR kind={type(exc).__name__}", file=sys.stderr)
        return 3
    passing = sum(row.get("status") == "PASS" for row in report["checks"])
    print(f"{report['status']} checks_pass={passing}/{len(report['checks'])} "
          f"json={json_path} report={markdown_path}")
    if report["status"] == "ASSESSMENT_INCOMPLETE":
        return 3
    # The local assessment has no authority or evidence source to certify a company host.
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
