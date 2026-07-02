#!/usr/bin/env python3
"""Dispatch Codex hooks to this workspace's shared agent hooks."""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys


WORKSPACE = pathlib.Path("/Users/mt/Documents/Codex-codex-work").resolve()


def in_workspace(path_text: str) -> bool:
    try:
        path = pathlib.Path(path_text).resolve()
    except Exception:
        return False
    return path == WORKSPACE or WORKSPACE in path.parents


def main() -> int:
    if len(sys.argv) < 2:
        print("codex-hook-dispatch: missing target command", file=sys.stderr)
        return 2

    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        payload = {}

    cwd = payload.get("cwd") or os.getcwd()
    if not in_workspace(str(cwd)):
        return 0

    env = os.environ.copy()
    env["AGENT_RUNTIME"] = "codex"
    env["AGENT_WORKSPACE"] = str(WORKSPACE)

    result = subprocess.run(
        sys.argv[1:],
        input=raw,
        text=True,
        cwd=str(WORKSPACE),
        env=env,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
