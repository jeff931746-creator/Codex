#!/usr/bin/env python3
"""
玩法承接 v1.1 矩阵验证脚本
应用 9 个 CC 主簇 + R/G/LT 承接结构,用 DeepSeek V4 Pro 跑 1700+ 爆款样本。

数据源:archive/资料/竞品库/爆款年度榜/{平台}/{年份}.md
模型:DeepSeek V4 Pro(通过统一 llm_client,LLM_PROVIDER=deepseek)
输出:archive/资料/玩法承接库/_draft/validation_report_v1.1_{date}.md
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
RAW_DIR = OUTPUT_DIR / "_raw" / "v1.1"
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
# 玩法承接 v1.1 归类规则(必须严格遵守)

## 命名约定

- CC (Core Carrier):核心承接维度 — 玩法承接的底层动机
- R (Response):反馈结构 — 输入如何被系统回应
- G (Growth):成长结构 — 玩家变强的路径
- LT (Loop Time):时间结构 — 循环时长组织

## 9 个 CC 主簇

| 编号 | 名称 | 底层动机 | 典型代表 |
|---|---|---|---|
| CC1 | 战胜真人 | 我比别人强(对真人) | 王者、和平精英、传奇 |
| CC2 | 战胜内容 | 我克服了挑战(对系统/BOSS/关卡) | 黑神话、艾尔登、流放之路、暗黑 |
| CC3 | 数值膨胀 | 我变强了(纯数字/战力/境界) | 修仙放置、咸鱼之王、寻道大千、向僵尸开炮 |
| CC5 | 系统跑通 | 我让它转起来了(多元素涌现) | Factorio、文明、SLG经营、模拟经营 |
| CC6 | 规则破解 | 我理解了(解谜/构筑/解码) | 杀戮尖塔、纪念碑谷、推理 |
| CC7 | 被人看见 | 别人认可我(炫耀/输出) | 小红书穿搭、攻略输出、晒阵容(游戏作主承接罕见) |
| CC8 | 关系陪伴 | 我和谁有连接(角色/对象) | 乙女、原神角色、宠物养成、霸总短剧 |
| CC9 | 协作归属 | 我在组织里有位置 | SLG联盟、公会副本、团队协作 |
| CC10 | 情绪释放 | 我现在状态变好了(无强目标) | 消消乐、治愈剧、派对游戏、解压 |

(CC4 收集完整 已降级为副承接维度,不作主簇)

## R 反馈结构(5 个)

- R1 即时打击:输入毫秒级有打击/视觉/音效反馈(动作、射击、操作)
- R2 数值累积:输入→数字慢慢涨(放置、养成)
- R3 涌现组合:输入触发系统跑出意外结果(自动化、Roguelike、4X)
- R4 完成达成:输入推进闭环达成(关卡、解谜、消除)
- R5 见证:输入主要带来情感/剧情/视觉见证(叙事、乙女、社交炫耀)

## G 成长结构(6 个)

- G0 无成长:局内即结束,跨局无累积(派对、单局解谜)
- G1 数值膨胀:数字越来越大,体感是碾压
- G2 能力解锁:玩家驾驭系统能力提升(含角色技能 + 操作熟练 + 系统理解)
- G3 装备/资源积累:收集稀有物品
- G4 理解加深:规则/知识/世界观理解
- G5 关系深入:角色亲密度/羁绊

## LT 时间结构(4 个)

- LT1 单局闭环:一局结束体验完整
- LT2 短跨局累积:一局/天有产出,周内消化
- LT3 长跨局经营:跨周-月-赛季长期投入
- LT4 持续在场:不需结束,玩家可一直待

## CC4 收集完整 作副承接

如样本有强收集元素(图鉴/抽卡),在 secondary_cc 标注 CC4。

## CC 主簇判断核心问题(必须按顺序回答)

1. 用户为什么留下来?(留存动机)
2. 用户为什么愿意付费?(付费动机)
3. 素材钩子主要承诺什么?(点击动机)

冲突时按 2 > 1 > 3 排序。

## boundary 易混对判据

| 易混 | 判据 |
|---|---|
| CC1 vs CC9 | 高光是个人上分 → CC1;高光是团队配合 → CC9 |
| CC2 vs CC3 | 数值碾压感是核心 → CC3;关卡/BOSS挑战感是核心 → CC2 |
| CC2 vs CC6 | 卡关想"练手感/数值不够" → CC2;卡关想"机制没看明白" → CC6 |
| CC5 vs CC6 | 想"系统跑起来" → CC5;想"理解规则" → CC6 |
| CC5 vs CC9 | 主导个人经营 → CC5;在组织里有位置 → CC9 |
| CC8 vs CC10 | 关系/陪伴角色是核心 → CC8;无目标解压 → CC10 |
| CC10 vs CC1 | 派对游戏:高光是赢 → CC1;高光是欢乐打闹 → CC10 |

## 输出规则

每个样本必须:
- main_cc:9 个主簇之一(或"无合适承接")
- secondary_cc:0-2 个副承接,CC4 出现在副承接里(收集型样本)
- r/g/lt:可多选,但每个维度至少 1 个
- confidence:high/medium/low
  - high:三问一致,无相邻簇候选,boundary 排除清晰
  - medium:三问一致,1 个相邻簇候选
  - low:三问不一致,需人工复核
- boundary_excluded:显式列出排除的相邻簇 ID + 理由
"""


def build_prompt(samples_batch, batch_idx, total_batches):
    samples_str = "\n".join(
        f"{s['id']}. 【{s['year']}/{s['section']}】《{s['name']}》— 类型:{s['tag']};特色:{s['feature']}"
        for s in samples_batch
    )
    return f"""你是资深游戏玩法分析师。请用以下 v1.1 玩法承接归类规则对真实爆款样本做归类验证。
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
    "main_cc": "CC2",
    "secondary_cc": ["CC4"],
    "r": ["R1"],
    "g": ["G2", "G3"],
    "lt": ["LT1", "LT3"],
    "confidence": "high",
    "boundary_excluded": "排除 CC3 因为卡关靠练手感/装备,不是数值碾压;排除 CC6 因为不是规则解码"
  }}
]
```

【硬约束】
- 全部样本必须有 main_cc
- confidence 是 3 个枚举之一
- 必须显式回答 boundary_excluded(与最相邻簇的差异理由)
- 不能用品类/题材直接定主承接
- r/g/lt 每个维度至少 1 个值

只返回 JSON 数组,不要其他文字或代码块标记。"""


def parse_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text.strip())


def write_report(all_results, all_samples):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / f"validation_report_v1.1_{TODAY}.md"

    sample_by_id = {s["id"]: s for s in all_samples}
    cc_count = {}
    confidence_count = {"high": 0, "medium": 0, "low": 0}
    no_cluster = []
    secondary_count = 0
    r_count = {}
    g_count = {}
    lt_count = {}

    section_cc = {}
    year_cc = {}

    for r in all_results:
        cc = r.get("main_cc", "未知")
        cc_count[cc] = cc_count.get(cc, 0) + 1

        conf = r.get("confidence", "unknown")
        if conf in confidence_count:
            confidence_count[conf] += 1

        if cc == "无合适承接":
            no_cluster.append(r)

        sec = r.get("secondary_cc", [])
        if sec and len(sec) > 0:
            secondary_count += 1

        for r_val in r.get("r", []):
            r_count[r_val] = r_count.get(r_val, 0) + 1
        for g_val in r.get("g", []):
            g_count[g_val] = g_count.get(g_val, 0) + 1
        for lt_val in r.get("lt", []):
            lt_count[lt_val] = lt_count.get(lt_val, 0) + 1

        s = sample_by_id.get(r["id"], {})
        section = s.get("section", "未知")
        year = s.get("year", 0)
        section_cc.setdefault(section, {})
        section_cc[section][cc] = section_cc[section].get(cc, 0) + 1
        year_cc.setdefault(year, {})
        year_cc[year][cc] = year_cc[year].get(cc, 0) + 1

    total = len(all_results)
    high_rate = confidence_count["high"] / total * 100 if total else 0
    low_rate = confidence_count["low"] / total * 100 if total else 0
    no_cluster_rate = len(no_cluster) / total * 100 if total else 0

    lines = [
        f"# 玩法承接 v1.1 矩阵验证报告({total} 真实爆款)",
        f"",
        f"**日期**:{TODAY}",
        f"**样本数**:{total}",
        f"**模型**:DeepSeek V4 Pro(`LLM_PROVIDER=deepseek`)",
        f"",
        f"## 一、v1.1 验证指标",
        f"",
        f"| 指标 | 数值 | 阈值 | 状态 |",
        f"|---|---|---|---|",
        f"| 主簇置信度 high 率 | {high_rate:.1f}% | >70% 通过 | {'✅' if high_rate > 70 else '⚠️'} |",
        f"| 主簇置信度 low 率 | {low_rate:.1f}% | <10% 通过 | {'✅' if low_rate < 10 else '⚠️'} |",
        f"| 无簇可归率 | {no_cluster_rate:.1f}% | <10% 通过 | {'✅' if no_cluster_rate < 10 else '⚠️'} |",
        f"",
        f"## 二、9 个 CC 主簇归类分布",
        f"",
        f"| CC | 样本数 | 占比 |",
        f"|---|---|---|",
    ]
    for cid in ["CC1", "CC2", "CC3", "CC5", "CC6", "CC7", "CC8", "CC9", "CC10", "无合适承接"]:
        c = cc_count.get(cid, 0)
        pct = c / total * 100 if total else 0
        lines.append(f"| {cid} | {c} | {pct:.1f}% |")

    lines += [
        f"",
        f"## 三、置信度分布",
        f"",
        f"| 置信度 | 样本数 | 占比 |",
        f"|---|---|---|",
        f"| high | {confidence_count['high']} | {confidence_count['high']/total*100:.1f}% |",
        f"| medium | {confidence_count['medium']} | {confidence_count['medium']/total*100:.1f}% |",
        f"| low | {confidence_count['low']} | {confidence_count['low']/total*100:.1f}% |",
        f"",
        f"## 四、R/G/LT 维度分布",
        f"",
        f"### R 反馈结构",
        f"",
        f"| R | 样本数 |",
        f"|---|---|",
    ]
    for rk in ["R1", "R2", "R3", "R4", "R5"]:
        lines.append(f"| {rk} | {r_count.get(rk, 0)} |")
    lines += [f"", f"### G 成长结构", f"", f"| G | 样本数 |", f"|---|---|"]
    for gk in ["G0", "G1", "G2", "G3", "G4", "G5"]:
        lines.append(f"| {gk} | {g_count.get(gk, 0)} |")
    lines += [f"", f"### LT 时间结构", f"", f"| LT | 样本数 |", f"|---|---|"]
    for ltk in ["LT1", "LT2", "LT3", "LT4"]:
        lines.append(f"| {ltk} | {lt_count.get(ltk, 0)} |")

    lines += [
        f"",
        f"## 五、按平台 CC 分布(前 5)",
        f"",
        f"| 平台 | 主要 CC 分布 |",
        f"|---|---|",
    ]
    for sec, cmap in sorted(section_cc.items()):
        dist = sorted(cmap.items(), key=lambda x: -x[1])[:5]
        lines.append(f"| {sec} | " + "、".join(f"{c}({n})" for c, n in dist) + " |")

    lines += [
        f"",
        f"## 六、按年份 CC 分布(前 5)",
        f"",
        f"| 年份 | 主要 CC 分布 |",
        f"|---|---|",
    ]
    for year in sorted(year_cc.keys()):
        cmap = year_cc[year]
        dist = sorted(cmap.items(), key=lambda x: -x[1])[:5]
        lines.append(f"| {year} | " + "、".join(f"{c}({n})" for c, n in dist) + " |")

    lines += [f"", f"## 七、Low 置信度样本(必须人工复核)", f""]
    low_samples = [r for r in all_results if r.get("confidence") == "low"]
    if low_samples:
        for r in low_samples:
            s = sample_by_id.get(r["id"], {})
            lines.append(
                f"- **{r['id']}. 《{r['name']}》** [{s.get('year','—')}/{s.get('section','—')}] | 主 {r.get('main_cc')} | {r.get('boundary_excluded','—')}"
            )
    else:
        lines.append("无")

    lines += [
        f"",
        f"## 八、所有样本归类全表",
        f"",
        f"| ID | 年份 | 平台 | 样本 | 主CC | 副CC | R | G | LT | 置信度 |",
        f"|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in all_results:
        s = sample_by_id.get(r["id"], {})
        sec = "、".join(r.get("secondary_cc", [])) or "—"
        r_v = "、".join(r.get("r", [])) or "—"
        g_v = "、".join(r.get("g", [])) or "—"
        lt_v = "、".join(r.get("lt", [])) or "—"
        lines.append(
            f"| {r['id']} | {s.get('year','—')} | {s.get('section','—')} | {r['name'][:18]} | {r['main_cc']} | {sec} | {r_v} | {g_v} | {lt_v} | {r.get('confidence','—')} |"
        )

    lines += [f"", f"## 九、自动判定", f""]
    if high_rate > 70 and low_rate < 10 and no_cluster_rate < 10:
        verdict = "✅ v1.1 矩阵 + 9 个 CC 主簇验证通过"
    elif high_rate > 50:
        verdict = "⚠️ v1.1 基本可用,但置信度分布需优化"
    else:
        verdict = "❌ v1.1 需调整"
    lines.append(f"**结论**:{verdict}")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    log(f"  ✓ 写出报告:{report_path}")
    return report_path, high_rate, low_rate, no_cluster_rate


def main():
    log("=" * 60)
    log("玩法承接 v1.1 矩阵验证(1700+ 真实样本 + 9 CC 主簇)")
    log("=" * 60)
    provider = os.environ.get("LLM_PROVIDER", "未设置")
    log(f"LLM_PROVIDER:{provider}")
    log(f"DEEPSEEK_MODEL:{os.environ.get('DEEPSEEK_MODEL', '默认')}")

    log("\n[1/3] 加载样本...")
    samples = load_all_samples()
    log(f"  去重后:{len(samples)} 个")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    BATCH_SIZE = 20  # 比 audience 验证更小,因为 prompt 更长
    batches = [samples[i:i + BATCH_SIZE] for i in range(0, len(samples), BATCH_SIZE)]
    log(f"\n[2/3] 分 {len(batches)} 批,每批最多 {BATCH_SIZE} 个")

    all_results = []
    for i, batch in enumerate(batches, 1):
        log(f"\n  批次 {i}/{len(batches)}({len(batch)} 样本)")
        prompt = build_prompt(batch, i, len(batches))
        raw = call_llm_cached(prompt, f"validation_v1.1_batch{i:03d}", max_tokens=12000)
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

    report, high, low, no_cluster = write_report(all_results, samples)
    log("\n" + "=" * 60)
    log(f"✅ v1.1 玩法承接验证完成!")
    log(f"   样本数:{len(all_results)}")
    log(f"   高置信度:{high:.1f}%")
    log(f"   低置信度:{low:.1f}%")
    log(f"   无簇可归:{no_cluster:.1f}%")
    log(f"   报告:{report}")
    log("=" * 60)


if __name__ == "__main__":
    main()
