#!/usr/bin/env python3
"""
人群簇库 - 小样脚本（Sprint 0.2）
从 5 个机制库游戏的目标用户字段提取人群簇草稿，供用户审核标准是否合理。

输入：5 个游戏的 00_总档.md
输出：3-5 个 AUD 草稿到 archive/资料/人群簇库/_draft/sample-*.md

route：SiliconFlow_GLM（深度推理，需要按情绪×玩法×付费三维聚类）
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
OUTPUT_DIR = Path("/Users/mt/Documents/Codex/archive/资料/人群簇库/_draft")
RAW_DIR = OUTPUT_DIR / "_raw"
TODAY = datetime.now().strftime("%Y-%m-%d")

# 小样：5 个有人群代表性的游戏（覆盖 Y/M/F/C 等不同人群特征）
SAMPLE_GAMES = [
    "/Users/mt/Documents/Codex/archive/资料/机制库/向僵尸开炮",     # 中度休闲射击
    "/Users/mt/Documents/Codex/archive/资料/机制库/一念逍遥",       # 仙侠放置
    "/Users/mt/Documents/Codex/archive/资料/机制库/三国志战略版",   # SLG重氪
    "/Users/mt/Documents/Codex/archive/资料/机制库/咸鱼之王",       # 全民休闲
    "/Users/mt/Documents/Codex/archive/资料/机制库/保卫向日葵",     # 经典塔防
]

LLM_ROUTE = "SiliconFlow_GLM"

# ========== 日志 ==========
def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

# ========== LLM 调用 ==========
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
    info = {"name": game_dir.name, "summary": "", "conclusion": ""}
    total_file = game_dir / "00_总档.md"
    if total_file.exists():
        info["summary"] = total_file.read_text(encoding="utf-8")[:3500]
    conclusion_dir = game_dir / "90_结论提炼"
    if conclusion_dir.exists():
        files = list(conclusion_dir.glob("*.md"))
        if files:
            info["conclusion"] = files[0].read_text(encoding="utf-8")[:2000]
    return info

# ========== Prompt 构造 ==========
def build_extract_prompt(games_data: list) -> str:
    games_str = "\n\n".join(
        f"## 游戏 {i+1}: {g['name']}\n\n### 总档摘要\n{g['summary']}\n\n### 结论提炼\n{g['conclusion']}"
        for i, g in enumerate(games_data)
    )

    return f"""你是游戏用户研究专家。请从以下 {len(games_data)} 个游戏的机制拆解中，提取"人群簇"条目。

## 人群簇定义

人群簇 = 在游戏消费行为上具有稳定共性的玩家群体。
不是按"年龄段+性别"划分，而是按"情绪需求 + 玩法偏好 + 付费习惯"三维度聚类。

例：
- ✅ AUD-Y-001 "压力释放型休闲玩家"（情绪：放松；玩法：轻度；付费：广告变现）
- ✅ AUD-M-001 "SLG策略重氪用户"（情绪：成就；玩法：策略；付费：数值养成）
- ❌ "25-35岁男性玩家"（人口学描述，无法指导买量）
- ❌ "口袋奇兵核心用户"（绑死产品）

## 大类代码

| 代码 | 大类 | 核心特征 |
|---|---|---|
| Y | Young 年轻向 | 18-30岁，娱乐型消费，对新奇内容敏感 |
| M | Middle 中年向 | 30-45岁，时间碎片化，付费力强 |
| S | Senior 成熟向 | 45+岁，习惯熟悉品类，对学习成本敏感 |
| F | Female 女性向 | 强女性向偏好，情感叙事驱动 |
| C | Core 核心玩家 | 重度玩家，追求深度和挑战 |
| H | Hybrid 混合型 | 跨多个人群特征，无明显边界 |

**注意**：归大类的依据是**核心买量识别特征**——能决定素材表达的那个维度。

## 输入数据

{games_str}

## 任务要求

1. 从上述游戏中识别出 3-5 个独立的"人群簇"
2. 如果两个游戏面向同一人群（情绪需求、玩法偏好、付费习惯相同），合并成一个条目
3. 一个游戏可能命中多个人群簇（如咸鱼之王同时命中休闲玩家和怀旧用户）
4. **必须填 boundary 字段**：说明与已识别的相邻人群簇的差异

## 输出格式（JSON 数组，每个条目）

```json
{{
  "draft_id": "draft-AUD-X-001",  // X 是大类代码
  "name": "人群簇名称（≤12字）",
  "category": "Y/M/S/F/C/H",
  "description": "一句话描述（≤30字）",
  "emotion_need": ["压力释放", "身份代入"],
  "playstyle_preference": ["策略", "放置"],
  "payment_pattern": ["数值养成", "月卡", "抽卡", "广告变现"],
  "acquisition_difficulty": 1-5,
  "ltv_potential": 1-5,
  "evidence_level": "S/A/B/C/D",
  "age_range": "如 18-35（可选）",
  "gender_lean": "male/female/neutral",
  "geo": ["国内一二线", "东南亚"],
  "info_channels": ["抖音短视频", "B站"],
  "representative_games": ["游戏1", "游戏2", "游戏3"],
  "boundary": "与 AUD-X-XXX 的区别：...（必填，说明与已识别的相邻人群簇的差异）",
  "risk_notes": "风险说明",
  "source_games": ["源自输入的哪个游戏"]
}}
```

只返回 JSON 数组，不要其他文字或代码块标记。"""

# ========== 解析 ==========
def parse_json(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text.strip())

# ========== 写出草稿 ==========
def write_draft(entry: dict, idx: int):
    draft_id = entry.get("draft_id", f"draft-AUD-X-{idx:03d}")
    filename = f"sample-{idx:02d}-{draft_id}.md"
    path = OUTPUT_DIR / filename

    def fmt_list(v):
        if isinstance(v, list):
            return ", ".join(str(x) for x in v) if v else "—"
        return str(v) if v else "—"

    content = f"""---
draft_id: {draft_id}
name: {entry.get('name', '?')}
category: {entry.get('category', '?')}
status: draft (Sprint 0 小样)
created: {TODAY}
---

# {entry.get('name', '?')}（{draft_id}）

## 描述

{entry.get('description', '—')}

## 核心特征（三维度聚类）

| 维度 | 内容 |
|---|---|
| 情绪需求 | {fmt_list(entry.get('emotion_need'))} |
| 玩法偏好 | {fmt_list(entry.get('playstyle_preference'))} |
| 付费习惯 | {fmt_list(entry.get('payment_pattern'))} |

## 评分

- 获量难度：{entry.get('acquisition_difficulty', '—')}/5
- LTV 潜力：{entry.get('ltv_potential', '—')}/5
- 证据等级：{entry.get('evidence_level', '—')}

## 人口学参考（仅辅助识别）

- 年龄段：{entry.get('age_range', '—')}
- 性别倾向：{entry.get('gender_lean', '—')}
- 地域：{fmt_list(entry.get('geo'))}
- 信息渠道：{fmt_list(entry.get('info_channels'))}

## 代表游戏

{fmt_list(entry.get('representative_games'))}

## boundary（边界差异，核心防呆）

{entry.get('boundary', '—')}

## 风险

{entry.get('risk_notes', '—')}

## 来源游戏（Sprint 0 小样追溯）

{fmt_list(entry.get('source_games'))}

---

**审核要点**：
- [ ] 是否按"情绪+玩法+付费"三维聚类，而非人口学
- [ ] boundary 字段是否清晰说明与相邻簇的差异
- [ ] 命名是否避开"年龄段"和"产品名"
- [ ] 大类归属是否合理
"""
    path.write_text(content, encoding="utf-8")
    log(f"  ✓ 写出 {filename}")
    return path

# ========== 主流程 ==========
def main():
    log("=" * 50)
    log("Sprint 0.2: 人群簇小样生成")
    log("=" * 50)
    log(f"模型：{LLM_ROUTE}")
    log(f"输入：{len(SAMPLE_GAMES)} 个游戏")
    log(f"输出：{OUTPUT_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    log("\n[1/3] 读取游戏数据...")
    games_data = []
    for game_path in SAMPLE_GAMES:
        game_dir = Path(game_path)
        if not game_dir.exists():
            log(f"  ⚠️ 不存在：{game_dir}")
            continue
        info = read_game_data(game_dir)
        games_data.append(info)
        log(f"  ✓ {info['name']}: 总档 {len(info['summary'])} 字符, 结论 {len(info['conclusion'])} 字符")

    if not games_data:
        log("❌ 没有游戏数据，退出")
        return

    log(f"\n[2/3] 调用 LLM 提取人群簇...")
    prompt = build_extract_prompt(games_data)
    raw = call_llm_cached(prompt, "audience_sample", max_tokens=6000)
    if not raw:
        log("❌ LLM 空响应")
        return
    log(f"  原始响应：{len(raw)} 字符")

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
    log(f"✅ Sprint 0.2 完成！")
    log(f"   生成 {len(entries)} 个草稿到 {OUTPUT_DIR}")
    log("=" * 50)

if __name__ == "__main__":
    main()
