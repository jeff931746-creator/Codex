#!/usr/bin/env python3
"""
深度聚类: 把 1570 款游戏按"心理任务激活 + 题材三要素"做更精细的聚类。

策略:
  1. 加载所有已 analysis 的作品(从 raw analysis batch 缓存)
  2. 分大类聚类:
     - 按"主心理任务" 先分组(收集养成/战斗/探索/解谜/经营/竞速/解谜/策略/休闲...)
     - 每个大类内再按"题材壳" 二次聚类
  3. 目标 30-50 个细粒度题材簇
  4. 输出: 题材簇深度.md + 高潜簇清单.md

启动:
  set -a; source "$HOME/Library/Application Support/FeishuCodexBridge/bridge/.env"; set +a
  export LLM_ROUTE=DeepSeek_Official_Pro
  python3 archive/tools/scripts/deep_cluster_game_themes.py
"""
import concurrent.futures
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path("/Users/mt/Documents/Codex")
sys.path.insert(0, str(ROOT))

from archive.tools.lib.llm_client import chat_text
from archive.tools.lib.llm_common import RetryPolicy

LIB_ROOT = ROOT / "archive/资料/游戏题材库"
RAW_DIR = LIB_ROOT / "_raw"
CLUSTER_DIR = LIB_ROOT / "题材聚类_深度"
CLUSTER_DIR.mkdir(parents=True, exist_ok=True)

LLM_ROUTE = "DeepSeek_Official_Pro"

def log(msg):
    from datetime import datetime
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def call_llm_json(prompt: str, label: str, max_tokens: int = 8000) -> list:
    cache = RAW_DIR / f"{label}.txt"
    if cache.exists() and cache.stat().st_size > 100:
        text = cache.read_text(encoding="utf-8")
    else:
        text = chat_text(
            prompt, route=LLM_ROUTE, max_tokens=max_tokens, temperature=0.2,
            timeout=240, retry_policy=RetryPolicy(retries=3, base_delay=3.0),
            return_empty_on_error=True
        )
        if text:
            cache.write_text(text, encoding="utf-8")
        else:
            return []
    # parse
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            text = re.sub(r",\s*([}\]])", r"\1", text)
            return json.loads(text)
        except Exception as e:
            log(f"  [ERR] {label} parse failed: {e}")
            return []


def load_all_analyzed() -> list:
    """加载所有 analysis batch 数据"""
    works = []
    for f in sorted(RAW_DIR.glob("*analysis_batch*.txt")):
        try:
            text = f.read_text(encoding="utf-8").strip()
            if text.startswith("```"):
                text = re.sub(r"^```(?:json)?\s*", "", text)
                text = re.sub(r"\s*```$", "", text)
            text = text.strip()
            text = re.sub(r",\s*([}\]])", r"\1", text)
            items = json.loads(text)
            if isinstance(items, list):
                works.extend(items)
        except Exception as e:
            log(f"  [WARN] {f.name}: {e}")
    return works


def make_macro_cluster_prompt(works: list) -> str:
    """让 LLM 按心理任务 + 题材三要素 给作品打"主任务大类"标签"""
    lines = []
    for w in works:
        title = w.get("title", "?").strip("《》")
        env = w.get("theme_env", "")
        culture = w.get("theme_culture", "")
        narrative = w.get("theme_narrative", "")
        psych = "/".join(w.get("psych_tasks", []) or [])
        lines.append(f"《{title}》| 环境:{env} | 文化:{culture} | 叙事:{narrative} | 心理:{psych}")
    summary = "\n".join(lines)

    return f"""你是游戏题材分析专家。下面是 {len(works)} 款任天堂主机/掌机游戏的题材摘要。

请把每款游戏分类到下列大类中的 1 个(只能选 1 个,选最主要的):

大类清单:
A. 收集养成 - 主任务是收集生物/卡片/装备并培育进化
B. 探索冒险 - 主任务是探索未知地图/解谜/发现
C. 战斗对抗 - 主任务是对战/动作打击/反应
D. 战略策略 - 主任务是回合策略/战棋/SLG/卡牌策略
E. 经营建造 - 主任务是经营/建造/模拟/扩张
F. 竞速运动 - 主任务是赛车/运动竞技
G. 节奏音游 - 主任务是节奏/音乐反应
H. 模拟养成 - 主任务是养宠物/养角色/养社交关系
I. 推理解谜 - 主任务是推理/审讯/解谜叙事
J. 叙事情感 - 主任务是剧情体验/AVG/角色羁绊
K. 派对休闲 - 主任务是聚会小游戏/休闲娱乐

输出 JSON 数组,每条:
- "title": 作品名(去掉《》)
- "macro": 大类字母 A-K
- "theme_shell": 题材壳标签(2-4字,如"末世废土"、"日式校园"、"魔法学院"、"宝可梦风"等,精确到能用来二级聚类)

作品列表:
{summary}

只返回 JSON 数组,不要其他文字。"""


def macro_categorize(all_works: list) -> dict:
    """对所有作品做大类分类。分批调用 LLM。"""
    BATCH = 40
    results = {}
    batches = [all_works[i:i+BATCH] for i in range(0, len(all_works), BATCH)]
    log(f"Macro categorize: {len(all_works)} 款分 {len(batches)} 批")

    def process(args):
        idx, batch = args
        prompt = make_macro_cluster_prompt(batch)
        items = call_llm_json(prompt, f"macro_cluster_b{idx:03d}", max_tokens=4000)
        return idx, items

    done = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        futures = [ex.submit(process, (i, b)) for i, b in enumerate(batches)]
        for f in concurrent.futures.as_completed(futures):
            idx, items = f.result()
            for item in items:
                title = item.get("title", "").strip().strip("《》")
                if title:
                    results[title] = {"macro": item.get("macro"), "theme_shell": item.get("theme_shell", "")}
            done += 1
            if done % 5 == 0 or done == len(batches):
                log(f"  进度 {done}/{len(batches)}")

    return results


def make_subcluster_prompt(macro_label: str, works: list) -> str:
    """对一个大类下的作品做二级聚类"""
    lines = []
    for w in works:
        title = w.get("title", "?").strip("《》")
        env = w.get("theme_env", "")
        culture = w.get("theme_culture", "")
        narrative = w.get("theme_narrative", "")
        shell = w.get("_theme_shell", "")
        psych = "/".join(w.get("psych_tasks", []) or [])
        explore = w.get("exploration_value", "")
        acq = w.get("acquisition_score", 0)
        roi = w.get("roi_score", 0)
        lines.append(
            f"《{title}》| 壳:{shell} | 环境:{env} | 文化:{culture} | 叙事:{narrative} "
            f"| 心理:{psych} | 获量:{acq} ROI:{roi} | 探索:{explore}"
        )
    summary = "\n".join(lines)

    return f"""你是游戏题材分析专家。下面是 {len(works)} 款属于「{macro_label}」大类的游戏摘要。

请把这些作品聚类到 4-8 个细粒度题材簇(基于"题材壳 + 心理任务激活组合")。

聚类原则:
1. 簇名称必须具体(8字以内,如"宝可梦式收集"、"猎魂式合成召唤"、"恶魔之子式契约")
2. 同一个簇内的作品必须共享"题材壳风格 + 至少 2 个核心心理任务"
3. 每个簇至少 3 款作品
4. 不要笼统的"卡牌养成"这种空名,要具体到"做了什么题材壳+激活什么心理任务"

输出 JSON 数组,每个簇:
- "cluster_name": 簇名(8字以内,具体)
- "description": 30字以内,说明该簇靠什么独特组合成立
- "theme_shells": 共享的题材壳标签数组(2-3个)
- "core_psych_tasks": 核心心理任务数组(2-4个)
- "core_elements": 共同核心要素(3-5个关键词)
- "emotion_signature": 标志性情绪(15字以内)
- "instinct_sources": 用户本能调教来源数组(2-4个)
- "representative_works": 代表作品数组(从输入里挑3-8款,带《》)
- "modern_opportunity": 当代立项机会(50字以内,具体到承接玩法+解决什么市场痛点)
- "exploration_value": **当代中重度手游市场**(2023-2026 国内+海外中重度手游,不含主机/掌机/PC)的开发程度,枚举:
    * "已饱和": 当代中重度手游里有 ≥3 个验证过 ≥6 个月 LTV 的同品类同壳产品在线运营(例如"全明星派对赛车"被 QQ飞车系列饱和)
    * "部分开发": 当代手游有 1-2 个尝试,但未形成主流赛道,或国内/海外其中一侧仍有空白(例如"火焰纹章式战棋"虽在主机饱和,但当代手游战棋赛道只有少量产品)
    * "高潜未开发": 当代中重度手游基本空白,但主机/掌机时代有 ≥3 款验证过的代表作(例如"幽灵附身式回溯"完全空白)
    * "难复刻": 主机/掌机验证强,但因为体感/硬件依赖/玩法时长/付费模式等结构性原因,手游难以承接(例如"任天堂跨界乱斗"依赖跨IP授权,"实体玩具虚实交互"依赖硬件)
  注意: 判断标准**只看当代中重度手游市场**,主机/PC/单机/独立游戏的活跃不算"已饱和"。主机饱和但手游空白的题材是"高潜未开发"或"部分开发",不是"已饱和"。
- "acquisition_potential": **当代手游买量市场**的获量潜力,枚举: "高"/"中"/"低"
  注意: 评估当代手游买量素材能否在 15 秒内讲清并吸引点击,不是评估主机时代的影响力
- "roi_potential": **当代手游中重度承接**的 ROI 潜力,枚举: "高"/"中"/"低"
  注意: 评估当代手游能否在该题材上承接半年以上 LTV 和深度付费,不是评估主机销量

作品列表:
{summary}

只返回 JSON 数组,不要其他文字。"""


def sub_cluster(macro_label: str, works: list) -> list:
    """对一个大类做二级聚类"""
    if len(works) < 4:
        return []  # 太少不聚类
    log(f"  {macro_label}: {len(works)} 款 → 二级聚类")
    prompt = make_subcluster_prompt(macro_label, works)
    clusters = call_llm_json(prompt, f"subcluster_{macro_label}", max_tokens=7000)
    log(f"    {macro_label}: 得到 {len(clusters)} 簇")
    return clusters


def cluster_to_markdown(cluster: dict, macro_label: str) -> str:
    name = cluster.get("cluster_name", "未命名")
    lines = [
        f"# 题材簇: {name}",
        "",
        f"**大类**: {macro_label}",
        f"**描述**: {cluster.get('description', '—')}",
        "",
        f"**标志情绪**: {cluster.get('emotion_signature', '—')}",
        "",
        f"**核心心理任务**: {'、'.join(cluster.get('core_psych_tasks', []))}",
        "",
        f"**题材壳**: {'、'.join(cluster.get('theme_shells', []))}",
        "",
        f"**核心要素**: {'、'.join(cluster.get('core_elements', []))}",
        "",
        f"**本能调教来源**: {'、'.join(cluster.get('instinct_sources', []))}",
        "",
        "## 市场评估",
        "",
        "| 维度 | 评级 |",
        "|---|---|",
        f"| 获量潜力 | {cluster.get('acquisition_potential', '—')} |",
        f"| ROI潜力 | {cluster.get('roi_potential', '—')} |",
        f"| 探索潜力 | {cluster.get('exploration_value', '—')} |",
        "",
        "## 当代立项机会",
        "",
        cluster.get("modern_opportunity", "—"),
        "",
        "## 代表作品",
        "",
    ]
    for w in cluster.get("representative_works", []):
        lines.append(f"- {w}")
    return "\n".join(lines)


def write_index(all_clusters: list, macro_buckets: dict) -> str:
    high_potential = [c for c in all_clusters if c.get("exploration_value") == "高潜未开发"]
    high_acq_roi_high_potential = [
        c for c in high_potential
        if c.get("acquisition_potential") in ("高", "中") and c.get("roi_potential") in ("高", "中")
    ]

    lines = [
        "# 题材簇深度聚类总览",
        "",
        f"**总簇数**: {len(all_clusters)}",
        f"**高潜未开发**: {len(high_potential)}",
        f"**高潜未开发 + 获量/ROI ≥ 中**: {len(high_acq_roi_high_potential)}",
        "",
        "## 高潜未开发题材簇(立项重点关注)",
        "",
        "| 簇名 | 大类 | 获量 | ROI | 探索 | 代表作 |",
        "|---|---|---|---|---|---|",
    ]
    for c in sorted(high_potential, key=lambda x: (
        {"高":0,"中":1,"低":2}.get(x.get("acquisition_potential",""), 9) +
        {"高":0,"中":1,"低":2}.get(x.get("roi_potential",""), 9)
    )):
        reps = "、".join(c.get("representative_works", [])[:3])
        lines.append(
            f"| {c.get('cluster_name','?')} "
            f"| {c.get('_macro','?')} "
            f"| {c.get('acquisition_potential','?')} "
            f"| {c.get('roi_potential','?')} "
            f"| {c.get('exploration_value','?')} "
            f"| {reps} |"
        )

    lines += ["", "## 全部题材簇(按大类)", ""]
    for macro_label, _ in sorted(macro_buckets.items()):
        cs = [c for c in all_clusters if c.get("_macro") == macro_label]
        if not cs:
            continue
        lines += [
            f"### {macro_label}",
            "",
            "| 簇名 | 获量 | ROI | 探索 | 代表作 |",
            "|---|---|---|---|---|",
        ]
        for c in cs:
            reps = "、".join(c.get("representative_works", [])[:3])
            lines.append(
                f"| {c.get('cluster_name','?')} "
                f"| {c.get('acquisition_potential','?')} "
                f"| {c.get('roi_potential','?')} "
                f"| {c.get('exploration_value','?')} "
                f"| {reps} |"
            )
        lines.append("")
    return "\n".join(lines)


MACRO_LABELS = {
    "A": "收集养成",
    "B": "探索冒险",
    "C": "战斗对抗",
    "D": "战略策略",
    "E": "经营建造",
    "F": "竞速运动",
    "G": "节奏音游",
    "H": "模拟养成",
    "I": "推理解谜",
    "J": "叙事情感",
    "K": "派对休闲",
}


def main():
    log("=== 深度聚类启动 ===")
    works = load_all_analyzed()
    log(f"加载已分析作品: {len(works)} 款")

    if len(works) < 100:
        log("[FATAL] 作品数过少,无法聚类")
        sys.exit(1)

    # Phase 1: macro 分类
    log("=== Phase 1: Macro 分类 ===")
    macro_map = macro_categorize(works)
    log(f"Macro 分类完成: {len(macro_map)} 款已打标")

    # 整合
    for w in works:
        title = w.get("title", "").strip().strip("《》")
        info = macro_map.get(title, {})
        w["_macro_code"] = info.get("macro", "?")
        w["_macro_label"] = MACRO_LABELS.get(info.get("macro"), "未分类")
        w["_theme_shell"] = info.get("theme_shell", "")

    macro_buckets = defaultdict(list)
    for w in works:
        if w.get("_macro_label") != "未分类":
            macro_buckets[w["_macro_label"]].append(w)
    log(f"Macro 桶分布:")
    for k in sorted(macro_buckets.keys()):
        log(f"  {k}: {len(macro_buckets[k])}")

    # Phase 2: 二级聚类
    log("=== Phase 2: 二级聚类 ===")
    all_clusters = []
    for macro_label, group_works in sorted(macro_buckets.items()):
        clusters = sub_cluster(macro_label, group_works)
        for c in clusters:
            c["_macro"] = macro_label
        all_clusters.extend(clusters)

    log(f"全部题材簇: {len(all_clusters)}")

    # 写出每个簇 + 索引
    log("=== 写出文件 ===")
    for c in all_clusters:
        cname = (c.get("cluster_name", "未命名") or "未命名").replace("/", "_").replace(" ", "_")
        macro = c.get("_macro", "?")
        path = CLUSTER_DIR / f"{macro}_{cname}.md"
        path.write_text(cluster_to_markdown(c, macro), encoding="utf-8")

    (LIB_ROOT / "00_深度聚类总览.md").write_text(write_index(all_clusters, macro_buckets), encoding="utf-8")
    log(f"写出 {len(all_clusters)} 个簇文件 + 总览")
    log("=== 完成 ===")


if __name__ == "__main__":
    main()
