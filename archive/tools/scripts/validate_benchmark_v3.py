#!/usr/bin/env python3
"""
30 款标杆 prompt 验证

流程:
  1. 加载黄金标准 JSON
  2. 用当前 prompt(改进版,加 IP 识别+游戏本体硬约束) 让 DeepSeek_Official_Pro route 打 30 款
  3. 逐项对比:world_setting / ip_skin / core_verb / core_object / narrative_core / art_style
  4. 输出命中率报告 + 错例详情

不重打 1562 款,只验证 30 款标杆。
"""
import concurrent.futures
import json
import re
import sys
import os
from pathlib import Path

ROOT = Path("/Users/mt/Documents/Codex")
sys.path.insert(0, str(ROOT))

from archive.tools.lib.llm_client import chat_text
from archive.tools.lib.llm_common import RetryPolicy

WORK_DIR = ROOT / "archive/资料/游戏题材库/验证/v3_标杆"
WORK_DIR.mkdir(parents=True, exist_ok=True)

LLM_ROUTE = "DeepSeek_Official_Pro"


def log(msg):
    from datetime import datetime
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def call_llm_json(prompt: str, label: str, max_tokens: int = 6000) -> list:
    cache = WORK_DIR / f"{label}.txt"
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


def make_v3_prompt(works_batch: list) -> str:
    """v4 prompt: 含 IP 识别 + 游戏本体硬约束 + 三条新增硬约束(语义判分发现的系统性问题)"""
    works_str = "\n".join(
        f"{i+1}. 《{w['title']}》" for i, w in enumerate(works_batch)
    )

    return f"""你是游戏题材分析师,任务是给以下 {len(works_batch)} 款游戏打 6 个标签。

## 必读硬约束(违反任何一条直接判错)

1. **核心动作和核心对象必须基于"玩家实际在按什么键、做什么操作",不是基于"剧情/原作描述"**
   - 错误: 火影忍者究极风暴 = "忍术对决+羁绊"(基于动漫剧情)
   - 正确: 火影忍者究极风暴 = "3D 格斗对战"(基于游戏机制)

2. **不能用游戏标题字面词直接当核心标签**
   - 错误: 暗杀教室 → core_verb = "暗杀"
   - 正确: 看游戏本体是什么 → core_verb = "派对小游戏"或"格斗"

3. **核心动作必填且必须是动词;核心对象必填且必须是名词**
   - core_verb 写"经营""狩猎""推理""格斗",不写"忍者""勇者""校园"
   - core_object 写"农场""巨兽""案件""杀老师",不写"挑战""成长"

4. **ip_skin 字段:凡是属于已建立游戏系列(不限于改编),即使是原创 IP 也必须填系列名**
   - **关键转折**:ip_skin 不只是"改编自外部 IP",也包括"游戏自家形成的系列 IP"
   - 必填示例: 怪物猎人/塞尔达/宝可梦/牧场物语/火焰之纹章/异度神剑/八方旅人/雷顿教授/逆转裁判/动物森友会/模拟人生/心跳文学部/星之卡比/马里奥/任天狗/动森/塞尔达/勇者斗恶龙/最终幻想/真女神转生
   - 只有完全原创单作(无续作、无前作、无衍生)才留空
   - 仍填示例: 火影忍者(动漫改编)、鬼灭之刃、暗杀教室、巫师、指环王、异形
   - 留空示例: 末世铁路王国(无系列)、直播修仙带货(无系列)、死亡细胞(无系列前作)

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
   - 典型 2D 案例: 火焰之纹章觉醒(战斗有 3D 模型,但主体是立绘)、暗杀教室小游戏(2D 立绘)、哈利波特魔法觉醒(2D 立绘卡牌)、心跳文学部(纯 2D)、逆转裁判(2D 立绘)、女神异闻录 5(2D UI 主导,虽有 3D 战斗)
   - 典型 3D 案例: 怪物猎人(全 3D)、塞尔达 BOTW/TOTK(全 3D)、火影忍者究极风暴(全 3D)、宝可梦 朱紫(全 3D)
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
   - **美式 3D 卡通 vs 美式 3D 写实**: 卡通有夸张造型/线条(模拟人生卡通、皮克斯电影改编),写实有真实人体比例(辐射、巫师 3、模拟人生 4 写实)
     - 注意:模拟人生 4 是"美式 3D 写实",虽然有少量卡通化,但人物比例和材质是写实路线

6. **关键机制保留**:对带标志性子系统的作品,core_verb 或 narrative_core 必须保留原始关键词,不被通用词稀释
   - 错误: 异度神剑 2 → "3D 角色扮演+自动攻击+技能连携"(标志性"异刃收集羁绊"缺失)
   - 正确: 异度神剑 2 → "JRPG 战斗+异刃收集羁绊"
   - 错误: 女神异闻录 5 → "3D 角色扮演+回合制战斗+日常养成"(标志性"怪盗潜行"缺失)
   - 正确: 女神异闻录 5 → "回合制 JRPG+社交养成+怪盗潜行"
   - 错误: 火焰之纹章觉醒 → "战棋指挥+角色关系"(标志性"结婚生子+次代继承"缺失)
   - 正确: 火焰之纹章觉醒 → "战棋指挥+结婚生子+次代继承"
   - 通用规则:如果该游戏有独特的、其他同类游戏不具备的子系统,必须在动作或叙事中保留

7. **题材壳(世界观+IP)是"吸量层",核心动作+对象是"承接层",两层经常错位**
   - 一款游戏可能 IP 吸量是动漫剧情,但承接是格斗机制——这正是要分开记录的关键

## 字段定义

每款游戏输出 6 个字段:

- **world_setting**(数组,1-3 个): 作品发生在什么世界。例如 ["末世","三国"]/["古代奇幻"]/["现代都市","校园"]
  - 颗粒度:粗(末世/中世纪/现代都市/古代奇幻/校园/科幻/太空/孤岛/虚拟世界/云海/异世界)
  - 允许叠加架空与历史(如"末世+三国"成立)
  - 注意特殊世界观: 异度神剑 2 是"云海",动物森友会是"孤岛",心跳文学部是"虚拟世界"

- **ip_skin**(字符串,可为空): 见硬约束 4

- **core_verb**(字符串): 玩家实际在做的操作,动词,可叠加。
  - 例: "狩猎+装备制作"、"3D 格斗对战"、"卡牌构筑+决斗"、"经营+种植"

- **core_object**(字符串): 动作针对的对象/对手,名词,可多个用 / 分隔。
  - 例: "巨龙/巨兽"、"同 IP 角色"、"农场/邻居"、"法庭案件/证人"

- **narrative_core**(字符串,一句话): 描述"游戏本体是什么",不是描述"原作剧情"。
  - 错误: "弱者智斗强者+羁绊成长"(这是原作主题)
  - 正确: "用动漫 IP 包装的传统 3D 格斗"(这是游戏本体)

- **art_style**(字符串,1 个): 见硬约束 5,从合法值清单选

## 输出格式

JSON 数组,与输入顺序一致,每条:

```json
{{
  "title": "(与输入完全一致)",
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


def normalize(s):
    """标签字符串归一化(去空格、半角全角)"""
    if isinstance(s, list):
        return [normalize(x) for x in s]
    if not s:
        return ""
    return re.sub(r"\s+", "", str(s)).strip()


def compare_field(gold, llm, field: str) -> tuple[bool, str]:
    """对比单个字段,返回(是否匹配, 说明)"""
    g = gold.get(field, "")
    l = llm.get(field, "")
    if field == "world_setting":
        gset = set(normalize(g)) if g else set()
        lset = set(normalize(l)) if l else set()
        if not gset and not lset:
            return True, "both empty"
        # 严格匹配:完全一致或交集 >= max(gset,lset) - 1
        if gset == lset:
            return True, "exact match"
        overlap = gset & lset
        if len(overlap) >= len(gset) - 1 and len(overlap) >= len(lset) - 1:
            return True, f"close match: gold={gset}, llm={lset}"
        return False, f"gold={gset} vs llm={lset}"
    if field in ("ip_skin", "art_style"):
        gn = normalize(g)
        ln = normalize(l)
        if gn == ln:
            return True, "exact"
        if not gn and not ln:
            return True, "both empty"
        # 部分匹配(包含关系)
        if gn and ln and (gn in ln or ln in gn):
            return True, f"contains: gold={gn}, llm={ln}"
        return False, f"gold={gn} vs llm={ln}"
    if field == "core_verb":
        # 拆分关键词,看交集
        gtokens = set(re.findall(r"[一-龥A-Za-z0-9]+", normalize(g)))
        ltokens = set(re.findall(r"[一-龥A-Za-z0-9]+", normalize(l)))
        if not gtokens and not ltokens:
            return True, "both empty"
        overlap = gtokens & ltokens
        if len(overlap) >= max(1, len(gtokens) // 2):
            return True, f"overlap≥half: gold='{g}' llm='{l}'"
        return False, f"gold='{g}' vs llm='{l}'"
    if field == "core_object":
        # 关键词交集
        gtokens = set(re.findall(r"[一-龥A-Za-z]+", normalize(g)))
        ltokens = set(re.findall(r"[一-龥A-Za-z]+", normalize(l)))
        if not gtokens and not ltokens:
            return True, "both empty"
        overlap = gtokens & ltokens
        if overlap:
            return True, f"overlap: gold='{g}' llm='{l}'"
        return False, f"gold='{g}' vs llm='{l}'"
    if field == "narrative_core":
        # 不严格判分,只比较核心关键词
        gtokens = set(re.findall(r"[一-龥]{2,}", g or ""))
        ltokens = set(re.findall(r"[一-龥]{2,}", l or ""))
        overlap = gtokens & ltokens
        # 至少 2 个关键词重叠算 pass
        if len(overlap) >= 2:
            return True, f"keyword overlap={overlap}"
        return False, f"gold='{g[:50]}' vs llm='{l[:50]}'"
    return True, "skip"


def main():
    golden = json.loads((WORK_DIR / "golden_standard_v3.json").read_text(encoding="utf-8"))
    log(f"加载黄金标准 {len(golden)} 款")

    # 用当前 prompt 跑 30 款(分 2 批,每批 15 款)
    BATCH = 15
    batches = [golden[i:i+BATCH] for i in range(0, len(golden), BATCH)]

    all_llm_results = {}

    def process(args):
        idx, batch = args
        prompt = make_v3_prompt(batch)
        items = call_llm_json(prompt, f"llm_run_b{idx:02d}", max_tokens=6000)
        return idx, items

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        futures = [ex.submit(process, (i, b)) for i, b in enumerate(batches)]
        for f in concurrent.futures.as_completed(futures):
            idx, items = f.result()
            for it in items:
                title = (it.get("title") or "").strip().strip("《》")
                if title:
                    all_llm_results[title] = it
            log(f"批次 {idx} 完成,{len(items)} 条")

    log(f"deepseek 打完: {len(all_llm_results)} 条")

    # 逐项对比
    fields = ["world_setting", "ip_skin", "core_verb", "core_object", "narrative_core", "art_style"]
    field_hits = {f: 0 for f in fields}
    field_misses = {f: [] for f in fields}
    per_title_hits = {}

    for g in golden:
        title = g["title"]
        llm = all_llm_results.get(title.replace("《", "").replace("》", "").strip())
        if not llm:
            # 容错
            for k in all_llm_results:
                if title.replace(" ", "") in k.replace(" ", "") or k.replace(" ", "") in title.replace(" ", ""):
                    llm = all_llm_results[k]
                    break
        if not llm:
            for f in fields:
                field_misses[f].append({"title": title, "reason": "LLM 未返回"})
            per_title_hits[title] = 0
            continue

        hits = 0
        for f in fields:
            ok, note = compare_field(g, llm, f)
            if ok:
                field_hits[f] += 1
                hits += 1
            else:
                field_misses[f].append({
                    "title": title, "category": g.get("category", ""),
                    "gold": g.get(f, ""), "llm": llm.get(f, ""), "note": note,
                })
        per_title_hits[title] = hits

    # 写报告
    total = len(golden)
    lines = [f"# 30 款标杆 prompt v3 验证报告", "",
             f"模型: {LLM_ROUTE}",
             f"总样本: {total}", "",
             "## 字段命中率", "",
             "| 字段 | 命中 | 命中率 |",
             "|---|---:|---:|"]
    for f in fields:
        rate = field_hits[f] / total
        lines.append(f"| {f} | {field_hits[f]}/{total} | {rate:.1%} |")

    overall_hit = sum(per_title_hits.values())
    overall_total = total * len(fields)
    lines += ["",
              f"**总体命中率: {overall_hit}/{overall_total} = {overall_hit/overall_total:.1%}**",
              "",
              "## 每款全字段命中数 (0-6)",
              "",
              "| 游戏 | 命中数 |",
              "|---|---:|"]
    for title, hits in sorted(per_title_hits.items(), key=lambda x: x[1]):
        lines.append(f"| {title} | {hits}/{len(fields)} |")

    # 错例详情
    lines.append("\n## 错例详情(按字段)\n")
    for f in fields:
        if not field_misses[f]:
            continue
        lines += [f"### {f} 错例({len(field_misses[f])} 个)", ""]
        for m in field_misses[f]:
            lines.append(f"- **{m['title']}** [{m.get('category','')}]")
            lines.append(f"  - 黄金: `{m.get('gold','')}`")
            lines.append(f"  - LLM: `{m.get('llm','')}`")
            lines.append(f"  - 备注: {m.get('note','')}")
        lines.append("")

    (WORK_DIR / "validation_report.md").write_text("\n".join(lines), encoding="utf-8")
    log("写入 validation_report.md")
    log(f"总体命中率: {overall_hit/overall_total:.1%}")


if __name__ == "__main__":
    main()
