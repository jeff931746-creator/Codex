#!/usr/bin/env python3
"""Record Agent evidence and explicit user confirmations for the GDD workflow."""
from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

from hook_utils import WORKSPACE, git_diff_hash, normalize_path, now, write_json, read_json

AGENT_STAGES = ('G1', 'G2', 'G3', 'G4', 'G5', 'C4', 'G6', 'GR')
REQUIRED_USER_CONFIRMATIONS = ('U1', 'U2', 'U3', 'U4', 'U5')
VALID_RESULTS = ('in-progress', 'user-authorized-direction-delivery', 'user-authorized-formal-delivery')


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
    parser = argparse.ArgumentParser(description='Record GDD Agent evidence and user confirmations.')
    parser.add_argument('--doc', required=True)
    parser.add_argument('--doc-id', default='')
    parser.add_argument('--main-agent-id', required=True)
    parser.add_argument('--stage', choices=AGENT_STAGES)
    parser.add_argument('--agent-id', default='')
    parser.add_argument('--agent-role', default='')
    parser.add_argument('--proof-token', default='')
    parser.add_argument('--stage-status', default='completed', choices=['completed'])
    parser.add_argument('--summary', default='')
    parser.add_argument('--user-confirmation-stage', choices=REQUIRED_USER_CONFIRMATIONS)
    parser.add_argument('--confirmed-object', default='', help='Exact planning object or action confirmed by the user.')
    parser.add_argument('--user-message-excerpt', default='', help='Direct quote or faithful excerpt from the user message.')
    parser.add_argument('--confirmation-source', default='user', choices=['user'])
    parser.add_argument('--result', default='in-progress', choices=VALID_RESULTS)
    parser.add_argument('--direction-validation-items', default=None)
    parser.add_argument('--formal-blockers', default=None)
    parser.add_argument('--accepted-risk', default=None, help='Risk explicitly accepted by the user at U5, if any.')
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
    state.setdefault('user_confirmations', {})
    state['updated_at'] = ts
    state['expires_at'] = ts + args.ttl_seconds
    state['result'] = args.result

    if args.result != 'in-progress' and args.user_confirmation_stage != 'U5':
        raise SystemExit('A delivery result requires recording U5 in the same checkpoint call')

    if args.stage:
        required = (args.agent_id.strip(), args.agent_role.strip(), args.summary.strip(), args.proof_token.strip())
        if not all(required):
            raise SystemExit('--agent-id, --agent-role, --summary and --proof-token are required with --stage')
        state['stages'][args.stage] = {
            'agent_id': args.agent_id.strip(),
            'agent_role': args.agent_role.strip(),
            'proof_token': args.proof_token.strip(),
            'status': args.stage_status,
            'summary': args.summary.strip(),
            'target_doc_diff_hash_at_stage': git_diff_hash([target_doc]),
            'recorded_at': ts,
        }

    if args.user_confirmation_stage:
        if not args.confirmed_object.strip() or not args.user_message_excerpt.strip():
            raise SystemExit('--confirmed-object and --user-message-excerpt are required with --user-confirmation-stage')
        state['user_confirmations'][args.user_confirmation_stage] = {
            'status': 'confirmed',
            'source': args.confirmation_source,
            'confirmed_object': args.confirmed_object.strip(),
            'user_message_excerpt': args.user_message_excerpt.strip(),
            'target_artifact_hash': git_diff_hash([target_doc]),
            'recorded_at': ts,
        }

    if args.direction_validation_items is not None:
        state['direction_validation_pending_items'] = split_csv(args.direction_validation_items)
    else:
        state.setdefault('direction_validation_pending_items', [])
    if args.formal_blockers is not None:
        state['formal_gdd_blockers'] = split_csv(args.formal_blockers)
    else:
        state.setdefault('formal_gdd_blockers', [])
    if args.accepted_risk is not None:
        state['accepted_risk'] = args.accepted_risk.strip()
    else:
        state.setdefault('accepted_risk', '')
    state['agent_stages'] = list(AGENT_STAGES)
    state['required_user_confirmations'] = list(REQUIRED_USER_CONFIRMATIONS)
    if args.user_confirmation_stage == 'U5' and args.result != 'in-progress':
        state['target_doc_diff_hash'] = git_diff_hash([target_doc])

    write_json(path, state)
    print(f'✅ gdd workflow checkpoint recorded: {path.relative_to(WORKSPACE)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
