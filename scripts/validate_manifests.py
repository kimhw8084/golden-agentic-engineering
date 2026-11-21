#!/usr/bin/env python3
"""Offline structural checks for Golden's JSON manifests and OpenCode assets."""
from __future__ import annotations

import json
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
from golden_route import validation_errors as validate_route_references
from react_license_supplements import validate as validate_react_license_supplements


def read(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def validate_capability_types(registry: dict, schema: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(registry, dict) or not isinstance(schema, dict):
        return ['capability registry and schema roots must be objects']
    properties = schema.get('properties')
    candidate_property = properties.get('candidates') if isinstance(properties, dict) else None
    candidate_schema = candidate_property.get('items') if isinstance(candidate_property, dict) else None
    candidate_properties = candidate_schema.get('properties') if isinstance(candidate_schema, dict) else None
    required = candidate_schema.get('required', []) if isinstance(candidate_schema, dict) else []
    type_property = candidate_properties.get('capability_type') if isinstance(candidate_properties, dict) else None
    allowed = type_property.get('enum') if isinstance(type_property, dict) else None
    root_required = schema.get('required')
    minimum_candidates = candidate_property.get('minItems') if isinstance(candidate_property, dict) else None
    if (schema.get('type') != 'object' or not isinstance(properties, dict)
            or not isinstance(root_required, list) or not root_required
            or any(not isinstance(key, str) for key in root_required)
            or len(root_required) != len(set(root_required))
            or not isinstance(candidate_property, dict)
            or not isinstance(minimum_candidates, int) or isinstance(minimum_candidates, bool)
            or minimum_candidates < 0
            or not isinstance(candidate_properties, dict)
            or not isinstance(required, list) or not required
            or any(not isinstance(key, str) for key in required)
            or len(required) != len(set(required))
            or set(required) - set(candidate_properties)
            or not isinstance(type_property, dict) or type_property.get('type') != 'string'
            or not isinstance(allowed, list) or not allowed
            or any(not isinstance(value, str) or not value for value in allowed)
            or len(allowed) != len(set(allowed))
            or 'capability_type' not in required):
        return ['capability schema has invalid root/candidate fields, bounds, or capability_type enum']
    schema_id = properties.get('schema', {}).get('const') if isinstance(properties.get('schema'), dict) else None
    if registry.get('schema') != schema_id:
        errors.append('capability registry schema identifier does not match its JSON Schema')
    missing_root = [key for key in root_required if key not in registry]
    if missing_root:
        errors.append(f"capability registry is missing schema-required fields: {', '.join(missing_root)}")
    rows = registry.get('candidates')
    if not isinstance(rows, list):
        return errors + ['capability candidates must be an array of objects']
    if len(rows) < minimum_candidates:
        errors.append('capability candidate array is below the schema minimum')
    for row in rows:
        if not isinstance(row, dict):
            errors.append('capability candidate must be an object')
            continue
        for key in required:
            value = row.get(key)
            field_schema = candidate_properties.get(key)
            if (not isinstance(field_schema, dict) or field_schema.get('type') != 'string'
                    or not isinstance(value, str) or not value):
                errors.append(f"research candidate {row.get('id', 'unknown')}: {key} missing or invalid")
        kind = row.get('capability_type')
        if not isinstance(kind, str) or not kind:
            if 'capability_type' not in required:
                errors.append(f"research candidate {row.get('id', 'unknown')}: capability_type missing")
        elif kind not in allowed:
            errors.append(f"research candidate {row.get('id', 'unknown')}: unknown capability_type {kind}")
        commit = row.get('commit')
        if not isinstance(commit, str) or len(commit) != 40 or any(char not in '0123456789abcdefABCDEF' for char in commit):
            errors.append(f"research candidate {row.get('id', 'unknown')}: commit must be a full 40-character hex pin")
    return errors


def validate() -> list[str]:
    errors: list[str] = []
    errors.extend(validate_react_license_supplements(ROOT))
    required_json = [
        'standards/release.json', 'standards/rules.json', 'tools/candidates.json',
        '.opencode/opencode.json', 'workflows/task-routing.json',
        'opencode.json',
        'schemas/task-routing.schema.json', 'schemas/capability-selection.schema.json',
        'research/capability-selection.json',
        'benchmarks/cases.json',
        'integrations/mcp/github-enterprise-readonly.example.json',
        'offline/assets-manifest.json', 'offline/egress-policy.template.json',
    ]
    documents = {}
    for rel in required_json:
        try:
            documents[rel] = read(ROOT / rel)
        except (OSError, ValueError) as exc:
            errors.append(f'{rel}: invalid JSON or unreadable ({type(exc).__name__})')
    if errors:
        return errors
    non_object = [rel for rel, document in documents.items() if not isinstance(document, dict)]
    if non_object:
        return [f'{rel}: manifest root must be an object' for rel in non_object]
    release = documents['standards/release.json']
    rules = documents['standards/rules.json'].get('rules')
    if release.get('status') != 'PILOT_UNQUALIFIED':
        errors.append('release status must remain PILOT_UNQUALIFIED before company approval')
    if (not isinstance(rules, list) or len(rules) != 19
            or any(not isinstance(rule, dict) for rule in rules)
            or len({rule.get('id') for rule in rules if isinstance(rule, dict)}) != len(rules)):
        errors.append('baseline rules must contain 19 unique executable descriptors')
    else:
        for rule in rules:
            if rule.get('stage') not in ('fast', 'full') or not isinstance(rule.get('mandatory'), bool):
                errors.append(f"rule {rule.get('id')}: invalid stage/mandatory fields")
    candidates = documents['tools/candidates.json'].get('candidates')
    if (not isinstance(candidates, list) or len(candidates) != 64
            or any(not isinstance(candidate, dict) for candidate in candidates)
            or len({candidate.get('id') for candidate in candidates if isinstance(candidate, dict)}) != len(candidates)):
        errors.append('public-source baseline must contain 64 uniquely identified candidates')
    routing = documents['workflows/task-routing.json']
    workflows = routing.get('workflows')
    if routing.get('schema') != 'golden-task-routing/v2' or not isinstance(workflows, list) or len(workflows) != 12:
        errors.append('task routing must contain 12 workflows under golden-task-routing/v2')
    else:
        required = {'id', 'entry', 'complexity', 'primary_agent', 'skills', 'specialists', 'pattern', 'context', 'mcp', 'mcp_candidates', 'mcp_policy', 'deterministic_tools', 'trust', 'no_ai', 'outputs', 'acceptance'}
        for row in workflows:
            if not isinstance(row, dict) or not required <= row.keys():
                route_id = row.get('id') if isinstance(row, dict) else 'unknown'
                errors.append(f"workflow {route_id}: required routing fields missing")
        if len({row.get('id') for row in workflows if isinstance(row, dict)}) != len(workflows):
            errors.append('task-routing workflow IDs must be unique')
        errors.extend(validate_route_references(ROOT))
    registry = documents['research/capability-selection.json']
    capability_schema = documents['schemas/capability-selection.schema.json']
    errors.extend(validate_capability_types(registry, capability_schema))
    decisions = registry.get('task_decisions')
    if not isinstance(decisions, list) or len(decisions) < 12:
        errors.append('capability selection must include task decisions for all engineering workflow types')
    else:
        for decision in decisions:
            if (not isinstance(decision, dict)
                    or not all(decision.get(key) for key in ('task', 'ranked_candidates', 'current_choice', 'reason', 'measurement'))
                    or not isinstance(decision.get('ranked_candidates'), list)
                    or any(not isinstance(candidate, str) for candidate in decision['ranked_candidates'])):
                task_id = decision.get('task') if isinstance(decision, dict) else 'unknown'
                errors.append(f"capability decision {task_id}: selection evidence fields missing")
    route_ids = {row.get('id') for row in workflows if isinstance(row, dict)} if isinstance(workflows, list) else set()
    covered_routes = registry.get('workflow_routes_covered')
    if (not isinstance(covered_routes, list) or any(not isinstance(route_id, str) for route_id in covered_routes)
            or set(covered_routes) != route_ids):
        errors.append('capability registry must explicitly cover all 12 task-routing workflow IDs')
    registry_candidates = registry.get('candidates')
    if not isinstance(registry_candidates, list) or any(not isinstance(candidate, dict) for candidate in registry_candidates):
        errors.append('capability candidates must be an array of objects')
        registry_candidates = []
    candidate_id_values = [candidate.get('id') for candidate in registry_candidates if isinstance(candidate.get('id'), str)]
    candidate_ids = set(candidate_id_values)
    if len(candidate_ids) != len(registry_candidates):
        errors.append('capability candidate IDs must be nonempty and unique')
    non_public_values = registry.get('non_public_capability_ids')
    if not isinstance(non_public_values, list) or any(not isinstance(candidate, str) for candidate in non_public_values):
        errors.append('non-public capability IDs must be a string array')
        non_public_values = []
    non_public_ids = set(non_public_values)
    ranked_ids = {candidate for decision in decisions if isinstance(decision, dict)
                  for candidate in (decision.get('ranked_candidates') if isinstance(decision.get('ranked_candidates'), list) else [])
                  if isinstance(candidate, str)} if isinstance(decisions, list) else set()
    if ranked_ids - candidate_ids - non_public_ids:
        errors.append(f"capability ranking references unresolved IDs: {sorted(ranked_ids - candidate_ids - non_public_ids)}")
    benchmark_cases = documents['benchmarks/cases.json']
    tasks = benchmark_cases.get('tasks')
    if (benchmark_cases.get('schema') != 'golden-benchmark-cases/v1'
            or benchmark_cases.get('status') != 'LOCAL_FIXTURES_EXECUTED_COMPANY_RUNTIME_COMPARISON_BLOCKED'
            or not isinstance(tasks, list) or len(tasks) != 6
            or len({row.get('id') for row in tasks if isinstance(row, dict)}) != len(tasks)):
        errors.append('benchmark case manifest requires six uniquely identified local fixtures and an explicit company-runtime block')
    else:
        by_id = {row.get('id'): row for row in tasks if isinstance(row, dict)}
        for task in tasks:
            if (not isinstance(task, dict)
                    or not all(task.get(key) for key in ('id', 'fixture', 'acceptance', 'local_fixture_status'))
                    or not isinstance(task.get('evidence'), list)
                    or not task['evidence']):
                errors.append(f"benchmark case {task.get('id') if isinstance(task, dict) else 'unknown'}: acceptance, status and evidence are required")
                continue
            for evidence in task['evidence']:
                relative = evidence.partition('#')[0] if isinstance(evidence, str) else ''
                if (not relative or Path(relative).is_absolute() or '..' in Path(relative).parts
                        or not (ROOT / relative).is_file()):
                    errors.append(f"benchmark case {task['id']}: evidence must reference a repository file")
        react = by_id.get('react-feature', {})
        browser = by_id.get('browser-verification', {})
        if react.get('local_fixture_status') != 'PASS_MACOS_ARM64':
            errors.append('React benchmark status must reflect the committed local macOS arm64 pass')
        manual_smokes = set(browser.get('evidence', []))
        required_manual_smokes = {
            'verification/2026-11-20/react-browser-smoke.md',
            'verification/2026-11-20/nicegui-browser-smoke.md',
        }
        if (browser.get('local_fixture_status') != 'PARTIAL_MANUAL_REACT_AND_NICEGUI_SMOKES'
                or browser.get('automated_browser_status') != 'NOT_RUN_PLAYWRIGHT_ASSETS_NOT_STAGED'
                or not required_manual_smokes.issubset(manual_smokes)):
            errors.append('browser benchmark must distinguish manual smoke evidence from unrun automated browser checks')
    mcp_config = documents['opencode.json'].get('mcp', {})
    mcp = mcp_config.get('servers', {}) if isinstance(mcp_config, dict) else {}
    if not isinstance(mcp, dict):
        mcp = {}
    fixture = mcp.get('golden-synthetic-readonly')
    if not isinstance(fixture, dict) or fixture.get('disabled') is not True:
        errors.append('synthetic MCP fixture must exist and remain disabled')
    for config_name in ('opencode.json', '.opencode/opencode.json'):
        permissions = documents[config_name].get('permissions', [])
        denied = {(item.get('action'), item.get('resource'), item.get('effect'))
                  for item in permissions if isinstance(item, dict)}
        if not {('webfetch', '*', 'deny'), ('websearch', '*', 'deny')} <= denied:
            errors.append(f'{config_name}: public webfetch and websearch must be denied by project permissions')
    github_template = documents['integrations/mcp/github-enterprise-readonly.example.json']
    github_servers = github_template.get('mcp', {}).get('servers', {}) if isinstance(github_template.get('mcp'), dict) else {}
    github = github_servers.get('github-enterprise-readonly') if isinstance(github_servers, dict) else None
    github_env = github.get('environment', {}) if isinstance(github, dict) else {}
    github_command = github.get('command', []) if isinstance(github, dict) else []
    if (not isinstance(github, dict) or github.get('type') != 'local' or github.get('disabled') is not True
            or github.get('protocol') != 'legacy'
            or not isinstance(github_command, list) or len(github_command) != 5
            or github_command[0] != 'github-mcp-server'
            or github_command[1:] != ['stdio', '--read-only', '--toolsets', 'repos,issues,pull_requests,actions']
            or not isinstance(github_env, dict)
            or github_env.get('GITHUB_HOST') != 'https://replace-with-approved-internal-ghes-hostname.invalid'
            or github_env.get('GITHUB_PERSONAL_ACCESS_TOKEN') != '{env:GITHUB_PERSONAL_ACCESS_TOKEN}'):
        errors.append('GitHub MCP example must remain disabled, local, read-only, narrowly scoped, and use non-routable placeholders')
    assets = documents['offline/assets-manifest.json']
    asset_rows = assets.get('assets')
    required_asset_names = {
        'Python wheelhouse and dependency locks', 'React npm lock and offline store',
        'Playwright browser binaries', 'MCP Python SDK and transitive dependencies',
        'Company OpenCode and internal model evidence', 'OS-enforced no-public-egress policy and attempt monitor',
    }
    if assets.get('schema') != 'golden-offline-assets/v2' or not isinstance(asset_rows, list):
        errors.append('offline asset manifest has an unsupported schema or invalid assets field')
    else:
        asset_names = [item.get('name') for item in asset_rows if isinstance(item, dict)]
        if (len(asset_names) != len(asset_rows) or any(not isinstance(name, str) for name in asset_names)
                or len(asset_names) != len(set(asset_names)) or not required_asset_names <= set(asset_names)):
            errors.append('offline asset manifest must preserve all required asset groups without duplicate names')
        for item in asset_rows:
            if not isinstance(item, dict):
                continue
            if (item.get('status') not in ('STAGED', 'NOT_STAGED')
                    or not isinstance(item.get('platforms'), list) or not item['platforms']
                    or any(not isinstance(os_name, str) for os_name in item['platforms'])
                    or not isinstance(item.get('owner'), str) or not item['owner']
                    or not isinstance(item.get('required_action'), str) or not item['required_action']):
                errors.append(f"offline asset {item.get('name')}: invalid staging fields")
            if item.get('status') == 'STAGED' and (
                    not isinstance(item.get('required_targets'), list) or not item['required_targets']
                    or not isinstance(item.get('platform_artifacts'), list) or not item['platform_artifacts']):
                errors.append(f"offline asset {item.get('name')}: STAGED requires target-specific artifacts")
            partial_evidence = item.get('partial_evidence', [])
            if not isinstance(partial_evidence, list):
                errors.append(f"offline asset {item.get('name')}: partial_evidence must be a list")
                continue
            if partial_evidence and (item.get('status') != 'NOT_STAGED' or not isinstance(item.get('partial_progress'), str)):
                errors.append(f"offline asset {item.get('name')}: partial evidence must stay explicitly unqualified")
            for evidence in partial_evidence:
                if not isinstance(evidence, dict):
                    errors.append(f"offline asset {item.get('name')}: invalid partial evidence record")
                    continue
                relative = evidence.get('path')
                digest = evidence.get('sha256')
                if (not isinstance(relative, str) or not relative or '\\' in relative or ':' in relative
                        or Path(relative).is_absolute() or '..' in Path(relative).parts
                        or not isinstance(digest, str) or len(digest) != 64
                        or any(char not in '0123456789abcdef' for char in digest.lower())):
                    errors.append(f"offline asset {item.get('name')}: unsafe partial evidence path or digest")
                    continue
                artifact = ROOT / relative
                cursor = ROOT
                symlinked = False
                for part in Path(relative).parts:
                    cursor = cursor / part
                    if cursor.is_symlink():
                        symlinked = True
                        break
                try:
                    actual = hashlib.sha256(artifact.read_bytes()).hexdigest() if artifact.is_file() and not symlinked else None
                except OSError:
                    actual = None
                if actual != digest.lower():
                    errors.append(f"offline asset {item.get('name')}: partial evidence missing or hash mismatch")
            if item.get('status') == 'STAGED':
                digest = item.get('sha256')
                asset_path = item.get('path')
                if (not isinstance(asset_path, str) or not asset_path or '\\' in asset_path
                        or asset_path.startswith('/') or '..' in Path(asset_path).parts
                        or not isinstance(digest, str) or len(digest) != 64
                        or any(char not in '0123456789abcdef' for char in digest.lower())
                        or item.get('license_review_status') not in ('APPROVED', 'PENDING')):
                    errors.append(f"offline asset {item.get('name')}: staged assets require a safe path, SHA-256 and license state")
    egress = documents['offline/egress-policy.template.json']
    if (egress.get('schema') != 'golden-egress-policy/v1' or egress.get('enforcement') != 'DEFAULT_DENY'
            or egress.get('allowed_destinations') != [] or egress.get('status') != 'TEMPLATE_ONLY_NOT_APPLIED'):
        errors.append('egress policy template must remain empty-allowlist default deny and unapplied')
    opencode_env = egress.get('required_opencode_environment', {}).get('variables', {})
    if (opencode_env.get('OPENCODE_DISABLE_AUTOUPDATE') != '1'
            or opencode_env.get('OPENCODE_DISABLE_MODELS_FETCH') != '1'
            or not any(item == {'action': 'webfetch', 'resource': '*', 'effect': 'deny'}
                       for item in egress.get('project_tool_permissions', []))
            or not any(item == {'action': 'websearch', 'resource': '*', 'effect': 'deny'}
                       for item in egress.get('project_tool_permissions', []))):
        errors.append('egress template must disable OpenCode update/catalog checks and deny public web tools')
    for root, expected in (('agents', 5), ('skills', 12), ('commands', 7)):
        folder = ROOT / '.opencode' / root
        files = sorted(folder.rglob('*.md'))
        if len(files) != expected:
            errors.append(f'.opencode/{root}: expected {expected} Markdown files, found {len(files)}')
    for path in sorted((ROOT / '.opencode' / 'skills').glob('*/SKILL.md')):
        content = path.read_text(encoding='utf-8')
        if not content.startswith('---\n') or '\nname:' not in content.split('---', 2)[1] or '\ndescription:' not in content.split('---', 2)[1]:
            errors.append(f'{path.relative_to(ROOT)}: skill frontmatter requires name and description')
    manifests = [ROOT / 'examples' / 'python-app' / 'golden.project.json', ROOT / 'examples' / 'nicegui-app' / 'golden.project.json', ROOT / 'examples' / 'react-app' / 'golden.project.json']
    for path in manifests:
        try:
            data = read(path)
            if not isinstance(data, dict):
                errors.append(f'{path.relative_to(ROOT)}: manifest root must be an object')
                continue
            if data.get('golden_version') != release.get('version'):
                errors.append(f'{path.relative_to(ROOT)}: Golden pin does not match release')
            if not isinstance(data.get('capabilities'), dict) or not isinstance(data.get('commands'), dict):
                errors.append(f'{path.relative_to(ROOT)}: invalid project manifest fields')
        except (OSError, ValueError) as exc:
            errors.append(f'{path.relative_to(ROOT)}: invalid JSON ({type(exc).__name__})')
    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print('FAIL', error)
        return 2
    selection = read(ROOT / 'research' / 'capability-selection.json')
    print(f"MANIFEST_VALIDATION_PASS rules=19 candidates=64 workflows=12 agents=5 skills=12 commands=7 capability_candidates={len(selection.get('candidates', []))} task_decisions={len(selection.get('task_decisions', []))} react_license_supplements=3 unresolved=1")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
