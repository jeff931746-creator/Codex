#!/usr/bin/env python3
"""
人群簇库 - 小样脚本 v2（Sprint 0.2 重跑）
基于市面上代表性游戏全景反推人群簇，不依赖机制库。

数据源：LLM 训练知识中的市面买量游戏全景
route：SiliconFlow_GLM
输出：5-7 个 AUD 草稿到 archive/资料/人群簇库/_draft/sample-v2-*.md
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

OUTPUT_DIR = Path("/Users/mt/Documents/Codex/archive/资料/人群簇库/_draft")
RAW_DIR = OUTPUT_DIR / "_raw"
TODAY = datetime.now().strftime("%Y-%m-%d")

LLM_ROUTE = "SiliconFlow_GLM"

def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def call_llm(prompt: str, max_tokens: int = 6000, retries: int = 3) -> str:
    return chat_text(
        prompt,
        route=LLM_ROUTE,
        max_tokens=max_tokens,
        temperature=0.3,
        timeout=240,
        retry_policy=RetryPolicy(retries=retries, base_delay=3),
        logger=lambda msg: log(f"  {msg}"),
        return_empty_on_error=True,
    )

def call_llm_cached(prompt: str, label: str, max_tokens: int = 6000) -> str:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_DIR / f"{TODAY}_{label}.txt"
    if raw_path.exists() and raw_path.stat().st_size > 100:
        log(f"  [{label}] 使用缓存")
        return raw_path.read_text(encoding="utf-8")
    raw = call_llm(prompt, max_tokens)
    if raw:
        raw_path.write_text(raw, encoding="utf-8")
    return raw

def build_prompt() -> str:
    return """你是手游买量市场的资深用户研究专家。请基于**市面上代表性买量手游的真实玩家画像**，提取稳定的"人群簇"。

## 人群簇定义

人群簇 = 在游戏消费行为上具有稳定共性的玩家群体。
按"情绪需求 + 玩法偏好 + 付费习惯"三维聚类，**不按人口学**。

## 大类代码

| 代码 | 大类 | 核心特征 |
|---|---|---|
| Y | Young 年轻向 | 18-30岁，娱乐型消费，对新奇内容敏感 |
| M | Middle 中年向 | 30-45岁，时间碎片化，付费力强 |
| S | Senior 成熟向 | 45+岁，习惯熟悉品类，对学习成本敏感 |
| F | Female 女性向 | 强女性向偏好，情感叙事驱动 |
| C | Core 核心玩家 | 重度玩家，追求深度和挑战 |
| H | Hybrid 混合型 | 跨多个人群特征，无明显边界 |

## 命名硬约束（违反者拒绝）

✅ 好的命名：
- "策略协同重氪玩家"（行为+付费）
- "情绪推关型休闲玩家"（情绪+玩法）
- "二次元养成抽卡用户"（玩法+付费）

❌ 不允许：
- 包含**题材词**：修仙、三国、末世、宫斗（这些是题材，不是人群）
- 包含**品类代码**：SLG、RPG、MOBA（这些是玩法品类）
- 包含**程度词**：轻度、中度、重度（不是聚类维度）
- 包含**包装词**：割草、搞怪、沙盘（这些是表象）
- 包含**产品名**：口袋奇兵用户、原神党
- 包含**年龄段**：25-35岁男性

## 字段硬约束（违反者拒绝）

**representative_games 必须 ≥3 个真实存在的市面游戏**，少于 3 个直接拒绝该条目。

## 市场参考范围

请从以下市面上代表性买量游戏中识别人群簇（你可以引用所有你知道的同类游戏）：

**SLG/策略**：三国志战略版、率土之滨、口袋奇兵、Whiteout Survival 无尽冬日、万国觉醒、Top War 战火指挥官、Last War 末日

**放置/挂机**：一念逍遥、寻道大千、剑与远征、最强祖师、卡皇、AFK Journey

**Roguelite/肉鸽**：向僵尸开炮、菇勇者传说、咒术学院、吸血鬼幸存者、星之破晓

**二次元/卡牌**：原神、明日方舟、崩坏星穹铁道、鸣潮、阴阳师、坎公骑冠剑、第七史诗

**休闲/合家欢**：咸鱼之王、寻道大千、率土之滨、动物餐厅、提灯与地下城

**女性向**：恋与制作人、光与夜之恋、闪耀暖暖、未定事件簿、世界之外

**塔防**：保卫向日葵、王国保卫战、Bloons TD、明日方舟（塔防侧）

**模拟经营**：模拟人生、动物森友会、星露谷物语、波西亚时光

**消除/match**：开心消消乐、Royal Match、Candy Crush、梦幻花园

## 目标产出

识别 5-7 个市场上**真实存在且付费验证清晰**的人群簇。每个簇必须有：
- ≥3 个真实代表游戏
- 与至少一个其他簇的明确 boundary
- 三维度差异不能与其他簇重复

## 输出格式（JSON 数组）

```json
{
  "draft_id": "draft-AUD-X-001",
  "name": "人群簇名称（≤12字，遵守命名硬约束）",
  "category": "Y/M/S/F/C/H",
  "description": "一句话描述（≤30字）",
  "emotion_need": ["压力释放", "身份代入"],
  "playstyle_preference": ["策略", "放置", "构筑"],
  "payment_pattern": ["数值养成", "月卡", "抽卡", "广告变现"],
  "acquisition_difficulty": 1-5,
  "ltv_potential": 1-5,
  "evidence_level": "S/A/B/C/D",
  "age_range": "辅助参考，不是聚类依据",
  "gender_lean": "male/female/neutral",
  "geo": ["国内一二线", "下沉市场", "东南亚"],
  "info_channels": ["抖音短视频", "B站", "微信小游戏"],
  "representative_games": ["真实游戏1", "真实游戏2", "真实游戏3"],  // 硬约束：≥3
  "boundary": "与 AUD-X-XXX 的区别：本簇 vs 那簇 在 [情绪/玩法/付费] 维度上的具体差异",
  "risk_notes": "风险说明"
}
```

只返回 JSON 数组，不要其他文字或代码块标记。"""

def parse_json(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text.strip())

def validate_entry(entry: dict) -> tuple:
    """硬约束校验，返回 (是否通过, 失败原因列表)"""
    failures = []
    name = entry.get("name", "")

    # 命名硬约束
    forbidden = ["修仙", "三国", "末世", "宫斗", "末日", "二次元",
                 "SLG", "RPG", "MOBA", "FPS", "塔防",
                 "轻度", "中度", "重度",
                 "割草", "搞怪", "沙盘", "推关"]
    hits = [w for w in forbidden if w in name]
    if hits:
        failures.append(f"命名含禁词：{hits}")

    # representative_games ≥3
    rep_games = entry.get("representative_games", [])
    if len(rep_games) < 3:
        failures.append(f"代表游戏只有 {len(rep_games)} 个（要求≥3）")

    # boundary 必填
    boundary = entry.get("boundary", "")
    if not boundary or len(boundary) < 20:
        failures.append("boundary 缺失或过短")

    return (len(failures) == 0, failures)

def write_draft(entry: dict, idx: int, validation_result: tuple):
    draft_id = entry.get("draft_id", f"draft-AUD-X-{idx:03d}")
    passed, failures = validation_result
    status_tag = "✅ 通过硬约束" if passed else f"⚠️ 硬约束未通过：{'; '.join(failures)}"

    filename = f"sample-v2-{idx:02d}-{draft_id}.md"
    path = OUTPUT_DIR / filename

    def fmt_list(v):
        if isinstance(v, list):
            return ", ".join(str(x) for x in v) if v else "—"
        return str(v) if v else "—"

    content = f"""---
draft_id: {draft_id}
name: {entry.get('name', '?')}
category: {entry.get('category', '?')}
status: draft (Sprint 0 小样 v2)
validation: {status_tag}
created: {TODAY}
---

# {entry.get('name', '?')}（{draft_id}）

> **硬约束校验**：{status_tag}

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

## 代表游戏（硬约束：≥3）

{fmt_list(entry.get('representative_games'))}

## boundary（核心防呆）

{entry.get('boundary', '—')}

## 风险

{entry.get('risk_notes', '—')}

---

**审核要点**：
- [ ] 是否按"情绪+玩法+付费"三维聚类，而非人口学
- [ ] boundary 是否清晰
- [ ] 命名是否避开题材词/品类词/程度词/包装词
- [ ] 代表游戏 ≥3 个且真实存在
"""
    path.write_text(content, encoding="utf-8")
    log(f"  ✓ 写出 {filename} ({status_tag[:30]})")

def main():
    log("=" * 50)
    log("Sprint 0.2 v2: 人群簇小样生成（市场全景反推）")
    log("=" * 50)
    log(f"模型：{LLM_ROUTE}")
    log(f"数据源：LLM 训练知识中的市面买量游戏全景")
    log(f"输出：{OUTPUT_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    log("\n[1/2] 调用 LLM 提取人群簇...")
    prompt = build_prompt()
    raw = call_llm_cached(prompt, "audience_sample_v2", max_tokens=8000)
    if not raw:
        log("❌ LLM 空响应")
        return
    log(f"  原始响应：{len(raw)} 字符")

    log(f"\n[2/2] 解析并写出草稿...")
    try:
        entries = parse_json(raw)
        if not isinstance(entries, list):
            log("❌ 返回的不是数组")
            return
        log(f"  解析到 {len(entries)} 个条目")

        pass_count = 0
        for idx, entry in enumerate(entries, start=1):
            result = validate_entry(entry)
            if result[0]:
                pass_count += 1
            write_draft(entry, idx, result)

        log(f"\n硬约束校验：{pass_count}/{len(entries)} 通过")

    except Exception as e:
        log(f"❌ 解析失败：{e}")
        log(f"原始响应：\n{raw[:500]}")
        return

    log("\n" + "=" * 50)
    log(f"✅ Sprint 0.2 v2 完成！")
    log("=" * 50)

if __name__ == "__main__":
    main()
