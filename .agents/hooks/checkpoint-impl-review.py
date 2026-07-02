#!/usr/bin/env python3
"""Record structured independent implementation review checkpoint."""
from __future__ import annotations

import argparse
import json
from hook_utils import RUNTIME, active_task_scope, checkpoint_path, git_diff_hash, normalize_path, now, project_code_changed_paths, write_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--main-runtime', default=RUNTIME)
    parser.add_argument('--reviewer-runtime', required=True)
    parser.add_argument('--result', choices=['pass', 'fail'], required=True)
    parser.add_argument('--blocking-findings', default='[]')
    parser.add_argument('--scope', action='append', default=[])
    parser.add_argument('--ttl-seconds', type=int, default=1800)
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
    changed = project_code_changed_paths(active_task_scope() or ['.'])
    scope = sorted(set(normalize_path(p) for p in (args.scope or changed)))
    if not scope:
        print('No changed code/script files detected; checkpoint not written.')
        return 1
    ts = now()
    write_json(checkpoint_path('implementation-review.json'), {
        'result': args.result,
        'main_runtime': args.main_runtime,
        'reviewer_runtime': args.reviewer_runtime,
        'scope_paths': scope,
        'reviewed_diff_hash': git_diff_hash(scope),
        'blocking_findings': blocking,
        'created_at': ts,
        'expires_at': ts + args.ttl_seconds,
    })
    print('✅ implementation review checkpoint recorded')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
