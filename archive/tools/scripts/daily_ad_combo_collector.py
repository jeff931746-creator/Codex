#!/usr/bin/env python3
"""
Daily Ad Combo Collector
每日自动收集买量组合候选（题材 × 画风），生成待评估列表，通过飞书通知用户。
独立脚本，由系统 cron 调用，零 Claude token 消耗。
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
LIBRARY_ROOT = Path(os.environ.get(
    "AD_COMBO_LIBRARY_ROOT",
    "/Users/mt/Documents/Codex/reference/资料/买量组合库"
))
STATE_FILE = Path(os.environ.get(
    "AD_COMBO_STATE_FILE",
    "/tmp/ad_combo_candidates.json"
))
LOG_FILE = Path(os.environ.get(
    "AD_COMBO_LOG_FILE",
    "/tmp/ad_combo_collector.log"
))
FEISHU_BRIDGE_URL = os.environ.get(
    "FEISHU_WEBHOOK_URL",
    "http://127.0.0.1:3002/send_message"
)
FEISHU_CHAT_ID = os.environ.get("FEISHU_TARGET_CHAT_ID", "")

# ========== API key ==========
api_key = os.environ.get("SILICONFLOW_API_KEY", "").strip()
if not api_key:
    raise RuntimeError("SILICONFLOW_API_KEY 未设置")

# ========== 日志 ==========
def log(msg: str):
    timestamp = datetime.now().isoformat(timespec='seconds')
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ========== LLM 调用 ==========
def call_llm(prompt: str, max_tokens: int = 2000) -> str:
    """大模型调用（榜单获取用）"""
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "Pro/zai-org/GLM-5.1",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.3
    }

    ctx = ssl.create_default_context(cafile=certifi.where())
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        log(f"LLM 调用失败: {e}")
        return ""

# ========== WebSearch 调用（用 LLM 知识库代替联网搜索）==========
def web_search(query: str) -> str:
    """用 LLM 训练知识回答搜索问题（SiliconFlow 不支持真正联网搜索）"""
    prompt = f"请列举你知道的与以下主题相关的具体名称（游戏名、剧名、小说名、题材名等），直接给出名称列表，每行一个，不需要解释：\n\n主题：{query}"
    result = call_llm(prompt, max_tokens=1000)
    if not result:
        log(f"web_search 调用失败: {query}")
    return result

# ========== 蓝海分计算 ==========
def calc_demand_score(theme: str, sources: list, frequency: int) -> int:
    score = 0
    sources = _as_list(sources)
    if any(("短剧" in s or "小说" in s or "动漫" in s) for s in sources):
        score += 3
    if frequency >= 2:
        score += 2
    return score

def _assess_competition_one_batch(themes_batch: list) -> dict:
    """单批次竞争评估（最多20个题材），返回 {theme: (deduction, risk_desc)}"""
    theme_list = "\n".join(f"- {t}" for t in themes_batch)
    prompt = f"""对以下每个题材，评估其在手游市场的竞争密度。

题材列表：
{theme_list}

评估维度：
- 同题材在售手游数量（多=竞争大）
- 是否有腾讯/网易/米哈游等大厂产品
- 买量素材是否已高度饱和

必须返回 JSON 对象（不是数组），key 是题材名，value 是对象：
{{"题材名": {{"count": 数量整数, "major": true或false, "saturated": true或false}}, ...}}
只返回 JSON 对象，不要其他文字，不要 markdown 代码块。"""

    result = call_llm(prompt, max_tokens=1000)
    if not result:
        return {}

    try:
        data = _parse_json(result)
        # 防御：GLM 偶尔返回 list，跳过
        if isinstance(data, list):
            log(f"竞争评估返回了 list，跳过该批次")
            return {}
        out = {}
        for theme, info in data.items():
            if not isinstance(info, dict):
                continue
            deduction = 0
            risks = []
            count = info.get("count", 0)
            if isinstance(count, (int, float)):
                count = int(count)
                if count > 5:
                    deduction += 3
                    risks.append(f"同题材游戏约{count}款")
                elif count > 2:
                    deduction += 1
                    risks.append(f"同题材游戏约{count}款")
            if info.get("major"):
                deduction += 2
                risks.append("大厂已入场")
            if info.get("saturated"):
                deduction += 1
                risks.append("买量已饱和")
            out[theme] = (deduction, "、".join(risks) if risks else "低")
        return out
    except Exception as e:
        log(f"竞争评估批次解析失败: {e}")
        return {}


def assess_competition_batch(themes: list) -> dict:
    """批量评估竞争密度，每批最多20个并行，合并结果"""
    if not themes:
        return {}

    BATCH_SIZE = 20
    batches = [themes[i:i+BATCH_SIZE] for i in range(0, len(themes), BATCH_SIZE)]
    log(f"竞争评估：{len(themes)} 个题材分 {len(batches)} 批并行...")

    out = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(_assess_competition_one_batch, b): i for i, b in enumerate(batches)}
        for future in concurrent.futures.as_completed(futures):
            try:
                out.update(future.result())
            except Exception as e:
                log(f"竞争评估批次执行失败: {e}")
    return out

def assess_competition(theme: str) -> tuple[int, str]:
    """单题材竞争评估（兜底用）"""
    result = assess_competition_batch([theme])
    return result.get(theme, (0, "未知"))

def _as_list(value) -> list:
    """Normalize LLM string/list fields into a compact list."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    text = str(value).strip()
    if not text:
        return []
    return [part.strip() for part in re.split(r"[、,，;；\n]+", text) if part.strip()]

def _merge_unique_list(left, right) -> list:
    seen = set()
    out = []
    for item in _as_list(left) + _as_list(right):
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out

def _normalize_monetization(value: str) -> str:
    text = str(value or "").strip()
    upper = text.upper().replace(" ", "")
    if not text:
        return "未知"
    if "IAP+IAA" in upper or "混合" in text:
        return "IAP+IAA"
    if "IAA" in upper or "广告" in text or "内容消费" in text or "ONLY" in upper:
        return "IAA主导"
    if "IAP" in upper or "内购" in text or "付费" in text:
        return "IAP主导"
    return "未知"

def _normalize_market_status(value: str, blue_ocean_score_value: int = 0, competition_risk: str = "") -> str:
    text = str(value or "").strip()
    risk = str(competition_risk or "")
    if "浅" in text and "红" in text:
        return "浅红海"
    if "红" in text:
        return "红海"
    if "蓝" in text or "稀缺" in text:
        return "蓝海"
    if any(flag in risk for flag in ("大厂", "饱和", "同题材游戏约")):
        return "红海"
    if blue_ocean_score_value >= 3:
        return "蓝海"
    if blue_ocean_score_value >= 1:
        return "浅红海"
    return "红海"

def _normalize_recommendation(value: str) -> str:
    text = str(value or "").strip()
    if "差异" in text:
        return "差异化后保留"
    if "改写" in text or "复评" in text:
        return "改写后复评"
    if "排除" in text or "不保留" in text:
        return "排除"
    if "保留" in text:
        return "保留"
    return "未知"

def _pick_first(*values) -> str:
    for value in values:
        if isinstance(value, list):
            value = "、".join(_as_list(value))
        text = str(value or "").strip()
        if text:
            return text
    return ""

def _theme_name(item) -> str:
    if isinstance(item, dict):
        return str(item.get("theme") or item.get("name") or "").strip()
    return str(item or "").strip()

def _format_theme_for_assessment(item) -> str:
    if not isinstance(item, dict):
        return f"- 题材：{item}"
    hooks = "、".join(_as_list(item.get("ad_creative_hooks"))[:5])
    return (
        f"- 题材：{_theme_name(item)}；"
        f"游戏幻想：{item.get('game_fantasy', '')}；"
        f"承接玩法：{item.get('gameplay_carrier', '')}；"
        f"付费驱动：{item.get('iap_driver', '')}；"
        f"素材母题：{hooks}；"
        f"风险标签：{item.get('risk_tag', '')}；"
        f"来源：{'、'.join(_as_list(item.get('sources') or item.get('source')))}"
    )

def _merge_theme_record(existing: dict, incoming: dict) -> dict:
    existing["frequency"] = existing.get("frequency", 0) + incoming.get("frequency", 1)
    existing["sources"] = _merge_unique_list(existing.get("sources"), incoming.get("sources") or incoming.get("source"))
    existing["reference_games"] = _merge_unique_list(existing.get("reference_games"), incoming.get("reference_games"))
    existing["ad_creative_hooks"] = _merge_unique_list(existing.get("ad_creative_hooks"), incoming.get("ad_creative_hooks"))
    for key in ("game_fantasy", "gameplay_carrier", "iap_driver", "risk_tag"):
        if not existing.get(key) and incoming.get(key):
            existing[key] = incoming.get(key)
    return existing

def _standardize_assessment(theme: dict, info: dict) -> dict:
    score = info.get("score", 0)
    try:
        score = max(0, min(6, int(score)))
    except (TypeError, ValueError):
        score = 0

    monetization_fit = _normalize_monetization(
        info.get("monetization_fit") or info.get("monetization") or theme.get("monetization_fit") or theme.get("monetization")
    )
    market_status = _normalize_market_status(
        info.get("market_status") or theme.get("market_status"),
        theme.get("blue_ocean_score", 0),
        theme.get("competition_risk", "")
    )
    recommendation = _normalize_recommendation(info.get("recommendation") or theme.get("recommendation"))
    differentiation_angle = _pick_first(info.get("differentiation_angle"), theme.get("differentiation_angle"))

    if recommendation == "未知":
        if monetization_fit == "IAA主导":
            recommendation = "排除"
        elif market_status == "红海":
            recommendation = "差异化后保留"
        else:
            recommendation = "保留"

    if market_status in ("红海", "浅红海"):
        if not differentiation_angle and recommendation in ("保留", "差异化后保留"):
            recommendation = "改写后复评"
        elif differentiation_angle and recommendation == "保留":
            recommendation = "差异化后保留"

    return {
        "score": score,
        "reason": _pick_first(info.get("reason"), theme.get("game_viability_reason"), "未评估"),
        "monetization_fit": monetization_fit,
        "market_status": market_status,
        "recommendation": recommendation,
        "gameplay_carrier": _pick_first(info.get("gameplay_carrier"), theme.get("gameplay_carrier")),
        "differentiation_angle": differentiation_angle,
        "ad_creative_hooks": _merge_unique_list(info.get("ad_creative_hooks"), theme.get("ad_creative_hooks")),
    }

def _theme_sort_key(theme: dict):
    recommendation_rank = {"保留": 3, "差异化后保留": 2, "改写后复评": 1, "排除": 0, "未知": 0}
    monetization_rank = {"IAP主导": 3, "IAP+IAA": 2, "IAA主导": 0, "未知": 1}
    market_rank = {"蓝海": 3, "浅红海": 2, "红海": 1, "未知": 0}
    return (
        -recommendation_rank.get(theme.get("recommendation", "未知"), 0),
        -monetization_rank.get(theme.get("monetization_fit", "未知"), 0),
        -market_rank.get(theme.get("market_status", "未知"), 0),
        -len(_as_list(theme.get("ad_creative_hooks"))),
        -theme.get("game_viability_score", 0),
        -theme.get("blue_ocean_score", 0),
    )

def _md_cell(value) -> str:
    if isinstance(value, list):
        value = "、".join(_as_list(value))
    return str(value or "").replace("|", "/").replace("\n", " ")

_VIABILITY_PROMPT_TEMPLATE = """你是一名买量游戏立项评审，目标不是判断"能不能做成游戏"，而是判断一个题材是否能成为可投放验证的题材风格假设。
你要同时评估：题材幻想、玩法承接、商业化闭环、素材母题、市场竞争与差异化切口。

## 六个评估维度（各1分，满分6分，≥3分才合格）

1. **IAP/混合变现驱动力**：题材是否天然支撑"越付越强/越稀有/越领先"
   - 不得分：爽点是看结果、看热闹、看反转，只适合广告变现
   - 得分：角色/装备/技能/宠物/基地/资源/领地能持续成长并形成数值压力

2. **3秒买量钩子**：是否能用一眼画面讲清冲突和爽点
   - 不得分：需要大量文字解释，主要靠剧情理解
   - 得分：尸潮压境、Boss破门、抽到神宠、装备带出、基地进化等画面直观

3. **素材可持续性**：是否能持续产出素材母题
   - 不得分：只有一次性的反转/揭秘/测算结果
   - 得分：失败开局、升级爆发、稀有掉落、压迫翻盘、三选一、撤离贪婪等可重复拍

4. **玩法承接清晰度**：能否落到明确玩法载体
   - 不得分：只有设定，没有循环
   - 得分：塔防、割草、放置RPG、卡牌、搜打撤、模拟经营、SLG、肉鸽等承接清楚

5. **蓝海/差异化潜力**：题材是否供给不足，或红海中有明确切口
   - 不得分：大类红海且没有子题材/画风/玩法错位
   - 得分：蓝海子题材，或红海题材能给出清晰差异化切口

6. **受众-付费习惯匹配**：题材受众是否愿意为成长、稀缺、竞争或效率付费
   - 不得分：种田、日常、恋爱、温馨、治愈、情感、邻里（无对抗）
   - 得分：末世资源争夺、御兽进化、战争扩张、搜打撤装备带出、技能Build成长

## 硬性扣分规则（触发任一条直接 ≤2 分）

- 含"种田/日常/温馨/恋爱/治愈/邻里/宅斗"且无明确对抗元素
- 题材受众是轻娱乐消费者但玩法需要策略重度用户
- 爽点完全依赖剧情反转（打脸/掉马/复仇揭秘），无独立游戏目标
- 题材核心爽点是"看结果/看内容"而非"操控/积累/成长/带出"
- 红海题材没有子题材、画风、玩法或平台错位的差异化切口

## 分类要求

- **IAP主导蓝海**：IAP主导 + 蓝海/浅红海 + 保留
- **IAP+IAA混合潜力**：局内爽感强，广告可补资源/复活/加速，但长期仍有成长付费
- **好题材但红海**：需求强、竞争多，必须给出差异化切口，推荐结论通常为"差异化后保留"
- **IAA-only内容消费型**：看结果/看反转/看内容，若无法改写成成长或战斗结构则排除

## 变现模式判断

- **IAP主导**：角色/装备/技能/资源/领地等付费深度强
- **IAP+IAA**：局内爽感和广告点强，同时有装备、技能、Build、关卡或资源成长承接
- **IAA主导**：主要靠内容消费、一次性反转或结果揭示，缺少越付越强压力

## 市场状态判断

- **蓝海**：需求有证据，但同类游戏和买量素材明显少
- **浅红海**：已有供给，但仍有题材、画风、玩法或平台切口
- **红海**：竞品和素材都多，必须说明差异化切口

题材列表：
{theme_list}

返回 JSON 对象，key 是题材名，value 必须包含：
{{
  "score": 1-6,
  "reason": "指出最关键的通过/降级/排除理由",
  "monetization_fit": "IAP主导/IAP+IAA/IAA主导",
  "market_status": "蓝海/浅红海/红海",
  "recommendation": "保留/差异化后保留/改写后复评/排除",
  "gameplay_carrier": "塔防/割草/搜打撤/RPG/卡牌/放置/模拟经营/SLG/肉鸽等",
  "differentiation_angle": "蓝海可为空；浅红海或红海必须填写",
  "ad_creative_hooks": ["至少3个素材母题"]
}}
只返回 JSON 对象，不要其他文字，不要 markdown 代码块。"""


def _assess_viability_one_batch(themes_batch: list) -> dict:
    """单批次可玩性评估（最多15个题材）"""
    theme_list = "\n".join(_format_theme_for_assessment(t) for t in themes_batch)
    prompt = _VIABILITY_PROMPT_TEMPLATE.format(theme_list=theme_list)
    result = call_llm(prompt, max_tokens=3500)
    if not result:
        return {}
    try:
        data = _parse_json(result)
        if isinstance(data, list):
            log(f"可玩性评估返回了 list，跳过该批次")
            return {}
        return {k: v for k, v in data.items() if isinstance(v, dict) and "score" in v}
    except Exception as e:
        log(f"可玩性评估批次解析失败: {e}")
        return {}


def assess_game_viability_batch(themes: list) -> dict:
    """批量评估题材商业潜力，每批最多15个并行，合并结果"""
    if not themes:
        return {}

    BATCH_SIZE = 15
    batches = [themes[i:i+BATCH_SIZE] for i in range(0, len(themes), BATCH_SIZE)]
    log(f"商业潜力评估：{len(themes)} 个题材分 {len(batches)} 批并行...")

    out = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(_assess_viability_one_batch, b) for b in batches]
        for future in concurrent.futures.as_completed(futures):
            try:
                out.update(future.result())
            except Exception as e:
                log(f"商业潜力评估批次执行失败: {e}")
    return out

def blue_ocean_score(theme: str, sources: list, frequency: int, competition_map: dict = None) -> tuple[int, str]:
    demand = calc_demand_score(theme, sources, frequency)
    if competition_map and theme in competition_map:
        deduction, risk_desc = competition_map[theme]
    else:
        deduction, risk_desc = assess_competition(theme)
    score = demand - deduction
    return score, risk_desc

# ========== 数据发现模块 ==========
ENT_QUERIES = [
    ("小说", "2024-2025年网络小说（番茄小说/起点/晋江）中最火的细分题材"),
    ("短剧", "2024-2025年抖音/爱奇艺短剧中最火的细分题材"),
]

def fetch_entertainment_trends() -> list:
    """从泛娱乐内容中提取可游戏化幻想（并行，每源 20 个）"""
    log("开始获取泛娱乐可游戏化幻想（并行）...")

    def _fetch_one(source_topic):
        source, topic = source_topic
        prompt = f"""根据你对{topic}的了解，列出20个最适合转译成买量游戏的题材幻想。

要求：
- 必须具体（4-8个字），有明确画面感，不能是宽泛大类
- 禁止：修仙、仙侠、都市、恐怖、科幻、悬疑、历史、古代、现代（单独一词）
- 优先选择能承接成长、战斗、收集、资源争夺、撤离带出、基地建设、抽卡概率心理的题材
- 对算命、直播、怪谈、短剧反转等内容消费型题材，必须先尝试改写成可操控/可积累/可付费的游戏幻想；改写不了就不要输出
- 正确示例：虫族母巢进化、极寒末世囤货、民俗纸扎撤离、御兽血脉进化、天师镇邪收鬼

返回 JSON 数组：
[{{"theme": "题材名", "game_fantasy": "一句话游戏幻想", "gameplay_carrier": "塔防/割草/搜打撤/RPG/卡牌/放置/模拟经营/SLG/肉鸽等", "iap_driver": "成长/稀缺/竞争/抽卡/资源焦虑等付费驱动", "ad_creative_hooks": ["至少3个素材母题"], "risk_tag": "蓝海/浅红海/红海/内容消费风险", "frequency": 热度分1-5}}]
只返回 JSON 数组，不要其他文字，不要 markdown 代码块。"""
        out = call_llm(prompt, max_tokens=1000)
        items = []
        if out:
            try:
                items = _parse_json(out)
                for item in items:
                    item["source"] = source
                    item["sources"] = [source]
                    item["ad_creative_hooks"] = _as_list(item.get("ad_creative_hooks"))
            except Exception as e:
                log(f"泛娱乐题材解析失败（{source}）: {e}")
        log(f"泛娱乐（{source}）提取到 {len(items)} 个题材")
        return items

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(_fetch_one, sq) for sq in ENT_QUERIES]
        for future in concurrent.futures.as_completed(futures):
            try:
                results.extend(future.result())
            except Exception as e:
                log(f"泛娱乐并行调用失败: {e}")

    return results

def fetch_game_rankings() -> dict:
    """获取游戏榜单数据（并行化）"""
    log("开始获取游戏榜单（并行）...")

    queries = {
        "ios":    "iOS 游戏免费榜 Top 50 2026年4月",
        "taptap": "TapTap 热门游戏榜单 2026年4月",
        "wechat": "微信小游戏热榜 2026年4月",
    }

    def _fetch_one(key_query):
        key, query = key_query
        result = web_search(query)
        games = parse_game_list(result, key) if result else []
        return key, games

    rankings = {"ios": [], "taptap": [], "wechat": []}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(_fetch_one, kq): kq[0] for kq in queries.items()}
        for future in concurrent.futures.as_completed(futures):
            try:
                key, games = future.result()
                rankings[key] = games
            except Exception as e:
                log(f"榜单获取失败（{futures[future]}）: {e}")

    log(f"榜单获取完成: iOS {len(rankings['ios'])} 款, TapTap {len(rankings['taptap'])} 款, 微信 {len(rankings['wechat'])} 款")
    return rankings

def _parse_json(text: str):
    """从 LLM 输出中提取 JSON，自动修复常见格式问题"""
    text = text.strip()
    # 去除 markdown 代码块
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    text = text.strip()
    # 修复 LLM 漏写逗号：}{ → },{
    text = re.sub(r"\}\s*\{", "},{", text)
    # 修复单引号
    text = text.replace("'", '"')
    # 修复尾逗号 ,] 或 ,}
    text = re.sub(r",\s*([}\]])", r"\1", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # 兜底：用正则提取所有 {...} 对象
        objects = re.findall(r'\{[^{}]+\}', text)
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

def parse_game_list(text: str, source: str) -> list:
    """从搜索结果中提取游戏列表"""
    prompt = f"""
从以下内容中提取手机游戏/小游戏名称列表，返回 JSON 数组：
[{{"name": "游戏名", "rank": 排名数字}}]

只返回 JSON 数组，不要其他任何文字，不要 markdown 代码块。如果无法提取，返回 []。

内容：
{text[:1500]}
"""
    result = call_llm(prompt, max_tokens=1000)
    try:
        games = _parse_json(result)
        return [{"name": g["name"], "rank": g.get("rank", 999), "source": source} for g in games]
    except Exception:
        return []

def extract_themes(rankings: dict, entertainment_themes: list) -> list:
    """从游戏榜单 + 泛娱乐热榜提取题材风格假设"""
    log("开始提取题材风格假设...")

    all_games = []
    for source, games in rankings.items():
        all_games.extend([g["name"] for g in games[:20]])

    games_text = "、".join(all_games[:30])
    prompt = f"""
从以下游戏列表中提取具体的买量题材风格假设，要求：
- 必须是具体子题材，不能是宽泛大类（禁止："修仙"、"三国"、"末日"等单独宽泛词）
- 必须补充游戏幻想、玩法承接、IAP/IAP+IAA付费驱动、至少3个素材母题
- 红海题材可以输出，但必须说明差异化切口；内容消费型题材必须先改写成可操控/积累/成长结构
- 正确示例：末日丧尸生存、修仙宗门经营、民俗纸扎撤离、克苏鲁地下城、虫族母巢进化
- 每个题材标签 4-8 个字，有明确画面感和场景感

返回 JSON 数组：
[{{"theme": "题材名", "reference_games": ["游戏1", "游戏2"], "frequency": 出现次数, "game_fantasy": "一句话游戏幻想", "gameplay_carrier": "塔防/割草/搜打撤/RPG/卡牌/放置/模拟经营/SLG/肉鸽等", "iap_driver": "成长/稀缺/竞争/抽卡/资源焦虑等付费驱动", "ad_creative_hooks": ["至少3个素材母题"], "risk_tag": "蓝海/浅红海/红海/内容消费风险"}}]

只返回 JSON 数组，不要其他任何文字，不要 markdown 代码块。

游戏列表：
{games_text}
"""
    game_themes = []
    result = call_llm(prompt, max_tokens=1500)
    try:
        game_themes = _parse_json(result)
        for t in game_themes:
            t.setdefault("sources", ["游戏榜单"])
            t["ad_creative_hooks"] = _as_list(t.get("ad_creative_hooks"))
    except Exception:
        log("游戏题材提取失败")

    # 合并泛娱乐题材
    ent_map: dict = {}
    for et in entertainment_themes:
        name = et.get("theme", "")
        if not name:
            continue
        meta = {
            "theme": name,
            "reference_games": et.get("reference_games", []),
            "frequency": et.get("frequency", 1),
            "sources": et.get("sources") or [et.get("source", "短剧")],
            "game_fantasy": et.get("game_fantasy", ""),
            "gameplay_carrier": et.get("gameplay_carrier", ""),
            "iap_driver": et.get("iap_driver", ""),
            "ad_creative_hooks": _as_list(et.get("ad_creative_hooks")),
            "risk_tag": et.get("risk_tag", "")
        }
        if name not in ent_map:
            ent_map[name] = meta
        else:
            ent_map[name] = _merge_theme_record(ent_map[name], meta)

    # 若游戏题材与泛娱乐重叠，合并 sources
    game_themes = [t for t in game_themes if isinstance(t, dict) and "theme" in t]
    game_theme_names = {t["theme"] for t in game_themes}
    for name, meta in ent_map.items():
        if name in game_theme_names:
            for t in game_themes:
                if t["theme"] == name:
                    t.setdefault("sources", ["游戏榜单"])
                    _merge_theme_record(t, meta)
        else:
            game_themes.append(meta)

    log(f"合并后共 {len(game_themes)} 个题材风格假设（含泛娱乐）")
    return game_themes

def extract_art_styles(rankings: dict) -> list:
    """从游戏中提取画风标签"""
    log("开始提取画风...")

    all_games = []
    for source, games in rankings.items():
        all_games.extend([g["name"] for g in games[:20]])

    if not all_games:
        return []

    games_text = "、".join(all_games[:30])
    prompt = f"""
从以下游戏列表中提取画风标签（如：第五人格画风、像素复古、黑神话国风、赛博朋克2.0、水墨3D等）。
返回 JSON 数组：
[{{"art_style": "画风名", "reference_games": ["游戏1", "游戏2"], "frequency": 出现次数}}]

只返回 JSON，不要其他文字。

游戏列表：
{games_text}
"""
    result = call_llm(prompt, max_tokens=1500)
    try:
        styles = _parse_json(result)
        log(f"提取到 {len(styles)} 个画风")
        return styles
    except:
        log("画风提取失败")
        return []

def identify_combos(themes: list, art_styles: list) -> list:
    """识别题材幻想 × 画风 × 玩法承接组合"""
    log("开始识别题材风格组合...")

    if not themes or not art_styles:
        return []

    theme_lines = []
    for t in themes[:12]:
        hooks = "、".join(_as_list(t.get("ad_creative_hooks"))[:3])
        theme_lines.append(
            f"- {t['theme']}｜幻想：{t.get('game_fantasy', '')}｜玩法：{t.get('gameplay_carrier', '')}｜付费：{t.get('iap_driver', '')}｜素材：{hooks}"
        )
    themes_text = "\n".join(theme_lines)
    styles_text = "、".join([s["art_style"] for s in art_styles[:10]])

    prompt = f"""
从以下题材幻想和画风中，识别有潜力的买量组合（题材幻想 × 画风 × 玩法承接）。
优先选择：
1. 3秒素材画面强，缩略图能看出冲突或爽点
2. 能承接 IAP 或 IAP+IAA：装备/技能/宠物/资源/关卡/Build/撤离带出
3. 红海题材必须有差异化切口，不能只是常见大类换皮
4. 画风能放大题材差异，而不是单纯跟随榜单常见风格

返回 JSON 数组（最多 5 个）：
[{{"theme": "题材名", "art_style": "画风名", "gameplay_carrier": "承接玩法", "monetization_fit": "IAP主导/IAP+IAA", "creative_hook": "最强素材母题", "reference_game": "参考游戏（如有）", "reason": "推荐理由"}}]

只返回 JSON，不要其他文字。

题材：
{themes_text}

画风：{styles_text}
"""
    result = call_llm(prompt, max_tokens=2000)
    try:
        combos = _parse_json(result)
        log(f"识别到 {len(combos)} 个组合")
        return combos
    except:
        log("组合识别失败")
        return []

_BRAINSTORM_BATCHES = [
    ("动作/战斗/生存类", "末世生存、怪物猎杀、异能战斗、太空战争、地下城探险"),
    ("策略/经营/建造类", "基地建设、资源争夺、领地扩张、星球殖民、文明重建"),
    ("内容消费转游戏化改写类", "玄学算命、民俗怪谈、直播热度、短剧打脸、身份反转"),
]

def _brainstorm_one_batch(batch_info: tuple) -> list:
    focus, examples = batch_info
    prompt = f"""你是一名买量游戏立项专家。请列举15个中国移动游戏市场中值得验证的题材风格假设，聚焦"{focus}"方向。

筛选标准：
1. 受众需求已在小说/短剧/动漫中被验证（有大量粉丝）
2. 题材能支撑重复对抗/建造/收集/撤离/成长/抽卡类核心循环，不是纯叙事消耗品
3. 至少能给出3个可拍买量素材母题
4. 如果题材本身偏内容消费（算命/直播/打脸/反转），必须改写成可操控、可积累、可成长、可付费的游戏幻想
5. 红海题材可以输出，但必须给出子题材、玩法错位、画风错位或平台错位的差异化切口

题材格式：4-8个字，具体有画面感。
参考方向（举例，不要直接照抄）：{examples}

返回 JSON 数组：
[{{"theme": "题材名", "game_fantasy": "一句话游戏幻想", "gameplay_carrier": "塔防/割草/搜打撤/RPG/卡牌/放置/模拟经营/SLG/肉鸽等", "iap_driver": "成长/稀缺/竞争/抽卡/资源焦虑等付费驱动", "ad_creative_hooks": ["至少3个素材母题"], "risk_tag": "蓝海/浅红海/红海/内容消费风险", "demand_source": "需求来源（小说/短剧/动漫等）", "frequency": 热度分1-5}}]
只返回 JSON 数组，不要其他文字，不要 markdown 代码块。"""
    out = call_llm(prompt, max_tokens=2200)
    if not out:
        return []
    try:
        items = _parse_json(out)
        for item in items:
            item.setdefault("source", item.pop("demand_source", "头脑风暴"))
            item.setdefault("sources", [item["source"]])
            item["ad_creative_hooks"] = _as_list(item.get("ad_creative_hooks"))
        return items
    except Exception as e:
        log(f"蓝海头脑风暴批次解析失败（{focus}）: {e}")
        return []


def brainstorm_blue_ocean_direct() -> list:
    """直接头脑风暴题材风格假设（多批并行，避免单次超时）"""
    log(f"开始直接题材风格头脑风暴（{len(_BRAINSTORM_BATCHES)}批并行）...")
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(_brainstorm_one_batch, b) for b in _BRAINSTORM_BATCHES]
        for future in concurrent.futures.as_completed(futures):
            try:
                results.extend(future.result())
            except Exception as e:
                log(f"蓝海头脑风暴并行调用失败: {e}")
    log(f"直接头脑风暴提取到 {len(results)} 个题材风格假设")
    return results


# ========== 输出：题材总表（持久化主表）==========
MASTER_TABLE_FILE = LIBRARY_ROOT / "题材总表.md"

def update_theme_master_table(state: dict):
    """从 JSON 状态重新生成题材总表.md（按商业潜力排序，完整覆盖写入）"""
    themes = state.get("candidates", {}).get("themes", [])
    if not themes:
        log("题材队列为空，跳过总表更新")
        return

    sorted_themes = sorted(themes, key=_theme_sort_key)

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# 题材总表（按商业化买量潜力排序）",
        "",
        f"> 更新时间：{now}　　共 {len(sorted_themes)} 个题材",
        "",
        "| 题材 | 商业化 | 市场状态 | 推荐结论 | 玩法承接 | 蓝海分 | 可玩性 | 差异化切口 | 素材钩子 | 可玩性说明 | 来源 | 发现日期 | 状态 |",
        "|------|--------|----------|----------|----------|--------|--------|------------|----------|------------|------|----------|------|",
    ]

    for t in sorted_themes:
        name = t.get("name", "")
        bo = t.get("blue_ocean_score", 0)
        via = t.get("game_viability_score", 0)
        via_reason = t.get("game_viability_reason", "")
        monetization = t.get("monetization_fit") or t.get("monetization", "未知")
        market_status = t.get("market_status", "未知")
        recommendation = t.get("recommendation", "未知")
        gameplay_carrier = t.get("gameplay_carrier", "")
        differentiation_angle = t.get("differentiation_angle", "")
        hooks = "、".join(_as_list(t.get("ad_creative_hooks"))[:3])
        source = t.get("source", "")
        discovered = t.get("discovered_at", "")[:10]
        status = t.get("status", "待评估")
        bo_str = f"+{bo}" if bo >= 0 else str(bo)
        lines.append(
            f"| {_md_cell(name)} | {_md_cell(monetization)} | {_md_cell(market_status)} | {_md_cell(recommendation)} | "
            f"{_md_cell(gameplay_carrier)} | {bo_str} | {via}/6 | {_md_cell(differentiation_angle)} | "
            f"{_md_cell(hooks)} | {_md_cell(via_reason)} | {_md_cell(source)} | {discovered} | {_md_cell(status)} |"
        )

    MASTER_TABLE_FILE.parent.mkdir(parents=True, exist_ok=True)
    MASTER_TABLE_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log(f"题材总表已更新: {MASTER_TABLE_FILE}（{len(sorted_themes)} 条）")


# ========== 去重与优先级模块 ==========
def load_existing_data() -> dict:
    """读取已有库数据"""
    existing = {
        "themes": set(),
        "art_styles": set(),
        "combos": set()
    }

    # 读取题材索引
    theme_index = LIBRARY_ROOT / "题材库" / "题材索引.md"
    if theme_index.exists():
        content = theme_index.read_text(encoding="utf-8")
        # 简单提取：查找 markdown 链接中的题材名
        for match in re.finditer(r'\[([^\]]+)\]', content):
            existing["themes"].add(match.group(1))

    # 读取画风索引
    style_index = LIBRARY_ROOT / "画风库" / "画风索引.md"
    if style_index.exists():
        content = style_index.read_text(encoding="utf-8")
        for match in re.finditer(r'\[([^\]]+)\]', content):
            existing["art_styles"].add(match.group(1))

    # 读取组合索引
    combo_index = LIBRARY_ROOT / "组合案例库" / "组合索引.md"
    if combo_index.exists():
        content = combo_index.read_text(encoding="utf-8")
        # 提取 "题材×画风" 格式
        for match in re.finditer(r'([^×\[\]]+)×([^×\[\]\.]+)', content):
            combo_key = f"{match.group(1).strip()}×{match.group(2).strip()}"
            existing["combos"].add(combo_key)

    log(f"已有数据: 题材 {len(existing['themes'])} 个, 画风 {len(existing['art_styles'])} 个, 组合 {len(existing['combos'])} 个")
    return existing

def deduplicate(candidates: dict, existing: dict) -> dict:
    """去重"""
    new_candidates = {
        "themes": [],
        "art_styles": [],
        "combos": []
    }

    # 去重题材
    for theme in candidates.get("themes", []):
        if theme["theme"] not in existing["themes"]:
            new_candidates["themes"].append(theme)

    # 去重画风
    for style in candidates.get("art_styles", []):
        if style["art_style"] not in existing["art_styles"]:
            new_candidates["art_styles"].append(style)

    # 去重组合
    for combo in candidates.get("combos", []):
        combo_key = f"{combo['theme']}×{combo['art_style']}"
        if combo_key not in existing["combos"]:
            new_candidates["combos"].append(combo)

    log(f"去重后: 题材 {len(new_candidates['themes'])} 个, 画风 {len(new_candidates['art_styles'])} 个, 组合 {len(new_candidates['combos'])} 个")
    return new_candidates

def calculate_priority(item: dict, item_type: str, competition_map: dict = None) -> tuple[str, int, str]:
    """计算蓝海分和优先级，返回 (优先级, 蓝海分, 竞争风险说明)"""
    theme_name = item.get("theme") or item.get("art_style") or item.get("name", "")
    sources = item.get("sources", ["游戏榜单"])
    frequency = item.get("frequency", 1)

    score, risk_desc = blue_ocean_score(theme_name, sources, frequency, competition_map)

    if score >= 3:
        priority = "high"
    elif score >= 1:
        priority = "medium"
    else:
        priority = "low"

    return priority, score, risk_desc

BROAD_THEMES = {"科幻", "恐怖", "古代", "现代", "都市", "历史", "战争", "爱情", "奇幻", "玄幻", "悬疑"}

def _is_specific_enough(name: str) -> bool:
    if len(name) < 4:
        return False
    if name in BROAD_THEMES:
        return False
    return True

def prioritize(candidates: dict) -> dict:
    """计算商业潜力分类；红海不硬过滤，IAA-only 排除。"""
    original_theme_count = len(candidates["themes"])

    # 批量竞争评估（单次调用）
    all_theme_names = [t.get("theme", "") for t in candidates["themes"] if _is_specific_enough(t.get("theme", ""))]
    competition_map = assess_competition_batch(all_theme_names) if all_theme_names else {}
    log(f"批量竞争评估完成：{len(competition_map)} 个题材")

    filtered_themes = []
    for theme in candidates["themes"]:
        priority, score, risk = calculate_priority(theme, "theme", competition_map)
        theme["priority"] = priority
        theme["blue_ocean_score"] = score
        theme["competition_risk"] = risk
        name = theme.get("theme", "")
        if not _is_specific_enough(name):
            log(f"[过滤] 题材「{name}」过于宽泛，排除")
        else:
            if score <= 0:
                log(f"[观察] 题材「{name}」蓝海分={score}（{risk}），进入商业潜力复评")
            filtered_themes.append(theme)

    filtered_styles = []
    for style in candidates["art_styles"]:
        priority, score, risk = calculate_priority(style, "art_style", {})
        style["priority"] = priority
        style["blue_ocean_score"] = score
        style["competition_risk"] = risk
        filtered_styles.append(style)  # 画风不过滤，仅标注

    for combo in candidates["combos"]:
        combo["priority"] = "medium"
        combo["blue_ocean_score"] = 0
        combo["competition_risk"] = "待评估"

    log(f"宽泛题材过滤后：题材 {len(filtered_themes)} 个（原 {original_theme_count} 个）")

    # ── 商业潜力分类 ──
    viability_map = assess_game_viability_batch(filtered_themes)
    log(f"商业潜力评估完成：{len(viability_map)} 个题材")

    viable_themes = []
    for theme in filtered_themes:
        name = theme["theme"]
        info = viability_map.get(name, {})
        if not info:
            theme["game_viability_score"] = 0
            theme["game_viability_reason"] = "商业潜力评估缺失，保留待复评"
            theme["monetization_fit"] = theme.get("monetization_fit", theme.get("monetization", "未知"))
            theme["monetization"] = theme["monetization_fit"]
            theme["market_status"] = _normalize_market_status(
                theme.get("market_status"),
                theme.get("blue_ocean_score", 0),
                theme.get("competition_risk", "")
            )
            theme["recommendation"] = "改写后复评"
            theme["gameplay_carrier"] = theme.get("gameplay_carrier", "")
            theme["differentiation_angle"] = theme.get("differentiation_angle", "")
            theme["ad_creative_hooks"] = _as_list(theme.get("ad_creative_hooks"))
            theme["priority"] = "low"
            log(f"[待复评] 题材「{name}」商业潜力评估缺失，保留到队列")
            viable_themes.append(theme)
            continue
        assessment = _standardize_assessment(theme, info)
        score = assessment["score"]
        reason = assessment["reason"]
        theme["game_viability_score"] = score
        theme["game_viability_reason"] = reason
        theme["monetization_fit"] = assessment["monetization_fit"]
        theme["monetization"] = assessment["monetization_fit"]
        theme["market_status"] = assessment["market_status"]
        theme["recommendation"] = assessment["recommendation"]
        theme["gameplay_carrier"] = assessment["gameplay_carrier"]
        theme["differentiation_angle"] = assessment["differentiation_angle"]
        theme["ad_creative_hooks"] = assessment["ad_creative_hooks"]

        if theme["recommendation"] == "保留" and theme["monetization_fit"] == "IAP主导" and theme["market_status"] == "蓝海":
            theme["priority"] = "high"
        elif theme["recommendation"] in ("保留", "差异化后保留") and theme["monetization_fit"] in ("IAP主导", "IAP+IAA"):
            theme["priority"] = "medium" if theme["recommendation"] == "差异化后保留" else "high"
        else:
            theme["priority"] = "low"

        if score < 3:
            log(f"[过滤] 题材「{name}」商业潜力={score}/6（{reason}），排除")
        elif theme["monetization_fit"] == "IAA主导" and theme["recommendation"] == "排除":
            log(f"[过滤] 题材「{name}」变现模式=IAA主导且建议排除（{reason}）")
        else:
            viable_themes.append(theme)

    log(f"商业潜力过滤后：题材 {len(viable_themes)} 个（原 {len(filtered_themes)} 个）")

    candidates["themes"] = sorted(viable_themes, key=_theme_sort_key)
    candidates["art_styles"] = sorted(filtered_styles, key=lambda x: -x["blue_ocean_score"])

    return candidates

# ========== 候选队列管理 ==========
def load_candidate_queue() -> dict:
    """读取候选队列"""
    if not STATE_FILE.exists():
        return {
            "last_run": None,
            "candidates": {"themes": [], "art_styles": [], "combos": []},
            "evaluated": {"combos": []}
        }

    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except:
        return {
            "last_run": None,
            "candidates": {"themes": [], "art_styles": [], "combos": []},
            "evaluated": {"combos": []}
        }

def save_candidate_queue(state: dict):
    """保存候选队列"""
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"候选队列已保存: {STATE_FILE}")

def merge_candidates(old_state: dict, new_candidates: dict) -> dict:
    """合并新旧候选（队列内去重）"""
    today = datetime.now().isoformat()

    existing_theme_names = {t["name"] for t in old_state["candidates"]["themes"]}
    existing_style_names = {s["name"] for s in old_state["candidates"]["art_styles"]}
    existing_combo_keys = {f"{c['theme']}×{c['art_style']}" for c in old_state["candidates"]["combos"]}

    # 合并题材
    for theme in new_candidates["themes"]:
        if theme["theme"] in existing_theme_names:
            continue
        existing_theme_names.add(theme["theme"])
        sources = _as_list(theme.get("sources") or theme.get("source") or ["游戏榜单"])
        old_state["candidates"]["themes"].append({
            "name": theme["theme"],
            "source": "、".join(sources),
            "discovered_at": today,
            "priority": theme["priority"],
            "blue_ocean_score": theme.get("blue_ocean_score", 0),
            "competition_risk": theme.get("competition_risk", "未知"),
            "game_viability_score": theme.get("game_viability_score", 0),
            "game_viability_reason": theme.get("game_viability_reason", ""),
            "game_fantasy": theme.get("game_fantasy", ""),
            "gameplay_carrier": theme.get("gameplay_carrier", ""),
            "iap_driver": theme.get("iap_driver", ""),
            "monetization_fit": theme.get("monetization_fit", theme.get("monetization", "未知")),
            "monetization": theme.get("monetization_fit", theme.get("monetization", "未知")),
            "market_status": theme.get("market_status", "未知"),
            "recommendation": theme.get("recommendation", "未知"),
            "differentiation_angle": theme.get("differentiation_angle", ""),
            "ad_creative_hooks": _as_list(theme.get("ad_creative_hooks")),
            "risk_tag": theme.get("risk_tag", ""),
            "status": "pending"
        })

    # 合并画风
    for style in new_candidates["art_styles"]:
        if style["art_style"] in existing_style_names:
            continue
        existing_style_names.add(style["art_style"])
        old_state["candidates"]["art_styles"].append({
            "name": style["art_style"],
            "source": f"榜单提取（{', '.join(style.get('reference_games', [])[:2])}）",
            "discovered_at": today,
            "priority": style["priority"],
            "status": "pending"
        })

    # 合并组合
    for combo in new_candidates["combos"]:
        key = f"{combo['theme']}×{combo['art_style']}"
        if key in existing_combo_keys:
            continue
        existing_combo_keys.add(key)
        old_state["candidates"]["combos"].append({
            "theme": combo["theme"],
            "art_style": combo["art_style"],
            "reference_game": combo.get("reference_game", ""),
            "gameplay_carrier": combo.get("gameplay_carrier", ""),
            "monetization_fit": combo.get("monetization_fit", ""),
            "creative_hook": combo.get("creative_hook", ""),
            "reason": combo.get("reason", ""),
            "source": "自动识别",
            "discovered_at": today,
            "priority": combo["priority"],
            "status": "pending",
            "user_notes": ""
        })

    old_state["last_run"] = today
    return old_state

# ========== 飞书通知模块 ==========
def format_daily_digest(new_candidates: dict) -> str:
    """格式化每日摘要"""
    today = datetime.now().strftime("%Y-%m-%d")

    lines = [
        f"【买量组合库 - 每日发现】{today}",
        "",
        "📊 今日收集概况",
        f"- 新题材：{len(new_candidates['themes'])} 个",
        f"- 新画风：{len(new_candidates['art_styles'])} 个",
        f"- 新组合：{len(new_candidates['combos'])} 个",
        ""
    ]

    # 题材风格假设
    top_themes = sorted(new_candidates["themes"], key=_theme_sort_key)
    if top_themes:
        lines.append("🔥 题材风格假设（买量钩子 × 商业承接 × 差异化）")
        for i, theme in enumerate(top_themes[:5], 1):
            sources = "、".join(_as_list(theme.get("sources") or theme.get("source") or ["游戏榜单"]))
            bo = theme.get("blue_ocean_score", 0)
            via = theme.get("game_viability_score", 0)
            via_reason = theme.get("game_viability_reason", "")
            monetization = theme.get("monetization_fit") or theme.get("monetization", "未知")
            market_status = theme.get("market_status", "未知")
            recommendation = theme.get("recommendation", "未知")
            gameplay_carrier = theme.get("gameplay_carrier", "")
            hooks = _as_list(theme.get("ad_creative_hooks"))
            first_hook = hooks[0] if hooks else ""
            bo_str = f"+{bo}" if bo >= 0 else str(bo)
            lines.append(
                f"{i}. {theme['theme']}（{monetization} / {market_status} / {recommendation} / "
                f"玩法：{gameplay_carrier or '未知'} / 蓝海分：{bo_str} / 商业潜力：{via}/6）"
            )
            if first_hook:
                lines.append(f"   - 素材钩子：{first_hook}")
            if via_reason:
                lines.append(f"   → {via_reason}")
        lines.append("")

    # 画风（标注蓝海分）
    top_styles = sorted(new_candidates["art_styles"], key=lambda x: -x.get("blue_ocean_score", 0))
    if top_styles:
        lines.append("🎨 候选画风")
        for i, style in enumerate(top_styles[:3], 1):
            score = style.get("blue_ocean_score", 0)
            sign = "+" if score >= 0 else ""
            lines.append(f"{i}. {style['art_style']}（蓝海分：{sign}{score}）")
        lines.append("")

    # 待评估组合
    if new_candidates["combos"]:
        lines.append("💡 待评估组合（题材幻想 × 画风 × 玩法承接）")
        for i, combo in enumerate(new_candidates["combos"][:5], 1):
            ref = f"参考游戏：{combo.get('reference_game', '无')}" if combo.get("reference_game") else ""
            lines.append(f"{i}. {combo['theme']} × {combo['art_style']}")
            if combo.get("gameplay_carrier") or combo.get("monetization_fit"):
                lines.append(
                    f"   - 承接：{combo.get('gameplay_carrier', '未知')} / 变现：{combo.get('monetization_fit', '未知')}"
                )
            if combo.get("creative_hook"):
                lines.append(f"   - 素材钩子：{combo['creative_hook']}")
            if combo.get("reason"):
                lines.append(f"   - 理由：{combo['reason']}")
            if ref:
                lines.append(f"   - {ref}")
            lines.append(f"   - 待补充：目标受众年龄段、付费意愿")
        lines.append("")

    lines.extend([
        "---",
        "💬 如需补充数据或触发完整评估，请回复：",
        "- \"补充 [组合名] [数据]\"",
        "- \"评估 [组合名]\"",
        "",
        "📁 详细数据已保存至本地库"
    ])

    return "\n".join(lines)

def send_feishu_notification(message: str):
    """通过飞书 bridge 发送通知"""
    if not FEISHU_CHAT_ID:
        log("FEISHU_TARGET_CHAT_ID 未设置，跳过飞书通知")
        return

    payload = {
        "chat_id": FEISHU_CHAT_ID,
        "message": message
    }

    try:
        req = urllib.request.Request(
            FEISHU_BRIDGE_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = resp.read().decode("utf-8")
            log(f"飞书通知已发送: {result}")
    except Exception as e:
        log(f"飞书通知发送失败: {e}")

# ========== 主流程 ==========
def main():
    log("========== 买量组合收集开始 ==========")

    # 1. 并行发起：游戏榜单 + 泛娱乐 + 直接头脑风暴
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        f_rankings      = executor.submit(fetch_game_rankings)
        f_entertainment = executor.submit(fetch_entertainment_trends)
        f_brainstorm    = executor.submit(brainstorm_blue_ocean_direct)

    rankings             = f_rankings.result()
    entertainment_themes = f_entertainment.result()
    brainstorm_themes    = f_brainstorm.result()
    log(f"三路发现合计：游戏榜单 {sum(len(v) for v in rankings.values())} 款，"
        f"泛娱乐 {len(entertainment_themes)} 个，"
        f"直接头脑风暴 {len(brainstorm_themes)} 个")

    # 2. 将头脑风暴题材规范化后并入娱乐趋势
    for item in brainstorm_themes:
        item.setdefault("source", "头脑风暴")
        item.setdefault("frequency", 3)
    entertainment_themes = entertainment_themes + brainstorm_themes

    # 3. 提取题材和画风
    themes = extract_themes(rankings, entertainment_themes)
    art_styles = extract_art_styles(rankings)

    raw_candidates = {
        "themes": themes,
        "art_styles": art_styles,
        "combos": []
    }

    # 5. 去重
    existing = load_existing_data()
    new_candidates = deduplicate(raw_candidates, existing)

    # 6. 商业潜力分类 + 过滤排序
    new_candidates = prioritize(new_candidates)

    # 7. 基于通过商业潜力分类的题材识别组合
    combo_candidates = identify_combos(new_candidates["themes"], new_candidates["art_styles"])
    existing_combo_keys = existing.get("combos", set())
    new_candidates["combos"] = []
    for combo in combo_candidates:
        key = f"{combo.get('theme', '')}×{combo.get('art_style', '')}"
        if key in existing_combo_keys:
            continue
        combo["priority"] = "medium"
        combo["blue_ocean_score"] = 0
        combo["competition_risk"] = "待评估"
        new_candidates["combos"].append(combo)

    # 8. 合并到候选队列
    state = load_candidate_queue()
    state = merge_candidates(state, new_candidates)
    save_candidate_queue(state)

    # 9. 更新持久化题材总表
    update_theme_master_table(state)

    # 10. 发送飞书通知
    if any(len(v) > 0 for v in new_candidates.values()):
        digest = format_daily_digest(new_candidates)
        send_feishu_notification(digest)
        log("今日有新发现，已发送飞书通知")
    else:
        log("今日无新发现")

    log("========== 买量组合收集完成 ==========")

if __name__ == "__main__":
    main()
