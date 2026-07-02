#!/usr/bin/env python3
"""Hard block delivery when code/script files changed but no validation was detected."""
from __future__ import annotations

from hook_utils import active_task_scope, checkpoint_path, deny, load_payload, now, project_code_changed_paths, read_json, transcript_commands

VALIDATION_KEYWORDS = [
    'py_compile', 'pytest', 'unittest', 'npm test', 'yarn test', 'pnpm test',
    'python3 -m', 'python -m', 'node ', 'bash ', 'sh ', 'lint', 'mypy', 'ruff',
    'flake8', 'black --check', 'smoke', 'assert', 'test', 'check', 'verify', 'json.tool',
]
MAX_AGE = 1800


def code_changed() -> list[str]:
    return project_code_changed_paths(active_task_scope() or ['.'])


def checkpoint_ok() -> bool:
    checkpoint = read_json(checkpoint_path('validation.json'))
    if not checkpoint:
        return False
    if int(checkpoint.get('expires_at') or 0) <= now():
        return False
    scope = checkpoint.get('scope_paths') or []
    changed = code_changed()
    return bool(scope) and all(any(p == s or p.startswith(str(s).rstrip('/') + '/') for s in scope) for p in changed)


def main() -> int:
    payload = load_payload()
    changed = code_changed()
    if not changed:
        return 0
    commands = ' \n'.join(transcript_commands(payload)).lower()
    ran_validation = any(keyword in commands for keyword in VALIDATION_KEYWORDS)
    if ran_validation or checkpoint_ok():
        return 0
    return deny('BLOCKED: code/script files changed but no validation command/checkpoint was detected.\nChanged: ' + ', '.join(changed[:12]))


if __name__ == '__main__':
    raise SystemExit(main())
