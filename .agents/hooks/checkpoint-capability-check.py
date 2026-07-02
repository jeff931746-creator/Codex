#!/usr/bin/env python3
"""Record capability standard lookup for scoped work."""
from __future__ import annotations

import argparse
from hook_utils import active_task_scope, checkpoint_path, normalize_path, now, write_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--capability', action='append', required=True)
    parser.add_argument('--standard-path', action='append', default=[])
    parser.add_argument('--missing-standard', action='append', default=[])
    parser.add_argument('--scope', action='append', default=[])
    parser.add_argument('--ttl-seconds', type=int, default=1800)
    args = parser.parse_args()
    ts = now()
    scope = sorted(set(normalize_path(p) for p in (args.scope or active_task_scope() or ['.'])))
    write_json(checkpoint_path('capability-check.json'), {
        'result': 'pass',
        'scope_paths': scope,
        'capabilities': args.capability,
        'standard_paths': sorted(set(normalize_path(p) for p in args.standard_path)),
        'missing_standards': sorted(set(args.missing_standard)),
        'created_at': ts,
        'expires_at': ts + args.ttl_seconds,
    })
    print('✅ capability-check checkpoint recorded')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
