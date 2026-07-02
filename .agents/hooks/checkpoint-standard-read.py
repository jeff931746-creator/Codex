#!/usr/bin/env python3
"""Record that applicable standards were read for the current scoped work."""
from __future__ import annotations

import argparse
from hook_utils import active_task_scope, checkpoint_path, normalize_path, now, write_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--standard', action='append', required=True)
    parser.add_argument('--scope', action='append', default=[])
    parser.add_argument('--basis', required=True)
    parser.add_argument('--ttl-seconds', type=int, default=1800)
    args = parser.parse_args()
    ts = now()
    scope = sorted(set(normalize_path(p) for p in (args.scope or active_task_scope() or ['.'])))
    write_json(checkpoint_path('standard-read.json'), {
        'result': 'pass',
        'scope_paths': scope,
        'standards_read': sorted(set(normalize_path(p) for p in args.standard)),
        'basis': args.basis,
        'created_at': ts,
        'expires_at': ts + args.ttl_seconds,
    })
    print('✅ standard-read checkpoint recorded')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
