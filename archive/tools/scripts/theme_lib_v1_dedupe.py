#!/usr/bin/env python3
"""
样本去重合并脚本(Step 7)

合并同 IP 的不同版本变体到单一主作品。

合并范围:
  同媒介 + 同归一化主名 → 合并为 1 部

归一化规则:
  1. 去除繁简体差异(繁→简)
  2. 去除书名号"》"、引号
  3. 去除"(2024,..)"等说明性括号
  4. 去除后缀"最终季/Part X/完结篇/后篇/前篇/完全版/重制版/剧场版/总集篇/OVA/漫画"
  5. 去除"第 X 季/卷/部/章"(虽然迁移时已清,兜底)

字段合并策略:
  - work_name:最简洁的主名(变体中最短的、无后缀的)
  - year_first:最早;year_range[1]:最晚
  - acquisition_score:max(代表系列峰值)
  - n_main / theme_primary:最频繁出现
  - n_others / theme_secondary / visual_tags / material_hooks:并集(去重,取前 5)
  - existing_games / risk_notes:并集
  - 新增 merged_count(合并几部)和 merged_variants(原 work_name 列表)

跨媒介:不合并(媒介本身是分类轴)
work_id:取被合并集合中最早分配的 ID

用法:
    cd /Users/mt/Documents/Codex
    python3 archive/tools/scripts/theme_lib_v1_dedupe.py --dry-run    # 只看会合并多少
    python3 archive/tools/scripts/theme_lib_v1_dedupe.py              # 真合并
    python3 archive/tools/scripts/theme_lib_v1_dedupe.py --preview 10  # 看 10 个合并样例

合并前会自动备份到 _去重前备份/
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/Users/mt/Documents/Codex")
LIB_ROOT = WORKSPACE / "archive/资料/历史题材库"
SAMPLES_DIR = LIB_ROOT / "样本/按媒介"
BACKUP_DIR = LIB_ROOT.parent.parent / "tools/scripts/历史题材库_数据/_合并前备份"
TODAY = datetime.now().strftime("%Y-%m-%d")


# ========== 归一化 ==========
# 后缀清理顺序很重要,从长到短
# ⚠️ 不清"沙丘 2 / 速度与激情 5"这种续作数字 — 它们是独立电影
TRAILING_PATTERNS = [
    r"》?\s*[（(]\s*\d{4}\s*[,，][^)]*[)）]",        # "》(2024,欧美,xxx)"
    r"》?\s*[（(]\s*\d{4}\s*[)）]",                  # "》(2024)"
    r"》?\s*[（(]\s*\d{4}\s*版\s*[)）]",              # "(2009版)"
    r"》?\s*[（(]\s*\d+\s*版\s*[)）]",                # "(美版)"
    r"》?\s*[（(]\s*[^)）\d]+\s*[)）]",                # "(美版)/(欧版)/(剧场版)" — 但不含纯数字
    r"\s*[（(][^)）]*$",                              # 未闭合括号到末尾
    r"\s*第[一二三四五六七八九十百千零]+[季卷部章节集]\s*(?:Part\s*\d+|后篇|前篇|完结篇)?",  # 中文数字第X季
    r"\s*第\d+[季卷部章节集]\s*(?:Part\s*\d+|后篇|前篇|完结篇)?",                          # 阿拉伯数字第X季
    r"\s*最终季\s*(?:Part\s*\d+|后篇|前篇|完结篇)?",                  # 最终季 Part X
    r"\s*完结篇\s*(?:后篇|前篇)?",                                    # 完结篇 后篇
    r"\s*(?:完全版|前传|后传|续传|新剧场版|剧场版|总集篇|OVA|0[Vv][Aa]|重制版|MOVIE\s*\d*|漫画|英文版|原版|动画版|游戏版|完整版|未删减版|导演剪辑版)",
    r"\s*Part\s*\d+\s*(?:后篇|前篇|完结篇)?",                         # 末尾的 Part X(同一作品播出分批)
    r"\s*(?:后篇|前篇)\s*$",
    r"》\s*$",                                                        # 末尾"》"
    r"[:：]\s*$",                                                     # 末尾":"
]

TRADITIONAL_TO_SIMPLIFIED = {
    "進": "进", "擊": "击", "傳": "传", "戰": "战", "電": "电",
    "視": "视", "為": "为", "從": "从", "後": "后", "詠": "咏",
    "響": "响", "團": "团", "華": "华", "麗": "丽", "勝": "胜",
    "態": "态", "權": "权", "聲": "声", "雙": "双", "圖": "图",
    "繪": "绘", "覺": "觉", "夢": "梦", "麻": "麻", "節": "节",
    "醒": "醒", "謀": "谋", "謹": "谨", "詩": "诗", "識": "识",
    "鐵": "铁", "錄": "录", "鬪": "斗", "鬥": "斗", "陳": "陈",
    "陰": "阴", "陽": "阳", "雲": "云",
}

def t2s(s: str) -> str:
    return "".join(TRADITIONAL_TO_SIMPLIFIED.get(c, c) for c in s)


def normalize_name(name: str) -> str:
    """归一化作品名,用于去重 key"""
    n = name.strip()
    # 去引号
    n = n.strip('"').strip("'").strip("《").strip("》")
    # 繁→简
    n = t2s(n)
    # 反复应用后缀清理(因为有嵌套)
    for _ in range(3):
        for pat in TRAILING_PATTERNS:
            n = re.sub(pat, "", n)
        n = n.strip().rstrip(":").rstrip(":").rstrip("：").strip()
    return n


# ========== yaml 解析 ==========
FM_RE = re.compile(r"^(---\n)(.*?)(\n---)(.*)$", re.DOTALL)


def parse_fm(text: str) -> tuple[str, dict, str, str]:
    m = FM_RE.match(text)
    if not m:
        return "", {}, "", text
    head = m.group(1)
    fm_text = m.group(2)
    tail = m.group(3)
    body = m.group(4) or ""
    fields = {}
    for line in fm_text.splitlines():
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue
        m2 = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.*)$", line)
        if m2:
            value = m2.group(2)
            value = re.sub(r"\s+#.*$", "", value).strip()
            fields[m2.group(1)] = value
    return head, fields, tail, body


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
    cur, in_q, qc = "", False, ""
    for ch in inner:
        if ch in ('"', "'"):
            if not in_q:
                in_q, qc = True, ch
            elif ch == qc:
                in_q = False
        elif ch == "," and not in_q:
            parts.append(cur.strip().strip('"').strip("'"))
            cur = ""
            continue
        cur += ch
    if cur.strip():
        parts.append(cur.strip().strip('"').strip("'"))
    return parts


def strip_quote(s: str) -> str:
    s = s.strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s


def yaml_quote(s: str) -> str:
    if not s:
        return '""'
    if any(c in s for c in [":", "#", '"', "'", "\n", "[", "]", "{", "}", "&", "*"]):
        return '"' + s.replace('"', '\\"') + '"'
    return s


def yaml_list(items: list[str]) -> str:
    if not items:
        return "[]"
    return "[" + ", ".join(yaml_quote(it) for it in items) + "]"


# ========== 合并逻辑 ==========
def merge_group(samples: list[tuple[Path, dict, str, str, str]]) -> dict:
    """samples: [(path, fields, head, fm_text, body), ...]  按 work_id 排序

    合并字段:
    - work_name: 选最简洁(归一化后等于自身、长度最短)
    - year_first: min;year_range[1]: max
    - acquisition_score: max
    - n_main / theme_primary / rel_object: 最频繁
    - 数组字段: 并集去重
    - merged_count / merged_variants 新增
    """
    # 选 work_name:归一化后等于自身的优先;长度短的优先
    name_to_path = []
    for path, fields, _, _, _ in samples:
        wn = strip_quote(fields.get("work_name", ""))
        norm = normalize_name(wn)
        priority = (0 if wn == norm else 1, len(wn))  # 主名优先,然后短名优先
        name_to_path.append((priority, wn, fields))
    name_to_path.sort()
    primary_name = name_to_path[0][1]
    primary_fields = name_to_path[0][2]

    # 取 work_id: 第一个分配的(最小编号)
    all_work_ids = sorted([f.get("work_id", "") for _, f, _, _, _ in samples])
    new_work_id = all_work_ids[0]

    # 年份
    years = []
    year_ends = []
    for _, f, _, _, _ in samples:
        try:
            years.append(int(f.get("year_first", "0") or 0))
        except ValueError:
            pass
        yr = parse_list(f.get("year_range", "[]"))
        if len(yr) >= 2:
            try:
                year_ends.append(int(yr[1]))
            except ValueError:
                pass
    year_first = min(years) if years else 0
    year_end = max(year_ends + years) if (year_ends or years) else year_first

    # 获量:取 max
    acqs = []
    for _, f, _, _, _ in samples:
        try:
            v = int(f.get("acquisition_score", "0") or 0)
            if v > 0:
                acqs.append(v)
        except ValueError:
            pass
    new_acq = max(acqs) if acqs else 0

    # n_main / theme_primary / rel_object:最频繁
    def most_common(field_name: str) -> str:
        c = Counter()
        for _, f, _, _, _ in samples:
            v = f.get(field_name, "")
            if v and v != "TBD":
                c[v] += 1
        return c.most_common(1)[0][0] if c else primary_fields.get(field_name, "")

    new_n = most_common("n_main")
    new_l1 = most_common("theme_primary")
    new_rel = most_common("rel_object") or "null"

    # 数组字段:并集去重,取前 5
    def union_list(field_name: str, max_n: int = 5) -> list[str]:
        seen = set()
        result = []
        for _, f, _, _, _ in samples:
            for item in parse_list(f.get(field_name, "[]")):
                if item not in seen:
                    seen.add(item)
                    result.append(item)
        return result[:max_n]

    new_n_others = union_list("n_others", 2)
    new_t = union_list("t_can_carry", 3)
    new_l2 = union_list("theme_secondary", 5)
    new_l3 = union_list("visual_tags", 5)
    new_hooks = union_list("material_hooks", 5)
    new_games = union_list("existing_games", 10)
    new_risks = union_list("risk_notes", 5)

    # 三要素:取最长的
    def longest_field(field_name: str) -> str:
        best = ""
        for _, f, _, _, _ in samples:
            v = strip_quote(f.get(field_name, ""))
            if len(v) > len(best):
                best = v
        return best

    new_env = longest_field("environment")
    new_cp = longest_field("cultural_paradigm")
    new_nc = longest_field("narrative_core")
    new_cc = longest_field("core_conflict")

    # 变体清单
    variants = [strip_quote(f.get("work_name", "")) for _, f, _, _, _ in samples]
    variants = [v for v in variants if v != primary_name]

    media_type = primary_fields.get("media_type", "?")

    return {
        "work_id": new_work_id,
        "work_name": primary_name,
        "media_type": media_type,
        "year_first": year_first,
        "year_end": year_end,
        "environment": new_env,
        "cultural_paradigm": new_cp,
        "narrative_core": new_nc,
        "core_conflict": new_cc,
        "n_main": new_n,
        "n_others": new_n_others,
        "rel_object": new_rel,
        "t_can_carry": new_t,
        "theme_primary": new_l1,
        "theme_secondary": new_l2,
        "visual_tags": new_l3,
        "acquisition_score": new_acq,
        "material_hooks": new_hooks,
        "existing_games": new_games,
        "risk_notes": new_risks,
        "merged_count": len(samples),
        "merged_variants": variants,
        "_orig_paths": [p for p, _, _, _, _ in samples],
    }


def render_merged_sample(merged: dict) -> str:
    """渲染合并后的样本 markdown"""
    return f"""---
# === 身份 ===
work_id: {merged['work_id']}
work_name: {yaml_quote(merged['work_name'])}
work_name_alt: []
media_type: {merged['media_type']}
year_first: {merged['year_first']}
year_range: [{merged['year_first']}, {merged['year_end']}]
season_count: null

# === 三要素 ===
environment: {yaml_quote(merged['environment'])}
cultural_paradigm: {yaml_quote(merged['cultural_paradigm'])}
narrative_core: {yaml_quote(merged['narrative_core'])}

# === SDT 心理需求 ===
n_main: {merged['n_main']}
n_others: {yaml_list(merged['n_others'])}
rel_object: {merged['rel_object']}
t_can_carry: {yaml_list(merged['t_can_carry'])}
core_emotion_note: ""
core_conflict: {yaml_quote(merged['core_conflict'])}

# === 三层标签(主检索路径,见 TAGS.md)===
theme_primary: {merged['theme_primary']}
theme_secondary: {yaml_list(merged['theme_secondary'])}
visual_tags: {yaml_list(merged['visual_tags'])}

# === 评分 ===
acquisition_score: {merged['acquisition_score']}

# === 素材与玩法 ===
material_hooks: {yaml_list(merged['material_hooks'])}
existing_games: {yaml_list(merged['existing_games'])}
recommended_playstyles: []
risk_notes: {yaml_list(merged['risk_notes'])}

# === 元数据 ===
source: SiliconFlow_DeepSeek_Flash + v0-migrate + tags + dedupe
source_run_id: {TODAY}-dedupe
evidence_level: B
review_status: auto
last_updated: {TODAY}
merged_count: {merged['merged_count']}
merged_variants: {yaml_list(merged['merged_variants'])}
---
"""


# ========== 主流程 ==========
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--preview", type=int, default=0, help="预览前 N 个合并组")
    args = parser.parse_args()

    print(f"[{datetime.now().strftime('%H:%M:%S')}] 样本合并去重开始")

    # 扫描所有样本
    samples = []
    for media_dir in sorted(SAMPLES_DIR.iterdir()):
        if not media_dir.is_dir() or not media_dir.name[0].isdigit():
            continue
        for fp in sorted(media_dir.glob("*.md")):
            text = fp.read_text(encoding="utf-8")
            head, fields, tail, body = parse_fm(text)
            if not fields:
                continue
            samples.append((fp, fields, head, "", body))

    print(f"  扫描到样本: {len(samples)}")

    # 分组:(归一化主名, 媒介)→ 变体列表
    groups: dict[tuple[str, str], list] = defaultdict(list)
    for fp, fields, head, _, body in samples:
        wn = strip_quote(fields.get("work_name", ""))
        media = fields.get("media_type", "?")
        norm = normalize_name(wn)
        if norm and media:
            groups[(norm, media)].append((fp, fields, head, "", body))

    # 找重复组
    dup_groups = {k: v for k, v in groups.items() if len(v) >= 2}
    single_groups = {k: v for k, v in groups.items() if len(v) == 1}

    total_before = len(samples)
    total_after = len(groups)
    reduction = total_before - total_after

    print(f"\n=== 合并预览 ===")
    print(f"  原始样本:       {total_before}")
    print(f"  归一化后独立组: {total_after}")
    print(f"  重复合并组:     {len(dup_groups)}")
    print(f"  净减少样本:     {reduction}({reduction/total_before*100:.1f}%)")

    if args.preview > 0:
        print(f"\n=== 前 {args.preview} 个重复合并组 ===")
        sorted_dups = sorted(dup_groups.items(), key=lambda x: -len(x[1]))
        for (norm, media), group in sorted_dups[: args.preview]:
            print(f"\n  [{media}] '{norm}' ({len(group)} 个变体):")
            for _, f, _, _, _ in group:
                print(f"    - {strip_quote(f.get('work_name', ''))}")

    if args.dry_run:
        print("\n[--dry-run] 不写文件")
        return

    # 备份
    print(f"\n[备份] 复制 样本/按媒介/ → {BACKUP_DIR}")
    if BACKUP_DIR.exists():
        shutil.rmtree(BACKUP_DIR)
    shutil.copytree(SAMPLES_DIR, BACKUP_DIR)

    # 执行合并
    print(f"\n[合并 + 写入]")
    written = 0
    deleted = 0
    for (norm, media), group in groups.items():
        if len(group) == 1:
            continue  # 单条不需合并
        merged = merge_group(group)
        primary_path = None
        for path, fields, _, _, _ in group:
            if fields.get("work_id") == merged["work_id"]:
                primary_path = path
                break
        if primary_path is None:
            primary_path = group[0][0]
        new_content = render_merged_sample(merged)
        primary_path.write_text(new_content, encoding="utf-8")
        written += 1
        for path, _, _, _, _ in group:
            if path != primary_path:
                path.unlink()
                deleted += 1

    print(f"  合并后重写:   {written} 部")
    print(f"  删除的变体:   {deleted} 部")

    # 终态扫描
    final_count = sum(1 for d in SAMPLES_DIR.iterdir() if d.is_dir() and d.name[0].isdigit()
                      for _ in d.glob("*.md"))
    print(f"\n[终态] 最终样本数: {final_count}")
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 完成")


if __name__ == "__main__":
    main()
