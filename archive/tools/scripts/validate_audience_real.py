#!/usr/bin/env python3
"""
人群簇 v1.0 矩阵扩大验证脚本 v2 - 从本地榜单读取真实样本

数据源：archive/资料/竞品库/爆款年度榜/2024.md / 2025.md / 2026.md
含 Steam 部分 + 微信小游戏部分（去重）

输出：归类报告 validation_report_real_samples_{date}.md
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

LLM_ROUTE = "SiliconFlow_DeepSeek_Flash"

RANKING_DIR = Path("/Users/mt/Documents/Codex/archive/资料/竞品库/爆款年度榜")

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

# ========== LLM 调用 ==========
def call_llm(prompt, max_tokens=16000, retries=4):
    """
    LLM 调用，带阶梯重试：
      - 前 3 次：短间隔重试（3s/6s/9s），覆盖偶发网络抖动
      - 第 4 次：长间隔重试（300-600s），覆盖临时限流和服务降级
    """
    return chat_text(
        prompt,
        route=LLM_ROUTE,
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

def call_llm_cached(prompt, label, max_tokens=16000):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_DIR / f"{TODAY}_{label}.txt"
    if raw_path.exists() and raw_path.stat().st_size > 100:
        log(f"  [{label}] 使用缓存")
        return raw_path.read_text(encoding="utf-8")
    raw = call_llm(prompt, max_tokens)
    if raw:
        raw_path.write_text(raw, encoding="utf-8")
    return raw

# ========== 从榜单提取样本 ==========
def extract_samples_from_md(file_path, year):
    """从年度榜单 markdown 提取游戏样本"""
    samples = []
    text = file_path.read_text(encoding="utf-8")
    current_section = None
    seen_in_file = set()

    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("## "):
            current_section = line[3:].strip()
            continue
        if not line.startswith("|") or "---" in line:
            continue
        if line.startswith("| 游戏名"):
            continue

        # 解析表格行
        cells = [c.strip() for c in line.split("|") if c.strip()]
        if len(cells) < 3:
            continue
        name, tag, feature = cells[0], cells[1], cells[2]
        if not name or name in seen_in_file:
            continue
        seen_in_file.add(name)

        samples.append({
            "year": year,
            "section": current_section or "未分类",
            "name": name,
            "tag": tag,
            "feature": feature,
        })
    return samples

def load_all_samples():
    """加载 2024/2025/2026 三个榜单的全部样本（按 name 去重）"""
    all_samples = []
    seen_names = {}  # name -> 最新出现的 sample

    for year in [2024, 2025, 2026]:
        file_path = RANKING_DIR / f"{year}.md"
        if not file_path.exists():
            log(f"  ⚠️ {file_path} 不存在，跳过")
            continue
        year_samples = extract_samples_from_md(file_path, year)
        log(f"  {year} 榜单：{len(year_samples)} 个样本")
        for s in year_samples:
            # 同名跨年保留最新年份的版本
            if s["name"] not in seen_names or seen_names[s["name"]]["year"] < s["year"]:
                seen_names[s["name"]] = s

    all_samples = list(seen_names.values())
    # 加上 id
    for i, s in enumerate(all_samples, start=1):
        s["id"] = i
    return all_samples


def stratified_sample(all_samples, target_size=230, seed=42):
    """按平台分层抽样，确保 Steam 和微信小游戏均衡覆盖"""
    import random
    random.seed(seed)

    # 按平台分组
    by_section = {}
    for s in all_samples:
        by_section.setdefault(s["section"], []).append(s)

    # 按比例分配名额
    total = len(all_samples)
    sampled = []
    for sec, items in by_section.items():
        # 按平台占比分配
        quota = round(len(items) / total * target_size)
        # 在该平台内按年份再分层（优先取较新的年份）
        items_sorted = sorted(items, key=lambda x: -x["year"])
        # 不能简单取前 N，要在每年内随机抽
        by_year = {}
        for it in items_sorted:
            by_year.setdefault(it["year"], []).append(it)

        year_quotas = {}
        for yr, year_items in by_year.items():
            year_quotas[yr] = round(len(year_items) / len(items) * quota)

        for yr, year_items in by_year.items():
            yr_quota = year_quotas[yr]
            if yr_quota >= len(year_items):
                sampled.extend(year_items)
            else:
                sampled.extend(random.sample(year_items, yr_quota))

    # 重新分配 ID
    sampled.sort(key=lambda x: (x["section"], -x["year"], x["name"]))
    for i, s in enumerate(sampled, start=1):
        s["id"] = i
    return sampled

# ========== 12 簇定义 ==========
CLUSTERS_DEF = """
| 簇 ID | 主任务 | 主承接偏好 | 核心收益 | 典型代表 |
|---|---|---|---|---|
| C01 | T1 情绪调节 | P1 强刺激覆盖 | — | 爽文/割草/爆装 |
| C02 | T1 情绪调节 | P2 情感共鸣 | — | 治愈/陪伴向 |
| C03 | T1 情绪调节 | P3 低负荷转移 | — | 消除/放置/短视频 |
| C04 | T2 自我确认 | P1 强刺激覆盖 | — | PVE 逆袭/战神向 |
| C05 | T2 自我确认 | P4 系统模拟 | Y1 竞争排名 | PVP战神/榜单 |
| C06 | T2 自我确认 | P4 系统模拟 | Y3 秩序优化 | 经济流派炫耀 |
| C07 | T3 亲密连接 | P2 情感共鸣 | — | 乙女/恋爱/角色养成 |
| C08 | T4 协作归属 | P2 情感共鸣 | — | MMO团魂/公会剧情 |
| C09 | T4 协作归属 | P4 系统模拟 | Y2 协作分工 | SLG联盟/MMO公会 |
| C10 | T5 认知扩展 | P4 系统模拟 | Y4 规则解码 | 解谜/构筑/策略 |
| C11 | T6 控制感重建 | P4 系统模拟 | Y3 秩序优化 | 模拟经营/建造 |
| C12 | T6 控制感重建 | P4 系统模拟 | Y1 竞争排名 | SLG重氪霸主 |

【作用域 boundary 判据】
- 满足感来自"我个体更强/更稀有" → 自我确认（C04/C05/C06）
- 满足感来自"我让一套系统/组织/世界按我规则运转" → 控制感重建（C11/C12）
- 主簇判断优先级：付费动机 > 留存动机 > 点击动机
- 副簇允许 0-2 个，超过 2 个标"产品定位模糊"
"""

def build_prompt(samples_batch, batch_idx, total_batches):
    samples_str = "\n".join(
        f"{s['id']}. 【{s['year']}/{s['section']}】《{s['name']}》— 类型：{s['tag']}；特色：{s['feature']}"
        for s in samples_batch
    )
    return f"""你是资深用户研究专家。请用以下"12 强簇候选 (v1.0)"对真实爆款游戏样本做归类验证。
这是第 {batch_idx}/{total_batches} 批，共 {len(samples_batch)} 个样本。

# 12 强簇定义

{CLUSTERS_DEF}

# 一级任务（6 个，互斥）

1. 情绪调节：处理焦虑、压抑、疲惫、无聊
2. 自我确认：确认我是谁、我有价值、我没掉队
3. 亲密连接：获得情感连接、被看见、被需要
4. 协作归属：在群体中有位置、有任务、被依赖
5. 认知扩展：理解世界、解码规则、满足好奇
6. 控制感重建：在不可控生活中建立可控小世界

# 主承接偏好（4 个）

- 强刺激覆盖：爽文、爆装、割草、搞笑、恐怖
- 情感共鸣：治愈、恋爱、剧情、陪伴
- 低负荷转移：消除、放置、美食、日常
- 系统模拟：SLG、经营、建造、解谜、策略

# 验证规则

1. 每个样本选 1 个**主簇**（C01-C12，或"无合适簇"）
2. 如有显著副任务，标 1-2 个**副簇**
3. **冲突标记**：归类是否勉强必须诚实标注
4. 不能拼凑：若 12 簇都不合适，必须标"无合适簇"并说明缺什么维度
5. 微信小游戏样本特别关注：是否大量集中 C03（低负荷）？还是有差异

# 待验证样本（{len(samples_batch)} 个）

{samples_str}

# 输出格式（JSON 数组，{len(samples_batch)} 个）

```json
[
  {{
    "id": 1,
    "name": "样本名",
    "audience_desc": "核心受众一句话（30字内）",
    "main_task": "协作归属",
    "main_carrier": "系统模拟",
    "system_yield": "协作分工",
    "main_cluster": "C09",
    "secondary_clusters": ["C12"],
    "fit_quality": "good/marginal/poor/none",
    "conflict_note": "归类是否勉强、与哪个簇冲突、为什么（30字内，无填'无'）",
    "missing_dim": "若 main_cluster=无合适簇，缺什么维度"
  }}
]
```

【硬约束】
- 全部样本必须有 main_cluster
- fit_quality 是 4 个枚举之一
- conflict_note 必须具体或填'无'

只返回 JSON 数组，不要其他文字或代码块标记。"""

def parse_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text.strip())

def write_report(all_results, all_samples):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / f"validation_report_real_samples_{TODAY}.md"

    sample_by_id = {s["id"]: s for s in all_samples}

    cluster_count = {}
    fit_count = {"good": 0, "marginal": 0, "poor": 0, "none": 0}
    no_cluster = []
    poor = []
    secondary_count = 0
    conflicts = []
    section_cluster = {}  # section → cluster → count
    year_cluster = {}     # year → cluster → count

    for r in all_results:
        cluster = r.get("main_cluster", "未知")
        cluster_count[cluster] = cluster_count.get(cluster, 0) + 1
        fit = r.get("fit_quality", "unknown")
        if fit in fit_count:
            fit_count[fit] += 1
        if cluster == "无合适簇":
            no_cluster.append(r)
        if fit == "poor":
            poor.append(r)
        if r.get("secondary_clusters"):
            secondary_count += 1
        cn = r.get("conflict_note", "")
        if cn and cn != "无" and len(cn) > 3:
            conflicts.append(r)

        s = sample_by_id.get(r["id"], {})
        section = s.get("section", "未知")
        year = s.get("year", 0)
        section_cluster.setdefault(section, {})
        section_cluster[section][cluster] = section_cluster[section].get(cluster, 0) + 1
        year_cluster.setdefault(year, {})
        year_cluster[year][cluster] = year_cluster[year].get(cluster, 0) + 1

    total = len(all_results)
    success = (fit_count["good"] + fit_count["marginal"]) / total * 100 if total else 0
    no_cluster_rate = fit_count["none"] / total * 100 if total else 0
    poor_rate = fit_count["poor"] / total * 100 if total else 0

    lines = [
        f"# 人群簇 v1.0 矩阵扩大验证报告（真实爆款样本）",
        f"",
        f"**日期**：{TODAY}",
        f"**样本来源**：archive/资料/竞品库/爆款年度榜/2024-2026.md（已去重）",
        f"**样本数**：{total}",
        f"**模型**：{LLM_ROUTE}",
        f"",
        f"## 一、关键指标",
        f"",
        f"| 指标 | 数值 | 判据 |",
        f"|---|---|---|",
        f"| 归类成功率（good+marginal） | {success:.1f}% | ≥85% 通过 |",
        f"| poor 质量率 | {poor_rate:.1f}% | <15% 通过 |",
        f"| 无簇可归率 | {no_cluster_rate:.1f}% | <10% 通过 |",
        f"",
        f"## 二、12 簇归类分布",
        f"",
        f"| 簇 ID | 样本数 | 占比 | 状态 |",
        f"|---|---|---|---|",
    ]
    for cid in ["C01","C02","C03","C04","C05","C06","C07","C08","C09","C10","C11","C12","无合适簇"]:
        c = cluster_count.get(cid, 0)
        pct = c / total * 100 if total else 0
        if cid == "无合适簇":
            status = "⚠️ 需关注" if c > 0 else "✅"
        else:
            status = "✅ 充足" if c >= 5 else ("⚠️ 偏少" if c > 0 else "❌ 空簇")
        lines.append(f"| {cid} | {c} | {pct:.1f}% | {status} |")

    lines += [
        f"",
        f"## 三、按平台归类分布",
        f"",
        f"| 平台 | 主要归簇分布（前 5） |",
        f"|---|---|",
    ]
    for sec, cmap in sorted(section_cluster.items()):
        dist = sorted(cmap.items(), key=lambda x: -x[1])[:5]
        dist_str = "、".join(f"{c}({n})" for c, n in dist)
        lines.append(f"| {sec} | {dist_str} |")

    lines += [
        f"",
        f"## 四、按年份归类分布",
        f"",
        f"| 年份 | 主要归簇分布（前 5） |",
        f"|---|---|",
    ]
    for year in sorted(year_cluster.keys()):
        cmap = year_cluster[year]
        dist = sorted(cmap.items(), key=lambda x: -x[1])[:5]
        dist_str = "、".join(f"{c}({n})" for c, n in dist)
        lines.append(f"| {year} | {dist_str} |")

    lines += [
        f"",
        f"## 五、无合适簇样本",
        f"",
    ]
    if no_cluster:
        for r in no_cluster:
            lines.append(f"- **{r['id']}. 《{r['name']}》**：{r.get('audience_desc','')}；缺维度：{r.get('missing_dim','')}")
    else:
        lines.append("无")

    lines += [f"", f"## 六、Poor 质量样本", f""]
    if poor:
        for r in poor:
            lines.append(f"- {r['id']} 《{r['name']}》| 主簇 {r['main_cluster']} | {r.get('conflict_note','')}")
    else:
        lines.append("无")

    lines += [
        f"",
        f"## 七、冲突清单（{len(conflicts)} 个）",
        f"",
        f"| ID | 样本 | 主簇 | 副簇 | 质量 | 冲突说明 |",
        f"|---|---|---|---|---|---|",
    ]
    for r in conflicts:
        sec = "、".join(r.get("secondary_clusters", [])) or "—"
        lines.append(f"| {r['id']} | {r['name'][:20]} | {r['main_cluster']} | {sec} | {r['fit_quality']} | {r['conflict_note']} |")

    lines += [
        f"",
        f"## 八、所有样本归类全表",
        f"",
        f"| ID | 年份 | 平台 | 样本 | 主簇 | 副簇 | 质量 |",
        f"|---|---|---|---|---|---|---|",
    ]
    for r in all_results:
        s = sample_by_id.get(r["id"], {})
        sec = "、".join(r.get("secondary_clusters", [])) or "—"
        lines.append(f"| {r['id']} | {s.get('year','—')} | {s.get('section','—')} | {r['name'][:22]} | {r['main_cluster']} | {sec} | {r['fit_quality']} |")

    lines += [f"", f"## 九、自动判定", f""]
    if success >= 85 and no_cluster_rate <= 10 and poor_rate <= 15:
        verdict = f"✅ 矩阵在 {total} 真实样本规模下仍然稳定，可保留 v1.0"
    elif success >= 70:
        verdict = "⚠️ 矩阵基本可用，需补判据或处理边界样本"
    else:
        verdict = "❌ 矩阵需调整，回到 v1.1"
    lines.append(f"**结论**：{verdict}")

    lines += [f"", f"## 十、关注点", f""]
    empty = [c for c in ["C01","C02","C03","C04","C05","C06","C07","C08","C09","C10","C11","C12"]
             if cluster_count.get(c, 0) < 5]
    if empty:
        lines.append(f"- 样本数 < 5 的簇：{', '.join(empty)}——观察是否需要合并或寻找更多样本")
    if cluster_count.get("无合适簇", 0) > 0:
        lines.append(f"- {cluster_count['无合适簇']} 个无合适簇样本，可能暴露矩阵盲区")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    log(f"  ✓ 写出报告：{report_path}")
    return report_path, success, no_cluster_rate, fit_count

def main():
    log("=" * 60)
    log("人群簇 v1.0 矩阵扩大验证（真实爆款样本）")
    log("=" * 60)
    log(f"模型：{LLM_ROUTE}")

    # 加载真实样本
    log("\n[1/3] 加载本地榜单样本...")
    full_samples = load_all_samples()
    log(f"  去重后总样本数：{len(full_samples)}")

    # 分层抽样到 230 个
    all_samples = stratified_sample(full_samples, target_size=230)
    log(f"  分层抽样后：{len(all_samples)} 个")

    # 统计
    from collections import Counter
    section_count = Counter(s["section"] for s in all_samples)
    year_count = Counter(s["year"] for s in all_samples)
    log(f"  按平台：{dict(section_count)}")
    log(f"  按年份：{dict(year_count)}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 分批
    BATCH_SIZE = 50
    batches = [all_samples[i:i+BATCH_SIZE] for i in range(0, len(all_samples), BATCH_SIZE)]
    log(f"\n[2/3] 分 {len(batches)} 批，每批最多 {BATCH_SIZE} 个")

    all_results = []
    for i, batch in enumerate(batches, start=1):
        log(f"\n  批次 {i}/{len(batches)}（{len(batch)} 样本）")
        prompt = build_prompt(batch, i, len(batches))
        raw = call_llm_cached(prompt, f"validation_real_batch{i:02d}", max_tokens=16000)
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

        # 批次间间隔，避免连续敲 API（除最后一批）
        if i < len(batches):
            import time
            time.sleep(5)

    log(f"\n[3/3] 总解析 {len(all_results)} 个结果（期望 {len(all_samples)}）")
    if not all_results:
        log("❌ 无结果")
        return

    report_path, success, no_cluster, fit = write_report(all_results, all_samples)

    log("\n" + "=" * 60)
    log(f"✅ 验证完成！")
    log(f"   样本数：{len(all_results)}")
    log(f"   归类成功率：{success:.1f}%")
    log(f"   poor 数：{fit['poor']}")
    log(f"   无簇数：{fit['none']}")
    log(f"   报告：{report_path}")
    log("=" * 60)

if __name__ == "__main__":
    main()
