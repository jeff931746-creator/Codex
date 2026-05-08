#!/usr/bin/env python3
"""
pre-commit 门禁：验证 neat-freak 检查点是否在 30 分钟内完成。
从 stdin 读取 Claude hook JSON，仅拦截 git commit 命令。
"""
import sys
import json
import re
import os
import time

data = json.load(sys.stdin)
tool_name = data.get('tool_name', '')
command = data.get('tool_input', {}).get('command', '')

if tool_name != 'Bash':
    sys.exit(0)
if not re.search(r'git\s+commit', command):
    sys.exit(0)

CHECKPOINT_FILE = '/Users/mt/Documents/Codex/.claude/.neat-freak-checkpoint'
MAX_AGE = 1800  # 30 分钟

if not os.path.exists(CHECKPOINT_FILE):
    print('BLOCK:未找到 neat-freak 检查点。commit 前请完成 neat-freak 收尾步骤，并运行 .claude/hooks/neat-freak-checkpoint.sh', flush=True)
    sys.exit(2)

try:
    checkpoint_time = int(open(CHECKPOINT_FILE).read().strip())
except Exception:
    print('BLOCK:neat-freak 检查点文件损坏，请重新运行 .claude/hooks/neat-freak-checkpoint.sh', flush=True)
    sys.exit(2)

age = int(time.time()) - checkpoint_time
if age > MAX_AGE:
    minutes = age // 60
    print(f'BLOCK:neat-freak 检查点已过期（{minutes} 分钟前）。请重新完成 neat-freak 收尾步骤后再 commit', flush=True)
    sys.exit(2)

sys.exit(0)
