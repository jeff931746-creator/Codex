#!/usr/bin/env python3
"""
运行 测试_001 的盲归类(65 条样本)。

调用约定:
  - 严格遵守 .claude/rules/api-client-architecture.md
  - 通过 archive.tools.lib.llm_client 调用,不直接 import deepseek_client
  - LLM_PROVIDER 由调用方环境提供,默认期望 deepseek + deepseek-v4-pro

启动示例:
  set -a
  source "$HOME/Library/Application Support/FeishuCodexBridge/bridge/.env"
  set +a
  export LLM_PROVIDER=deepseek
  export DEEPSEEK_MODEL=deepseek-v4-pro
  python3 archive/tools/scripts/run_theme_motif_classification.py

产物:
  03-results/<group>__<index>__<theme>.json
  03-results/_failures.json
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path("/Users/mt/Documents/Codex")
sys.path.insert(0, str(ROOT))

from archive.tools.lib.llm_client import chat_text  # noqa: E402
from archive.tools.lib.llm_common import RetryPolicy  # noqa: E402

TEST_DIR = ROOT / "archive/资料/买量组合库/题材库/测试/测试_001"
PROMPTS_DIR = TEST_DIR / "01-prompts"
SAMPLES_DIR = TEST_DIR / "02-samples"
RESULTS_DIR = TEST_DIR / "03-results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

CANDIDATE_LIBRARY_PATH = ROOT / "archive/资料/买量组合库/题材库/_draft/母题材候选库_v0.2.1.md"

VALID_PRIMARY_MOTIFS = {
    "绝境守存", "撤离夺宝", "异种进化", "巨物驯御", "废械拼强",
    "禁忌探索", "镇邪收容", "改命逆袭", "暴富翻身", "权争上位",
    "领地开拓", "异能爆发", "未归类",
}
VALID_UNASSIGNED_REASONS = {
    "", "no_matching_psych_task", "conflict_structure_not_covered",
    "only_observer_tag_matched", "insufficient_information",
}
VALID_TEST_RESULTS = {"pass", "ambiguous", "unassigned", "fail"}
VALID_OBSERVER_TAGS = {"群体压境", "高压渗透", "观众反馈", "专家身份"}

REQUIRED_FIELDS = [
    "raw_theme", "culture_shell", "action_cut", "feedback_channel",
    "threat_pattern", "primary_psych_task", "emotion_promise",
    "conflict_structure", "user_role_position", "strongest_carrier_relation",
    "monetization_fit", "commercial_failure_cases", "primary_motif",
    "unassigned_reason", "secondary_cut_cluster", "observer_tags",
    "boundary_notes", "test_result",
]


def load_system_prompt() -> str:
    template = (PROMPTS_DIR / "system.md").read_text(encoding="utf-8")
    candidate = CANDIDATE_LIBRARY_PATH.read_text(encoding="utf-8")
    return template.replace("【__CANDIDATE_LIBRARY__】", candidate)


def load_user_template() -> str:
    return (PROMPTS_DIR / "user_template.md").read_text(encoding="utf-8")


def build_user_prompt(template: str, sample: dict) -> str:
    return (template
            .replace("__RAW_THEME__", sample.get("raw_theme", ""))
            .replace("__QUADRANT__", sample.get("quadrant", ""))
            .replace("__ACQUISITION_SCORE__", sample.get("acquisition_score", ""))
            .replace("__ROI_SCORE__", sample.get("roi_score", ""))
            .replace("__PLAYSTYLE_HINT__", sample.get("playstyle_hint", ""))
            .replace("__MATERIAL_HOOKS__", sample.get("material_hooks", ""))
            .replace("__REVIEW_NOTES__", sample.get("review_notes", ""))
            .replace("__SOURCE__", sample.get("source", "")))


def strip_code_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n", "", text)
        text = re.sub(r"\n```$", "", text)
    return text.strip()


def validate(record: dict) -> list[str]:
    errors = []
    for field in REQUIRED_FIELDS:
        if field not in record:
            errors.append(f"missing field: {field}")
    if record.get("primary_motif") not in VALID_PRIMARY_MOTIFS:
        errors.append(f"invalid primary_motif: {record.get('primary_motif')!r}")
    if record.get("unassigned_reason", "") not in VALID_UNASSIGNED_REASONS:
        errors.append(f"invalid unassigned_reason: {record.get('unassigned_reason')!r}")
    if record.get("test_result") not in VALID_TEST_RESULTS:
        errors.append(f"invalid test_result: {record.get('test_result')!r}")
    if record.get("primary_motif") == "未归类" and not record.get("unassigned_reason"):
        errors.append("primary_motif=未归类 but unassigned_reason 为空")
    if record.get("primary_motif") != "未归类" and record.get("unassigned_reason"):
        errors.append("primary_motif 非未归类 但 unassigned_reason 非空")
    if not isinstance(record.get("commercial_failure_cases", []), list) or len(record.get("commercial_failure_cases", [])) < 2:
        errors.append("commercial_failure_cases 必须至少 2 项")
    for tag in record.get("observer_tags", []) or []:
        if tag not in VALID_OBSERVER_TAGS:
            errors.append(f"observer_tags 含非法值: {tag}")
    return errors


def classify_one(sample: dict, system_prompt: str, user_template: str) -> tuple[dict | None, list[str], str]:
    user = build_user_prompt(user_template, sample)
    raw = chat_text(
        user,
        system=system_prompt,
        max_tokens=2500,
        temperature=0.1,
        timeout=180,
        retry_policy=RetryPolicy(retries=2, base_delay=3.0),
    )
    text = strip_code_fence(raw)
    try:
        record = json.loads(text)
    except json.JSONDecodeError as e:
        return None, [f"json decode failed: {e}", "raw:" + text[:500]], raw
    errors = validate(record)
    return record, errors, raw


def file_safe(name: str) -> str:
    return re.sub(r"[^\w一-龥]", "_", name)[:40]


def main():
    provider = os.environ.get("LLM_PROVIDER", "").strip().lower()
    if provider not in {"deepseek", "siliconflow"}:
        print(f"[FATAL] LLM_PROVIDER 必须是 deepseek 或 siliconflow,当前 {provider!r}")
        sys.exit(2)
    print(f"[info] LLM_PROVIDER={provider}")
    print(f"[info] DEEPSEEK_MODEL={os.environ.get('DEEPSEEK_MODEL', '(default)')}")

    system_prompt = load_system_prompt()
    user_template = load_user_template()

    samples = []
    for fname in ("positive_36.json", "boundary_17.json", "blind_12.json"):
        # try multiple possible naming
        for cand in (fname, fname.replace("36", "30"), fname.replace("17", "18")):
            path = SAMPLES_DIR / cand
            if path.exists():
                samples.extend(json.loads(path.read_text(encoding="utf-8")))
                print(f"[info] 加载 {cand}: {len(json.loads(path.read_text(encoding='utf-8')))} 条")
                break
    if not samples:
        # fallback by glob
        for p in sorted(SAMPLES_DIR.glob("*.json")):
            data = json.loads(p.read_text(encoding="utf-8"))
            samples.extend(data)
            print(f"[info] 加载 {p.name}: {len(data)} 条")
    print(f"[info] 共 {len(samples)} 条样本")

    failures = []
    t0 = time.time()
    for i, sample in enumerate(samples, 1):
        theme = sample["raw_theme"]
        group = sample["sample_group"]
        idx = sample["table_index"]
        out_path = RESULTS_DIR / f"{group}__{idx:03d}__{file_safe(theme)}.json"
        if out_path.exists():
            print(f"[skip] {i}/{len(samples)} {theme}(已存在)")
            continue
        try:
            print(f"[run] {i}/{len(samples)} {group} | {theme}", flush=True)
            record, errors, raw = classify_one(sample, system_prompt, user_template)
            if errors:
                failures.append({
                    "sample": sample, "errors": errors,
                    "record": record, "raw_excerpt": raw[:1000],
                })
                print(f"  [WARN] 校验失败: {errors[:2]}")
            payload = {
                "sample_meta": {
                    "sample_group": group, "table_index": idx,
                    "raw_theme": theme, "quadrant": sample.get("quadrant"),
                },
                "classification": record,
                "validation_errors": errors,
            }
            out_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        except Exception as e:
            failures.append({"sample": sample, "exception": str(e)})
            print(f"  [ERROR] 异常: {e}", flush=True)
        if i % 5 == 0:
            elapsed = time.time() - t0
            print(f"  ... 进度 {i}/{len(samples)} 用时 {elapsed:.1f}s")

    if failures:
        (RESULTS_DIR / "_failures.json").write_text(
            json.dumps(failures, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"[done] 失败 {len(failures)} 条,详见 _failures.json")
    else:
        print(f"[done] 全部成功,总用时 {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
