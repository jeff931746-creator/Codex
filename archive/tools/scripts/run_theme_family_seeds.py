#!/usr/bin/env python3
"""
为 10 个种子题材族生成总档。

调用约定:
  - 通过 archive.tools.lib.llm_client 调用 DeepSeek_Official_Pro route
  - 严格 zero-shot,只给方法论标准和模板

启动:
  set -a
  source "$HOME/Library/Application Support/FeishuCodexBridge/bridge/.env"
  set +a
  export LLM_ROUTE=DeepSeek_Official_Pro
  python3 archive/tools/scripts/run_theme_family_seeds.py

产物:
  题材库/_run_seeds/02-results/<族名>.md
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path("/Users/mt/Documents/Codex")
sys.path.insert(0, str(ROOT))

from archive.tools.lib.llm_client import chat_text
from archive.tools.lib.llm_common import RetryPolicy

THEME_LIB = ROOT / "archive/资料/买量组合库/题材库"
RUN_DIR = THEME_LIB / "_run_seeds"
PROMPTS_DIR = RUN_DIR / "01-prompts"
RESULTS_DIR = RUN_DIR / "02-results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

STANDARD_PATH = THEME_LIB / "题材族拆解标准.md"
TEMPLATE_PATH = THEME_LIB / "00_题材族总档模板.md"
SEEDS_PATH = PROMPTS_DIR / "seeds.json"


def load_system_prompt() -> str:
    template = (PROMPTS_DIR / "system.md").read_text(encoding="utf-8")
    standard = STANDARD_PATH.read_text(encoding="utf-8")
    template_text = TEMPLATE_PATH.read_text(encoding="utf-8")
    return (template
            .replace("【__STANDARD__】", standard)
            .replace("【__TEMPLATE__】", template_text))


def load_user_template() -> str:
    return (PROMPTS_DIR / "user_template.md").read_text(encoding="utf-8")


def build_user(template: str, seed: dict) -> str:
    return (template
            .replace("__FAMILY_NAME__", seed["family_name"])
            .replace("__EXPECTED_POSITION__", seed["expected_position"])
            .replace("__HINT_REPRESENTATIVES__", seed["hint_representatives"])
            .replace("__ADJACENT_FAMILIES__", seed["adjacent_families"]))


def safe_name(name: str) -> str:
    return name.replace("/", "_").replace(" ", "_")[:40]


def main():
    llm_route = "DeepSeek_Official_Pro"
    print(f"[info] LLM_ROUTE={llm_route}")

    seeds = json.loads(SEEDS_PATH.read_text(encoding="utf-8"))
    print(f"[info] 加载 {len(seeds)} 个种子题材族")

    system = load_system_prompt()
    user_tmpl = load_user_template()
    print(f"[info] system prompt 长度: {len(system)} chars")

    t0 = time.time()
    failures = []
    for i, seed in enumerate(seeds, 1):
        name = seed["family_name"]
        out_path = RESULTS_DIR / f"{safe_name(name)}.md"
        if out_path.exists():
            print(f"[skip] {i}/{len(seeds)} {name} (已存在)")
            continue
        user = build_user(user_tmpl, seed)
        try:
            print(f"[run] {i}/{len(seeds)} {name}", flush=True)
            t1 = time.time()
            text = chat_text(
                user,
                system=system,
                route=llm_route,
                max_tokens=6000,
                temperature=0.2,
                timeout=300,
                retry_policy=RetryPolicy(retries=2, base_delay=4.0),
            )
            elapsed = time.time() - t1
            print(f"  -> {elapsed:.1f}s, {len(text)} chars", flush=True)
            out_path.write_text(text, encoding="utf-8")
        except Exception as e:
            print(f"  [ERROR] {e}", flush=True)
            failures.append({"family": name, "error": str(e)})

    if failures:
        (RESULTS_DIR / "_failures.json").write_text(
            json.dumps(failures, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    total = time.time() - t0
    print(f"[done] 失败 {len(failures)} 条; 总用时 {total:.1f}s")


if __name__ == "__main__":
    main()
