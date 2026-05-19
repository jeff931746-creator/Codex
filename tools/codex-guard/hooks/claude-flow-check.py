#!/usr/bin/env python3
"""Codex hooks: require Claude rule intake before mutating workspace files.

Claude remains the rule author. This hook only records whether Codex has read
the Claude-owned rule sources for the current workspace turn, then blocks
write-capable tool calls until that intake is visible.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import sys
import time
from pathlib import Path
from typing import Any


WORKSPACE = "/Users/mt/Documents/Codex"
STATE_PATH = Path("/private/tmp/codex-claude-flow-check-state.json")
STATE_TTL_SECONDS = 60 * 60

REQUIRED_CLAUDE_SOURCES = {
    "memory": "/Users/mt/.claude/projects/-Users-mt-Documents-Codex/memory/MEMORY.md",
    "workflow": f"{WORKSPACE}/.claude/rules/workflow-chain.md",
    "task_flow": f"{WORKSPACE}/.claude/rules/task-flow-matrix.md",
    "delegation": f"{WORKSPACE}/.claude/rules/agent-delegation-policy.md",
}

KNOWLEDGE_ASSET_ROOTS = (
    f"{WORKSPACE}/archive/方法论",
    f"{WORKSPACE}/archive/资料/人群簇库",
    f"{WORKSPACE}/archive/资料/买量组合库",
    f"{WORKSPACE}/reference/部门标准",
)

KNOWLEDGE_ASSET_NAME_PATTERNS = (
    "标准",
    "方法论",
    "总表",
)

EXPLICIT_WRITE_VERBS = (
    "写入",
    "写到",
    "沉淀",
    "更新",
    "整理",
    "修改",
    "保存",
    "落到",
    "加到",
    "加入",
    "改文档",
    "改文件",
    "修订",
    "补充到",
    "记录到",
    "放到",
)

DISCUSSION_MARKERS = (
    "为什么",
    "怎么",
    "如何",
    "是否",
    "能不能",
    "是不是",
    "要不要",
    "吗",
    "?",
    "？",
)

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


def collect_strings(payload: Any) -> list[str]:
    values: list[str] = []
    for _key, value in iter_items(payload):
        if isinstance(value, str):
            values.append(value)
    return values


def load_payload() -> Any:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


def load_state() -> dict[str, Any]:
    try:
        state = json.loads(STATE_PATH.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        state = {}
    if time.time() - float(state.get("started_at", 0)) > STATE_TTL_SECONDS:
        state = {}
    return state


def save_state(state: dict[str, Any]) -> None:
    state["updated_at"] = time.time()
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n")


def normalize_path(value: str, workdir: str | None) -> str:
    if value.startswith("/"):
        return os.path.normpath(value)
    return os.path.normpath(os.path.join(workdir or WORKSPACE, value))


def is_knowledge_asset_path(path: str) -> bool:
    normalized = os.path.normpath(path)
    if any(normalized == root or normalized.startswith(root + "/") for root in KNOWLEDGE_ASSET_ROOTS):
        return True
    basename = os.path.basename(normalized)
    return basename.endswith(".md") and any(pattern in basename for pattern in KNOWLEDGE_ASSET_NAME_PATTERNS)


def command_tokens(command: str) -> list[str]:
    try:
        return shlex.split(command)
    except ValueError:
        return []


def shell_looks_mutating(command: str) -> bool:
    if re.search(r"(^|[^<])>>?|<<|<<<", command):
        return True
    tokens = command_tokens(command)
    if not tokens:
        return bool(re.search(r"\b(rm|mv|cp|tee|mkdir|touch|chmod|perl|sed|python3?|sh|zsh)\b", command))
    executable = os.path.basename(tokens[0])
    if executable in {"sed", "perl"}:
        return any(flag.startswith("-i") for flag in tokens[1:])
    if executable in READ_COMMANDS and executable not in MUTATING_COMMANDS:
        return False
    if executable == "cat":
        return bool(re.search(r"(^|[^<])>>?", command))
    return executable in MUTATING_COMMANDS


def is_read_command(command: str) -> bool:
    tokens = command_tokens(command)
    if not tokens:
        return False
    executable = os.path.basename(tokens[0])
    return executable in READ_COMMANDS and not shell_looks_mutating(command)


def mentioned_sources(command: str, workdir: str | None) -> set[str]:
    sources: set[str] = set()
    tokens = command_tokens(command)
    haystack = [command, *tokens]
    for name, source in REQUIRED_CLAUDE_SOURCES.items():
        for value in haystack:
            if source in value or normalize_path(value, workdir) == source:
                sources.add(name)
                break
    return sources


def patch_looks_mutating(text: str | None) -> bool:
    return bool(text and "*** Begin Patch" in text)


def patch_target_paths(text: str | None, workdir: str | None) -> set[str]:
    if not text:
        return set()
    targets: set[str] = set()
    for line in text.splitlines():
        match = re.match(r"\*\*\* (?:Add|Update|Delete) File: (.+)$", line)
        if match:
            targets.add(normalize_path(match.group(1).strip(), workdir))
    return targets


def command_target_paths(command: str | None, workdir: str | None) -> set[str]:
    if not command:
        return set()
    targets: set[str] = set()
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()
    for token in tokens:
        if token.startswith("-"):
            continue
        if token.startswith("/") or "/" in token or token.endswith(".md"):
            targets.add(normalize_path(token, workdir))
    return targets


def targets_knowledge_asset(paths: set[str]) -> bool:
    return any(is_knowledge_asset_path(path) for path in paths)


def explicit_write_authorized(prompt: str | None) -> bool:
    if not prompt:
        return False
    has_write_verb = any(verb in prompt for verb in EXPLICIT_WRITE_VERBS)
    if not has_write_verb:
        return False
    # Discussion-style questions are not write authorization unless they also
    # contain a concrete destination such as "写入/更新/沉淀到 X".
    has_destination = bool(re.search(r"(写入|写到|沉淀到|更新到|整理到|保存到|落到|加到|加入|补充到|记录到|放到|改文档|改文件)", prompt))
    if any(marker in prompt for marker in DISCUSSION_MARKERS) and not has_destination:
        return False
    return True


def latest_prompt_from_payload(payload: Any) -> str | None:
    prompt = find_key(payload, {"prompt", "user_prompt", "user_input", "message"})
    if prompt:
        return prompt
    # Some runtimes use different hook payload shapes. On UserPromptSubmit the
    # user prompt is usually the longest string and there is no tool command.
    strings = [value for value in collect_strings(payload) if value.strip()]
    if not strings:
        return None
    return max(strings, key=len)


def looks_like_user_prompt_submit(payload: Any, tool_name: str, command: str, patch_text: str | None) -> bool:
    if tool_name or command or patch_looks_mutating(patch_text):
        return False
    event = find_key(payload, {"hook_event_name", "event", "type"}) or ""
    if "UserPromptSubmit" in event:
        return True
    return bool(latest_prompt_from_payload(payload))


def block(message: str) -> int:
    print(f"Blocked Codex flow: {message}", file=sys.stderr)
    print(
        "Read Claude rule sources first; Claude is the authoritative rule source for this workspace.",
        file=sys.stderr,
    )
    return 1


def block_knowledge_asset(message: str) -> int:
    print(f"Blocked knowledge-asset write: {message}", file=sys.stderr)
    print(
        "Current user prompt must explicitly authorize writing/updating/saving the knowledge asset.",
        file=sys.stderr,
    )
    return 1


def main() -> int:
    payload = load_payload()
    tool_name = find_key(payload, {"tool_name", "name", "recipient_name"}) or ""
    command = find_key(payload, {"cmd", "command"}) or ""
    patch_text = find_key(payload, {"patch", "input", "raw"})
    workdir = find_key(payload, {"workdir", "cwd"}) or WORKSPACE

    state = load_state()
    if not state:
        state = {
            "started_at": time.time(),
            "required": sorted(REQUIRED_CLAUDE_SOURCES),
            "read": [],
        }

    if looks_like_user_prompt_submit(payload, tool_name, command, patch_text):
        prompt = latest_prompt_from_payload(payload)
        state["latest_user_prompt"] = prompt or ""
        state["latest_user_prompt_at"] = time.time()
        state["knowledge_asset_write_authorized"] = explicit_write_authorized(prompt)
        save_state(state)
        print("Codex Claude flow check passed.")
        return 0

    if command and is_read_command(command):
        read = set(state.get("read", []))
        read.update(mentioned_sources(command, workdir))
        state["read"] = sorted(read)
        save_state(state)
        print("Codex Claude flow check passed.")
        return 0

    read = set(state.get("read", []))
    missing = sorted(set(REQUIRED_CLAUDE_SOURCES) - read)
    mutating = bool(command and shell_looks_mutating(command)) or "apply_patch" in tool_name or patch_looks_mutating(patch_text)

    target_paths = command_target_paths(command, workdir) | patch_target_paths(patch_text, workdir)
    if mutating and targets_knowledge_asset(target_paths) and not bool(state.get("knowledge_asset_write_authorized")):
        return block_knowledge_asset("missing explicit write authorization in the current user prompt")

    if mutating and missing:
        return block(f"missing Claude rule intake: {', '.join(missing)}")

    if not mutating and missing:
        print(f"Codex flow warning: Claude rule intake incomplete: {', '.join(missing)}", file=sys.stderr)

    save_state(state)
    print("Codex Claude flow check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
