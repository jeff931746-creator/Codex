#!/usr/bin/env python3
"""
1562 款任天堂游戏的多维度题材+画风重打标

题材定义(2 个维度 + 画风独立字段):
  - 世界观(world_setting): 1-3 个值,例如 末世/三国/科幻/校园/古代奇幻
  - 主要元素(key_elements): 0-5 个值,例如 龙族/忍者/校园/复仇
  - 画风(art_style): 1 个值,例如 日式动漫/3D写实/像素/童话绘本

玩法沿用旧脚本的程序归类规则,不重新打。
"""
import concurrent.futures
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path("/Users/mt/Documents/Codex")
sys.path.insert(0, str(ROOT))

from archive.tools.lib.llm_client import chat_text
from archive.tools.lib.llm_common import RetryPolicy

LIB_ROOT = ROOT / "archive/资料/游戏题材库"
RAW_DIR = LIB_ROOT / "_raw"
OUT_DIR = LIB_ROOT / "整理"
OUT_DIR.mkdir(parents=True, exist_ok=True)

LLM_ROUTE = "DeepSeek_Official_Pro"

# 沿用旧脚本的玩法归类规则
from organize_game_themes import PLAY_BUCKETS, categorize_play, load_all_analyzed


def log(msg):
    from datetime import datetime
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def call_llm_json(prompt: str, label: str, max_tokens: int = 6000) -> list:
    cache = RAW_DIR / f"{label}.txt"
    if cache.exists() and cache.stat().st_size > 100:
        text = cache.read_text(encoding="utf-8")
    else:
        text = chat_text(
            prompt, route=LLM_ROUTE, max_tokens=max_tokens, temperature=0.1,
            timeout=240, retry_policy=RetryPolicy(retries=3, base_delay=3.0),
            return_empty_on_error=True,
        )
        if text:
            cache.write_text(text, encoding="utf-8")
        else:
            return []
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    text = re.sub(r",\s*([}\]])", r"\1", text.strip())
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        log(f"  [ERR] {label}: {e}")
        return []


# ========== Prompt ==========
def make_multidim_prompt(works_batch: list) -> str:
    lines = []
    for i, w in enumerate(works_batch):
        title = w.get("title", "?").strip("《》")
        env = w.get("theme_env", "")
        culture = w.get("theme_culture", "")
        narrative = w.get("theme_narrative", "")
        brief = w.get("brief", "")
        lines.append(f"{i+1}. 《{title}》| 环境:{env} | 文化:{culture} | 叙事:{narrative} | 简介:{brief}")
    summary = "\n".join(lines)

    return f"""你是游戏题材分析师。下面是 {len(works_batch)} 款游戏的元数据。

请为每款游戏打 3 类标签(题材 2 维度 + 画风 1 个字段)。

## 维度 1: 世界观(world_setting)

定义: 作品发生在什么世界。允许填 1-3 个值并存(可叠加架空与历史)。

值清单(从中选,允许新增):
末世、现在、未来、科幻、太空、古代奇幻、修仙界、童话世界、
三国、战国、春秋、唐朝、宋朝、明朝、清末、维多利亚、二战、一战、冷战、
中世纪、文艺复兴、古希腊、古罗马、古埃及、古印度、古阿拉伯、
现代都市、近未来、史前、原始时代、海洋世界、太空殖民地、地心、地下世界、
赛博朋克、蒸汽朋克、柴油朋克、生化朋克、
校园、监狱、城堡、孤岛、丛林、沙漠、雪原、深海、宇宙、
异世界、平行宇宙、梦境、虚拟世界

举例:
- 《最终幻想7重制版》→ ["未来", "科幻"]
- 《辐射4》→ ["末世", "近未来"]
- 《三国群英传 Switch》→ ["三国"]
- 《维多利亚 蒸汽朋克》→ ["维多利亚", "蒸汽朋克"]
- 《末世铁路王国》→ ["末世"]
- 《修仙宗门建设》→ ["修仙界"]

## 维度 2: 主要元素(key_elements)

定义: 作品的标志性具体元素。允许填 0-5 个值,没有可为空。

值类型(可混合):
- 物种/生物: 龙族、吸血鬼、僵尸、机甲、巨兽、恐龙、精灵、怪兽、人鱼、外星人、虫族、狼人、人偶...
- 角色身份: 忍者、武士、海盗、警察、侦探、间谍、骑士、女王、修士、刺客、商人、医生、教师...
- 场景类型: 校园、地下城、监狱、餐厅、医院、公寓、神社、寺庙、农场、矿区、墓地...
- 关键事件/动作: 复仇、穿越、重生、直播、暗杀、偷盗、契约、转生、轮回、流放...
- 性别变奏: 女版、男版、雌雄同体

举例:
- 《忍者龙剑传》→ ["忍者"]
- 《最终幻想7重制版》→ [](世界观已说明,无显著元素)
- 《刺客信条 奥德赛》→ ["刺客", "古希腊"]——古希腊是元素,因为时空已是"古希腊"则不重复
- 《暗杀教室》→ ["校园", "暗杀"]
- 《灵魂能力 6》→ ["武士"]
- 《侦探俱乐部》→ ["侦探"]

## 维度 3: 画风(art_style)

定义: 作品的主视觉表达风格。每款游戏只能选 1 个最显著的画风。

值清单:
- 日式 2D 动漫: 二次元立绘+卡通色彩
- 日式 3D 动漫: 二次元 3D 模型(如蓝色协议风)
- 日式像素: 16/32位日式像素
- 日式 3D 写实: 拟真但带日式审美(如《最终幻想7重制版》)
- 美式卡通: 迪士尼/皮克斯/华纳风
- 美式 3D 写实: 真实模型与质感(《辐射》《GTA》)
- 美式像素: 复古像素(《传说之下》)
- 韩式 MMO 写实: 韩国 MMORPG 拟真厚涂(《剑灵》)
- 中式水墨: 中国水墨/工笔
- 中式国风 3D: 中国风 3D 拟真(《黑神话》)
- 童话绘本: 翻书绘本风(《雷顿教授》)
- Q 版萌系: 头身比 2-3,大头大眼(《动物森友会》)
- 黑白线稿/极简: 黑白或单色线条(《Limbo》)
- 哥特暗黑: 维多利亚+暗黑(《血源诅咒》)
- 蒸汽朋克美术: 齿轮+黄铜+蒸汽
- 赛博朋克美术: 霓虹+故障感+黑客感
- 像素风(通用): 不属于上述的像素
- 写实(通用): 不属于上述的拟真
- 其他风格

## 打标规则

1. 每款游戏必须有 1 个画风
2. 世界观至少 1 个,最多 3 个,优先选最具体的(避免选"现在"作为兜底)
3. 主要元素 0-5 个,没有时填 []
4. 标签必须用 2-6 字简短词,不要长描述
5. 看不出来的游戏(如益智、消除、纯小游戏合集),画风照样要打,世界观打"无明显世界观",元素打 []

## 输出格式

JSON 数组,与输入顺序一致,每条:
- "title": 与输入完全一致(不带《》)
- "world_setting": 数组(1-3 个值)
- "key_elements": 数组(0-5 个值,可为空数组)
- "art_style": 字符串(必填,1 个值)

只返回 JSON 数组,不要其他文字。

游戏列表:
{summary}"""


def run_multidim_tagging(works: list) -> dict:
    """逐款打多维度标签"""
    BATCH = 25  # 字段更多,batch 小一些
    batches = [works[i:i+BATCH] for i in range(0, len(works), BATCH)]
    log(f"多维度打标: {len(works)} 款分 {len(batches)} 批")

    results = {}

    def process(args):
        idx, batch = args
        prompt = make_multidim_prompt(batch)
        items = call_llm_json(prompt, f"multidim_b{idx:03d}", max_tokens=6000)
        return idx, items

    done = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        futures = [ex.submit(process, (i, b)) for i, b in enumerate(batches)]
        for f in concurrent.futures.as_completed(futures):
            idx, items = f.result()
            for item in items:
                title = item.get("title", "").strip().strip("《》")
                if title:
                    results[title] = {
                        "world_setting": item.get("world_setting", []) or [],
                        "key_elements": item.get("key_elements", []) or [],
                        "art_style": item.get("art_style", ""),
                    }
            done += 1
            if done % 5 == 0 or done == len(batches):
                log(f"  进度 {done}/{len(batches)}")
    return results


# ========== 输出 ==========
def normalize_tag(s: str) -> str:
    """统一标签:去空格,半角全角,常见同义词归并"""
    if not s:
        return s
    s = re.sub(r"\s+", "", s).strip()
    # 同义词归并
    aliases = {
        # 画风
        "日式3D动漫": ["日式3D动漫"],
        "日式2D动漫": ["日式2D动漫"],
        "日式3D写实": ["日式3D写实"],
        "美式3D写实": ["美式3D写实"],
        "Q版萌系": ["Q版萌系"],
        "童话绘本": ["童话绘本风", "绘本"],
        "美式卡通": ["美式卡通风"],
        "日式像素": ["日式像素风"],
        "美式像素": ["美式像素风"],
        "像素风": ["像素风(通用)", "通用像素"],
        "写实风": ["写实(通用)", "通用写实"],
        "黑白线稿": ["黑白线稿/极简", "极简"],
        # 世界观
        "现代都市": ["都市", "现代都市", "现代生活", "都市生活"],
        "现在": ["现在", "当代", "现代"],
        "古代奇幻": ["古代奇幻"],
        "奇幻": ["奇幻", "奇幻世界"],
        "异世界": ["异世界"],
        "未来": ["未来", "未来世界"],
        "近未来": ["近未来"],
        "科幻": ["科幻", "科幻世界"],
        "末世": ["末世", "末日", "后启示录"],
        "童话世界": ["童话世界", "童话"],
        "校园": ["校园", "学院"],
        "中世纪": ["中世纪"],
        "蒸汽朋克": ["蒸汽朋克"],
        "赛博朋克": ["赛博朋克"],
        "维多利亚": ["维多利亚"],
        "三国": ["三国"],
        "战国": ["战国"],
        "二战": ["二战"],
        "孤岛": ["孤岛", "无人岛", "荒岛"],
        "海洋世界": ["海洋", "海洋世界"],
        "深海": ["深海"],
        "丛林": ["丛林"],
        "宇宙": ["宇宙"],
        "太空": ["太空", "外太空"],
        "太空殖民地": ["太空殖民地", "殖民地"],
        "地下城": ["地下城"],
        "地下世界": ["地下世界"],
        "梦境": ["梦境", "梦境世界"],
        "虚拟世界": ["虚拟世界", "虚拟空间"],
        # 元素
        "宝可梦": ["宝可梦", "口袋妖怪"],
        "校园(场景)": ["校园(场景)"],
    }
    # 反向索引
    for canon, syns in aliases.items():
        if s in syns:
            return canon
    return s


def normalize_tags(tag_map: dict) -> dict:
    """对所有标签字段做归一化"""
    out = {}
    for title, tags in tag_map.items():
        ws = [normalize_tag(v) for v in tags.get("world_setting") or []]
        ke = [normalize_tag(v) for v in tags.get("key_elements") or []]
        art = normalize_tag(tags.get("art_style", ""))
        # 去重
        ws = list(dict.fromkeys([x for x in ws if x]))
        ke = list(dict.fromkeys([x for x in ke if x]))
        out[title] = {
            "world_setting": ws,
            "key_elements": ke,
            "art_style": art,
        }
    return out


def normalize_title(t: str) -> str:
    t2 = re.sub(r"\s+", "", t)
    t2 = t2.replace("(", "(").replace(")", ")")
    t2 = re.sub(r"[:::·~~・//\-—_『』「」【】\[\]、,,。!!??\"\"'']", "", t2)
    t2 = t2.replace("之", "")
    t2 = re.sub(r"(导演剪辑版|豪华版|完整版|完美版|完全版|终极版|加强版|专家版|专业版|HD版|HD复刻版|重制版|Encore|DX|GX|Plus|\+)$", "", t2)
    return t2


def write_outputs(works: list, tag_map: dict):
    log("=== 写出文件 ===")

    # 1. 多维度标签 JSON
    (OUT_DIR / "07_多维度标签.json").write_text(
        json.dumps(tag_map, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"  07_多维度标签.json")

    # 2. 玩法归类(沿用旧规则)
    play_map = {}
    for w in works:
        title = (w.get("title") or "").strip().strip("《》")
        if title:
            play_map[title] = categorize_play(w)

    # 建立 title -> work 字典(带 year/platform)
    work_by_title = {}
    for w in works:
        t = (w.get("title") or "").strip().strip("《》")
        if t and t not in work_by_title:
            work_by_title[t] = w

    # 统计辅助
    def get_works_with_tag(dim: str, value: str) -> list[dict]:
        """按某维度某值取该值下的所有游戏"""
        out = []
        for title, tags in tag_map.items():
            if dim == "world_setting" and value in (tags.get("world_setting") or []):
                pass
            elif dim == "key_elements" and value in (tags.get("key_elements") or []):
                pass
            elif dim == "art_style" and value == tags.get("art_style"):
                pass
            else:
                continue
            work = work_by_title.get(title, {})
            out.append({
                "title": title,
                "year": work.get("year"),
                "platform": work.get("platform"),
                "acq": work.get("acquisition_score", 0),
                "roi": work.get("roi_score", 0),
                "play": play_map.get(title, "其他"),
                "world_setting": tags.get("world_setting") or [],
                "key_elements": tags.get("key_elements") or [],
                "art_style": tags.get("art_style", ""),
            })
        return out

    # 3. 各维度计数
    ws_counter = Counter()
    ke_counter = Counter()
    art_counter = Counter()
    for tags in tag_map.values():
        for v in tags.get("world_setting") or []:
            ws_counter[v] += 1
        for v in tags.get("key_elements") or []:
            ke_counter[v] += 1
        if tags.get("art_style"):
            art_counter[tags["art_style"]] += 1

    # 4. 世界观分布 + TOP-10
    md_ws = ["# 世界观维度分布", "",
             f"共 {len(ws_counter)} 个世界观标签,合计标记 {sum(ws_counter.values())} 次",
             "", "## 频次排名", "",
             "| 排名 | 世界观 | 数量 |",
             "|---|---|---:|"]
    for i, (v, n) in enumerate(ws_counter.most_common(), 1):
        md_ws.append(f"| {i} | {v} | {n} |")

    md_ws.append("\n## 每个世界观 TOP-10 代表作\n")
    for v, n in ws_counter.most_common(50):  # 前 50 个写 TOP10
        items = get_works_with_tag("world_setting", v)
        seen = set()
        dedup = []
        for w in items:
            k = normalize_title(w["title"])
            if k not in seen:
                seen.add(k)
                dedup.append(w)
        dedup.sort(key=lambda x: -(x["acq"] + x["roi"]))
        top10 = dedup[:10]
        md_ws += [f"### {v}(共 {n} 款)", "",
                  "| 作品 | 年份 | 平台 | 画风 | 玩法 | 元素 | 获量+ROI |",
                  "|---|---|---|---|---|---|---|"]
        for w in top10:
            elems = "、".join(w["key_elements"][:3]) if w["key_elements"] else "—"
            md_ws.append(
                f"| 《{w['title']}》 | {w['year']} | {w['platform']} | {w['art_style']} | {w['play']} | {elems} | {w['acq']+w['roi']}/10 |"
            )
        md_ws.append("")

    (OUT_DIR / "08_世界观分布.md").write_text("\n".join(md_ws), encoding="utf-8")
    log(f"  08_世界观分布.md")

    # 5. 主要元素分布 + TOP-10
    md_ke = ["# 主要元素维度分布", "",
             f"共 {len(ke_counter)} 个元素标签,合计标记 {sum(ke_counter.values())} 次",
             "", "## 频次排名 TOP-100", "",
             "| 排名 | 元素 | 数量 |",
             "|---|---|---:|"]
    for i, (v, n) in enumerate(ke_counter.most_common(100), 1):
        md_ke.append(f"| {i} | {v} | {n} |")

    md_ke.append("\n## 每个元素 TOP-10 代表作(频次前 50 元素)\n")
    for v, n in ke_counter.most_common(50):
        items = get_works_with_tag("key_elements", v)
        seen = set()
        dedup = []
        for w in items:
            k = normalize_title(w["title"])
            if k not in seen:
                seen.add(k)
                dedup.append(w)
        dedup.sort(key=lambda x: -(x["acq"] + x["roi"]))
        top10 = dedup[:10]
        md_ke += [f"### {v}(共 {n} 款)", "",
                  "| 作品 | 年份 | 平台 | 世界观 | 画风 | 玩法 |",
                  "|---|---|---|---|---|---|"]
        for w in top10:
            ws = "、".join(w["world_setting"][:2])
            md_ke.append(f"| 《{w['title']}》 | {w['year']} | {w['platform']} | {ws} | {w['art_style']} | {w['play']} |")
        md_ke.append("")

    (OUT_DIR / "09_主要元素分布.md").write_text("\n".join(md_ke), encoding="utf-8")
    log(f"  09_主要元素分布.md")

    # 6. 画风分布 + TOP-10
    md_art = ["# 画风维度分布", "",
              f"共 {len(art_counter)} 个画风标签,合计标记 {sum(art_counter.values())} 次",
              "", "## 频次排名", "",
              "| 排名 | 画风 | 数量 |",
              "|---|---|---:|"]
    for i, (v, n) in enumerate(art_counter.most_common(), 1):
        md_art.append(f"| {i} | {v} | {n} |")

    md_art.append("\n## 每个画风 TOP-10 代表作\n")
    for v, n in art_counter.most_common():
        items = get_works_with_tag("art_style", v)
        seen = set()
        dedup = []
        for w in items:
            k = normalize_title(w["title"])
            if k not in seen:
                seen.add(k)
                dedup.append(w)
        dedup.sort(key=lambda x: -(x["acq"] + x["roi"]))
        top10 = dedup[:10]
        md_art += [f"### {v}(共 {n} 款)", "",
                   "| 作品 | 年份 | 平台 | 世界观 | 玩法 | 元素 |",
                   "|---|---|---|---|---|---|"]
        for w in top10:
            ws = "、".join(w["world_setting"][:2])
            elems = "、".join(w["key_elements"][:3]) if w["key_elements"] else "—"
            md_art.append(f"| 《{w['title']}》 | {w['year']} | {w['platform']} | {ws} | {w['play']} | {elems} |")
        md_art.append("")

    (OUT_DIR / "10_画风分布.md").write_text("\n".join(md_art), encoding="utf-8")
    log(f"  10_画风分布.md")

    # 7. 世界观 × 玩法 交叉表
    top_ws = [v for v, _ in ws_counter.most_common(40)]
    play_counts = Counter(play_map.values())
    top_plays = [v for v, _ in play_counts.most_common(20)]

    cross_ws_play = defaultdict(lambda: defaultdict(int))
    for title, tags in tag_map.items():
        play = play_map.get(title, "其他")
        for ws in tags.get("world_setting") or []:
            cross_ws_play[ws][play] += 1

    md_cross1 = ["# 世界观 × 玩法 交叉表", "",
                 "| 世界观 \\ 玩法 | " + " | ".join(top_plays) + " | **合计** |",
                 "|---" * (len(top_plays) + 2) + "|"]
    for ws in top_ws:
        row = [ws]
        total = 0
        for p in top_plays:
            n = cross_ws_play[ws].get(p, 0)
            row.append(str(n) if n else "—")
            total += n
        row.append(f"**{total}**")
        md_cross1.append("| " + " | ".join(row) + " |")
    (OUT_DIR / "11_世界观×玩法交叉表.md").write_text("\n".join(md_cross1), encoding="utf-8")
    log(f"  11_世界观×玩法交叉表.md")

    # 8. 画风 × 世界观 交叉表
    top_arts = [v for v, _ in art_counter.most_common(20)]
    cross_art_ws = defaultdict(lambda: defaultdict(int))
    for title, tags in tag_map.items():
        art = tags.get("art_style", "")
        for ws in tags.get("world_setting") or []:
            if art:
                cross_art_ws[art][ws] += 1
    md_cross2 = ["# 画风 × 世界观 交叉表", "",
                 "| 画风 \\ 世界观 | " + " | ".join(top_ws[:20]) + " | **合计** |",
                 "|---" * 22 + "|"]
    for art in top_arts:
        row = [art]
        total = 0
        for ws in top_ws[:20]:
            n = cross_art_ws[art].get(ws, 0)
            row.append(str(n) if n else "—")
            total += n
        row.append(f"**{total}**")
        md_cross2.append("| " + " | ".join(row) + " |")
    (OUT_DIR / "12_画风×世界观交叉表.md").write_text("\n".join(md_cross2), encoding="utf-8")
    log(f"  12_画风×世界观交叉表.md")

    # 9. 元素 × 世界观 交叉表(常用元素)
    top_kes = [v for v, _ in ke_counter.most_common(30)]
    cross_ke_ws = defaultdict(lambda: defaultdict(int))
    for title, tags in tag_map.items():
        for ke in tags.get("key_elements") or []:
            for ws in tags.get("world_setting") or []:
                cross_ke_ws[ke][ws] += 1
    md_cross3 = ["# 主要元素 × 世界观 交叉表(频次 TOP-30 元素)", "",
                 "| 元素 \\ 世界观 | " + " | ".join(top_ws[:20]) + " | **合计** |",
                 "|---" * 22 + "|"]
    for ke in top_kes:
        row = [ke]
        total = 0
        for ws in top_ws[:20]:
            n = cross_ke_ws[ke].get(ws, 0)
            row.append(str(n) if n else "—")
            total += n
        row.append(f"**{total}**")
        md_cross3.append("| " + " | ".join(row) + " |")
    (OUT_DIR / "13_元素×世界观交叉表.md").write_text("\n".join(md_cross3), encoding="utf-8")
    log(f"  13_元素×世界观交叉表.md")


def main():
    log("=== 多维度题材+画风重打标 ===")
    works = load_all_analyzed()
    log(f"加载 {len(works)} 款作品")

    if len(works) < 100:
        log("[FATAL] 数据不足")
        sys.exit(1)

    tag_map = run_multidim_tagging(works)
    log(f"打标完成: {len(tag_map)} 款")

    # 归一化同义词
    tag_map = normalize_tags(tag_map)
    log(f"标签归一化完成")

    write_outputs(works, tag_map)
    log("=== 完成 ===")


if __name__ == "__main__":
    main()
