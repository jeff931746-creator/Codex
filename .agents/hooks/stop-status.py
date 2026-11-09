#!/usr/bin/env python3
"""Report workspace changes without Unix tools."""
from hook_utils import RUNTIME, run_git


def main() -> int:
    result = run_git(['status', '--short'])
    changed = [line for line in result.stdout.splitlines() if 'worktrees/' not in line]
    if changed:
        print(f'{RUNTIME}: {len(changed)} uncommitted workspace entries; review scoped changes before committing.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
