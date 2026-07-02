#!/usr/bin/env python3
"""Hard block runtime pointer files that copy workflow logic instead of pointing to .agents."""
from __future__ import annotations

from pathlib import Path
from hook_utils import WORKSPACE, deny, git_changed_paths

POINTERS = ['AGENTS.md', 'CODEX.md', 'CLAUDE.md']
MAX_NONEMPTY_LINES = 90
REQUIRED = ['.agents/AI-ONBOARDING.md', '.agents/AI-ENTRYPOINTS.md']
FORBIDDEN_HEADINGS = ['## Flow Types', '## Plan Requirements', '## Review Discipline', '## Git Hygiene']


def pointer_bad(path: Path) -> str | None:
    if not path.exists():
        return None
    text = path.read_text(errors='ignore')
    if any(req not in text for req in REQUIRED):
        return 'missing .agents onboarding/entrypoints pointers'
    nonempty = [line for line in text.splitlines() if line.strip()]
    if len(nonempty) > MAX_NONEMPTY_LINES:
        return f'too long for thin pointer ({len(nonempty)} non-empty lines)'
    for heading in FORBIDDEN_HEADINGS:
        if heading in text:
            return f'copies workflow section {heading}'
    return None


def main() -> int:
    changed = set(git_changed_paths(POINTERS))
    if not changed:
        return 0
    problems = []
    for rel in POINTERS:
        if rel in changed:
            reason = pointer_bad(WORKSPACE / rel)
            if reason:
                problems.append(f'{rel}: {reason}')
    if problems:
        return deny('BLOCKED: runtime entry files must remain thin pointers.\n' + '\n'.join(problems))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
