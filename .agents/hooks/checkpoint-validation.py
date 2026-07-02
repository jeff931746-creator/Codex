#!/usr/bin/env python3
"""Record validation checkpoint for changed code/script files."""
from __future__ import annotations

import argparse
from hook_utils import active_task_scope, checkpoint_path, normalize_path, now, project_code_changed_paths, write_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--command', required=True)
    parser.add_argument('--scope', action='append', default=[])
    parser.add_argument('--ttl-seconds', type=int, default=1800)
    args = parser.parse_args()
    changed = project_code_changed_paths(active_task_scope() or ['.'])
    scope = sorted(set(normalize_path(p) for p in (args.scope or changed)))
    ts = now()
    write_json(checkpoint_path('validation.json'), {
        'result': 'pass',
        'command': args.command,
        'scope_paths': scope,
        'created_at': ts,
        'expires_at': ts + args.ttl_seconds,
    })
    print('✅ validation checkpoint recorded')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
