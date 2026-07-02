#!/usr/bin/env python3
"""Record a structured independent-review checkpoint for strict knowledge assets."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import subprocess
import time

WORKSPACE = pathlib.Path(os.environ.get('AGENT_WORKSPACE', pathlib.Path(__file__).resolve().parents[2])).resolve()
LONG_TERM_PREFIXES = ('.agents/', 'reference/', 'archive/')
DEFAULT_RUNTIME = os.environ.get('AGENT_RUNTIME', 'codex')


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


def in_scope(path: str, scope_paths: list[str]) -> bool:
    p = normalize_path(path)
    for raw in scope_paths:
        scope = normalize_path(str(raw)).rstrip('/')
        if p == scope or p.startswith(scope + '/'):
            return True
    return False


def changed_paths(scope_paths: list[str] | None = None) -> list[str]:
    query_paths = [normalize_path(str(p)) for p in (scope_paths or ['.agents', 'reference', 'archive'])]
    result = run_git(['-c', 'core.quotePath=false', 'status', '--porcelain=v1', '--', *query_paths])
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


def untracked_file_material(paths: list[str]) -> str:
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


def current_diff_hash(scope_paths: list[str]) -> str:
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Record independent review checkpoint.')
    parser.add_argument('--runtime', default=DEFAULT_RUNTIME, help='Checkpoint runtime directory. Codex Stop hooks read codex by default.')
    parser.add_argument('--main-runtime', default=None, help='Main editing runtime identity. Defaults to --runtime.')
    parser.add_argument('--reviewer-runtime', required=True)
    parser.add_argument('--reviewer-role', default='independent-review')
    parser.add_argument('--result', choices=['pass', 'fail'], required=True)
    parser.add_argument('--blocking-findings', default='[]', help='JSON list of blocking findings')
    parser.add_argument('--similar-assets-scanned', action='append', default=[])
    parser.add_argument('--rules-read', action='append', default=[])
    parser.add_argument('--automation-entrypoints-checked', action='append', default=[])
    parser.add_argument('--source-of-truth', required=True)
    parser.add_argument('--scope', action='append', default=[], help='Reviewed path. Defaults to current long-term asset changes.')
    parser.add_argument('--ttl-seconds', type=int, default=1800)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    runtime = args.runtime or DEFAULT_RUNTIME
    main_runtime = args.main_runtime or runtime
    checkpoint_dir = WORKSPACE / 'workspace/tmp/agent-checkpoints' / runtime
    checkpoint_file = checkpoint_dir / 'independent-review.json'
    scope_file = checkpoint_dir / 'independent-review-scope.json'
    changed = changed_paths()
    scope = sorted(set(normalize_path(p) for p in (args.scope or changed)))
    if not scope:
        print('No long-term asset changes detected; checkpoint not written.')
        return 1
    if normalize_path(args.reviewer_runtime) == normalize_path(main_runtime):
        print('--reviewer-runtime must differ from --main-runtime')
        return 2
    if 'independent' not in (args.reviewer_role or '').lower():
        print('--reviewer-role must contain independent')
        return 2
    scoped_changed = changed_paths(scope)
    if not scoped_changed:
        print('Reviewed scope has no changed long-term assets; checkpoint not written.')
        return 1
    try:
        blocking = json.loads(args.blocking_findings)
        if not isinstance(blocking, list):
            raise ValueError
    except Exception:
        print('--blocking-findings must be a JSON list')
        return 2
    now = int(time.time())
    checkpoint = {
        'flow_intensity': 'strict',
        'task_type': 'knowledge-asset',
        'result': args.result,
        'reviewer_role': args.reviewer_role,
        'reviewer_runtime': args.reviewer_runtime,
        'main_runtime': main_runtime,
        'scope_paths': scope,
        'required_plan_fields': {
            'similar_assets_scanned': args.similar_assets_scanned,
            'rules_read': args.rules_read,
            'automation_entrypoints_checked': args.automation_entrypoints_checked,
            'source_of_truth': args.source_of_truth,
        },
        'reviewed_diff_hash': current_diff_hash(scope),
        'blocking_findings': blocking,
        'created_at': now,
        'expires_at': now + args.ttl_seconds,
    }
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    scope_file.write_text(json.dumps({'scope_paths': scope, 'created_at': now}, ensure_ascii=False, indent=2) + '\n')
    checkpoint_file.write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2) + '\n')
    print(f'✅ independent review checkpoint recorded: {checkpoint_file}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
