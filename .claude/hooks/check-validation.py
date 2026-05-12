#!/usr/bin/env python3
"""
Stop 钩子：检测本轮是否修改了代码或脚本但没有运行验证命令。
非阻断，仅作警告。
"""
import sys
import json
import os
import subprocess

WORKSPACE = '/Users/mt/Documents/Codex'

# 读取 Stop 钩子 stdin（包含本轮工具调用记录）
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

# 从 transcript 提取本轮工具调用
transcript = data.get('transcript', [])

CODE_EXTENSIONS = {'.py', '.sh', '.js', '.ts', '.go', '.rb', '.rs', '.swift'}
VALIDATION_KEYWORDS = [
    'py_compile', 'pytest', 'unittest', 'npm test', 'yarn test',
    'python3 -m', 'python -m', 'node ', 'bash ', 'sh ',
    'lint', 'mypy', 'ruff', 'flake8', 'black --check',
    'smoke', 'assert', 'test', 'check', 'verify',
]

modified_code = False
ran_validation = False

for entry in transcript:
    tool = entry.get('toolName', '') or entry.get('tool_name', '')
    tool_input = entry.get('toolInput', {}) or entry.get('tool_input', {}) or {}

    # 检测代码/脚本文件改动（Write 或 Edit 工具）
    if tool in ('Write', 'Edit'):
        path = tool_input.get('file_path', '')
        _, ext = os.path.splitext(path)
        if ext in CODE_EXTENSIONS:
            modified_code = True

    # 检测验证命令（Bash 工具）
    if tool == 'Bash':
        command = tool_input.get('command', '').lower()
        if any(kw in command for kw in VALIDATION_KEYWORDS):
            ran_validation = True

if modified_code and not ran_validation:
    msg = '本轮修改了代码或脚本，但未检测到验证命令。交付前请运行 smoke check 或逻辑测试。'
    print(f'⚠️  validation：{msg}', flush=True)
    subprocess.run([
        'osascript', '-e',
        f'display notification "{msg}" with title "⚠️ Claude · 未验证即交付" sound name "Basso"'
    ], capture_output=True)

sys.exit(0)
