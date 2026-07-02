#!/usr/bin/env python3
"""Record or resolve context-pressure handoff state."""
from __future__ import annotations

import argparse

from hook_utils import checkpoint_path, now, write_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--status', required=True, choices=['pending-next-task', 'active', 'handoff-complete', 'resolved'])
    parser.add_argument('--used-percent', type=int, default=0)
    parser.add_argument('--reason', default='')
    parser.add_argument('--handoff-path', default='')
    parser.add_argument('--ttl-seconds', type=int, default=86400)
    args = parser.parse_args()

    ts = now()
    write_json(checkpoint_path('context-pressure.json'), {
        'status': args.status,
        'handoff_required': args.status == 'active',
        'applies_from_next_task': args.status == 'pending-next-task',
        'used_percent': args.used_percent,
        'reason': args.reason,
        'handoff_path': args.handoff_path,
        'created_at': ts,
        'expires_at': ts + args.ttl_seconds,
    })
    print('context-pressure checkpoint recorded')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
