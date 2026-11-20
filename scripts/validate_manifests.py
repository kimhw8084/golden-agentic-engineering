#!/usr/bin/env python3
"""Offline structural checks for Golden's JSON manifests and OpenCode assets."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


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
    release = documents['standards/release.json']
    rules = documents['standards/rules.json'].get('rules')
    if release.get('status') != 'PILOT_UNQUALIFIED':
        errors.append('release status must remain PILOT_UNQUALIFIED before company approval')
    if not isinstance(rules, list) or len(rules) != 19 or len({r.get('id') for r in rules}) != len(rules):
        errors.append('baseline rules must contain 19 unique executable descriptors')
    else:
        for rule in rules:
            if rule.get('stage') not in ('fast', 'full') or not isinstance(rule.get('mandatory'), bool):
                errors.append(f"rule {rule.get('id')}: invalid stage/mandatory fields")
    candidates = documents['tools/candidates.json'].get('candidates')
    if not isinstance(candidates, list) or len(candidates) != 64 or len({c.get('id') for c in candidates}) != len(candidates):
        errors.append('public-source baseline must contain 64 uniquely identified candidates')
    routing = documents['workflows/task-routing.json']
    workflows = routing.get('workflows')
    if routing.get('schema') != 'golden-task-routing/v1' or not isinstance(workflows, list) or len(workflows) != 12:
        errors.append('task routing must contain 12 workflows under golden-task-routing/v1')
    else:
        required = {'id', 'entry', 'complexity', 'primary_agent', 'skill', 'pattern', 'context', 'mcp', 'deterministic_tools', 'trust', 'no_ai', 'outputs', 'acceptance'}
        for row in workflows:
            if not required <= row.keys():
                errors.append(f"workflow {row.get('id')}: required routing fields missing")
        if len({row.get('id') for row in workflows}) != len(workflows):
            errors.append('task-routing workflow IDs must be unique')
    registry = documents['research/capability-selection.json']
    decisions = registry.get('task_decisions')
    if not isinstance(decisions, list) or len(decisions) < 12:
        errors.append('capability selection must include task decisions for all engineering workflow types')
    else:
        for decision in decisions:
            if not all(decision.get(key) for key in ('task', 'ranked_candidates', 'current_choice', 'reason', 'measurement')) or not isinstance(decision.get('ranked_candidates'), list):
                errors.append(f"capability decision {decision.get('task')}: selection evidence fields missing")
    route_ids = {row.get('id') for row in workflows} if isinstance(workflows, list) else set()
    covered_routes = registry.get('workflow_routes_covered')
    if not isinstance(covered_routes, list) or set(covered_routes) != route_ids:
        errors.append('capability registry must explicitly cover all 12 task-routing workflow IDs')
    candidate_ids = {candidate.get('id') for candidate in registry.get('candidates', [])}
    non_public_ids = set(registry.get('non_public_capability_ids', []))
    ranked_ids = {candidate for decision in decisions for candidate in decision.get('ranked_candidates', [])} if isinstance(decisions, list) else set()
    if ranked_ids - candidate_ids - non_public_ids:
        errors.append(f"capability ranking references unresolved IDs: {sorted(ranked_ids - candidate_ids - non_public_ids)}")
    for candidate in registry.get('candidates', []):
        for key in ('id', 'owner_repo', 'commit', 'license', 'license_evidence', 'license_url', 'transitive_dependencies', 'windows_linux', 'offline_telemetry', 'context_cost', 'permissions', 'prompt_injection_security', 'measured_evidence', 'decision'):
            if not candidate.get(key):
                errors.append(f"research candidate {candidate.get('id')}: {key} missing")
        if not isinstance(candidate.get('commit'), str) or len(candidate['commit']) != 40 or any(c not in '0123456789abcdef' for c in candidate['commit'].lower()):
            errors.append(f"research candidate {candidate.get('id')}: commit must be a full 40-character hex pin")
    mcp = documents['opencode.json'].get('mcp', {}).get('servers', {})
    fixture = mcp.get('golden-synthetic-readonly')
    if not isinstance(fixture, dict) or fixture.get('disabled') is not True:
        errors.append('synthetic MCP fixture must exist and remain disabled')
    for root, expected in (('agents', 5), ('skills', 12), ('commands', 6)):
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
    print(f"MANIFEST_VALIDATION_PASS rules=19 candidates=64 workflows=12 agents=5 skills=12 commands=6 capability_candidates={len(selection.get('candidates', []))} task_decisions={len(selection.get('task_decisions', []))}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
