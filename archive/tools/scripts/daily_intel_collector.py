#!/usr/bin/env python3
"""每日信息收集脚本（测试版）

从公众号拉取最新文章 → DeepSeek 分类/提取 → 写入战略库或竞品库。

用法：
    # 加载 API keys
    set -a && source "$HOME/Library/Application Support/FeishuCodexBridge/bridge/.env" && set +a
    export LLM_PROVIDER=deepseek
    export WX_API_KEY="你的 wechat-article-exporter API key"

    # 测试：只跑 GameLook 一个来源，最多 3 篇
    cd /Users/mt/Documents/Codex
    python3 -m archive.tools.scripts.daily_intel_collector --test

    # 正式：跑来源注册表中所有 T1 来源
    python3 -m archive.tools.scripts.daily_intel_collector
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# ── 路径 ──────────────────────────────────────────────
CODEX_ROOT = Path(__file__).resolve().parents[3]  # /Users/mt/Documents/Codex
STRATEGY_DIR = CODEX_ROOT / "archive" / "资料" / "战略库"
COMPETE_DIR = CODEX_ROOT / "archive" / "资料" / "竞品库"
FILTER_LOG = STRATEGY_DIR / "过滤日志.md"

sys.path.insert(0, str(CODEX_ROOT))

from archive.tools.lib.llm_client import chat_text  # noqa: E402


# ── 配置 ──────────────────────────────────────────────
WX_API_BASE = "https://down.mptext.top"
WX_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 "
    "MicroMessenger/8.0.34(0x16082222) NetType/WIFI Language/zh_CN"
)

# 测试用：GameLook 的 fakeid
TEST_SOURCES = [
    {"name": "GameLook", "fakeid": "MjM5NzQwMjI4MA==", "line": "双线", "tier": "T1"},
]

# 分流关键词
PRODUCT_KEYWORDS = [
    "新游", "上线", "首发", "公测", "上架", "首曝", "实机",
    "榜单", "Top", "畅销", "下载量", "流水", "月收入",
    "拆解", "评测", "体验",
]
STRATEGY_KEYWORDS = [
    "买量", "投放", "ROI", "CPI", "CPM", "素材", "创意",
    "市场", "趋势", "大盘", "政策", "平台", "算法",
    "出海", "海外", "全球",
    "融资", "收购", "上市", "财报",
]


# ── API 调用 ──────────────────────────────────────────

def wx_api_get(endpoint: str, params: dict | None = None) -> dict:
    """调用 wechat-article-exporter API（通过 curl，避免 Python urllib 被 403）。"""
    import urllib.parse

    api_key = os.environ.get("WX_API_KEY", "")
    if not api_key:
        raise RuntimeError("WX_API_KEY 未设置")

    url = f"{WX_API_BASE}{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    result = subprocess.run(
        ["curl", "-s", "--max-time", "30", "-H", f"X-Auth-Key: {api_key}", url],
        capture_output=True, text=True, timeout=35,
    )
    if result.returncode != 0:
        raise RuntimeError(f"curl 失败: {result.stderr}")
    return json.loads(result.stdout)


def get_article_list(fakeid: str, count: int = 5) -> list[dict]:
    """获取公众号最新文章列表。"""
    data = wx_api_get("/api/public/v1/article", {
        "fakeid": fakeid,
        "begin": 0,
        "size": count,
    })
    return data.get("articles", [])


def fetch_article_content(url: str) -> str:
    """用 url-md + 微信 UA 读取文章全文（Markdown 格式）。"""
    try:
        result = subprocess.run(
            ["url-md", "md", url, "--quiet", "--timeout", "20"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            # 去掉 frontmatter
            text = result.stdout
            if text.startswith("---\n"):
                parts = text.split("---\n", 2)
                if len(parts) >= 3:
                    return parts[2].strip()
            return text.strip()
    except Exception:
        pass

    # fallback: curl + UA 伪装
    try:
        result = subprocess.run(
            ["curl", "-sL", "-H", f"User-Agent: {WX_UA}", url],
            capture_output=True, text=True, timeout=20,
        )
        if result.returncode == 0:
            # 粗提取：去 HTML 标签
            text = re.sub(r"<script[^>]*>.*?</script>", "", result.stdout, flags=re.S)
            text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.S)
            text = re.sub(r"<[^>]+>", "\n", text)
            text = re.sub(r"\n{3,}", "\n\n", text)
            return text.strip()[:5000]
    except Exception:
        pass

    return ""


# ── 分流与分析 ─────────────────────────────────────────

def classify_article(title: str, content_preview: str) -> str:
    """快速分流：product / strategy / both。"""
    text = f"{title} {content_preview[:300]}"
    has_product = any(kw in text for kw in PRODUCT_KEYWORDS)
    has_strategy = any(kw in text for kw in STRATEGY_KEYWORDS)

    if has_product and has_strategy:
        return "both"
    if has_product:
        return "product"
    return "strategy"


# ── 硬过滤（代码层，不依赖 LLM）────────────────────

BLACKLISTED_COMPANIES = {
    "腾讯", "网易", "米哈游", "字节跳动", "莉莉丝", "三七互娱", "完美世界",
    "盛趣", "4399", "快手", "弹指宇宙", "光子", "天美", "北极光",
    "索尼", "sony", "微软", "microsoft", "任天堂", "nintendo",
    "ea", "育碧", "ubisoft", "动视暴雪", "activision", "blizzard",
    "take-two", "rockstar", "square enix", "capcom", "bandai namco", "sega",
    "epic games", "valve",
}

BLACKLISTED_KEYWORDS_STRATEGY = {
    "任天堂", "nintendo", "switch", "ps5", "xbox", "掌机",
    "股价", "市值", "人事", "离职", "加入",
    "收购艺画", "灵笼",
}

# 非游戏行业关键词：标题命中则整篇跳过（不进战略库也不进竞品库的 DeepSeek 分析）
NON_GAME_KEYWORDS = {
    "录音笔", "智能硬件", "AI硬件", "耳机", "音箱",
    "跨境电商", "跨境营销", "外贸", "物流", "供应链",
    "房地产", "金融理财", "保险", "医疗",
    "设计大奖", "design award",
}


def _is_blacklisted_product(prod: dict) -> bool:
    """硬过滤：大厂产品、3A、超休闲。"""
    name = (prod.get("name", "") or "").lower()
    dev = (prod.get("developer", "") or "").lower()
    pub = (prod.get("publisher", "") or "").lower()
    cats = " ".join(prod.get("category_tags", [])).lower()
    combined = f"{name} {dev} {pub} {cats}"

    # 大厂黑名单
    for company in BLACKLISTED_COMPANIES:
        if company.lower() in combined:
            return True

    # 3A 关键词
    if any(kw in combined for kw in ("3a", "aaa", "主机大作")):
        return True

    return False


def _is_blacklisted_strategy(title: str) -> bool:
    """硬过滤：战略库不关注的内容。"""
    title_lower = title.lower()
    for kw in BLACKLISTED_KEYWORDS_STRATEGY:
        if kw.lower() in title_lower:
            return True
    return False


def _is_non_game_content(title: str, content_preview: str) -> bool:
    """硬过滤：非游戏行业内容，整篇跳过。"""
    text = f"{title} {content_preview[:500]}".lower()
    for kw in NON_GAME_KEYWORDS:
        if kw.lower() in text:
            return True
    return False


ANALYSIS_SYSTEM = """你是一个游戏行业信息分析助手。只处理与游戏行业直接相关的内容（手游、小游戏、PC/Steam 游戏、游戏行业市场数据、游戏买量投放）。如果文章与游戏行业无关（如硬件产品、电商、金融、通用营销），返回 {"info_types": [], "strategy": null, "new_products": []}。

根据文章内容，判断信息类型并输出结构化 JSON。

## 信息类型判断

先判断这篇文章属于哪个类型（可以多选）：
- new: 推荐/曝光新游戏（重点：之前没怎么听说过的、最近刚上线或刚公布的游戏）
- data: 榜单排名、流水数据、下载量统计
- ad: 买量投放策略、平台算法变化、获客成本分析
- biz: 融资并购、人事变动、政策法规、公司财报
- teardown: 对已知游戏的深度系统拆解（跳过，不处理）

## 输出格式

```json
{
  "info_types": ["new", "data"],
  "strategy": null 或 { 战略库条目 },
  "new_products": [] 或 [ 新产品列表 ]
}
```

### strategy 字段（当 info_types 包含 data/ad/biz 时填写）

```json
{
  "value_score": 1-5,
  "content_type": "数据报告|行业分析|演讲实录|案例复盘|政策公告|观点评论|产品软文|方法论",
  "source_credibility": "高|中|低",
  "bias_note": "",
  "category": "买量与投放|市场与趋势|产品与设计|立项参考",
  "tags": ["标签1", "标签2"],
  "core_thesis": "核心论点1-3句",
  "actionable_insights": ["洞察1"],
  "key_points": ["要点1", "要点2"],
  "evaluation": "信息质量评估"
}
```

value_score 评分标准（严格执行，宁可漏收不可滥收）：
- 5: 含一手数据（原始表格/具体数字/明确口径）的深度报告
- 4: 有数据支撑的买量/投放策略洞察，或平台政策/规则变化
- 3: 有参考价值的赛道趋势分析（有数据支撑）
- 2: 以下任一→不入库：纯新闻转述无分析/大厂八卦人事/单产品软文/无数据的观点文
- 1: 纯推广/与手游小游戏IAA无关的内容（如PC主机3A新闻、任天堂硬件等）

战略库只关注：买量投放、平台政策、IAA/小游戏市场数据、赛道趋势。
不关注：大厂人事/八卦、PC/主机/3A行业新闻、IP收购、独立游戏个人故事、任天堂/索尼/微软硬件新闻、腾讯网易股价。

### new_products 字段（当 info_types 包含 new 时填写）

⚠️ 新品收录标准（严格执行）：

收录条件（满足任一）：
- N1: 海外未上线产品（公布/预约/测试阶段），轻度到中度
- N2: 海外已上线，国内没有同类玩法/品类的产品
- N3: 国内 IAA（广告变现）新品
- N4: Steam 新品（独立游戏、创新玩法）
- N5: 微信/抖音小游戏新品

排除条件（命中任一直接不收录，无例外）：
- X1: 以下公司的产品一律不收录：腾讯、网易、米哈游、字节跳动、莉莉丝、三七互娱、完美世界、盛趣、4399、快手（弹指宇宙）、索尼、微软、任天堂、EA、育碧、动视暴雪、Take-Two、Square Enix、Capcom、Bandai Namco、Sega
- X2: 三消类游戏（含三消+装修/三消+RPG 等变体）
- X3: 过于轻度的超休闲（打螺丝、撕封条、解压、涂色、ASMR 等纯消磨时间无深度的游戏）
- X4: PC/主机 3A 大作
- X5: 已广为人知的手游（原神、王者荣耀、和平精英、崩坏星穹铁道、鸣潮、明日方舟、阴阳师、少女前线等）

收录时还需标注产品重度：
- "轻度": 休闲、放置、超休闲（但有深度的）、益智
- "中度": 塔防、卡牌、模拟经营、Roguelite、策略
- "重度": SLG、MMO、ARPG、开放世界、竞技

举例：
- 某海外独立工作室的 Roguelite → ✅ N1，中度
- Steam 上新出的独立塔防 → ✅ N4，中度
- 微信小游戏 IAA 放置塔防 → ✅ N5，中度
- 腾讯的造化工坊 → ❌ X1（腾讯）
- 快手弹指宇宙的诡秘之主 → ❌ X1（快手）
- 战神新作 → ❌ X4 + X1（索尼）
- 打螺丝小游戏 → ❌ X3
- 某三消装修游戏 → ❌ X2

⚠️ 产品命名规则（严格执行）：
- name 必须是游戏的正式名称（中文名或英文名均可），如"沙画消消"、"Last Asylum"、"墨境"
- 禁止使用描述性名称，如"微恐蔚蓝Like新品"、"DW Like新品"、"某款塔防游戏"
- 如果文章没有明确提到游戏名称，不要收录这个产品

⚠️ 信息提取规则（尽量填充，只有文章确实没提到才写空）：
- developer/publisher：从文章中尽力提取。文章提到"XX团队开发"、"由XX发行"、"XX出品"、"XX推出"等都算
- release_date：文章提到任何时间信息都要填（"近期"、"6月"、"2025年Q2"等）
- monetization：从玩法和平台推断（微信小游戏多为IAA或混合，Steam多为买断，手游多为IAP或混合）
- art_style：从文章描述或截图提取（像素、3D写实、二次元、卡通、水墨等）
- similar_games：文章中提到的对标/类似产品

```json
[
  {
    "name": "游戏正式名称（必填，不接受描述性名称）",
    "is_genuinely_new": true,
    "newness_reason": "为什么认为这是新品",
    "weight": "轻度|中度|重度",
    "platform": ["iOS", "Android", "Steam", "微信小游戏", "抖音小游戏"],
    "category_primary": "主品类（如塔防/卡牌/Roguelite/放置/SLG/二合/消除等）",
    "category_tags": ["玩法标签1", "玩法标签2"],
    "developer": "开发商（从文章中提取，实在没有才写未知）",
    "publisher": "发行商（从文章中提取，实在没有才写未知）",
    "release_status": "已上线|测试中|预约中|已公布|待确认",
    "release_date": "尽量填具体日期或时间段，实在没有才写待确认",
    "region": ["地区"],
    "core_gameplay": "核心玩法2-3句话描述，包含核心循环和差异化点",
    "monetization": "IAA|IAP|混合|买断（根据平台和玩法推断，不要轻易写待确认）",
    "art_style": "美术风格（像素/3D写实/卡通/二次元/水墨/低多边形等，从文章描述提取）",
    "similar_games": "文章中提到的对标或类似产品（如'类似XX'、'XX-like'），没有则为空字符串",
    "chart_info": "榜单/收入/下载量数据，没有则为空字符串",
    "summary": "一句话概述，突出这个产品的独特卖点"
  }
]
```

如果文章里没有符合条件的新产品，new_products 返回空数组 []。
如果文章是纯 teardown 类型，info_types 只写 ["teardown"]，strategy 和 new_products 都为 null/[]。

只输出 JSON，不要输出其他内容。"""


def analyze_article(title: str, content: str, source_name: str) -> dict | None:
    """用 DeepSeek 分析文章，返回结构化数据。最多重试 3 次。"""
    prompt = f"来源：{source_name}\n标题：{title}\n\n正文（截取前 3000 字）：\n{content[:3000]}"

    for attempt in range(3):
        if attempt > 0:
            time.sleep(3)
        try:
            result = chat_text(
                prompt,
                system=ANALYSIS_SYSTEM,
                provider="deepseek",
                max_tokens=2000,
                temperature=0.1,
            )
            result = result.strip()
            if result.startswith("```"):
                result = re.sub(r"^```\w*\n?", "", result)
                result = re.sub(r"\n?```$", "", result)
            parsed = json.loads(result)

            strategy = parsed.get("strategy")
            if strategy and not strategy.get("core_thesis") and not strategy.get("key_points"):
                print(f"  ⚠️ DeepSeek 返回 strategy 但关键字段为空 (attempt {attempt+1}/3)")
                continue

            return parsed
        except json.JSONDecodeError as e:
            print(f"  ⚠️ JSON 解析失败 (attempt {attempt+1}/3): {e}")
        except Exception as e:
            print(f"  ⚠️ DeepSeek 分析失败 (attempt {attempt+1}/3): {e}")

    print(f"  ❌ DeepSeek 分析最终失败（3 次均失败）: {title[:30]}...")
    return None


# ── 写入文件 ──────────────────────────────────────────

def write_strategy_entry(article: dict, analysis: dict, source_name: str) -> Path | None:
    """写入战略库条目。"""
    strategy = analysis.get("strategy") or analysis
    if not strategy:
        return None

    # 内容质量校验：核心论点和要点不能全空
    if not strategy.get("core_thesis") and not strategy.get("key_points"):
        return None

    value_score = strategy.get("value_score", 3)
    if value_score <= 2:
        # 记过滤日志
        with open(FILTER_LOG, "a", encoding="utf-8") as f:
            f.write(f"- [{time.strftime('%Y-%m-%d')}] [{source_name}] {article['title']} | value_score={value_score}\n")
        return None

    today = time.strftime("%Y-%m-%d")
    # 生成文件名
    slug = re.sub(r'[/\\:*?"<>|]', '_', article["title"])[:30]
    filename = f"{today}_{slug}.md"
    filepath = STRATEGY_DIR / "条目" / filename

    # 避免重复
    if filepath.exists():
        return filepath

    ts = article.get("update_time", 0)
    pub_date = time.strftime("%Y-%m-%d", time.localtime(ts)) if ts else "未知"

    yaml_block = f"""---
entry_id: INTEL-{today}-{int(time.time()) % 10000:04d}
title: "{article['title']}"
date: "{pub_date}"
source_name: "{source_name}"
url: "{article.get('link', '')}"
source_author: "{article.get('author_name', '未知')}"
content_type: "{strategy.get('content_type', '行业分析')}"
core_thesis: "{strategy.get('core_thesis', '')}"
actionable_insights: {json.dumps(strategy.get('actionable_insights', []), ensure_ascii=False)}
source_credibility: "{strategy.get('source_credibility', '中')}"
bias_note: "{strategy.get('bias_note', '')}"
value_score: {value_score}
category: "{strategy.get('category', '市场与趋势')}"
tags: {json.dumps(strategy.get('tags', []), ensure_ascii=False)}
related_entries: []
related_libraries: []
user_rating: null
user_note: ""
collected_date: "{today}"
---"""

    key_points = strategy.get("key_points", [])
    key_points_text = "\n".join(f"- {p}" for p in key_points) if key_points else "（待补充）"

    body = f"""{yaml_block}

## 核心论点
{strategy.get('core_thesis', '（待补充）')}

## 关键信息
{key_points_text}

## 评估
{strategy.get('evaluation', '（待补充）')}

## 可行动洞察
{chr(10).join('- ' + i for i in strategy.get('actionable_insights', [])) or '（无）'}
"""

    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(body, encoding="utf-8")
    return filepath


def write_product_entry(product: dict, article: dict, source_name: str) -> Path | None:
    """写入竞品库条目。按轻中重度分档 + 日期命名。"""
    name = product.get("name", "").strip()
    if not name:
        return None

    # 拒绝描述性名称（非正式游戏名）
    reject_patterns = ["新品", "like新品", "未知", "未命名", "某款", "一款"]
    name_lower = name.lower()
    if any(p in name_lower for p in reject_patterns):
        print(f"    ⏭️ 竞品库跳过: 非正式名称 '{name}'")
        return None

    weight = product.get("weight", "中度")
    if weight not in ("轻度", "中度", "重度"):
        weight = "中度"

    weight_dir = COMPETE_DIR / weight
    weight_dir.mkdir(parents=True, exist_ok=True)

    today = time.strftime("%Y-%m-%d")
    slug = re.sub(r'[/\\:*?"<>|]', '_', name)
    filepath = weight_dir / f"{today}_{slug}.md"

    if filepath.exists():
        # 追加到信息时间线（按 URL 去重，避免同文章多次追加）
        existing = filepath.read_text(encoding="utf-8")
        article_url = article.get("link", "")
        if article_url and article_url in existing:
            return filepath
        timeline_entry = f"- [{today}] [{source_name}] {article['title']}: {product.get('summary', '')}"
        if "## 信息时间线" in existing:
            existing = existing.replace(
                "## 信息时间线\n",
                f"## 信息时间线\n{timeline_entry}\n",
            )
            filepath.write_text(existing, encoding="utf-8")
        return filepath

    # 新建条目 —— 重要信息优先
    dev = product.get("developer", "")
    pub = product.get("publisher", "")
    gameplay = product.get("core_gameplay", "")
    art = product.get("art_style", "")
    similar = product.get("similar_games", "")

    yaml_block = f"""---
title: "{name}"
weight: "{weight}"
platform: {json.dumps(product.get('platform', []), ensure_ascii=False)}
core_gameplay: "{gameplay}"
category_primary: "{product.get('category_primary', '')}"
category_tags: {json.dumps(product.get('category_tags', []), ensure_ascii=False)}
art_style: "{art}"
similar_games: "{similar}"
developer: "{dev}"
publisher: "{pub}"
monetization: "{product.get('monetization', '')}"
release_status: "{product.get('release_status', '')}"
release_date: "{product.get('release_date', '')}"
region: {json.dumps(product.get('region', []), ensure_ascii=False)}
chart_info: "{product.get('chart_info', '')}"
entry_id: PROD-{today}-{int(time.time()) % 10000:04d}
source_name: "{source_name}"
url: "{article.get('link', '')}"
collected_date: "{today}"
last_updated: "{today}"
user_rating: null
user_note: ""
---"""

    # 正文也按重要性排列
    dev_pub = ""
    if dev:
        dev_pub += f"开发商: {dev}"
    if pub:
        dev_pub += f" | 发行商: {pub}" if dev_pub else f"发行商: {pub}"

    body = f"""{yaml_block}

## {name}

{product.get('summary', '')}

{f'**{dev_pub}**' if dev_pub else ''}
{f'**美术风格**: {art}' if art else ''}
{f'**对标产品**: {similar}' if similar else ''}

## 信息时间线
- [{today}] [{source_name}] {article['title']}: {product.get('summary', '')}

## 市场表现
{f"榜单: {product['chart_info']}" if product.get('chart_info') else '（暂无数据）'}
"""

    filepath.write_text(body, encoding="utf-8")
    return filepath


# ── 主流程 ────────────────────────────────────────────

def process_source(source: dict, max_articles: int = 5) -> dict:
    """处理单个来源，返回统计。"""
    name = source["name"]
    fakeid = source["fakeid"]
    stats = {"source": name, "fetched": 0, "strategy": 0, "product": 0, "filtered": 0, "errors": 0}

    print(f"\n📡 {name} (fakeid={fakeid[:10]}...)")

    # 1. 拉文章列表
    try:
        articles = get_article_list(fakeid, count=max_articles)
    except Exception as e:
        print(f"  ❌ 拉取文章列表失败: {e}")
        stats["errors"] = 1
        return stats

    # API 可能返回超过请求数量的文章，截断到 max_articles
    if len(articles) > max_articles:
        articles = articles[:max_articles]
    stats["fetched"] = len(articles)
    print(f"  获取 {len(articles)} 篇文章")

    for art in articles:
        title = art.get("title", "")
        link = art.get("link", "")
        if not title or not link:
            continue

        # 2. 读全文
        content = fetch_article_content(link)
        if not content or len(content) < 100:
            print(f"  → ⚠️ {title[:30]}... 内容过短，跳过")
            stats["errors"] += 1
            continue

        # 2.5 非游戏内容硬过滤（在 DeepSeek 调用前拦截，节省 API 费用）
        if _is_non_game_content(title, content):
            print(f"  → 🚫 非游戏内容: {title[:30]}...")
            stats["filtered"] += 1
            continue

        # 3. DeepSeek 分析（分类 + 提取一步完成）
        analysis = analyze_article(title, content, name)
        if not analysis:
            stats["errors"] += 1
            continue

        info_types = analysis.get("info_types", [])
        print(f"  → [{','.join(info_types)}] {title[:40]}...")

        # 4. 跳过纯 teardown
        if info_types == ["teardown"]:
            print(f"    ⏭️ 产品拆解，跳过")
            stats["filtered"] += 1
            continue

        # 5. 战略库写入（data/ad/biz 类型 + 硬过滤）
        strategy = analysis.get("strategy")
        if strategy and any(t in info_types for t in ("data", "ad", "biz")):
            if _is_blacklisted_strategy(title):
                print(f"    🚫 战略库硬过滤: {title[:30]}...")
                stats["filtered"] += 1
                continue
            path = write_strategy_entry(art, {"strategy": strategy, "type": "strategy"}, name)
            if path:
                stats["strategy"] += 1
                print(f"    ✅ 战略库: {path.name}")
            else:
                stats["filtered"] += 1
                print(f"    ⏭️ 战略库过滤（value_score ≤ 2）")

        # 6. 竞品库写入（new 类型，只收新产品 + 硬过滤大厂）
        new_products = analysis.get("new_products", [])
        for prod in new_products:
            if not prod.get("is_genuinely_new", False):
                continue
            # 硬过滤：大厂黑名单（代码层强制，不依赖 DeepSeek）
            if _is_blacklisted_product(prod):
                print(f"    🚫 竞品库硬过滤: {prod.get('name','')} (大厂/3A/超休闲)")
                continue
            path = write_product_entry(prod, art, name)
            if path:
                stats["product"] += 1
                print(f"    ✅ 竞品库: {path.name} ({prod.get('newness_reason', '')})")

        # 限速：避免 DeepSeek 频率限制
        time.sleep(2)

    return stats


def main():
    parser = argparse.ArgumentParser(description="每日信息收集")
    parser.add_argument("--test", action="store_true", help="测试模式：只跑 GameLook，最多 3 篇")
    parser.add_argument("--max", type=int, default=5, help="每个来源最多处理几篇")
    args = parser.parse_args()

    # 检查环境
    for key in ("WX_API_KEY", "DEEPSEEK_API_KEY"):
        if not os.environ.get(key):
            print(f"❌ {key} 未设置")
            sys.exit(1)

    if args.test:
        sources = TEST_SOURCES
    else:
        from archive.tools.scripts.source_registry import SOURCES
        sources = [{"name": s["name"], "fakeid": s["fakeid"], "line": ",".join(s["types"]), "tier": "T1"} for s in SOURCES]
    max_articles = 3 if args.test else args.max

    print(f"{'='*50}")
    print(f"📊 每日信息收集 {'[测试模式]' if args.test else ''}")
    print(f"来源数: {len(sources)} | 每源最多: {max_articles} 篇")
    print(f"{'='*50}")

    all_stats = []
    for source in sources:
        if not source.get("fakeid"):
            print(f"\n⏭️ {source['name']}: 无 fakeid，跳过")
            continue
        stats = process_source(source, max_articles=max_articles)
        all_stats.append(stats)
        time.sleep(3)

    # 汇总
    print(f"\n{'='*50}")
    print("📊 汇总")
    total_fetched = sum(s["fetched"] for s in all_stats)
    total_strategy = sum(s["strategy"] for s in all_stats)
    total_product = sum(s["product"] for s in all_stats)
    total_filtered = sum(s["filtered"] for s in all_stats)
    total_errors = sum(s["errors"] for s in all_stats)
    print(f"  拉取: {total_fetched} | 战略库: {total_strategy} | 竞品库: {total_product} | 过滤: {total_filtered} | 错误: {total_errors}")
    for s in all_stats:
        print(f"  {s['source']}: 拉{s['fetched']} 战{s['strategy']} 竞{s['product']} 滤{s['filtered']} 错{s['errors']}")


if __name__ == "__main__":
    main()
