#!/usr/bin/env python3
"""Activate the context-pressure handoff brake for the current runtime."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description='Activate context-pressure handoff brake.')
    parser.add_argument('--used-percent', type=int, default=60)
    parser.add_argument('--reason', default='user-reported-context-pressure')
    parser.add_argument('--handoff-path', default='')
    parser.add_argument('--ttl-seconds', type=int, default=86400)
    args = parser.parse_args()

    checkpoint = Path(__file__).with_name('checkpoint-context-pressure.py')
    command = [
        sys.executable,
        str(checkpoint),
        '--status',
        'active',
        '--used-percent',
        str(args.used_percent),
        '--reason',
        args.reason,
        '--ttl-seconds',
        str(args.ttl_seconds),
    ]
    if args.handoff_path:
        command.extend(['--handoff-path', args.handoff_path])
    return subprocess.run(command).returncode


if __name__ == '__main__':
    raise SystemExit(main())
