#!/usr/bin/env python3
"""Run shared hooks with one Python interpreter, without shell dependencies."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--runtime', default='agent')
    parser.add_argument('hook')
    args = parser.parse_args()
    directory = Path(__file__).resolve().parent
    target = (directory / args.hook).resolve()
    if target.parent != directory or target.suffix != '.py' or not target.is_file() or target == Path(__file__).resolve():
        parser.error('hook must name a Python file in .agents/hooks')
    env = os.environ.copy()
    env.update(AGENT_RUNTIME=args.runtime, AGENT_WORKSPACE=str(directory.parent.parent),
               PYTHONUTF8='1', PYTHONIOENCODING='utf-8')
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        print('Invalid hook JSON payload', file=sys.stderr)
        return 2
    if not isinstance(payload, dict):
        print('Hook payload must be a JSON object', file=sys.stderr)
        return 2
    cwd = Path(payload.get('cwd') or os.getcwd()).resolve()
    workspace = directory.parent.parent
    if cwd != workspace and workspace not in cwd.parents:
        return 0
    result = subprocess.run([sys.executable, '-X', 'utf8', str(target)],
                            input=raw, capture_output=True, text=True,
                            encoding='utf-8', env=env, cwd=directory.parent.parent)
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    # These two historical implementations use exit 1; hook denial is exit 2.
    if args.hook in {'check-commit-message.py', 'warn-dangerous.py'} and result.returncode:
        return 2
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
