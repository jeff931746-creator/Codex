#!/usr/bin/env python3
"""拦截危险 bash 命令。从 stdin 读取 Claude hook JSON。"""
import sys
import json
import re
import subprocess

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

# worktree 前置检查：只检查命令首行，避免误匹配 commit message 等字符串内容
REPO = '/Users/mt/Documents/Codex'
first_line = command.strip().splitlines()[0] if command.strip() else ''
# 模式分段拼接，避免源码本身被 hook 误匹配
wt_pattern = r'git\s+' + 'worktree' + r'\s+add'
if re.search(wt_pattern, first_line):
    result = subprocess.run(
        ['git', '-C', REPO, 'status', '--porcelain'],
        capture_output=True, text=True
    )
    dirty = [l for l in result.stdout.splitlines() if l.strip()]
    if dirty:
        count = len(dirty)
        print(f'DANGER:worktree 操作被拦截：主目录有 {count} 个未提交改动，请先 commit 或 stash。', flush=True)
        sys.exit(1)

sys.exit(0)
