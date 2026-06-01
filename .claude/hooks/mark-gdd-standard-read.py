#!/usr/bin/env python3
"""PostToolUse: 当 Read 工具读取 GDD写作标准.md 时，写入 session 标记文件。"""
import sys
import json
import os

data = json.load(sys.stdin)

if data.get('tool_name') != 'Read':
    sys.exit(0)

file_path = data.get('tool_input', {}).get('file_path', '')
if 'GDD写作标准' not in file_path:
    sys.exit(0)

# 用 PPID 作为 session 标识符：同一 Claude 进程内保持一致，新会话有新 PID
ppid = str(os.getppid())
marker = f'/tmp/gdd_standard_read_{ppid}'
with open(marker, 'w') as f:
    f.write(file_path + '\n')

sys.exit(0)
