#!/usr/bin/env python3
"""
1562 款任天堂游戏的 v5 prompt 全量重打标

v5 prompt = v3 + 三条硬约束(IP 自家系列也填/art_style 只填技法/关键机制保留) + art_style 两条细化(2D/3D 判据/独特画风桶保留)

字段:
  - world_setting: 1-3 个值,允许叠加
  - ip_skin: 凡是已建立游戏系列都填,不限于改编
  - core_verb: 玩家实际操作,动词
  - core_object: 操作对象,名词
  - narrative_core: 游戏本体描述,不是原作剧情
  - art_style: 技法层,从合法值清单选

玩法字段沿用旧脚本的程序归类规则,不在 LLM 阶段处理。
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
OUT_DIR = LIB_ROOT / "整理_v5"
OUT_DIR.mkdir(parents=True, exist_ok=True)

LLM_ROUTE = "DeepSeek_Official_Pro"

# 复用旧脚本的玩法归类规则 + load_all_analyzed
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


def make_v5_prompt(works_batch: list) -> str:
    works_str = "\n".join(
        f"{i+1}. 《{w.get('title', '?').strip()}》| 环境:{w.get('theme_env','')} | 文化:{w.get('theme_culture','')} | 叙事:{w.get('theme_narrative','')} | 简介:{w.get('brief','')}"
        for i, w in enumerate(works_batch)
    )

    return f"""你是游戏题材分析师,任务是给以下 {len(works_batch)} 款游戏打 6 个标签。

## 必读硬约束(违反任何一条直接判错)

1. **核心动作和核心对象必须基于"玩家实际在按什么键、做什么操作",不是基于"剧情/原作描述"**
   - 错误: 火影忍者究极风暴 = "忍术对决+羁绊"(基于动漫剧情)
   - 正确: 火影忍者究极风暴 = "3D 格斗对战"(基于游戏机制)

2. **不能用游戏标题字面词直接当核心标签**
   - 错误: 暗杀教室 → core_verb = "暗杀"
   - 正确: 看游戏本体是什么 → core_verb = "派对小游戏"或"格斗"
   - **豁免**: IP 名与游戏内核心实体名完全重合时允许使用。例: "宝可梦"既是 IP 名也是游戏内精灵生物的通称，core_object = "宝可梦/训练师" 合法

3. **核心动作必填且必须是动词;核心对象必填且必须是名词**
   - core_verb 写"经营""狩猎""推理""格斗",不写"忍者""勇者""校园"
   - core_object 写"农场""巨兽""案件""杀老师",不写"挑战""成长"

4. **ip_skin 字段:凡是属于已建立游戏系列(不限于改编),即使是原创 IP 也必须填系列名**
   - **关键转折**:ip_skin 不只是"改编自外部 IP",也包括"游戏自家形成的系列 IP"
   - 必填示例: 怪物猎人/塞尔达/宝可梦/牧场物语/火焰之纹章/异度神剑/八方旅人/雷顿教授/逆转裁判/动物森友会/模拟人生/心跳文学部/星之卡比/马里奥/任天狗/动森/勇者斗恶龙/最终幻想/真女神转生
   - 只有完全原创单作(无续作、无前作、无衍生)才留空
   - 仍填示例: 火影忍者(动漫改编)、鬼灭之刃、暗杀教室、巫师、指环王、异形
   - 留空示例: 末世铁路王国(无系列)、死亡细胞(无系列前作)

5. **art_style 字段只填"画面技法 + 美术风格",不能填题材类**
   - **关键转折**:art_style 是"画风/视觉技法",不是"题材/年代"
   - 必填合法值(从这些里选):
     - 日式 2D 动漫 / 日式 3D 动漫 / 日式 3D 写实 / 日式像素
     - 美式 2D 卡通 / 美式 3D 卡通 / 美式 3D 写实 / 美式像素
     - 中式水墨 / 中式国风 3D
     - Q 版萌系 / 童话绘本 / 哥特暗黑 / 黑白线稿 / 像素风 / 写实风 / 其他风格
   - 禁止填: "蒸汽朋克美术"、"末世风"、"赛博朋克美术"——这些是"题材壳",不是"画风技法"
   - 「蒸汽朋克题材」的画风可能是"日式 3D 动漫"或"美式 3D 写实",取决于技法不是题材

5a. **art_style 2D/3D 判断:看主视觉表现层,不看场景结构**
   - 立绘/角色头像/对话窗为主视觉 → 2D
   - 全 3D 模型+实时渲染为主视觉 → 3D
   - 典型 2D 案例: 火焰之纹章觉醒(战斗有 3D 模型,但主体是立绘)、暗杀教室小游戏、哈利波特魔法觉醒、心跳文学部、逆转裁判、女神异闻录 5(2D UI 主导)
   - 典型 3D 案例: 怪物猎人(全 3D)、塞尔达 BOTW/TOTK、火影忍者究极风暴、宝可梦 朱紫
   - 经验法则:如果对话/菜单/UI 主要靠 2D 立绘,就算战斗有 3D 模型,主视觉仍归 2D

5b. **art_style 独特画风桶必须保留,不要被"日式 3D/2D 动漫"通用桶吸走**
   - **Q 版萌系**: 头身比 2-3、大头大眼、卡通可爱(动物森友会、牧场物语橄榄镇、任天狗、星之卡比)
     - 不能归"日式 3D 动漫"或"日式 2D 动漫"
   - **童话绘本**: 翻书插画风、水彩纸感、绘本叙事(雷顿教授、绘本童话游戏)
     - 不能归"日式 2D 动漫"
   - **像素 HD-2D**: 像素角色 + 3D 场景+景深特效(八方旅人、勇者斗恶龙 11、神之天平)
     - 算"日式像素"
   - **哥特暗黑**: 维多利亚阴郁+暗黑美术(血源诅咒、恶魔城晓月圆舞曲、黑暗之魂)
     - 不能归"日式 3D 写实"或"美式 3D 写实"
   - **美式 3D 卡通 vs 美式 3D 写实**: 卡通有夸张造型/线条(模拟人生卡通、皮克斯改编),写实有真实人体比例(辐射、巫师 3、模拟人生 4)

6. **关键机制保留**:对带标志性子系统的作品,core_verb 或 narrative_core 必须保留原始关键词,不被通用词稀释
   - 错误: 异度神剑 2 → "3D 角色扮演+自动攻击+技能连携"(标志性"异刃收集羁绊"缺失)
   - 正确: 异度神剑 2 → "JRPG 战斗+异刃收集羁绊"
   - 错误: 女神异闻录 5 → "3D 角色扮演+回合制战斗"(标志性"怪盗潜行"缺失)
   - 正确: 女神异闻录 5 → "回合制 JRPG+社交养成+怪盗潜行"
   - 通用规则:如果该游戏有独特的、其他同类游戏不具备的子系统,必须在动作或叙事中保留

7. **题材壳(世界观+IP)是"吸量层",核心动作+对象是"承接层",两层经常错位**
   - 一款游戏可能 IP 吸量是动漫剧情,但承接是格斗机制——这正是要分开记录的关键

## 字段定义

每款游戏输出 6 个字段:

- **world_setting**(数组,1-3 个): 作品发生在什么世界
  - 颗粒度:粗(末世/中世纪/现代都市/古代奇幻/校园/科幻/太空/孤岛/虚拟世界/云海/异世界)
  - 允许叠加架空与历史(如"末世+三国"成立)

- **ip_skin**(字符串,可为空): 见硬约束 4

- **core_verb**(字符串): 玩家实际操作,动词,可叠加
  - 例: "狩猎+装备制作"、"3D 格斗对战"、"卡牌构筑+决斗"、"经营+种植"

- **core_object**(字符串): 动作对象/对手,名词,可多个用 / 分隔
  - 例: "巨龙/巨兽"、"同 IP 角色"、"农场/邻居"、"法庭案件/证人"

- **narrative_core**(字符串,一句话): 描述"游戏本体是什么",不是描述"原作剧情"
  - 错误: "弱者智斗强者+羁绊成长"(原作主题)
  - 正确: "用动漫 IP 包装的传统 3D 格斗"(游戏本体)

- **art_style**(字符串,1 个): 见硬约束 5/5a/5b

## 输出格式

JSON 数组,与输入顺序一致,每条:

```json
{{
  "title": "(与输入完全一致,不带《》)",
  "world_setting": [...],
  "ip_skin": "",
  "core_verb": "...",
  "core_object": "...",
  "narrative_core": "...",
  "art_style": "..."
}}
```

只返回 JSON 数组,不要其他文字。

## 游戏列表

{works_str}"""


def run_v5_tagging(works: list) -> dict:
    BATCH = 20
    batches = [works[i:i+BATCH] for i in range(0, len(works), BATCH)]
    log(f"v5 全量打标: {len(works)} 款分 {len(batches)} 批")

    results = {}

    def process(args):
        idx, batch = args
        prompt = make_v5_prompt(batch)
        items = call_llm_json(prompt, f"v5_tag_b{idx:03d}", max_tokens=6500)
        return idx, items

    done = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        futures = [ex.submit(process, (i, b)) for i, b in enumerate(batches)]
        for f in concurrent.futures.as_completed(futures):
            idx, items = f.result()
            for item in items:
                title = (item.get("title") or "").strip().strip("《》")
                if title:
                    results[title] = {
                        "world_setting": item.get("world_setting", []) or [],
                        "ip_skin": item.get("ip_skin", "") or "",
                        "core_verb": item.get("core_verb", "") or "",
                        "core_object": item.get("core_object", "") or "",
                        "narrative_core": item.get("narrative_core", "") or "",
                        "art_style": item.get("art_style", "") or "",
                    }
            done += 1
            if done % 5 == 0 or done == len(batches):
                log(f"  进度 {done}/{len(batches)}")
    return results


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
    (OUT_DIR / "07_多维度标签_v5.json").write_text(
        json.dumps(tag_map, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"  07_多维度标签_v5.json ({len(tag_map)} 条)")

    # 2. 玩法归类
    play_map = {}
    for w in works:
        title = (w.get("title") or "").strip().strip("《》")
        if title:
            play_map[title] = categorize_play(w)

    work_by_title = {}
    for w in works:
        t = (w.get("title") or "").strip().strip("《》")
        if t and t not in work_by_title:
            work_by_title[t] = w

    def get_works_with_tag(dim: str, value: str) -> list[dict]:
        out = []
        for title, tags in tag_map.items():
            if dim == "world_setting" and value in (tags.get("world_setting") or []):
                pass
            elif dim == "ip_skin" and value == tags.get("ip_skin"):
                pass
            elif dim == "art_style" and value == tags.get("art_style"):
                pass
            elif dim == "core_verb_token":
                tokens = set(re.findall(r"[一-龥A-Za-z0-9]+", tags.get("core_verb", "")))
                if value not in tokens:
                    continue
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
                "ip_skin": tags.get("ip_skin", ""),
                "core_verb": tags.get("core_verb", ""),
                "core_object": tags.get("core_object", ""),
                "art_style": tags.get("art_style", ""),
            })
        return out

    # 计数
    ws_counter = Counter()
    ip_counter = Counter()
    art_counter = Counter()
    verb_token_counter = Counter()
    for tags in tag_map.values():
        for v in tags.get("world_setting") or []:
            ws_counter[v] += 1
        if tags.get("ip_skin"):
            ip_counter[tags["ip_skin"]] += 1
        if tags.get("art_style"):
            art_counter[tags["art_style"]] += 1
        for token in re.findall(r"[一-龥A-Za-z0-9]+", tags.get("core_verb", "")):
            verb_token_counter[token] += 1

    # 3. 世界观分布
    md = ["# 世界观分布 v5", "",
          f"共 {len(ws_counter)} 个标签,合计标记 {sum(ws_counter.values())} 次",
          "", "## 频次 TOP-60", "",
          "| 排名 | 世界观 | 数量 |", "|---|---|---:|"]
    for i, (v, n) in enumerate(ws_counter.most_common(60), 1):
        md.append(f"| {i} | {v} | {n} |")
    md.append("\n## 每个世界观 TOP-10 代表作\n")
    for v, n in ws_counter.most_common(40):
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
        md += [f"### {v}(共 {n} 款)", "",
               "| 作品 | 年份 | 平台 | IP | 画风 | 玩法 | 动作 |",
               "|---|---|---|---|---|---|---|"]
        for w in top10:
            md.append(f"| 《{w['title']}》 | {w['year']} | {w['platform']} | {w['ip_skin'] or '—'} | {w['art_style']} | {w['play']} | {w['core_verb']} |")
        md.append("")
    (OUT_DIR / "08_世界观分布_v5.md").write_text("\n".join(md), encoding="utf-8")
    log(f"  08_世界观分布_v5.md")

    # 4. IP 分布
    md_ip = ["# IP 分布 v5", "",
             f"共 {len(ip_counter)} 个 IP,合计标记 {sum(ip_counter.values())} 次",
             "", "## 频次 TOP-100", "",
             "| 排名 | IP | 数量 |", "|---|---|---:|"]
    for i, (v, n) in enumerate(ip_counter.most_common(100), 1):
        md_ip.append(f"| {i} | {v} | {n} |")
    md_ip.append("\n## 每个 IP TOP-10\n")
    for v, n in ip_counter.most_common(50):
        items = get_works_with_tag("ip_skin", v)
        seen = set()
        dedup = []
        for w in items:
            k = normalize_title(w["title"])
            if k not in seen:
                seen.add(k)
                dedup.append(w)
        dedup.sort(key=lambda x: -(x["acq"] + x["roi"]))
        top10 = dedup[:10]
        md_ip += [f"### {v}(共 {n} 款)", "",
                  "| 作品 | 年份 | 平台 | 画风 | 玩法 | 动作 |",
                  "|---|---|---|---|---|---|"]
        for w in top10:
            md_ip.append(f"| 《{w['title']}》 | {w['year']} | {w['platform']} | {w['art_style']} | {w['play']} | {w['core_verb']} |")
        md_ip.append("")
    (OUT_DIR / "09_IP分布_v5.md").write_text("\n".join(md_ip), encoding="utf-8")
    log(f"  09_IP分布_v5.md")

    # 5. 画风分布
    md_art = ["# 画风分布 v5", "",
              f"共 {len(art_counter)} 个画风,合计标记 {sum(art_counter.values())} 次",
              "", "## 频次", "",
              "| 排名 | 画风 | 数量 |", "|---|---|---:|"]
    for i, (v, n) in enumerate(art_counter.most_common(), 1):
        md_art.append(f"| {i} | {v} | {n} |")
    md_art.append("\n## 每个画风 TOP-10\n")
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
                   "| 作品 | 年份 | 平台 | 世界观 | IP | 玩法 |",
                   "|---|---|---|---|---|---|"]
        for w in top10:
            ws = "、".join(w["world_setting"][:2])
            md_art.append(f"| 《{w['title']}》 | {w['year']} | {w['platform']} | {ws} | {w['ip_skin'] or '—'} | {w['play']} |")
        md_art.append("")
    (OUT_DIR / "10_画风分布_v5.md").write_text("\n".join(md_art), encoding="utf-8")
    log(f"  10_画风分布_v5.md")

    # 6. 玩法 × 世界观
    top_ws = [v for v, _ in ws_counter.most_common(40)]
    play_counts = Counter(play_map.values())
    top_plays = [v for v, _ in play_counts.most_common(20)]
    cross_ws_play = defaultdict(lambda: defaultdict(int))
    for title, tags in tag_map.items():
        play = play_map.get(title, "其他")
        for ws in tags.get("world_setting") or []:
            cross_ws_play[ws][play] += 1
    md_x = ["# 世界观 × 玩法 交叉表 v5", "",
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
        md_x.append("| " + " | ".join(row) + " |")
    (OUT_DIR / "11_世界观×玩法交叉表_v5.md").write_text("\n".join(md_x), encoding="utf-8")
    log(f"  11_世界观×玩法交叉表_v5.md")

    # 7. 画风 × 世界观
    top_arts = [v for v, _ in art_counter.most_common(20)]
    cross_art_ws = defaultdict(lambda: defaultdict(int))
    for title, tags in tag_map.items():
        art = tags.get("art_style", "")
        for ws in tags.get("world_setting") or []:
            if art:
                cross_art_ws[art][ws] += 1
    md_y = ["# 画风 × 世界观 交叉表 v5", "",
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
        md_y.append("| " + " | ".join(row) + " |")
    (OUT_DIR / "12_画风×世界观交叉表_v5.md").write_text("\n".join(md_y), encoding="utf-8")
    log(f"  12_画风×世界观交叉表_v5.md")


def main():
    log("=== v5 prompt 全量重打 ===")
    works = load_all_analyzed()
    log(f"加载 {len(works)} 款作品")

    if len(works) < 100:
        log("[FATAL] 数据不足")
        sys.exit(1)

    tag_map = run_v5_tagging(works)
    log(f"打标完成: {len(tag_map)} 款")

    write_outputs(works, tag_map)
    log("=== 完成 ===")


if __name__ == "__main__":
    main()
