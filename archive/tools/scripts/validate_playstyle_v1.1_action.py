#!/usr/bin/env python3
"""
玩法承接 v1.1 矩阵验证脚本(行为契约版 A/P/F/N)

公分母:玩法承接 = 玩家行为契约
  A (Action):    反复行为
  P (Pressure):  成本/压力
  F (Feedback):  成功反馈
  N (Need):      心理收益(直接对接人群簇 T1-T6)

模型:DeepSeek V4 Pro(LLM_PROVIDER=deepseek)
输出:archive/资料/玩法承接库/_draft/validation_report_v1.1_action_{date}.md
"""

import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
for _parent in _THIS_FILE.parents:
    if (_parent / "archive" / "tools" / "lib").is_dir():
        sys.path.insert(0, str(_parent))
        break

from archive.tools.lib.llm_client import chat_text
from archive.tools.lib.llm_common import RetryPolicy

OUTPUT_DIR = Path("/Users/mt/Documents/Codex/archive/资料/玩法承接库/_draft")
RAW_DIR = OUTPUT_DIR / "_raw" / "v1.1_action"
TODAY = datetime.now().strftime("%Y-%m-%d")
RANKING_DIR = Path("/Users/mt/Documents/Codex/archive/资料/竞品库/爆款年度榜")


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def call_llm(prompt, max_tokens=18000, retries=4):
    return chat_text(
        prompt,
        max_tokens=max_tokens,
        temperature=0.2,
        timeout=360,
        retry_policy=RetryPolicy(
            retries=retries,
            base_delay=3,
            long_retry_after_attempt=3,
            long_delay_range=(300, 600),
        ),
        logger=lambda msg: log(f"  {msg}"),
        return_empty_on_error=True,
    )


def call_llm_cached(prompt, label, max_tokens=18000):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_DIR / f"{TODAY}_{label}.txt"
    if raw_path.exists() and raw_path.stat().st_size > 100:
        log(f"  [{label}] 使用缓存")
        return raw_path.read_text(encoding="utf-8")
    raw = call_llm(prompt, max_tokens)
    if raw:
        raw_path.write_text(raw, encoding="utf-8")
    return raw


def extract_samples_from_md(file_path, year, section):
    samples = []
    text = file_path.read_text(encoding="utf-8")
    seen = set()
    for line in text.split("\n"):
        line = line.strip()
        if not line.startswith("|") or "---" in line:
            continue
        if line.startswith("| 游戏名"):
            continue
        cells = [c.strip() for c in line.split("|") if c.strip()]
        if len(cells) < 3:
            continue
        name, tag, feature = cells[0], cells[1], cells[2]
        if not name or name in seen:
            continue
        seen.add(name)
        samples.append({
            "year": year,
            "section": section,
            "name": name,
            "tag": tag,
            "feature": feature,
        })
    return samples


def load_all_samples():
    seen = {}
    platforms = ["Steam", "微信小游戏", "手游", "任天堂"]
    for platform in platforms:
        platform_dir = RANKING_DIR / platform
        if not platform_dir.exists():
            log(f"  ⚠️ {platform_dir} 不存在")
            continue
        for year in range(2015, 2027):
            fp = platform_dir / f"{year}.md"
            if not fp.exists():
                continue
            year_samples = extract_samples_from_md(fp, year, platform)
            log(f"  {platform}/{year}: {len(year_samples)} 个")
            for s in year_samples:
                if s["name"] not in seen or seen[s["name"]]["year"] < s["year"]:
                    seen[s["name"]] = s
    samples = list(seen.values())
    samples.sort(key=lambda x: (x["section"], -x["year"], x["name"]))
    for i, s in enumerate(samples, 1):
        s["id"] = i
    return samples


V11_RULES = """
# 玩法承接 v1.1 行为契约归类规则(必须严格遵守)

## 公分母

玩法承接 = 玩家行为契约 = A × P × F × N

每个游戏必须用以下 4 个维度描述:
- A (Action):     玩家每天/每局/每节点反复做什么
- P (Pressure):   玩家付出什么 + 承受什么(成本 + 压力)
- F (Feedback):   成功时给玩家什么反馈
- N (Need):       这个反馈满足什么心理需求(直接对接人群簇 T1-T6)

## A 反复行为(7 个)

| 编号 | A 类型 | 描述 |
|---|---|---|
| A1 | 对抗真人 | 与真人 PVP 胜负、比拼、博弈 |
| A2 | 克服 PVE 内容 | 打 BOSS、推关卡、刷怪 |
| A3 | 投入累积 | 登录、领奖、看战力涨、刷资源(强调"看见数字") |
| A4 | 调整系统 | 设计布局、排序、优化流程、调参 |
| A5 | 探索/试错 | 抽卡组、走未知路线、试规则、解谜 |
| A6 | 见证内容 | 看剧情、看角色、看演出(操作低,主动接收) |
| A7 | 协同执行 | 和真人协调任务、分工执行(非对抗) |

允许多选(一个游戏可同时有多个 A),但必须标 1 个主 A。

## P 成本与压力(成本 5 + 压力 6)

P-成本(玩家必须投入什么):
- P-Rxn: 反应力(操作手感、即时判断)
- P-Time: 时间(单局时长 / 长期在线)
- P-Cog: 认知(钻研规则、查攻略、推演)
- P-Soc: 社交(必须有真人队友/对手/熟人局)
- P-$: 金钱(高 ARPU 才能解锁完整体验)

P-压力(玩家承受什么):
- Pr-Lose: 失败压力(失败惩罚强)
- Pr-Cmp: 比较压力(与真人/排名比较)
- Pr-Rnd: 随机压力(不可控运气因素)
- Pr-Sct: 稀缺压力(资源/时间/角色不够)
- Pr-Spd: 时间限制压力(版本压迫、活动限时)
- Pr-Low: 低压力(基本无压力,自我节奏)

允许多选,但 Pr-Low 与其他压力互斥(同时只能有一个压力主轴)。

## F 成功反馈(6 个)

| 编号 | F 类型 | 反馈本质 |
|---|---|---|
| F1 | 击杀反馈 | 即时打击、爆装、命中(秒级反馈) |
| F2 | 数值膨胀 | 数字慢慢涨,看见就有满足 |
| F3 | 系统涌现 | 多元素跑出意外好结果 |
| F4 | 闭环达成 | 关卡通过、谜题解开、套装齐 |
| F5 | 情感见证 | 剧情进展、角色亲密 |
| F6 | 社交认可 | 排名提升、被点赞、被认同 |

允许多选,但必须标 1 个主 F。

## N 心理收益(6 个,直接对接人群簇 T1-T6)

| 编号 | N 心理收益 | 对应人群簇心理任务 | 典型 |
|---|---|---|---|
| N-Adj | 状态调节 | T1 情绪调节 | 消除、派对、治愈、放置爽感 |
| N-Conf | 自我确认 | T2 自我确认 | 战神文、PVP上分、数值养成、晒收藏 |
| N-Int | 亲密连接 | T3 亲密连接 | 乙女、原神角色、宠物 |
| N-Bel | 协作归属 | T4 协作归属 | SLG联盟、公会副本、组织协作 |
| N-Cog | 认知扩展 | T5 认知扩展 | 解谜、推理、规则解码、构筑 |
| N-Ctrl | 控制感重建 | T6 控制感重建 | 模拟经营、自动化、SLG建设 |

必须标 1 个主 N。允许 0-2 个副 N。

## 核心判断流程

### Step 1: 找出"反复行为 A"

问:玩家每天/每局/每节点绕不开什么?
- 反复对抗真人 → A1
- 反复打怪推图 → A2
- 反复登录领奖、看数字涨 → A3
- 反复调整布局/优化 → A4
- 反复试错/探索 → A5
- 反复看剧情/演出 → A6
- 反复和队友协同任务 → A7

### Step 2: 找出"成本与压力 P"

- 操作手感重要吗?→ P-Rxn
- 需要长时间投入吗?→ P-Time
- 需要思考钻研吗?→ P-Cog
- 必须有真人队友/对手吗?→ P-Soc
- 高付费才能进核心体验吗?→ P-$
- 失败惩罚强吗?→ Pr-Lose
- 跟别人比较吗?→ Pr-Cmp
- 运气主导吗?→ Pr-Rnd
- 资源/时间稀缺吗?→ Pr-Sct
- 限时压迫吗?→ Pr-Spd
- 基本无压力吗?→ Pr-Low

### Step 3: 找出"成功反馈 F"

成功瞬间玩家看到的反馈类型 → F1-F6

### Step 4: 推出"心理收益 N"

"这个反馈在玩家心理上满足了什么底层需求"
→ 严格对接人群簇 T1-T6

### Step 5: 输出置信度

- high:A/P/F/N 一致,核心反复行为清晰,N 与 F/P 强相关
- medium:A 清晰但 N 有 1 个相邻候选
- low:A 不清晰,或 N 在多个候选间摇摆

## 易混判据(boundary)

| 易混对 | 判据 |
|---|---|
| A1 vs A7 | 高光是赢对手 → A1;高光是和队友完成任务 → A7 |
| A2 vs A3 | 关键是"克服设计"(BOSS/关卡) → A2;关键是"看见数字涨" → A3 |
| A3 vs A4 | 看着系统涨(被动) → A3;主动调系统(优化) → A4 |
| A4 vs A5 | 在已知系统里优化 → A4;在未知里试错 → A5 |
| A5 vs A6 | 主动选择/试错 → A5;被动接收 → A6 |
| Pr-Low vs 其他 | 基本无压力 → Pr-Low,不与其他压力并存 |
| Pr-Cmp vs Pr-Lose | 主要因输给真人有压力 → Pr-Cmp;主要因失败惩罚 → Pr-Lose |
| N-Conf vs N-Cog | 满足来自"我变强了/我赢了" → N-Conf;满足来自"我懂了" → N-Cog |
| N-Conf vs N-Ctrl | "我变强"(向内) → N-Conf;"系统按我设计运转"(向外) → N-Ctrl |
| N-Int vs N-Bel | 关系对象是虚拟角色 → N-Int;关系对象是真人组织 → N-Bel |
| N-Adj vs N-Conf | Pr-Low + 无目标 → N-Adj;Pr-Cmp/Pr-Lose + 有目标 → N-Conf |

## 输出规则

每个样本必须:
- a_main: A1-A7 主反复行为(必填,1 个)
- a_others: 其他 A(选填,数组)
- p_cost: P-Rxn/P-Time/P-Cog/P-Soc/P-$ 中的多选(数组,至少 1 个)
- p_pressure: Pr-Lose/Pr-Cmp/Pr-Rnd/Pr-Sct/Pr-Spd/Pr-Low 中的多选(数组,至少 1 个)
- f_main: F1-F6 主反馈(必填,1 个)
- f_others: 其他 F(选填,数组)
- n_main: N-Adj/N-Conf/N-Int/N-Bel/N-Cog/N-Ctrl 主心理收益(必填,1 个)
- n_others: 副心理收益(0-2 个,数组)
- confidence: high/medium/low
- boundary_excluded: 显式排除的最相邻 N 的理由
"""


def build_prompt(samples_batch, batch_idx, total_batches):
    samples_str = "\n".join(
        f"{s['id']}. 【{s['year']}/{s['section']}】《{s['name']}》— 类型:{s['tag']};特色:{s['feature']}"
        for s in samples_batch
    )
    return f"""你是资深游戏玩法分析师。请用以下 v1.1 玩法承接行为契约规则对真实爆款样本做归类。
这是第 {batch_idx}/{total_batches} 批,共 {len(samples_batch)} 个样本。

{V11_RULES}

# 待验证样本({len(samples_batch)} 个)

{samples_str}

# 输出格式(JSON 数组,{len(samples_batch)} 个)

```json
[
  {{
    "id": 1,
    "name": "样本名",
    "a_main": "A1",
    "a_others": ["A7"],
    "p_cost": ["P-Rxn", "P-Soc", "P-Time"],
    "p_pressure": ["Pr-Lose", "Pr-Cmp"],
    "f_main": "F1",
    "f_others": ["F6"],
    "n_main": "N-Conf",
    "n_others": ["N-Bel"],
    "confidence": "high",
    "boundary_excluded": "排除 N-Bel 作主 因为高光是个人上分而非团队任务;排除 N-Cog 因为不靠规则破解"
  }}
]
```

【硬约束】
- 每个样本必须有 a_main / f_main / n_main(都是单选)
- p_cost / p_pressure 必填,至少 1 个
- confidence 是 3 个枚举之一
- 必须显式回答 boundary_excluded(与最相邻 N 的差异理由)
- 不能用品类/题材直接推 N,必须从 A/P/F 推
- Pr-Low 与其他 P-压力 互斥

只返回 JSON 数组,不要其他文字或代码块标记。"""


def parse_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text.strip())


def write_report(all_results, all_samples):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / f"validation_report_v1.1_action_{TODAY}.md"

    sample_by_id = {s["id"]: s for s in all_samples}
    n_count = {}
    a_count = {}
    f_count = {}
    confidence_count = {"high": 0, "medium": 0, "low": 0}
    p_cost_count = {}
    p_pressure_count = {}

    section_n = {}

    for r in all_results:
        n = r.get("n_main", "未知")
        a = r.get("a_main", "未知")
        f = r.get("f_main", "未知")

        n_count[n] = n_count.get(n, 0) + 1
        a_count[a] = a_count.get(a, 0) + 1
        f_count[f] = f_count.get(f, 0) + 1

        conf = r.get("confidence", "unknown")
        if conf in confidence_count:
            confidence_count[conf] += 1

        for c in r.get("p_cost", []):
            p_cost_count[c] = p_cost_count.get(c, 0) + 1
        for p in r.get("p_pressure", []):
            p_pressure_count[p] = p_pressure_count.get(p, 0) + 1

        s = sample_by_id.get(r["id"], {})
        section = s.get("section", "未知")
        section_n.setdefault(section, {})
        section_n[section][n] = section_n[section].get(n, 0) + 1

    total = len(all_results)
    high_rate = confidence_count["high"] / total * 100 if total else 0
    low_rate = confidence_count["low"] / total * 100 if total else 0
    no_n = sum(1 for r in all_results if r.get("n_main", "").startswith("无")) / total * 100 if total else 0

    lines = [
        f"# 玩法承接 v1.1 行为契约验证报告({total} 真实爆款)",
        f"",
        f"**日期**:{TODAY}",
        f"**样本数**:{total}",
        f"**模型**:DeepSeek V4 Pro",
        f"**框架**:玩法承接 = A(反复行为) × P(成本/压力) × F(成功反馈) × N(心理收益)",
        f"",
        f"## 一、验证指标",
        f"",
        f"| 指标 | 数值 | 阈值 | 状态 |",
        f"|---|---|---|---|",
        f"| 主 N 置信度 high 率 | {high_rate:.1f}% | >70% 通过 | {'✅' if high_rate > 70 else '⚠️'} |",
        f"| 主 N 置信度 low 率 | {low_rate:.1f}% | <10% 通过 | {'✅' if low_rate < 10 else '⚠️'} |",
        f"| 无 N 可归率 | {no_n:.1f}% | <10% 通过 | {'✅' if no_n < 10 else '⚠️'} |",
        f"",
        f"## 二、N 心理收益分布(对接人群簇 T1-T6)",
        f"",
        f"| N | 对应 T | 样本数 | 占比 |",
        f"|---|---|---|---|",
    ]
    n_label = {
        "N-Adj": "T1 情绪调节",
        "N-Conf": "T2 自我确认",
        "N-Int": "T3 亲密连接",
        "N-Bel": "T4 协作归属",
        "N-Cog": "T5 认知扩展",
        "N-Ctrl": "T6 控制感重建",
    }
    for nk in ["N-Adj", "N-Conf", "N-Int", "N-Bel", "N-Cog", "N-Ctrl"]:
        c = n_count.get(nk, 0)
        pct = c / total * 100 if total else 0
        lines.append(f"| {nk} | {n_label.get(nk, '—')} | {c} | {pct:.1f}% |")

    lines += [
        f"",
        f"## 三、A 反复行为分布",
        f"",
        f"| A | 样本数 | 占比 |",
        f"|---|---|---|",
    ]
    a_label = {
        "A1": "对抗真人",
        "A2": "克服 PVE 内容",
        "A3": "投入累积",
        "A4": "调整系统",
        "A5": "探索/试错",
        "A6": "见证内容",
        "A7": "协同执行",
    }
    for ak in ["A1", "A2", "A3", "A4", "A5", "A6", "A7"]:
        c = a_count.get(ak, 0)
        pct = c / total * 100 if total else 0
        lines.append(f"| {ak} {a_label.get(ak, '')} | {c} | {pct:.1f}% |")

    lines += [
        f"",
        f"## 四、F 主反馈分布",
        f"",
        f"| F | 样本数 |",
        f"|---|---|",
    ]
    f_label = {
        "F1": "击杀反馈",
        "F2": "数值膨胀",
        "F3": "系统涌现",
        "F4": "闭环达成",
        "F5": "情感见证",
        "F6": "社交认可",
    }
    for fk in ["F1", "F2", "F3", "F4", "F5", "F6"]:
        c = f_count.get(fk, 0)
        lines.append(f"| {fk} {f_label.get(fk, '')} | {c} |")

    lines += [
        f"",
        f"## 五、P-成本分布",
        f"",
        f"| P-成本 | 样本数 |",
        f"|---|---|",
    ]
    for pk in ["P-Rxn", "P-Time", "P-Cog", "P-Soc", "P-$"]:
        lines.append(f"| {pk} | {p_cost_count.get(pk, 0)} |")

    lines += [
        f"",
        f"## 六、P-压力分布",
        f"",
        f"| P-压力 | 样本数 |",
        f"|---|---|",
    ]
    for pk in ["Pr-Lose", "Pr-Cmp", "Pr-Rnd", "Pr-Sct", "Pr-Spd", "Pr-Low"]:
        lines.append(f"| {pk} | {p_pressure_count.get(pk, 0)} |")

    lines += [
        f"",
        f"## 七、置信度分布",
        f"",
        f"| 置信度 | 样本数 | 占比 |",
        f"|---|---|---|",
        f"| high | {confidence_count['high']} | {confidence_count['high']/total*100:.1f}% |",
        f"| medium | {confidence_count['medium']} | {confidence_count['medium']/total*100:.1f}% |",
        f"| low | {confidence_count['low']} | {confidence_count['low']/total*100:.1f}% |",
        f"",
        f"## 八、按平台 N 分布",
        f"",
        f"| 平台 | N 分布(前 5)|",
        f"|---|---|",
    ]
    for sec, nmap in sorted(section_n.items()):
        dist = sorted(nmap.items(), key=lambda x: -x[1])[:5]
        lines.append(f"| {sec} | " + "、".join(f"{n}({c})" for n, c in dist) + " |")

    lines += [
        f"",
        f"## 九、Low 置信度样本",
        f"",
    ]
    low_samples = [r for r in all_results if r.get("confidence") == "low"]
    if low_samples:
        for r in low_samples:
            s = sample_by_id.get(r["id"], {})
            lines.append(
                f"- **{r['id']}. 《{r['name']}》** [{s.get('year','—')}/{s.get('section','—')}] | A={r.get('a_main')} N={r.get('n_main')} | {r.get('boundary_excluded','—')}"
            )
    else:
        lines.append("无")

    lines += [
        f"",
        f"## 十、所有样本归类全表",
        f"",
        f"| ID | 年份 | 平台 | 样本 | A主 | F主 | N主 | N副 | 置信度 |",
        f"|---|---|---|---|---|---|---|---|---|",
    ]
    for r in all_results:
        s = sample_by_id.get(r["id"], {})
        n_other = "、".join(r.get("n_others", [])) or "—"
        lines.append(
            f"| {r['id']} | {s.get('year','—')} | {s.get('section','—')} | {r['name'][:18]} | {r.get('a_main','—')} | {r.get('f_main','—')} | {r.get('n_main','—')} | {n_other} | {r.get('confidence','—')} |"
        )

    lines += [f"", f"## 十一、自动判定", f""]
    if high_rate > 70 and low_rate < 10:
        verdict = "✅ v1.1 行为契约框架验证通过"
    elif high_rate > 50:
        verdict = "⚠️ v1.1 基本可用,boundary 需进一步优化"
    else:
        verdict = "❌ v1.1 需调整"
    lines.append(f"**结论**:{verdict}")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    log(f"  ✓ 写出报告:{report_path}")
    return report_path, high_rate, low_rate, no_n


def main():
    log("=" * 60)
    log("玩法承接 v1.1 行为契约验证(A/P/F/N)")
    log("=" * 60)
    provider = os.environ.get("LLM_PROVIDER", "未设置")
    log(f"LLM_PROVIDER:{provider}")
    log(f"DEEPSEEK_MODEL:{os.environ.get('DEEPSEEK_MODEL', '默认')}")

    log("\n[1/3] 加载样本...")
    samples = load_all_samples()
    log(f"  去重后:{len(samples)} 个")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    BATCH_SIZE = 20
    batches = [samples[i:i + BATCH_SIZE] for i in range(0, len(samples), BATCH_SIZE)]
    log(f"\n[2/3] 分 {len(batches)} 批,每批最多 {BATCH_SIZE} 个")

    all_results = []
    for i, batch in enumerate(batches, 1):
        log(f"\n  批次 {i}/{len(batches)}({len(batch)} 样本)")
        prompt = build_prompt(batch, i, len(batches))
        raw = call_llm_cached(prompt, f"validation_action_batch{i:03d}", max_tokens=12000)
        if not raw:
            log(f"  ❌ 批次 {i} 空响应")
            continue
        try:
            results = parse_json(raw)
            log(f"  解析 {len(results)} 个结果")
            all_results.extend(results)
        except Exception as e:
            log(f"  ❌ 批次 {i} 解析失败:{e}")
            log(f"  前 300:{raw[:300]}")

        if i < len(batches):
            time.sleep(3)

    log(f"\n[3/3] 总解析 {len(all_results)}/{len(samples)}")
    if not all_results:
        log("❌ 无结果")
        return

    report, high, low, no_n = write_report(all_results, samples)
    log("\n" + "=" * 60)
    log(f"✅ v1.1 行为契约验证完成!")
    log(f"   样本数:{len(all_results)}")
    log(f"   高置信度:{high:.1f}%")
    log(f"   低置信度:{low:.1f}%")
    log(f"   无 N 可归:{no_n:.1f}%")
    log(f"   报告:{report}")
    log("=" * 60)


if __name__ == "__main__":
    main()
