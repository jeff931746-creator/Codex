#!/usr/bin/env python3
"""Block dangerous shell commands for any runtime adapter."""
import json
import os
import pathlib
import re
import subprocess
import sys

DANGEROUS_PATTERNS = [
    r'rm\s+-[a-zA-Z]*r[a-zA-Z]*f',
    r'rm\s+-[a-zA-Z]*f[a-zA-Z]*r',
    r'git\s+push\s+.*--force',
    r'git\s+push\s+.*-f\b',
    r'git\s+reset\s+--hard',
    r'git\s+clean\s+.*-f',
    r'git\s+branch\s+.*-D\b',
    r'chmod\s+-R\s+777',
]

WORKSPACE = os.environ.get(
    'AGENT_WORKSPACE',
    str(pathlib.Path(__file__).resolve().parents[2]),
)

data = json.load(sys.stdin)
tool_name = data.get('tool_name', '')
command = data.get('tool_input', {}).get('command', '')

if tool_name != 'Bash':
    sys.exit(0)

for pattern in DANGEROUS_PATTERNS:
    if re.search(pattern, command):
        print(f'DANGER:{command[:80]}', flush=True)
        sys.exit(1)

first_line = command.strip().splitlines()[0] if command.strip() else ''
wt_pattern = r'git\s+' + 'worktree' + r'\s+add'
if re.search(wt_pattern, first_line):
    result = subprocess.run(
        ['git', '-C', WORKSPACE, 'status', '--porcelain'],
        capture_output=True,
        text=True,
    )
    dirty = [line for line in result.stdout.splitlines() if line.strip()]
    if dirty:
        print(
            f'DANGER:worktree 操作被拦截：主目录有 {len(dirty)} 个未提交改动，请先 commit 或 stash。',
            flush=True,
        )
        sys.exit(1)

sys.exit(0)

