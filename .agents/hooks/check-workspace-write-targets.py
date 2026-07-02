#!/usr/bin/env python3
"""Hard block file writes outside the workspace or allowed temp roots."""
from __future__ import annotations

from hook_utils import active_task_scope, deny, extract_write_paths, in_scope, is_allowed_write, load_payload, rel_to_workspace, resolve_path, tool_name, WRITE_TOOLS


def main() -> int:
    payload = load_payload()
    name = tool_name(payload)
    paths = extract_write_paths(payload)
    if name not in WRITE_TOOLS and not paths:
        return 0
    blocked = []
    scope = active_task_scope()
    out_of_scope = []
    for raw in paths:
        path = resolve_path(raw, payload.get('cwd'))
        if not is_allowed_write(path):
            blocked.append(f'{raw} -> {path}')
        rel = rel_to_workspace(path)
        if scope and rel and not in_scope(rel, scope):
            out_of_scope.append(rel)
    if blocked:
        return deny('BLOCKED: write target outside allowed workspace/temp roots.\n' + '\n'.join(blocked[:12]))
    if out_of_scope:
        return deny('BLOCKED: write target outside active task scope.\n' + ', '.join(out_of_scope[:12]))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
