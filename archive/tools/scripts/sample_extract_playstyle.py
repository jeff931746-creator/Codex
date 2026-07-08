#!/usr/bin/env python3
"""
玩法承接库 - 小样脚本（Sprint 0.1）
从 3 个机制库游戏中提取玩法承接草稿，供用户审核标准是否合理。

输入：3 个游戏的 00_总档.md + 90_结论提炼/
输出：3-5 个 PLY 草稿到 archive/资料/玩法承接库/_draft/sample-*.md

route：SiliconFlow_GLM（深度推理）
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
for _parent in _THIS_FILE.parents:
    if (_parent / "archive" / "tools" / "lib").is_dir():
        sys.path.insert(0, str(_parent))
        break

from archive.tools.lib.llm_common import RetryPolicy
from archive.tools.lib.llm_client import chat_text

# ========== 配置 ==========
OUTPUT_DIR = Path("/Users/mt/Documents/Codex/archive/资料/玩法承接库/_draft")
RAW_DIR = OUTPUT_DIR / "_raw"
TODAY = datetime.now().strftime("%Y-%m-%d")

# 小样：3 个有代表性的游戏（射击肉鸽、放置仙侠、SLG）
SAMPLE_GAMES = [
    "/Users/mt/Documents/Codex/archive/资料/机制库/向僵尸开炮",
    "/Users/mt/Documents/Codex/archive/资料/机制库/一念逍遥",
    "/Users/mt/Documents/Codex/archive/资料/机制库/口袋奇兵",
]

LLM_ROUTE = "SiliconFlow_GLM"

# ========== 日志 ==========
def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

# ========== LLM 调用（复用 build_historical_theme_library 的模式）==========
def call_llm(prompt: str, max_tokens: int = 4000, retries: int = 3) -> str:
    return chat_text(
        prompt,
        route=LLM_ROUTE,
        max_tokens=max_tokens,
        temperature=0.3,
        timeout=180,
        retry_policy=RetryPolicy(retries=retries, base_delay=3),
        logger=lambda msg: log(f"  {msg}"),
        return_empty_on_error=True,
    )

def call_llm_cached(prompt: str, label: str, max_tokens: int = 4000) -> str:
    """带缓存的 LLM 调用"""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_DIR / f"{TODAY}_{label}.txt"
    if raw_path.exists() and raw_path.stat().st_size > 100:
        log(f"  [{label}] 使用缓存")
        return raw_path.read_text(encoding="utf-8")
    raw = call_llm(prompt, max_tokens)
    if raw:
        raw_path.write_text(raw, encoding="utf-8")
    return raw

# ========== 读取游戏数据 ==========
def read_game_data(game_dir: Path) -> dict:
    """读取一个游戏的关键信息"""
    info = {"name": game_dir.name, "summary": "", "conclusion": ""}

    # 读总档
    total_file = game_dir / "00_总档.md"
    if total_file.exists():
        content = total_file.read_text(encoding="utf-8")
        info["summary"] = content[:3000]  # 取前3000字符

    # 读结论提炼（如果有）
    conclusion_dir = game_dir / "90_结论提炼"
    if conclusion_dir.exists():
        conclusion_files = list(conclusion_dir.glob("*.md"))
        if conclusion_files:
            info["conclusion"] = conclusion_files[0].read_text(encoding="utf-8")[:2000]

    return info

# ========== Prompt 构造 ==========
def build_extract_prompt(games_data: list) -> str:
    """构造玩法承接提取 prompt"""
    games_str = "\n\n".join(
        f"## 游戏 {i+1}: {g['name']}\n\n### 总档摘要\n{g['summary']}\n\n### 结论提炼\n{g['conclusion']}"
        for i, g in enumerate(games_data)
    )

    return f"""你是游戏设计专家。请从以下 {len(games_data)} 个游戏的机制拆解中，提取"玩法承接"条目。

## 玩法承接定义

玩法承接 = 品类骨架 + 具体核心循环 + 商业化承接方式 的组合。
是抽象层概念，不是某个游戏的具体机制描述。

例：
- ✅ PLY-TD-001 "波次防守 + 局外塔型升级"（PVZ模式）
- ✅ PLY-RG-001 "肉鸽局内构筑 + 局外永久成长"
- ❌ "塔防"（太宽泛，无法区分PVZ vs 向僵尸开炮）
- ❌ "向僵尸开炮玩法"（绑死参考游戏）

## 大类代码

| 代码 | 品类 |
|---|---|
| TD | 塔防 |
| RPG | 角色扮演 |
| SLG | 策略 |
| RG | Roguelike |
| IDL | 放置 |
| CD | 卡牌 |
| SIM | 模拟经营 |
| PZ | 解谜 |
| ACT | 动作 |
| BAT | 战斗策略 |

## 独立性五问（必须全部通过）

1. 成功案例：这个玩法能否单独做成一个**成功**的游戏？
2. 操作冲突：与其他玩法结合时是否产生操作冲突？
3. 时间分离：与其他玩法的时间分离是否清晰？
4. 成果体现：成果能否在其他玩法中直接体现？
5. 深度检验：本身是否有足够深度撑起长线？

## 输入数据

{games_str}

## 任务要求

1. 从上述游戏中识别出 3-5 个独立的"玩法承接"（**不是每个游戏一个**）
2. 如果两个游戏属于同一玩法承接（同样的品类骨架+核心循环），合并成一个条目
3. 如果一个游戏由 2 个独立玩法组合而成，拆分成 2 个玩法承接

## 输出格式（JSON 数组，每个条目）

```json
{{
  "draft_id": "draft-PLY-XX-001",  // XX 是大类代码
  "name": "玩法承接名称（≤15字，品类骨架+核心循环）",
  "category": "TD/RPG/SLG/RG/IDL/CD/SIM/PZ/ACT/BAT",
  "core_loop": "核心循环描述（≤50字）",
  "independence_check": {{
    "成功案例": "✅/❌ + 理由",
    "操作冲突": "✅/❌ + 理由",
    "时间分离": "✅/❌ + 理由",
    "成果体现": "✅/❌ + 理由",
    "深度检验": "✅/❌ + 理由"
  }},
  "representative_games": ["游戏1", "游戏2", "游戏3"],
  "core_systems": ["系统1", "系统2"],
  "monetization": ["数值养成", "抽卡"],
  "retention_depth": 1-5,
  "operation_burden": 1-5,
  "risk_notes": ["风险1", "风险2"],
  "source_games": ["源自输入的哪个游戏"],
  "evidence_level": "S/A/B/C/D"
}}
```

只返回 JSON 数组，不要其他文字或代码块标记。"""

# ========== 解析输出 ==========
def parse_json(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    text = text.strip()
    return json.loads(text)

# ========== 写出草稿 ==========
def write_draft(entry: dict, idx: int):
    """把一个玩法承接条目写成 markdown 草稿"""
    draft_id = entry.get("draft_id", f"draft-PLY-XX-{idx:03d}")
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', entry.get("name", "未命名"))
    filename = f"sample-{idx:02d}-{draft_id}.md"
    path = OUTPUT_DIR / filename

    check = entry.get("independence_check", {})
    representatives = entry.get("representative_games", [])
    systems = entry.get("core_systems", [])
    monetization = entry.get("monetization", [])
    risks = entry.get("risk_notes", [])
    sources = entry.get("source_games", [])

    content = f"""---
draft_id: {draft_id}
name: {entry.get('name', '?')}
category: {entry.get('category', '?')}
status: draft (Sprint 0 小样)
created: {TODAY}
---

# {entry.get('name', '?')}（{draft_id}）

## 核心循环

{entry.get('core_loop', '—')}

## 独立性五问

| 问题 | 回答 |
|---|---|
| 成功案例 | {check.get('成功案例', '—')} |
| 操作冲突 | {check.get('操作冲突', '—')} |
| 时间分离 | {check.get('时间分离', '—')} |
| 成果体现 | {check.get('成果体现', '—')} |
| 深度检验 | {check.get('深度检验', '—')} |

## 代表游戏

{chr(10).join(f"- {g}" for g in representatives) if representatives else "—"}

## 核心系统

{', '.join(systems) if systems else '—'}

## 商业化方式

{', '.join(monetization) if monetization else '—'}

## 评分

- 长线留存深度：{entry.get('retention_depth', '—')}/5
- 操作负担：{entry.get('operation_burden', '—')}/5
- 证据等级：{entry.get('evidence_level', '—')}

## 风险

{chr(10).join(f"- {r}" for r in risks) if risks else "—"}

## 来源游戏（Sprint 0 小样追溯）

{', '.join(sources) if sources else '—'}

---

**审核要点**：
- [ ] 命名是否符合"品类骨架+核心循环"原则
- [ ] independence_check 是否真正答到点
- [ ] 与其他条目是否有重复（去重逻辑是否生效）
"""
    path.write_text(content, encoding="utf-8")
    log(f"  ✓ 写出 {filename}")
    return path

# ========== 主流程 ==========
def main():
    log("=" * 50)
    log("Sprint 0.1: 玩法承接小样生成")
    log("=" * 50)
    log(f"模型：{LLM_ROUTE}")
    log(f"输入：{len(SAMPLE_GAMES)} 个游戏")
    log(f"输出：{OUTPUT_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. 读取游戏数据
    log("\n[1/3] 读取游戏数据...")
    games_data = []
    for game_path in SAMPLE_GAMES:
        game_dir = Path(game_path)
        if not game_dir.exists():
            log(f"  ⚠️ 游戏目录不存在：{game_dir}")
            continue
        info = read_game_data(game_dir)
        games_data.append(info)
        log(f"  ✓ {info['name']}: 总档 {len(info['summary'])} 字符, 结论 {len(info['conclusion'])} 字符")

    if not games_data:
        log("❌ 没有可用的游戏数据，退出")
        return

    # 2. 调用 LLM 提取
    log(f"\n[2/3] 调用 LLM 提取玩法承接...")
    prompt = build_extract_prompt(games_data)
    raw = call_llm_cached(prompt, "playstyle_sample", max_tokens=6000)

    if not raw:
        log("❌ LLM 返回空响应")
        return

    log(f"  原始响应：{len(raw)} 字符")

    # 3. 解析并写出草稿
    log(f"\n[3/3] 解析并写出草稿...")
    try:
        entries = parse_json(raw)
        if not isinstance(entries, list):
            log(f"❌ 返回的不是数组")
            return
        log(f"  解析到 {len(entries)} 个条目")

        for idx, entry in enumerate(entries, start=1):
            write_draft(entry, idx)

    except Exception as e:
        log(f"❌ 解析失败：{e}")
        log(f"原始响应：\n{raw[:500]}")
        return

    log("\n" + "=" * 50)
    log(f"✅ Sprint 0.1 完成！")
    log(f"   生成 {len(entries)} 个草稿到 {OUTPUT_DIR}")
    log(f"   原始响应保存在 {RAW_DIR}")
    log(f"\n下一步：人工审核草稿是否符合标准")
    log("=" * 50)

if __name__ == "__main__":
    main()
