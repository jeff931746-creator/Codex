#!/usr/bin/env python3
"""Record structured independent semantic-review checkpoint."""
from __future__ import annotations

import argparse
import json
from hook_utils import RUNTIME, active_task_scope, checkpoint_path, git_diff_hash, normalize_path, now, write_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--main-runtime', default=RUNTIME)
    parser.add_argument('--reviewer-runtime', required=True)
    parser.add_argument('--result', choices=['pass', 'fail'], required=True)
    parser.add_argument('--blocking-findings', default='[]')
    parser.add_argument('--scope', action='append', default=[])
    parser.add_argument('--ttl-seconds', type=int, default=1800)
    parser.add_argument('--standard', action='append', default=[])
    parser.add_argument('--dimension', action='append', default=[])
    args = parser.parse_args()
    if normalize_path(args.reviewer_runtime) == normalize_path(args.main_runtime):
        print('--reviewer-runtime must differ from --main-runtime')
        return 2
    try:
        blocking = json.loads(args.blocking_findings)
        if not isinstance(blocking, list):
            raise ValueError
    except Exception:
        print('--blocking-findings must be a JSON list')
        return 2
    scope = sorted(set(normalize_path(p) for p in (args.scope or active_task_scope() or ['.'])))
    ts = now()
    data = {
        'result': args.result,
        'main_runtime': args.main_runtime,
        'reviewer_runtime': args.reviewer_runtime,
        'scope_paths': scope,
        'reviewed_diff_hash': git_diff_hash(scope),
        'blocking_findings': blocking,
        'standards': [normalize_path(p) for p in args.standard],
        'created_at': ts,
        'expires_at': ts + args.ttl_seconds,
    }
    data['dimensions'] = args.dimension
    write_json(checkpoint_path('semantic-review.json'), data)
    print('✅ semantic-review checkpoint recorded')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
