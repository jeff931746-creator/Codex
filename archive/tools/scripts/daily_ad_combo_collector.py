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
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

import certifi

# ========== 配置 ==========
LIBRARY_ROOT = Path(os.environ.get(
    "AD_COMBO_LIBRARY_ROOT",
    "/Users/mt/Documents/Codex/archive/资料/买量组合库"
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

# ========== API keys ==========
api_key = os.environ.get("SILICONFLOW_API_KEY", "").strip()
if not api_key:
    raise RuntimeError("SILICONFLOW_API_KEY 未设置")

# DeepSeek Flash 与 GLM 共用同一个 SiliconFlow key

# 当前 LLM backend："glm"（分析用）或 "deepseek"（收集用）
_llm_backend = "glm"

# ========== 日志 ==========
def log(msg: str):
    timestamp = datetime.now().isoformat(timespec='seconds')
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ========== LLM 调用 ==========
def _call_glm(prompt: str, max_tokens: int) -> str:
    """GLM-5.1 via SiliconFlow（分析阶段用）"""
    url = "https://api.siliconflow.cn/v1/chat/completions"
    payload = {
        "model": "Pro/zai-org/GLM-5.1",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.3
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    ctx = ssl.create_default_context(cafile=certifi.where())
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                 headers=headers, method="POST")
    with urllib.request.urlopen(req, context=ctx, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))["choices"][0]["message"]["content"].strip()


def _call_deepseek(prompt: str, max_tokens: int) -> str:
    """DeepSeek-V4-Flash via SiliconFlow（收集阶段用，与 GLM 共用 key）"""
    url = "https://api.siliconflow.cn/v1/chat/completions"
    payload = {
        "model": "deepseek-ai/DeepSeek-V4-Flash",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.3
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    ctx = ssl.create_default_context(cafile=certifi.where())
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                 headers=headers, method="POST")
    with urllib.request.urlopen(req, context=ctx, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))["choices"][0]["message"]["content"].strip()


def call_llm(prompt: str, max_tokens: int = 2000) -> str:
    """统一 LLM 调用入口，backend 由 _llm_backend 决定"""
    try:
        if _llm_backend == "deepseek":
            return _call_deepseek(prompt, max_tokens)
        return _call_glm(prompt, max_tokens)
    except Exception as e:
        log(f"LLM 调用失败 [{_llm_backend}]: {e}")
        return ""

# ========== WebSearch 调用（用 LLM 知识库代替联网搜索）==========
def web_search(query: str) -> str:
    """用 LLM 训练知识回答搜索问题"""
    prompt = f"请列举你知道的与以下主题相关的具体名称（游戏名、剧名、小说名、题材名等），直接给出名称列表，每行一个，不需要解释：\n\n主题：{query}"
    result = call_llm(prompt, max_tokens=1000)
    if not result:
        log(f"web_search 调用失败: {query}")
    return result

# ========== 市场数据采集（免费公开 API，无需 Key）==========

def fetch_itunes_market_data(keyword_cn: str, keyword_en: str = "") -> list:
    """iTunes Search API：查找与题材相关的 iOS 游戏（无需 API Key）"""
    seen_names: set = set()
    results: list = []

    keywords = [kw for kw in [keyword_cn, keyword_en] if kw and kw.strip()]
    for kw in keywords:
        url = (
            "https://itunes.apple.com/search"
            f"?term={urllib.parse.quote(kw)}"
            "&entity=software&mediaType=software&limit=20&country=cn"
        )
        try:
            ctx = ssl.create_default_context(cafile=certifi.where())
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            for app in data.get("results", []):
                genre = app.get("primaryGenreName", "")
                if "Game" not in genre and "游戏" not in genre:
                    continue
                name = app.get("trackName", "").strip()
                if name and name not in seen_names:
                    seen_names.add(name)
                    results.append({
                        "name": name,
                        "ratings": app.get("userRatingCount", 0),
                    })
        except Exception as e:
            log(f"[enrich] iTunes API 失败（{kw}）: {e}")
        time.sleep(0.5)

    return results


def fetch_steam_market_data(keyword_en: str) -> list:
    """Steam Store Search API：查找相关 PC 游戏（无需 API Key）"""
    if not keyword_en or not keyword_en.strip():
        return []
    url = (
        "https://store.steampowered.com/api/storesearch/"
        f"?term={urllib.parse.quote(keyword_en)}&l=english&cc=US&count=15"
    )
    try:
        ctx = ssl.create_default_context(cafile=certifi.where())
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return [{"name": g["name"]} for g in data.get("items", []) if g.get("name")]
    except Exception as e:
        log(f"[enrich] Steam API 失败（{keyword_en}）: {e}")
        return []


def compute_evidence_grade(itunes_count: int, steam_count: int) -> str:
    """根据真实 API 返回数量计算证据等级（按题材评估标准定义）
    A：两类外部强证据互相印证（竞品拆解 + 榜单数据）
    B：有明确竞品（单平台 3+ 款）
    C：无实证（纯 LLM 知识）
    """
    if itunes_count >= 3 and steam_count >= 3:
        return "A"
    if itunes_count >= 3 or steam_count >= 3:
        return "B"
    return "C"


def enrich_themes(state: dict) -> dict:
    """Enrich Agent：为 raw_candidates 中每个题材附加真实市场数据（iTunes + Steam）"""
    log("========== [丰富] 开始（iTunes + Steam API）==========")
    themes = state.get("raw_candidates", {}).get("themes", [])
    if not themes:
        log("[丰富] raw_candidates.themes 为空，跳过（请先运行 collect）")
        return state

    for i, theme in enumerate(themes):
        name = theme.get("theme") or theme.get("name", "")
        en_kw = theme.get("en_keyword", "")

        itunes_apps = fetch_itunes_market_data(name, en_kw)
        steam_games = fetch_steam_market_data(en_kw)

        evidence_grade = compute_evidence_grade(len(itunes_apps), len(steam_games))
        theme["market_data"] = {
            "itunes_apps":  itunes_apps[:5],
            "itunes_count": len(itunes_apps),
            "steam_games":  steam_games[:5],
            "steam_count":  len(steam_games),
            "evidence_grade": evidence_grade,
        }
        log(
            f"[丰富] {name}: iOS={len(itunes_apps)} / Steam={len(steam_games)} "
            f"→ 证据等级={evidence_grade} ({i+1}/{len(themes)})"
        )
        time.sleep(0.3)

    state["last_enrich"] = datetime.now().isoformat()
    save_candidate_queue(state)
    log(f"[丰富] 完成：共处理 {len(themes)} 个题材")
    log("========== [丰富] 结束 ==========")
    return state


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

    # 注入真实市场数据（enrich 阶段产生）
    market_str = ""
    md = item.get("market_data")
    if isinstance(md, dict):
        itunes_names = "、".join(a["name"] for a in md.get("itunes_apps", [])[:3]) or "无"
        steam_names  = "、".join(g["name"] for g in md.get("steam_games",  [])[:3]) or "无"
        market_str = (
            f"；【市场实证】iOS竞品{md['itunes_count']}款（{itunes_names}）"
            f"，Steam竞品{md['steam_count']}款（{steam_names}）"
            f"，证据等级:{md['evidence_grade']}"
        )

    return (
        f"- 题材：{_theme_name(item)}；"
        f"游戏幻想：{item.get('game_fantasy', '')}；"
        f"承接玩法：{item.get('gameplay_carrier', '')}；"
        f"付费驱动：{item.get('iap_driver', '')}；"
        f"素材母题：{hooks}；"
        f"风险标签：{item.get('risk_tag', '')}；"
        f"来源：{'、'.join(_as_list(item.get('sources') or item.get('source')))}"
        f"{market_str}"
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
    # 兼容旧格式（仅有 score 字段）
    if "score" in info and "dim1_demand" not in info:
        return {
            "effective_acquisition_score": 0.0,
            "roi_score": 0.0,
            "quadrant": "未知",
            "hard_fail_dims": [],
            "recommendation": "改写后复评",
            "reason": _pick_first(info.get("reason"), "旧格式数据，需重新评估"),
            "gameplay_carrier": _pick_first(info.get("gameplay_carrier"), theme.get("gameplay_carrier")),
            "entry_angle": _pick_first(info.get("differentiation_angle"), theme.get("differentiation_angle")),
            "ad_creative_hooks": _merge_unique_list(info.get("ad_creative_hooks"), theme.get("ad_creative_hooks")),
        }

    def _dim(key: str) -> int:
        val = info.get(key, 3)
        try:
            return max(1, min(5, int(val)))
        except (TypeError, ValueError):
            return 3

    acq_dims = [_dim("dim1_demand"), _dim("dim2_hook"), _dim("dim3_freshness"),
                _dim("dim4_competition"), _dim("dim5_cpi")]
    roi_dims = [_dim("dim6_ltv"), _dim("dim7_retention"), _dim("dim8_payment"),
                _dim("dim9_content"), _dim("dim10_payback")]

    ea = round(sum(acq_dims) / 5, 1)
    roi = round(sum(roi_dims) / 5, 1)

    dim_names = ["需求规模", "第一眼刺激", "素材新鲜度", "竞争压力", "CPI风险",
                 "LTV上限", "留存深度", "付费自然度", "内容效率", "回本压力"]
    all_dims = acq_dims + roi_dims
    hard_fail_dims = [dim_names[i] for i, v in enumerate(all_dims) if v < 3]

    if ea >= 4 and roi >= 4:
        quadrant = "高获量+高ROI"
    elif ea >= 4:
        quadrant = "高获量+低ROI"
    elif roi >= 4:
        quadrant = "低获量+高ROI"
    else:
        quadrant = "低获量+低ROI"

    # 均分 < 3 为轴级硬伤，直接不通过
    if ea < 3 or roi < 3:
        recommendation = "不通过"
    # 单维度 < 3 为项级硬伤，不得用均分掩盖；降为补证
    elif hard_fail_dims:
        recommendation = "补证"
    # 任一轴均分在 3-4 之间，需补证
    elif ea < 4 or roi < 4:
        recommendation = "补证"
    else:
        recommendation = "通过"

    # 从 market_data 读取证据等级（enrich 阶段已计算）
    md = theme.get("market_data")
    evidence_grade = md.get("evidence_grade", "C") if isinstance(md, dict) else "C"

    # 硬规则 0：人群对齐置信度 = 0 → 骗点素材，直接不通过
    raw_align = info.get("audience_alignment_confidence", 1.0)
    try:
        audience_alignment_confidence = float(raw_align)
    except (TypeError, ValueError):
        audience_alignment_confidence = 1.0
    if audience_alignment_confidence == 0:
        recommendation = "不通过"
        hard_fail_dims.append("点击-留存人群错位（骗点素材）")

    # 硬规则 1：进入切口为空 → 不得标"通过"
    entry_angle = _pick_first(info.get("entry_angle"), theme.get("entry_angle"), theme.get("differentiation_angle"))
    if (not entry_angle or len(entry_angle.strip()) < 10) and recommendation == "通过":
        recommendation = "补证"
        hard_fail_dims.append("进入切口为空")

    # 硬规则 2：按证据等级约束结论上限
    # C 级（纯 LLM）：只能是草稿，不进候选池
    # B 级（iOS/Steam 竞品存在）：证明市场存在，不证明买量成立 → 待买量验证
    # B+ 及以上（人工 Layer 2 核验通过）：由 SKILL 手动升级，代码不自动产出
    # A 级（跨平台市场强证据）：可通过
    if evidence_grade == "C" and recommendation == "通过":
        recommendation = "待买量验证"
    elif evidence_grade == "B" and recommendation == "通过":
        recommendation = "待买量验证"

    return {
        "effective_acquisition_score": ea,
        "roi_score": roi,
        "quadrant": quadrant,
        "hard_fail_dims": hard_fail_dims,
        "recommendation": recommendation,
        "evidence_grade": evidence_grade,
        "audience_alignment_confidence": audience_alignment_confidence,
        "reason": _pick_first(info.get("reason"), theme.get("game_viability_reason"), "未评估"),
        "gameplay_carrier": _pick_first(info.get("gameplay_carrier"), theme.get("gameplay_carrier")),
        "entry_angle": entry_angle,
        "ad_creative_hooks": _merge_unique_list(info.get("ad_creative_hooks"), theme.get("ad_creative_hooks")),
    }

def _theme_sort_key(theme: dict):
    quadrant_rank = {"高获量+高ROI": 4, "高获量+低ROI": 2, "低获量+高ROI": 2, "低获量+低ROI": 0, "未知": 0}
    recommendation_rank = {"通过": 4, "补证": 3, "待买量验证": 2, "改写后复评": 1, "不通过": 0, "差异化后保留": 3, "保留": 4, "排除": 0, "未知": 0}
    return (
        -quadrant_rank.get(theme.get("quadrant", "未知"), 0),
        -recommendation_rank.get(theme.get("recommendation", "未知"), 0),
        -theme.get("effective_acquisition_score", 0.0),
        -theme.get("roi_score", 0.0),
        -len(_as_list(theme.get("ad_creative_hooks"))),
    )

def _md_cell(value) -> str:
    if isinstance(value, list):
        value = "、".join(_as_list(value))
    return str(value or "").replace("|", "/").replace("\n", " ")

_THEME_EVAL_PROMPT = """你是一名买量游戏题材评审专家，依据"有效获量能力 × ROI承接能力"四象限方法论对每个题材评分。

## 有效获量轴（5个维度，各1-5分）

1. **需求规模**：主承接人群的剩余可触达规模是否足够大？（不评估题材整体热度，而评估"当前市场里还没被竞品覆盖、仍可被低成本触达"的人群体量）
   1分=人群小众或已被竞品饱和覆盖；3分=有一定体量但竞品已占据主要份额；5分=人群体量大且尚有明显空白（竞品少或覆盖浅）

2. **第一眼刺激**：第一张图是否有强识别、强情绪、强冲突？
   1分=需要大量解释才懂；3分=能看懂但无冲击；5分=一眼识别+立即触发情绪反应

3. **素材新鲜度**：和现有买量素材相比，是否有一眼可见的新表达？
   1分=高度同质化，素材桥段已被大量使用；3分=有差异但不突出；5分=新视角/新冲突/新人群切口

4. **竞争压力**（反向评分）：同题材、同人群、同素材表达是否已高度拥挤？
   1分=红海+腾讯/网易/米哈游已大量入场；3分=有竞争但有可见切口；5分=蓝海/供给明显不足

5. **CPI风险**：预估买量成本是否仍在产品可承接范围内？
   1分=行业公认CPI过高，难以回本；3分=成本不确定；5分=预期CPI合理可接受

有效获量均分 = (dim1+dim2+dim3+dim4+dim5) / 5

## ROI承接轴（5个维度，各1-5分）

6. **LTV上限**：题材是否支撑足够高的长期变现价值？
   1分=只适合广告变现，无成长付费点；3分=有部分付费承接；5分=多条成长线+自然付费深度

7. **留存深度**：是否能形成持续目标和重复行为？
   1分=一次性体验，看完即走；3分=有目标但牵引力不强；5分=身份目标+阶段推进+长期追求都清楚

8. **付费自然度**：付费是否服务体验而非硬塞？
   1分=强行插入付费破坏体验；3分=付费可接受但不自然；5分=付费完全服务题材情绪和成长逻辑

9. **内容效率**：题材内容是否能持续生产且成本可控？
   1分=需大量高成本美术/剧情才成立；3分=可以适度制作；5分=角色/关卡/皮肤可稳定低成本扩展

10. **回本压力**：预期回本周期是否匹配团队能力？
    1分=回本周期超长或获量成本极高；3分=回本路径不确定；5分=轻量产品快速验证或回本路径清晰

ROI承接均分 = (dim6+dim7+dim8+dim9+dim10) / 5

## 四象限判断

- 有效获量均分 ≥ 4 且 ROI均分 ≥ 4 → 高获量+高ROI（优先立项）
- 有效获量均分 ≥ 4 且 ROI均分 < 4 → 高获量+低ROI（需增加长线承接）
- 有效获量均分 < 4 且 ROI均分 ≥ 4 → 低获量+高ROI（需换外壳或找新切口）
- 有效获量均分 < 4 且 ROI均分 < 4 → 低获量+低ROI（不建议立项）

任一维度 < 3 → 该轴存在硬伤，必须说明，不得用均分掩盖。

## 进入切口

蓝海题材可为空；红海题材（竞争压力维度 ≤ 2）必须填写：
新表达 / 新人群 / 新玩法承接 / 成本优势，说明具体切口。

题材列表：
{theme_list}

返回 JSON 对象，key 是题材名，value 必须包含：
{{
  "dim1_demand": 1到5的整数,
  "dim2_hook": 1到5的整数,
  "dim3_freshness": 1到5的整数,
  "dim4_competition": 1到5的整数,
  "dim5_cpi": 1到5的整数,
  "dim6_ltv": 1到5的整数,
  "dim7_retention": 1到5的整数,
  "dim8_payment": 1到5的整数,
  "dim9_content": 1到5的整数,
  "dim10_payback": 1到5的整数,
  "entry_angle": "进入切口描述，蓝海可为空，红海必填",
  "reason": "一句话评审结论",
  "gameplay_carrier": "塔防/割草/搜打撤/RPG/卡牌/放置/模拟经营/SLG/肉鸽等",
  "ad_creative_hooks": ["至少3个素材母题"],
  "audience_alignment_confidence": 1.0
}}

audience_alignment_confidence 取值规则（必须输出数字，不得输出文字）：
- 1.0：素材钩子描述的冲突 = 游戏主循环，点击/留存/付费是同一批人
- 0.7：素材和主玩法有落差，但产品可以设计 D1 过渡机制承接
- 0.5：素材和玩法明显错位，但题材本身有市场，存在一定自然转化
- 0.0：素材和产品吸引的完全是不同人群，属于骗点素材
只返回 JSON 对象，不要其他文字，不要 markdown 代码块。"""


def _assess_viability_one_batch(themes_batch: list) -> dict:
    """单批次四象限评估（最多15个题材）"""
    theme_list = "\n".join(_format_theme_for_assessment(t) for t in themes_batch)
    prompt = _THEME_EVAL_PROMPT.format(theme_list=theme_list)
    result = call_llm(prompt, max_tokens=3500)
    if not result:
        return {}
    try:
        data = _parse_json(result)
        if isinstance(data, list):
            log(f"四象限评估返回了 list，跳过该批次")
            return {}
        return {k: v for k, v in data.items() if isinstance(v, dict) and ("dim1_demand" in v or "score" in v)}
    except Exception as e:
        log(f"四象限评估批次解析失败: {e}")
        return {}


def assess_game_viability_batch(themes: list) -> dict:
    """批量评估题材商业潜力，每批最多15个并行，合并结果"""
    if not themes:
        return {}

    BATCH_SIZE = 5
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
    ("海外影视", "2024-2025年Netflix/Disney+/HBO/全球票房最火的美剧英剧日剧动漫电影细分题材"),
    ("Steam", "Steam 2024-2025年最热门最畅销游戏的题材类型风格"),
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
        "steam":  "Steam 2025-2026年最热门最畅销游戏 Top 100 题材类型",
    }

    def _fetch_one(key_query):
        key, query = key_query
        result = web_search(query)
        games = parse_game_list(result, key) if result else []
        return key, games

    rankings = {"ios": [], "taptap": [], "wechat": [], "steam": []}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(_fetch_one, kq): kq[0] for kq in queries.items()}
        for future in concurrent.futures.as_completed(futures):
            try:
                key, games = future.result()
                rankings[key] = games
            except Exception as e:
                log(f"榜单获取失败（{futures[future]}）: {e}")

    log(f"榜单获取完成: iOS {len(rankings['ios'])} 款, TapTap {len(rankings['taptap'])} 款, "
        f"微信 {len(rankings['wechat'])} 款, Steam {len(rankings['steam'])} 款")
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
    ("海外IP/影视/Steam题材本土化", "西方奇幻冒险、赛博朋克生存、超级英雄能力、末日科幻殖民、北欧神话战斗、吸血鬼贵族成长、蒸汽朋克工业经营"),
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
[{{"theme": "题材名", "en_keyword": "English search keyword (2-4 words)", "game_fantasy": "一句话游戏幻想", "gameplay_carrier": "塔防/割草/搜打撤/RPG/卡牌/放置/模拟经营/SLG/肉鸽等", "iap_driver": "成长/稀缺/竞争/抽卡/资源焦虑等付费驱动", "ad_creative_hooks": ["至少3个素材母题"], "risk_tag": "蓝海/浅红海/红海/内容消费风险", "demand_source": "需求来源（小说/短剧/动漫等）", "frequency": 热度分1-5}}]
只返回 JSON 数组，不要其他文字，不要 markdown 代码块。"""
    out = call_llm(prompt, max_tokens=2200)
    if not out:
        return []
    try:
        items = _parse_json(out)
        for item in items:
            item.setdefault("source", item.pop("demand_source", "头脑风暴"))
            item.setdefault("sources", [item["source"]])
            item.setdefault("en_keyword", "")
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
        "# 题材总表（按四象限评分排序）",
        "",
        f"> 更新时间：{now}　　共 {len(sorted_themes)} 个题材",
        "",
        "| 题材 | 四象限 | 有效获量 | ROI承接 | 证据等级 | 推荐结论 | 玩法承接 | 进入切口 | 硬伤维度 | 素材钩子 | 评审说明 | 来源 | 发现日期 | 状态 |",
        "|------|--------|----------|---------|----------|----------|----------|----------|----------|----------|----------|------|----------|------|",
    ]

    for t in sorted_themes:
        name = t.get("name", "")
        quadrant = t.get("quadrant", "未知")
        ea = t.get("effective_acquisition_score", 0.0)
        roi = t.get("roi_score", 0.0)
        evidence_grade = t.get("evidence_grade", "C")
        recommendation = t.get("recommendation", "未知")
        gameplay_carrier = t.get("gameplay_carrier", "")
        entry_angle = t.get("entry_angle", "")
        hard_fails = "、".join(t.get("hard_fail_dims", []))
        hooks = "、".join(_as_list(t.get("ad_creative_hooks"))[:3])
        reason = t.get("game_viability_reason", "")
        source = t.get("source", "")
        discovered = t.get("discovered_at", "")[:10]
        status = t.get("status", "待评估")
        lines.append(
            f"| {_md_cell(name)} | {_md_cell(quadrant)} | {ea} | {roi} | {evidence_grade} | "
            f"{_md_cell(recommendation)} | {_md_cell(gameplay_carrier)} | {_md_cell(entry_angle)} | "
            f"{_md_cell(hard_fails)} | {_md_cell(hooks)} | {_md_cell(reason)} | "
            f"{_md_cell(source)} | {discovered} | {_md_cell(status)} |"
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
                log(f"[观察] 题材「{name}」竞争预判分={score}（{risk}），进入四象限复评")
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
    log(f"四象限评估完成：{len(viability_map)} 个题材")

    viable_themes = []
    for theme in filtered_themes:
        name = theme["theme"]
        info = viability_map.get(name, {})
        if not info:
            theme["effective_acquisition_score"] = 0.0
            theme["roi_score"] = 0.0
            theme["quadrant"] = "未知"
            theme["hard_fail_dims"] = []
            theme["recommendation"] = "改写后复评"
            theme["gameplay_carrier"] = theme.get("gameplay_carrier", "")
            theme["entry_angle"] = theme.get("entry_angle", theme.get("differentiation_angle", ""))
            theme["ad_creative_hooks"] = _as_list(theme.get("ad_creative_hooks"))
            theme["priority"] = "low"
            log(f"[待复评] 题材「{name}」四象限评估缺失，保留到队列")
            viable_themes.append(theme)
            continue
        assessment = _standardize_assessment(theme, info)
        ea = assessment["effective_acquisition_score"]
        roi = assessment["roi_score"]
        theme["effective_acquisition_score"] = ea
        theme["roi_score"] = roi
        theme["quadrant"] = assessment["quadrant"]
        theme["hard_fail_dims"] = assessment["hard_fail_dims"]
        theme["recommendation"] = assessment["recommendation"]
        theme["evidence_grade"] = assessment["evidence_grade"]
        theme["audience_alignment_confidence"] = assessment["audience_alignment_confidence"]
        theme["gameplay_carrier"] = assessment["gameplay_carrier"]
        theme["entry_angle"] = assessment["entry_angle"]
        theme["ad_creative_hooks"] = assessment["ad_creative_hooks"]
        theme["game_viability_reason"] = assessment["reason"]

        if ea < 3 or roi < 3:
            log(f"[过滤] 题材「{name}」有效获量={ea} ROI={roi}，硬伤排除（{assessment['reason']}）")
            continue

        if assessment["quadrant"] == "高获量+高ROI":
            theme["priority"] = "high"
        elif assessment["recommendation"] in ("通过", "补证", "待买量验证", "差异化后保留", "保留"):
            theme["priority"] = "medium"
        else:
            theme["priority"] = "low"

        if assessment["recommendation"] == "不通过":
            log(f"[过滤] 题材「{name}」四象限结论=不通过（{assessment['reason']}）")
        else:
            viable_themes.append(theme)
            if assessment["recommendation"] == "待买量验证":
                log(f"[Layer2待核验] 题材「{name}」市场存在（{assessment['evidence_grade']}级），需补买量证据")

    log(f"商业潜力过滤后：题材 {len(viable_themes)} 个（原 {len(filtered_themes)} 个）")

    candidates["themes"] = sorted(viable_themes, key=_theme_sort_key)
    candidates["art_styles"] = sorted(filtered_styles, key=lambda x: -x["blue_ocean_score"])

    return candidates

# ========== 候选队列管理 ==========
def load_candidate_queue() -> dict:
    """读取候选队列"""
    _default = {
        "last_run": None,
        "last_collection": None,
        "last_analysis": None,
        "last_review": None,
        "raw_candidates": {"themes": [], "art_styles": []},
        "scored_candidates": {"themes": [], "art_styles": [], "combos": []},
        "candidates": {"themes": [], "art_styles": [], "combos": []},
        "evaluated": {"combos": []}
    }
    if not STATE_FILE.exists():
        return _default

    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        # 兼容旧状态文件，补全新字段
        for key, val in _default.items():
            data.setdefault(key, val)
        return data
    except:
        return _default

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
            "effective_acquisition_score": theme.get("effective_acquisition_score", 0.0),
            "roi_score": theme.get("roi_score", 0.0),
            "quadrant": theme.get("quadrant", "未知"),
            "hard_fail_dims": theme.get("hard_fail_dims", []),
            "entry_angle": theme.get("entry_angle", ""),
            "evidence_grade": theme.get("evidence_grade", "C"),
            "blue_ocean_score": theme.get("blue_ocean_score", 0),
            "competition_risk": theme.get("competition_risk", "未知"),
            "game_viability_reason": theme.get("game_viability_reason", ""),
            "game_fantasy": theme.get("game_fantasy", ""),
            "gameplay_carrier": theme.get("gameplay_carrier", ""),
            "iap_driver": theme.get("iap_driver", ""),
            "recommendation": theme.get("recommendation", "未知"),
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

    # 按证据等级分组统计
    evidence_counts: dict = {"A": 0, "B": 0, "C": 0}
    for theme in new_candidates["themes"]:
        grade = theme.get("evidence_grade", "C")
        evidence_counts[grade] = evidence_counts.get(grade, 0) + 1

    lines = [
        f"【买量组合库 · 每日草稿】{today}",
        "",
        "📊 今日草稿概况",
        f"- 新题材：{len(new_candidates['themes'])} 个"
        f"（A级：{evidence_counts.get('A', 0)} / B级：{evidence_counts.get('B', 0)} / C级：{evidence_counts.get('C', 0)}）",
        f"- 新画风：{len(new_candidates['art_styles'])} 个",
        f"- 新组合：{len(new_candidates['combos'])} 个",
        "⚠️ 均为自动生成草稿，A/B级补证后可进候选池，C级需人工补充市场数据",
        ""
    ]

    # 题材风格假设
    top_themes = sorted(new_candidates["themes"], key=_theme_sort_key)
    if top_themes:
        lines.append("🔥 题材草稿（四象限 × 有效获量 × ROI承接 × 证据等级）")
        for i, theme in enumerate(top_themes[:5], 1):
            quadrant = theme.get("quadrant", "未知")
            ea = theme.get("effective_acquisition_score", 0.0)
            roi = theme.get("roi_score", 0.0)
            evidence_grade = theme.get("evidence_grade", "C")
            recommendation = theme.get("recommendation", "未知")
            gameplay_carrier = theme.get("gameplay_carrier", "")
            entry_angle = theme.get("entry_angle", "")
            reason = theme.get("game_viability_reason", "")
            hooks = _as_list(theme.get("ad_creative_hooks"))
            first_hook = hooks[0] if hooks else ""
            hard_fails = theme.get("hard_fail_dims", [])
            lines.append(
                f"{i}. {theme['theme']}（{quadrant} / 获量：{ea} / ROI：{roi} / "
                f"证据：{evidence_grade}级 / 玩法：{gameplay_carrier or '未知'} / {recommendation}）"
            )
            if first_hook:
                lines.append(f"   - 素材钩子：{first_hook}")
            if entry_angle:
                lines.append(f"   - 进入切口：{entry_angle}")
            if hard_fails:
                lines.append(f"   ⚠ 硬伤：{'、'.join(hard_fails)}")
            if reason:
                lines.append(f"   → {reason}")
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

# ========== 三阶段 Agent ==========

def run_collect(state: dict) -> dict:
    """收集 Agent（DeepSeek）：榜单+泛娱乐+头脑风暴 → raw_candidates"""
    global _llm_backend
    _llm_backend = "deepseek"
    log("========== [收集] 开始（DeepSeek）==========")

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

    for item in brainstorm_themes:
        item.setdefault("source", "头脑风暴")
        item.setdefault("frequency", 3)
    entertainment_themes = entertainment_themes + brainstorm_themes

    themes     = extract_themes(rankings, entertainment_themes)
    art_styles = extract_art_styles(rankings)

    # 对照已有库去重，只保留新题材
    existing  = load_existing_data()
    new_raw   = deduplicate({"themes": themes, "art_styles": art_styles}, existing)

    state["raw_candidates"]  = new_raw
    state["last_collection"] = datetime.now().isoformat()
    _llm_backend = "glm"  # 收集结束，恢复默认

    log(f"[收集] 完成：新题材 {len(new_raw['themes'])} 个，新画风 {len(new_raw['art_styles'])} 个")
    log("========== [收集] 结束 ==========")
    return state


def run_analyze(state: dict) -> dict:
    """分析 Agent（GLM）：竞争评估+四象限评分+过滤排序+组合识别 → scored_candidates"""
    global _llm_backend
    _llm_backend = "glm"
    log("========== [分析] 开始（GLM）==========")


    raw = state.get("raw_candidates", {"themes": [], "art_styles": []})
    if not raw.get("themes") and not raw.get("art_styles"):
        log("[分析] raw_candidates 为空，跳过（请先运行 collect）")
        return state

    candidates = {
        "themes":     list(raw.get("themes", [])),
        "art_styles": list(raw.get("art_styles", [])),
        "combos":     []
    }

    # 竞争评估 + 四象限评分（batch_size=5，避免超时）
    scored = prioritize(candidates)

    # 组合识别，排除已有组合
    combos = identify_combos(scored["themes"], scored["art_styles"])
    existing_combo_keys = {
        f"{c.get('theme','')}×{c.get('art_style','')}"
        for c in state.get("candidates", {}).get("combos", [])
    }
    new_combos = []
    for combo in combos:
        key = f"{combo.get('theme', '')}×{combo.get('art_style', '')}"
        if key not in existing_combo_keys:
            combo["priority"] = "medium"
            combo["blue_ocean_score"] = 0
            combo["competition_risk"] = "待评估"
            new_combos.append(combo)
    scored["combos"] = new_combos

    state["scored_candidates"] = scored
    state["last_analysis"]     = datetime.now().isoformat()

    log(f"[分析] 完成：题材 {len(scored['themes'])} 个，组合 {len(scored['combos'])} 个")
    log("========== [分析] 结束 ==========")
    return state


def run_review(state: dict) -> dict:
    """数据落地：合并主库+更新总表（通知由 Claude SKILL 负责）"""
    log("========== [数据落地] 开始 ==========")

    scored = state.get("scored_candidates", {"themes": [], "art_styles": [], "combos": []})
    if not scored.get("themes") and not scored.get("art_styles"):
        log("[数据落地] scored_candidates 为空，跳过（请先运行 analyze）")
        return state

    # 合并进主候选队列
    state = merge_candidates(state, scored)

    # 更新题材总表（供 Claude 审核时读取）
    update_theme_master_table(state)

    state["last_review"] = datetime.now().isoformat()
    log(f"[数据落地] 完成：已写入题材总表，等待 Claude 审核")
    log(f"  → 状态文件: {STATE_FILE}")
    log(f"  → 总表: {MASTER_TABLE_FILE}")
    log("========== [数据落地] 结束 ==========")
    return state


# ========== 主流程 ==========
def main():
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode not in {"collect", "enrich", "analyze", "review", "all"}:
        print(f"用法: python3 {sys.argv[0]} [collect|enrich|analyze|review|all]")
        print("  collect  — 收集榜单+题材（写入 raw_candidates）")
        print("  enrich   — iTunes+Steam市场数据丰富（读写 raw_candidates，计算证据等级）")
        print("  analyze  — 四象限评估+过滤（读 raw_candidates，写 scored_candidates）")
        print("  review   — 数据落地+总表更新（读 scored_candidates，合并主库）")
        print("  all      — 顺序执行四步（默认）")
        sys.exit(1)

    state = load_candidate_queue()

    if mode in ("collect", "all"):
        state = run_collect(state)
        save_candidate_queue(state)

    if mode in ("enrich", "all"):
        state = enrich_themes(state)
        # enrich_themes 内部已调用 save_candidate_queue，此处无需重复

    if mode in ("analyze", "all"):
        state = run_analyze(state)
        save_candidate_queue(state)

    if mode in ("review", "all"):
        state = run_review(state)
        save_candidate_queue(state)

    log(f"[{mode}] 完成")

if __name__ == "__main__":
    main()
