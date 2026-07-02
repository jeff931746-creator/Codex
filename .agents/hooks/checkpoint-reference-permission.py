#!/usr/bin/env python3
"""Record explicit user permission for scoped reference/ edits."""
from __future__ import annotations

import argparse
from hook_utils import checkpoint_path, normalize_path, now, write_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--scope', action='append', required=True)
    parser.add_argument('--basis', required=True, help='Short note quoting/summarizing explicit user permission')
    parser.add_argument('--ttl-seconds', type=int, default=1800)
    args = parser.parse_args()
    ts = now()
    write_json(checkpoint_path('reference-permission.json'), {
        'result': 'approved',
        'scope_paths': sorted(set(normalize_path(p) for p in args.scope)),
        'basis': args.basis,
        'created_at': ts,
        'expires_at': ts + args.ttl_seconds,
    })
    print('✅ reference permission checkpoint recorded')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
