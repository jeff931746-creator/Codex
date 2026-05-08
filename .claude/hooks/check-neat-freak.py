#!/usr/bin/env python3
"""
Stop 钩子：检查 neat-freak 检查点是否有效。
如果检测到未提交改动且检查点缺失或已过期，输出提示。
非阻断，仅作警告。
"""
import sys
import json
import os
import time
import subprocess

# 读取 stdin（Stop 钩子格式，不依赖其内容做判断）
try:
    json.load(sys.stdin)
except Exception:
    pass

WORKSPACE = '/Users/mt/Documents/Codex'
CHECKPOINT_FILE = os.path.join(WORKSPACE, '.claude/.neat-freak-checkpoint')
MAX_AGE = 1800  # 30 分钟

# 检查是否有未提交的改动
try:
    result = subprocess.run(
        ['git', '-C', WORKSPACE, 'status', '--porcelain'],
        capture_output=True, text=True, timeout=5
    )
    has_changes = bool(result.stdout.strip())
except Exception:
    sys.exit(0)

if not has_changes:
    sys.exit(0)

# 有未提交改动，检查 neat-freak 检查点
if not os.path.exists(CHECKPOINT_FILE):
    print('⚠️  neat-freak：检测到未提交改动，尚未完成收尾检查。commit 前请先完成 neat-freak 步骤并运行检查点脚本。', flush=True)
    sys.exit(0)

try:
    checkpoint_time = int(open(CHECKPOINT_FILE).read().strip())
except Exception:
    print('⚠️  neat-freak：检查点文件损坏，请重新运行 .claude/hooks/neat-freak-checkpoint.sh', flush=True)
    sys.exit(0)

age = int(time.time()) - checkpoint_time
if age > MAX_AGE:
    minutes = age // 60
    print(f'⚠️  neat-freak：检查点已过期（{minutes} 分钟前）。如有新改动请重新完成收尾步骤。', flush=True)

sys.exit(0)
