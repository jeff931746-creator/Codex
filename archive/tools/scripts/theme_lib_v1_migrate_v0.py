#!/usr/bin/env python3
"""
历史题材库 v0 → v1 迁移脚本(Step 1)

输入:archive/资料/历史题材库/按分类/{01-04}_*_汇总.md 4 个 markdown 表格
输出:archive/资料/历史题材库/样本/按媒介/{编号}_{媒介}/{作品名}.md 单作品 yaml frontmatter 文件

特性:
- 零 LLM 调用,纯本地解析
- 同 work_name + media_type 联合去重,year_first 取最早
- v0 已有字段(environment/cultural_paradigm/narrative_core/获量/ROI/已有游戏/风险)直接翻译
- v1 新字段(n_main/n_others/rel_object/t_can_carry/core_conflict/material_hooks/mother_theme_id)填占位 TBD/[]/null,等 LLM 阶段补
- 输出统计:总条数、去重数、各媒介分布、长度超标条数

用法:
    cd /Users/mt/Documents/Codex
    python3 archive/tools/scripts/theme_lib_v1_migrate_v0.py
    python3 archive/tools/scripts/theme_lib_v1_migrate_v0.py --dry-run   # 只统计不写文件
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# ========== 路径配置 ==========
WORKSPACE = Path("/Users/mt/Documents/Codex")
LIB_ROOT = WORKSPACE / "archive/资料/历史题材库"
V0_CATEGORY_DIR = LIB_ROOT / "按分类"
V1_SAMPLES_DIR = LIB_ROOT / "样本/按媒介"
TODAY = datetime.now().strftime("%Y-%m-%d")

# v0 汇总表 → v1 媒介编号映射
V0_FILE_TO_MEDIA = {
    "01_日本动漫_汇总.md": ("ANI", "01_日本动漫"),
    "02_欧美影视_汇总.md": ("TVW", "02_欧美影视"),  # v0 把电视+电影合并;按主体归到 TVW
    "03_韩国电影_汇总.md": ("MVK", "03_韩国电影"),
    "04_文学作品_汇总.md": ("LIT", "05_海外文学"),
}

# 字段长度上限(SCHEMA §5.8 已放宽到 45)
MAX_LEN = {
    "environment": 45,
    "cultural_paradigm": 45,
    "narrative_core": 45,
    "core_conflict": 45,
}


@dataclass
class V0Row:
    """v0 markdown 表格中的一行原始数据"""
    work_name_raw: str
    year: int
    environment: str
    cultural_paradigm: str
    narrative_core: str
    emotion_hook: str  # v0 的"情绪钩子",作为 material_hooks 的种子(打 evidence_level C)
    existing_games: str
    acquisition: int  # 1-5
    roi: int  # 1-5
    risks: str

    @property
    def work_name(self) -> str:
        """清洗作品名:去书名号、去"第 X 季"、特殊字符替换"""
        name = self.work_name_raw.strip()
        # 去书名号
        name = name.strip("《》").strip("「」").strip('"').strip("'")
        # 去"第 X 季 / 第 X 卷"后缀,只保留主名
        name = re.sub(r"\s*第[一二三四五六七八九十百千\d]+[季卷部期].*$", "", name)
        # 去注释性括号(如"2007，日本，xxx")
        name = re.sub(r"[（(][^)]*年[^)]*[)）]", "", name)
        # 特殊字符替换为下划线(用于文件名)
        # 注意:这里只清洗"会让作品名混乱"的部分,不动 work_name 主字段
        return name.strip()

    @property
    def file_name_safe(self) -> str:
        """转成安全的文件名"""
        s = self.work_name
        s = re.sub(r'[/\\:*?"<>|]', "_", s)
        s = s.replace(" ", "_")
        return s


def parse_v0_table(file_path: Path) -> list[V0Row]:
    """从 v0 markdown 表格里抽 V0Row 列表"""
    rows: list[V0Row] = []
    if not file_path.exists():
        return rows
    text = file_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    for line in lines:
        line = line.strip()
        # 只取数据行,不取表头/分隔行
        if not line.startswith("|"):
            continue
        if line.startswith("| 作品 |") or line.startswith("|---|"):
            continue

        # 切列(注意作品名可能含 |,但 v0 数据中作品名都是中文,没遇到这个问题)
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 12:
            continue  # 不是数据行

        try:
            year = int(parts[1])
        except ValueError:
            continue  # 年份不是整数,跳过

        # 解析获量分数 "5/5" → 5
        try:
            acq = int(parts[7].split("/")[0])
        except (ValueError, IndexError):
            acq = 0
        try:
            roi = int(parts[8].split("/")[0])
        except (ValueError, IndexError):
            roi = 0

        row = V0Row(
            work_name_raw=parts[0],
            year=year,
            environment=parts[2],
            cultural_paradigm=parts[3],
            narrative_core=parts[4],
            emotion_hook=parts[5],
            existing_games=parts[6],
            acquisition=acq,
            roi=roi,
            risks=parts[11],
        )
        rows.append(row)

    return rows


def detect_media_in_tvw(row: V0Row) -> str:
    """欧美影视汇总表混了 TVW 和 MVW,根据现有提示分流;无法判断默认 TVW"""
    text = f"{row.environment} {row.cultural_paradigm} {row.narrative_core} {row.work_name_raw}"
    # 简单启发:出现"第 X 季"明显是剧;出现单部电影特征不强,默认归 TVW
    if "第" in row.work_name_raw and ("季" in row.work_name_raw or "部" in row.work_name_raw):
        return "TVW"
    # 没把握的全归 TVW,v1 LLM 阶段如发现错位可单独修
    return "TVW"


def derive_quadrant(acq: int, roi: int) -> str:
    if acq == 0 or roi == 0:
        return "未知"
    if acq >= 4 and roi >= 4:
        return "高获量×高ROI"
    if acq >= 4 and roi <= 3:
        return "高获量×低ROI"
    if acq <= 3 and roi >= 4:
        return "低获量×高ROI"
    return "低获量×低ROI"


def truncate_to_max_len(value: str, field_name: str) -> tuple[str, bool]:
    """检查字段长度,超长则截断;返回(值, 是否截断)"""
    if not value:
        return "", False
    max_len = MAX_LEN.get(field_name, 999)
    if len(value) <= max_len:
        return value, False
    return value[:max_len], True


def split_existing_games(v0_games: str) -> list[str]:
    """v0 的'已有游戏'是顿号/逗号分隔的字符串,或者 dict 字符串"""
    if not v0_games or v0_games in ("—", "-", "无", "TBD"):
        return []
    # 处理 v0 偶现的 dict 字符串(如《兄弟连》{'name':..})
    if v0_games.startswith("{"):
        try:
            d = eval(v0_games, {"__builtins__": {}}, {})
            if isinstance(d, dict) and "name" in d:
                return [str(d["name"])]
        except Exception:
            pass
    # 普通分隔
    parts = re.split(r"[、,，;;]", v0_games)
    return [p.strip() for p in parts if p.strip() and p.strip() not in ("—", "-")]


def split_risks(v0_risks: str) -> list[str]:
    if not v0_risks or v0_risks in ("—", "-", "无", "TBD"):
        return []
    parts = re.split(r"[、,，;;]", v0_risks)
    return [p.strip()[:15] for p in parts if p.strip() and p.strip() not in ("—", "-")]


def split_emotion_hooks(v0_emotion: str) -> list[str]:
    """v0 的'情绪钩子'是顿号分隔的形容词,作为 material_hooks 的种子;后续 LLM 重判"""
    if not v0_emotion:
        return []
    parts = re.split(r"[、,，;;]", v0_emotion)
    cleaned = []
    for p in parts:
        p = p.strip()
        if not p or p in ("—", "-"):
            continue
        if len(p) > 10:
            p = p[:10]
        cleaned.append(p)
    return cleaned[:5]  # 最多 5 个


@dataclass
class V1Sample:
    """v1 单作品 yaml frontmatter 的数据载体"""
    work_id: str
    work_name: str
    media_type: str
    media_name: str
    year_first: int
    year_range: list[int]
    # v0 已知字段
    environment: str
    cultural_paradigm: str
    narrative_core: str
    acquisition_score: int
    roi_score: int
    existing_games: list[str]
    risks: list[str]
    material_hooks_v0_seed: list[str]
    # v1 待 LLM 补字段
    n_main: str = "TBD"  # 待 LLM 判
    n_others: list[str] = field(default_factory=list)
    rel_object: str = "null"
    t_can_carry: list[str] = field(default_factory=list)
    core_conflict: str = "TBD"
    # 母题
    mother_theme_id: str = "THM-UNK-001"
    secondary_motif_ids: list[str] = field(default_factory=list)
    motif_confidence: str = "low"
    # 元数据
    evidence_level: str = "C"  # v0 翻译来的数据先标 C,LLM 补字段后升 B
    review_status: str = "auto"
    duplicate_count: int = 1
    truncated_fields: list[str] = field(default_factory=list)


def yaml_quote(s: str) -> str:
    """yaml 字符串安全引号"""
    if not s:
        return '""'
    # 含特殊字符的加双引号
    if any(c in s for c in [':', '#', '"', "'", '\n', '[', ']', '{', '}', '&', '*']):
        escaped = s.replace('"', '\\"')
        return f'"{escaped}"'
    return s


def yaml_list(items: list[str]) -> str:
    if not items:
        return "[]"
    return "[" + ", ".join(yaml_quote(it) for it in items) + "]"


def render_sample(s: V1Sample) -> str:
    """把 V1Sample 渲染成完整的 markdown 文件内容"""
    quadrant = derive_quadrant(s.acquisition_score, s.roi_score)
    truncated_note = (
        f"\n# truncated_fields: {','.join(s.truncated_fields)}" if s.truncated_fields else ""
    )
    dup_note = f"\n# v0_duplicate_count: {s.duplicate_count}" if s.duplicate_count > 1 else ""

    return f"""---
# === 身份 ===
work_id: {s.work_id}
work_name: {yaml_quote(s.work_name)}
work_name_alt: []
media_type: {s.media_type}
year_first: {s.year_first}
year_range: [{s.year_first}, {s.year_range[1]}]
season_count: null

# === 三要素(v0 已有,迁移直翻)===
environment: {yaml_quote(s.environment)}
cultural_paradigm: {yaml_quote(s.cultural_paradigm)}
narrative_core: {yaml_quote(s.narrative_core)}

# === SDT 心理需求(TBD,等 LLM 阶段补)===
n_main: {s.n_main}
n_others: []
rel_object: {s.rel_object}
t_can_carry: []
core_emotion_note: ""
core_conflict: {s.core_conflict}

# === 母题归并(占位)===
mother_theme_id: {s.mother_theme_id}
secondary_motif_ids: []
motif_confidence: {s.motif_confidence}

# === 评分(v0 已有)===
acquisition_score: {s.acquisition_score}
roi_score: {s.roi_score}
quadrant: {quadrant}

# === 素材与玩法 ===
material_hooks: {yaml_list(s.material_hooks_v0_seed)}
existing_games: {yaml_list(s.existing_games)}
recommended_playstyles: []
risk_notes: {yaml_list(s.risks)}

# === 元数据 ===
source: v0-migrate
source_run_id: {TODAY}-migrate
evidence_level: {s.evidence_level}
review_status: {s.review_status}
last_updated: {TODAY}{dup_note}{truncated_note}
---

## 迁移备注

本样本由 v0 markdown 表格迁移而来,LLM 阶段尚未补 SDT 三需求 / T 任务态 / core_conflict / material_hooks 重判。
迁移完成后 evidence_level = C,LLM 增量打标后升至 B。
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="只统计,不写文件")
    parser.add_argument("--media", help="只处理指定媒介(ANI/TVW/MVK/LIT),默认全部")
    args = parser.parse_args()

    print(f"[{datetime.now().strftime('%H:%M:%S')}] v0 → v1 迁移开始")
    print(f"  workspace: {WORKSPACE}")
    print(f"  v0 source: {V0_CATEGORY_DIR}")
    print(f"  v1 output: {V1_SAMPLES_DIR}")
    print()

    # Step 1: 解析所有 v0 表格
    rows_by_media: dict[str, list[V0Row]] = defaultdict(list)
    for v0_file, (media_code, media_dir) in V0_FILE_TO_MEDIA.items():
        if args.media and args.media != media_code:
            continue
        file_path = V0_CATEGORY_DIR / v0_file
        rows = parse_v0_table(file_path)
        print(f"  [{v0_file}] 解析到 {len(rows)} 行")
        rows_by_media[media_code].extend(rows)

    # Step 2: 去重(同 work_name + media_type 合并;year_first 取最早,duplicate_count 计数)
    print("\n[去重]")
    samples_by_media: dict[str, dict[str, V1Sample]] = defaultdict(dict)
    media_to_dir = {v: m for v, (m, _) in [(f, (V0_FILE_TO_MEDIA[f])) for f in V0_FILE_TO_MEDIA]}
    media_dir_map = {code: name for _, (code, name) in V0_FILE_TO_MEDIA.items()}

    for media_code, rows in rows_by_media.items():
        media_dir = media_dir_map[media_code]
        # work_id 在该媒介内顺序分配
        next_id = 1
        for row in rows:
            wn = row.work_name
            if not wn:
                continue

            key = wn  # 用清洗后的 work_name 做去重 key
            if key in samples_by_media[media_code]:
                existing = samples_by_media[media_code][key]
                existing.duplicate_count += 1
                # year_first 取最早,year_range[1] 取最晚
                if row.year < existing.year_first:
                    existing.year_first = row.year
                if row.year > existing.year_range[1]:
                    existing.year_range[1] = row.year
                continue

            # 字段长度检查与截断
            truncated = []
            env, t = truncate_to_max_len(row.environment, "environment")
            if t:
                truncated.append("environment")
            cp, t = truncate_to_max_len(row.cultural_paradigm, "cultural_paradigm")
            if t:
                truncated.append("cultural_paradigm")
            nc, t = truncate_to_max_len(row.narrative_core, "narrative_core")
            if t:
                truncated.append("narrative_core")

            sample = V1Sample(
                work_id=f"WORK-{media_code}-{next_id:05d}",
                work_name=wn,
                media_type=media_code,
                media_name=media_dir,
                year_first=row.year,
                year_range=[row.year, row.year],
                environment=env,
                cultural_paradigm=cp,
                narrative_core=nc,
                acquisition_score=row.acquisition,
                roi_score=row.roi,
                existing_games=split_existing_games(row.existing_games),
                risks=split_risks(row.risks),
                material_hooks_v0_seed=split_emotion_hooks(row.emotion_hook),
                truncated_fields=truncated,
            )
            samples_by_media[media_code][key] = sample
            next_id += 1

        unique = len(samples_by_media[media_code])
        total_dup = sum(s.duplicate_count for s in samples_by_media[media_code].values())
        print(f"  [{media_code}] 去重前 {len(rows)} 行 → 去重后 {unique} 部 (合并 {total_dup - unique} 重复)")

    # Step 3: 写文件
    if args.dry_run:
        print("\n[--dry-run] 不写文件")
    else:
        print("\n[写文件]")
        total_written = 0
        truncate_count = 0
        for media_code, samples_map in samples_by_media.items():
            media_dir = V1_SAMPLES_DIR / media_dir_map[media_code]
            media_dir.mkdir(parents=True, exist_ok=True)
            for sample in samples_map.values():
                fp = media_dir / f"{sample.work_name.replace('/', '_').replace(' ', '_')}.md"
                fp.write_text(render_sample(sample), encoding="utf-8")
                total_written += 1
                if sample.truncated_fields:
                    truncate_count += 1
        print(f"  共写入 {total_written} 个样本文件")
        print(f"  其中字段被截断的样本: {truncate_count}")

    # Step 4: 汇总统计
    print("\n=== 迁移统计 ===")
    total_unique = sum(len(m) for m in samples_by_media.values())
    print(f"  总独立作品(去重后): {total_unique}")
    for media_code, samples_map in sorted(samples_by_media.items()):
        n = len(samples_map)
        dup = sum(s.duplicate_count - 1 for s in samples_map.values())
        long_env = sum(1 for s in samples_map.values() if s.truncated_fields)
        print(f"  [{media_code}] 独立 {n} 部,合并 {dup} 重复,长度超标 {long_env} 部")

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 完成")


if __name__ == "__main__":
    main()
