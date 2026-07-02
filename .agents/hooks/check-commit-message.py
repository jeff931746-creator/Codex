#!/usr/bin/env python3
"""Check whether git commit messages contain Chinese characters."""
import json
import re
import sys

data = json.load(sys.stdin)
tool_name = data.get('tool_name', '')
command = data.get('tool_input', {}).get('command', '')

if tool_name != 'Bash':
    sys.exit(0)
if not re.search(r'git\s+commit', command):
    sys.exit(0)

match = re.search(r'-m\s+(["\'])(.*?)\1', command, re.DOTALL)
if not match:
    sys.exit(0)

message = match.group(2).strip().split('\n')[0]
if message.startswith('$(') or message.startswith('`'):
    sys.exit(0)

if not re.search(r'[一-鿿㐀-䶿]', message):
    print(f'FAIL:{message[:60]}', flush=True)
    sys.exit(1)

sys.exit(0)

