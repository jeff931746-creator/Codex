#!/usr/bin/env python3
"""Block project-memory writes to runtime-private state locations."""
from __future__ import annotations

import json
import os
import re
import shlex
import sys
from typing import Any


PRIVATE_PATTERNS = (
    ".claude",
    ".codex",
    ".cursor",
    ".continue",
    ".aider",
    ".gemini",
    "/Users/mt/.claude",
    "/Users/mt/.codex",
    "/Users/mt/.cursor",
    "/Users/mt/.continue",
    "/Users/mt/.aider",
    "/Users/mt/.gemini",
)

WRITE_TOOLS = {
    "Write",
    "Edit",
    "MultiEdit",
    "NotebookEdit",
    "apply_patch",
    "functions.apply_patch",
}

MUTATING_COMMANDS = {
    "cat",
    "chmod",
    "chown",
    "cp",
    "ditto",
    "install",
    "ln",
    "mkdir",
    "mv",
    "perl",
    "python",
    "python3",
    "rm",
    "rsync",
    "sed",
    "sh",
    "tee",
    "touch",
    "zsh",
}


def iter_items(value: Any):
    if isinstance(value, dict):
        for child in value.values():
            yield from iter_items(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_items(child)
    elif isinstance(value, str):
        yield value


def load_payload() -> Any:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


def mentions_private_path(text: str) -> bool:
    normalized = text.replace("\\", "/")
    return any(pattern in normalized for pattern in PRIVATE_PATTERNS)


def shell_looks_mutating(command: str) -> bool:
    if re.search(r"(^|[^<])>>?|<<|<<<", command):
        return True
    try:
        tokens = shlex.split(command)
    except ValueError:
        return bool(re.search(r"\b(rm|mv|cp|tee|mkdir|touch|chmod|perl|sed|python3?|sh|zsh)\b", command))
    if not tokens:
        return False
    executable = os.path.basename(tokens[0])
    if executable in {"sed", "perl"}:
        return any(flag.startswith("-i") for flag in tokens[1:])
    if executable == "cat":
        return bool(re.search(r"(^|[^<])>>?", command))
    return executable in MUTATING_COMMANDS


def find_string(payload: Any, keys: set[str]) -> str:
    if not isinstance(payload, dict):
        return ""
    stack = [payload]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            for key, value in current.items():
                if key in keys and isinstance(value, str):
                    return value
                if isinstance(value, (dict, list)):
                    stack.append(value)
        elif isinstance(current, list):
            stack.extend(item for item in current if isinstance(item, (dict, list)))
    return ""


def deny(reason: str) -> int:
    print(reason, file=sys.stderr, flush=True)
    return 2


def main() -> int:
    payload = load_payload()
    tool_name = find_string(payload, {"tool_name", "name", "recipient_name"})
    command = find_string(payload, {"command", "cmd"})

    values = list(iter_items(payload))

    if tool_name in WRITE_TOOLS and any(mentions_private_path(value) for value in values):
        return deny("DANGER:工程记忆/规则不得写入 runtime 私有目录。请写入 .agents/memory、.agents/rules 或 workspace/tmp/agent-checkpoints/<runtime>/。")

    if command and shell_looks_mutating(command) and mentions_private_path(command):
        return deny("DANGER:工程记忆/规则不得写入 runtime 私有目录。请写入 .agents/memory、.agents/rules 或 workspace/tmp/agent-checkpoints/<runtime>/。")

    patch_text = find_string(payload, {"patch", "input", "raw"})
    if patch_text and "*** Begin Patch" in patch_text and mentions_private_path(patch_text):
        return deny("DANGER:工程记忆/规则不得写入 runtime 私有目录。请写入 .agents/memory、.agents/rules 或 workspace/tmp/agent-checkpoints/<runtime>/。")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
