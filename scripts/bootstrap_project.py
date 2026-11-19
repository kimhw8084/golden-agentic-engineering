#!/usr/bin/env python3
"""Create minimal Golden project pin and instructions; no overwrites, dry-run default."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent

GUIDANCE = '''# Golden project engineering contract

This application uses a pinned Golden engineering release defined in `golden.project.json`.

- Use authorized internal OpenCode for normal edits, tests and direct commits to main where permitted. Do not demand per-edit Golden approvals.
- Use the locally installed Golden release's agents/skills/commands for relevant work; do not download tools or load every skill.
- To run checks, use `python <GOLDEN_HOME>/scripts/golden.py check --fast --project .` during development and `--full` for pre-release qualification. Replace `<GOLDEN_HOME>` with the approved local pinned release directory.
- Treat FAIL/NOT_RUN as blockers unless existing company exception process has granted a documented waiver; DEFERRED is not a full-pass state.
- Standard changes and application releases follow distinct approval processes. Normal code commits are not automatic production deployment.
- Protect data, respect permissions and human-control production/irreversible operations.
- Existing corporate infrastructure and local offline deterministic tools take priority over introducing a new service.
'''


def main():
    ap = argparse.ArgumentParser(description='Opt-in Golden project bootstrap; no overwrites.')
    ap.add_argument('--target', type=Path, required=True)
    ap.add_argument('--name', required=True)
    ap.add_argument('--profile', choices=('react','nicegui','python','other'), required=True)
    ap.add_argument('--criticality', choices=('simple','workflow','production-critical'), default='simple')
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    if not args.target.is_dir():
        ap.error('--target must be an existing application directory')
    target = args.target.resolve()
    manifest = {
        'name': args.name, 'golden_version': json.loads((ROOT/'standards/release.json').read_text())['version'],
        'profile': args.profile, 'criticality': args.criticality,
        'capabilities': {'ui': args.profile in ('react','nicegui'), 'api': False, 'database': False,
                         'jobs': False, 'observability': False, 'mcp': False, 'ai': False, 'manufacturing_data': False},
        'commands': {}
    }
    targets = {target / 'golden.project.json': json.dumps(manifest, indent=2)+'\n', target / 'AGENTS.md': GUIDANCE}
    for path, content in targets.items():
        if path.exists():
            print('SKIP EXISTING:', path, '— merge manually if needed')
        elif args.apply:
            path.write_text(content, encoding='utf-8'); print('CREATED:', path)
        else:
            print('WOULD CREATE:', path)
    print('Next: review capabilities, configure real test commands, qualify the local Golden version, and test OpenCode discovery.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
