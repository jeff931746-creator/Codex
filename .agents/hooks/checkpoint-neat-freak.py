#!/usr/bin/env python3
"""Record the shared scoped QA checkpoint on every OS."""
import argparse
from hook_utils import active_task_scope, checkpoint_path, git_diff_hash, now, write_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--scope', action='append', default=[])
    args = parser.parse_args()
    scope = args.scope or active_task_scope() or ['.']
    write_json(checkpoint_path('neat-freak.json'), {
        'result': 'pass', 'scope_paths': scope, 'diff_hash': git_diff_hash(scope), 'created_at': now(),
    })
    print('QA checkpoint recorded; changes to the scoped diff invalidate it.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
