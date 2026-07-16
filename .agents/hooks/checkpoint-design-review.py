#!/usr/bin/env python3
"""Record structured independent design inspection without granting decision authority."""
from __future__ import annotations

import argparse
import json
from hook_utils import RUNTIME, active_task_scope, checkpoint_path, git_diff_hash, normalize_path, now, write_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--main-runtime', default=RUNTIME)
    parser.add_argument('--reviewer-runtime', required=True)
    parser.add_argument('--result', choices=['reviewed', 'incomplete'], required=True)
    parser.add_argument('--findings', default='[]')
    parser.add_argument('--user-message-excerpt', default='')
    parser.add_argument('--scope', action='append', default=[])
    parser.add_argument('--ttl-seconds', type=int, default=1800)
    parser.add_argument('--standard', action='append', default=[])
    args = parser.parse_args()
    if normalize_path(args.reviewer_runtime) == normalize_path(args.main_runtime):
        print('--reviewer-runtime must differ from --main-runtime')
        return 2
    try:
        findings = json.loads(args.findings)
        if not isinstance(findings, list):
            raise ValueError
    except Exception:
        print('--findings must be a JSON list')
        return 2
    if findings and not args.user_message_excerpt.strip():
        print('non-empty --findings require --user-message-excerpt')
        return 2
    scope = sorted(set(normalize_path(p) for p in (args.scope or active_task_scope() or ['.'])))
    ts = now()
    data = {
        'result': args.result,
        'main_runtime': args.main_runtime,
        'reviewer_runtime': args.reviewer_runtime,
        'scope_paths': scope,
        'reviewed_diff_hash': git_diff_hash(scope),
        'findings': findings,
        'user_message_excerpt': args.user_message_excerpt.strip(),
        'standards': [normalize_path(p) for p in args.standard],
        'created_at': ts,
        'expires_at': ts + args.ttl_seconds,
    }
    write_json(checkpoint_path('design-review.json'), data)
    print('✅ design-review checkpoint recorded')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
