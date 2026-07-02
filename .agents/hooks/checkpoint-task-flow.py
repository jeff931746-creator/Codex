#!/usr/bin/env python3
"""Record task-flow state for Stop hook enforcement."""
from __future__ import annotations

import argparse
from hook_utils import checkpoint_path, now, write_json


def split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(',') if item.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--flow-intensity', required=True, choices=['quick', 'standard', 'strict'])
    parser.add_argument('--task-type', required=True, choices=['analysis', 'doc-change', 'implementation', 'review', 'collection', 'knowledge-asset'])
    parser.add_argument('--current-gate', required=True)
    parser.add_argument('--completed-gates', default='')
    parser.add_argument('--next-gate', default='')
    parser.add_argument('--blocked-on', default='')
    parser.add_argument('--plan', required=True)
    parser.add_argument('--gate-sequence', default='')
    parser.add_argument('--approval-basis', default='')
    parser.add_argument('--scope', action='append', required=True)
    parser.add_argument('--ttl-seconds', type=int, default=1800)
    args = parser.parse_args()
    ts = now()
    write_json(checkpoint_path('task-flow.json'), {
        'flow_intensity': args.flow_intensity,
        'task_type': args.task_type,
        'current_gate': args.current_gate,
        'completed_gates': split_csv(args.completed_gates),
        'next_gate': args.next_gate,
        'blocked_on': args.blocked_on,
        'plan': args.plan,
        'gate_sequence': split_csv(args.gate_sequence),
        'approval_basis': args.approval_basis,
        'scope_paths': sorted(set(args.scope)),
        'created_at': ts,
        'expires_at': ts + args.ttl_seconds,
    })
    print('✅ task-flow checkpoint recorded')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
