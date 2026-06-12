#!/usr/bin/env python3
"""竞品库受控词表 —— 主品类 / 玩法标签的唯一真相源。

collector 用它约束 DeepSeek 输出，sync_to_bitable 用它归一化后再写多维表格。
多维表格的字段选项应与本文件对齐（本文件是 source of truth）。

设计原则：
- 主品类 PRIMARY_CATEGORIES 是**封闭枚举**，模型只能从中选最接近的一个。
- 玩法标签 GAMEPLAY_TAGS 是**推荐集**，优先选用；允许少量新增，但同义一律归并。
- ALIAS 表把历史脏值 / 同义写法映射回受控值，保证存量数据重新同步时也收敛。
"""

# ── 主品类：封闭受控集（27 个）────────────────────────────
PRIMARY_CATEGORIES = [
    "SLG", "塔防", "卡牌", "Roguelite", "放置RPG", "放置", "模拟经营",
    "消除", "合成", "射击", "RPG", "ARPG", "策略", "休闲", "超休闲",
    "解谜", "益智", "生存", "冒险", "动作", "体育", "搜打撤",
    "互动影游", "二合", "AI陪伴", "派对游戏", "社交",
]

# 历史脏值 / 同义 / 过细分类 → 受控值
PRIMARY_ALIAS = {
    "三消": "消除",
    "棋盘": "策略",
    "自走棋": "策略",
    "大富翁RPG": "策略",
    "策略RPG": "策略",
    "弹球": "休闲",
    "恋爱换装": "休闲",
    "多人对抗/寻宝": "搜打撤",
    "第一人称射击": "射击",
    "FPS": "射击",
    "MMO": "RPG",
    "MMORPG": "RPG",
    "回合制RPG": "RPG",
    "地牢RPG": "RPG",
    "地牢": "Roguelite",
    "卡牌RPG": "卡牌",
    "卡牌构筑": "卡牌",
    "Roguelite卡牌": "Roguelite",
    "Roguelike": "Roguelite",
    "竞速": "体育",
    "放置塔防": "塔防",
    "放置经营": "放置RPG",
    "模拟": "模拟经营",
    "动作冒险": "动作",
    "动作角色扮演": "ARPG",
    "益智解谜": "解谜",
    "合成解谜": "解谜",
    "拼图": "解谜",
    "找茬": "益智",
    "找茬/找不同": "益智",
    "短剧": "互动影游",
    "视觉小说": "互动影游",
    "乙女游戏": "互动影游",
}

# ── 玩法标签：推荐受控集（频次≥2 去重同义后）──────────────
GAMEPLAY_TAGS = [
    "模拟经营", "策略", "生存", "塔防", "Roguelite", "割草", "丧尸",
    "SLG", "RPG", "放置", "休闲", "卡牌", "科幻", "剧情", "建造",
    "射击", "中世纪", "开放世界", "搜打撤", "骰子", "二次元", "动作",
    "合成", "推箱子", "真人互动", "卡牌收集", "猫咪", "生活模拟",
    "像素风", "国风", "经营", "竖屏", "开箱", "背包管理", "独立游戏",
    "写实", "AI原生", "俯视角", "海洋题材", "RTS", "医院", "挖矿",
    "废土", "放置街机", "微观", "数值门", "Thronefall-like", "KSlike",
]

# 标签同义归并
TAG_ALIAS = {
    "肉鸽": "Roguelite",
    "Roguelike": "Roguelite",
    "像素": "像素风",
    "城建": "建造",
    "城镇建设": "建造",
    "基地建设": "建造",
    "模拟": "模拟经营",
}

_PRIMARY_SET = set(PRIMARY_CATEGORIES)
_TAG_SET = set(GAMEPLAY_TAGS)


def normalize_primary(value: str) -> str | None:
    """归一化主品类到受控集。未知值返回原值（由调用方决定是否保留）。"""
    if not value or str(value).strip() in ("", "未知", "待确认"):
        return None
    v = str(value).strip()
    if v in _PRIMARY_SET:
        return v
    return PRIMARY_ALIAS.get(v, v)  # 命中 alias 则映射，否则原样返回


def normalize_tags(values, strict: bool = False) -> list[str]:
    """归一化玩法标签列表：同义归并 + 去重，保序。

    strict=True 时丢弃受控集外的标签（同步多维表格用，防止选项膨胀）。
    strict=False 保留全部（写 .md 用，不丢原始信息）。
    """
    if not values:
        return []
    if isinstance(values, str):
        values = [values]
    out = []
    seen = set()
    for x in values:
        v = str(x).strip()
        if not v or v in ("未知", "待确认"):
            continue
        v = TAG_ALIAS.get(v, v)
        if strict and v not in _TAG_SET:
            continue
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


def primary_in_vocab(value: str) -> bool:
    """归一化后是否落在封闭受控集内。"""
    n = normalize_primary(value)
    return n in _PRIMARY_SET if n else True  # None(空) 视为合法


if __name__ == "__main__":
    # 自检：跑本地竞品库全量，报告归一化覆盖率
    import re, json
    from pathlib import Path
    from collections import Counter

    COMPETE = Path(__file__).resolve().parents[3] / "archive" / "资料" / "竞品库"

    def parse_yaml(fp):
        text = fp.read_text(encoding="utf-8")
        m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
        if not m:
            return {}
        d = {}
        for line in m.group(1).split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            mm = re.match(r"^(\w[\w_]*)\s*:\s*(.*)", line)
            if mm:
                k, v = mm.group(1), mm.group(2).strip()
                if v.startswith("["):
                    try:
                        d[k] = json.loads(v)
                    except json.JSONDecodeError:
                        try:
                            d[k] = json.loads(v.replace("'", '"'))
                        except Exception:
                            d[k] = v
                elif v.startswith('"') and v.endswith('"'):
                    d[k] = v[1:-1]
                elif v in ("null", "~"):
                    d[k] = None
                else:
                    d[k] = v
        return d

    files = [f for w in ["轻度", "中度", "重度"] for f in (COMPETE / w).glob("*.md")]
    prim_unmapped = Counter()
    prim_ok = 0
    tag_total = 0
    tag_in_vocab = 0
    new_tags = Counter()

    for fp in files:
        d = parse_yaml(fp)
        p = d.get("category_primary")
        if p:
            n = normalize_primary(p)
            if n in _PRIMARY_SET:
                prim_ok += 1
            else:
                prim_unmapped[p] += 1
        for t in normalize_tags(d.get("category_tags", [])):
            tag_total += 1
            if t in _TAG_SET:
                tag_in_vocab += 1
            else:
                new_tags[t] += 1

    print(f"主品类: {prim_ok}/{prim_ok + sum(prim_unmapped.values())} 落入受控集")
    if prim_unmapped:
        print(f"  ⚠️ 未覆盖（需补 alias 或受控集）: {dict(prim_unmapped)}")
    else:
        print("  ✅ 100% 覆盖")
    print(f"\n标签: {tag_in_vocab}/{tag_total} 在受控集内 ({tag_in_vocab/tag_total*100:.0f}%)")
    print(f"  受控集外（保留为新增选项）: {len(new_tags)} 种、{sum(new_tags.values())} 次")
    print(f"  其中出现≥2次的受控集外标签: {[k for k,v in new_tags.items() if v>=2]}")
