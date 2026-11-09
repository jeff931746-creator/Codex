#!/usr/bin/env python3
"""Cross-platform helper for an already installed Ollama (no installer or global cleanup)."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import urllib.request


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('serve', 'pull', 'test'))
    parser.add_argument('--model', default='gemma4:e2b')
    parser.add_argument('--prompt', default='请只回复：部署成功。')
    args = parser.parse_args()
    if args.action == 'test':
        host = os.environ.get('OLLAMA_HOST', 'http://127.0.0.1:11434')
        if '://' not in host:
            host = 'http://' + host
        payload = json.dumps({'model': args.model, 'messages': [{'role': 'user', 'content': args.prompt}], 'stream': False}).encode('utf-8')
        request = urllib.request.Request(host.rstrip('/') + '/api/chat', payload, {'Content-Type': 'application/json'})
        with urllib.request.urlopen(request, timeout=300) as response:
            print(response.read().decode('utf-8'))
        return 0
    binary = os.environ.get('OLLAMA_BIN') or shutil.which('ollama')
    if not binary:
        parser.error('Install Ollama and add it to PATH, or set OLLAMA_BIN to its executable.')
    env = os.environ.copy()
    if env.get('OLLAMA_MODELS'):
        Path(env['OLLAMA_MODELS']).expanduser().mkdir(parents=True, exist_ok=True)
    command = [binary, 'serve'] if args.action == 'serve' else [binary, 'pull', args.model]
    try:
        return subprocess.call(command, env=env)
    except KeyboardInterrupt:
        return 130


if __name__ == '__main__':
    raise SystemExit(main())
