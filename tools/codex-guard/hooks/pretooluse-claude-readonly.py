#!/usr/bin/env python3
"""Codex PreToolUse hook: keep Claude-owned paths read-only for Codex.

The hook accepts either:
- a Codex hook JSON payload on stdin, or
- explicit path/command arguments for local testing.

It exits non-zero only when a write-capable tool invocation appears to target a
Claude-owned path.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import sys
from typing import Any


PROTECTED_ROOTS = (
    "/Users/mt/.claude",
    "/Users/mt/Documents/Codex/.claude",
)

WRITE_TOOL_HINTS = {
    "apply_patch",
    "functions.apply_patch",
    "exec_command",
    "functions.exec_command",
    "write_stdin",
    "functions.write_stdin",
}

MUTATING_COMMANDS = {
    "apply_patch",
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

READ_COMMANDS = {
    "awk",
    "cat",
    "find",
    "grep",
    "head",
    "less",
    "ls",
    "mdls",
    "nl",
    "rg",
    "sed",
    "stat",
    "tail",
    "wc",
}


def has_claude_segment(value: str) -> bool:
    normalized = value.replace("\\", "/")
    return (
        normalized == ".claude"
        or normalized.startswith(".claude/")
        or "/.claude/" in normalized
        or normalized.endswith("/.claude")
    )


def absolute_path(value: str, workdir: str | None = None) -> str:
    if value.startswith("/"):
        return os.path.normpath(value)
    base = workdir or os.getcwd()
    return os.path.normpath(os.path.join(base, value))


def is_protected_value(value: str, workdir: str | None = None) -> bool:
    if not value:
        return False
    if has_claude_segment(value):
        return True
    absolute = absolute_path(value, workdir)
    return any(absolute == root or absolute.startswith(root + "/") for root in PROTECTED_ROOTS)


def iter_items(value: Any, prefix: str = ""):
    if isinstance(value, dict):
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            yield from iter_items(child, child_prefix)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_items(child, f"{prefix}[{index}]")
    else:
        yield prefix, value


def find_key(payload: Any, wanted: set[str]) -> str | None:
    for key, value in iter_items(payload):
        if key.split(".")[-1] in wanted and isinstance(value, str):
            return value
    return None


def collect_path_values(payload: Any) -> list[tuple[str, str]]:
    path_keys = {
        "file",
        "file_path",
        "filename",
        "path",
        "target",
        "target_path",
        "uri",
        "workdir",
        "cwd",
    }
    results: list[tuple[str, str]] = []
    for key, value in iter_items(payload):
        leaf = key.split(".")[-1]
        if leaf in path_keys and isinstance(value, str):
            results.append((key, value))
    return results


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
    if executable in READ_COMMANDS and executable not in MUTATING_COMMANDS:
        return False
    if executable == "cat":
        return bool(re.search(r"(^|[^<])>>?", command))
    if executable in MUTATING_COMMANDS:
        return True
    return False


def command_mentions_protected(command: str, workdir: str | None = None) -> bool:
    if ".claude" in command or "/Users/mt/.claude" in command:
        return True
    try:
        tokens = shlex.split(command)
    except ValueError:
        return False
    return any(is_protected_value(token, workdir) for token in tokens)


def text_mentions_protected_path(text: str) -> bool:
    if ".claude" in text or "/Users/mt/.claude" in text:
        return True
    return any(root in text for root in PROTECTED_ROOTS)


def block(message: str) -> int:
    print(f"Blocked Codex tool call: {message}", file=sys.stderr)
    print("Codex must treat .claude paths as read-only. Use a Codex-owned file or ask the user.", file=sys.stderr)
    return 1


def load_payload(argv: list[str]) -> Any:
    if argv:
        return {"argv": argv}

    raw = sys.stdin.read()
    if not raw.strip():
        return {}

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


def main() -> int:
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if is_protected_value(arg):
                return block(f"argument targets Claude-owned path: {arg}")
        print("Codex PreToolUse guard passed.")
        return 0

    payload = load_payload(sys.argv[1:])
    tool_name = find_key(payload, {"tool_name", "name", "recipient_name"}) or ""
    workdir = find_key(payload, {"workdir", "cwd"})
    command = find_key(payload, {"cmd", "command"})
    patch_text = find_key(payload, {"patch", "input", "raw"})

    if command and shell_looks_mutating(command) and command_mentions_protected(command, workdir):
        return block(f"mutating shell command targets Claude-owned path: {command}")

    if "apply_patch" in tool_name or (patch_text and "*** Begin Patch" in patch_text):
        if patch_text and text_mentions_protected_path(patch_text):
            return block("apply_patch payload contains a Claude-owned path")

    for key, value in collect_path_values(payload):
        if is_protected_value(value, workdir):
            if tool_name in WRITE_TOOL_HINTS or shell_looks_mutating(command or ""):
                return block(f"{key} targets Claude-owned path: {value}")

    print("Codex PreToolUse guard passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
