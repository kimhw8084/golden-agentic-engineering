#!/usr/bin/env python3
"""Offline structural checks for Golden's JSON manifests and OpenCode assets."""
from __future__ import annotations

import json
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
from golden_route import validation_errors as validate_route_references


def read(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def validate() -> list[str]:
    errors: list[str] = []
    required_json = [
        'standards/release.json', 'standards/rules.json', 'tools/candidates.json',
        '.opencode/opencode.json', 'workflows/task-routing.json',
        'opencode.json',
        'schemas/task-routing.schema.json', 'research/capability-selection.json',
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
    candidate_ids = {candidate.get('id') for candidate in registry_candidates if isinstance(candidate.get('id'), str)}
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
    for candidate in registry_candidates:
        for key in ('id', 'owner_repo', 'commit', 'license', 'license_evidence', 'license_url', 'transitive_dependencies', 'windows_linux', 'offline_telemetry', 'context_cost', 'permissions', 'prompt_injection_security', 'measured_evidence', 'decision'):
            if not candidate.get(key):
                errors.append(f"research candidate {candidate.get('id')}: {key} missing")
        if not isinstance(candidate.get('commit'), str) or len(candidate['commit']) != 40 or any(c not in '0123456789abcdef' for c in candidate['commit'].lower()):
            errors.append(f"research candidate {candidate.get('id')}: commit must be a full 40-character hex pin")
    mcp_config = documents['opencode.json'].get('mcp', {})
    mcp = mcp_config.get('servers', {}) if isinstance(mcp_config, dict) else {}
    if not isinstance(mcp, dict):
        mcp = {}
    fixture = mcp.get('golden-synthetic-readonly')
    if not isinstance(fixture, dict) or fixture.get('disabled') is not True:
        errors.append('synthetic MCP fixture must exist and remain disabled')
    assets = documents['offline/assets-manifest.json']
    asset_rows = assets.get('assets')
    required_asset_names = {
        'Python wheelhouse and dependency locks', 'React npm lock and offline store',
        'Playwright browser binaries', 'MCP Python SDK and transitive dependencies',
        'Company OpenCode and internal model evidence', 'OS-enforced no-public-egress policy and attempt monitor',
    }
    if assets.get('schema') != 'golden-offline-assets/v1' or not isinstance(asset_rows, list):
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
    print(f"MANIFEST_VALIDATION_PASS rules=19 candidates=64 workflows=12 agents=5 skills=12 commands=7 capability_candidates={len(selection.get('candidates', []))} task_decisions={len(selection.get('task_decisions', []))}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
