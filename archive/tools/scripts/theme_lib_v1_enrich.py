#!/usr/bin/env python3
"""
历史题材库 v1 LLM 增量打标脚本(Step 3)

输入:archive/资料/历史题材库/样本/按媒介/.../*.md 中 n_main=TBD 的样本
输出:同名文件,但补全 7 个 v1 新字段:
      - n_main / n_others / rel_object / t_can_carry
      - core_conflict / material_hooks(重判,覆盖 v0 情绪钩子种子)
      - 评分为 0 的样本顺便补 acquisition_score / roi_score

特性:
- 调 SiliconFlow Flash(默认),16 线程并发,断点续传
- 已经补好(n_main!=TBD)的样本自动跳过
- 失败的写入 _logs,不阻塞其他样本
- 每条 ~500 token,3945 条预算约 ¥5

用法:
    cd /Users/mt/Documents/Codex
    source "$HOME/Library/Application Support/FeishuCodexBridge/bridge/.env" && export LLM_ROUTE=SiliconFlow_DeepSeek_Flash

    # 试跑 5 部
    python3 archive/tools/scripts/theme_lib_v1_enrich.py --limit 5

    # 试跑 50 部
    python3 archive/tools/scripts/theme_lib_v1_enrich.py --limit 50

    # 全量跑(默认 16 线程)
    python3 archive/tools/scripts/theme_lib_v1_enrich.py

    # 指定线程数
    python3 archive/tools/scripts/theme_lib_v1_enrich.py --workers 8

    # 重跑某个媒介
    python3 archive/tools/scripts/theme_lib_v1_enrich.py --media LIT --force
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import sys
import threading
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/Users/mt/Documents/Codex")
sys.path.insert(0, str(WORKSPACE))


# ========== 桥接 .env 自动加载 ==========
def load_bridge_env() -> None:
    """如果当前环境没有 LLM key,尝试从飞书桥接的 .env 加载"""
    bridge_env = Path.home() / "Library/Application Support/FeishuCodexBridge/bridge/.env"
    if not bridge_env.exists():
        return
    if os.environ.get("DEEPSEEK_API_KEY") and os.environ.get("SILICONFLOW_API_KEY"):
        return  # 已经设置就不覆盖
    for line in bridge_env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and value and key not in os.environ:
            os.environ[key] = value


load_bridge_env()

from archive.tools.lib.llm_client import chat_text
from archive.tools.lib.llm_common import RetryPolicy

# ========== 路径配置 ==========
LIB_ROOT = WORKSPACE / "archive/资料/历史题材库"
SAMPLES_DIR = LIB_ROOT / "样本/按媒介"
LOGS_DIR = LIB_ROOT.parent.parent / "tools/scripts/历史题材库_数据/_logs"
TODAY = datetime.now().strftime("%Y-%m-%d")

# ========== 提示词 ==========
SYSTEM_PROMPT = """你是游戏题材分析师,熟悉 SDT(自我决定理论)和游戏立项的题材-人群-玩法三位一体框架。

任务:给定一部作品的已有字段(work_name / year / environment / cultural_paradigm / narrative_core / acquisition_score / roi_score / material_hooks_v0_seed),你需要补全 6-8 个新字段,严格按 JSON 输出。

输出 JSON 格式(只输出 JSON,不加任何额外文字、不要 markdown 代码块标记):
{
  "n_main": "N-Comp" | "N-Auto" | "N-Rel",
  "n_others": [],
  "rel_object": "virtual" | "real" | "mixed" | null,
  "t_can_carry": ["T1"-"T6"],
  "core_conflict": "一句话核心冲突,不超过 45 字",
  "material_hooks": ["视觉钩子1", "视觉钩子2", "..."],
  "acquisition_score": 1-5,
  "roi_score": 1-5,
  "core_emotion_note": "选填,N 摇摆或副 N 解释,无则空字符串"
}

判定原则:
1. N(SDT 三需求)
   - N-Comp(胜任感):主角变强 / 破解世界 / 掌控局面 / 数值膨胀 — 黑神话、咸鱼之王、Factorio
   - N-Auto(自主性):无目标自由 / 自由探索 / 自定节奏 — 动森、Minecraft 创造、模拟人生
   - N-Rel(关系感):
     · 温和归属 — 乙女、宠物、公会(rel_object=virtual/real/mixed)
     · 权力关系 — SLG 霸服、权力的游戏、纸牌屋(rel_object=real,因为支配对象都是人)
   - 本能反应判据:观众退出/读完后第一反应想什么?
     · "我也想变强" → N-Comp
     · "好治愈/想在那个世界生活" → N-Auto
     · "好嗑/想和某某建立关系/这个组织真好" → N-Rel(温和)
     · "想看谁干掉谁/谁会上位" → N-Rel(权力)

2. n_others:0-2 个副 N,**只在能明显观察到 20%+ 核心爽点来自该 N 时才填**;否则空数组。宁缺勿滥。

3. rel_object:
   - n_main=N-Rel 或 n_others 含 N-Rel 时必填(virtual/real/mixed)
   - 否则必须 null
   - 只看作品内提供的关系对象,不计读者社群/演员粉丝/UGC 等周边

4. t_can_carry(任务态):0-2 个,主 T 在前,副 T 仅在能明显观察到时才填。常见对应:
   - T1 状态调节(下饭剧、爽片):《老友记》大众观众、咸鱼之王挂机时段
   - T2 价值/能力确认(变强):《黑神话:悟空》、咸鱼之王肝战力
   - T3 对象亲密(角色驱动、CP 向):乙女游戏、《老友记》核心粉
   - T4 群体位置(组织斗争、团队竞技):MMO 公会、SLG 联盟、《权力的游戏》
   - T5 规则理解(烧脑悬疑、解谜):《杀戮尖塔》入坑期、《名侦探柯南》、《死亡笔记》
   - T6 秩序掌控(经营建造、长期搭建):Factorio、星露谷
   - 主 T 按"长期留存+付费最核心驱动"判,不按"看的人最多"判
   - 反例提醒:政治权谋类(《权力的游戏》《纸牌屋》)是 T4 不是 T2

5. core_conflict:一句话核心冲突,不超过 45 字。例:
   - 进击的巨人:"人类对抗巨人 + 内部权力博弈"
   - 权力的游戏:"七大家族争夺铁王座 + 北境长城外异鬼威胁"

6. material_hooks:3-5 个素材钩子,每个 ≤10 字
   - 优先视觉钩子(画面/角色/特效/场面):"巨人压迫感"、"立体机动战斗"、"城墙崩塌"
   - 视觉薄弱时填概念钩子(主题/隐喻/反转):"阶级反差"、"预言弥赛亚"
   - 同一作品内不要混填视觉+概念
   - v0 的 material_hooks_v0_seed 是"情绪形容词",可以参考但要重判为视觉钩子

7. acquisition_score(1-5):IP 知名度 × 视觉钩子强度
   - 5:顶级 IP 全球破圈 + 视觉强(进击的巨人、海贼王)
   - 4:本地高热度 + 视觉明显
   - 3:中等知名度 + 标准素材
   - 2:小众 + 视觉需长解释
   - 1:无 IP 价值 + 视觉薄弱
   - 如果 v0 已有评分(>0),沿用 v0;只在 v0=0 时重新评

8. roi_score(1-5):付费深度 × 数值成长空间
   - 5:奇幻战斗/修仙/SLG 天然导出抽卡/数值
   - 4:RPG/二游/宠物收集
   - 3:动作冒险/模拟经营
   - 2:剧情向/解谜向
   - 1:纯休闲/纯艺术向
   - 同 acquisition_score 规则:v0 已有>0 则沿用

严格按 JSON 输出,无前后文字,无 markdown,无解释。"""


USER_TEMPLATE = """请为以下作品补全 v1 字段,输出 JSON:

work_name: {work_name}
year_first: {year}
media_type: {media_type}
environment: {environment}
cultural_paradigm: {cultural_paradigm}
narrative_core: {narrative_core}
acquisition_score_v0: {acq}  ({"已有,沿用" if acq > 0 else "缺失,需要你给出"})
roi_score_v0: {roi}  ({"已有,沿用" if roi > 0 else "缺失,需要你给出"})
material_hooks_v0_seed: {hooks}  (情绪形容词种子,**请重判为视觉钩子**)
"""

# ========== yaml frontmatter 解析/写回 ==========
FRONTMATTER_RE = re.compile(r"^(---\n.*?\n---)(\n.*)?$", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict, str, str]:
    """返回 (字段 dict, frontmatter 原文, 正文)"""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, "", text
    fm_text = m.group(1)
    body = m.group(2) or ""
    fields = {}
    for line in fm_text.splitlines():
        line = line.rstrip()
        if not line or line.startswith("#") or line == "---":
            continue
        m2 = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.*)$", line)
        if m2:
            fields[m2.group(1)] = m2.group(2).strip()
    return fields, fm_text, body


def needs_enrichment(fields: dict, force: bool = False) -> bool:
    """判断这条样本是否需要 LLM 补字段"""
    if force:
        return True
    if fields.get("n_main", "TBD") == "TBD":
        return True
    if fields.get("core_conflict", "TBD") == "TBD":
        return True
    return False


def yaml_quote(s: str) -> str:
    if not s:
        return '""'
    if any(c in s for c in [':', '#', '"', "'", '\n', '[', ']', '{', '}', '&', '*']):
        escaped = s.replace('"', '\\"')
        return f'"{escaped}"'
    return s


def yaml_list(items: list[str]) -> str:
    if not items:
        return "[]"
    return "[" + ", ".join(yaml_quote(it) for it in items) + "]"


def update_field(fm_text: str, field_name: str, new_value: str) -> str:
    """替换 frontmatter 中某个字段的值(保持注释行不变)"""
    pattern = rf"^({re.escape(field_name)}):\s*.*$"
    replacement = f"{field_name}: {new_value}"
    return re.sub(pattern, replacement, fm_text, count=1, flags=re.MULTILINE)


# ========== LLM 调用 ==========
LOCK = threading.Lock()
STATS = {"ok": 0, "failed": 0, "skipped": 0, "by_media": {}}


def log(msg: str, file=None):
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] {msg}"
    with LOCK:
        print(line, flush=True)
        if file:
            file.write(line + "\n")
            file.flush()


def parse_llm_json(raw: str) -> dict | None:
    if not raw:
        return None
    raw = raw.strip()
    # 去除 markdown 代码块
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # 尝试提取第一个 {} 块
        m = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", raw, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass
        return None


def enrich_sample(sample_path: Path, log_file, force: bool = False) -> str:
    """对单个样本调 LLM,补字段,写回。返回 ok/failed/skipped"""
    text = sample_path.read_text(encoding="utf-8")
    fields, fm_text, body = parse_frontmatter(text)

    if not fields:
        log(f"  [PARSE_ERR] {sample_path.name}: 无法解析 frontmatter", log_file)
        STATS["failed"] += 1
        return "failed"

    if not needs_enrichment(fields, force):
        STATS["skipped"] += 1
        return "skipped"

    # 准备 LLM 输入
    work_name = fields.get("work_name", "").strip('"').strip("'")
    year = fields.get("year_first", "?")
    media_type = fields.get("media_type", "?")
    environment = fields.get("environment", "").strip('"').strip("'")
    cultural_paradigm = fields.get("cultural_paradigm", "").strip('"').strip("'")
    narrative_core = fields.get("narrative_core", "").strip('"').strip("'")
    try:
        acq = int(fields.get("acquisition_score", "0"))
    except ValueError:
        acq = 0
    try:
        roi = int(fields.get("roi_score", "0"))
    except ValueError:
        roi = 0

    hooks_raw = fields.get("material_hooks", "[]")
    # 简单解析
    hooks = []
    if hooks_raw.startswith("[") and hooks_raw.endswith("]"):
        inner = hooks_raw[1:-1]
        hooks = [h.strip().strip('"').strip("'") for h in inner.split(",") if h.strip()]

    # f-string 不能放表达式 — 手工拼
    acq_note = "已有,沿用" if acq > 0 else "缺失,需要你给出"
    roi_note = "已有,沿用" if roi > 0 else "缺失,需要你给出"
    user_prompt = f"""请为以下作品补全 v1 字段,输出 JSON:

work_name: {work_name}
year_first: {year}
media_type: {media_type}
environment: {environment}
cultural_paradigm: {cultural_paradigm}
narrative_core: {narrative_core}
acquisition_score_v0: {acq}  ({acq_note})
roi_score_v0: {roi}  ({roi_note})
material_hooks_v0_seed: {hooks}  (情绪形容词种子,请重判为视觉钩子)
"""

    # 调 LLM
    try:
        raw = chat_text(
            user_prompt,
            system=SYSTEM_PROMPT,
            route="SiliconFlow_DeepSeek_Flash",
            max_tokens=600,
            temperature=0.2,
            timeout=60,
            retry_policy=RetryPolicy(retries=2, base_delay=1.5),
            return_empty_on_error=True,
        )
    except Exception as exc:
        log(f"  [LLM_ERR] {work_name}: {exc}", log_file)
        STATS["failed"] += 1
        return "failed"

    if not raw:
        log(f"  [LLM_EMPTY] {work_name}: 空响应", log_file)
        STATS["failed"] += 1
        return "failed"

    parsed = parse_llm_json(raw)
    if not parsed:
        log(f"  [JSON_ERR] {work_name}: 解析失败 raw={raw[:120]}", log_file)
        STATS["failed"] += 1
        return "failed"

    # 写回字段
    n_main = parsed.get("n_main", "TBD")
    n_others = parsed.get("n_others") or []
    rel_obj = parsed.get("rel_object")
    if rel_obj is None:
        rel_obj_str = "null"
    else:
        rel_obj_str = rel_obj
    t_can_carry = parsed.get("t_can_carry") or []
    core_conflict = parsed.get("core_conflict", "TBD")
    new_hooks = parsed.get("material_hooks") or hooks
    new_acq = parsed.get("acquisition_score", acq)
    new_roi = parsed.get("roi_score", roi)
    note = parsed.get("core_emotion_note", "")

    # 派生 quadrant
    if new_acq >= 4 and new_roi >= 4:
        quadrant = "高获量×高ROI"
    elif new_acq >= 4 and new_roi <= 3:
        quadrant = "高获量×低ROI"
    elif new_acq <= 3 and new_roi >= 4:
        quadrant = "低获量×高ROI"
    else:
        quadrant = "低获量×低ROI"

    new_fm = fm_text
    new_fm = update_field(new_fm, "n_main", n_main)
    new_fm = update_field(new_fm, "n_others", yaml_list(n_others))
    new_fm = update_field(new_fm, "rel_object", rel_obj_str)
    new_fm = update_field(new_fm, "t_can_carry", yaml_list(t_can_carry))
    new_fm = update_field(new_fm, "core_emotion_note", yaml_quote(note))
    new_fm = update_field(new_fm, "core_conflict", yaml_quote(core_conflict))
    new_fm = update_field(new_fm, "material_hooks", yaml_list(new_hooks))
    new_fm = update_field(new_fm, "acquisition_score", str(new_acq))
    new_fm = update_field(new_fm, "roi_score", str(new_roi))
    new_fm = update_field(new_fm, "quadrant", quadrant)
    new_fm = update_field(new_fm, "evidence_level", "B")
    new_fm = update_field(new_fm, "source", "SiliconFlow_DeepSeek_Flash + v0-migrate")
    new_fm = update_field(new_fm, "source_run_id", f"{TODAY}-llm-enrich")
    new_fm = update_field(new_fm, "last_updated", TODAY)

    sample_path.write_text(new_fm + body, encoding="utf-8")
    STATS["ok"] += 1
    media_code = fields.get("media_type", "?")
    STATS["by_media"][media_code] = STATS["by_media"].get(media_code, 0) + 1
    return "ok"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="只跑前 N 部(用于试跑)")
    parser.add_argument("--workers", type=int, default=16, help="并发线程数")
    parser.add_argument("--media", help="只跑某媒介")
    parser.add_argument("--force", action="store_true", help="强制重跑(包括已补字段的样本)")
    parser.add_argument("--dry-run", action="store_true", help="只列出会跑的样本数,不调 LLM")
    args = parser.parse_args()

    # 扫描候选样本
    candidates = []
    for media_dir in sorted(SAMPLES_DIR.iterdir()):
        if not media_dir.is_dir():
            continue
        if args.media and args.media not in media_dir.name:
            continue
        for fp in sorted(media_dir.glob("*.md")):
            text = fp.read_text(encoding="utf-8")
            fields, _, _ = parse_frontmatter(text)
            if needs_enrichment(fields, args.force):
                candidates.append(fp)

    if args.limit > 0:
        candidates = candidates[: args.limit]

    print(f"[{datetime.now().strftime('%H:%M:%S')}] LLM 增量打标开始")
    print(f"  workers: {args.workers}")
    print(f"  candidates: {len(candidates)} 部待补 (force={args.force})")
    print()

    if args.dry_run:
        print(f"[--dry-run] 不调 LLM,列出前 10 个候选:")
        for fp in candidates[:10]:
            print(f"  {fp.relative_to(LIB_ROOT)}")
        return 0

    if not candidates:
        print("[INFO] 没有候选样本,所有样本已补完字段")
        return 0

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / f"enrich_{TODAY}.log"

    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(f"\n=== enrich run {datetime.now()} workers={args.workers} candidates={len(candidates)} ===\n")

        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {executor.submit(enrich_sample, fp, log_file, args.force): fp for fp in candidates}
            done = 0
            for fut in concurrent.futures.as_completed(futures):
                fp = futures[fut]
                try:
                    fut.result()
                except Exception as exc:
                    log(f"  [WORKER_ERR] {fp.name}: {exc}", log_file)
                    STATS["failed"] += 1
                done += 1
                if done % 20 == 0:
                    log(f"进度 {done}/{len(candidates)} (ok={STATS['ok']}, failed={STATS['failed']})", log_file)

    print()
    print("=" * 60)
    print("=== LLM 打标完成 ===")
    print(f"成功:  {STATS['ok']}")
    print(f"失败:  {STATS['failed']}")
    print(f"跳过:  {STATS['skipped']}")
    if STATS['by_media']:
        print(f"按媒介: {dict(STATS['by_media'])}")
    print(f"日志: {log_path}")
    return 0 if STATS['failed'] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
