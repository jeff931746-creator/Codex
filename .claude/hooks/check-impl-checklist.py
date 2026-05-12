#!/usr/bin/env python3
"""
Stop 钩子：检测 implementation 任务是否完成了 independent review。
判断依据：代码/脚本文件被修改，但 impl-review-checkpoint 缺失或已过期。
非阻断，仅作警告。
"""
import sys
import json
import os
import time
import subprocess

WORKSPACE = '/Users/mt/Documents/Codex'
CHECKPOINT_FILE = os.path.join(WORKSPACE, '.claude/.impl-review-checkpoint')
MAX_AGE = 1800  # 30 分钟

CODE_EXTENSIONS = {'.py', '.sh', '.js', '.ts', '.jsx', '.tsx', '.go', '.rb', '.rs', '.swift', '.zsh', '.bash'}

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

transcript = data.get('transcript', [])

modified_code = False
for entry in transcript:
    tool = entry.get('toolName', '') or entry.get('tool_name', '')
    tool_input = entry.get('toolInput', {}) or entry.get('tool_input', {}) or {}

    if tool in ('Write', 'Edit'):
        path = tool_input.get('file_path', '')
        _, ext = os.path.splitext(path)
        if ext in CODE_EXTENSIONS:
            modified_code = True
            break

if not modified_code:
    sys.exit(0)

# 代码被改动，检查 independent review 检查点
checkpoint_ok = False
if os.path.exists(CHECKPOINT_FILE):
    try:
        checkpoint_time = int(open(CHECKPOINT_FILE).read().strip())
        age = int(time.time()) - checkpoint_time
        if age <= MAX_AGE:
            checkpoint_ok = True
    except Exception:
        pass

if not checkpoint_ok:
    msg = 'implementation 任务修改了代码，但未检测到 independent review 检查点。完成 review 后请运行：bash .claude/hooks/impl-review-checkpoint.sh'
    print(f'⚠️  impl-checklist：{msg}', flush=True)
    subprocess.run([
        'osascript', '-e',
        f'display notification "independent review 检查点缺失或已过期" with title "⚠️ Claude · impl validation 未完整" sound name "Basso"'
    ], capture_output=True)

sys.exit(0)
