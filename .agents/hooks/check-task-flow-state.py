#!/usr/bin/env python3
"""Hard block delivery when file-changing work lacks a task-flow checkpoint."""
from __future__ import annotations

from hook_utils import active_task_scope, checkpoint_path, deny, load_payload, now, scoped_project_changed_paths, read_json

MAX_AGE = 1800
STRICT_LONG_TERM_PREFIXES = ('.agents/', 'reference/', 'archive/')


def is_long_term(path: str) -> bool:
    return any(path == p.rstrip('/') or path.startswith(p) for p in STRICT_LONG_TERM_PREFIXES)


def main() -> int:
    load_payload()
    changed = scoped_project_changed_paths(['.'])
    meaningful = [p for p in changed if not p.startswith('workspace/tmp/agent-checkpoints/')]
    if not meaningful:
        return 0
    checkpoint = read_json(checkpoint_path('task-flow.json'))
    if not checkpoint:
        return deny('BLOCKED: file-changing work requires task-flow checkpoint before delivery. Run .agents/hooks/checkpoint-task-flow.py.')
    if int(checkpoint.get('expires_at') or 0) <= now():
        return deny('BLOCKED: task-flow checkpoint expired.')
    flow = checkpoint.get('flow_intensity')
    task_type = checkpoint.get('task_type')
    if flow not in {'quick', 'standard', 'strict'} or not task_type:
        return deny('BLOCKED: task-flow checkpoint missing flow_intensity/task_type.')
    if any(is_long_term(p) for p in meaningful) and flow != 'strict':
        return deny('BLOCKED: long-term workflow asset changes require strict flow checkpoint.')
    if flow == 'strict' and not checkpoint.get('approval_basis'):
        return deny('BLOCKED: strict flow requires approval_basis in task-flow checkpoint.')
    if task_type in {'doc-change', 'implementation'} and not checkpoint.get('gate_sequence'):
        return deny('BLOCKED: doc-change/implementation requires gate_sequence in task-flow checkpoint.')
    if not checkpoint.get('plan'):
        return deny('BLOCKED: task-flow checkpoint missing plan.')
    if not checkpoint.get('scope_paths'):
        return deny('BLOCKED: task-flow checkpoint missing scope_paths.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
