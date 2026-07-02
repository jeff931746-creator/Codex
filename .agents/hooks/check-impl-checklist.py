#!/usr/bin/env python3
"""Hard block implementation/code changes without structured independent review."""
from __future__ import annotations

from hook_utils import active_task_scope, checkpoint_path, deny, git_diff_hash, in_scope, load_payload, now, project_code_changed_paths, read_json

MAX_AGE = 1800


def code_changed() -> list[str]:
    return project_code_changed_paths(active_task_scope() or ['.'])


def main() -> int:
    load_payload()
    changed = code_changed()
    if not changed:
        return 0
    checkpoint = read_json(checkpoint_path('implementation-review.json'))
    if not checkpoint:
        return deny('BLOCKED: implementation/code changes require structured independent review checkpoint.')
    if checkpoint.get('result') != 'pass':
        return deny('BLOCKED: implementation review checkpoint is not pass.')
    if int(checkpoint.get('expires_at') or 0) <= now() or int(checkpoint.get('created_at') or 0) <= 0:
        return deny('BLOCKED: implementation review checkpoint expired or invalid.')
    if checkpoint.get('reviewer_runtime') == checkpoint.get('main_runtime'):
        return deny('BLOCKED: implementation review reviewer_runtime must differ from main_runtime.')
    if checkpoint.get('blocking_findings') not in ([], None):
        return deny('BLOCKED: implementation review has blocking findings.')
    scope = checkpoint.get('scope_paths') or []
    missing = [p for p in changed if not in_scope(p, scope)]
    if missing:
        return deny('BLOCKED: implementation review scope does not cover changed code.\nMissing: ' + ', '.join(missing[:12]))
    if checkpoint.get('reviewed_diff_hash') != git_diff_hash(scope):
        return deny('BLOCKED: implementation review diff hash does not match current scoped diff.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
