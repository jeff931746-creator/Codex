#!/usr/bin/env python3
"""Block project-memory writes to runtime-private state locations."""
from __future__ import annotations

import pathlib

from hook_utils import deny, extract_write_paths, load_payload, rel_to_workspace, resolve_path

PRIVATE_RUNTIME_NAMES = (
    "claude",
    "codex",
    "cursor",
    "continue",
    "aider",
    "gemini",
)

PRIVATE_PROJECT_DIRS = tuple("." + name for name in PRIVATE_RUNTIME_NAMES)
PRIVATE_HOME_DIRS = tuple(pathlib.Path("/Users/mt") / name for name in PRIVATE_PROJECT_DIRS)

DANGER_MESSAGE = "DANGER:工程记忆/规则不得写入 runtime 私有目录。请写入 .agents/memory、.agents/rules 或 workspace/tmp/agent-checkpoints/<runtime>/。"


def is_under(path: pathlib.Path, root: pathlib.Path) -> bool:
    try:
        return path == root or root in path.parents
    except Exception:
        return False


def is_private_write_target(raw_path: str, cwd: str | None) -> bool:
    path = resolve_path(raw_path, cwd)
    rel = rel_to_workspace(path)
    if rel:
        return any(rel == name or rel.startswith(name + "/") for name in PRIVATE_PROJECT_DIRS)
    return any(is_under(path, root) for root in PRIVATE_HOME_DIRS)


def main() -> int:
    payload = load_payload()
    cwd = payload.get("cwd")
    cwd = cwd if isinstance(cwd, str) else None
    blocked = [path for path in extract_write_paths(payload) if is_private_write_target(path, cwd)]
    if blocked:
        return deny(DANGER_MESSAGE + "\n" + "\n".join(blocked[:12]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
