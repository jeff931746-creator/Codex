#!/usr/bin/env python3
"""Foreground bounded Claude resume loop for Windows, macOS and Linux."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

BASE = Path(__file__).resolve().parent
PROJECT = BASE.parents[2]
STATE = BASE / '_state'
LOGS = BASE / '_logs'


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('start', 'session', 'stop', 'status', 'list'))
    parser.add_argument('label', nargs='?')
    parser.add_argument('--session-id')
    parser.add_argument('--cwd', type=Path, default=PROJECT)
    parser.add_argument('--interval', type=float, default=30, help='Minutes between attempts')
    parser.add_argument('--max-attempts', type=int, default=48)
    args = parser.parse_args()
    if args.action == 'list':
        for path in sorted(STATE.glob('*.json')):
            print(path.stem, path.read_text(encoding='utf-8'))
        return 0
    if not args.label or not re.fullmatch(r'[\w.-]+', args.label) or args.label in {'.', '..'}:
        parser.error('Supply a label consisting of letters, digits, _, . or -')
    state_path = STATE / f'{args.label}.json'
    if args.action == 'status':
        print(state_path.read_text(encoding='utf-8') if state_path.exists() else 'Not running')
        return 0
    if args.action == 'stop':
        if state_path.exists():
            data = json.loads(state_path.read_text(encoding='utf-8'))
            data['status'] = 'stopped'
            state_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        return 0
    if args.interval <= 0 or args.max_attempts < 1:
        parser.error('interval and max-attempts must be positive')
    if args.action == 'session' and not args.session_id:
        parser.error('session requires --session-id')
    if not args.cwd.is_dir():
        parser.error('cwd must be an existing directory')
    if state_path.exists() and json.loads(state_path.read_text(encoding='utf-8')).get('status') == 'running':
        parser.error('This label is already running; stop it before restarting')
    binary = os.environ.get('CLAUDE_BIN') or shutil.which('claude')
    if not binary:
        parser.error('Claude CLI not found; add it to PATH or set CLAUDE_BIN')
    STATE.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    data = {'status': 'running', 'attempts': 0, 'max_attempts': args.max_attempts,
            'session_id': args.session_id, 'cwd': str(args.cwd.resolve()), 'pid': os.getpid()}

    def save() -> None:
        state_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    save()
    prompt_path = BASE / 'prompts' / f'{args.label}.txt'
    prompt = (prompt_path.read_text(encoding='utf-8') if prompt_path.exists() else
              (f'运行 session-resume {args.label} 恢复任务状态。' if not args.session_id else '继续本对话已交代但未完成的任务。') +
              '只推进机械、可验证的工作；需要用户判断时说明并停止。整个任务完成后最后单独输出一行 TASK_COMPLETE。')
    command = [binary] + (['--resume', args.session_id] if args.session_id else []) + ['-p', prompt]
    # Resolve npm's JS entry instead of sending user prompts through cmd.exe.
    if os.name == 'nt' and Path(binary).suffix.lower() in {'.cmd', '.bat'}:
        wrapper = Path(binary)
        match = re.search(r'%dp0%[\\/]([^"\r\n]+\.(?:js|mjs|cjs))"', wrapper.read_text(encoding='utf-8'))
        node = shutil.which('node')
        if not match or not node:
            parser.error('Set CLAUDE_BIN to the real executable, or install the npm CLI with Node.js on PATH')
        entry = wrapper.parent / match.group(1).replace('\\', '/')
        command = [node, str(entry), *command[1:]]
    try:
        for attempt in range(1, args.max_attempts + 1):
            if json.loads(state_path.read_text(encoding='utf-8')).get('status') != 'running':
                return 0
            data['attempts'] = attempt
            save()
            result = subprocess.run(command, cwd=args.cwd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            with (LOGS / f'{args.label}.log').open('a', encoding='utf-8') as log:
                log.write(f'\nAttempt {attempt}/{args.max_attempts}, exit={result.returncode}\n{result.stdout}\n{result.stderr}')
            if result.returncode == 0 and 'TASK_COMPLETE' in result.stdout.splitlines():
                data['status'] = 'complete'
                save()
                return 0
            if attempt < args.max_attempts:
                deadline = time.monotonic() + args.interval * 60
                while time.monotonic() < deadline:
                    if json.loads(state_path.read_text(encoding='utf-8')).get('status') != 'running':
                        return 0
                    time.sleep(min(1, max(0, deadline - time.monotonic())))
        data['status'] = 'exhausted'
        save()
    except KeyboardInterrupt:
        data['status'] = 'stopped'
        save()
        return 130
    except (OSError, subprocess.SubprocessError):
        data['status'] = 'error'
        save()
        raise
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
