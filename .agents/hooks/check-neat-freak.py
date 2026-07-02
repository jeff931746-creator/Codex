#!/usr/bin/env python3
"""Hard block delivery after file writes unless neat-freak checkpoint matches current scoped diff."""
from __future__ import annotations

from hook_utils import active_task_scope, checkpoint_path, deny, git_diff_hash, load_payload, scoped_project_changed_paths


def checkpoint_valid(scope: list[str]) -> tuple[bool, str]:
    path = checkpoint_path('neat-freak.json')
    if not path.exists():
        return False, 'missing'
    try:
        import json
        data = json.loads(path.read_text())
    except Exception:
        return False, 'corrupt'
    if data.get('result') != 'pass':
        return False, 'not pass'
    saved_scope = data.get('scope_paths') or []
    if set(saved_scope) != set(scope):
        return False, 'scope mismatch'
    if data.get('diff_hash') != git_diff_hash(scope):
        return False, 'diff changed'
    return True, 'ok'


def main() -> int:
    load_payload()
    scope = active_task_scope() or ['.']
    changed = scoped_project_changed_paths(['.'])
    if not changed:
        return 0
    ok, reason = checkpoint_valid(scope)
    if ok:
        return 0
    return deny(f'BLOCKED: file changes require neat-freak/QA checkpoint before delivery ({reason}).')


if __name__ == '__main__':
    raise SystemExit(main())
