#!/usr/bin/env python3
"""
任天堂游戏题材库整理 - 数据事实驱动

不让 LLM 创造分类,只让 LLM 给每款游戏打"题材壳标签"。
然后用程序统计交叉表。

输入: archive/资料/游戏题材库/_raw/*analysis_batch*.txt (1570 款 已分析数据)
输出:
  archive/资料/游戏题材库/整理/
    01_题材壳标签_原始.json        # 每款游戏的主/辅题材壳标签(自由生成)
    02_题材壳标签_合并.json        # 程序合并近义词后的标准化标签
    03_玩法归类.json               # 每款游戏的玩法标签(genre+carrier+psych 交叉)
    04_交叉表.md                  # 题材壳 × 玩法 交叉计数表
    05_每壳TOP10.md               # 每个题材壳下 TOP-10 代表作
    06_饱和度分析.md              # 高频/低频/缺失组合
"""
import concurrent.futures
import json
import re
import sys
import os
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

MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro")


def log(msg):
    from datetime import datetime
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def call_llm_json(prompt: str, label: str, max_tokens: int = 6000) -> list:
    cache = RAW_DIR / f"{label}.txt"
    if cache.exists() and cache.stat().st_size > 100:
        text = cache.read_text(encoding="utf-8")
    else:
        text = chat_text(
            prompt, model=MODEL, max_tokens=max_tokens, temperature=0.1,
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
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            text = re.sub(r",\s*([}\]])", r"\1", text)
            return json.loads(text)
        except Exception as e:
            log(f"  [ERR] {label}: {e}")
            return []


def load_all_analyzed() -> list:
    """加载所有 analysis batch 数据 + 合并 discovery 的 year/platform"""
    # 1. 先加载 discovery,建 title -> meta 索引
    title_meta = {}
    for f in sorted(RAW_DIR.glob("*discovery_*.txt")):
        try:
            text = f.read_text(encoding="utf-8").strip()
            if text.startswith("```"):
                text = re.sub(r"^```(?:json)?\s*", "", text)
                text = re.sub(r"\s*```$", "", text)
            text = re.sub(r",\s*([}\]])", r"\1", text.strip())
            items = json.loads(text)
            if not isinstance(items, list):
                continue
            for it in items:
                t = (it.get("title") or "").strip().strip("《》")
                if t and t not in title_meta:
                    title_meta[t] = {
                        "year": it.get("year"),
                        "platform": it.get("platform"),
                        "genre": it.get("genre"),
                        "developer": it.get("developer"),
                    }
        except Exception:
            pass

    # 2. 加载 analysis,补齐 year/platform
    works = []
    for f in sorted(RAW_DIR.glob("*analysis_batch*.txt")):
        try:
            text = f.read_text(encoding="utf-8").strip()
            if text.startswith("```"):
                text = re.sub(r"^```(?:json)?\s*", "", text)
                text = re.sub(r"\s*```$", "", text)
            text = re.sub(r",\s*([}\]])", r"\1", text.strip())
            items = json.loads(text)
            if not isinstance(items, list):
                continue
            for it in items:
                t = (it.get("title") or "").strip().strip("《》")
                meta = title_meta.get(t, {})
                for k, v in meta.items():
                    if v is not None and it.get(k) in (None, "", "?"):
                        it[k] = v
                works.append(it)
        except Exception as e:
            log(f"  [WARN] {f.name}: {e}")
    return works


# ========== Phase 1: deepseek 逐款打题材壳标签 ==========
def make_shell_extract_prompt(works_batch: list) -> str:
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

任务: 给每款游戏提取「题材壳标签」,严格遵循以下规则。

什么是题材壳?
- 题材壳 = 这款游戏的世界观/文化背景在用户脑里激活的第一关联词
- 题材壳必须是名词,具体到能联想到一类作品
- 题材壳不带玩法(不允许"塔防壳"、"卡牌壳"、"SLG壳")
- 题材壳不带情绪(不允许"治愈壳"、"焦虑壳")

**核心约束:奇幻类必须细分,严禁笼统打"高奇幻"**

奇幻类细分(根据题材具体特征选最贴近的):
- 中世纪奇幻: 中世纪欧洲背景+剑与魔法+城堡领地
- 龙与地下城: 桌游 D&D 风格+种族职业+迷宫探索
- 童话奇幻: 公主王子+魔法师+童话原型(白雪/灰姑娘/绿野仙踪)
- 日式幻想: 日式 JRPG 经典(勇者斗恶龙/最终幻想/星之海洋)
- 魔法学院: 学校设定+师生+魔法学习
- 暗黑奇幻: 哥特氛围+诡异魔法+黑暗叙事
- 水晶幻想: 最终幻想系特有+水晶能源
- 蘑菇王国: 马里奥系特有+蘑菇变身
- 西幻精灵: 精灵族/兽人/矮人世界
- 高奇幻史诗: 魔戒式宏大世界观+多种族战争

如果游戏明显属于一个具体壳(如《最终幻想》归"水晶幻想"或"日式幻想"),
绝对不能打"高奇幻"。

题材壳示例(供参考,但不限于这些):
末世、丧尸末世、废土、极寒末世、太空殖民、星际科幻、赛博朋克、蒸汽朋克、
修仙、修真、武侠、三国、战国、东方神话、希腊神话、北欧神话、克苏鲁、
现代都市、都市异能、校园、学院、魔法学院、童话奇幻、日式幻想、暗黑奇幻、
僵尸末日、机甲、忍者、海盗、间谍、特种部队、警察、侦探、
恐龙、宠物、精灵、怪兽、虫族、龙族、吸血鬼、狼人、僵尸、
童话、绘本、卡通、二次元、动漫风、像素风、
牧场、农场、田园、海岛、孤岛、深海、地心、地下城、
赛车、足球、篮球、运动、健身、料理、音乐、舞蹈

打标规则:
1. 每款游戏必须有 1 个「主题材壳」(最能代表用户脑里第一反应的)
2. 可有 0-2 个「辅题材壳」(共存的次要标签,如"末世"+"机甲"+"搜打撤")
3. 主辅标签必须 2-4 字,不要长描述
4. 如果游戏是纯运动/休闲/派对/工具类无明显题材壳,主标签填"无题材壳"
5. 严禁使用心理学描述("孤独感"、"成长冲突")或玩法名("塔防"、"卡牌")

输出 JSON 数组,与输入顺序一致,每条:
- "title": 与输入完全一致(不带《》)
- "primary_shell": 主题材壳(2-4字)
- "secondary_shells": 辅题材壳数组(0-2 个,可为空)

只返回 JSON 数组,不要其他文字。

游戏列表:
{summary}"""


def run_shell_extraction(works: list) -> dict:
    """对 1570 款逐款打题材壳标签。返回 {title: {primary, secondaries}}"""
    BATCH = 30
    batches = [works[i:i+BATCH] for i in range(0, len(works), BATCH)]
    log(f"Phase 1 题材壳提取: {len(works)} 款分 {len(batches)} 批")

    results = {}

    def process(args):
        idx, batch = args
        prompt = make_shell_extract_prompt(batch)
        items = call_llm_json(prompt, f"shell_extract_b{idx:03d}", max_tokens=5000)
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
                        "primary_shell": item.get("primary_shell", ""),
                        "secondary_shells": item.get("secondary_shells", []) or [],
                    }
            done += 1
            if done % 5 == 0 or done == len(batches):
                log(f"  进度 {done}/{len(batches)}")
    return results


# ========== Phase 2: 程序合并近义词 ==========
SHELL_SYNONYMS = {
    # 末世系
    "末世": ["末日", "末世废土", "末日废土", "废土末世", "末世后", "灾后", "灾难", "后启示录", "后末日"],
    "丧尸末世": ["丧尸末日", "僵尸末日", "丧尸围城", "僵尸末世", "丧尸", "僵尸"],
    "废土": ["废土科幻", "废土生存", "辐射", "核冬天"],
    "极寒末世": ["冰封末世", "极地", "冰雪末世", "冰原", "极地末世"],
    # 科幻系
    "太空科幻": ["太空", "星际", "宇宙", "星际科幻", "太空殖民", "外太空", "星空", "深空"],
    "异星科幻": ["异星", "外星", "异星科幻"],
    "近未来": ["近未来", "未来科幻"],
    "赛博朋克": ["赛博", "电子朋克", "cyberpunk"],
    "蒸汽朋克": ["蒸汽", "蒸汽世界", "steampunk"],
    # 东方
    "修仙": ["修真", "玄幻", "仙侠", "飞升", "炼丹"],
    "武侠": ["江湖", "侠客", "中国武侠"],
    "三国": ["三国时代", "三国乱世"],
    "战国": ["战国时代", "日本战国"],
    "东方神话": ["东方仙怪", "中式神话", "上古神话", "山海经"],
    "日本神话": ["日本神道", "和风神话"],
    "和风": ["和风奇幻", "日式和风", "日式古风"],
    # 西方
    "希腊神话": ["希腊", "奥林匹斯"],
    "北欧神话": ["北欧", "维京", "诸神黄昏"],
    "波斯神话": ["波斯", "波斯传说"],
    "克苏鲁": ["邪神", "旧日支配者", "宇宙恐怖", "lovecraft"],
    # 奇幻细分(避免笼统打"高奇幻")
    "高奇幻": ["高奇幻", "高奇幻史诗", "西幻", "西方奇幻", "中世纪奇幻", "魔戒式"],
    "日式幻想": ["日式幻想", "日式JRPG", "日式RPG奇幻", "勇者斗恶龙风", "最终幻想风"],
    "暗黑奇幻": ["黑暗奇幻", "暗黑"],
    "童话奇幻": ["童话奇幻", "童话风奇幻", "格林童话", "童话原型"],
    "魔法学院": ["魔法学校", "魔法师学院", "学院奇幻"],
    "水晶幻想": ["水晶幻想", "FF水晶", "水晶能源"],
    "蘑菇王国": ["蘑菇王国", "马里奥世界"],
    # 现代
    "现代都市": ["都市", "现代", "现代社会", "都市生活"],
    "都市异能": ["都市超能力", "异能都市", "现代异能"],
    "校园": ["校园生活", "高中", "学院生活", "学生"],
    # 机甲/战争
    "机甲": ["机器人", "战甲", "高达", "机甲战士"],
    "现代战场": ["现代军事", "现代战争", "特种部队"],
    "二战": ["二战时代", "WWII"],
    "军事谍战": ["军事谍战", "谍战"],
    "间谍": ["谍报", "spy"],
    # 题材壳生物
    "恐龙": ["恐龙时代", "侏罗纪", "史前生物", "史前", "原始生态"],
    "宠物": ["小动物", "宠物养成"],
    "精灵": ["精灵生物", "口袋妖怪", "宝可梦", "捕捉精灵"],
    "怪兽": ["怪兽世界", "巨兽", "巨型怪物"],
    "虫族": ["昆虫", "虫群", "虫类"],
    "龙族": ["龙", "巨龙"],
    "吸血鬼": ["血族", "夜族"],
    # 童话/卡通
    "童话": ["童话故事", "童话风格"],
    "绘本": ["绘本风", "插画"],
    "卡通": ["卡通风", "卡通动画"],
    "二次元": ["二次元动漫", "日式动漫", "日漫"],
    "迪士尼": ["迪士尼风", "迪士尼动画"],
    # 治愈/田园
    "牧场": ["农场", "田园", "种田", "牧歌"],
    "海岛": ["孤岛", "无人岛", "热带岛", "荒岛"],
    "深海": ["海底", "海洋", "深海科幻"],
    "丛林": ["丛林冒险", "热带丛林", "丛林"],
    "地下城": ["地下迷宫", "地牢", "地下矿洞"],
    # 恐怖
    "民俗恐怖": ["中式民俗", "日式民俗", "民俗诡谲", "怪谈"],
    "心理恐怖": ["精神恐怖", "心灵恐怖"],
    "鬼怪": ["灵异", "鬼神", "妖怪", "鬼魂", "诡异"],
    "鬼屋": ["鬼宅", "幽灵屋", "凶宅"],
    "哥特恐怖": ["哥特", "维多利亚哥特", "哥特式恐怖"],
    "生化恐怖": ["生化危机", "病毒恐怖"],
    "梦境": ["梦境世界", "梦魇"],
    # 运动细分
    "高尔夫": ["高尔夫球"],
    "足球": ["足球运动"],
    "篮球": ["篮球运动"],
    "赛车": ["街头赛车", "越野赛车", "拉力赛", "卡丁车"],
    # 角色类型
    "侦探": ["侦探推理", "名侦探"],
    "海盗": ["加勒比海盗"],
    "忍者": ["和风忍者"],
    "怪盗": ["怪盗"],
    "超级英雄": ["美式超级英雄", "漫威", "DC"],
    "魔界": ["魔界战记", "恶魔世界"],
    "炼金术": ["炼金工房", "炼金"],
    "音乐": ["音乐题材"],
    "动物园": ["动物园经营"],
    "料理": ["美食", "厨艺"],
    "航海冒险": ["大航海"],
    "主题乐园": ["游乐园经营", "主题公园"],
    # 派对/无壳
    "无题材壳": ["无题材", "无明显题材", "中性", "工具", "教育"],
}

# 反向索引
SYNONYM_TO_CANONICAL = {}
for canonical, syns in SHELL_SYNONYMS.items():
    SYNONYM_TO_CANONICAL[canonical] = canonical
    for syn in syns:
        SYNONYM_TO_CANONICAL[syn] = canonical


def normalize_shell(shell: str) -> str:
    if not shell:
        return ""
    shell = shell.strip()
    # 精确匹配
    if shell in SYNONYM_TO_CANONICAL:
        return SYNONYM_TO_CANONICAL[shell]
    # 子串匹配(优先长的)
    for syn in sorted(SYNONYM_TO_CANONICAL.keys(), key=lambda x: -len(x)):
        if syn in shell or shell in syn:
            return SYNONYM_TO_CANONICAL[syn]
    return shell


def normalize_all_shells(raw: dict) -> dict:
    """合并近义词"""
    normalized = {}
    for title, data in raw.items():
        p = normalize_shell(data.get("primary_shell", ""))
        s = [normalize_shell(x) for x in data.get("secondary_shells", []) if x]
        s = [x for x in s if x and x != p]
        normalized[title] = {"primary_shell": p, "secondary_shells": s}
    return normalized


# ========== Phase 3: 玩法归类(genre + gameplay_carrier + psych 交叉) ==========
# 优先级:特征明确的玩法在前,通用类在后,卡牌严格化作为最后兜底
PLAY_BUCKETS = {
    "搜打撤": ["搜打撤", "extraction"],
    "肉鸽": ["肉鸽", "Roguelike", "Roguelite", "roguelike"],
    "战棋": ["战棋", "SRPG", "战略RPG", "战术RPG"],
    "塔防": ["塔防", "tower defense"],
    "JRPG": ["JRPG", "日式RPG", "传统RPG", "回合RPG", "回合制RPG", "回合制角色扮演"],
    "ARPG": ["ARPG", "动作RPG", "动作角色扮演"],
    "MMORPG": ["MMORPG", "MMO", "网络RPG"],
    "格斗": ["格斗", "fighting", "对战格斗"],
    "音游": ["音游", "节奏游戏", "音乐游戏"],
    "AVG/VN": ["AVG", "视觉小说", "互动叙事", "叙事冒险", "文字冒险"],
    "竞速": ["赛车", "竞速", "racing"],
    "运动": ["足球", "篮球", "网球", "高尔夫", "棒球", "滑板", "体育", "运动"],
    "种田/牧场": ["种田", "牧场", "农场", "田园"],
    "经营模拟": ["模拟经营", "城市建设", "建造游戏", "经营游戏", "管理游戏"],
    "派对": ["派对", "聚会", "小游戏合集", "minigame"],
    "沙盒": ["沙盒", "建造沙盒"],
    "潜行": ["潜行", "stealth"],
    "解谜": ["解谜", "推理", "逻辑游戏", "puzzle"],
    "射击": ["FPS", "TPS", "射击游戏", "shoot"],
    "动作": ["动作冒险", "横版动作", "动作游戏", "平台动作", "ACT", "动作"],
    "策略": ["SLG", "回合策略", "战略游戏", "tactical", "策略游戏"],
    # 严格化卡牌:只匹配明确的 TCG/DBG/卡牌对战,不再吃 RPG/JRPG 的"卡牌养成"
    "卡牌": ["TCG", "DBG", "卡组构筑", "卡牌对战", "卡牌游戏", "集换式卡牌"],
    # RPG 兜底
    "RPG": ["RPG", "角色扮演"],
    "工具/教育": ["工具", "脑训练", "教育游戏", "学习游戏"],
}


def categorize_play(work: dict) -> str:
    """返回单个主玩法,优先级从 PLAY_BUCKETS 顺序匹配"""
    # 优先看 genre(品类) — 通常最准
    # 然后看 gameplay_carrier(推荐玩法) — 注意"卡牌养成"这种词需要被 JRPG 等更具体的关键词先匹配
    genre = str(work.get("genre", "") or "")
    carrier_list = work.get("gameplay_carrier", []) or []
    if isinstance(carrier_list, str):
        carrier_list = [carrier_list]
    psych_list = work.get("psych_tasks", []) or []
    if isinstance(psych_list, str):
        psych_list = [psych_list]

    # 先单独看 genre
    genre_lower = genre.lower()
    for bucket, kws in PLAY_BUCKETS.items():
        for kw in kws:
            if kw.lower() in genre_lower:
                return bucket

    # 再看 gameplay_carrier
    carrier_text = " ".join(str(c) for c in carrier_list).lower()
    for bucket, kws in PLAY_BUCKETS.items():
        for kw in kws:
            if kw.lower() in carrier_text:
                return bucket

    # 最后看 psych_tasks(很少能匹配,但留个兜底)
    psych_text = " ".join(str(p) for p in psych_list).lower()
    for bucket, kws in PLAY_BUCKETS.items():
        for kw in kws:
            if kw.lower() in psych_text:
                return bucket

    return "其他"


# ========== Phase 4: 输出 ==========
def write_outputs(works: list, shell_map: dict, normalized_shell_map: dict):
    log("=== 写出文件 ===")

    # 1. 原始标签
    (OUT_DIR / "01_题材壳标签_原始.json").write_text(
        json.dumps(shell_map, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"  01_题材壳标签_原始.json")

    # 2. 合并后标签
    (OUT_DIR / "02_题材壳标签_合并.json").write_text(
        json.dumps(normalized_shell_map, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"  02_题材壳标签_合并.json")

    # 3. 玩法归类(对每款游戏,单玩法)
    play_map = {}
    for w in works:
        title = w.get("title", "").strip().strip("《》")
        if title:
            play_map[title] = categorize_play(w)
    (OUT_DIR / "03_玩法归类.json").write_text(
        json.dumps(play_map, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"  03_玩法归类.json")

    # 4. 交叉表(每款游戏只算 1 个玩法 + 1 个主题材壳)
    cross = defaultdict(lambda: defaultdict(list))
    shell_counts = Counter()
    play_counts = Counter()
    # 建立 title -> work 字典,带 year/platform
    work_by_title = {}
    for w in works:
        t = w.get("title", "").strip().strip("《》")
        if t and t not in work_by_title:
            work_by_title[t] = w
    for title, work in work_by_title.items():
        if title not in normalized_shell_map:
            continue
        primary = normalized_shell_map[title].get("primary_shell", "")
        if not primary:
            continue
        play = play_map.get(title, "其他")
        cross[primary][play].append({
            "title": title,
            "year": work.get("year"),
            "platform": work.get("platform"),
            "acq": work.get("acquisition_score", 0),
            "roi": work.get("roi_score", 0),
        })
        shell_counts[primary] += 1
        play_counts[play] += 1

    # 4a. 交叉表 markdown
    sorted_shells = [s for s, c in shell_counts.most_common() if s]
    sorted_plays = [p for p, c in play_counts.most_common() if p]

    md = ["# 题材壳 × 玩法 交叉表", "",
          f"数据源: 1570 款任天堂平台游戏(2000-2014 多机型 + 2017-2026 Switch)", "",
          f"题材壳数: {len(sorted_shells)},玩法类数: {len(sorted_plays)}", "",
          "## 完整交叉表(单元格=该组合的游戏数)", ""]
    md.append("| 题材壳 \\ 玩法 | " + " | ".join(sorted_plays) + " | **合计** |")
    md.append("|---" * (len(sorted_plays) + 2) + "|")
    for shell in sorted_shells:
        row = [shell]
        total = 0
        for play in sorted_plays:
            n = len(cross[shell].get(play, []))
            row.append(str(n) if n else "—")
            total += n
        row.append(f"**{total}**")
        md.append("| " + " | ".join(row) + " |")

    md += ["", "## 题材壳频次排名", "",
           "| 排名 | 题材壳 | 游戏数 | 累计占比 |",
           "|---|---|---:|---:|"]
    total_all = sum(shell_counts.values())
    cum = 0
    for i, (shell, n) in enumerate(shell_counts.most_common(), 1):
        cum += n
        md.append(f"| {i} | {shell} | {n} | {cum/total_all:.1%} |")

    (OUT_DIR / "04_交叉表.md").write_text("\n".join(md), encoding="utf-8")
    log(f"  04_交叉表.md ({len(sorted_shells)} 个题材壳, {len(sorted_plays)} 个玩法类)")

    # 5. 每壳 TOP-10
    md2 = ["# 每个题材壳 TOP-10 代表作", "", "按 获量+ROI 综合得分 排序", ""]

    def normalize_title(t: str) -> str:
        # 去重时忽略空格、半角全角差异、版本后缀、标点差异
        t2 = re.sub(r"\s+", "", t)
        t2 = t2.replace("(", "(").replace(")", ")")
        # 去除所有标点(便于"之"字/冒号差异不影响去重)
        t2 = re.sub(r"[:：·~~・/／\-—_『』「」【】\[\]、,，。!!??""'']", "", t2)
        # 移除"之"字(火焰之纹章 vs 火焰纹章)
        t2 = t2.replace("之", "")
        # 移除常见版本后缀
        t2 = re.sub(r"(导演剪辑版|豪华版|完整版|完美版|完全版|终极版|加强版|专家版|专业版|HD版|HD复刻版|重制版|Encore|DX|GX|Plus|\+)$", "", t2)
        return t2

    for shell in sorted_shells:
        all_works = []
        for play, items in cross[shell].items():
            all_works.extend(items)
        # 去重(去空格/版本后缀)
        seen = set()
        dedup = []
        for w in all_works:
            key = normalize_title(w["title"])
            if key not in seen:
                seen.add(key)
                dedup.append(w)
        dedup.sort(key=lambda x: -(x["acq"] + x["roi"]))
        top10 = dedup[:10]
        md2 += [f"## {shell}(共 {shell_counts[shell]} 款)", "",
                "| 排名 | 作品 | 年份 | 平台 | 获量 | ROI |",
                "|---|---|---|---|---|---|"]
        for i, w in enumerate(top10, 1):
            md2.append(f"| {i} | 《{w['title']}》 | {w['year']} | {w['platform']} | {w['acq']}/5 | {w['roi']}/5 |")
        md2.append("")
    (OUT_DIR / "05_每壳TOP10.md").write_text("\n".join(md2), encoding="utf-8")
    log(f"  05_每壳TOP10.md")

    # 6. 饱和度分析(纯数据)
    md3 = ["# 题材壳 × 玩法 饱和度分析(纯数据视角)", "",
           "说明: 本表只反映 1570 款任天堂游戏中各组合的实际密度,",
           "不评估当代手游市场。当代手游市场的对照需要单独评估。", "",
           "## 高频组合(≥10 款)", "",
           "| 题材壳 | 玩法 | 数量 |",
           "|---|---|---:|"]
    high_freq = []
    low_freq = []
    for shell in sorted_shells:
        for play in sorted_plays:
            n = len(cross[shell].get(play, []))
            if n >= 10:
                high_freq.append((shell, play, n))
            elif 1 <= n <= 3:
                low_freq.append((shell, play, n))
    high_freq.sort(key=lambda x: -x[2])
    for shell, play, n in high_freq:
        md3.append(f"| {shell} | {play} | {n} |")

    md3 += ["", "## 低频组合(1-3 款,可能的实验缝隙)", "",
            "| 题材壳 | 玩法 | 数量 |",
            "|---|---|---:|"]
    low_freq.sort(key=lambda x: x[2])
    for shell, play, n in low_freq[:80]:  # 限 80 行
        md3.append(f"| {shell} | {play} | {n} |")

    md3 += ["", "## 完全缺失组合(0 款)", "",
            "下列组合在 1570 款任天堂游戏中完全没有代表作,",
            "可能是天然不契合,也可能是真空(需结合当代市场判断)。", ""]
    missing_pairs = []
    common_shells = sorted_shells[:30]  # 取前 30 高频题材壳
    common_plays = sorted_plays[:15]    # 取前 15 高频玩法
    for shell in common_shells:
        for play in common_plays:
            if len(cross[shell].get(play, [])) == 0:
                missing_pairs.append((shell, play))
    md3.append(f"前 30 题材壳 × 前 15 玩法 = {len(common_shells)*len(common_plays)} 组合,其中缺失 {len(missing_pairs)} 个")
    md3.append("")
    md3.append("| 题材壳 | 缺失玩法 |")
    md3.append("|---|---|")
    miss_by_shell = defaultdict(list)
    for shell, play in missing_pairs:
        miss_by_shell[shell].append(play)
    for shell in common_shells:
        if shell in miss_by_shell:
            md3.append(f"| {shell} | {'、'.join(miss_by_shell[shell])} |")

    (OUT_DIR / "06_饱和度分析.md").write_text("\n".join(md3), encoding="utf-8")
    log(f"  06_饱和度分析.md")


def main():
    log("=== 任天堂游戏题材库整理 ===")
    works = load_all_analyzed()
    log(f"加载 {len(works)} 款作品")

    if len(works) < 100:
        log("[FATAL] 数据不足")
        sys.exit(1)

    # Phase 1: 题材壳提取
    shell_map = run_shell_extraction(works)
    log(f"Phase 1 完成: {len(shell_map)} 款已打标")

    # Phase 2: 合并近义词
    normalized = normalize_all_shells(shell_map)
    log(f"Phase 2 完成: 合并近义词")

    # 统计变化
    raw_primary_set = set()
    norm_primary_set = set()
    for d in shell_map.values():
        if d.get("primary_shell"):
            raw_primary_set.add(d["primary_shell"])
    for d in normalized.values():
        if d.get("primary_shell"):
            norm_primary_set.add(d["primary_shell"])
    log(f"  原始题材壳数: {len(raw_primary_set)}, 合并后: {len(norm_primary_set)}")

    # Phase 3 + 4: 玩法归类 + 输出
    write_outputs(works, shell_map, normalized)
    log("=== 完成 ===")


if __name__ == "__main__":
    main()
