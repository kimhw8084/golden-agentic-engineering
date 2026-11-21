#!/usr/bin/env python3
"""Offline high-confidence secret-pattern scan for a tree and Git history."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
PATTERNS = [
    ('private_key', re.compile(r'-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----')),
    ('github_token', re.compile(r'\bgh[pousr]_[A-Za-z0-9]{30,}\b')),
    ('github_fine_grained_token', re.compile(r'\bgithub_pat_[A-Za-z0-9_]{20,}\b')),
    ('aws_access_key_id', re.compile(r'\bAKIA[0-9A-Z]{16}\b')),
    ('slack_token', re.compile(r'\bxox[baprs]-[A-Za-z0-9-]{20,}\b')),
    ('google_api_key', re.compile(r'\bAIza[0-9A-Za-z_-]{30,}\b')),
    ('openai_api_key', re.compile(r'\bsk-(?!ant-)(?:proj-)?[A-Za-z0-9_-]{24,}\b')),
    ('anthropic_api_key', re.compile(r'\bsk-ant-[A-Za-z0-9_-]{20,}\b')),
    ('npm_token', re.compile(r'\bnpm_[A-Za-z0-9]{30,}\b')),
    ('stripe_secret_key', re.compile(r'\b(?:sk|rk)_(?:live|test)_[A-Za-z0-9]{16,}\b')),
    ('sendgrid_api_key', re.compile(r'\bSG\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\b')),
    ('twilio_api_key', re.compile(r'\bSK[0-9a-fA-F]{32}\b')),
    ('credential_assignment', re.compile(r'''(?i)\b(?:password|secret|api[_-]?key|access[_-]?token)\b\s*[:=]\s*["'][^"']{12,}["']''')),
]
PLACEHOLDER = re.compile(r'(?i)(example|replace|your[-_ ]|dummy|redacted|placeholder|changeme|xxx|\{env:)')


def scan_text(text: str, relative: str) -> list[dict]:
    findings = []
    for number, line in enumerate(text.splitlines(), 1):
        for kind, pattern in PATTERNS:
            match = pattern.search(line)
            if match and not PLACEHOLDER.search(match.group(0)):
                findings.append({'file': relative, 'line': number, 'kind': kind})
    return findings


def scan_file(path: Path, relative: str) -> list[dict]:
    try:
        text = path.read_text(encoding='utf-8')
    except (UnicodeError, OSError):
        return []
    return scan_text(text, relative)


def git_output(repo: Path, *args: str) -> subprocess.CompletedProcess:
    """Run Git without a shell and suppress stderr, which may contain unsafe input."""
    return subprocess.run(['git', '-C', str(repo), *args], stdout=subprocess.PIPE,
                          stderr=subprocess.DEVNULL, check=False)


def scan_history(repo: Path) -> tuple[list[dict], int]:
    """Scan every reachable blob from all refs without retaining blob contents in memory."""
    shallow = git_output(repo, 'rev-parse', '--is-shallow-repository')
    if shallow.returncode != 0 or shallow.stdout.strip() != b'false':
        raise ValueError('complete Git history is unavailable; history scan cannot be certified')
    objects = git_output(repo, 'rev-list', '--objects', '--all')
    if objects.returncode != 0:
        raise ValueError('Git refs could not be enumerated; history scan cannot be certified')
    paths: dict[str, str] = {}
    for raw_line in objects.stdout.splitlines():
        oid_bytes, _, path_bytes = raw_line.partition(b' ')
        try:
            oid = oid_bytes.decode('ascii')
        except UnicodeDecodeError:
            continue
        if len(oid) in (40, 64):
            paths.setdefault(oid, path_bytes.decode('utf-8', errors='replace') or oid)

    findings: list[dict] = []
    scanned_blobs = 0
    # Redirect the batch output to a temporary file: large histories cannot fill a pipe
    # or force the complete repository contents into the Python process's memory.
    with tempfile.TemporaryFile() as object_input, tempfile.TemporaryFile() as object_output:
        for oid in paths:
            object_input.write(oid.encode('ascii') + b'\n')
        object_input.seek(0)
        proc = subprocess.run(['git', '-C', str(repo), 'cat-file', '--batch'],
                              stdin=object_input, stdout=object_output,
                              stderr=subprocess.DEVNULL, check=False)
        if proc.returncode != 0:
            raise ValueError('Git objects could not be read; history scan cannot be certified')
        object_output.seek(0)
        while True:
            header = object_output.readline()
            if not header:
                break
            fields = header.rstrip(b'\n').split(b' ')
            if len(fields) != 3:
                raise ValueError('Git returned an invalid object record; history scan cannot be certified')
            oid, object_type, size_bytes = fields
            try:
                size = int(size_bytes)
            except ValueError as exc:
                raise ValueError('Git returned an invalid object size; history scan cannot be certified') from exc
            if object_type == b'blob':
                scanned_blobs += 1
                data = object_output.read(size)
                try:
                    text = data.decode('utf-8')
                except UnicodeDecodeError:
                    text = ''
                if text:
                    oid_text = oid.decode('ascii')
                    relative = f"history:{paths.get(oid_text, oid_text)}@blob:{oid_text[:12]}"
                    findings.extend(scan_text(text, relative))
            else:
                object_output.seek(size, 1)
            if object_output.read(1) != b'\n':
                raise ValueError('Git returned a truncated object; history scan cannot be certified')
    return findings, scanned_blobs


def main() -> int:
    parser = argparse.ArgumentParser(description='Offline high-confidence secret-pattern scan; values are never printed.')
    parser.add_argument('--repo', type=Path, default=ROOT)
    parser.add_argument('--history', action='store_true', help='also scan every blob reachable from every local Git ref')
    args = parser.parse_args()
    findings = []
    history_blobs = None
    repo = args.repo.resolve()
    excluded = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'dist', 'build', '.next', 'coverage'}
    files = [path for path in repo.rglob('*') if path.is_file() and not path.is_symlink()
             and not any(part in excluded for part in path.relative_to(repo).parts)]
    for path in files:
        if path.is_file() and not path.is_symlink():
            findings.extend(scan_file(path, path.relative_to(repo).as_posix()))
    if args.history:
        try:
            history_findings, history_blobs = scan_history(repo)
        except ValueError as exc:
            print(f'SECRET_PATTERN_SCAN_INCOMPLETE reason={exc} no_values_emitted=true', file=sys.stderr)
            return 3
        findings.extend(history_findings)
    if findings:
        for item in findings:
            safe_path = json.dumps(item['file'], ensure_ascii=True)
            print(f"FINDING {safe_path}:{item['line']} {item['kind']}")
        return 2
    history_detail = f' scanned_history_blobs={history_blobs}' if history_blobs is not None else ''
    print(f'SECRET_PATTERN_SCAN_PASS scanned_files={len(files)}{history_detail} no_values_emitted=true')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
