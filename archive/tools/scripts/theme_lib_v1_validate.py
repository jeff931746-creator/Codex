#!/usr/bin/env python3
"""
历史题材库 v1 样本校验脚本(Step 2)

实现 SCHEMA §5 的 12 项质量门禁,扫描 archive/资料/历史题材库/样本/按媒介/ 全部样本。

输出:
- 控制台:汇总统计 + 失败明细
- 已知问题/FAILURES.md:失败清单(供 04_失败复检 提示词使用)
- _logs/validate_{date}.log:详细日志(每个失败样本一行)

用法:
    cd /Users/mt/Documents/Codex
    python3 archive/tools/scripts/theme_lib_v1_validate.py
    python3 archive/tools/scripts/theme_lib_v1_validate.py --media LIT  # 只校验某媒介
    python3 archive/tools/scripts/theme_lib_v1_validate.py --strict      # TBD 也算失败(LLM 跑后用这个)
"""
from __future__ import annotations

import argparse
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# ========== 路径配置 ==========
WORKSPACE = Path("/Users/mt/Documents/Codex")
LIB_ROOT = WORKSPACE / "archive/资料/历史题材库"
SAMPLES_DIR = LIB_ROOT / "样本/按媒介"
MOTIF_DIR = LIB_ROOT / "母题归并"
FAILURES_FILE = LIB_ROOT / "已知问题/FAILURES.md"
LOGS_DIR = LIB_ROOT.parent.parent / "tools/scripts/历史题材库_数据/_logs"
TODAY = datetime.now().strftime("%Y-%m-%d")

# ========== 枚举值 ==========
MEDIA_TYPES = {"ANI", "TVW", "MVW", "MVK", "LIT", "TVK", "TVC"}
N_VALUES = {"N-Comp", "N-Auto", "N-Rel", "TBD"}  # TBD 是迁移阶段允许的占位
REL_OBJECTS = {"virtual", "real", "mixed", "null", "None"}
T_VALUES = {"T1", "T2", "T3", "T4", "T5", "T6", "T7-candidate"}
MOTIF_CONFIDENCE = {"high", "medium", "low"}
EVIDENCE_LEVELS = {"S", "A", "B", "C", "D"}
REVIEW_STATUSES = {"auto", "human-reviewed", "disputed"}

# 字段长度上限(SCHEMA §5.8)
MAX_LEN = {
    "environment": 45,
    "cultural_paradigm": 45,
    "narrative_core": 45,
    "core_conflict": 45,
}


def load_motif_ids() -> set[str]:
    """扫描 母题归并/ 下所有 THM-*.md 文件,提取合法 mother_theme_id"""
    motif_ids = {"THM-UNK-001"}  # 占位母题始终合法
    if MOTIF_DIR.exists():
        for f in MOTIF_DIR.glob("THM-*.md"):
            # 文件名格式:THM-{category}-{NNN}_{name}.md
            m = re.match(r"(THM-[A-Z]+-\d{3})", f.name)
            if m:
                motif_ids.add(m.group(1))
    return motif_ids


def parse_yaml_simple(text: str) -> dict | None:
    """简单 yaml frontmatter 解析,不依赖外部库"""
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    yaml_block = parts[1]

    result = {}
    for line in yaml_block.splitlines():
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue
        # 顶级 key: value
        m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.*)$", line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        result[key] = value
    return result


def parse_list_value(v: str) -> list[str]:
    """解析 yaml 列表值: [a, b, c] 或 [\"a\", \"b\"]"""
    if not v or v in ("[]", ""):
        return []
    v = v.strip()
    if not (v.startswith("[") and v.endswith("]")):
        return []
    inner = v[1:-1].strip()
    if not inner:
        return []
    # 简单切分
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


def strip_quote(v: str) -> str:
    v = v.strip()
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]
    return v


class FailureRecord:
    def __init__(self, sample_path: Path, work_id: str, gates: list[tuple[int, str]]):
        self.sample_path = sample_path
        self.work_id = work_id
        self.gates = gates  # [(gate_no, message), ...]


def validate_sample(sample_path: Path, motif_ids: set[str], strict: bool) -> list[tuple[int, str]]:
    """返回失败的门禁列表;空列表 = 全部通过"""
    failures: list[tuple[int, str]] = []

    text = sample_path.read_text(encoding="utf-8")
    data = parse_yaml_simple(text)
    if data is None:
        return [(1, "YAML 解析失败:无 frontmatter 或格式错")]

    # === 门禁 1: YAML 合法性 ===
    required_fields = [
        "work_id", "work_name", "media_type", "year_first",
        "environment", "cultural_paradigm", "narrative_core", "core_conflict",
        "n_main", "n_others", "rel_object", "t_can_carry",
        "theme_primary", "theme_secondary", "visual_tags",
        "acquisition_score",
        "material_hooks", "evidence_level", "review_status", "last_updated",
    ]
    missing = [f for f in required_fields if f not in data]
    if missing:
        failures.append((1, f"必填字段缺失: {','.join(missing)}"))
        return failures  # 字段都不全,后面校验无意义

    # === 门禁 2: 枚举值合法性 ===
    if data["media_type"] not in MEDIA_TYPES:
        failures.append((2, f"media_type 非法: {data['media_type']}"))
    if data["n_main"] not in N_VALUES:
        failures.append((2, f"n_main 非法: {data['n_main']}"))
    elif data["n_main"] == "TBD" and strict:
        failures.append((2, "n_main 仍为 TBD,LLM 阶段未完成"))

    rel_obj = strip_quote(data["rel_object"])
    if rel_obj not in REL_OBJECTS:
        failures.append((2, f"rel_object 非法: {rel_obj}"))

    for t in parse_list_value(data["t_can_carry"]):
        if t and t not in T_VALUES:
            failures.append((2, f"t_can_carry 含非法 T 值: {t}"))
            break

    for n in parse_list_value(data["n_others"]):
        if n and n not in N_VALUES:
            failures.append((2, f"n_others 含非法 N 值: {n}"))
            break

    if data["evidence_level"] not in EVIDENCE_LEVELS:
        failures.append((2, f"evidence_level 非法: {data['evidence_level']}"))
    if data["review_status"] not in REVIEW_STATUSES:
        failures.append((2, f"review_status 非法: {data['review_status']}"))

    # === 门禁 3: rel_object 一致性 ===
    n_others_list = parse_list_value(data["n_others"])
    has_nrel = data["n_main"] == "N-Rel" or "N-Rel" in n_others_list
    if has_nrel and rel_obj in ("null", "None"):
        failures.append((3, "n 含 N-Rel 但 rel_object 是 null"))
    if not has_nrel and rel_obj not in ("null", "None"):
        failures.append((3, f"n 不含 N-Rel 但 rel_object={rel_obj}(应为 null)"))

    # === 门禁 4: 评分范围 ===
    # 非严格模式:0 表示 v0 缺数据,LLM 阶段会补;严格模式:必须 1-5
    try:
        acq = int(data["acquisition_score"])
        if strict and not (1 <= acq <= 5):
            failures.append((4, f"acquisition_score 超出 1-5: {acq}"))
        elif not strict and not (0 <= acq <= 5):
            failures.append((4, f"acquisition_score 超出 0-5: {acq}"))
    except ValueError:
        failures.append((4, f"acquisition_score 非整数: {data['acquisition_score']}"))

    # === 门禁 5/6: 母题引用合法性(已删) — v1.1 不再使用母题 ===
    # === 门禁 5/6: quadrant + 母题引用 — v1.1 已删除 ===

    # === 门禁 7: 去重检查(在外层做,这里不查)===

    # === 门禁 8: 字段长度限制 ===
    for fld, max_len in MAX_LEN.items():
        v = strip_quote(data.get(fld, ""))
        if v in ("TBD", "") and not strict:
            continue
        if len(v) > max_len:
            failures.append((8, f"{fld} 超长 {len(v)} > {max_len}"))

    for hook in parse_list_value(data["material_hooks"]):
        if len(hook) > 10:
            failures.append((8, f"material_hooks 元素超长: {hook[:15]}..."))
            break

    for risk in parse_list_value(data.get("risk_notes", "[]")):
        if len(risk) > 15:
            failures.append((8, f"risk_notes 元素超长: {risk[:20]}..."))
            break

    # === 门禁 9: material_hooks 数组长度 3-5 ===
    hooks = parse_list_value(data["material_hooks"])
    if strict:
        if not (3 <= len(hooks) <= 5):
            failures.append((9, f"material_hooks 数组长度 {len(hooks)},应为 3-5"))
    else:
        # 迁移阶段允许 0-5(v0 部分作品情绪钩子可能少于 3)
        if len(hooks) > 5:
            failures.append((9, f"material_hooks 数组长度 {len(hooks)} > 5"))

    # === 门禁 10: t_can_carry 数组长度 0-2 ===
    ts = parse_list_value(data["t_can_carry"])
    if len(ts) > 2:
        failures.append((10, f"t_can_carry 数组长度 {len(ts)} > 2"))

    # === 门禁 11: n_others 数组长度 0-2 ===
    nos = parse_list_value(data["n_others"])
    if len(nos) > 2:
        failures.append((11, f"n_others 数组长度 {len(nos)} > 2"))

    return failures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--media", help="只校验某媒介(ANI/TVW/MVW/MVK/LIT)")
    parser.add_argument("--strict", action="store_true",
                        help="严格模式:TBD 占位算失败、material_hooks 必须 3-5(LLM 跑后使用)")
    args = parser.parse_args()

    print(f"[{datetime.now().strftime('%H:%M:%S')}] v1 样本校验开始")
    print(f"  目录: {SAMPLES_DIR}")
    print(f"  严格模式: {args.strict}")
    print()

    motif_ids = load_motif_ids()
    print(f"[母题列表] 共 {len(motif_ids)} 个合法 mother_theme_id: {sorted(motif_ids)[:5]}...")
    print()

    # 扫描所有样本
    sample_files = []
    for media_dir in sorted(SAMPLES_DIR.iterdir()):
        if not media_dir.is_dir():
            continue
        if args.media and args.media not in media_dir.name:
            continue
        sample_files.extend(sorted(media_dir.glob("*.md")))

    print(f"[扫描] 找到 {len(sample_files)} 个样本文件")
    print()

    # 校验
    all_failures: list[FailureRecord] = []
    gate_counts: dict[int, int] = defaultdict(int)
    work_id_set = set()
    duplicate_work_ids = []

    # 去重检查:work_name + media_type 组合
    name_media_keys: set[tuple[str, str]] = set()
    duplicate_keys = []

    for fp in sample_files:
        text = fp.read_text(encoding="utf-8")
        data = parse_yaml_simple(text)
        work_id = data.get("work_id", "?") if data else "?"

        # 去重检查
        if data:
            work_name = strip_quote(data.get("work_name", ""))
            media_type = data.get("media_type", "")
            key = (work_name, media_type)
            if key in name_media_keys:
                duplicate_keys.append(f"{key} in {fp.name}")
            name_media_keys.add(key)
            if work_id in work_id_set:
                duplicate_work_ids.append(f"{work_id} in {fp.name}")
            work_id_set.add(work_id)

        failures = validate_sample(fp, motif_ids, args.strict)
        if failures:
            all_failures.append(FailureRecord(fp, work_id, failures))
            for gate_no, _ in failures:
                gate_counts[gate_no] += 1

    # === 输出报告 ===
    total = len(sample_files)
    failed = len(all_failures)
    passed = total - failed
    pass_rate = (passed / total * 100) if total else 0

    print("=" * 60)
    print(f"=== 校验结果 ===")
    print(f"总样本: {total}")
    print(f"通过:  {passed} ({pass_rate:.1f}%)")
    print(f"失败:  {failed}")
    print(f"门禁 7 去重检查:  {'通过' if not duplicate_keys else f'失败 {len(duplicate_keys)} 处'}")
    print()

    if gate_counts:
        print("=== 失败门禁分布 ===")
        gate_names = {
            1: "YAML 合法性",
            2: "枚举值合法性",
            3: "rel_object 一致性",
            4: "评分范围",
            6: "母题引用合法性",
            8: "字段长度",
            9: "material_hooks 长度",
            10: "t_can_carry 长度",
            11: "n_others 长度",
        }
        for gate_no in sorted(gate_counts.keys()):
            name = gate_names.get(gate_no, f"门禁{gate_no}")
            print(f"  门禁 {gate_no} {name}: {gate_counts[gate_no]} 次")
        print()

    # 失败明细(前 20 条)
    if all_failures:
        print("=== 失败明细 (前 20 条)===")
        for rec in all_failures[:20]:
            rel = rec.sample_path.relative_to(LIB_ROOT)
            print(f"  [{rec.work_id}] {rel}")
            for gate_no, msg in rec.gates:
                print(f"    门禁 {gate_no}: {msg}")
        if len(all_failures) > 20:
            print(f"  ... 还有 {len(all_failures) - 20} 条失败,详见 FAILURES.md")

    # 写 FAILURES.md
    if all_failures:
        FAILURES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with FAILURES_FILE.open("w", encoding="utf-8") as f:
            f.write(f"# 校验失败记录\n\n")
            f.write(f"> 生成时间: {datetime.now()}\n")
            f.write(f"> 总样本 {total},失败 {failed},通过率 {pass_rate:.1f}%\n")
            f.write(f"> 严格模式: {args.strict}\n\n")
            f.write("## 失败清单\n\n")
            for rec in all_failures:
                rel = rec.sample_path.relative_to(LIB_ROOT)
                f.write(f"### {rec.work_id} `{rel}`\n\n")
                for gate_no, msg in rec.gates:
                    f.write(f"- 门禁 {gate_no}: {msg}\n")
                f.write("\n")
        print(f"\n[写] FAILURES.md ({failed} 条) → {FAILURES_FILE}")

    # 写详细日志
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / f"validate_{TODAY}.log"
    with log_path.open("w", encoding="utf-8") as f:
        f.write(f"validate run: {datetime.now()}\n")
        f.write(f"total={total} passed={passed} failed={failed} pass_rate={pass_rate:.1f}%\n")
        for rec in all_failures:
            for gate_no, msg in rec.gates:
                f.write(f"{rec.work_id}\t{rec.sample_path.name}\tgate{gate_no}\t{msg}\n")
    print(f"[写] 详细日志 → {log_path}")

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 校验完成")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
