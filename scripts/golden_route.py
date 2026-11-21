#!/usr/bin/env python3
"""Resolve one Golden task route from local OpenCode assets, without network or AI."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROUTES = ROOT / 'workflows' / 'task-routing.json'
CAPABILITIES = ROOT / 'research' / 'capability-selection.json'
CONFIG = ROOT / 'opencode.json'


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def validation_errors(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    try:
        routing = read_json(root / 'workflows' / 'task-routing.json')
        capabilities = read_json(root / 'research' / 'capability-selection.json')
        config = read_json(root / 'opencode.json')
        project_config = read_json(root / '.opencode' / 'opencode.json')
    except (OSError, ValueError) as exc:
        return [f'Cannot read route inputs ({type(exc).__name__}).']
    if (not isinstance(routing, dict) or not isinstance(capabilities, dict)
            or not isinstance(config, dict) or not isinstance(project_config, dict)):
        return ['Routing, capability, and OpenCode config roots must be JSON objects.']
    default_agent = project_config.get('default_agent')
    if not isinstance(default_agent, str) or not re.fullmatch(r'[a-z0-9-]+', default_agent):
        errors.append('Project OpenCode config must select a local Golden primary agent.')
    else:
        agent_path = root / '.opencode' / 'agents' / f'{default_agent}.md'
        try:
            agent_source = agent_path.read_text(encoding='utf-8')
        except OSError:
            errors.append('Project OpenCode default agent is missing locally.')
        else:
            frontmatter = re.match(r'\A---\s*\n(.*?)\n---\s*(?:\n|$)', agent_source, re.DOTALL)
            if not frontmatter or not re.search(r'^mode:\s*primary\s*$', frontmatter[1], re.MULTILINE):
                errors.append('Project OpenCode default agent must declare mode: primary.')
    workflows = routing.get('workflows')
    if routing.get('schema') != 'golden-task-routing/v2' or not isinstance(workflows, list):
        return ['Unsupported or malformed task-routing manifest.']
    if len(workflows) != 12:
        errors.append('Expected 12 task workflows.')
    default = routing.get('default')
    if (not isinstance(default, dict) or set(default) != {
            'agent', 'specialists', 'skill_loading', 'selection_registry',
            'agentic_first_policy', 'patterns', 'pattern_policy', 'mcp_policy'}
            or default.get('agent') != 'primary'
            or any(not isinstance(default.get(field), str) or len(default[field]) < 8
                   for field in ('pattern_policy', 'mcp_policy', 'skill_loading', 'selection_registry', 'agentic_first_policy', 'specialists'))
            or not isinstance(default.get('patterns'), list)
            or not default['patterns']
            or any(not isinstance(pattern, str) or not pattern.strip() for pattern in default['patterns'])
            or len(set(default['patterns'])) != len(default['patterns'])):
        errors.append('Default routing policy is incomplete.')
    candidate_records = capabilities.get('candidates', [])
    non_public = capabilities.get('non_public_capability_ids', [])
    if not isinstance(candidate_records, list) or not isinstance(non_public, list) or any(not isinstance(item, str) for item in non_public):
        errors.append('Capability registry IDs must be arrays of records and strings.')
        candidate_records, non_public = [], []
    candidate_ids = {item.get('id') for item in candidate_records if isinstance(item, dict) and isinstance(item.get('id'), str)}
    candidate_ids |= set(non_public)
    configured = config.get('mcp', {}).get('servers', {}) if isinstance(config.get('mcp'), dict) else {}
    if not isinstance(configured, dict):
        configured = {}
    required = {'id', 'entry', 'complexity', 'primary_agent', 'skills', 'specialists', 'pattern', 'context',
                'mcp', 'mcp_candidates', 'mcp_policy', 'deterministic_tools', 'trust', 'no_ai', 'outputs', 'acceptance'}
    allowed = required | {'capability_candidates'}
    allowed_complexity = {'small', 'small-to-medium', 'medium', 'medium-to-large', 'high-risk'}
    route_ids: set[str] = set()
    for row in workflows:
        if not isinstance(row, dict):
            errors.append('Workflow record must be an object.')
            continue
        route_id = row.get('id')
        if not isinstance(route_id, str) or route_id in route_ids:
            errors.append('Workflow IDs must be unique nonempty strings.')
            continue
        route_ids.add(route_id)
        if not re.fullmatch(r'[a-z0-9-]+', route_id) or not required <= row.keys() or row.keys() - allowed:
            errors.append(f'{route_id}: invalid ID or required route fields missing.')
        if row.get('complexity') not in allowed_complexity:
            errors.append(f'{route_id}: unsupported complexity value.')
        for field in ('entry', 'mcp_policy', 'trust', 'no_ai', 'acceptance'):
            if not isinstance(row.get(field), str) or len(row[field]) < 8:
                errors.append(f'{route_id}: {field} must be a nonempty descriptive string.')
        if not isinstance(row.get('pattern'), str) or len(row['pattern']) < 4:
            errors.append(f'{route_id}: pattern must be a nonempty string.')
        primary_agent = row.get('primary_agent')
        if not isinstance(primary_agent, str) or (primary_agent != 'primary' and not (root / '.opencode' / 'agents' / f'{primary_agent}.md').is_file()):
            errors.append(f'{route_id}: primary agent is not a local OpenCode agent.')
        skills = row.get('skills')
        if (not isinstance(skills, list) or (not skills and route_id != 'small-fix')
                or (skills and route_id == 'small-fix')
                or any(not isinstance(skill, str) for skill in skills) or len(set(skills)) != len(skills)):
            errors.append(f'{route_id}: only small-fix may omit a skill; other routes need unique skills.')
        else:
            for skill in skills:
                if not isinstance(skill, str) or not (root / '.opencode' / 'skills' / skill / 'SKILL.md').is_file():
                    errors.append(f'{route_id}: skill reference is missing locally.')
        specialists = row.get('specialists')
        if not isinstance(specialists, list):
            errors.append(f'{route_id}: specialists must be an array.')
        else:
            for specialist in specialists:
                agent = specialist.get('agent') if isinstance(specialist, dict) else None
                if (not isinstance(specialist, dict) or set(specialist) != {'agent', 'when'}
                        or not isinstance(agent, str) or not re.fullmatch(r'[a-z0-9-]+', agent)
                        or not isinstance(specialist.get('when'), str) or len(specialist['when']) < 8
                        or not (root / '.opencode' / 'agents' / f'{agent}.md').is_file()):
                    errors.append(f'{route_id}: specialist is not a local OpenCode agent.')
        for field in ('context', 'deterministic_tools', 'outputs'):
            values = row.get(field)
            if not isinstance(values, list) or not values or any(not isinstance(value, str) or not value.strip() for value in values):
                errors.append(f'{route_id}: {field} must be a nonempty string array.')
        actual_mcp = row.get('mcp')
        if (not isinstance(actual_mcp, list) or any(not isinstance(name, str) for name in actual_mcp)
                or len(set(actual_mcp)) != len(actual_mcp) or any(name not in configured for name in actual_mcp)):
            errors.append(f'{route_id}: MCP references must match repository-configured servers.')
        candidates = row.get('mcp_candidates', [])
        if (not isinstance(candidates, list) or any(not isinstance(name, str) for name in candidates)
                or len(set(candidates)) != len(candidates) or any(name not in candidate_ids for name in candidates)):
            errors.append(f'{route_id}: MCP candidate references must resolve in the capability registry.')
        capability_candidates = row.get('capability_candidates', [])
        if (not isinstance(capability_candidates, list)
                or any(not isinstance(name, str) or not name.strip() for name in capability_candidates)
                or len(set(capability_candidates)) != len(capability_candidates)
                or any(name not in candidate_ids for name in capability_candidates)):
            errors.append(f'{route_id}: capability_candidates must be a string array.')
    return errors


def route_for(task_id: str, root: Path = ROOT) -> dict:
    errors = validation_errors(root)
    if errors:
        raise ValueError('Routing manifest invalid: ' + '; '.join(errors))
    routes = read_json(root / 'workflows' / 'task-routing.json')['workflows']
    capability_registry = read_json(root / 'research' / 'capability-selection.json')
    capabilities = {item['id']: item for item in capability_registry.get('candidates', []) if isinstance(item, dict) and isinstance(item.get('id'), str)}
    matches = [row for row in routes if row['id'] == task_id]
    if len(matches) != 1:
        raise ValueError('Unknown task ID; use --list to inspect supported workflow IDs.')
    row = matches[0]
    return {
        'schema': 'golden-task-route/v1',
        'id': row['id'],
        'entry': row['entry'],
        'complexity': row['complexity'],
        'primary_agent': row['primary_agent'],
        'skills': [{'id': name, 'path': f'.opencode/skills/{name}/SKILL.md'} for name in row['skills']],
        'specialists': row['specialists'],
        'mcp': {'configured_for_route': row['mcp'], 'evaluation_candidates_only': row.get('mcp_candidates', []),
                'policy': row['mcp_policy']},
        'capability_candidates': [
            ({'id': capability_id, 'owner_repo': capabilities[capability_id].get('owner_repo'),
              'purpose': capabilities[capability_id].get('purpose'),
              'decision': capabilities[capability_id].get('decision'),
              'measured_evidence': capabilities[capability_id].get('measured_evidence')}
             if capability_id in capabilities else {'id': capability_id, 'decision': 'LOCAL_FALLBACK'})
            for capability_id in row.get('capability_candidates', [])
        ],
        'pattern': row['pattern'],
        'context': row['context'],
        'deterministic_tools': row['deterministic_tools'],
        'trust': row['trust'],
        'no_ai': row['no_ai'],
        'outputs': row['outputs'],
        'acceptance': row['acceptance'],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Resolve one Golden workflow route using local, read-only files.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--task-id')
    group.add_argument('--list', action='store_true')
    parser.add_argument('--json', action='store_true', help='Emit the selected route as JSON.')
    args = parser.parse_args()
    errors = validation_errors()
    if errors:
        for error in errors:
            print('FAIL', error, file=sys.stderr)
        return 2
    try:
        if args.list:
            for row in read_json(ROUTES)['workflows']:
                print(f"{row['id']} — {row['entry']}")
            return 0
        route = route_for(args.task_id)
        if args.json:
            print(json.dumps(route, indent=2, ensure_ascii=False))
        else:
            print(f"ROUTE {route['id']} ({route['complexity']})")
            print(f"Primary: OpenCode {route['primary_agent']}")
            print('Load skills: ' + ', '.join(skill['path'] for skill in route['skills']))
            print('Conditional specialists: ' + (', '.join(item['agent'] for item in route['specialists']) or 'none'))
            print('Configured MCP for route: ' + (', '.join(route['mcp']['configured_for_route']) or 'none'))
            print('MCP candidates are evaluation-only; ' + route['mcp']['policy'])
            print('Capability candidates: ' + (', '.join(f"{item['id']} [{item['decision']}]" for item in route['capability_candidates']) or 'none'))
            print('Context: ' + '; '.join(route['context']))
            print('Trust: ' + route['trust'])
            print('No-AI fallback: ' + route['no_ai'])
            print('Acceptance: ' + route['acceptance'])
        return 0
    except (OSError, ValueError) as exc:
        print(f'Routing error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
