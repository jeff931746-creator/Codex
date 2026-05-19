#!/usr/bin/env python3
"""
Stop 钩子：检查 neat-freak 检查点和 QA 检查点是否有效。
如果检测到未提交改动但检查点缺失或已过期，输出提示。
非阻断，仅作警告。
"""
import sys
import json
import os
import time
import subprocess

try:
    json.load(sys.stdin)
except Exception:
    pass

WORKSPACE = '/Users/mt/Documents/Codex'
NEAT_FREAK_CHECKPOINT = os.path.join(WORKSPACE, '.claude/.neat-freak-checkpoint')
QA_CHECKPOINT = os.path.join(WORKSPACE, '.claude/.qa-checkpoint')
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

now = int(time.time())
NOTIFY_COOLDOWN = 1800  # 通知冷却：30 分钟内不重复发
LAST_NOTIFY_FILE = os.path.join(WORKSPACE, '.claude/.neat-freak-last-notify')

def checkpoint_valid(path):
    if not os.path.exists(path):
        return False, 'missing'
    try:
        ts = int(open(path).read().strip())
        age = now - ts
        if age > MAX_AGE:
            return False, f'expired ({age // 60} 分钟前)'
        return True, 'ok'
    except Exception:
        return False, 'corrupt'

def notify_cooldown_ok():
    """返回 True 表示可以发通知（距上次通知已超过冷却时间）"""
    if not os.path.exists(LAST_NOTIFY_FILE):
        return True
    try:
        last = int(open(LAST_NOTIFY_FILE).read().strip())
        return (now - last) >= NOTIFY_COOLDOWN
    except Exception:
        return True

neat_ok, neat_reason = checkpoint_valid(NEAT_FREAK_CHECKPOINT)
qa_ok, qa_reason = checkpoint_valid(QA_CHECKPOINT)

warnings = []

if not neat_ok:
    warnings.append(f'neat-freak 检查点{"缺失" if neat_reason == "missing" else "已过期" if "expired" in neat_reason else "损坏"}，commit 前请先完成 neat-freak 步骤并运行 .claude/hooks/neat-freak-checkpoint.sh')

if not qa_ok:
    warnings.append(f'QA 检查点{"缺失" if qa_reason == "missing" else "已过期" if "expired" in qa_reason else "损坏"}，commit 前请先启动收尾子 agent 完成 QA，子 agent 运行 .claude/hooks/qa-checkpoint.sh 后方可继续')

if warnings:
    for w in warnings:
        print(f'⚠️  neat-freak：{w}', flush=True)
    # 只在冷却期过后才发系统通知，避免重复轰炸
    if notify_cooldown_ok():
        subprocess.run([
            'osascript', '-e',
            'display notification "收尾检查点未完成，请勿 commit" with title "⚠️ Claude · 收尾门禁" sound name "Basso"'
        ], capture_output=True)
        try:
            open(LAST_NOTIFY_FILE, 'w').write(str(now))
        except Exception:
            pass

sys.exit(0)
