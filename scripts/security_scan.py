#!/usr/bin/env python3
"""Offline high-confidence secret-pattern scan for tracked repository files."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
PATTERNS = [
    ('private_key', re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')),
    ('github_token', re.compile(r'\bgh[pousr]_[A-Za-z0-9]{30,}\b')),
    ('aws_access_key_id', re.compile(r'\bAKIA[0-9A-Z]{16}\b')),
    ('credential_assignment', re.compile(r'''(?i)\b(?:password|secret|api[_-]?key|access[_-]?token)\b\s*[:=]\s*["'][^"']{12,}["']''')),
]
PLACEHOLDER = re.compile(r'(?i)(example|replace|your[-_ ]|dummy|redacted|placeholder|changeme|xxx|\{env:)')


def scan_file(path: Path, relative: str) -> list[dict]:
    try:
        text = path.read_text(encoding='utf-8')
    except (UnicodeError, OSError):
        return []
    findings = []
    for number, line in enumerate(text.splitlines(), 1):
        for kind, pattern in PATTERNS:
            match = pattern.search(line)
            if match:
                if kind == 'credential_assignment' and PLACEHOLDER.search(match.group(0)):
                    continue
                findings.append({'file': relative, 'line': number, 'kind': kind})
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description='Offline high-confidence secret-pattern scan; values are never printed.')
    parser.add_argument('--repo', type=Path, default=ROOT)
    args = parser.parse_args()
    findings = []
    repo = args.repo.resolve()
    excluded = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'dist', 'build', '.next', 'coverage'}
    files = [path for path in repo.rglob('*') if path.is_file() and not path.is_symlink()
             and not any(part in excluded for part in path.relative_to(repo).parts)]
    for path in files:
        if path.is_file() and not path.is_symlink():
            findings.extend(scan_file(path, path.relative_to(repo).as_posix()))
    if findings:
        for item in findings:
            print(f"FINDING {item['file']}:{item['line']} {item['kind']}")
        return 2
    print(f'SECRET_PATTERN_SCAN_PASS scanned_files={len(files)} no_values_emitted=true')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
