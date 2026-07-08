#!/usr/bin/env python3
"""
任天堂平台游戏题材库构建脚本

覆盖范围:
  - 2000-2014: 任天堂掌机/主机重要平台(NDS / GBA / GBC / N64 / GameCube / Wii / 3DS 早期)
  - 2017-2026: Switch 完整生命周期

route: DeepSeek_Official_Pro
并发: 5 workers
预计产出: ~2400 款游戏

输出: archive/资料/游戏题材库/

启动:
  set -a
  source "$HOME/Library/Application Support/FeishuCodexBridge/bridge/.env"
  set +a
  export LLM_ROUTE=DeepSeek_Official_Pro
  python3 archive/tools/scripts/build_game_theme_library.py
"""
import concurrent.futures
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

from archive.tools.lib.llm_client import chat_text
from archive.tools.lib.llm_common import RetryPolicy

# ========== 配置 ==========
OUTPUT_ROOT = Path(os.environ.get(
    "GAME_THEME_LIBRARY_ROOT",
    "/Users/mt/Documents/Codex/archive/资料/游戏题材库"
))
RAW_DIR = OUTPUT_ROOT / "_raw"
CLUSTER_DIR = OUTPUT_ROOT / "题材聚类"
TODAY = datetime.now().strftime("%Y-%m-%d")

LLM_ROUTE = "DeepSeek_Official_Pro"

# 并发配置
DISCOVERY_WORKERS = 5
ANALYSIS_WORKERS = 5

# 平台生命周期(避免空跑)
PLATFORMS = [
    # name, full_name, year_range, batches_per_year, per_batch
    {"name": "GBA",         "full_name": "Game Boy Advance",        "years": list(range(2001, 2008)), "batches": 3, "per_batch": 15},  # 7年 × 45 = 315
    {"name": "GameCube",    "full_name": "Nintendo GameCube",       "years": list(range(2001, 2007)), "batches": 2, "per_batch": 15},  # 6年 × 30 = 180
    {"name": "NDS",         "full_name": "Nintendo DS",             "years": list(range(2004, 2014)), "batches": 4, "per_batch": 15},  # 10年 × 60 = 600
    {"name": "Wii",         "full_name": "Nintendo Wii",            "years": list(range(2006, 2013)), "batches": 3, "per_batch": 15},  # 7年 × 45 = 315
    {"name": "3DS",         "full_name": "Nintendo 3DS",            "years": list(range(2011, 2015)), "batches": 3, "per_batch": 15},  # 4年 × 45 = 180
    {"name": "Wii_U",       "full_name": "Nintendo Wii U",          "years": list(range(2012, 2015)), "batches": 2, "per_batch": 15},  # 3年 × 30 = 90
    {"name": "Switch",      "full_name": "Nintendo Switch",         "years": list(range(2017, 2027)), "batches": 5, "per_batch": 20},  # 10年 × 100 = 1000
]
# 预计总量: ~2680 款

# ========== 日志 ==========
def log(msg: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)

# ========== LLM 调用 ==========
def call_llm(prompt: str, max_tokens: int = 8000, retries: int = 3) -> str:
    return chat_text(
        prompt,
        route=LLM_ROUTE,
        max_tokens=max_tokens,
        temperature=0.3,
        timeout=240,
        retry_policy=RetryPolicy(retries=retries, base_delay=3.0),
        logger=log,
        return_empty_on_error=True,
    )

def _parse_json(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    text = text.strip()
    text = re.sub(r"\}\s*\{", "},{", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # 尝试抓零散 JSON 对象
        objects = re.findall(r'\{[^{}]+\}', text, re.DOTALL)
        results = []
        for obj in objects:
            obj = re.sub(r",\s*([}\]])", r"\1", obj)
            try:
                results.append(json.loads(obj))
            except Exception:
                pass
        if results:
            return results
        raise

def call_llm_json(prompt: str, label: str, max_tokens: int = 8000):
    """调用 LLM 并解析 JSON; 已有 raw 文件则跳过(幂等)"""
    raw_path = RAW_DIR / f"{TODAY}_{label}.txt"
    if raw_path.exists() and raw_path.stat().st_size > 100:
        text = raw_path.read_text(encoding="utf-8")
    else:
        text = call_llm(prompt, max_tokens=max_tokens)
        if text:
            raw_path.write_text(text, encoding="utf-8")
        else:
            log(f"  [WARN] {label} 返回空")
            return []
    try:
        result = _parse_json(text)
        if isinstance(result, list):
            return result
        if isinstance(result, dict):
            for v in result.values():
                if isinstance(v, list):
                    return v
            return [result]
        return []
    except Exception as e:
        log(f"  [ERR] {label} JSON解析失败: {e}")
        return []

# ========== Phase 1: 发现 ==========
def _year_note(year: int) -> str:
    if year >= 2025:
        return "(2025-2026年知识可能不完整,已知几款就列几款,不凑数)"
    if year >= 2023:
        return "(2023-2024年知识可能不完整)"
    return "(尽量列足代表作)"

_GAME_DISCOVERY_FIELDS = """- "title": 中文名(无则用常用英文名)
- "original_title": 原名(英文/日文)
- "year": 发售年份(整数)
- "platform": 主要发售平台(如"NDS"、"Switch"、"Wii"、"GBA"等)
- "developer": 开发商(简短)
- "publisher": 发行商(简短,若与开发商相同可省略写"同上")
- "genre": 游戏品类(如"RPG"、"动作"、"模拟经营"、"塔防"、"解谜"等)
- "brief": 一句话核心题材(20字以内,描述题材壳+核心玩法,如"魔法学院战斗冒险"、"末世废土生存建造")"""

def make_discovery_queries() -> list:
    """按各平台实际生命周期生成 query,避免年份-平台错配"""
    queries = []

    for plat in PLATFORMS:
        name = plat["name"]
        full = plat["full_name"]
        for y in plat["years"]:
            note = _year_note(y)
            per_batch = plat["per_batch"]
            for batch in range(1, plat["batches"] + 1):
                start_rank = (batch - 1) * per_batch + 1
                end_rank = batch * per_batch
                queries.append({
                    "key": f"{name}_y{y}_b{batch}",
                    "merge_as": name,
                    "year": y,
                    "platform": name,
                    "max_tokens": 2800,
                    "prompt": (
                        f"请列举{y}年在 {full}({name}) 平台发售的、综合影响力(销量+口碑+IP延续性)排名第{start_rank}-{end_rank}的游戏作品,共{per_batch}款{note}。\n"
                        f"硬要求:\n"
                        f"1. 必须是该年首发于 {name} 平台或同时登陆 {name} 的作品,不要列其他平台\n"
                        f"2. 优先列出题材独特/玩法创新/有续作影响的作品\n"
                        f"3. 跳过纯衍生小游戏合集、纯运动竞速类、纯赌博类\n"
                        f"4. 如果该年该平台的代表作不足{per_batch}款,只列已知的,不要凑数(返回少于{per_batch}条是允许的)\n"
                        f"以JSON数组返回,每个条目:\n{_GAME_DISCOVERY_FIELDS}\n"
                        f"只返回JSON数组,不要其他文字。"
                    )
                })
    return queries

DISCOVERY_QUERIES = make_discovery_queries()

def run_discovery() -> tuple[dict, list]:
    """Phase 1: 并发发现游戏列表"""
    log(f"=== Phase 1: Discovery ({len(DISCOVERY_QUERIES)} 条查询, 并发 {DISCOVERY_WORKERS}) ===")
    merged: dict[str, list] = {}
    failed_keys: list[str] = []
    done = 0

    def fetch_one(q):
        key = q["key"]
        mt = q.get("max_tokens", 3000)
        items = call_llm_json(q["prompt"], f"discovery_{key}", max_tokens=mt)
        for item in items:
            item.setdefault("year", q.get("year", 0))
            item.setdefault("platform", q.get("platform", "未知"))
        return q["merge_as"], items, key

    with concurrent.futures.ThreadPoolExecutor(max_workers=DISCOVERY_WORKERS) as executor:
        futures = [executor.submit(fetch_one, q) for q in DISCOVERY_QUERIES]
        for future in concurrent.futures.as_completed(futures):
            try:
                merge_as, items, key = future.result()
            except Exception as e:
                log(f"  [ERR] discovery future failed: {e}")
                continue
            if not items:
                failed_keys.append(key)
            merged.setdefault(merge_as, []).extend(items)
            done += 1
            if done % 20 == 0 or done == len(DISCOVERY_QUERIES):
                total = sum(len(v) for v in merged.values())
                log(f"  进度 {done}/{len(DISCOVERY_QUERIES)},已发现 {total} 款")

    for cat, works in merged.items():
        log(f"  {cat}: {len(works)} 款")
    return merged, failed_keys

# ========== Phase 2: 分析 ==========
def build_analysis_prompt(works_batch: list) -> str:
    works_str = "\n".join(
        f"{i+1}. 《{w.get('title', '?')}》"
        f"({w.get('year', '?')}年,{w.get('platform', '?')},{w.get('developer','')}发行,品类:{w.get('genre','')},简介:{w.get('brief', '')})"
        for i, w in enumerate(works_batch)
    )
    return f"""请对以下{len(works_batch)}款任天堂平台游戏作品,从"为当代手游/中重度游戏立项提供题材参考"角度分析。

作品列表:
{works_str}

对每款游戏以JSON数组返回分析(数组长度必须与输入相同):
- "title": 与输入相同的标题
- "theme_env": 题材环境/时代(20字以内,如"日本江户时代"、"架空魔法学院"、"末日地球")
- "theme_culture": 文化范式或战斗体系(25字以内,如"东方剑术+幕府文化"、"宝可梦捕捉+培育体系")
- "theme_narrative": 叙事核心(15字以内,如"成长冒险"、"末世求生"、"权谋复仇")
- "emotion_hooks": 核心情绪钩子(数组,1-3个,如["收集成就","战略博弈"])
- "instinct_calibration": 用户对该题材的本能调教来源(数组,1-3个,如"日式童年回忆"、"宝可梦动画粉丝群")
- "psych_tasks": 激活的玩家心理任务(数组,3-5个,如"收集养成"、"探索发现"、"战斗碾压"、"建造经营"、"社交协作")
- "platform_release": 平台/发行年(一句话,如"Switch 2017首发")
- "developer_pub": 开发/发行(一句话)
- "sales_tier": 销量量级(枚举: "百万级"/"千万级"/"五百万级"/"小众"/"未知")
- "modern_adaptation": 已被买量或中重度手游借鉴情况(数组,如["已被手游改编《xxx》"、"题材被买量市场反复套用"、"暂无中重度借鉴"])
- "acquisition_score": 获量能力(整数1-5)
- "acquisition_reason": 获量得分理由(15字以内)
- "roi_score": ROI承接能力(整数1-5)
- "roi_reason": ROI得分理由(15字以内)
- "gameplay_carrier": 推荐当代玩法载体(数组,如["卡牌养成"、"放置RPG"、"SLG策略"])
- "exploration_value": 是否有未开发题材方向(枚举: "高潜未开发"/"部分开发"/"已饱和"/"难复刻")
- "risk_tags": 风险标签(数组,如["IP版权重"、"题材偏小众"、"美术成本高"])

评分标准:
获量能力(1-5): 用当代中重度立项视角评估。5=题材本能调教强且未充分被现代手游开发; 1=题材小众或时代局限难以做素材
ROI承接(1-5): 评估该题材在中重度玩法承接下的付费深度潜力。5=有完整养成/收集/对抗体系; 1=纯叙事难承接长线

只返回JSON数组,不要其他文字或代码块标记。"""

def _calc_quadrant(acq: int, roi: int) -> str:
    a = "高" if acq >= 4 else ("中" if acq >= 3 else "低")
    r = "高" if roi >= 4 else ("中" if roi >= 3 else "低")
    return f"获量{a}×ROI{r}"

def analyze_batch(batch: list, batch_idx: int) -> list:
    prompt = build_analysis_prompt(batch)
    items = call_llm_json(prompt, f"analysis_batch{batch_idx:03d}", max_tokens=8000)
    for item in items:
        acq = item.get("acquisition_score", 3)
        roi = item.get("roi_score", 3)
        item["quadrant"] = _calc_quadrant(acq, roi)
    return items

def run_analysis(discovery: dict) -> tuple[dict, list]:
    log("=== Phase 2: Analysis ===")

    all_works = []
    for key, items in discovery.items():
        for item in items:
            item["_category"] = key
            all_works.append(item)

    log(f"  总作品数: {len(all_works)}")

    BATCH_SIZE = 8
    batches = [all_works[i:i+BATCH_SIZE] for i in range(0, len(all_works), BATCH_SIZE)]
    log(f"  分 {len(batches)} 批, 每批 {BATCH_SIZE} 款, 并发 {ANALYSIS_WORKERS}")

    failed_batches: list[int] = []

    def process_batch(args):
        idx, batch = args
        results = analyze_batch(batch, idx)
        if not results:
            return len(batch), idx
        for work, result in zip(batch, results):
            work.update(result)
            acq = work.get("acquisition_score", 0)
            roi = work.get("roi_score", 0)
            if acq and roi:
                work["quadrant"] = _calc_quadrant(acq, roi)
        return len(batch), None

    done = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=ANALYSIS_WORKERS) as executor:
        futures = {executor.submit(process_batch, (i, b)): i for i, b in enumerate(batches)}
        for future in concurrent.futures.as_completed(futures):
            try:
                count, failed_idx = future.result()
            except Exception as e:
                log(f"  [ERR] analysis future: {e}")
                continue
            if failed_idx is not None:
                failed_batches.append(failed_idx)
            done += count
            if done % 80 == 0 or done == len(all_works):
                log(f"  进度 {done}/{len(all_works)}")

    categorized = {}
    for work in all_works:
        cat = work.get("_category", "其他")
        categorized.setdefault(cat, []).append(work)

    return categorized, failed_batches

# ========== Phase 3: 题材聚类 ==========
def build_cluster_prompt(works: list) -> str:
    lines = []
    for w in works:
        env = w.get("theme_env", w.get("brief", ""))
        culture = w.get("theme_culture", "")
        narrative = w.get("theme_narrative", "")
        psych = "/".join(w.get("psych_tasks", []) or [])[:30]
        lines.append(f"《{w.get('title', '?')}》| {env} | {culture} | {narrative} | 心理任务:{psych}")
    summary = "\n".join(lines[:150])

    return f"""基于以下{min(len(lines),150)}款任天堂平台游戏的题材数据,做"用于当代中重度手游立项参考"的自然题材聚类分析。

作品题材摘要(格式: 作品名 | 环境/时代 | 文化范式 | 叙事核心 | 心理任务):
{summary}

识别 12-18 个对当代立项有参考价值的题材簇。每个簇必须:
1. 有独特的玩家心理任务激活组合
2. 包含至少 3 款代表作品
3. 优先选择"主机/掌机有验证,但未充分被当代中重度手游开发"的题材
4. 跳过纯系列衍生(只算 IP)的簇

以JSON数组返回,每个条目:
- "cluster_name": 题材簇名称(8字以内)
- "description": 题材核心描述(30字以内)
- "core_elements": 共同核心要素(数组, 3-5 个关键词)
- "core_psych_tasks": 激活的核心玩家心理任务(数组, 2-4 个)
- "emotion_signature": 标志性情绪(15字以内)
- "representative_works": 代表作品(数组, 3-8 款)
- "modern_opportunity": 当代手游立项机会(50字以内,具体到承接玩法)
- "exploration_value": 探索潜力(枚举: "高潜未开发"/"部分开发"/"已饱和")
- "acquisition_potential": 当代获量潜力(枚举: "高"/"中"/"低")
- "roi_potential": 当代ROI潜力(枚举: "高"/"中"/"低")
- "instinct_sources": 用户本能调教来源(数组, 2-4 个)

只返回JSON数组,不要其他文字。"""

def run_clustering(all_works_flat: list) -> list:
    log("=== Phase 3: Clustering ===")
    # 优先取高分作品做聚类
    priority = [w for w in all_works_flat if w.get("acquisition_score", 0) >= 4 or w.get("roi_score", 0) >= 4]
    sample = priority[:80] if len(priority) > 80 else priority
    if len(sample) < 30:
        sample = all_works_flat[:80]
    log(f"  聚类样本: {len(sample)} 款高价值作品")
    prompt = build_cluster_prompt(sample)
    clusters = call_llm_json(prompt, "clustering", max_tokens=6000)
    log(f"  识别到 {len(clusters)} 个题材簇")
    return clusters

# ========== 写出 Markdown ==========
def _quadrant_sort_key(w):
    acq = w.get("acquisition_score", 0)
    roi = w.get("roi_score", 0)
    return -(acq + roi)

def works_to_markdown(works: list, title: str) -> str:
    works_sorted = sorted(works, key=_quadrant_sort_key)
    lines = [f"# {title}", "", f"共 {len(works)} 款游戏,按(获量+ROI)综合得分降序排列。", ""]
    lines += [
        "| 作品 | 年份 | 平台 | 开发/发行 | 销量量级 | 环境/时代 | 文化范式 | 叙事核心 | 心理任务 | 情绪钩子 | 调教来源 | 当代借鉴 | 获量 | ROI | 象限 | 推荐玩法 | 探索潜力 | 风险 |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"
    ]
    for w in works_sorted:
        def safe(key, default="—"):
            v = w.get(key, default)
            if isinstance(v, list):
                return "、".join(str(x) for x in v) if v else "—"
            return str(v) if v else default

        lines.append(
            f"| {safe('title')} | {safe('year')} | {safe('platform')} "
            f"| {safe('developer_pub') if w.get('developer_pub') else safe('developer')} "
            f"| {safe('sales_tier')} "
            f"| {safe('theme_env')} | {safe('theme_culture')} | {safe('theme_narrative')} "
            f"| {safe('psych_tasks')} | {safe('emotion_hooks')} | {safe('instinct_calibration')} "
            f"| {safe('modern_adaptation')} "
            f"| {safe('acquisition_score')}/5 | {safe('roi_score')}/5 | {safe('quadrant')} "
            f"| {safe('gameplay_carrier')} | {safe('exploration_value')} | {safe('risk_tags')} |"
        )
    return "\n".join(lines)

def cluster_to_markdown(cluster: dict) -> str:
    name = cluster.get("cluster_name", "未命名")
    lines = [
        f"# 题材簇: {name}",
        "",
        f"**描述**: {cluster.get('description', '—')}",
        "",
        f"**标志情绪**: {cluster.get('emotion_signature', '—')}",
        "",
        f"**核心要素**: {'、'.join(cluster.get('core_elements', []))}",
        "",
        f"**核心心理任务**: {'、'.join(cluster.get('core_psych_tasks', []))}",
        "",
        f"**本能调教来源**: {'、'.join(cluster.get('instinct_sources', []))}",
        "",
        "## 市场评估",
        "",
        f"| 维度 | 评级 |",
        f"|---|---|",
        f"| 当代获量潜力 | {cluster.get('acquisition_potential', '—')} |",
        f"| 当代ROI潜力 | {cluster.get('roi_potential', '—')} |",
        f"| 探索潜力 | {cluster.get('exploration_value', '—')} |",
        "",
        "## 当代立项机会",
        "",
        cluster.get("modern_opportunity", "—"),
        "",
        "## 代表作品",
        "",
    ]
    for work in cluster.get("representative_works", []):
        lines.append(f"- 《{work}》")
    return "\n".join(lines)

def write_overview(categorized: dict, clusters: list) -> str:
    total = sum(len(v) for v in categorized.values())
    all_works = [w for works in categorized.values() for w in works]
    quadrant_counts = {}
    exploration_counts = {}
    for w in all_works:
        q = w.get("quadrant", "未知")
        quadrant_counts[q] = quadrant_counts.get(q, 0) + 1
        e = w.get("exploration_value", "未知")
        exploration_counts[e] = exploration_counts.get(e, 0) + 1

    lines = [
        "# 任天堂平台游戏题材库 总览",
        "",
        f"构建时间: {TODAY}  ",
        f"数据来源: DeepSeek_Official_Pro route  ",
        f"覆盖范围: 2000-2014(任天堂掌机/主机) + 2017-2026(Switch)",
        "",
        "## 收录统计",
        "",
        "| 分类 | 数量 |",
        "|---|---|",
    ]
    for cat, works in categorized.items():
        lines.append(f"| {cat} | {len(works)} |")
    lines += [
        f"| **合计** | **{total}** |",
        "",
        "## 四象限分布",
        "",
        "| 象限 | 数量 |",
        "|---|---|",
    ]
    for q, count in sorted(quadrant_counts.items(), key=lambda x: -x[1]):
        lines.append(f"| {q} | {count} |")

    lines += [
        "",
        "## 探索潜力分布",
        "",
        "| 探索潜力 | 数量 |",
        "|---|---|",
    ]
    for e, count in sorted(exploration_counts.items(), key=lambda x: -x[1]):
        lines.append(f"| {e} | {count} |")

    lines += [
        "",
        "## 题材聚类一览",
        "",
        "| 题材簇 | 获量 | ROI | 探索潜力 | 代表作 |",
        "|---|---|---|---|---|",
    ]
    for c in clusters:
        reps = "、".join(c.get("representative_works", [])[:3])
        lines.append(
            f"| {c.get('cluster_name','?')} "
            f"| {c.get('acquisition_potential','?')} "
            f"| {c.get('roi_potential','?')} "
            f"| {c.get('exploration_value','?')} "
            f"| {reps} |"
        )

    lines += [
        "",
        "## 字段说明",
        "",
        "| 字段 | 说明 |",
        "|---|---|",
        "| 心理任务 | 题材激活的玩家心理任务,可对齐人群簇标准 |",
        "| 调教来源 | 用户对该题材已被影视/动漫/纪录片/前作训练的来源 |",
        "| 当代借鉴 | 该题材是否已被当代中重度手游/买量市场借鉴 |",
        "| 探索潜力 | 该题材尚未充分被当代中重度立项开发的程度 |",
        "| 获量(1-5) | 当代中重度立项视角,IP+本能调教+素材钩子 |",
        "| ROI(1-5) | 当代中重度玩法承接下的付费深度潜力 |",
    ]
    return "\n".join(lines)

def write_readme() -> str:
    return """\
# 任天堂平台游戏题材库

任天堂平台游戏作品的结构化题材档案。覆盖范围:
- **2000-2014**: 任天堂掌机/主机(GBA、NDS、3DS 早期、N64、GameCube、Wii)
- **2017-2026**: Switch 完整生命周期

**用途**: 为当代中重度手游立项的题材选型提供参考,从主机/掌机时代验证过的题材中反推可用于当代立项的方向。

## 目录结构

| 文件 | 内容 |
|---|---|
| `00_总览.md` | 统计概览、四象限分布、探索潜力分布、题材聚类一览 |
| `01_任天堂掌机_汇总.md` | GBA/NDS/3DS 等掌机作品 |
| `02_任天堂主机_汇总.md` | N64/GameCube/Wii 等主机作品 |
| `03_Switch_汇总.md` | Switch 平台作品 |
| `题材聚类/` | 按题材簇深度分析,含当代立项机会判断 |
| `_raw/` | DeepSeek 原始响应存档 |

## 与 历史题材库 的差异

| 维度 | 历史题材库 | 游戏题材库(本库) |
|---|---|---|
| 来源 | 影视/动漫/文学/短剧 | 主机/掌机游戏 |
| 视角 | 题材本能调教 | 题材已被游戏验证的形式 |
| 输出 | 用户本能联想 | 已被验证的游戏题材+未开发方向 |

## 核心字段

- **题材三要素**: 环境/时代 × 文化范式 × 叙事核心
- **心理任务**: 题材激活的玩家心理任务清单
- **调教来源**: 用户对该题材的本能熟悉度来源
- **当代借鉴情况**: 该题材是否已被当代手游借鉴
- **探索潜力**: 该题材在当代手游市场的未开发空间
- **获量(1-5)**: 当代立项视角的获量评分
- **ROI(1-5)**: 当代中重度玩法承接的付费深度

## 数据说明

- 数据来源: DeepSeek_Official_Pro route,基于训练知识综合判断
- 2025-2026 年作品覆盖可能不完整
- 销量量级为综合估算,非严格官方数据
"""

# ========== 主流程 ==========
def main():
    log("构建任天堂平台游戏题材库")
    log(f"  目标: 2000-2014(任天堂掌机/主机) + 2017-2026(Switch)")
    log(f"  Route: {LLM_ROUTE}")
    log(f"  Discovery 查询数: {len(DISCOVERY_QUERIES)}")
    log(f"  并发: discovery={DISCOVERY_WORKERS}, analysis={ANALYSIS_WORKERS}")
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    CLUSTER_DIR.mkdir(parents=True, exist_ok=True)

    # Phase 1
    discovery, failed_discovery = run_discovery()
    total_discovered = sum(len(v) for v in discovery.values())
    log(f"Phase 1 完成: 共发现 {total_discovered} 款作品, {len(failed_discovery)} 条查询失败")

    if total_discovered == 0:
        log("[FATAL] Phase 1 完全失败, 退出")
        sys.exit(1)

    # 去重(按 title+year)
    seen = set()
    for cat, works in discovery.items():
        unique = []
        for w in works:
            key = (w.get("title", "").strip(), w.get("year"))
            if key in seen or not key[0]:
                continue
            seen.add(key)
            unique.append(w)
        discovery[cat] = unique
    log(f"去重后: {sum(len(v) for v in discovery.values())} 款")

    # Phase 2
    categorized, failed_analysis_batches = run_analysis(discovery)
    log(f"Phase 2 完成: {len(failed_analysis_batches)} 批次失败")

    # 合并所有作品做聚类
    all_works_flat = [w for works in categorized.values() for w in works]
    clusters = run_clustering(all_works_flat)

    # 写出按分类汇总
    log("=== 写出文件 ===")
    cat_filename_map = {
        "GBA":       "01_GBA_汇总.md",
        "GameCube":  "02_GameCube_汇总.md",
        "NDS":       "03_NDS_汇总.md",
        "Wii":       "04_Wii_汇总.md",
        "3DS":       "05_3DS_汇总.md",
        "Wii_U":     "06_WiiU_汇总.md",
        "Switch":    "07_Switch_汇总.md",
    }
    for cat, works in categorized.items():
        if not works:
            continue
        fname = cat_filename_map.get(cat, f"{cat}.md")
        (OUTPUT_ROOT / fname).write_text(
            works_to_markdown(works, f"{cat} 题材分析"), encoding="utf-8")
        log(f"  写出 {fname} ({len(works)} 款)")

    # 写出按年份(可选,跳过节省体积)

    # 题材聚类
    for c in clusters:
        cname = c.get("cluster_name", "未命名").replace("/", "_").replace(" ", "_")
        (CLUSTER_DIR / f"{cname}.md").write_text(cluster_to_markdown(c), encoding="utf-8")

    # 总览 + README
    (OUTPUT_ROOT / "00_总览.md").write_text(write_overview(categorized, clusters), encoding="utf-8")
    (OUTPUT_ROOT / "README.md").write_text(write_readme(), encoding="utf-8")

    # 失败报告
    if failed_discovery or failed_analysis_batches:
        report_lines = [f"# 失败报告 {TODAY}", ""]
        if failed_discovery:
            report_lines += ["## Discovery 失败", ""] + [f"- `{k}`" for k in sorted(failed_discovery)]
        if failed_analysis_batches:
            report_lines += ["", "## Analysis 失败批次", ""] + [f"- `analysis_batch{i:03d}`" for i in sorted(failed_analysis_batches)]
        (OUTPUT_ROOT / f"_failures_{TODAY}.md").write_text("\n".join(report_lines), encoding="utf-8")

    log("=== 完成 ===")
    log(f"  输出目录: {OUTPUT_ROOT}")
    log(f"  总作品数: {sum(len(v) for v in categorized.values())}")
    log(f"  题材簇数: {len(clusters)}")


if __name__ == "__main__":
    main()
