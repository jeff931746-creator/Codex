#!/usr/bin/env python3
"""检查 git commit message 是否包含中文字符。从 stdin 读取 Claude hook JSON。"""
import sys
import json
import re

data = json.load(sys.stdin)
tool_name = data.get('tool_name', '')
command = data.get('tool_input', {}).get('command', '')

if tool_name != 'Bash':
    sys.exit(0)
if not re.search(r'git\s+commit', command):
    sys.exit(0)

# 提取 -m 参数后的 message（支持单引号和双引号）
m = re.search(r'-m\s+(["\'])(.*?)\1', command, re.DOTALL)
if not m:
    # heredoc 或其他格式，无法静态解析，放行
    sys.exit(0)

message = m.group(2).strip().split('\n')[0]

# 检测中文字符（CJK 统一表意文字）
has_chinese = bool(re.search(r'[一-鿿㐀-䶿]', message))
if not has_chinese:
    print(f'FAIL:{message[:60]}', flush=True)
    sys.exit(1)

sys.exit(0)
