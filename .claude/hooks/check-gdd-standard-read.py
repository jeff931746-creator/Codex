#!/usr/bin/env python3
"""PreToolUse: 写设计文档前检查本 session 是否已读 GDD写作标准.md。"""
import sys
import json
import os

# 触发检查的文件路径关键词（文件名包含任意一个即视为设计文档）
DESIGN_KEYWORDS = [
    '系统设计', '玩法设计', '战斗设计', '战斗系统',
    '关卡设计', '功能需求', 'GDD', '规格文档', '设计文档', '策划文档',
]

# 排除路径（标准文件本身、规则文件、记忆文件不触发）
EXCLUDE_PATHS = [
    'GDD写作标准',
    '.claude/rules',
    'memory/',
    'reference/部门标准',
    'history/GDD',
]

data = json.load(sys.stdin)
tool_name = data.get('tool_name', '')

if tool_name not in ('Edit', 'Write'):
    sys.exit(0)

file_path = data.get('tool_input', {}).get('file_path', '')

# 排除标准文件和规则文件本身
if any(ex in file_path for ex in EXCLUDE_PATHS):
    sys.exit(0)

# 只检查名称匹配设计文档关键词的文件
if not any(kw in file_path for kw in DESIGN_KEYWORDS):
    sys.exit(0)

# 检查 session 标记
ppid = str(os.getppid())
marker = f'/tmp/gdd_standard_read_{ppid}'
if not os.path.exists(marker):
    print(
        '⛔ GDD标准未读\n'
        '修改设计文档前必须先读取：\n'
        '  reference/部门标准/策划/current/GDD写作标准.md\n'
        '读完后此次 Edit/Write 会自动放行。',
        flush=True,
    )
    sys.exit(1)

sys.exit(0)
