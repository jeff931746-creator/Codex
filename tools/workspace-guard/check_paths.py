#!/usr/bin/env python3
"""Validate write destinations against the checkout and OS temporary directory."""
from __future__ import annotations
import pathlib
import os
import sys
import tempfile

WORKSPACE = pathlib.Path(__file__).resolve().parents[2]


def allowed_roots() -> tuple[pathlib.Path, ...]:
    roots = (WORKSPACE, pathlib.Path(tempfile.gettempdir()).resolve())
    return roots + ((pathlib.Path('/tmp').resolve(),) if os.name != 'nt' else ())


def is_allowed(path: pathlib.Path) -> bool:
    resolved = path.expanduser().resolve()
    return any(resolved == root or root in resolved.parents for root in allowed_roots())


def main(argv: list[str] | None = None) -> int:
    paths = sys.argv[1:] if argv is None else argv
    if not paths:
        print('Usage: python tools/workspace-guard/check_paths.py <path> [...]', file=sys.stderr)
        return 64
    blocked = [p for p in paths if not is_allowed(pathlib.Path(p))]
    if blocked:
        for path in blocked:
            print(f'Blocked write target outside workspace/temp: {path}', file=sys.stderr)
        return 1
    print(f'Workspace guard passed: {len(paths)} path(s).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
