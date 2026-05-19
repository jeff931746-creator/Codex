#!/usr/bin/env python3
"""
v1.1 索引生成脚本(Step 6)

从样本目录扫描所有作品的 yaml frontmatter,产出多个 markdown 索引视图:

- 00_总览.md           — 库总览 dashboard(数量 + L1 分布 + N 分布 + Top 高获量)
- 索引/按L1主题.md      — 按 L1 大类分组,每组列全部作品
- 索引/按L2子题材.md    — 按 L2 标签分组,每个 L2 标签 → 作品列表
- 索引/按L3视觉.md      — 按 L3 视觉标签分组
- 索引/按N+T组合.md     — 按心理需求 × 任务态组合分组
- 索引/按获量.md        — 按 acquisition_score 5→1 列全部
- 索引/按年代.md        — 按 year_first 倒序

不调 LLM,纯本地从样本 yaml 生成。

用法:
    cd /Users/mt/Documents/Codex
    python3 archive/tools/scripts/theme_lib_v1_indexes.py
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/Users/mt/Documents/Codex")
LIB_ROOT = WORKSPACE / "archive/资料/历史题材库"
SAMPLES_DIR = LIB_ROOT / "样本/按媒介"
INDEXES_DIR = LIB_ROOT / "样本/索引"
OVERVIEW_FILE = LIB_ROOT / "00_总览.md"
TODAY = datetime.now().strftime("%Y-%m-%d")

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def parse_yaml_simple(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fields = {}
    for line in m.group(1).splitlines():
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue
        m2 = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.*)$", line)
        if m2:
            value = m2.group(2)
            value = re.sub(r"\s+#.*$", "", value).strip()
            fields[m2.group(1)] = value
    return fields


def parse_list(v: str) -> list[str]:
    if not v or v == "[]":
        return []
    v = v.strip()
    if not (v.startswith("[") and v.endswith("]")):
        return []
    inner = v[1:-1].strip()
    if not inner:
        return []
    parts = []
    current = ""
    in_quote = False
    quote_char = ""
    for ch in inner:
        if ch in ('"', "'"):
            if not in_quote:
                in_quote = True
                quote_char = ch
            elif ch == quote_char:
                in_quote = False
        elif ch == "," and not in_quote:
            parts.append(current.strip().strip('"').strip("'"))
            current = ""
            continue
        current += ch
    if current.strip():
        parts.append(current.strip().strip('"').strip("'"))
    return parts


def strip_quote(s: str) -> str:
    s = s.strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s


class Work:
    """单部作品的可索引摘要"""
    def __init__(self, fields: dict, path: Path):
        self.path = path
        self.work_id = fields.get("work_id", "?")
        self.work_name = strip_quote(fields.get("work_name", "?"))
        self.media_type = fields.get("media_type", "?")
        self.year = int(fields.get("year_first", "0") or 0)
        self.n_main = fields.get("n_main", "?")
        self.n_others = parse_list(fields.get("n_others", "[]"))
        self.t_can_carry = parse_list(fields.get("t_can_carry", "[]"))
        self.theme_primary = fields.get("theme_primary", "TBD")
        self.theme_secondary = parse_list(fields.get("theme_secondary", "[]"))
        self.visual_tags = parse_list(fields.get("visual_tags", "[]"))
        try:
            self.acq = int(fields.get("acquisition_score", "0") or 0)
        except ValueError:
            self.acq = 0
        self.environment = strip_quote(fields.get("environment", ""))
        self.core_conflict = strip_quote(fields.get("core_conflict", ""))

    @property
    def rel_link(self) -> str:
        rel = self.path.relative_to(LIB_ROOT)
        return f"[{self.work_name}]({rel})"


def scan_samples() -> list[Work]:
    works = []
    for media_dir in sorted(SAMPLES_DIR.iterdir()):
        if not media_dir.is_dir() or not media_dir.name[0].isdigit():
            continue
        for fp in sorted(media_dir.glob("*.md")):
            try:
                text = fp.read_text(encoding="utf-8")
                fields = parse_yaml_simple(text)
                if fields and "work_id" in fields:
                    works.append(Work(fields, fp))
            except Exception as e:
                print(f"[WARN] {fp.name}: {e}")
    return works


# ========== 索引生成 ==========
def write_overview(works: list[Work]):
    total = len(works)
    media_counter = Counter(w.media_type for w in works)
    n_counter = Counter(w.n_main for w in works)
    l1_counter = Counter(w.theme_primary for w in works)
    acq_counter = Counter(w.acq for w in works)

    # Top 50 高获量
    top_acq = sorted([w for w in works if w.acq >= 4], key=lambda w: (-w.acq, w.work_name))[:50]

    lines = [
        f"# 历史题材库 v1.1 总览\n",
        f"> 更新日期:{TODAY} | 总样本:{total} 部\n",
        f"> 配套:[SCHEMA.md](SCHEMA.md) / [TAGS.md](TAGS.md) / [样本/索引/](样本/索引/)\n",
        "",
        "## 一、样本规模",
        "",
        "| 媒介 | 数量 | 占比 |",
        "|---|---|---|",
    ]
    media_name = {"ANI": "日本动漫", "TVW": "欧美影视", "MVK": "韩国电影", "LIT": "海外文学"}
    for code, name in media_name.items():
        n = media_counter.get(code, 0)
        pct = n / total * 100 if total else 0
        lines.append(f"| {name} ({code}) | {n} | {pct:.1f}% |")
    lines.append(f"| **合计** | **{total}** | 100% |")
    lines.append("")

    # N 分布
    lines.extend([
        "## 二、SDT 心理需求分布(主 N)",
        "",
        "| N | 数量 | 占比 | 含义 |",
        "|---|---|---|---|",
    ])
    n_desc = {"N-Comp": "胜任感(变强/掌控/智斗)", "N-Auto": "自主性(自由探索/自定节奏)", "N-Rel": "关系感(温和归属/权力)"}
    for n in ["N-Comp", "N-Rel", "N-Auto"]:
        c = n_counter.get(n, 0)
        pct = c / total * 100 if total else 0
        lines.append(f"| {n} | {c} | {pct:.1f}% | {n_desc.get(n, '')} |")
    lines.append("")

    # L1 分布
    lines.extend([
        "## 三、L1 主题大类分布",
        "",
        "| L1 主题 | 数量 | 占比 |",
        "|---|---|---|",
    ])
    for tag, c in sorted(l1_counter.items(), key=lambda x: -x[1]):
        if tag == "TBD":
            continue
        pct = c / total * 100 if total else 0
        lines.append(f"| {tag} | {c} | {pct:.1f}% |")
    if l1_counter.get("TBD"):
        lines.append(f"| (TBD 未补) | {l1_counter['TBD']} | - |")
    lines.append("")

    # 获量分布
    lines.extend([
        "## 四、acquisition_score 分布",
        "",
        "| 获量 | 数量 |",
        "|---|---|",
    ])
    for score in [5, 4, 3, 2, 1, 0]:
        c = acq_counter.get(score, 0)
        if c:
            lines.append(f"| {score} | {c} |")
    lines.append("")

    # Top 高获量
    lines.extend([
        "## 五、Top 50 高获量作品(acquisition_score ≥ 4)",
        "",
        "| 作品 | 媒介 | 年份 | L1 | 获量 | 主 N | 链接 |",
        "|---|---|---|---|---|---|---|",
    ])
    for w in top_acq:
        rel = w.path.relative_to(LIB_ROOT)
        lines.append(f"| {w.work_name} | {w.media_type} | {w.year} | {w.theme_primary} | {w.acq} | {w.n_main} | [↓]({rel}) |")
    lines.append("")

    # 索引导航
    lines.extend([
        "## 六、索引导航",
        "",
        "- [样本/索引/按L1主题.md](样本/索引/按L1主题.md) — 按主题大类查",
        "- [样本/索引/按L2子题材.md](样本/索引/按L2子题材.md) — 按细分子题材查(如'丧尸/二战/异世界穿越')",
        "- [样本/索引/按L3视觉.md](样本/索引/按L3视觉.md) — 按视觉标签查(如'废土/机甲/数字雨')",
        "- [样本/索引/按N+T组合.md](样本/索引/按N+T组合.md) — 按心理需求 × 任务态查(立项工具)",
        "- [样本/索引/按获量.md](样本/索引/按获量.md) — 按 acquisition_score 高到低排",
        "- [样本/索引/按年代.md](样本/索引/按年代.md) — 按首发年倒序",
        "",
    ])

    OVERVIEW_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✓ {OVERVIEW_FILE.relative_to(LIB_ROOT)}")


def write_index_by_l1(works: list[Work]):
    by_l1 = defaultdict(list)
    for w in works:
        by_l1[w.theme_primary].append(w)

    lines = [
        f"# 按 L1 主题大类索引\n",
        f"> 更新:{TODAY} | 总作品:{len(works)} | L1 大类:{len(by_l1)}",
        "",
        "## L1 大类概览",
        "",
        "| L1 主题 | 作品数 | 跳转 |",
        "|---|---|---|",
    ]
    for tag, ws in sorted(by_l1.items(), key=lambda x: -len(x[1])):
        if tag == "TBD":
            continue
        anchor = tag.replace(" ", "-").lower()
        lines.append(f"| {tag} | {len(ws)} | [↓](#{anchor}) |")
    lines.append("")

    for tag, ws in sorted(by_l1.items(), key=lambda x: -len(x[1])):
        if tag == "TBD":
            continue
        lines.append(f"## {tag}\n")
        lines.append(f"共 {len(ws)} 部。\n")
        lines.append("| 作品 | 媒介 | 年份 | L2 子题材 | 获量 | 主 N |")
        lines.append("|---|---|---|---|---|---|")
        for w in sorted(ws, key=lambda x: (-x.acq, -x.year, x.work_name)):
            l2_str = " / ".join(w.theme_secondary[:5]) if w.theme_secondary else "-"
            rel = w.path.relative_to(LIB_ROOT)
            lines.append(f"| [{w.work_name}]({rel}) | {w.media_type} | {w.year} | {l2_str} | {w.acq} | {w.n_main} |")
        lines.append("")

    fp = INDEXES_DIR / "按L1主题.md"
    fp.write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✓ {fp.relative_to(LIB_ROOT)}")


def write_index_by_l2(works: list[Work]):
    by_l2 = defaultdict(list)
    for w in works:
        for tag in w.theme_secondary:
            by_l2[tag].append(w)

    lines = [
        f"# 按 L2 子题材索引\n",
        f"> 更新:{TODAY} | 总作品:{len(works)} | L2 标签:{len(by_l2)}",
        "",
        "## L2 标签概览(按作品数倒序)",
        "",
        "| L2 标签 | 作品数 |",
        "|---|---|",
    ]
    sorted_l2 = sorted(by_l2.items(), key=lambda x: -len(x[1]))
    for tag, ws in sorted_l2:
        lines.append(f"| {tag} | {len(ws)} |")
    lines.append("")

    for tag, ws in sorted_l2:
        if len(ws) < 3:  # 少于 3 部的小标签合并到末尾
            continue
        lines.append(f"## {tag}\n")
        lines.append(f"共 {len(ws)} 部。\n")
        lines.append("| 作品 | 媒介 | 年份 | L1 | 获量 |")
        lines.append("|---|---|---|---|---|")
        for w in sorted(ws, key=lambda x: (-x.acq, -x.year))[:50]:  # 每标签最多展示 50 部
            rel = w.path.relative_to(LIB_ROOT)
            lines.append(f"| [{w.work_name}]({rel}) | {w.media_type} | {w.year} | {w.theme_primary} | {w.acq} |")
        if len(ws) > 50:
            lines.append(f"\n*... 还有 {len(ws) - 50} 部*\n")
        lines.append("")

    fp = INDEXES_DIR / "按L2子题材.md"
    fp.write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✓ {fp.relative_to(LIB_ROOT)}")


def write_index_by_l3(works: list[Work]):
    """L3 视觉标签索引:在索引阶段做二次清洗"""
    # === 二次清洗规则 ===
    import re as _re

    def normalize_l3(tag: str) -> str:
        """把 LLM 自由生成的具体标签归并到大类"""
        # 1. "年份+地点" / "年份+风格" → "时代复古风"
        if _re.search(r"\d{2,4}\s*[年代世纪s]", tag):
            return "时代复古风"
        # 2. 城堡/古堡 合并
        if tag in ("城堡", "古堡", "城堡塔楼", "中世纪城堡"):
            return "古堡"
        # 3. 都市/都市夜景/都市繁华 区分保留(都是高频独立维度)
        # 4. 校园/操场/教室 区分保留
        return tag

    # 先做标签计数(原始)
    raw_counter = Counter()
    for w in works:
        for tag in w.visual_tags:
            raw_counter[tag] += 1

    # 应用规则,但只保留出现 ≥10 次(作品支撑充足)
    MIN_COUNT = 10
    valid_tags = {t for t, c in raw_counter.items() if c >= MIN_COUNT}

    # 加上规则归并后会出现的大类(总数可能 ≥10)
    normalized_counter = Counter()
    for tag, count in raw_counter.items():
        normalized_counter[normalize_l3(tag)] += count
    valid_normalized = {t for t, c in normalized_counter.items() if c >= MIN_COUNT}

    # 构建 tag → works 映射(用归并后的标签)
    by_l3 = defaultdict(list)
    for w in works:
        seen_tags = set()
        for tag in w.visual_tags:
            normalized = normalize_l3(tag)
            if normalized in valid_normalized and normalized not in seen_tags:
                by_l3[normalized].append(w)
                seen_tags.add(normalized)

    sorted_l3 = sorted(by_l3.items(), key=lambda x: -len(x[1]))

    # 统计
    total_raw = len(raw_counter)
    total_visible = len(by_l3)
    filtered_out = total_raw - total_visible

    lines = [
        f"# 按 L3 视觉标签索引(已清洗)\n",
        f"> 更新:{TODAY} | 总作品:{len(works)}",
        f"> 原始 L3 标签:{total_raw} 个 → 清洗后展示:{total_visible} 个(≥{MIN_COUNT} 部作品)",
        f"> 过滤:{filtered_out} 个长尾标签(每个 <{MIN_COUNT} 部);'年份+地点'类自动归到'时代复古风'",
        "",
        f"## L3 主标签概览(前 100 个)",
        "",
        "| L3 标签 | 作品数 |",
        "|---|---|",
    ]
    for tag, ws in sorted_l3[:100]:
        lines.append(f"| {tag} | {len(ws)} |")
    lines.append("")

    # 详细列表
    for tag, ws in sorted_l3:
        lines.append(f"## {tag}\n")
        lines.append(f"共 {len(ws)} 部。\n")
        lines.append("| 作品 | 媒介 | 年份 | L1 | 获量 |")
        lines.append("|---|---|---|---|---|")
        for w in sorted(ws, key=lambda x: (-x.acq, -x.year))[:30]:
            rel = w.path.relative_to(LIB_ROOT)
            lines.append(f"| [{w.work_name}]({rel}) | {w.media_type} | {w.year} | {w.theme_primary} | {w.acq} |")
        if len(ws) > 30:
            lines.append(f"\n*... 还有 {len(ws) - 30} 部*\n")
        lines.append("")

    fp = INDEXES_DIR / "按L3视觉.md"
    fp.write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✓ {fp.relative_to(LIB_ROOT)}")


def write_index_by_nt(works: list[Work]):
    """按 N + 主 T 组合分组(立项工具)"""
    by_nt = defaultdict(list)
    for w in works:
        t_main = w.t_can_carry[0] if w.t_can_carry else "-"
        key = (w.n_main, t_main)
        by_nt[key].append(w)

    sorted_nt = sorted(by_nt.items(), key=lambda x: -len(x[1]))

    lines = [
        f"# 按 N+T 组合索引\n",
        f"> 更新:{TODAY} | 总作品:{len(works)}",
        "",
        "**用途**:立项时按目标人群定位查参考作品。",
        "",
        "## N+T 组合概览",
        "",
        "| N | 主 T | 作品数 | 典型用户群 |",
        "|---|---|---|---|",
    ]
    nt_desc = {
        ("N-Comp", "T2"): "C04 变强确认人群(战神/逆袭/数值膨胀)",
        ("N-Comp", "T1"): "C01 强刺激泄压人群(割草/爽片)",
        ("N-Comp", "T5"): "C10 规则解码人群(智斗/解谜/构筑)",
        ("N-Comp", "T6"): "C11 秩序经营人群(经营建造/系统优化)",
        ("N-Rel",  "T3"): "C07 拟亲密人群(乙女/角色养成)",
        ("N-Rel",  "T4"): "C08/C09 群体归属(团魂/MMO/SLG)",
        ("N-Auto", "T1"): "自主放空人群(自由探索/治愈)",
        ("N-Auto", "T6"): "沙盒掌控人群(Minecraft/动森)",
    }
    for (n, t), ws in sorted_nt:
        desc = nt_desc.get((n, t), "-")
        lines.append(f"| {n} | {t} | {len(ws)} | {desc} |")
    lines.append("")

    for (n, t), ws in sorted_nt:
        if len(ws) < 5:
            continue
        lines.append(f"## {n} × {t}\n")
        lines.append(f"共 {len(ws)} 部。{nt_desc.get((n, t), '')}\n")
        lines.append("| 作品 | 媒介 | 年份 | L1 | L2 | 获量 |")
        lines.append("|---|---|---|---|---|---|")
        for w in sorted(ws, key=lambda x: (-x.acq, -x.year))[:50]:
            l2_str = " / ".join(w.theme_secondary[:3]) if w.theme_secondary else "-"
            rel = w.path.relative_to(LIB_ROOT)
            lines.append(f"| [{w.work_name}]({rel}) | {w.media_type} | {w.year} | {w.theme_primary} | {l2_str} | {w.acq} |")
        if len(ws) > 50:
            lines.append(f"\n*... 还有 {len(ws) - 50} 部*\n")
        lines.append("")

    fp = INDEXES_DIR / "按N+T组合.md"
    fp.write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✓ {fp.relative_to(LIB_ROOT)}")


def write_index_by_acq(works: list[Work]):
    lines = [
        f"# 按 acquisition_score 索引\n",
        f"> 更新:{TODAY} | 总作品:{len(works)}",
        "",
    ]
    for score in [5, 4, 3, 2, 1, 0]:
        ws = [w for w in works if w.acq == score]
        if not ws:
            continue
        lines.append(f"## 获量 {score}({len(ws)} 部)\n")
        lines.append("| 作品 | 媒介 | 年份 | L1 | 主 N |")
        lines.append("|---|---|---|---|---|")
        for w in sorted(ws, key=lambda x: (-x.year, x.work_name))[:200]:
            rel = w.path.relative_to(LIB_ROOT)
            lines.append(f"| [{w.work_name}]({rel}) | {w.media_type} | {w.year} | {w.theme_primary} | {w.n_main} |")
        if len(ws) > 200:
            lines.append(f"\n*... 还有 {len(ws) - 200} 部*\n")
        lines.append("")

    fp = INDEXES_DIR / "按获量.md"
    fp.write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✓ {fp.relative_to(LIB_ROOT)}")


def write_index_by_year(works: list[Work]):
    by_year = defaultdict(list)
    for w in works:
        by_year[w.year].append(w)

    lines = [
        f"# 按年代索引\n",
        f"> 更新:{TODAY} | 总作品:{len(works)}",
        "",
    ]
    for year in sorted(by_year.keys(), reverse=True):
        ws = by_year[year]
        lines.append(f"## {year}({len(ws)} 部)\n")
        lines.append("| 作品 | 媒介 | L1 | 获量 | 主 N |")
        lines.append("|---|---|---|---|---|")
        for w in sorted(ws, key=lambda x: -x.acq):
            rel = w.path.relative_to(LIB_ROOT)
            lines.append(f"| [{w.work_name}]({rel}) | {w.media_type} | {w.theme_primary} | {w.acq} | {w.n_main} |")
        lines.append("")

    fp = INDEXES_DIR / "按年代.md"
    fp.write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✓ {fp.relative_to(LIB_ROOT)}")


def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 索引生成开始")
    print(f"  样本目录: {SAMPLES_DIR}")
    print()

    works = scan_samples()
    print(f"[扫描] {len(works)} 部作品")
    print()

    INDEXES_DIR.mkdir(parents=True, exist_ok=True)

    print("[生成]")
    write_overview(works)
    write_index_by_l1(works)
    write_index_by_l2(works)
    write_index_by_l3(works)
    write_index_by_nt(works)
    write_index_by_acq(works)
    write_index_by_year(works)

    print()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 完成")


if __name__ == "__main__":
    main()
