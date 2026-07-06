#!/usr/bin/env python3
"""Block risky new-task work while an active context handoff is required."""
from __future__ import annotations

from hook_utils import (
    checkpoint_path,
    command_text,
    deny,
    extract_write_paths,
    load_payload,
    read_json,
    rel_to_workspace,
    resolve_path,
    shell_executable,
    shell_looks_mutating,
    tool_name,
    WRITE_TOOLS,
)

STATE_NAME = 'context-pressure.json'
GIT_COMMANDS = {'git'}
LONG_RUNNING_COMMANDS = {'codex', 'claude', 'python', 'python3', 'node', 'npm', 'pnpm', 'yarn', 'bash', 'sh', 'zsh'}


def pressure_active() -> bool:
    state = read_json(checkpoint_path(STATE_NAME))
    if not state:
        return False
    # pending-next-task is deliberately non-blocking so the current task can finish.
    return state.get('status') == 'active' and bool(state.get('handoff_required', True))


def is_state_update_path(raw_path: str, cwd: str | None) -> bool:
    rel = rel_to_workspace(resolve_path(raw_path, cwd))
    return bool(rel and rel.startswith('workspace/tmp/agent-checkpoints/') and rel.endswith('/context-pressure.json'))


def is_allowed_state_update(payload: dict) -> bool:
    paths = extract_write_paths(payload)
    return bool(paths) and all(is_state_update_path(path, payload.get('cwd')) for path in paths)


def is_context_checkpoint_command(command: str) -> bool:
    return any(
        marker in command
        for marker in (
            'checkpoint-context-pressure.py',
            'context-pressure-on.py',
            'context-pressure-off.py',
        )
    )


def risky_tool(payload: dict) -> bool:
    name = tool_name(payload)
    if name in WRITE_TOOLS:
        return not is_allowed_state_update(payload)
    command = command_text(payload)
    if not command:
        return False
    if is_context_checkpoint_command(command):
        return False
    exe = shell_executable(command)
    if exe in GIT_COMMANDS:
        return True
    if shell_looks_mutating(command):
        return not is_allowed_state_update(payload)
    if exe in LONG_RUNNING_COMMANDS:
        return True
    return False


def main() -> int:
    payload = load_payload()
    if not pressure_active():
        return 0
    if risky_tool(payload):
        return deny(
            'BLOCKED: context pressure handoff is required before starting risky new-task work. '
            'Write or deliver a compact continuation summary first, then mark '
            'workspace/tmp/agent-checkpoints/<runtime>/context-pressure.json as '
            'status=handoff-complete or resolved.'
        )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
