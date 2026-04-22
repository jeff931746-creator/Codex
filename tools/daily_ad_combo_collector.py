#!/usr/bin/env python3
"""
Daily Ad Combo Collector
每日自动收集买量组合候选（题材 × 画风），生成待评估列表，通过飞书通知用户。
独立脚本，由系统 cron 调用，零 Claude token 消耗。
"""
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
    "/Users/mt/Documents/Codex/research/资料/买量组合库"
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
    """调用 SiliconFlow API"""
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "Qwen/Qwen2.5-7B-Instruct",
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
        with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        log(f"LLM 调用失败: {e}")
        return ""

# ========== WebSearch 调用 ==========
def web_search(query: str) -> str:
    """使用 SiliconFlow 的 WebSearch 能力"""
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "Qwen/Qwen2.5-7B-Instruct",
        "messages": [
            {
                "role": "user",
                "content": f"搜索并总结：{query}。只返回结构化数据，不要解释。"
            }
        ],
        "tools": [{"type": "web_search"}],
        "max_tokens": 2000
    }

    ctx = ssl.create_default_context(cafile=certifi.where())
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=90) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        log(f"WebSearch 调用失败: {e}")
        return ""

# ========== 数据发现模块 ==========
def fetch_game_rankings() -> dict:
    """获取游戏榜单数据"""
    log("开始获取游戏榜单...")

    rankings = {
        "ios": [],
        "taptap": [],
        "wechat": []
    }

    # iOS 免费榜 Top 50
    ios_query = "iOS 游戏免费榜 Top 50 2026年4月"
    ios_result = web_search(ios_query)
    if ios_result:
        rankings["ios"] = parse_game_list(ios_result, "ios")

    # TapTap 热门榜 Top 30
    taptap_query = "TapTap 热门游戏榜单 2026年4月"
    taptap_result = web_search(taptap_query)
    if taptap_result:
        rankings["taptap"] = parse_game_list(taptap_result, "taptap")

    # 微信小游戏热榜 Top 20
    wechat_query = "微信小游戏热榜 2026年4月"
    wechat_result = web_search(wechat_query)
    if wechat_result:
        rankings["wechat"] = parse_game_list(wechat_result, "wechat")

    log(f"榜单获取完成: iOS {len(rankings['ios'])} 款, TapTap {len(rankings['taptap'])} 款, 微信 {len(rankings['wechat'])} 款")
    return rankings

def parse_game_list(text: str, source: str) -> list:
    """从搜索结果中提取游戏列表"""
    prompt = f"""
从以下搜索结果中提取游戏列表，返回 JSON 数组：
[{{"name": "游戏名", "rank": 排名数字}}]

只返回 JSON，不要其他文字。如果无法提取，返回空数组 []。

搜索结果：
{text[:1500]}
"""
    result = call_llm(prompt, max_tokens=1000)
    try:
        games = json.loads(result)
        return [{"name": g["name"], "rank": g.get("rank", 999), "source": source} for g in games]
    except:
        return []

def extract_themes(rankings: dict) -> list:
    """从游戏中提取题材标签"""
    log("开始提取题材...")

    all_games = []
    for source, games in rankings.items():
        all_games.extend([g["name"] for g in games[:20]])  # 每个来源取前 20

    if not all_games:
        return []

    games_text = "、".join(all_games[:30])  # 最多 30 款
    prompt = f"""
从以下游戏列表中提取题材标签（如：末日生存、暗黑童话、赛博朋克、修仙、三国、克苏鲁等）。
返回 JSON 数组：
[{{"theme": "题材名", "reference_games": ["游戏1", "游戏2"], "frequency": 出现次数}}]

只返回 JSON，不要其他文字。

游戏列表：
{games_text}
"""
    result = call_llm(prompt, max_tokens=1500)
    try:
        themes = json.loads(result)
        log(f"提取到 {len(themes)} 个题材")
        return themes
    except:
        log("题材提取失败")
        return []

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
        styles = json.loads(result)
        log(f"提取到 {len(styles)} 个画风")
        return styles
    except:
        log("画风提取失败")
        return []

def identify_combos(themes: list, art_styles: list) -> list:
    """识别题材 × 画风组合"""
    log("开始识别组合...")

    if not themes or not art_styles:
        return []

    themes_text = "、".join([t["theme"] for t in themes[:10]])
    styles_text = "、".join([s["art_style"] for s in art_styles[:10]])

    prompt = f"""
从以下题材和画风中，识别有潜力的买量组合（题材 × 画风）。
优先选择：
1. 题材和画风情感契合度高的组合
2. 市场上有成功案例但组合本身较少的
3. 具有视觉冲击力的组合

返回 JSON 数组（最多 5 个）：
[{{"theme": "题材名", "art_style": "画风名", "reference_game": "参考游戏（如有）", "reason": "推荐理由"}}]

只返回 JSON，不要其他文字。

题材：{themes_text}
画风：{styles_text}
"""
    result = call_llm(prompt, max_tokens=1500)
    try:
        combos = json.loads(result)
        log(f"识别到 {len(combos)} 个组合")
        return combos
    except:
        log("组合识别失败")
        return []

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

def calculate_priority(item: dict, item_type: str) -> str:
    """计算优先级：high | medium | low"""
    score = 0

    # 频率权重
    freq = item.get("frequency", 1)
    if freq >= 3:
        score += 3
    elif freq >= 2:
        score += 2
    else:
        score += 1

    # 榜单排名权重（如果有）
    if "rank" in item and item["rank"] <= 10:
        score += 2
    elif "rank" in item and item["rank"] <= 30:
        score += 1

    if score >= 4:
        return "high"
    elif score >= 2:
        return "medium"
    else:
        return "low"

def prioritize(candidates: dict) -> dict:
    """排序"""
    for theme in candidates["themes"]:
        theme["priority"] = calculate_priority(theme, "theme")

    for style in candidates["art_styles"]:
        style["priority"] = calculate_priority(style, "art_style")

    for combo in candidates["combos"]:
        combo["priority"] = "medium"  # 组合默认中等优先级

    # 按优先级排序
    priority_order = {"high": 0, "medium": 1, "low": 2}
    candidates["themes"].sort(key=lambda x: priority_order[x["priority"]])
    candidates["art_styles"].sort(key=lambda x: priority_order[x["priority"]])
    candidates["combos"].sort(key=lambda x: priority_order[x["priority"]])

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
    """合并新旧候选"""
    today = datetime.now().isoformat()

    # 合并题材
    for theme in new_candidates["themes"]:
        old_state["candidates"]["themes"].append({
            "name": theme["theme"],
            "source": f"榜单提取（{', '.join(theme.get('reference_games', [])[:2])}）",
            "discovered_at": today,
            "priority": theme["priority"],
            "status": "pending"
        })

    # 合并画风
    for style in new_candidates["art_styles"]:
        old_state["candidates"]["art_styles"].append({
            "name": style["art_style"],
            "source": f"榜单提取（{', '.join(style.get('reference_games', [])[:2])}）",
            "discovered_at": today,
            "priority": style["priority"],
            "status": "pending"
        })

    # 合并组合
    for combo in new_candidates["combos"]:
        old_state["candidates"]["combos"].append({
            "theme": combo["theme"],
            "art_style": combo["art_style"],
            "reference_game": combo.get("reference_game", ""),
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

    # 高优先级题材
    high_themes = [t for t in new_candidates["themes"] if t["priority"] == "high"]
    if high_themes:
        lines.append("🔥 高优先级题材")
        for i, theme in enumerate(high_themes[:3], 1):
            refs = ", ".join(theme.get("reference_games", [])[:2])
            lines.append(f"{i}. {theme['theme']}（来源：{refs}）")
        lines.append("")

    # 高优先级画风
    high_styles = [s for s in new_candidates["art_styles"] if s["priority"] == "high"]
    if high_styles:
        lines.append("🎨 高优先级画风")
        for i, style in enumerate(high_styles[:3], 1):
            refs = ", ".join(style.get("reference_games", [])[:2])
            lines.append(f"{i}. {style['art_style']}（来源：{refs}）")
        lines.append("")

    # 待评估组合
    if new_candidates["combos"]:
        lines.append("💡 待评估组合（需补充受众数据）")
        for i, combo in enumerate(new_candidates["combos"][:5], 1):
            ref = f"参考游戏：{combo.get('reference_game', '无')}" if combo.get("reference_game") else ""
            lines.append(f"{i}. {combo['theme']} × {combo['art_style']}")
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

    # 1. 获取榜单数据
    rankings = fetch_game_rankings()

    # 2. 提取题材和画风
    themes = extract_themes(rankings)
    art_styles = extract_art_styles(rankings)

    # 3. 识别组合
    combos = identify_combos(themes, art_styles)

    raw_candidates = {
        "themes": themes,
        "art_styles": art_styles,
        "combos": combos
    }

    # 4. 去重
    existing = load_existing_data()
    new_candidates = deduplicate(raw_candidates, existing)

    # 5. 排序
    new_candidates = prioritize(new_candidates)

    # 6. 合并到候选队列
    state = load_candidate_queue()
    state = merge_candidates(state, new_candidates)
    save_candidate_queue(state)

    # 7. 发送飞书通知
    if any(len(v) > 0 for v in new_candidates.values()):
        digest = format_daily_digest(new_candidates)
        send_feishu_notification(digest)
        log("今日有新发现，已发送飞书通知")
    else:
        log("今日无新发现")

    log("========== 买量组合收集完成 ==========")

if __name__ == "__main__":
    main()
