#!/usr/bin/env python3
"""
人群簇 v1.1 矩阵验证脚本
应用 v1.1 新归类流程：三问 + boundary 排除 + 错归筛查 + 卡关反应判据 + 置信度

数据源：archive/资料/竞品库/爆款年度榜/2024-2026.md（230 分层抽样）
模型：DeepSeek V4 Flash
输出：validation_report_v1.1_{date}.md，使用新验证指标
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

OUTPUT_DIR = Path("/Users/mt/Documents/Codex/archive/资料/人群簇库/_draft")
RAW_DIR = OUTPUT_DIR / "_raw"
TODAY = datetime.now().strftime("%Y-%m-%d")
RANKING_DIR = Path("/Users/mt/Documents/Codex/archive/资料/竞品库/爆款年度榜")

MODEL = os.environ.get("DEEPSEEK_FLASH_MODEL", "deepseek-ai/DeepSeek-V4-Flash")

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

# ========== LLM 调用（v1.1 优化：阶梯重试，最后一次 5-10 分钟）==========
def call_llm(prompt, max_tokens=18000, retries=4):
    return chat_text(
        prompt,
        model=MODEL,
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

# ========== 加载样本（适配新结构：{平台}/{年份}.md）==========
def extract_samples_from_md(file_path, year, section):
    """从单平台单年份的 markdown 提取样本"""
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
        samples.append({"year": year, "section": section,
                        "name": name, "tag": tag, "feature": feature})
    return samples

def load_all_samples():
    """加载 {平台}/{年份}.md 结构的所有样本，按 name 去重"""
    seen = {}
    # 平台目录列表
    platforms = ["Steam", "微信小游戏", "手游", "任天堂"]
    for platform in platforms:
        platform_dir = RANKING_DIR / platform
        if not platform_dir.exists():
            log(f"  ⚠️ {platform_dir} 不存在")
            continue
        for year in [2024, 2025, 2026]:
            fp = platform_dir / f"{year}.md"
            if not fp.exists():
                continue
            year_samples = extract_samples_from_md(fp, year, platform)
            log(f"  {platform}/{year}: {len(year_samples)} 个")
            for s in year_samples:
                # 同名跨年保留最新版本
                if s["name"] not in seen or seen[s["name"]]["year"] < s["year"]:
                    seen[s["name"]] = s
    samples = list(seen.values())
    for i, s in enumerate(samples, 1):
        s["id"] = i
    return samples

def stratified_sample(all_samples, target=230, seed=42):
    import random
    random.seed(seed)
    by_section = {}
    for s in all_samples:
        by_section.setdefault(s["section"], []).append(s)
    total = len(all_samples)
    sampled = []
    for sec, items in by_section.items():
        quota = round(len(items) / total * target)
        by_year = {}
        for it in items:
            by_year.setdefault(it["year"], []).append(it)
        year_quotas = {y: round(len(v) / len(items) * quota) for y, v in by_year.items()}
        for y, items_y in by_year.items():
            yq = year_quotas[y]
            if yq >= len(items_y):
                sampled.extend(items_y)
            else:
                sampled.extend(random.sample(items_y, yq))
    sampled.sort(key=lambda x: (x["section"], -x["year"], x["name"]))
    for i, s in enumerate(sampled, 1):
        s["id"] = i
    return sampled

# ========== v1.1 完整 Prompt（嵌入新规则）==========
V11_RULES = """
# v1.1 归类规则（必须严格遵守）

## 12 簇定义

| 簇 ID | 主任务 | 主承接 | 系统收益 | 典型代表 |
|---|---|---|---|---|
| C01 | T1 情绪调节 | P1 强刺激覆盖 | — | 爽文/割草/爆装/恐怖 |
| C02 | T1 情绪调节 | P2 情感共鸣 | — | 治愈/陪伴向 |
| C03 | T1 情绪调节 | P3 低负荷转移 | — | 真消除/找茬/合成 |
| C04 | T2 自我确认 | P1 强刺激覆盖 | — | PVE 逆袭/战神向（含 A 操作型/B 刷宝型/C 数值碾压型）|
| C05 | T2 自我确认 | P4 系统模拟 | Y1 竞争排名 | PVP战神/榜单 |
| C06 | T2 自我确认 | P4 系统模拟 | Y3 秩序优化 | 流派炫耀（游戏作主簇罕见）|
| C07 | T3 亲密连接 | P2 情感共鸣 | — | 乙女/恋爱/角色养成 |
| C08 | T4 协作归属 | P2 情感共鸣 | — | MMO团魂/公会剧情 |
| C09 | T4 协作归属 | P4 系统模拟 | Y2 协作分工 | SLG联盟/MMO公会 |
| C10 | T5 认知扩展 | P4 系统模拟 | Y4 规则解码 | 解谜/构筑/策略 |
| C11 | T6 控制感重建 | P4 系统模拟 | Y3 秩序优化 | 模拟经营/建造 |
| C12 | T6 控制感重建 | P4 系统模拟 | Y1 竞争排名 | SLG重氪霸主 |
| T7-candidate | 习惯维持/仪式延续 | — | — | 棋牌/麻将（候选状态）|

## 完整归类流程（必须按顺序执行）

### Step 1: 三问判主任务
- 用户主要为什么留下？
- 用户主要为什么付费/持续投入？
- 素材承诺与真实留存是否一致？（不一致时按留存）

**硬规则**：点击/品类/题材/操作强度都不能直接定主簇

### Step 2: 判承接偏好
P1 强刺激覆盖 / P2 情感共鸣 / P3 低负荷转移 / P4 系统模拟（再分 Y1/Y2/Y3/Y4）

### Step 3: 候选簇定位（按 T × P 落入）

### Step 4: boundary 排除（13 对硬判据）

| 边界 | 判据 |
|---|---|
| C01 vs C03 | 高唤醒短刺激 → C01；低唤醒注意力转移 → C03。跑酷/消除/找茬默认 C03，除非核心是爆炸/暴力/恐怖/速度压迫 |
| C01 vs C10 | 恐怖核心是"被吓/释放紧张" → C01；恐怖核心是"探索未知/解谜" → C10 |
| C03 vs C04-C | 低操作不等于 C03。长期目标是战力/境界/数值膨胀/碾压别人 → C04；只是消磨时间/重复轻反馈 → C03 |
| C04 vs C05 | 战胜内容/怪/关卡 → C04；战胜真人/排名/竞技 → C05。PvP 撤离/竞技/排位优先 C05 |
| C04 vs C05 (PvPvE) | 用户高光时刻是"PvP干掉真人" → C05；高光是"刷到稀有装备" → C04-B |
| C04 vs C10 | ARPG 默认不归 C10。构筑通向"我变强了，下一关需要更强的我" → C04；构筑通向"我破解了规则"（解读完整后退场） → C10 |
| C04 vs C11 | 修仙若核心是境界压制/战力膨胀 → C04；若核心是经营门派/资源秩序/生产链 → C11 |
| C07 vs C08 | C07 是我和角色的亲密；C08 是我和团体的归属。武侠 MMO 不因有剧情就归 C07 |
| C08 vs C09 | C08 是团魂/陪伴/情义；C09 是职责/分工/组织任务。临时合作和工具协作优先 C09 |
| C10 vs C11 | C10 是破解规则；C11 是优化系统。文明/4X 满足来自"理解规则" → C10；满足来自"经营起来" → C11 |
| C05 vs C12 | "我个体更强" → C05；"我让服务器按我规则运转" → C12 |
| C06 vs C11 | "我比别人更懂这个系统"（向外炫耀） → C06；"我让世界井然有序"（向内自洽） → C11 |
| C09 vs C12 | "我有位置被组织依赖" → C09；"我让组织按我规则运转" → C12 |

### Step 5: 错归筛查（针对 C03/C04/C10 历史大簇）

#### C03 错归筛查（必须显式排除）
1. 主循环是否显式围绕战力/境界/装备/推图卡点/付费加速？
   - 是 → 排除 C03，归 C04（标 C04-C 数值碾压）
2. 是否承载固定社交/仪式关系（熟人局/固定打卡）？
   - 是 → 标 T7-candidate，不归 C03
3. 都"否" → 真 C03

#### C10 强制排除 checklist（必须显式回答四个）
1. 主要靠战斗成长？是 → C04
2. 主要靠经营秩序？是 → C11
3. 主要靠竞技胜负？是 → C05
4. 主要靠剧情亲密/情感？是 → C07/C02

**复合产品的"主要靠"判定** —— 用"用户卡关时的本能反应"反推：
- 卡关想"我等级不够，去刷怪/装备" → C04
- 卡关想"这关有什么机制我没想到？" → C10
- 卡关想"我经济没建好/资源不够" → C11
- 卡关想"对手太强，得练手感/上分" → C05
- 卡关想"我想看主角和 NPC 关系" → C07

四个都"否"，且核心快感来自"理解规则/破解谜题/构筑有效解/掌握复杂系统" → 才进 C10

#### C04 错归筛查
1. 是否主要靠 PvP 战胜真人？是 → C05
2. 是否主要靠经营秩序？是 → C11
3. 是否主要靠规则解码（构筑后退场）？是 → C10
4. 都"否" → 真 C04

### Step 6: 输出格式（含置信度）

每个样本输出：
- main_cluster: C01-C12 / T7-candidate / 无合适簇
- secondary_clusters: [C-XX, C-YY] (0-2 个)
- main_task: T1-T6 / T7-candidate
- main_carrier: P1-P4
- system_yield: Y1-Y4 (仅 P4)
- confidence: high / medium / low
  - high: 三问一致，无相邻簇候选，错归筛查通过
  - medium: 三问一致，1 个相邻簇候选
  - low: 三问不一致，需人工复核
- boundary_excluded: 列出排除的相邻簇 ID 和理由
- error_check_passed: true/false（是否通过错归筛查）
- error_check_note: 错归筛查的关键判断说明
"""

def build_prompt(samples_batch, batch_idx, total_batches):
    samples_str = "\n".join(
        f"{s['id']}. 【{s['year']}/{s['section']}】《{s['name']}》— 类型：{s['tag']}；特色：{s['feature']}"
        for s in samples_batch
    )
    return f"""你是资深用户研究专家。请用以下 v1.1 归类规则对真实爆款样本做归类验证。
这是第 {batch_idx}/{total_batches} 批，共 {len(samples_batch)} 个样本。

{V11_RULES}

# 待验证样本（{len(samples_batch)} 个）

{samples_str}

# 输出格式（JSON 数组，{len(samples_batch)} 个）

```json
[
  {{
    "id": 1,
    "name": "样本名",
    "audience_desc": "核心受众一句话（30字内）",
    "main_task": "T2",
    "main_carrier": "P1",
    "system_yield": "—",
    "main_cluster": "C04",
    "secondary_clusters": ["C10"],
    "confidence": "high/medium/low",
    "boundary_excluded": "排除 C10 因为构筑通向'下一关更强'，不是'破解规则'",
    "error_check_passed": true,
    "error_check_note": "通过 C04 错归筛查：非 PvP/经营/纯解码"
  }}
]
```

【硬约束】
- 全部样本必须有 main_cluster
- confidence 是 3 个枚举之一
- 必须显式回答 boundary_excluded（与最相邻簇的差异理由）
- C03/C04/C10 必须填 error_check_passed
- 不能用品类/题材/操作强度直接定主簇

只返回 JSON 数组，不要其他文字或代码块标记。"""

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
    cluster_count = {}
    confidence_count = {"high": 0, "medium": 0, "low": 0}
    error_check_failed = []
    no_cluster = []
    secondary_count = 0
    multi_secondary = []

    section_cluster = {}
    year_cluster = {}

    for r in all_results:
        cluster = r.get("main_cluster", "未知")
        cluster_count[cluster] = cluster_count.get(cluster, 0) + 1

        conf = r.get("confidence", "unknown")
        if conf in confidence_count:
            confidence_count[conf] += 1

        if cluster == "无合适簇":
            no_cluster.append(r)

        # 错归筛查失败：仅当样本归到 C03/C04/C10 且筛查未通过时才算
        # 非历史大簇的样本 error_check_passed=false 是字段误标，不计入
        is_historic_big = cluster in ("C03", "C04", "C10")
        if is_historic_big and r.get("error_check_passed") is False:
            error_check_failed.append(r)

        sec = r.get("secondary_clusters", [])
        if sec and len(sec) > 0:
            secondary_count += 1
        if sec and len(sec) > 2:
            multi_secondary.append(r)

        s = sample_by_id.get(r["id"], {})
        section = s.get("section", "未知")
        year = s.get("year", 0)
        section_cluster.setdefault(section, {})
        section_cluster[section][cluster] = section_cluster[section].get(cluster, 0) + 1
        year_cluster.setdefault(year, {})
        year_cluster[year][cluster] = year_cluster[year].get(cluster, 0) + 1

    total = len(all_results)
    high_rate = confidence_count["high"] / total * 100 if total else 0
    low_rate = confidence_count["low"] / total * 100 if total else 0
    no_cluster_rate = len(no_cluster) / total * 100 if total else 0
    multi_sec_rate = len(multi_secondary) / total * 100 if total else 0
    error_fail_rate = len(error_check_failed) / total * 100 if total else 0

    lines = [
        f"# 人群簇 v1.1 矩阵验证报告（230 真实爆款 + 新规则）",
        f"",
        f"**日期**：{TODAY}",
        f"**样本数**：{total}",
        f"**模型**：{MODEL}",
        f"",
        f"## 一、v1.1 新验证指标",
        f"",
        f"| 指标 | 数值 | 阈值 | 状态 |",
        f"|---|---|---|---|",
        f"| 主簇置信度 high 率 | {high_rate:.1f}% | >70% 通过 | {'✅' if high_rate > 70 else '⚠️'} |",
        f"| 主簇置信度 low 率 | {low_rate:.1f}% | <10% 通过 | {'✅' if low_rate < 10 else '⚠️'} |",
        f"| 无簇可归率 | {no_cluster_rate:.1f}% | <10% 通过 | {'✅' if no_cluster_rate < 10 else '⚠️'} |",
        f"| 错归筛查失败率 | {error_fail_rate:.1f}% | <15% 通过 | {'✅' if error_fail_rate < 15 else '⚠️'} |",
        f"| 副簇 > 2 个率 | {multi_sec_rate:.1f}% | <10% 通过 | {'✅' if multi_sec_rate < 10 else '⚠️'} |",
        f"",
        f"## 二、12 簇 + T7-candidate 归类分布",
        f"",
        f"| 簇 ID | 样本数 | 占比 | 与 v1.0 对比 |",
        f"|---|---|---|---|",
    ]
    # v1.0 对比基准（来自上次跑的 230 验证）
    v10_baseline = {"C01":28,"C02":4,"C03":27,"C04":46,"C05":14,"C06":0,"C07":11,"C08":8,"C09":13,"C10":50,"C11":28,"C12":1}
    for cid in ["C01","C02","C03","C04","C05","C06","C07","C08","C09","C10","C11","C12","T7-candidate","无合适簇"]:
        c = cluster_count.get(cid, 0)
        pct = c / total * 100 if total else 0
        v10 = v10_baseline.get(cid, "—")
        diff = ""
        if isinstance(v10, int):
            delta = c - v10
            diff = f"{v10} → {c} ({'+' if delta >= 0 else ''}{delta})"
        lines.append(f"| {cid} | {c} | {pct:.1f}% | {diff} |")

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
        f"## 四、按平台归类分布",
        f"",
        f"| 平台 | 主要归簇分布（前 5）|",
        f"|---|---|",
    ]
    for sec, cmap in sorted(section_cluster.items()):
        dist = sorted(cmap.items(), key=lambda x: -x[1])[:5]
        lines.append(f"| {sec} | " + "、".join(f"{c}({n})" for c, n in dist) + " |")

    lines += [
        f"",
        f"## 五、按年份归类分布",
        f"",
        f"| 年份 | 主要归簇分布（前 5）|",
        f"|---|---|",
    ]
    for year in sorted(year_cluster.keys()):
        cmap = year_cluster[year]
        dist = sorted(cmap.items(), key=lambda x: -x[1])[:5]
        lines.append(f"| {year} | " + "、".join(f"{c}({n})" for c, n in dist) + " |")

    lines += [
        f"",
        f"## 六、Low 置信度样本（必须人工复核）",
        f"",
    ]
    low_samples = [r for r in all_results if r.get("confidence") == "low"]
    if low_samples:
        for r in low_samples:
            s = sample_by_id.get(r["id"], {})
            lines.append(f"- **{r['id']}. 《{r['name']}》** [{s.get('year','—')}/{s.get('section','—')}] | 主簇 {r.get('main_cluster')} | {r.get('boundary_excluded','—')}")
    else:
        lines.append("无")

    lines += [
        f"",
        f"## 七、错归筛查失败样本",
        f"",
    ]
    if error_check_failed:
        for r in error_check_failed:
            lines.append(f"- {r['id']} 《{r['name']}》| {r.get('error_check_note','—')}")
    else:
        lines.append("无")

    lines += [
        f"",
        f"## 八、所有样本归类全表",
        f"",
        f"| ID | 年份 | 平台 | 样本 | 主簇 | 副簇 | 置信度 | boundary 排除 |",
        f"|---|---|---|---|---|---|---|---|",
    ]
    for r in all_results:
        s = sample_by_id.get(r["id"], {})
        sec = "、".join(r.get("secondary_clusters", [])) or "—"
        be = (r.get("boundary_excluded", "") or "")[:40]
        lines.append(f"| {r['id']} | {s.get('year','—')} | {s.get('section','—')} | {r['name'][:18]} | {r['main_cluster']} | {sec} | {r.get('confidence','—')} | {be} |")

    lines += [f"", f"## 九、自动判定（v1.1 新指标）", f""]
    if high_rate > 70 and low_rate < 10 and no_cluster_rate < 10 and error_fail_rate < 15:
        verdict = "✅ v1.1 矩阵 + 新规则验证通过"
    elif high_rate > 50:
        verdict = "⚠️ v1.1 基本可用，但置信度分布需进一步优化"
    else:
        verdict = "❌ v1.1 需调整，回到 v1.2"
    lines.append(f"**结论**：{verdict}")

    lines += [f"", f"## 十、v1.0 vs v1.1 对比观察", f""]
    lines.append(f"- C04 占比: 20.0% (v1.0) → {cluster_count.get('C04', 0)/total*100:.1f}% (v1.1)")
    lines.append(f"- C10 占比: 21.7% (v1.0) → {cluster_count.get('C10', 0)/total*100:.1f}% (v1.1)")
    lines.append(f"- C03 占比: 11.7% (v1.0) → {cluster_count.get('C03', 0)/total*100:.1f}% (v1.1)")
    lines.append(f"- T7-candidate（v1.1 新增）：{cluster_count.get('T7-candidate', 0)} 个")
    lines.append(f"- C12 提升: 1 (v1.0) → {cluster_count.get('C12', 0)} (v1.1)")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    log(f"  ✓ 写出报告：{report_path}")
    return report_path, high_rate, low_rate, no_cluster_rate

def main():
    log("=" * 60)
    log("人群簇 v1.1 矩阵验证（230 真实样本 + 新规则）")
    log("=" * 60)
    log(f"模型：{MODEL}")

    log("\n[1/3] 加载样本...")
    full = load_all_samples()
    samples = stratified_sample(full, target=230)
    log(f"  抽样后：{len(samples)} 个")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    BATCH_SIZE = 30  # 8 批，每批更小避免超时
    batches = [samples[i:i+BATCH_SIZE] for i in range(0, len(samples), BATCH_SIZE)]
    log(f"\n[2/3] 分 {len(batches)} 批，每批最多 {BATCH_SIZE} 个")

    all_results = []
    for i, batch in enumerate(batches, 1):
        log(f"\n  批次 {i}/{len(batches)}（{len(batch)} 样本）")
        prompt = build_prompt(batch, i, len(batches))
        raw = call_llm_cached(prompt, f"validation_v1.1_b30_batch{i:02d}", max_tokens=12000)
        if not raw:
            log(f"  ❌ 批次 {i} 空响应")
            continue
        try:
            results = parse_json(raw)
            log(f"  解析 {len(results)} 个结果")
            all_results.extend(results)
        except Exception as e:
            log(f"  ❌ 批次 {i} 解析失败：{e}")
            log(f"  前 300：{raw[:300]}")

        if i < len(batches):
            import time
            time.sleep(5)

    log(f"\n[3/3] 总解析 {len(all_results)}/{len(samples)}")
    if not all_results:
        log("❌ 无结果")
        return

    report, high, low, no_cluster = write_report(all_results, samples)
    log("\n" + "=" * 60)
    log(f"✅ v1.1 验证完成！")
    log(f"   样本数：{len(all_results)}")
    log(f"   高置信度：{high:.1f}%")
    log(f"   低置信度：{low:.1f}%")
    log(f"   无簇可归：{no_cluster:.1f}%")
    log(f"   报告：{report}")
    log("=" * 60)

if __name__ == "__main__":
    main()
