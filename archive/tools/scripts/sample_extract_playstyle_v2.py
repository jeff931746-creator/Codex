#!/usr/bin/env python3
"""
玩法承接库 - 小样脚本 v2（Sprint 0.1 重跑）
加入硬约束 + 嵌入标准映射对照 + 五问诊断深度要求

模型：GLM-5.1
输出：3-5 个 PLY 草稿到 archive/资料/玩法承接库/_draft/sample-v2-*.md
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

from archive.tools.lib.siliconflow_client import RetryPolicy, chat_text

OUTPUT_DIR = Path("/Users/mt/Documents/Codex/archive/资料/玩法承接库/_draft")
RAW_DIR = OUTPUT_DIR / "_raw"
TODAY = datetime.now().strftime("%Y-%m-%d")

# 输入：3 个有代表性的游戏（射击肉鸽、放置仙侠、SLG）
SAMPLE_GAMES = [
    "/Users/mt/Documents/Codex/archive/资料/机制库/向僵尸开炮",
    "/Users/mt/Documents/Codex/archive/资料/机制库/一念逍遥",
    "/Users/mt/Documents/Codex/archive/资料/机制库/口袋奇兵",
]

MODEL = os.environ.get("SILICONFLOW_MODEL", "Pro/zai-org/GLM-5.1")

def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def call_llm(prompt: str, max_tokens: int = 6000, retries: int = 3) -> str:
    return chat_text(
        prompt,
        model=MODEL,
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

def read_game_data(game_dir: Path) -> dict:
    info = {"name": game_dir.name, "summary": "", "conclusion": ""}
    total_file = game_dir / "00_总档.md"
    if total_file.exists():
        info["summary"] = total_file.read_text(encoding="utf-8")[:3000]
    conclusion_dir = game_dir / "90_结论提炼"
    if conclusion_dir.exists():
        files = list(conclusion_dir.glob("*.md"))
        if files:
            info["conclusion"] = files[0].read_text(encoding="utf-8")[:2000]
    return info

def build_prompt(games_data: list) -> str:
    games_str = "\n\n".join(
        f"## 游戏 {i+1}: {g['name']}\n\n### 总档\n{g['summary']}\n\n### 结论\n{g['conclusion']}"
        for i, g in enumerate(games_data)
    )

    return f"""你是游戏设计资深专家。请从以下 {len(games_data)} 个游戏的机制拆解中，提取"玩法承接"条目。

## 玩法承接定义

玩法承接 = 品类骨架 + 具体核心循环 + 商业化承接方式 的组合。
是**抽象的、可复用**的层级，不是某个游戏的具体机制描述。

## 大类代码 + 参考映射（必读）

| 代码 | 品类 | 已知 PLY 参考 |
|---|---|---|
| TD | 塔防 | **向僵尸开炮 = 自走防守+卡组构筑（TD类）**，保卫向日葵 = 波次防守+局外塔型升级（TD类），Bloons TD |
| RPG | 角色扮演 | 原神、明日方舟、咸鱼之王 |
| SLG | 策略 | 三国志战略版、口袋奇兵、无尽冬日 |
| RG | Roguelike | 杀戮尖塔、吸血鬼幸存者、菇勇者传说 |
| IDL | 放置 | 一念逍遥、剑与远征、最强祖师 |
| CD | 卡牌 | 阴阳师、坎公骑冠剑 |
| SIM | 模拟经营 | Factorio、动物餐厅 |
| PZ | 解谜 | 纪念碑谷 |
| ACT | 动作 | 黑神话、艾尔登法环 |
| BAT | 战斗策略 | 皇室战争、英雄无敌 |

**重要警示**：
- 向僵尸开炮属于 **TD 大类**（自走塔防+局内构筑），不是 RG。它"看起来像肉鸽"但骨架是塔防的波次守线，肉鸽的局内三选一只是构筑层。
- 一念逍遥属于 **IDL 大类**，不是 RPG。挂机产出是骨架。
- 口袋奇兵属于 **SLG 大类**，但它的"即时合成"是核心创新点，区别于三战的卡组+大地图模式。

## 命名硬约束（违反者拒绝）

✅ 好的命名：
- "波次防守+局外塔型升级"（品类骨架+循环）
- "放置挂机+里程碑解锁"
- "即时合成+领地扩张"

❌ 不允许：
- **包含具体题材词**：修仙、三国、末世（题材不是玩法）
- **包含大类代码本身**：SLG/RPG/TD（重复信息）
- **包含游戏名**：PVZ玩法、向僵尸开炮模式（绑死参考）
- **机制堆叠**：塔防+卡牌+肉鸽（不是核心循环）

## 字段硬约束（违反者拒绝）

1. **representative_games 必须 ≥3 个真实存在的游戏**
2. **independence_check 五问每问必须举具体游戏案例或反例作论据**，禁止纯 ✅+套话

### 五问示例（达标 vs 不达标）

**示例：波次防守+局外塔型升级**

不达标 ❌：
```
1. 成功案例：✅ 已验证
2. 操作冲突：✅ 操作分离
3. 时间分离：✅ 时间分离清晰
```

达标 ✅：
```
1. 成功案例：✅ PVZ 系列、Bloons TD、王国保卫战 多家厂商独立验证可成功
2. 操作冲突：⚠️ 与"操控角色战斗"结合时会产生冲突——玩家同时要操控角色走位+部署塔，注意力分裂；Thronefall 的解法是用暂停机制错峰
3. 时间分离：✅ 波次间策略（部署/升级）vs 波次内自动（塔自动攻击），时间分离明确
4. 成果体现：✅ 局外塔型升级直接影响波次内表现（数值+解锁）
5. 深度检验：✅ 多塔组合+难度曲线+成就关卡撑起 100+ 关卡内容
```

## 输入数据

{games_str}

## 任务要求

1. 从上述游戏中识别 3-5 个"玩法承接"
2. 严格按上述参考映射归类（向僵尸开炮→TD，一念逍遥→IDL，口袋奇兵→SLG）
3. 如果游戏由 2 个独立玩法组合，可以拆分
4. **每个条目必须 ≥3 个 representative_games**，从市面同类游戏中补足

## 输出格式（JSON 数组）

```json
{{
  "draft_id": "draft-PLY-XX-001",
  "name": "玩法承接名称（≤15字，遵守命名硬约束）",
  "category": "TD/RPG/SLG/RG/IDL/CD/SIM/PZ/ACT/BAT",
  "core_loop": "核心循环描述（≤50字）",
  "independence_check": {{
    "成功案例": "✅/❌ + 至少举3个具体游戏",
    "操作冲突": "✅/⚠️/❌ + 具体冲突场景或佐证案例",
    "时间分离": "✅/❌ + 具体时间维度分析",
    "成果体现": "✅/❌ + 具体成果转化路径",
    "深度检验": "✅/❌ + 长线内容支撑机制"
  }},
  "representative_games": ["游戏1", "游戏2", "游戏3"],  // 硬约束：≥3
  "core_systems": ["系统1", "系统2"],
  "monetization": ["数值养成", "抽卡"],
  "retention_depth": 1-5,
  "operation_burden": 1-5,
  "risk_notes": ["针对该玩法的具体风险", "..."],
  "source_games": ["源自输入"],
  "evidence_level": "S/A/B/C/D"
}}
```

只返回 JSON 数组，不要其他文字或代码块标记。"""

def parse_json(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text.strip())

def validate_entry(entry: dict) -> tuple:
    failures = []
    name = entry.get("name", "")

    # 命名硬约束
    forbidden_theme = ["修仙", "三国", "末世", "宫斗", "末日"]
    forbidden_cat = ["SLG", "RPG", "MOBA", "FPS", "TD", "RG", "IDL", "CD", "SIM", "PZ", "ACT", "BAT"]
    forbidden_brand = ["PVZ", "向僵尸开炮", "原神", "口袋奇兵"]

    for w in forbidden_theme + forbidden_brand:
        if w in name:
            failures.append(f"命名含禁词：{w}")
    for w in forbidden_cat:
        # 检查整词，避免误伤（如"塔防"不在禁列）
        if re.search(rf'\b{w}\b', name):
            failures.append(f"命名含大类代码：{w}")

    # representative_games ≥3
    rep_games = entry.get("representative_games", [])
    if len(rep_games) < 3:
        failures.append(f"代表游戏只有 {len(rep_games)} 个（要求≥3）")

    # 五问深度检查
    check = entry.get("independence_check", {})
    short_answers = []
    for q, ans in check.items():
        if isinstance(ans, str) and len(ans) < 20:
            short_answers.append(q)
    if short_answers:
        failures.append(f"五问过短（无论据）：{short_answers}")

    return (len(failures) == 0, failures)

def write_draft(entry: dict, idx: int, validation_result: tuple):
    draft_id = entry.get("draft_id", f"draft-PLY-XX-{idx:03d}")
    passed, failures = validation_result
    status_tag = "✅ 通过硬约束" if passed else f"⚠️ 硬约束未通过：{'; '.join(failures)}"

    filename = f"sample-v2-{idx:02d}-{draft_id}.md"
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
status: draft (Sprint 0 小样 v2)
validation: {status_tag}
created: {TODAY}
---

# {entry.get('name', '?')}（{draft_id}）

> **硬约束校验**：{status_tag}

## 核心循环

{entry.get('core_loop', '—')}

## 独立性五问（必含具体论据）

| 问题 | 回答 |
|---|---|
| 成功案例 | {check.get('成功案例', '—')} |
| 操作冲突 | {check.get('操作冲突', '—')} |
| 时间分离 | {check.get('时间分离', '—')} |
| 成果体现 | {check.get('成果体现', '—')} |
| 深度检验 | {check.get('深度检验', '—')} |

## 代表游戏（硬约束：≥3）

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
- [ ] 命名是否符合"品类骨架+核心循环"（无题材词/品类代码/游戏名）
- [ ] independence_check 是否含具体论据
- [ ] representative_games ≥3 且真实存在
"""
    path.write_text(content, encoding="utf-8")
    log(f"  ✓ 写出 {filename} ({status_tag[:30]})")

def main():
    log("=" * 50)
    log("Sprint 0.1 v2: 玩法承接小样生成（加硬约束）")
    log("=" * 50)
    log(f"模型：{MODEL}")
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
        log(f"  ✓ {info['name']}")

    log(f"\n[2/3] 调用 LLM...")
    prompt = build_prompt(games_data)
    raw = call_llm_cached(prompt, "playstyle_sample_v2", max_tokens=8000)
    if not raw:
        log("❌ 空响应")
        return
    log(f"  原始响应：{len(raw)} 字符")

    log(f"\n[3/3] 解析+校验...")
    try:
        entries = parse_json(raw)
        if not isinstance(entries, list):
            log("❌ 返回非数组")
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
    log(f"✅ Sprint 0.1 v2 完成！")
    log("=" * 50)

if __name__ == "__main__":
    main()
