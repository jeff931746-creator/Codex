#!/usr/bin/env python3
"""
样本字段重塑脚本(Step 3)

把当前 v1 样本的 yaml frontmatter 重塑为 v1.1 结构:
- 删除:roi_score / quadrant / mother_theme_id / secondary_motif_ids / motif_confidence
- 新增:theme_primary (占位 TBD) / theme_secondary ([]) / visual_tags ([])

保留所有现有字段,不动 LLM 已经判定的 n_main / n_others / t_can_carry / core_conflict / material_hooks / acquisition_score。

幂等:重跑安全,已经是 v1.1 结构的样本会跳过。

用法:
    cd /Users/mt/Documents/Codex
    python3 archive/tools/scripts/theme_lib_v1_reshape.py --dry-run   # 看会改多少
    python3 archive/tools/scripts/theme_lib_v1_reshape.py             # 真改
"""
from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/Users/mt/Documents/Codex")
SAMPLES_DIR = WORKSPACE / "archive/资料/历史题材库/样本/按媒介"
TODAY = datetime.now().strftime("%Y-%m-%d")

# 要删除的字段(整行删)
FIELDS_TO_DELETE = [
    "roi_score",
    "quadrant",
    "mother_theme_id",
    "secondary_motif_ids",
    "motif_confidence",
]

# 要删除的段标题注释
SECTION_HEADERS_TO_DELETE = [
    "# === 母题归并(占位)===",
    "# === 母题归并(占位) ===",
    "# === 评分(v0 已有)===",
    "# === 评分(v0 已有) ===",
    "# === 评分 ===",
]


def reshape_sample(text: str) -> tuple[str, bool]:
    """返回 (新内容, 是否改动)"""
    # 解析 frontmatter
    m = re.match(r"^(---\n)(.*?)(\n---)(.*)$", text, re.DOTALL)
    if not m:
        return text, False

    head, fm, tail_dash, body = m.group(1), m.group(2), m.group(3), m.group(4)

    # 如果已经有 theme_primary 字段就跳过(幂等)
    if "theme_primary:" in fm:
        return text, False

    new_lines = []
    skip_next_section_header = False

    for line in fm.splitlines():
        stripped = line.strip()

        # 1. 删除字段行
        field_match = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*:", stripped)
        if field_match and field_match.group(1) in FIELDS_TO_DELETE:
            continue

        # 2. 删除特定段标题(如果该段下面所有字段都被删了)
        if stripped in SECTION_HEADERS_TO_DELETE:
            # "评分" 段下还有 acquisition_score 没删,所以这个 header 要保留改名;
            # "母题归并" 段全部删,header 也删
            if "母题归并" in stripped:
                continue

        new_lines.append(line)

    new_fm = "\n".join(new_lines)

    # 在 core_conflict 行之后插入三层标签新段
    insert_after_pattern = r"(core_conflict:.*?\n)"
    insertion = """
# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: TBD                # L1 主题大类(单选,30 个枚举,见 TAGS.md §二)
theme_secondary: []               # L2 子题材(多选 2-5,见 TAGS.md §三)
visual_tags: []                   # L3 视觉标签(多选 2-5,见 TAGS.md §四)
"""

    if re.search(insert_after_pattern, new_fm):
        new_fm = re.sub(insert_after_pattern, r"\1" + insertion, new_fm, count=1)
    else:
        # core_conflict 不在?把 insertion 放在末尾
        new_fm = new_fm + insertion

    # 把 evidence_level 从 B 降回 C(因为三层标签是 TBD,等下一轮 LLM 跑后才回 B)
    new_fm = re.sub(r"^(evidence_level:)\s*B\b", r"\1 C", new_fm, flags=re.MULTILINE)

    # 修改 source_run_id 表示进了 reshape 阶段
    new_fm = re.sub(
        r"^(source_run_id:)\s*.*$",
        f"\\1 {TODAY}-reshape",
        new_fm,
        flags=re.MULTILINE,
    )

    new_text = head + new_fm + tail_dash + body
    return new_text, True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="只统计,不写文件")
    args = parser.parse_args()

    print(f"[{datetime.now().strftime('%H:%M:%S')}] 样本字段重塑开始")
    print(f"  目录: {SAMPLES_DIR}")
    print(f"  dry-run: {args.dry_run}")
    print()

    total = 0
    changed = 0
    skipped = 0

    for media_dir in sorted(SAMPLES_DIR.iterdir()):
        if not media_dir.is_dir() or not media_dir.name[0].isdigit():
            continue
        media_changed = 0
        media_total = 0
        for fp in sorted(media_dir.glob("*.md")):
            total += 1
            media_total += 1
            text = fp.read_text(encoding="utf-8")
            new_text, did_change = reshape_sample(text)
            if did_change:
                if not args.dry_run:
                    fp.write_text(new_text, encoding="utf-8")
                changed += 1
                media_changed += 1
            else:
                skipped += 1
        print(f"  [{media_dir.name}] {media_total} 部,改 {media_changed} 部")

    print()
    print(f"=== 重塑完成 ===")
    print(f"总样本: {total}")
    print(f"改动:   {changed}")
    print(f"跳过:   {skipped}(已经是 v1.1 结构)")


if __name__ == "__main__":
    main()
