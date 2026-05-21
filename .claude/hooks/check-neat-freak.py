#!/usr/bin/env python3
"""
Stop 钩子：检查本轮会话是否完成了收尾 QA。
触发条件：本轮有实质性写操作（Write/Edit 工具调用）但 QA 检查点缺失或已过期。
与"有无未提交文件"无关。非阻断，仅作警告。
"""
import sys
import json
import os
import time
import subprocess

WORKSPACE = '/Users/mt/Documents/Codex'
QA_CHECKPOINT = os.path.join(WORKSPACE, '.claude/.neat-freak-checkpoint')
LAST_NOTIFY_FILE = os.path.join(WORKSPACE, '.claude/.neat-freak-last-notify')
MAX_AGE = 1800       # QA 检查点有效期：30 分钟
NOTIFY_COOLDOWN = 1800  # 通知冷却：30 分钟内不重复发

# 读取 transcript
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

transcript = data.get('transcript', [])

# 判断本轮是否有实质性写操作
WRITE_TOOLS = {'Write', 'Edit', 'NotebookEdit'}
has_write = False
for entry in transcript:
    tool = entry.get('toolName', '') or entry.get('tool_name', '')
    if tool in WRITE_TOOLS:
        has_write = True
        break

# 没有写操作，不需要 QA，直接退出
if not has_write:
    sys.exit(0)

now = int(time.time())

# 检查 QA 检查点是否有效
# 新格式：timestamp:diff_hash（工作树状态未变则永久有效，变了则回退到时间窗口）
def checkpoint_valid(path):
    if not os.path.exists(path):
        return False, 'missing'
    try:
        raw = open(path).read().strip()
        if ':' in raw:
            ts_str, saved_hash = raw.split(':', 1)
            ts = int(ts_str)
            # 取当前工作树 diff hash
            import hashlib, subprocess as _sp
            r = _sp.run(
                ['git', '-C', WORKSPACE, 'diff', 'HEAD'],
                capture_output=True, text=True
            )
            import hashlib
            cur_hash = hashlib.md5(r.stdout.encode()).hexdigest() if r.returncode == 0 else 'nodiff'
            if cur_hash == saved_hash:
                return True, 'ok'   # 工作树未变，检查点永久有效
            # 工作树已改变，回退到时间窗口
            age = now - ts
            if age > MAX_AGE:
                return False, f'expired ({age // 60} 分钟前)'
            return True, 'ok'
        else:
            # 旧格式：纯时间戳
            ts = int(raw)
            age = now - ts
            if age > MAX_AGE:
                return False, f'expired ({age // 60} 分钟前)'
            return True, 'ok'
    except Exception:
        return False, 'corrupt'

def notify_cooldown_ok():
    if not os.path.exists(LAST_NOTIFY_FILE):
        return True
    try:
        last = int(open(LAST_NOTIFY_FILE).read().strip())
        return (now - last) >= NOTIFY_COOLDOWN
    except Exception:
        return True

qa_ok, qa_reason = checkpoint_valid(QA_CHECKPOINT)

if not qa_ok:
    reason_str = '缺失' if qa_reason == 'missing' else f'已过期（{qa_reason}）' if 'expired' in qa_reason else '损坏'
    print(f'⚠️  收尾 QA：本轮有文件写操作，但 QA 检查点{reason_str}。请运行 neat-freak Skill，完成后运行 .claude/hooks/neat-freak-checkpoint.sh', flush=True)

    if notify_cooldown_ok():
        subprocess.run([
            'osascript', '-e',
            'display notification "本轮有写操作，尚未完成收尾 QA" with title "⚠️ Claude · 收尾 QA 未完成" sound name "Basso"'
        ], capture_output=True)
        try:
            open(LAST_NOTIFY_FILE, 'w').write(str(now))
        except Exception:
            pass

sys.exit(0)
