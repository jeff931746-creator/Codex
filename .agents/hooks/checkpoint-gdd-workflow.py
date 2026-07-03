#!/usr/bin/env python3
"""Record evidence for the multi-agent GDD writing workflow."""
from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

from hook_utils import WORKSPACE, git_diff_hash, normalize_path, now, write_json, read_json

REQUIRED_STAGES = ('G1', 'G2', 'G3', 'G4', 'G5', 'G6')
REQUIRED_DECISIONS = ('M1', 'M2', 'M3', 'M4')
VALID_RESULTS = ('in-progress', 'direction-validation-pass', 'formal-gdd-pass')


def doc_id_for(path: str) -> str:
    stem = Path(path).stem.lower()
    slug = re.sub(r'[^a-z0-9._-]+', '-', stem).strip('-')
    digest = hashlib.sha1(path.encode()).hexdigest()[:10]
    return f'{slug or "gdd"}-{digest}'


def state_path(doc_id: str) -> Path:
    return WORKSPACE / 'workspace/tmp/agent-checkpoints/gdd-write' / doc_id / 'workflow-state.json'


def split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(',') if item.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description='Record GDD multi-agent workflow evidence.')
    parser.add_argument('--doc', required=True, help='Target GDD document path, relative to workspace or absolute.')
    parser.add_argument('--doc-id', default='', help='Stable checkpoint id. Defaults to document stem slug.')
    parser.add_argument('--main-agent-id', required=True, help='Main agent/runtime id for distinctness checks.')
    parser.add_argument('--stage', choices=REQUIRED_STAGES, help='Sub-agent stage to record.')
    parser.add_argument('--agent-id', default='', help='Actual spawned sub-agent id for the stage.')
    parser.add_argument('--agent-role', default='', help='Stage role, such as target-breakdown or delivery-acceptance.')
    parser.add_argument('--proof-token', default='', help='Stage-specific token that must appear in the sub-agent transcript output.')
    parser.add_argument('--stage-status', default='completed', choices=['completed', 'pass'])
    parser.add_argument('--summary', default='', help='Short summary of the stage output.')
    parser.add_argument('--decision-stage', choices=REQUIRED_DECISIONS, help='Main-planner decision stage to record.')
    parser.add_argument('--decision', default='', help='Main-planner decision summary.')
    parser.add_argument('--decision-status', default='pass', choices=['pass'])
    parser.add_argument('--result', default='in-progress', choices=VALID_RESULTS)
    parser.add_argument('--direction-validation-items', default='', help='Comma-separated retained direction-validation items.')
    parser.add_argument('--formal-blockers', default='', help='Comma-separated formal GDD blockers.')
    parser.add_argument('--ttl-seconds', type=int, default=86400)
    args = parser.parse_args()

    raw_doc = normalize_path(args.doc)
    doc_path = Path(raw_doc)
    if doc_path.is_absolute():
        target_doc = normalize_path(doc_path.resolve().relative_to(WORKSPACE).as_posix())
    else:
        target_doc = raw_doc
    doc_id = args.doc_id or doc_id_for(target_doc)
    path = state_path(doc_id)
    state = read_json(path) or {}
    ts = now()

    state.setdefault('workflow', 'gdd-write')
    state['target_doc'] = target_doc
    state['doc_id'] = doc_id
    state['main_agent_id'] = args.main_agent_id.strip()
    state.setdefault('stages', {})
    state.setdefault('main_decisions', {})
    state['updated_at'] = ts
    state['expires_at'] = ts + args.ttl_seconds
    state['result'] = args.result

    if args.result != 'in-progress' and args.stage != 'G6':
        raise SystemExit('direction-validation-pass/formal-gdd-pass requires recording --stage G6 in the same checkpoint call')

    if args.stage:
        if not args.agent_id.strip():
            raise SystemExit('--agent-id is required when --stage is provided')
        if not args.agent_role.strip():
            raise SystemExit('--agent-role is required when --stage is provided')
        if not args.summary.strip():
            raise SystemExit('--summary is required when --stage is provided')
        if not args.proof_token.strip():
            raise SystemExit('--proof-token is required when --stage is provided')
        state['stages'][args.stage] = {
            'agent_id': args.agent_id.strip(),
            'agent_role': args.agent_role.strip(),
            'proof_token': args.proof_token.strip(),
            'status': args.stage_status,
            'summary': args.summary.strip(),
            'target_doc_diff_hash_at_stage': git_diff_hash([target_doc]),
            'recorded_at': ts,
        }

    if args.decision_stage:
        if not args.decision.strip():
            raise SystemExit('--decision is required when --decision-stage is provided')
        state['main_decisions'][args.decision_stage] = {
            'status': args.decision_status,
            'decision': args.decision.strip(),
            'recorded_at': ts,
        }

    state['direction_validation_pending_items'] = split_csv(args.direction_validation_items)
    state['formal_gdd_blockers'] = split_csv(args.formal_blockers)
    state['required_stages'] = list(REQUIRED_STAGES)
    state['required_main_decisions'] = list(REQUIRED_DECISIONS)
    if args.stage == 'G6' and args.result != 'in-progress':
        state['target_doc_diff_hash'] = git_diff_hash([target_doc])

    write_json(path, state)
    print(f'✅ gdd workflow checkpoint recorded: {path.relative_to(WORKSPACE)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
