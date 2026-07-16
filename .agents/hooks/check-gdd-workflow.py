#!/usr/bin/env python3
"""Block GDD delivery when Agent evidence or explicit user confirmations are missing."""
from __future__ import annotations

import json
import time
import re
from pathlib import Path

from hook_utils import WORKSPACE, RUNTIME, deny, git_diff_hash, load_payload, project_changed_paths, read_json

CHECKPOINT_ROOT = WORKSPACE / 'workspace/tmp/agent-checkpoints/gdd-write'
REQUIRED_COMMON_STAGES = ('G1', 'G2', 'G3', 'G4', 'G5', 'C4', 'G6')
REQUIRED_USER_CONFIRMATIONS = ('U1', 'U2', 'U3', 'U4', 'U5')
ACCEPTED_RESULTS = {'user-authorized-direction-delivery', 'user-authorized-formal-delivery'}
AGENT_ID_PATTERN = re.compile(r'^[0-9a-fA-F]{8,}-[0-9a-fA-F-]{12,}$')
def is_changed_design_doc(path: str) -> bool:
    p = path.replace('\\', '/')
    if not p.startswith('workspace/projects/'):
        return False
    if not p.endswith('.md'):
        return False
    name = Path(p).name
    if name == 'README.md':
        return False
    return True


def changed_project_markdown_paths() -> list[str]:
    found: set[str] = set()
    for rel in project_changed_paths(['workspace/projects']):
        root = WORKSPACE / rel
        if root.is_dir():
            for path in root.rglob('*.md'):
                try:
                    found.add(path.relative_to(WORKSPACE).as_posix())
                except Exception:
                    continue
        else:
            found.add(rel)
    return sorted(found)


def workflow_states() -> list[dict]:
    if not CHECKPOINT_ROOT.exists():
        return []
    states: list[dict] = []
    for path in sorted(CHECKPOINT_ROOT.glob('*/workflow-state.json')):
        data = read_json(path)
        if isinstance(data, dict):
            data['_checkpoint_path'] = path.relative_to(WORKSPACE).as_posix()
            states.append(data)
    return states


def collect_observed_agent_ids(payload: object) -> set[str]:
    found: set[str] = set()
    stack = [payload]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            for key, value in item.items():
                if key in {'agent_id', 'agentId', 'agent_path', 'agentPath'} and isinstance(value, str):
                    if AGENT_ID_PATTERN.match(value.strip()):
                        found.add(value.strip())
                elif isinstance(value, (dict, list)):
                    stack.append(value)
        elif isinstance(item, list):
            stack.extend(value for value in item if isinstance(value, (dict, list)))
    return found


def collect_agent_evidence_texts(payload: object) -> list[str]:
    texts: list[str] = []
    stack = [payload]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            name = str(item.get('toolName') or item.get('tool_name') or item.get('recipient_name') or item.get('name') or '')
            material = json.dumps(item, ensure_ascii=False, sort_keys=True)
            if (
                'multi_agent' in name
                or 'spawn_agent' in name
                or 'wait_agent' in name
                or 'send_input' in name
                or 'subagent' in material.lower()
                or 'agent_id' in item
                or 'agent_path' in item
            ):
                texts.append(material)
            for value in item.values():
                if isinstance(value, (dict, list)):
                    stack.append(value)
        elif isinstance(item, list):
            stack.extend(value for value in item if isinstance(value, (dict, list)))
    return texts


def collect_user_evidence_texts(payload: object) -> list[str]:
    texts: list[str] = []
    stack = [payload]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            role = str(item.get('role') or item.get('author_role') or item.get('authorRole') or '').lower()
            item_type = str(item.get('type') or item.get('message_type') or '').lower()
            if role == 'user' or item_type in {'user_message', 'user-message'}:
                texts.append(json.dumps(item, ensure_ascii=False, sort_keys=True))
            for value in item.values():
                if isinstance(value, (dict, list)):
                    stack.append(value)
        elif isinstance(item, list):
            stack.extend(value for value in item if isinstance(value, (dict, list)))
    return texts


def has_stage_evidence(agent_id: str, proof_token: str, evidence_texts: list[str]) -> bool:
    return any(agent_id in text and proof_token in text for text in evidence_texts)


def matching_states(target_doc: str, states: list[dict]) -> list[dict]:
    matches: list[dict] = []
    for state in states:
        if state.get('target_doc') == target_doc:
            matches.append(state)
    return matches


def validate_state(
    target_doc: str,
    state: dict,
    observed_agent_ids: set[str],
    evidence_texts: list[str],
    user_evidence_texts: list[str],
) -> tuple[bool, str]:
    now = int(time.time())
    if state.get('workflow') != 'gdd-write':
        return False, 'workflow is not gdd-write'
    if state.get('result') not in ACCEPTED_RESULTS:
        return False, 'result is not a user-authorized delivery state'
    if state.get('formal_gdd_blockers') not in ([], None) and not str(state.get('accepted_risk') or '').strip():
        return False, 'unclosed formal_gdd_blockers require explicit U5 accepted_risk text'
    if int(state.get('expires_at') or 0) <= now:
        return False, 'checkpoint expired'
    main_agent_id = str(state.get('main_agent_id') or '').strip()
    if not main_agent_id:
        return False, 'main_agent_id missing'
    stages = state.get('stages') or {}
    seen_agent_ids: set[str] = set()
    required_stages = list(REQUIRED_COMMON_STAGES)
    if state.get('result') == 'user-authorized-formal-delivery':
        required_stages.append('GR')
    for stage in required_stages:
        item = stages.get(stage) or {}
        if item.get('status') != 'completed':
            return False, f'{stage} status missing or not completed'
        agent_id = str(item.get('agent_id') or '').strip()
        if not agent_id:
            return False, f'{stage} agent_id missing'
        if not AGENT_ID_PATTERN.match(agent_id):
            return False, f'{stage} agent_id does not look like a spawned sub-agent id'
        if agent_id not in observed_agent_ids:
            return False, f'{stage} agent_id was not observed in this runtime transcript'
        if agent_id in {RUNTIME, main_agent_id}:
            return False, f'{stage} agent_id must not equal main runtime/main_agent_id'
        if agent_id in seen_agent_ids:
            return False, f'{stage} agent_id duplicates another stage'
        seen_agent_ids.add(agent_id)
        proof_token = str(item.get('proof_token') or '').strip()
        if not proof_token:
            return False, f'{stage} proof_token missing'
        if not has_stage_evidence(agent_id, proof_token, evidence_texts):
            return False, f'{stage} proof_token was not observed with its agent_id in this runtime transcript'
        if not str(item.get('agent_role') or '').strip():
            return False, f'{stage} agent_role missing'
        if not str(item.get('summary') or '').strip():
            return False, f'{stage} summary missing'
    confirmations = state.get('user_confirmations') or {}
    for stage in REQUIRED_USER_CONFIRMATIONS:
        item = confirmations.get(stage) or {}
        if item.get('status') != 'confirmed':
            return False, f'{stage} user confirmation missing or not confirmed'
        if item.get('source') != 'user':
            return False, f'{stage} confirmation source must be user'
        if not str(item.get('confirmed_object') or '').strip():
            return False, f'{stage} confirmed_object missing'
        if not str(item.get('user_message_excerpt') or '').strip():
            return False, f'{stage} user_message_excerpt missing'
        excerpt = str(item.get('user_message_excerpt') or '').strip()
        if not any(excerpt in text for text in user_evidence_texts):
            return False, f'{stage} user_message_excerpt was not observed in a user-authored runtime message'
        if int(item.get('recorded_at') or 0) <= 0:
            return False, f'{stage} recorded_at missing'
    for stage in ('U4', 'U5'):
        if confirmations[stage].get('target_artifact_hash') != git_diff_hash([target_doc]):
            return False, f'{stage} confirmation is stale for current document diff'
    for stage in ('C4',):
        if stages[stage].get('target_doc_diff_hash_at_stage') != git_diff_hash([target_doc]):
            return False, f'{stage} evidence is stale for current document diff'
    if state.get('result') == 'user-authorized-formal-delivery':
        if stages['GR'].get('target_doc_diff_hash_at_stage') != git_diff_hash([target_doc]):
            return False, 'GR evidence is stale for current document diff'
    g6 = stages.get('G6') or {}
    if g6.get('target_doc_diff_hash_at_stage') != git_diff_hash([target_doc]):
        return False, 'G6 evidence is stale for current document diff'
    if state.get('target_doc_diff_hash') != git_diff_hash([target_doc]):
        return False, 'target_doc_diff_hash does not match current document diff'
    return True, 'ok'


def main() -> int:
    payload = load_payload()
    changed = [p for p in changed_project_markdown_paths() if is_changed_design_doc(p)]
    if not changed:
        return 0
    observed_agent_ids = collect_observed_agent_ids(payload)
    evidence_texts = collect_agent_evidence_texts(payload)
    user_evidence_texts = collect_user_evidence_texts(payload)
    states = workflow_states()
    failures: list[str] = []
    for doc in changed:
        candidates = matching_states(doc, states)
        if not candidates:
            failures.append(f'{doc}: missing workflow-state.json')
            continue
        reasons: list[str] = []
        for state in candidates:
            ok, reason = validate_state(doc, state, observed_agent_ids, evidence_texts, user_evidence_texts)
            if ok:
                break
            reasons.append(f'{reason} ({state.get("_checkpoint_path", "unknown checkpoint")})')
        else:
            failures.append(f'{doc}: ' + '; '.join(reasons[:3]))
    if failures:
        return deny(
            'BLOCKED: changed design documents require real Agent evidence and explicit user confirmations.\n'
            + '\n'.join(f'- {item}' for item in failures[:12])
            + '\nRecord G1/G2/G3/G4/G5/C4/G6 after actual Agent runs, add GR for formal delivery, and record U1-U5 only from explicit user messages; Agent-generated decisions are invalid.'
        )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
