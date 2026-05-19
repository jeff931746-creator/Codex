#!/usr/bin/env python3
"""
用 GLM API 收集 2015-2026 年 Steam 和微信小游戏平台爆款游戏年度榜。

用法:
    python3 collect_hits.py              # 生成 2015-2026 全部年份
    python3 collect_hits.py --year 2020  # 只生成单年
    python3 collect_hits.py --overwrite  # 覆盖已存在的文件

输出:
    /Users/mt/Documents/Codex/reference/资料/竞品库/爆款年度榜/{year}.md
"""
import argparse
import os
import re
import sys
import time
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
for _parent in _THIS_FILE.parents:
    if (_parent / "archive" / "tools" / "lib").is_dir():
        sys.path.insert(0, str(_parent))
        break

from archive.tools.lib.siliconflow_client import SiliconFlowError, chat_text

# ---------- 路径配置 ----------

ENV_PATH = Path(__file__).resolve().parent / "breakdown-worker" / ".env"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "research" / "资料" / "竞品库" / "爆款年度榜"

YEARS = list(range(2015, 2027))
PLATFORMS = {
    "Steam": "Steam平台（PC/主机独立游戏及商业游戏）",
    "微信小游戏": "微信小游戏平台（微信内嵌小程序游戏）",
}

# ---------- 环境变量 ----------

def load_env():
    if not ENV_PATH.exists():
        return
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

# ---------- API 调用（流式）----------

TIMEOUT = 300  # 秒

def call_glm(prompt: str, model: str) -> str:
    """流式调用 SiliconFlow API，返回完整响应文本。"""
    try:
        return chat_text(
            prompt,
            model=model,
            max_tokens=8192,
            temperature=0.3,
            timeout=TIMEOUT,
            stream=True,
        )
    except SiliconFlowError as e:
        print(f"    [错] {type(e).__name__}: {e}", flush=True)
        return ""

# ---------- Prompt ----------

def make_prompt(year: int, platform: str, platform_desc: str) -> str:
    return f"""列出 {year} 年{platform_desc}上的游戏，严格输出 50-100 行，不得超过 100 行。

要求：
1. 按影响力从高到低排列，优先列有明显爆款表现的游戏（销量突出 / DAU峰值高 / 口碑评分高）
2. 每款游戏提供三列：游戏名 | 类型标签（2-4个词，用"/"分隔） | 一句话特色（≤25字，说明核心玩法或爆款原因）
3. 输出纯 Markdown 表格，表头和分割线都要有，表格之外不要任何说明文字
4. 严格控制在 100 行以内，到 100 行立即停止

输出格式：
| 游戏名 | 类型标签 | 一句话特色 |
|--------|----------|------------|
| 示例游戏 | 类型A/类型B | 核心玩法或爆款原因 |"""

# ---------- 解析 & 清洗 ----------

def clean_table(raw: str) -> str:
    """提取响应中的 Markdown 表格部分，去掉多余文字。"""
    lines = raw.strip().splitlines()
    table_lines = [l for l in lines if l.strip().startswith("|")]
    if not table_lines:
        return raw.strip()  # 无表格时原样返回
    return "\n".join(table_lines)

# ---------- 生成单年文件 ----------

def generate_year(year: int, model: str, api_key: str, base_url: str) -> str:
    """生成单年榜单，返回完整 Markdown 内容。"""
    sections = [f"# {year} 爆款游戏年度榜\n"]

    for platform, platform_desc in PLATFORMS.items():
        print(f"  [{platform}] 请求中…", flush=True)
        prompt = make_prompt(year, platform, platform_desc)
        raw = call_glm(prompt, model)

        if raw:
            table = clean_table(raw)
            sections.append(f"## {platform}\n")
            sections.append("| 游戏名 | 类型标签 | 一句话特色 |")
            sections.append("|--------|----------|------------|")
            # 去掉模型可能重复输出的表头
            for line in table.splitlines():
                if "游戏名" in line and "类型标签" in line:
                    continue
                if re.match(r'\|[-| ]+\|', line):
                    continue
                if line.strip().startswith("|"):
                    sections.append(line)
            sections.append("")
            print(f"  [{platform}] 完成，{len(raw)} chars", flush=True)
        else:
            sections.append(f"## {platform}\n")
            sections.append("（数据获取失败，需手动补充）\n")
            print(f"  [{platform}] 失败，写入占位符", flush=True)

        time.sleep(1)  # 避免请求过于密集

    return "\n".join(sections) + "\n"

# ---------- main ----------

def main():
    load_env()

    # 收集任务用非推理模型，避免浪费推理 tokens
    model = os.environ.get("COLLECT_MODEL", "Qwen/Qwen2.5-72B-Instruct")

    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, default=None, help="只生成指定年份（默认全部 2015-2026）")
    ap.add_argument("--overwrite", action="store_true", help="覆盖已存在的文件")
    args = ap.parse_args()

    years = [args.year] if args.year else YEARS
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[i] 模型：{model}  输出目录：{OUTPUT_DIR}", flush=True)
    print(f"[i] 待处理年份：{years}", flush=True)

    for year in years:
        out_file = OUTPUT_DIR / f"{year}.md"
        if out_file.exists() and not args.overwrite:
            print(f"[跳过] {year}.md 已存在（用 --overwrite 强制覆盖）", flush=True)
            continue

        print(f"\n[{year}] 开始生成…", flush=True)
        content = generate_year(year, model, api_key, base_url)
        out_file.write_text(content, encoding="utf-8")
        print(f"[{year}] ✓ 写入 {out_file}", flush=True)

    print(f"\n[✓] 全部完成，输出目录：{OUTPUT_DIR}", flush=True)


if __name__ == "__main__":
    main()
