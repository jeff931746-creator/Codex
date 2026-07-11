#!/usr/bin/env python3
"""Hard block content/governance work that lacks required standards, approvals, or reviewer checkpoints."""
from __future__ import annotations

import re

from hook_utils import WORKSPACE, checkpoint_path, deny, git_diff_hash, in_scope, load_payload, now, read_json, scoped_project_changed_paths

DOC_EXTENSIONS = ('.md', '.txt', '.docx')
SCAFFOLD_TEXT_EXTENSIONS = ('.md', '.txt')
DESIGN_WORDS = ('GDD', 'gdd', '设计', '方案', '功能', '玩法', '系统', '活动', '经济', '商业化', '数值', '机制')
MECHANISM_PATHS = ('archive/资料/机制库/', 'reference/部门标准/策划/机制拆解/', 'archive/skills/skills/游戏机制拆解/')
CAPABILITY_PATHS = ('reference/部门标准/', 'archive/skills/skills/', 'archive/方法论/', 'archive/资料/')
PROMOTION_PATHS = ('archive/', 'reference/')
AGENT_PATHS = ('.agents/',)
ANALYSIS_SCAFFOLD_STANDARD_PATH = 'reference/部门标准/策划/机制拆解/拆解质量标准.md'
DELIVERY_WRITING_STANDARD_PATH = 'reference/部门标准/通用/交付型文档写作标准.md'
SCAFFOLD_EXACT_MARKER = 'analysis-scaffold:exact-labels'
SCAFFOLD_SUFFIX_MARKER = 'analysis-scaffold:label-suffixes'
DELIVERY_TRIGGER_MARKER = 'delivery-writing:trigger-terms'
DELIVERY_ALLOW_REASON_MARKER = 'delivery-writing:allow-reasons'
DELIVERY_EXEMPT_FRAGMENT_MARKER = 'delivery-writing:exempt-path-fragments'
SCAFFOLD_HEADING_RE = re.compile(r'^(#{1,6})\s*(.+?)\s*$')
SCAFFOLD_BOLD_LABEL_RE = re.compile(r'^\s*\*\*(.+?)\*\*\s*[:：]?\s*$')
SCAFFOLD_LIST_LABEL_RE = re.compile(r'^\s*(?:[-*]|\d+[.)．、])\s*([^，。；;,.、]{2,12})\s*[:：]\s*')
SCAFFOLD_PLAIN_LABEL_RE = re.compile(r'^\s*([^，。；;,.、：:]{2,12})\s*[:：]\s*')
NUMBERED_SECTION_RE = re.compile(r'^([一二三四五六七八九十]+|\d+(?:\.\d+)*)[、.．]\s*')
DELIVERY_ALLOW_RE = re.compile(r'<!--\s*delivery-writing:allow-example\s+reason="([^"]+)"\s*-->')
DELIVERY_ALLOW_LINE_RE = re.compile(r'^\s*<!--\s*delivery-writing:allow-example\s+reason="([^"]+)"\s*-->\s*$')


def marker_values(text: str, marker: str) -> list[str]:
    start = f'<!-- {marker}:start -->'
    end = f'<!-- {marker}:end -->'
    if start not in text or end not in text:
        return []
    block = text.split(start, 1)[1].split(end, 1)[0]
    values: list[str] = []
    for line in block.splitlines():
        values.extend(re.findall(r'`([^`]+)`', line))
    return values


def load_scaffold_standard() -> tuple[set[str], tuple[str, ...], list[str]]:
    standard_path = WORKSPACE / ANALYSIS_SCAFFOLD_STANDARD_PATH
    try:
        text = standard_path.read_text()
    except Exception as exc:
        return set(), (), [f'analysis-scaffold standard unreadable: {ANALYSIS_SCAFFOLD_STANDARD_PATH}: {exc}']

    exact = set(marker_values(text, SCAFFOLD_EXACT_MARKER))
    suffixes = tuple(marker_values(text, SCAFFOLD_SUFFIX_MARKER))
    errors: list[str] = []
    if not exact:
        errors.append(f'analysis-scaffold exact labels missing in {ANALYSIS_SCAFFOLD_STANDARD_PATH}')
    if not suffixes:
        errors.append(f'analysis-scaffold label suffixes missing in {ANALYSIS_SCAFFOLD_STANDARD_PATH}')
    return exact, suffixes, errors


def load_delivery_writing_standard() -> tuple[tuple[str, ...], set[str], tuple[str, ...], list[str]]:
    standard_path = WORKSPACE / DELIVERY_WRITING_STANDARD_PATH
    try:
        text = standard_path.read_text()
    except Exception as exc:
        return (), set(), (), [f'delivery-writing standard unreadable: {DELIVERY_WRITING_STANDARD_PATH}: {exc}']

    triggers = tuple(marker_values(text, DELIVERY_TRIGGER_MARKER))
    allow_reasons = set(marker_values(text, DELIVERY_ALLOW_REASON_MARKER))
    exempt_fragments = tuple(marker_values(text, DELIVERY_EXEMPT_FRAGMENT_MARKER))
    errors: list[str] = []
    if not triggers:
        errors.append(f'delivery-writing trigger terms missing in {DELIVERY_WRITING_STANDARD_PATH}')
    if not allow_reasons:
        errors.append(f'delivery-writing allow reasons missing in {DELIVERY_WRITING_STANDARD_PATH}')
    if not exempt_fragments:
        errors.append(f'delivery-writing exempt path fragments missing in {DELIVERY_WRITING_STANDARD_PATH}')
    return triggers, allow_reasons, exempt_fragments, errors


def is_doc(path: str) -> bool:
    return path.endswith(DOC_EXTENSIONS)


def is_agent_internal(path: str) -> bool:
    return path == '.agents' or path.startswith(AGENT_PATHS)


def requires_standard_read(path: str) -> bool:
    if is_agent_internal(path):
        return False
    return is_doc(path) and (path.startswith('workspace/projects/') or path.startswith('archive/') or path.startswith('reference/'))


def requires_design_review(path: str) -> bool:
    if is_agent_internal(path) or not is_doc(path):
        return False
    return any(word in path for word in DESIGN_WORDS)


def requires_capability_check(path: str) -> bool:
    if is_agent_internal(path):
        return False
    return any(path == prefix.rstrip('/') or path.startswith(prefix) for prefix in CAPABILITY_PATHS)


def requires_promotion_approval(path: str) -> bool:
    if is_agent_internal(path):
        return False
    return any(path == prefix.rstrip('/') or path.startswith(prefix) for prefix in PROMOTION_PATHS)


def requires_semantic_review(path: str) -> bool:
    if is_agent_internal(path):
        return False
    return any(path.startswith(prefix) for prefix in MECHANISM_PATHS) or requires_design_review(path)


def requires_scaffold_check(path: str) -> bool:
    if path == ANALYSIS_SCAFFOLD_STANDARD_PATH:
        return False
    if is_agent_internal(path) or not path.endswith(SCAFFOLD_TEXT_EXTENSIONS):
        return False
    return path.startswith('workspace/projects/') or path.startswith('archive/') or path.startswith('reference/')


def requires_delivery_writing_check(path: str) -> bool:
    if path == DELIVERY_WRITING_STANDARD_PATH:
        return False
    if is_agent_internal(path) or not path.endswith(SCAFFOLD_TEXT_EXTENSIONS):
        return False
    if requires_design_review(path):
        return False
    return path.startswith('workspace/projects/') or path.startswith('archive/') or path.startswith('reference/')


def delivery_path_exempt(path: str, exempt_fragments: tuple[str, ...]) -> bool:
    normalized = '/' + path.strip('/')
    return any(fragment and fragment in normalized for fragment in exempt_fragments)


def strip_html_comments(line: str, in_comment: bool) -> tuple[str, bool]:
    rest = line
    visible = ''
    while rest:
        if in_comment:
            end = rest.find('-->')
            if end < 0:
                return visible, True
            rest = rest[end + 3:]
            in_comment = False
        start = rest.find('<!--')
        if start < 0:
            visible += rest
            return visible, False
        visible += rest[:start]
        rest = rest[start + 4:]
        end = rest.find('-->')
        if end < 0:
            return visible, True
        rest = rest[end + 3:]
    return visible, in_comment


def delivery_term_in_line(term: str, line: str) -> bool:
    if term.isascii():
        return re.search(rf'\b{re.escape(term)}s?\b', line, re.IGNORECASE) is not None
    return term in line


def delivery_allowed_lines(text: str, allow_reasons: set[str]) -> tuple[set[int], list[str]]:
    allowed: set[int] = set()
    invalid_markers: list[str] = []
    pending_allow = False
    in_code_block = False
    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith('```') or stripped.startswith('~~~'):
            pending_allow = False
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        allow_match = DELIVERY_ALLOW_LINE_RE.match(line)
        if allow_match:
            reason = allow_match.group(1).strip()
            if reason not in allow_reasons:
                invalid_markers.append(f'line {lineno}: invalid reason "{reason}"')
            else:
                pending_allow = True
            continue
        if DELIVERY_ALLOW_RE.search(line):
            invalid_markers.append(f'line {lineno}: allow marker must be on its own line')
            continue
        if not stripped or stripped.startswith('<!--'):
            continue
        if pending_allow:
            allowed.add(lineno)
            pending_allow = False
    return allowed, invalid_markers


def delivery_writing_findings_in_text(path: str, text: str, trigger_terms: tuple[str, ...], allow_reasons: set[str], exempt_fragments: tuple[str, ...]) -> list[str]:
    if delivery_path_exempt(path, exempt_fragments):
        return []

    allowed_lines, invalid_reasons = delivery_allowed_lines(text, allow_reasons)
    invalid_reasons = sorted(set(invalid_reasons))
    if invalid_reasons:
        return [f'{path}: invalid delivery-writing allow marker ({invalid_reasons[0]})']

    findings: list[str] = []
    in_code_block = False
    in_html_comment = False
    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith('```') or stripped.startswith('~~~'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        visible, in_html_comment = strip_html_comments(line, in_html_comment)
        if lineno in allowed_lines:
            continue
        if not visible.strip():
            continue
        for term in trigger_terms:
            if delivery_term_in_line(term, visible):
                findings.append(f'{path}:{lineno} uses delivery-writing trigger "{term}"')
                break
    return findings


def delivery_writing_findings(path: str, trigger_terms: tuple[str, ...], allow_reasons: set[str], exempt_fragments: tuple[str, ...]) -> list[str]:
    full_path = WORKSPACE / path
    try:
        text = full_path.read_text()
    except UnicodeDecodeError:
        try:
            text = full_path.read_text(encoding='utf-8')
        except Exception:
            return []
    except Exception:
        return []
    return delivery_writing_findings_in_text(path, text, trigger_terms, allow_reasons, exempt_fragments)


def scaffold_label_problem(label: str, exact_labels: set[str], label_suffixes: tuple[str, ...], allow_suffix: bool = True) -> bool:
    value = label.strip().strip(':：')
    if value in exact_labels:
        return True
    if allow_suffix and 2 <= len(value) <= 12 and value.endswith(label_suffixes):
        return True
    return False


def scaffold_findings(path: str, exact_labels: set[str], label_suffixes: tuple[str, ...]) -> list[str]:
    full_path = WORKSPACE / path
    try:
        text = full_path.read_text()
    except UnicodeDecodeError:
        try:
            text = full_path.read_text(encoding='utf-8')
        except Exception:
            return []
    except Exception:
        return []

    findings: list[str] = []
    in_code_block = False
    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith('```') or stripped.startswith('~~~'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        heading = SCAFFOLD_HEADING_RE.match(line)
        if heading:
            heading_label = heading.group(2).strip()
            # Numbered document sections like '九、当前风险' are allowed; unnumbered
            # short dimension headings such as '承接风险' remain blocked.
            allow_suffix = NUMBERED_SECTION_RE.match(heading_label) is None
            if scaffold_label_problem(heading_label, exact_labels, label_suffixes, allow_suffix=allow_suffix):
                findings.append(f'{path}:{lineno} uses analysis scaffold heading "{heading_label}"')
                continue

        bold = SCAFFOLD_BOLD_LABEL_RE.match(line)
        if bold and scaffold_label_problem(bold.group(1), exact_labels, label_suffixes):
            findings.append(f'{path}:{lineno} uses analysis scaffold label "{bold.group(1).strip()}"')
            continue

        list_label = SCAFFOLD_LIST_LABEL_RE.match(line)
        if list_label and scaffold_label_problem(list_label.group(1), exact_labels, label_suffixes):
            findings.append(f'{path}:{lineno} uses analysis scaffold list label "{list_label.group(1).strip()}"')
            continue

        plain_label = SCAFFOLD_PLAIN_LABEL_RE.match(line)
        if plain_label and scaffold_label_problem(plain_label.group(1), exact_labels, label_suffixes):
            findings.append(f'{path}:{lineno} uses analysis scaffold plain label "{plain_label.group(1).strip()}"')
            continue

    return findings


def checkpoint_scope_ok(data: dict, changed: list[str]) -> bool:
    scope = data.get('scope_paths') or []
    return bool(scope) and all(in_scope(path, scope) for path in changed)


def checkpoint_time_ok(data: dict) -> bool:
    return int(data.get('expires_at') or 0) > now()


def require_checkpoint(name: str, changed: list[str], result: str = 'pass', hash_required: bool = False, independent: bool = False) -> str | None:
    data = read_json(checkpoint_path(name))
    if not data:
        return f'{name} missing'
    if data.get('result') != result:
        return f'{name} result is not {result}'
    if not checkpoint_time_ok(data):
        return f'{name} expired'
    if not checkpoint_scope_ok(data, changed):
        return f'{name} scope does not cover changed paths'
    if independent and data.get('reviewer_runtime') == data.get('main_runtime'):
        return f'{name} reviewer_runtime must differ from main_runtime'
    if data.get('blocking_findings') not in ([], None):
        return f'{name} contains blocking findings'
    if hash_required and data.get('reviewed_diff_hash') != git_diff_hash(data.get('scope_paths') or []):
        return f'{name} diff hash does not match current scoped diff'
    return None


def main() -> int:
    load_payload()
    changed = scoped_project_changed_paths(['.'])
    if not changed:
        return 0

    failures: list[str] = []
    standard = [p for p in changed if requires_standard_read(p)]
    design = [p for p in changed if requires_design_review(p)]
    capability = [p for p in changed if requires_capability_check(p)]
    promotion = [p for p in changed if requires_promotion_approval(p)]
    semantic = [p for p in changed if requires_semantic_review(p)]
    scaffold = [p for p in changed if requires_scaffold_check(p)]
    delivery = [p for p in changed if requires_delivery_writing_check(p)]

    if standard:
        reason = require_checkpoint('standard-read.json', standard)
        if reason:
            failures.append('standard-read: ' + reason)
    if design:
        reason = require_checkpoint('design-review.json', design, hash_required=True, independent=True)
        if reason:
            failures.append('design-review: ' + reason)
    if capability:
        reason = require_checkpoint('capability-check.json', capability)
        if reason:
            failures.append('capability-check: ' + reason)
    if promotion:
        reason = require_checkpoint('promotion-approval.json', promotion, result='approved')
        if reason:
            failures.append('promotion-approval: ' + reason)
    if semantic:
        reason = require_checkpoint('semantic-review.json', semantic, hash_required=True, independent=True)
        if reason:
            failures.append('semantic-review: ' + reason)
    if scaffold:
        exact_labels, label_suffixes, scaffold_standard_errors = load_scaffold_standard()
        if scaffold_standard_errors:
            failures.extend(scaffold_standard_errors)
        else:
            scaffold_problems: list[str] = []
            for path in scaffold:
                scaffold_problems.extend(scaffold_findings(path, exact_labels, label_suffixes))
            if scaffold_problems:
                failures.append(
                    'analysis-scaffold: deliverable text violates '
                    f'{ANALYSIS_SCAFFOLD_STANDARD_PATH}. '
                    'Rewrite internal analysis scaffold labels as natural conclusion + logic paragraphs. '
                    + ' | '.join(scaffold_problems[:8])
                )
    if delivery:
        trigger_terms, allow_reasons, exempt_fragments, delivery_standard_errors = load_delivery_writing_standard()
        if delivery_standard_errors:
            failures.extend(delivery_standard_errors)
        else:
            delivery_problems: list[str] = []
            for path in delivery:
                delivery_problems.extend(delivery_writing_findings(path, trigger_terms, allow_reasons, exempt_fragments))
            if delivery_problems:
                failures.append(
                    'delivery-writing: deliverable text violates '
                    f'{DELIVERY_WRITING_STANDARD_PATH}. '
                    'Rewrite example-like content as conclusion, mechanism, boundary, or flow; '
                    'or add a valid hidden allow marker when the example is required for execution disambiguation. '
                    + ' | '.join(delivery_problems[:8])
                )

    if failures:
        return deny('BLOCKED: content governance checkpoints missing or invalid.\n' + '\n'.join(failures[:12]))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
