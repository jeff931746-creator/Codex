#!/usr/bin/env python3
"""Hard block reference/ writes unless a scoped permission checkpoint exists."""
from __future__ import annotations

from hook_utils import CHECKPOINT_DIR, deny, extract_write_paths, in_scope, is_reference_path, load_payload, now, read_json, rel_to_workspace, resolve_path

MAX_AGE = 1800
CHECKPOINT = CHECKPOINT_DIR / 'reference-permission.json'


def main() -> int:
    payload = load_payload()
    targets = []
    for raw in extract_write_paths(payload):
        path = resolve_path(raw, payload.get('cwd'))
        if is_reference_path(path):
            rel = rel_to_workspace(path)
            if rel:
                targets.append(rel)
    if not targets:
        return 0
    checkpoint = read_json(CHECKPOINT)
    if not checkpoint:
        return deny('BLOCKED: reference/ write requires explicit user permission checkpoint.\nTargets: ' + ', '.join(targets[:12]))
    if checkpoint.get('result') != 'approved':
        return deny('BLOCKED: reference/ permission checkpoint is not approved.')
    if int(checkpoint.get('expires_at') or 0) <= now():
        return deny('BLOCKED: reference/ permission checkpoint expired.')
    scope = checkpoint.get('scope_paths') or []
    missing = [p for p in targets if not in_scope(p, scope)]
    if missing:
        return deny('BLOCKED: reference/ write outside approved scope.\nUnapproved: ' + ', '.join(missing[:12]))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
