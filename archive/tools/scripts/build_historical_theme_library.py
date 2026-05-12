#!/usr/bin/env python3
"""
近25年题材库构建脚本（2000-2026）
逐年收集日本动漫、欧美影视、韩国电影、海外文学，提取题材三要素+四象限评分。
用途：游戏立项题材参考库。
运行：SILICONFLOW_API_KEY=xxx python3 build_historical_theme_library.py
"""
import concurrent.futures
import json
import os
import re
import ssl
import urllib.request
from datetime import datetime
from pathlib import Path

import certifi

# ========== 配置 ==========
OUTPUT_ROOT = Path(os.environ.get(
    "THEME_LIBRARY_ROOT",
    "/Users/mt/Documents/Codex/archive/资料/历史题材库"
))
RAW_DIR = OUTPUT_ROOT / "_raw"
CLUSTER_DIR = OUTPUT_ROOT / "题材聚类"
TODAY = datetime.now().strftime("%Y-%m-%d")

api_key = os.environ.get("SILICONFLOW_API_KEY", "").strip()
if not api_key:
    raise RuntimeError("SILICONFLOW_API_KEY 未设置")

MODEL = os.environ.get("DEEPSEEK_FLASH_MODEL", "deepseek-ai/DeepSeek-V4-Flash")

# ========== 日志 ==========
def log(msg: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)

# ========== LLM 调用 ==========
def call_llm(prompt: str, max_tokens: int = 8000, retries: int = 3) -> str:
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.3
    }
    ctx = ssl.create_default_context(cafile=certifi.where())
    for attempt in range(1, retries + 1):
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=180) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            log(f"LLM 调用失败 (attempt {attempt}/{retries}): {e}")
            if attempt < retries:
                import time
                wait_time = attempt * 2  # 递增等待：2s, 4s, 6s
                log(f"  等待 {wait_time}s 后重试...")
                time.sleep(wait_time)
            else:
                return ""

def _parse_json(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    text = text.strip()
    text = re.sub(r"\}\s*\{", "},{", text)
    text = text.replace("'", '"')
    text = re.sub(r",\s*([}\]])", r"\1", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
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
    """调用 LLM 并解析 JSON；已有 raw 文件则跳过调用（幂等）"""
    raw_path = RAW_DIR / f"{TODAY}_{label}.txt"
    if raw_path.exists() and raw_path.stat().st_size > 100:
        log(f"  [{label}] 使用已有缓存")
        raw = raw_path.read_text(encoding="utf-8")
    else:
        raw = call_llm(prompt, max_tokens)
        if not raw:
            log(f"  [{label}] 空响应，跳过")
            return []
        raw_path.write_text(raw, encoding="utf-8")
    try:
        data = _parse_json(raw)
        if isinstance(data, list):
            return data
        log(f"  [{label}] 返回了非数组，类型={type(data)}")
        return []
    except Exception as e:
        log(f"  [{label}] JSON 解析失败: {e}")
        return []

# ========== Phase 1: Discovery 发现阶段 ==========
YEARS = list(range(2000, 2027))  # 2000–2026

_JSON_FIELDS = '- "title": 中文名（无则用常用英文名）\n- "original_title": 原名\n- "year": 年份（整数）\n- "genre": 类型\n- "brief": 一句话核心题材（15字以内）\n- "region": "{region}"'

def _year_note(year: int) -> str:
    return "（2024-2026年知识可能不完整，已知几部就列几部，不凑数）" if year >= 2024 else "（尽量列足，已知多少就列多少）"

def make_discovery_queries() -> list:
    """
    每年每类100部：
      anime_y{y}_1-5    日本动漫，每批20部，共5批  max_tokens=2400
      wtv_y{y}_1-5      欧美电视，每批20部，共5批  max_tokens=2400
      wfilm_y{y}_1-5    欧美电影，每批20部，共5批  max_tokens=2400
      kfilm_y{y}_1-5    韩国电影，每批20部，共5批  max_tokens=2400
      lit_y{y}_1-5      文学作品，每批20部，共5批  max_tokens=2400
    合计：27年 × 5类 × 5批 = 675 条查询
    """
    queries = []

    fields_jp   = _JSON_FIELDS.format(region="日本")
    fields_west = _JSON_FIELDS.format(region="欧美")
    fields_kr   = _JSON_FIELDS.format(region="韩国")
    fields_lit  = _JSON_FIELDS.format(region="海外")

    for y in YEARS:
        note = _year_note(y)

        # 日本动漫：5批，每批20部
        for batch in range(1, 6):
            start_rank = (batch - 1) * 20 + 1
            end_rank = batch * 20
            queries.append({
                "key": f"anime_y{y}_b{batch}", "merge_as": "anime", "region": "日本", "year": y,
                "max_tokens": 2400,
                "prompt": (
                    f"请列举{y}年日本动漫综合影响力排名第{start_rank}-{end_rank}名的作品，共20部{note}。"
                    "选取标准：MAL评分、B站/国内播放量、全球知名度综合排名。\n"
                    "以JSON数组返回，每个条目：\n" + fields_jp + "\n只返回JSON数组，不要其他文字。"
                )
            })

        # 欧美电视：5批，每批20部
        for batch in range(1, 6):
            start_rank = (batch - 1) * 20 + 1
            end_rank = batch * 20
            queries.append({
                "key": f"wtv_y{y}_b{batch}", "merge_as": "western_tv", "region": "欧美", "year": y,
                "max_tokens": 2400,
                "prompt": (
                    f"请列举{y}年欧美电视剧综合影响力排名第{start_rank}-{end_rank}名的作品，共20部{note}。"
                    "按IMDb评分+全球影响力综合排名。\n"
                    "以JSON数组返回，每个条目：\n" + fields_west + "\n只返回JSON数组，不要其他文字。"
                )
            })

        # 欧美电影：5批，每批20部
        for batch in range(1, 6):
            start_rank = (batch - 1) * 20 + 1
            end_rank = batch * 20
            queries.append({
                "key": f"wfilm_y{y}_b{batch}", "merge_as": "western_film", "region": "欧美", "year": y,
                "max_tokens": 2400,
                "prompt": (
                    f"请列举{y}年欧美电影全球票房+口碑排名第{start_rank}-{end_rank}名的作品，共20部{note}。\n"
                    "以JSON数组返回，每个条目：\n" + fields_west + "\n只返回JSON数组，不要其他文字。"
                )
            })

        # 韩国电影：5批，每批20部
        for batch in range(1, 6):
            start_rank = (batch - 1) * 20 + 1
            end_rank = batch * 20
            queries.append({
                "key": f"kfilm_y{y}_b{batch}", "merge_as": "kfilm", "region": "韩国", "year": y,
                "max_tokens": 2400,
                "prompt": (
                    f"请列举{y}年韩国电影综合影响力排名第{start_rank}-{end_rank}名的作品，共20部{note}。"
                    "按韩国本土票房+国际影响力（戛纳/奥斯卡/IMDb）综合排名。\n"
                    "以JSON数组返回，每个条目：\n" + fields_kr + "\n只返回JSON数组，不要其他文字。"
                )
            })

        # 文学作品：5批，每批20部
        for batch in range(1, 6):
            start_rank = (batch - 1) * 20 + 1
            end_rank = batch * 20
            queries.append({
                "key": f"lit_y{y}_b{batch}", "merge_as": "literature", "region": "海外", "year": y,
                "max_tokens": 2400,
                "prompt": (
                    f"请列举{y}年全球影响力排名第{start_rank}-{end_rank}名的海外（非中国大陆）小说/漫画/轻小说作品，共20部{note}。"
                    "按Goodreads评分、销量、改编影响力综合排名。\n"
                    "以JSON数组返回，每个条目：\n" + fields_lit + "\n只返回JSON数组，不要其他文字。"
                )
            })

    return queries

DISCOVERY_QUERIES = make_discovery_queries()

def run_discovery() -> tuple[dict, list]:
    """Phase 1：每年每类100部（27年×5类×5批=675条），并发10，每次请求20部"""
    log(f"=== Phase 1: Discovery ({len(DISCOVERY_QUERIES)} 条查询，并发10) ===")
    merged: dict[str, list] = {}
    failed_keys: list[str] = []
    done = 0

    def fetch_one(q):
        key = q["key"]
        mt = q.get("max_tokens", 2400)
        items = call_llm_json(q["prompt"], f"discovery_{key}", max_tokens=mt)
        for item in items:
            item.setdefault("region", q.get("region", "未知"))
            item.setdefault("year", q.get("year", 0))
        return q["merge_as"], items, key

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_one, q) for q in DISCOVERY_QUERIES]
        for future in concurrent.futures.as_completed(futures):
            merge_as, items, key = future.result()
            if not items:
                failed_keys.append(key)
            merged.setdefault(merge_as, []).extend(items)
            done += 1
            if done % 50 == 0 or done == len(DISCOVERY_QUERIES):
                total = sum(len(v) for v in merged.values())
                log(f"  进度 {done}/{len(DISCOVERY_QUERIES)}，已发现 {total} 部")

    for cat, works in merged.items():
        log(f"  {cat} 合计 {len(works)} 部")
    return merged, failed_keys

# ========== Phase 2: 批量题材分析 ==========
def build_analysis_prompt(works_batch: list) -> str:
    works_str = "\n".join(
        f"{i+1}. 《{w.get('title', '?')}》（{w.get('year', '?')}，{w.get('region', '?')}，{w.get('brief', '')}）"
        for i, w in enumerate(works_batch)
    )
    return f"""请对以下{len(works_batch)}部影视/动漫/文学作品，从游戏立项角度分析题材价值。

作品列表：
{works_str}

对每部作品以JSON数组返回分析（数组长度必须与输入相同）：
- "title": 与输入相同的标题
- "theme_env": 题材环境/时代（20字以内，如：日本大正时代/架空奇幻大陆/现代都市地下世界）
- "theme_culture": 文化范式或战斗体系（20字以内，如：剑士武道+鬼怪文化/魔法学院体系/忍者组织体制）
- "theme_narrative": 叙事核心（15字以内，如：成长逆袭/权谋博弈+背叛/末世求生）
- "emotion_hooks": 核心情绪钩子（数组，1-3个，如["热血燃点","守护亲人"]）
- "audience": 受众画像（一句话，25字以内）
- "game_adaptations": 已知游戏改编作品（数组，无则[]）
- "acquisition_score": 获量能力（整数1-5）
- "acquisition_reason": 获量得分理由（15字以内）
- "roi_score": ROI承接能力（整数1-5）
- "roi_reason": ROI得分理由（15字以内）
- "gameplay_carrier": 推荐玩法载体（数组，如["卡牌","RPG","放置"]）
- "risk_tags": 风险标签（数组，如["红海","版权成本高","受众窄"]）

评分标准：
获量能力（1-5）：IP全球知名度 × 素材视觉钩子强度。5=全球顶级IP视觉张力极强；1=小众IP难做素材
ROI承接（1-5）：付费深度 × 数值成长空间。5=战斗养成完整重氪潜力大；1=情感向娱乐付费浅

只返回JSON数组，不要其他文字或代码块标记。"""

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
    """Phase 2：并行批量分析所有作品"""
    log("=== Phase 2: Analysis ===")

    label_map = {
        "anime": "日本动漫",
        "western_tv": "欧美电视",
        "western_film": "欧美电影",
        "kfilm": "韩国电影",
        "literature": "文学作品",
    }

    all_works = []
    for key, items in discovery.items():
        for item in items:
            item["_category"] = label_map.get(key, key)
            all_works.append(item)

    log(f"  总作品数：{len(all_works)}")

    BATCH_SIZE = 10
    batches = [all_works[i:i+BATCH_SIZE] for i in range(0, len(all_works), BATCH_SIZE)]
    log(f"  分 {len(batches)} 批，每批 {BATCH_SIZE} 部，并行度 8")

    failed_batches: list[int] = []

    def process_batch(args):
        idx, batch = args
        results = analyze_batch(batch, idx)
        if not results:
            return len(batch), idx  # 返回 idx 标记失败
        for work, result in zip(batch, results):
            work.update(result)
            acq = work.get("acquisition_score", 0)
            roi = work.get("roi_score", 0)
            if acq and roi:
                work["quadrant"] = _calc_quadrant(acq, roi)
        return len(batch), None

    done = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(process_batch, (i, b)): i for i, b in enumerate(batches)}
        for future in concurrent.futures.as_completed(futures):
            count, failed_idx = future.result()
            if failed_idx is not None:
                failed_batches.append(failed_idx)
            done += count
            if done % 100 == 0 or done == len(all_works):
                log(f"  已完成 {done}/{len(all_works)} 部")

    categorized = {}
    for work in all_works:
        cat = work.get("_category", "其他")
        categorized.setdefault(cat, []).append(work)

    return categorized, failed_batches

# ========== Phase 3: 题材聚类 ==========
def build_cluster_prompt(all_works: list) -> str:
    lines = []
    for w in all_works:
        env = w.get("theme_env", w.get("brief", ""))
        culture = w.get("theme_culture", "")
        narrative = w.get("theme_narrative", "")
        lines.append(f"《{w.get('title', '?')}》| {env} | {culture} | {narrative}")
    summary = "\n".join(lines[:120])

    return f"""基于以下{min(len(lines),120)}部近20年影视/动漫/文学作品的题材数据，进行自然题材聚类分析。

作品题材摘要（格式：作品名 | 环境/时代 | 文化范式 | 叙事核心）：
{summary}

识别12-16个自然题材簇，每个簇需：
1. 有独特的情绪特征和目标受众
2. 包含至少3部代表作品
3. 对游戏立项有实际参考价值

以JSON数组返回，每个条目：
- "cluster_name": 题材簇名称（8字以内，如"忍者武道"、"末世废土"）
- "description": 题材核心描述（30字以内）
- "core_elements": 共同核心要素（数组，3-5个关键词）
- "emotion_signature": 标志性情绪（15字以内）
- "representative_works": 代表作品（数组，3-8部）
- "game_opportunity": 游戏改编机会（50字以内）
- "acquisition_potential": 整体获量潜力（"高"/"中"/"低"）
- "roi_potential": 整体ROI潜力（"高"/"中"/"低"）
- "market_gap": 当前游戏市场空缺度（"蓝海"/"混战"/"红海"）

只返回JSON数组，不要其他文字。"""

def run_clustering(all_works_flat: list) -> list:
    log("=== Phase 3: Clustering ===")
    priority = [w for w in all_works_flat if w.get("acquisition_score", 0) >= 4 or w.get("roi_score", 0) >= 4]
    sample = priority[:50] if len(priority) > 50 else priority
    if len(sample) < 20:
        sample = all_works_flat[:50]
    log(f"  聚类样本：{len(sample)} 部高价值作品")
    prompt = build_cluster_prompt(sample)
    clusters = call_llm_json(prompt, "clustering", max_tokens=4000)
    log(f"  识别到 {len(clusters)} 个题材簇")
    return clusters

# ========== 写出 Markdown 文件 ==========
def _quadrant_sort_key(w):
    acq = w.get("acquisition_score", 0)
    roi = w.get("roi_score", 0)
    return -(acq + roi)

def works_to_markdown(works: list, title: str) -> str:
    works_sorted = sorted(works, key=_quadrant_sort_key)
    lines = [f"# {title}", "", f"共 {len(works)} 部作品，按（获量+ROI）综合得分降序排列。", ""]
    lines += [
        "| 作品 | 年份 | 环境/时代 | 文化范式 | 叙事核心 | 情绪钩子 | 已有游戏 | 获量 | ROI | 象限 | 推荐玩法 | 风险 |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|"
    ]
    for w in works_sorted:
        def safe(key, default="—"):
            v = w.get(key, default)
            if isinstance(v, list):
                return "、".join(str(x) for x in v) if v else "—"
            return str(v) if v else default

        lines.append(
            f"| {safe('title')} | {safe('year')} "
            f"| {safe('theme_env')} | {safe('theme_culture')} | {safe('theme_narrative')} "
            f"| {safe('emotion_hooks')} | {safe('game_adaptations')} "
            f"| {safe('acquisition_score')}/5 | {safe('roi_score')}/5 "
            f"| {safe('quadrant')} | {safe('gameplay_carrier')} | {safe('risk_tags')} |"
        )
    return "\n".join(lines)

def cluster_to_markdown(cluster: dict) -> str:
    name = cluster.get("cluster_name", "未命名")
    lines = [
        f"# 题材簇：{name}",
        "",
        f"**描述**：{cluster.get('description', '—')}",
        "",
        f"**标志情绪**：{cluster.get('emotion_signature', '—')}",
        "",
        f"**核心要素**：{'、'.join(cluster.get('core_elements', []))}",
        "",
        "## 市场评估",
        "",
        f"| 维度 | 评级 |",
        f"|---|---|",
        f"| 获量潜力 | {cluster.get('acquisition_potential', '—')} |",
        f"| ROI潜力 | {cluster.get('roi_potential', '—')} |",
        f"| 市场空缺度 | {cluster.get('market_gap', '—')} |",
        "",
        "## 游戏机会",
        "",
        cluster.get("game_opportunity", "—"),
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
    for w in all_works:
        q = w.get("quadrant", "未知")
        quadrant_counts[q] = quadrant_counts.get(q, 0) + 1

    lines = [
        "# 近25年题材库 总览",
        "",
        f"构建时间：{TODAY}  ",
        f"数据来源：DeepSeek-V4-Flash（SiliconFlow）  ",
        f"覆盖范围：2000-2026年，2024年后作品覆盖可能不完整",
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
        "## 题材聚类一览",
        "",
        "| 题材簇 | 获量 | ROI | 市场空缺 | 代表作 |",
        "|---|---|---|---|---|",
    ]
    for c in clusters:
        reps = "、".join(c.get("representative_works", [])[:3])
        lines.append(
            f"| {c.get('cluster_name','?')} "
            f"| {c.get('acquisition_potential','?')} "
            f"| {c.get('roi_potential','?')} "
            f"| {c.get('market_gap','?')} "
            f"| {reps} |"
        )

    lines += [
        "",
        "## 使用说明",
        "",
        "- `01_日本动漫.md`：日本动漫，按获量+ROI综合得分排序",
        "- `02_欧美影视.md`：欧美TV+电影合并",
        "- `03_韩国电影.md`：韩国电影",
        "- `04_文学作品.md`：海外小说/漫画原著",
        "- `题材聚类/`：按题材簇查找同类作品的共同规律和游戏机会",
        "- `_raw/`：DeepSeek 原始响应存档",
        "",
        "## 字段说明",
        "",
        "| 字段 | 说明 |",
        "|---|---|",
        "| 获量能力 | 1-5分，IP知名度×素材钩子强度 |",
        "| ROI承接 | 1-5分，付费深度×数值成长空间 |",
        "| 象限 | 获量高/中/低 × ROI高/中/低 |",
        "| 推荐玩法 | 适合承接该题材的游戏品类 |",
    ]
    return "\n".join(lines)

def write_readme() -> str:
    return """\
# 近25年题材库

近25年（2000-2026）日本动漫、欧美影视、韩国电影、海外文学作品的题材结构化档案。

**用途**：游戏立项题材选型参考，不限于真实历史背景。

## 目录结构

| 文件 | 内容 |
|---|---|
| `00_总览.md` | 统计概览、四象限分布、题材聚类一览 |
| `01_日本动漫.md` | 日本动漫题材分析表（~30部/年） |
| `02_欧美影视.md` | 欧美TV+电影合并分析表（~45部/年） |
| `03_韩国电影.md` | 韩国电影题材分析表（~15部/年） |
| `04_文学作品.md` | 海外小说/漫画原著分析表 |
| `题材聚类/` | 按题材簇归类的深度分析 |
| `_raw/` | DeepSeek 原始响应存档 |

## 核心字段

- **题材三要素**：环境/时代 × 文化范式 × 叙事核心
- **获量能力**（1-5）：IP知名度 × 素材视觉钩子强度
- **ROI承接**（1-5）：付费深度 × 数值成长空间
- **四象限**：获量高/中/低 × ROI高/中/低

## 数据说明

- 数据来源：DeepSeek-V4-Flash（SiliconFlow），基于训练知识综合判断
- 知识截止约2024年，2024-2026年新作覆盖可能不完整
- 排名为影响力综合判断，非严格官方榜单
"""

def write_failure_report(failed_discovery: list, failed_analysis_batches: list) -> str:
    lines = [
        f"# 失败报告 {TODAY}",
        "",
        f"## Discovery 阶段失败查询（返回0条）",
        "",
    ]
    if failed_discovery:
        for k in sorted(failed_discovery):
            lines.append(f"- `{k}`")
    else:
        lines.append("无")

    lines += [
        "",
        f"## Analysis 阶段失败批次（返回0条）",
        "",
    ]
    if failed_analysis_batches:
        for idx in sorted(failed_analysis_batches):
            lines.append(f"- `analysis_batch{idx:03d}`")
    else:
        lines.append("无")

    lines += [
        "",
        "## 处理建议",
        "",
        "- Discovery 失败：删除对应 `_raw/` 缓存文件后重跑，脚本会自动跳过已有缓存",
        "- Analysis 失败：删除对应 `_raw/` 批次缓存后重跑",
        "- 重跑命令：`SILICONFLOW_API_KEY=xxx python3 build_historical_theme_library.py`",
    ]
    return "\n".join(lines)

# ========== 主流程 ==========
def main():
    log("构建近27年题材库（2000-2026）")
    log(f"  目标：每年每类100部（动漫+欧美TV+欧美电影+韩国电影+文学 各100部/年）")
    log(f"  总查询数：{len(DISCOVERY_QUERIES)} 条（27年×5类×5批）")
    log(f"  预期产出：27年 × 5类 × 100部 = 13,500部作品")
    log(f"  优化配置：重试3次、超时180s、并发10（Discovery）/8（Analysis）")
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    CLUSTER_DIR.mkdir(parents=True, exist_ok=True)

    # Phase 1
    discovery, failed_discovery = run_discovery()
    total_discovered = sum(len(v) for v in discovery.values())
    log(f"Phase 1 完成：共发现 {total_discovered} 部作品，{len(failed_discovery)} 条查询失败")

    # Phase 2
    categorized, failed_analysis_batches = run_analysis(discovery)
    log(f"Phase 2 完成：{len(failed_analysis_batches)} 批次失败")

    # Phase 3
    all_works_flat = [w for works in categorized.values() for w in works]
    clusters = run_clustering(all_works_flat)

    # 写出文件（按年份组织）
    log("=== 写出文件（按年份） ===")

    (OUTPUT_ROOT / "README.md").write_text(write_readme(), encoding="utf-8")

    # 按年份分组所有作品
    works_by_year = {}
    for work in all_works_flat:
        year = work.get("year", 0)
        if year:
            works_by_year.setdefault(year, []).append(work)

    # 为每年生成一个文件
    for year in sorted(works_by_year.keys()):
        year_works = works_by_year[year]
        year_file = OUTPUT_ROOT / f"{year}.md"
        year_file.write_text(
            works_to_markdown(year_works, f"{year}年 题材分析"), encoding="utf-8")
        log(f"  写出 {year}.md ({len(year_works)} 部)")

    # 保留分类汇总文件
    anime_works = categorized.get("日本动漫", [])
    if anime_works:
        (OUTPUT_ROOT / "01_日本动漫_汇总.md").write_text(
            works_to_markdown(anime_works, "日本动漫 题材分析（全年汇总）"), encoding="utf-8")
        log(f"  写出 01_日本动漫_汇总.md ({len(anime_works)} 部)")

    western = categorized.get("欧美电视", []) + categorized.get("欧美电影", [])
    if western:
        (OUTPUT_ROOT / "02_欧美影视_汇总.md").write_text(
            works_to_markdown(western, "欧美影视 题材分析（全年汇总）"), encoding="utf-8")
        log(f"  写出 02_欧美影视_汇总.md ({len(western)} 部)")

    kfilm = categorized.get("韩国电影", [])
    if kfilm:
        (OUTPUT_ROOT / "03_韩国电影_汇总.md").write_text(
            works_to_markdown(kfilm, "韩国电影 题材分析（全年汇总）"), encoding="utf-8")
        log(f"  写出 03_韩国电影_汇总.md ({len(kfilm)} 部)")

    lit = categorized.get("文学作品", [])
    if lit:
        (OUTPUT_ROOT / "04_文学作品_汇总.md").write_text(
            works_to_markdown(lit, "文学作品 题材分析（全年汇总）"), encoding="utf-8")
        log(f"  写出 04_文学作品_汇总.md ({len(lit)} 部)")

    for cluster in clusters:
        name = cluster.get("cluster_name", "未命名")
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', name)
        path = CLUSTER_DIR / f"{safe_name}.md"
        path.write_text(cluster_to_markdown(cluster), encoding="utf-8")
    log(f"  写出 {len(clusters)} 个聚类文件到 题材聚类/")

    overview = write_overview(categorized, clusters)
    (OUTPUT_ROOT / "00_总览.md").write_text(overview, encoding="utf-8")
    log("  写出 00_总览.md")

    # 失败报告
    has_failures = bool(failed_discovery or failed_analysis_batches)
    report = write_failure_report(failed_discovery, failed_analysis_batches)
    (OUTPUT_ROOT / "FAILURES.md").write_text(report, encoding="utf-8")
    if has_failures:
        log(f"\n⚠️  有失败项，请查看 {OUTPUT_ROOT}/FAILURES.md")
        log(f"   Discovery 失败：{len(failed_discovery)} 条 | Analysis 失败批次：{len(failed_analysis_batches)} 批")
    else:
        log("\n✅ 全部完成，无失败项")

    log(f"\n完成！题材库位置：{OUTPUT_ROOT}")
    log(f"总作品数：{len(all_works_flat)}，题材簇：{len(clusters)} 个")

if __name__ == "__main__":
    main()
