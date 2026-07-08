#!/usr/bin/env python3
"""
用 Pro 模型按《游戏分析框架》修正爆款年度榜。

用法:
    python3 revise_hits.py              # 修正全部年份
    python3 revise_hits.py --year 2020  # 只修正单年

修正内容：
    - 类型标签：换成框架的核心行为动词 + 作用对象，去掉空洞品类标签
    - 一句话特色：去包装层和营销词，改为核心玩法 + 爆款原因的客观表述
    - 条目准确性：删除错误年份的游戏，保持 50-100 行
"""
import argparse
import re
import sys
import time
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
for _parent in _THIS_FILE.parents:
    if (_parent / "archive" / "tools" / "lib").is_dir():
        sys.path.insert(0, str(_parent))
        break

from archive.tools.lib.llm_client import chat_text

# ---------- 路径配置 ----------

OUTPUT_DIR    = Path(__file__).resolve().parent.parent / "research" / "资料" / "竞品库" / "爆款年度榜"
FRAMEWORK_PATH = Path(__file__).resolve().parent / "repos" / "codex-skills-repo" / "references" / "game-analysis-framework.md"

YEARS = list(range(2015, 2027))
TIMEOUT = 300  # 秒

# ---------- API 调用（流式）----------

LLM_ROUTE = "glm.siliconflow.5.1"


def call_glm(prompt: str) -> str:
    """流式调用 SiliconFlow Pro 模型，返回完整响应文本。"""
    try:
        return chat_text(
            prompt,
            route=LLM_ROUTE,
            max_tokens=8192,
            temperature=0.2,
            timeout=TIMEOUT,
            stream=True,
        )
    except Exception as e:
        print(f"    [错] {type(e).__name__}: {e}", flush=True)
        return ""

# ---------- Prompt ----------

# 只取框架核心部分（四层框架 + 案例 + 常见陷阱），避免 prompt 过长
FRAMEWORK_SECTIONS = [
    "## 四层分析框架",
    "## 常见陷阱",
]

def extract_framework_core(framework_text: str) -> str:
    """截取框架中最关键的部分：四层框架定义 + 案例 + 常见陷阱。"""
    lines = framework_text.splitlines()
    # 取从"## 四层分析框架"到"## 应用场景"之前的所有内容
    start = end = None
    for i, line in enumerate(lines):
        if "## 四层分析框架" in line:
            start = i
        if start and "## 应用场景" in line:
            end = i
            break
    if start is not None:
        core = lines[start:end] if end else lines[start:]
        # 再加常见陷阱部分
        for i, line in enumerate(lines):
            if "## 常见陷阱" in line:
                trap_end = None
                for j, l in enumerate(lines[i+1:], i+1):
                    if l.startswith("## ") and "常见陷阱" not in l:
                        trap_end = j
                        break
                trap_lines = lines[i:trap_end] if trap_end else lines[i:]
                core = core + ["", "---", ""] + trap_lines
                break
        return "\n".join(core)
    return framework_text[:4000]  # fallback: 取前4000字符


def make_prompt(framework_core: str, year_content: str, year: int) -> str:
    return f"""你是游戏设计分析师。根据下面的《游戏分析框架》，审校并修正 {year} 年的爆款游戏榜单。

## 修正要求

1. **条目准确性**：删除明显不属于 {year} 年的游戏；如有重要遗漏可补入，但保持总行数 50-100 行/平台
2. **类型标签修正**：
   - 换成框架的「核心行为动词 + 作用对象」格式（如：构建卡组/放置养成/射击闪避）
   - 去掉空洞的品类词（RPG、动作、休闲）除非无更精准替代
3. **一句话特色修正**：
   - 去掉包装层描述（主题、美术、世界观）
   - 去掉营销词（爆款、上瘾、惊艳、极致）
   - 改为：核心玩法机制 + 爆款传播原因（客观事实）
4. **格式要求**：
   - 保留 `# {year} 爆款游戏年度榜` 标题
   - 保留 `## Steam` 和 `## 微信小游戏` 两个分节标题
   - 保留表头行和分割线
   - 表格外不要任何说明文字

## 《游戏分析框架》核心部分

{framework_core}

## 待修正的榜单

{year_content}

直接输出修正后的完整 Markdown，不要任何解释。"""


# ---------- 解析输出 ----------

def clean_output(raw: str) -> str:
    """保留标题行和表格行，去掉多余内容。"""
    lines = raw.strip().splitlines()
    out = []
    for line in lines:
        s = line.strip()
        if s.startswith("#") or s.startswith("|") or s == "":
            out.append(line)
    # 去掉末尾空行
    while out and not out[-1].strip():
        out.pop()
    return "\n".join(out)


# ---------- main ----------

def main():
    if not FRAMEWORK_PATH.exists():
        sys.exit(f"[错] 框架文件不存在: {FRAMEWORK_PATH}")

    framework_text = FRAMEWORK_PATH.read_text(encoding="utf-8")
    framework_core = extract_framework_core(framework_text)
    print(f"[i] 框架核心段落：{len(framework_core):,} chars", flush=True)

    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, default=None, help="只修正指定年份")
    args = ap.parse_args()

    years = [args.year] if args.year else YEARS
    print(f"[i] route：{LLM_ROUTE}  待处理：{years}", flush=True)

    for year in years:
        out_file = OUTPUT_DIR / f"{year}.md"
        if not out_file.exists():
            print(f"[跳过] {year}.md 不存在", flush=True)
            continue

        content = out_file.read_text(encoding="utf-8")
        if "数据获取失败" in content:
            print(f"[跳过] {year}.md 含占位符，先用 collect_hits.py 补数据", flush=True)
            continue

        print(f"\n[{year}] 开始修正（{LLM_ROUTE}）…", flush=True)
        prompt = make_prompt(framework_core, content, year)
        print(f"  [prompt] {len(prompt):,} chars", flush=True)

        revised = call_glm(prompt)
        if not revised:
            print(f"  [失败] 跳过 {year}", flush=True)
            time.sleep(2)
            continue

        cleaned = clean_output(revised)
        out_file.write_text(cleaned + "\n", encoding="utf-8")
        print(f"  [✓] {year}.md 已写入，{len(cleaned):,} chars", flush=True)
        time.sleep(1)

    print(f"\n[✓] 全部完成，输出目录：{OUTPUT_DIR}", flush=True)


if __name__ == "__main__":
    main()
