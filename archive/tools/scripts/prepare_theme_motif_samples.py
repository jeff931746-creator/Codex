#!/usr/bin/env python3
"""
准备 测试_001 的 60 条样本(30 正例 + 18 混淆 + 12 盲选)。

抽样规则(矩阵 v0.2.1 第 3 修复):
- 编号 1-133 来自 题材总表.md 当前出现顺序
- 仲裁者抛硬币:正面 N=7,反面 N=13(由本脚本 random.choice([7,13]) 模拟)
- 从 N 开始,步长 11 抽 12 条,跳过已用样本
- 抽样种子 fixed,确保可复现

输出:
  02-samples/positive_30.json
  02-samples/boundary_18.json
  02-samples/blind_12.json
  02-samples/sampling_log.md
"""
from __future__ import annotations

import json
import random
import re
from pathlib import Path

ROOT = Path("/Users/mt/Documents/Codex")
THEMES_TABLE = ROOT / "archive/资料/买量组合库/题材总表.md"
TEST_DIR = ROOT / "archive/资料/买量组合库/题材库/测试/测试_001"
SAMPLES_DIR = TEST_DIR / "02-samples"
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

POSITIVE_THEMES = [
    "末世铁路王国", "极寒末世囤货", "美式丧尸末日生存",
    "古墓盗宝逃生", "星际矿工撤离", "废土拾荒撤离",
    "基因突变实验室", "基因异兽融合", "变异孢子繁衍",
    "恐龙公园经营", "深海巨兽驯养", "神话妖兽契约",
    "末日机甲改造", "废土机甲改装", "废土义体拆装",
    "古埃及法老陵墓探险", "克苏鲁深海恐怖探索", "深海遗迹探索",
    "天师镇邪收鬼", "民俗怪谈收容", "诡异收容武装",
    "算命改命逆天", "重生复仇改命", "玄学算命改修仙",
    "鉴宝捡漏暴富", "韩式财阀逆袭经营", "赘婿翻身商战",
    "豪门遗产争夺", "宫斗权谋上位", "海盗岛屿争霸",
    "荒野领主拓荒", "星际殖民开拓", "修仙宗门建设",
    "异能觉醒都市", "都市异能觉醒", "赛博修仙卡牌",
]

BOUNDARY_THEMES = [
    "虫族母巢进化", "血肉飞升修仙", "灵异直播探险",
    "鬼怪公寓经营", "阴阳当铺赎魂", "克苏鲁渔夫收集",
    "深海巨兽孵化", "末日基因改造", "废土拾荒者撤离",
    "地底矿脉争夺", "末日丧尸基地车", "西部淘金枪战",
    "吸血鬼贵族血统养成", "黑道卧底风云", "锦衣绣春暗杀",
    "直播修仙带货", "赛博朋克黑客入侵",
]


def parse_themes_table(path: Path) -> list[dict]:
    """解析题材总表 markdown,返回所有题材的字段字典."""
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.split("|")]
            cells = cells[1:-1] if cells and cells[-1] == "" else cells[1:]
            if len(cells) < 14:
                continue
            theme = cells[0]
            if theme in ("题材", "------") or "---" in theme:
                continue
            rows.append({
                "raw_theme": theme,
                "quadrant": cells[1],
                "acquisition_score": cells[2],
                "roi_score": cells[3],
                "evidence_level": cells[4],
                "recommendation": cells[5],
                "playstyle_hint": cells[6],
                "entry_cut": cells[7],
                "weakness": cells[8],
                "material_hooks": cells[9],
                "review_notes": cells[12] if len(cells) > 12 else "",
                "source": cells[13] if len(cells) > 13 else "",
                "discovered_at": cells[14] if len(cells) > 14 else "",
            })
    return rows


def main():
    all_themes = parse_themes_table(THEMES_TABLE)
    print(f"[parse] 题材总表共 {len(all_themes)} 条")
    name_index = {t["raw_theme"]: t for t in all_themes}
    indexed = [(i + 1, t) for i, t in enumerate(all_themes)]
    name_to_idx = {t["raw_theme"]: i for i, t in indexed}

    # 1. 30 条正例
    positive = []
    missing_pos = []
    for theme in POSITIVE_THEMES:
        rec = name_index.get(theme)
        if rec is None:
            missing_pos.append(theme)
            continue
        positive.append({"sample_group": "positive", "table_index": name_to_idx[theme], **rec})
    if missing_pos:
        for m in missing_pos:
            candidates = [n for n in name_index if m[:3] in n or m[-3:] in n]
            print(f"[warn] 正例样本未在总表中: {m}; 相近候选: {candidates[:5]}")

    # 2. 18 条混淆
    boundary = []
    missing_bd = []
    for theme in BOUNDARY_THEMES:
        rec = name_index.get(theme)
        if rec is None:
            missing_bd.append(theme)
            continue
        boundary.append({"sample_group": "boundary", "table_index": name_to_idx[theme], **rec})
    if missing_bd:
        for m in missing_bd:
            candidates = [n for n in name_index if m[:3] in n or m[-3:] in n]
            print(f"[warn] 混淆样本未在总表中: {m}; 相近候选: {candidates[:5]}")

    # 3. 12 条盲选(抛硬币 + 步长 11)
    rng = random.Random("2026-05-14-theme-motif-v0.2.1-arbiter-coin")
    coin = rng.choice(["heads", "tails"])
    N = 7 if coin == "heads" else 13
    used_names = {t["raw_theme"] for t in positive} | {t["raw_theme"] for t in boundary}

    blind = []
    sampling_log = [
        f"# 抽样日志(测试_001)",
        f"",
        f"- 仲裁者抛硬币种子: `2026-05-14-theme-motif-v0.2.1-arbiter-coin`",
        f"- 抛硬币结果: {coin}",
        f"- 起始位置 N: {N}",
        f"- 步长: 11",
        f"- 总表题材数: {len(all_themes)}",
        f"- 已用样本数(正例+混淆): {len(used_names)}",
        f"",
        f"## 抽样过程",
        f"",
    ]
    cursor = N
    visited = set()
    while len(blind) < 12 and len(visited) < len(all_themes):
        idx = ((cursor - 1) % len(all_themes)) + 1
        if idx in visited:
            cursor += 11
            continue
        visited.add(idx)
        rec = indexed[idx - 1][1]
        if rec["raw_theme"] in used_names:
            sampling_log.append(f"- 编号 {idx} 题材 `{rec['raw_theme']}` -> 跳过(已在已用样本中)")
            cursor += 11
            continue
        blind.append({"sample_group": "blind", "table_index": idx, **rec})
        sampling_log.append(f"- 编号 {idx} 题材 `{rec['raw_theme']}` -> 入选盲选样本")
        cursor += 11

    # 落盘
    (SAMPLES_DIR / f"positive_{len(positive)}.json").write_text(
        json.dumps(positive, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (SAMPLES_DIR / f"boundary_{len(boundary)}.json").write_text(
        json.dumps(boundary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (SAMPLES_DIR / f"blind_{len(blind)}.json").write_text(
        json.dumps(blind, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (SAMPLES_DIR / "sampling_log.md").write_text("\n".join(sampling_log), encoding="utf-8")

    print(f"[ok] 正例 {len(positive)} 条, 混淆 {len(boundary)} 条, 盲选 {len(blind)} 条")
    print(f"[ok] 写入 {SAMPLES_DIR}")
    if missing_pos or missing_bd:
        print(f"[FAIL] 有样本未匹配,请人工补全后再启动测试")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
