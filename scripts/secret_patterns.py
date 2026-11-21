"""Shared offline secret-pattern checks; findings never contain matched values."""
from __future__ import annotations

import re

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
    ('credential_assignment', re.compile(
        r'''(?i)\b(?:password|secret|api[_-]?key|access[_-]?token)\b\s*[:=]\s*["'][^"']{12,}["']''')),
]
PLACEHOLDER = re.compile(r'(?i)(example|replace|your[-_ ]|dummy|redacted|placeholder|changeme|xxx|\{env:)')


def scan_text(text: str, relative: str) -> list[dict]:
    """Return locations and pattern names only; never include matched text."""
    findings = []
    for number, line in enumerate(text.splitlines(), 1):
        for kind, pattern in PATTERNS:
            match = pattern.search(line)
            if match and not (kind == 'credential_assignment' and PLACEHOLDER.search(match.group(0))):
                findings.append({'file': relative, 'line': number, 'kind': kind})
    return findings
