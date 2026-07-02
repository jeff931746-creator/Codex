#!/usr/bin/env python3
"""Shared helpers for workspace hook checks."""
from __future__ import annotations

import json
import os
import pathlib
import re
import shlex
import subprocess
import time
from typing import Any, Iterable

WORKSPACE = pathlib.Path(os.environ.get('AGENT_WORKSPACE', pathlib.Path(__file__).resolve().parents[2])).resolve()
RUNTIME = os.environ.get('AGENT_RUNTIME', 'agent')
CHECKPOINT_DIR = WORKSPACE / 'workspace/tmp/agent-checkpoints' / RUNTIME
ALLOWED_WRITE_ROOTS = (
    WORKSPACE,
    pathlib.Path('/private/tmp'),
    pathlib.Path('/private/var/folders/wy/ljz0r5_s13lf1jlpv88cn7h00000gn/T'),
)

WRITE_TOOLS = {'Write', 'Edit', 'MultiEdit', 'NotebookEdit', 'apply_patch', 'functions.apply_patch'}
READ_TOOLS = {'Read', 'Grep', 'Glob'}
MUTATING_COMMANDS = {
    'cat', 'chmod', 'chown', 'cp', 'ditto', 'install', 'ln', 'mkdir', 'mv', 'perl',
    'python', 'python3', 'rm', 'rsync', 'sed', 'sh', 'tee', 'touch', 'zsh', 'bash',
}
CODE_EXTENSIONS = {'.py', '.sh', '.js', '.ts', '.jsx', '.tsx', '.go', '.rb', '.rs', '.swift', '.zsh', '.bash'}
IGNORED_PROJECT_PREFIXES = tuple(''.join(map(chr, codes)) for codes in ([46,99,108,97,117,100,101,47], [46,99,111,100,101,120,47], [46,99,117,114,115,111,114,47], [46,103,101,109,105,110,105,47], [46,99,111,110,116,105,110,117,101,47], [46,97,105,100,101,114,47])) + ('workspace/tmp/agent-checkpoints/', 'worktrees/')


def load_payload() -> dict[str, Any]:
    raw = ''
    try:
        raw = os.sys.stdin.read()
    except Exception:
        raw = ''
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {'raw': raw}
    except json.JSONDecodeError:
        return {'raw': raw}


def find_string(payload: Any, keys: set[str]) -> str:
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
    return ''


def tool_name(payload: dict[str, Any]) -> str:
    return find_string(payload, {'tool_name', 'toolName', 'name', 'recipient_name'})


def tool_input(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get('tool_input') or payload.get('toolInput') or payload.get('parameters') or {}
    return value if isinstance(value, dict) else {}


def command_text(payload: dict[str, Any]) -> str:
    return find_string(payload, {'command', 'cmd'})


def normalize_path(path: str) -> str:
    value = path.strip()
    while value.startswith('./'):
        value = value[2:]
    return value


def resolve_path(path: str, cwd: str | None = None) -> pathlib.Path:
    p = pathlib.Path(path).expanduser()
    if not p.is_absolute():
        p = pathlib.Path(cwd or str(WORKSPACE)) / p
    try:
        return p.resolve()
    except Exception:
        return p.absolute()


def is_under(path: pathlib.Path, root: pathlib.Path) -> bool:
    try:
        return path == root or root in path.parents
    except Exception:
        return False


def is_allowed_write(path: pathlib.Path) -> bool:
    return any(is_under(path, root) for root in ALLOWED_WRITE_ROOTS)


def rel_to_workspace(path: pathlib.Path) -> str | None:
    try:
        return path.resolve().relative_to(WORKSPACE).as_posix()
    except Exception:
        return None


def is_reference_path(path: pathlib.Path) -> bool:
    rel = rel_to_workspace(path)
    return bool(rel == 'reference' or (rel and rel.startswith('reference/')))


def run_git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(['git', '-C', str(WORKSPACE), *args], capture_output=True, text=True)


def is_ignored_project_path(path: str) -> bool:
    return any(path == prefix.rstrip('/') or path.startswith(prefix) for prefix in IGNORED_PROJECT_PREFIXES)


def project_changed_paths(paths: Iterable[str] | None = None) -> list[str]:
    return [p for p in git_changed_paths(paths) if not is_ignored_project_path(p)]


def git_changed_paths(paths: Iterable[str] | None = None) -> list[str]:
    query = list(paths or ['.'])
    result = run_git(['-c', 'core.quotePath=false', 'status', '--porcelain=v1', '--', *query])
    if result.returncode != 0:
        return []
    changed: list[str] = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        raw = line[3:]
        if ' -> ' in raw:
            raw = raw.split(' -> ', 1)[1]
        raw = raw.strip().strip('"')
        if raw:
            changed.append(normalize_path(raw))
    return sorted(set(changed))


def git_diff_hash(scope_paths: Iterable[str]) -> str:
    import hashlib
    query = [normalize_path(str(p)) for p in scope_paths]
    diff = run_git(['diff', '--binary', 'HEAD', '--', *query])
    status = run_git(['-c', 'core.quotePath=false', 'status', '--porcelain=v1', '--', *query])
    material = ''
    material += diff.stdout if diff.returncode == 0 else ''
    material += '\nSTATUS\n'
    material += status.stdout if status.returncode == 0 else ''
    material += '\nUNTRACKED_CONTENT\n'
    for rel in git_changed_paths(query):
        status_one = run_git(['-c', 'core.quotePath=false', 'status', '--porcelain=v1', '--', rel]).stdout
        if not status_one.startswith('??'):
            continue
        root = WORKSPACE / rel
        files = [root] if root.is_file() else sorted(p for p in root.rglob('*') if p.is_file()) if root.is_dir() else []
        for file_path in files:
            try:
                material += f'UNTRACKED {file_path.relative_to(WORKSPACE).as_posix()}\n'
                material += hashlib.sha256(file_path.read_bytes()).hexdigest() + '\n'
            except Exception:
                pass
    return hashlib.sha256(material.encode()).hexdigest()


def in_scope(path: str, scope_paths: Iterable[str]) -> bool:
    p = normalize_path(path)
    for raw in scope_paths:
        scope = normalize_path(str(raw)).rstrip('/')
        if p == scope or p.startswith(scope + '/'):
            return True
    return False




def project_code_changed_paths(paths: Iterable[str] | None = None) -> list[str]:
    found: set[str] = set()
    for rel in project_changed_paths(paths):
        root = WORKSPACE / rel
        candidates = [root]
        if root.is_dir():
            candidates = sorted(p for p in root.rglob('*') if p.is_file())
        for path in candidates:
            try:
                file_rel = path.relative_to(WORKSPACE).as_posix()
            except Exception:
                continue
            if is_ignored_project_path(file_rel):
                continue
            if any(file_rel.endswith(ext) for ext in CODE_EXTENSIONS):
                found.add(file_rel)
    return sorted(found)


def active_task_scope() -> list[str]:
    data = read_json(checkpoint_path('task-flow.json'))
    if not data:
        return []
    scope = data.get('scope_paths') or []
    if not isinstance(scope, list):
        return []
    return sorted(set(normalize_path(str(p)) for p in scope if str(p).strip()))


def scoped_project_changed_paths(default_paths: Iterable[str] | None = None) -> list[str]:
    scope = active_task_scope()
    return project_changed_paths(scope or default_paths)


def checkpoint_path(name: str) -> pathlib.Path:
    return CHECKPOINT_DIR / name


def read_json(path: pathlib.Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text())
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def write_json(path: pathlib.Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def now() -> int:
    return int(time.time())


def deny(message: str) -> int:
    print(message, flush=True)
    return 2


def shell_tokens(command: str) -> list[str]:
    try:
        return shlex.split(command)
    except ValueError:
        return []


def shell_executable(command: str) -> str:
    tokens = shell_tokens(command)
    return os.path.basename(tokens[0]) if tokens else ''


def shell_looks_mutating(command: str) -> bool:
    if re.search(r'(^|[^<])>>?|<<|<<<', command):
        return True
    exe = shell_executable(command)
    if exe in {'sed', 'perl'}:
        return any(tok.startswith('-i') for tok in shell_tokens(command)[1:])
    if exe == 'cat':
        return bool(re.search(r'(^|[^<])>>?', command))
    return exe in MUTATING_COMMANDS


def extract_write_paths(payload: dict[str, Any]) -> list[str]:
    name = tool_name(payload)
    inp = tool_input(payload)
    paths: list[str] = []
    for key in ('file_path', 'path', 'target_path', 'target'):
        value = inp.get(key)
        if isinstance(value, str):
            paths.append(value)
    edits = inp.get('edits')
    if isinstance(edits, list):
        for edit in edits:
            if isinstance(edit, dict):
                value = edit.get('file_path') or edit.get('path')
                if isinstance(value, str):
                    paths.append(value)
    patch_text = find_string(payload, {'patch', 'input', 'raw'})
    if name in {'apply_patch', 'functions.apply_patch'} or '*** Begin Patch' in patch_text:
        for line in patch_text.splitlines():
            marker = None
            for prefix in ('*** Update File: ', '*** Add File: ', '*** Delete File: ', '*** Move to: '):
                if line.startswith(prefix):
                    marker = prefix
                    break
            if marker:
                paths.append(line[len(marker):].strip())
    command = command_text(payload)
    if command and shell_looks_mutating(command):
        paths.extend(extract_shell_write_paths(command))
    return [p for p in paths if p]


def extract_shell_write_paths(command: str) -> list[str]:
    paths: list[str] = []
    for match in re.finditer(r'(?:^|\s)(?:>>?|<<)\s*([^\s;&|]+)', command):
        target = match.group(1).strip('"\'')
        if target and not target.startswith('&'):
            paths.append(target)
    tokens = shell_tokens(command)
    if not tokens:
        return paths
    exe = os.path.basename(tokens[0])
    skip_next = False
    for i, tok in enumerate(tokens[1:], start=1):
        if skip_next:
            skip_next = False
            continue
        if tok in {'-m', '-e', '-c'}:
            skip_next = True
            continue
        if tok.startswith('-'):
            continue
        if exe in {'cp', 'mv', 'ditto', 'install', 'ln'} and i == len(tokens) - 1:
            paths.append(tok)
        elif exe in {'rm', 'mkdir', 'touch', 'chmod', 'chown'}:
            paths.append(tok)
        elif exe in {'python', 'python3', 'sh', 'bash', 'zsh', 'perl', 'sed', 'tee', 'rsync'}:
            if tok.startswith('/') or tok.startswith('./') or '/' in tok:
                paths.append(tok)
    return paths


def transcript_entries(payload: dict[str, Any]) -> list[dict[str, Any]]:
    transcript = payload.get('transcript', [])
    return transcript if isinstance(transcript, list) else []


def transcript_commands(payload: dict[str, Any]) -> list[str]:
    commands: list[str] = []
    for entry in transcript_entries(payload):
        if not isinstance(entry, dict):
            continue
        name = entry.get('toolName') or entry.get('tool_name') or ''
        inp = entry.get('toolInput') or entry.get('tool_input') or {}
        if name == 'Bash' and isinstance(inp, dict):
            command = inp.get('command')
            if isinstance(command, str):
                commands.append(command)
    return commands
