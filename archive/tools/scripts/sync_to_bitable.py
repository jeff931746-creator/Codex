#!/usr/bin/env python3
"""竞品库 .md → 飞书多维表格 同步（正式流程，取代一次性脚本）。

幂等策略（因 lark-cli record-upsert 的 match_fields 在本版本不可用）：
  1. 抓取表内现有记录 产品名→record_id
  2. 删除「与本地产品同名」的所有表内记录（去重 + 清旧值）
  3. batch-create 全部本地记录（归一化后的新值）
  非本地来源的记录不受影响。重跑安全、不产生重复。

归一化：
  - 主品类 normalize_primary（封闭集）
  - 玩法标签 normalize_tags(strict=True)（收敛长尾）

用法：
    set -a && source "$HOME/Library/Application Support/FeishuCodexBridge/bridge/.env" && set +a
    python3 -m archive.tools.scripts.sync_to_bitable            # 全量同步
    python3 -m archive.tools.scripts.sync_to_bitable --since 2026-06-09
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

CODEX_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(CODEX_ROOT))
from archive.tools.scripts.controlled_vocab import (  # noqa: E402
    normalize_primary, normalize_tags,
)

BASE_TOKEN = "JQMtbtxcna9uucs6clocTMggn0f"
TABLE_ID = "tbl2yDXmGRFFN10V"
COMPETE_DIR = CODEX_ROOT / "archive" / "资料" / "竞品库"
MONETIZATION_ALIAS = {"混合变现": "混合"}

# 表字段顺序（batch-create 的 fields；空单元格用 null）
FIELDS = [
    "产品名", "核心玩法", "平台", "主品类", "玩法标签", "开发商", "发行商",
    "变现方式", "上线状态", "上线日期", "重度分类", "地区", "美术风格",
    "对标产品", "概述", "榜单信息", "来源", "文章链接", "录入日期",
]


def parse_yaml(fp: Path) -> dict:
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


def clean(v):
    return None if (v is None or str(v).strip() in ("", "未知", "待确认")) else v


def ensure_list(v):
    if v is None:
        return None
    if isinstance(v, str):
        return [v] if v else None
    return v if v else None


def build_row(data: dict, weight: str) -> tuple[str, list] | None:
    """返回 (产品名, 按 FIELDS 顺序的行)；空值填 None。"""
    title = (data.get("title") or "").strip()
    if not title:
        return None
    core = clean(data.get("core_gameplay"))
    primary = normalize_primary(data.get("category_primary", ""))
    tags = normalize_tags(data.get("category_tags", []), strict=True)
    mon = clean(data.get("monetization"))
    if mon:
        mon = MONETIZATION_ALIAS.get(mon, mon)
    collected = data.get("collected_date", "")
    collected = f"{collected} 00:00:00" if clean(collected) else None
    row = [
        title, core, ensure_list(data.get("platform")), primary, tags or None,
        clean(data.get("developer")), clean(data.get("publisher")), mon,
        clean(data.get("release_status")), clean(data.get("release_date")),
        weight, ensure_list(data.get("region")), clean(data.get("art_style")),
        clean(data.get("similar_games")), core, clean(data.get("chart_info")),
        clean(data.get("source_name")), clean(data.get("url")), collected,
    ]
    return title, row


def fetch_existing() -> dict[str, list[str]]:
    """抓取表内 产品名 → [record_id]（offset 分页）。"""
    name_to_ids: dict[str, list[str]] = {}
    offset = 0
    for _ in range(50):
        cmd = ["lark-cli", "base", "+record-list", "--base-token", BASE_TOKEN,
               "--table-id", TABLE_ID, "--as", "bot", "--format", "json",
               "--limit", "200", "--offset", str(offset)]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        d = json.loads(r.stdout)
        data = d.get("data", {})
        rows = data.get("data", [])
        rid = data.get("record_id_list", [])
        fields = data.get("fields", [])
        if not rows:
            break
        pi = fields.index("产品名") if "产品名" in fields else 0
        for row, rc in zip(rows, rid):
            nm = row[pi] if pi < len(row) else None
            if nm:
                name_to_ids.setdefault(nm, []).append(rc)
        if not data.get("has_more"):
            break
        offset += len(rows)
    return name_to_ids


def delete_ids(ids: list[str]) -> int:
    deleted = 0
    for i in range(0, len(ids), 100):
        part = ids[i:i + 100]
        cmd = ["lark-cli", "base", "+record-delete", "--base-token", BASE_TOKEN,
               "--table-id", TABLE_ID, "--as", "bot", "--yes"]
        for rc in part:
            cmd += ["--record-id", rc]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        try:
            if json.loads(r.stdout).get("ok"):
                deleted += len(part)
        except Exception:
            pass
        time.sleep(0.5)
    return deleted


def batch_create(rows: list[list]) -> tuple[int, int]:
    ok_n = fail_n = 0
    for i in range(0, len(rows), 50):
        part = rows[i:i + 50]
        payload = json.dumps({"fields": FIELDS, "rows": part}, ensure_ascii=False)
        cmd = ["lark-cli", "base", "+record-batch-create", "--base-token", BASE_TOKEN,
               "--table-id", TABLE_ID, "--as", "bot", "--json", payload]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        out = r.stdout or r.stderr
        try:
            resp = json.loads(out)
            if resp.get("ok"):
                n = len(resp.get("data", {}).get("record_id_list", []))
                ok_n += n
                print(f"  ✅ 批次 {i//50+1}: 写入 {n} 条")
            else:
                fail_n += len(part)
                print(f"  ❌ 批次 {i//50+1}: {resp.get('error',{}).get('message','')[:120]}")
        except Exception:
            fail_n += len(part)
            print(f"  ❌ 批次 {i//50+1}: {out[:120]}")
        time.sleep(1)
    return ok_n, fail_n


def main():
    ap = argparse.ArgumentParser(description="竞品库同步到多维表格")
    ap.add_argument("--since", help="只同步文件名日期 >= 该值（YYYY-MM-DD）")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    # 按产品名去重（同名多文件保留最后出现的：重度>中度>轻度、同档内日期靠后）
    by_name: dict[str, list] = {}
    for weight in ["轻度", "中度", "重度"]:
        for fp in sorted((COMPETE_DIR / weight).glob("*.md")):
            if args.since:
                m = re.match(r"^(\d{4}-\d{2}-\d{2})", fp.name)
                if not m or m.group(1) < args.since:
                    continue
            built = build_row(parse_yaml(fp), weight)
            if built:
                by_name[built[0]] = built[1]
    names = set(by_name.keys())
    rows = list(by_name.values())

    print(f"📊 本地待同步: {len(rows)} 条" + (f"（--since {args.since}）" if args.since else "（全量）"))
    if not rows:
        return

    print("🔍 抓取表内现有记录…")
    existing = fetch_existing()
    dup_ids = [rc for nm, ids in existing.items() if nm in names for rc in ids]
    print(f"  表内 {sum(len(v) for v in existing.values())} 条 / {len(existing)} 唯一名；"
          f"与本地同名需删除 {len(dup_ids)} 条")

    if args.dry_run:
        print("（dry-run，不执行写入）")
        return

    if dup_ids:
        print(f"🗑️  删除同名旧记录…")
        d = delete_ids(dup_ids)
        print(f"  已删除 {d} 条")

    print(f"📤 写入归一化记录…")
    ok_n, fail_n = batch_create(rows)
    print(f"\n{'='*46}\n✅ 写入: {ok_n} | ❌ 失败: {fail_n}")


if __name__ == "__main__":
    main()
