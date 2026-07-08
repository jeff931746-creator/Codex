#!/usr/bin/env python3
"""
汇总 测试_001 结果,生成 4 份报告:
  04-reports/覆盖率报告_测试001.md
  04-reports/边界混淆表_测试001.md
  04-reports/反证日志_测试001.md
  04-reports/无主归类聚类_测试001.md
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path("/Users/mt/Documents/Codex")
TEST_DIR = ROOT / "archive/资料/买量组合库/题材库/测试/测试_001"
RESULTS_DIR = TEST_DIR / "03-results"
REPORTS_DIR = TEST_DIR / "04-reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_PRIMARY = {
    # 正例期望主归类(来自 v0.2.1 候选库正例表)
    "末世铁路王国": "绝境守存", "极寒末世囤货": "绝境守存", "美式丧尸末日生存": "绝境守存",
    "古墓盗宝逃生": "撤离夺宝", "星际矿工撤离": "撤离夺宝", "废土拾荒撤离": "撤离夺宝",
    "基因突变实验室": "异种进化", "基因异兽融合": "异种进化", "变异孢子繁衍": "异种进化",
    "恐龙公园经营": "巨物驯御", "深海巨兽驯养": "巨物驯御", "神话妖兽契约": "巨物驯御",
    "末日机甲改造": "废械拼强", "废土机甲改装": "废械拼强", "废土义体拆装": "废械拼强",
    "古埃及法老陵墓探险": "禁忌探索", "克苏鲁深海恐怖探索": "禁忌探索", "深海遗迹探索": "禁忌探索",
    "天师镇邪收鬼": "镇邪收容", "民俗怪谈收容": "镇邪收容", "诡异收容武装": "镇邪收容",
    "算命改命逆天": "改命逆袭", "重生复仇改命": "改命逆袭", "玄学算命改修仙": "改命逆袭",
    "鉴宝捡漏暴富": "暴富翻身", "韩式财阀逆袭经营": "暴富翻身", "赘婿翻身商战": "暴富翻身",
    "豪门遗产争夺": "权争上位", "宫斗权谋上位": "权争上位", "海盗岛屿争霸": "权争上位",
    "荒野领主拓荒": "领地开拓", "星际殖民开拓": "领地开拓", "修仙宗门建设": "领地开拓",
    "异能觉醒都市": "异能爆发", "都市异能觉醒": "异能爆发", "赛博修仙卡牌": "异能爆发",
}


def load_results():
    results = []
    for p in sorted(RESULTS_DIR.glob("*.json")):
        if p.name.startswith("_"):
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        results.append(data)
    return results


def main():
    results = load_results()
    print(f"[info] 加载 {len(results)} 条结果")

    # 分组统计
    by_group = defaultdict(list)
    for r in results:
        by_group[r["sample_meta"]["sample_group"]].append(r)

    total = len(results)
    n_pos = len(by_group.get("positive", []))
    n_bnd = len(by_group.get("boundary", []))
    n_blind = len(by_group.get("blind", []))

    # ===== 覆盖率报告 =====
    motif_counter = Counter()
    unassigned_count = 0
    unassigned_reason_counter = Counter()
    test_result_counter = Counter()
    observer_only_count = 0
    observer_tag_counter = Counter()

    for r in results:
        c = r.get("classification") or {}
        motif = c.get("primary_motif")
        if motif == "未归类":
            unassigned_count += 1
            unassigned_reason_counter[c.get("unassigned_reason", "")] += 1
        else:
            motif_counter[motif] += 1
        test_result_counter[c.get("test_result")] += 1
        for tag in c.get("observer_tags") or []:
            observer_tag_counter[tag] += 1
        if motif == "未归类" and (c.get("unassigned_reason") == "only_observer_tag_matched"):
            observer_only_count += 1

    primary_rate = (total - unassigned_count) / total if total else 0
    unassigned_rate = unassigned_count / total if total else 0
    observer_only_rate = observer_only_count / total if total else 0

    lines = [
        f"# 覆盖率报告 测试_001",
        f"",
        f"- 生成日期: 2026-05-14",
        f"- 候选库版本: v0.2.1",
        f"- 测试矩阵版本: v0.2.1",
        f"- LLM route: DeepSeek_Official_Pro",
        f"- 总样本数: {total}(正例 {n_pos} / 混淆 {n_bnd} / 盲选 {n_blind})",
        f"",
        f"## 核心指标",
        f"",
        f"| 指标 | 数值 | 通过线 | 判断 |",
        f"|---|---:|---|---|",
        f"| 主归类率 | {primary_rate:.1%} | 60%-85% | {'OK' if 0.60 <= primary_rate <= 0.85 else ('过高(强行归类信号)' if primary_rate > 0.85 else '过低(候选库偏窄)')} |",
        f"| 无主归类率 | {unassigned_rate:.1%} | 5%-30% | {'OK' if 0.05 <= unassigned_rate <= 0.30 else ('过低(可能被强行归类)' if unassigned_rate < 0.05 else '过高(候选库偏窄)')} |",
        f"| 仅命中观察标签率 | {observer_only_rate:.1%} | ≤25% | {'OK' if observer_only_rate <= 0.25 else '过高(标签具升级潜力)'} |",
        f"",
        f"## test_result 分布",
        f"",
        f"| 状态 | 数量 | 占比 |",
        f"|---|---:|---:|",
    ]
    for k in ("pass", "ambiguous", "unassigned", "fail"):
        n = test_result_counter.get(k, 0)
        lines.append(f"| {k} | {n} | {n/total:.1%} |")

    lines += [
        "",
        "## 主母题命中分布",
        "",
        "| 主母题材 | 命中数 |",
        "|---|---:|",
    ]
    for motif, n in sorted(motif_counter.items(), key=lambda x: -x[1]):
        lines.append(f"| {motif} | {n} |")
    lines.append(f"| **未归类** | {unassigned_count} |")

    lines += [
        "",
        "## 未归类原因分布",
        "",
        "| 原因 | 数量 |",
        "|---|---:|",
    ]
    for reason, n in sorted(unassigned_reason_counter.items(), key=lambda x: -x[1]):
        if reason:
            lines.append(f"| {reason} | {n} |")

    lines += [
        "",
        "## 观察标签命中分布",
        "",
        "| 标签 | 命中数 |",
        "|---|---:|",
    ]
    for tag, n in sorted(observer_tag_counter.items(), key=lambda x: -x[1]):
        lines.append(f"| {tag} | {n} |")

    # 正例与期望对照
    if by_group.get("positive"):
        positive_mismatches = []
        for r in by_group["positive"]:
            theme = r["sample_meta"]["raw_theme"]
            actual = (r.get("classification") or {}).get("primary_motif")
            expected = EXPECTED_PRIMARY.get(theme)
            if expected and actual != expected:
                positive_mismatches.append((theme, expected, actual,
                                            (r.get("classification") or {}).get("boundary_notes", "")))
        match_rate = (len(by_group["positive"]) - len(positive_mismatches)) / len(by_group["positive"])
        lines += [
            "",
            "## 正例符合率(vs v0.2.1 候选库期望)",
            "",
            f"- 正例数: {len(by_group['positive'])}",
            f"- 不符合期望数: {len(positive_mismatches)}",
            f"- 符合率: {match_rate:.1%}",
            "",
            "### 与期望不符的正例",
            "",
            "| 题材 | 候选库期望 | 实际归类 | 边界说明 |",
            "|---|---|---|---|",
        ]
        for theme, exp, act, note in positive_mismatches:
            lines.append(f"| {theme} | {exp} | {act} | {note[:120]} |")

    lines += [
        "",
        "## 健康度判断",
        "",
    ]
    flags = []
    if primary_rate < 0.60:
        flags.append("- 主归类率 < 60%: 候选库偏窄,需扩库")
    elif primary_rate > 0.90:
        flags.append("- 主归类率 > 90%: 危险信号,执行者可能被迫强行归类")
    if unassigned_rate > 0.30:
        flags.append("- 无主归类率 > 30%: 体系覆盖缺口偏大,需扩库")
    if observer_only_rate > 0.25:
        flags.append("- 仅命中观察标签率 > 25%: 至少一个观察标签具备升级潜力")
    if not flags:
        flags.append("- 各指标处于健康区间,可进入混淆裁定与无主聚类")
    lines.extend(flags)

    (REPORTS_DIR / "覆盖率报告_测试001.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"[ok] 写入 覆盖率报告_测试001.md")

    # ===== 边界混淆表 =====
    bnd_lines = [
        "# 边界混淆表 测试_001",
        "",
        "记录混淆边界样本的归类结果,以及正例样本中 test_result=ambiguous 的样本。",
        "",
        "## 混淆边界样本归类",
        "",
        "| 题材 | 实际归类 | test_result | 观察标签 | 边界说明 |",
        "|---|---|---|---|---|",
    ]
    for r in by_group.get("boundary", []):
        c = r.get("classification") or {}
        theme = r["sample_meta"]["raw_theme"]
        tags = ",".join(c.get("observer_tags") or [])
        bnd_lines.append(f"| {theme} | {c.get('primary_motif')} | {c.get('test_result')} | {tags} | {c.get('boundary_notes','')[:200]} |")

    bnd_lines += [
        "",
        "## 所有 test_result=ambiguous 样本(含正例)",
        "",
        "| 题材 | 分组 | 归类 | 边界说明 |",
        "|---|---|---|---|",
    ]
    for r in results:
        c = r.get("classification") or {}
        if c.get("test_result") == "ambiguous":
            bnd_lines.append(f"| {r['sample_meta']['raw_theme']} | {r['sample_meta']['sample_group']} | {c.get('primary_motif')} | {c.get('boundary_notes','')[:200]} |")

    (REPORTS_DIR / "边界混淆表_测试001.md").write_text("\n".join(bnd_lines), encoding="utf-8")
    print(f"[ok] 写入 边界混淆表_测试001.md")

    # ===== 反证日志 =====
    refute_lines = [
        "# 反证日志 测试_001",
        "",
        "记录 test_result=fail 的样本(题材结构本身不成立)、JSON 校验错误、及正例与期望不符的样本。",
        "",
        "## test_result=fail 样本",
        "",
        "| 题材 | 分组 | 原因 |",
        "|---|---|---|",
    ]
    for r in results:
        c = r.get("classification") or {}
        if c.get("test_result") == "fail":
            refute_lines.append(f"| {r['sample_meta']['raw_theme']} | {r['sample_meta']['sample_group']} | {c.get('boundary_notes','')[:200]} |")

    refute_lines += [
        "",
        "## 校验错误样本",
        "",
        "| 题材 | 分组 | 错误 |",
        "|---|---|---|",
    ]
    for r in results:
        if r.get("validation_errors"):
            refute_lines.append(f"| {r['sample_meta']['raw_theme']} | {r['sample_meta']['sample_group']} | {'; '.join(r['validation_errors'][:2])} |")

    refute_lines += [
        "",
        "## 正例与候选库期望不一致样本",
        "",
        "见 `覆盖率报告_测试001.md` 末尾的'与期望不符的正例'。意义:候选库需要决定是修期望还是修定义。",
    ]
    (REPORTS_DIR / "反证日志_测试001.md").write_text("\n".join(refute_lines), encoding="utf-8")
    print(f"[ok] 写入 反证日志_测试001.md")

    # ===== 无主归类聚类(原始记录,仲裁者后续手工聚类) =====
    cluster_lines = [
        "# 无主归类聚类 测试_001",
        "",
        "本文件只记录所有 primary_motif=未归类 样本,仲裁者后续做聚类。",
        "",
        "## 聚类阈值(矩阵 v0.2.1)",
        "",
        "- 同一观察标签 ≥ 6 条 → 升格为候选母题候补",
        "- 同类无主样本簇 ≥ 6 条 → 成为新候选母题",
        "- 同类无主样本簇 ≥ 3 且 < 6 条 → 二级切口或观察簇",
        "- 单条无主样本 → 只记录",
        "",
        "## 全部 未归类 样本",
        "",
        "| 题材 | 分组 | 主心理任务 | 冲突结构 | 未归类原因 | 观察标签 | 边界说明 |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in results:
        c = r.get("classification") or {}
        if c.get("primary_motif") == "未归类":
            tags = ",".join(c.get("observer_tags") or [])
            cluster_lines.append(
                f"| {r['sample_meta']['raw_theme']} | {r['sample_meta']['sample_group']} "
                f"| {c.get('primary_psych_task','')[:80]} | {c.get('conflict_structure','')[:80]} "
                f"| {c.get('unassigned_reason','')} | {tags} | {c.get('boundary_notes','')[:120]} |"
            )

    cluster_lines += [
        "",
        "## 仲裁者待办",
        "",
        "1. 按主心理任务相似度、冲突结构相似度、用户角色位置相近度做聚类",
        "2. 对每个簇判断阈值(≥6 / 3-5 / 1-2)",
        "3. 把升格簇写入候选库 v0.3,把切口簇写入 secondary_cut_cluster",
    ]
    (REPORTS_DIR / "无主归类聚类_测试001.md").write_text("\n".join(cluster_lines), encoding="utf-8")
    print(f"[ok] 写入 无主归类聚类_测试001.md")


if __name__ == "__main__":
    main()
