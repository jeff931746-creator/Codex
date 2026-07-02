#!/usr/bin/env python3
"""Block delivery when long-term workflow assets changed without independent review."""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time
from typing import Iterable

WORKSPACE = pathlib.Path(os.environ.get('AGENT_WORKSPACE', pathlib.Path(__file__).resolve().parents[2])).resolve()
RUNTIME = os.environ.get('AGENT_RUNTIME', 'agent')
CHECKPOINT_DIR = WORKSPACE / 'workspace/tmp/agent-checkpoints' / RUNTIME
CHECKPOINT_FILE = CHECKPOINT_DIR / 'independent-review.json'
SCOPE_FILE = CHECKPOINT_DIR / 'independent-review-scope.json'
TASK_FLOW_FILE = CHECKPOINT_DIR / 'task-flow.json'
MAX_AGE = 1800
LONG_TERM_PREFIXES = ('.agents/', 'reference/', 'archive/')
REQUIRED_PLAN_FIELDS = ('similar_assets_scanned', 'rules_read', 'automation_entrypoints_checked', 'source_of_truth')
DEFAULT_GIT_PATHS = ('.agents', 'reference', 'archive')


def run_git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(['git', '-C', str(WORKSPACE), *args], capture_output=True, text=True)


def normalize_path(path: str) -> str:
    value = path.strip()
    while value.startswith('./'):
        value = value[2:]
    return value


def is_long_term(path: str) -> bool:
    p = normalize_path(path)
    return any(p == prefix.rstrip('/') or p.startswith(prefix) for prefix in LONG_TERM_PREFIXES)


def in_scope(path: str, scope_paths: Iterable[str]) -> bool:
    p = normalize_path(path)
    for raw in scope_paths:
        scope = normalize_path(str(raw)).rstrip('/')
        if p == scope or p.startswith(scope + '/'):
            return True
    return False


def changed_paths(scope_paths: Iterable[str] | None = None) -> list[str]:
    query_paths = [normalize_path(str(p)) for p in (scope_paths or DEFAULT_GIT_PATHS)]
    result = run_git(['-c', 'core.quotePath=false', 'status', '--porcelain=v1', '--', *query_paths])
    if result.returncode != 0:
        return []
    paths: list[str] = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        raw = line[3:]
        if ' -> ' in raw:
            raw = raw.split(' -> ', 1)[1]
        raw = raw.strip().strip('"')
        if raw and is_long_term(raw) and (scope_paths is None or in_scope(raw, query_paths)):
            paths.append(normalize_path(raw))
    return sorted(set(paths))


def iter_untracked_files(rel: str) -> list[pathlib.Path]:
    root = WORKSPACE / rel
    if root.is_file():
        return [root]
    if not root.is_dir():
        return []
    files: list[pathlib.Path] = []
    for path in root.rglob('*'):
        if path.is_file():
            files.append(path)
    return sorted(files)


def untracked_file_material(paths: Iterable[str]) -> str:
    parts: list[str] = []
    for rel in sorted(set(paths)):
        status = run_git(['-c', 'core.quotePath=false', 'status', '--porcelain=v1', '--', rel]).stdout
        if not status.startswith('??'):
            continue
        for path in iter_untracked_files(rel):
            try:
                data = path.read_bytes()
                file_rel = path.relative_to(WORKSPACE).as_posix()
            except Exception:
                continue
            parts.append(f'UNTRACKED {file_rel}\n')
            parts.append(hashlib.sha256(data).hexdigest())
            parts.append('\n')
    return ''.join(parts)


def current_diff_hash(scope_paths: Iterable[str]) -> str:
    query_paths = [normalize_path(str(p)) for p in scope_paths]
    diff = run_git(['diff', '--binary', 'HEAD', '--', *query_paths])
    status = run_git(['-c', 'core.quotePath=false', 'status', '--porcelain=v1', '--', *query_paths])
    material = ''
    material += diff.stdout if diff.returncode == 0 else ''
    material += '\nSTATUS\n'
    material += status.stdout if status.returncode == 0 else ''
    material += '\nUNTRACKED_CONTENT\n'
    material += untracked_file_material(changed_paths(query_paths))
    return hashlib.sha256(material.encode()).hexdigest()


def load_checkpoint() -> tuple[dict | None, str]:
    if not CHECKPOINT_FILE.exists():
        return None, 'missing'
    try:
        data = json.loads(CHECKPOINT_FILE.read_text())
    except Exception:
        return None, 'corrupt'
    return data, 'ok'


def load_scope() -> tuple[list[str], bool]:
    if not SCOPE_FILE.exists():
        return [], False
    try:
        data = json.loads(SCOPE_FILE.read_text())
    except Exception:
        return [], True
    raw_scope = data.get('scope_paths') if isinstance(data, dict) else data
    if not isinstance(raw_scope, list):
        return [], True
    return sorted(set(normalize_path(str(p)) for p in raw_scope if str(p).strip())), True



def active_task_scope() -> list[str]:
    if not TASK_FLOW_FILE.exists():
        return []
    try:
        data = json.loads(TASK_FLOW_FILE.read_text())
    except Exception:
        return []
    scope = data.get('scope_paths') if isinstance(data, dict) else []
    if not isinstance(scope, list):
        return []
    return sorted(set(normalize_path(str(p)) for p in scope if str(p).strip()))


def checkpoint_valid(checkpoint: dict, diff_hash: str, changed: list[str]) -> tuple[bool, str]:
    now = int(time.time())
    if checkpoint.get('task_type') != 'knowledge-asset':
        return False, 'task_type is not knowledge-asset'
    if checkpoint.get('flow_intensity') != 'strict':
        return False, 'flow_intensity is not strict'
    if checkpoint.get('result') != 'pass':
        return False, 'review result is not pass'
    if checkpoint.get('reviewed_diff_hash') != diff_hash:
        return False, 'reviewed diff hash does not match current diff'
    blocking = checkpoint.get('blocking_findings')
    if blocking not in ([], None):
        return False, 'checkpoint contains blocking findings'
    created_at = int(checkpoint.get('created_at') or 0)
    expires_at = int(checkpoint.get('expires_at') or 0)
    if created_at <= 0:
        return False, 'checkpoint missing created_at'
    if expires_at <= now:
        return False, 'checkpoint expired'
    if now - created_at > MAX_AGE:
        return False, 'checkpoint too old'
    review = checkpoint.get('reviewer_role') or ''
    if 'independent' not in review.lower():
        return False, 'reviewer_role is not independent-review'
    reviewer_runtime = str(checkpoint.get('reviewer_runtime') or '').strip()
    main_runtime = str(checkpoint.get('main_runtime') or '').strip()
    if not reviewer_runtime:
        return False, 'reviewer_runtime is empty'
    if not main_runtime:
        return False, 'main_runtime is empty'
    if reviewer_runtime == main_runtime:
        return False, 'reviewer_runtime must differ from main_runtime'
    fields = checkpoint.get('required_plan_fields') or {}
    for key in REQUIRED_PLAN_FIELDS:
        value = fields.get(key)
        if value in (None, '', [], {}):
            return False, f'required_plan_fields.{key} is empty'
    scope_paths = [normalize_path(str(p)) for p in checkpoint.get('scope_paths') or []]
    if not scope_paths:
        return False, 'scope_paths is empty'
    missing_scope = [p for p in changed if not in_scope(p, scope_paths)]
    if missing_scope:
        return False, 'checkpoint scope does not cover changed paths: ' + ', '.join(missing_scope[:8])
    return True, 'ok'


def main() -> int:
    try:
        json.load(sys.stdin)
    except Exception:
        pass
    task_scope = active_task_scope()
    all_changed = changed_paths(task_scope or None)
    if not all_changed:
        return 0
    checkpoint, status = load_checkpoint()
    scope_paths, has_scope_file = load_scope()
    checkpoint_scope = [normalize_path(str(p)) for p in (checkpoint or {}).get('scope_paths') or []]
    if scope_paths and checkpoint_scope and set(scope_paths) != set(checkpoint_scope):
        print('BLOCKED: independent review scope file does not match checkpoint scope.\n'
              f'Runtime: {RUNTIME}\n'
              'Record a fresh independent review checkpoint for the current scope.', flush=True)
        return 2
    if not scope_paths and checkpoint_scope:
        scope_paths = checkpoint_scope
    if not scope_paths:
        print('BLOCKED: long-term workflow assets changed but no strict review scope exists.\n'
              f'Runtime: {RUNTIME}\nChanged candidates: {", ".join(all_changed[:12])}\n'
              'Declare the reviewed scope and record an independent review checkpoint with '
              '.agents/hooks/checkpoint-independent-review.py.', flush=True)
        return 2
    unscoped = [p for p in all_changed if not in_scope(p, scope_paths)]
    if unscoped:
        print('BLOCKED: scoped long-term workflow assets changed outside the independent-review scope.\n'
              f'Runtime: {RUNTIME}\nUnreviewed paths: {", ".join(unscoped[:12])}\n'
              'Expand the reviewed scope and record a fresh independent review checkpoint.', flush=True)
        return 2
    changed = changed_paths(scope_paths)
    if not changed:
        return 0
    diff_hash = current_diff_hash(scope_paths)

    if checkpoint is None:
        print('BLOCKED: long-term workflow assets changed but no independent review checkpoint exists.\n'
              f'Runtime: {RUNTIME}\nChanged paths: {", ".join(changed[:12])}\n'
              'Run an independent review, then record it with .agents/hooks/checkpoint-independent-review.py.', flush=True)
        return 2
    ok, reason = checkpoint_valid(checkpoint, diff_hash, changed)
    if not ok:
        print('BLOCKED: long-term workflow assets changed but independent review checkpoint is invalid.\n'
              f'Reason: {reason}\nRuntime: {RUNTIME}\nChanged paths: {", ".join(changed[:12])}\n'
              'Run an independent review against the current diff and record a fresh checkpoint.', flush=True)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
