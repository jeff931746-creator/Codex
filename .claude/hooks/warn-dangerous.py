#!/usr/bin/env python3
"""拦截危险 bash 命令。从 stdin 读取 Claude hook JSON。"""
import sys
import json
import re

DANGEROUS_PATTERNS = [
    r'rm\s+-[a-zA-Z]*r[a-zA-Z]*f',   # rm -rf
    r'rm\s+-[a-zA-Z]*f[a-zA-Z]*r',   # rm -fr
    r'git\s+push\s+.*--force',
    r'git\s+push\s+.*-f\b',
    r'git\s+reset\s+--hard',
    r'git\s+clean\s+.*-f',
    r'git\s+branch\s+.*-D\b',
    r'chmod\s+-R\s+777',
]

data = json.load(sys.stdin)
tool_name = data.get('tool_name', '')
command = data.get('tool_input', {}).get('command', '')

if tool_name != 'Bash':
    sys.exit(0)

for pattern in DANGEROUS_PATTERNS:
    if re.search(pattern, command):
        summary = command[:80]
        print(f'DANGER:{summary}', flush=True)
        sys.exit(1)

sys.exit(0)
