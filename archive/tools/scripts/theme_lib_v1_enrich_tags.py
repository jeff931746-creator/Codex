#!/usr/bin/env python3
"""
v1.1 三层标签增量打标脚本(Step 4)

只补三个新字段 + 重判 acquisition_score:
- theme_primary(L1 单选)
- theme_secondary(L2 多选 2-5)
- visual_tags(L3 多选 2-5,半开放)
- acquisition_score(重判,基于 IP 知名度 × 视觉钩子强度)

其他字段(n_main / n_others / rel_object / t_can_carry / core_conflict / material_hooks)
不动 — 沿用上一轮 LLM 输出。

特性:
- SiliconFlow_DeepSeek_Flash route + 16 线程并发
- 已经补好(theme_primary != TBD)的样本自动跳过 — 断点续传
- 失败写 _logs/enrich_tags_*.log

用法:
    cd /Users/mt/Documents/Codex
    LLM_ROUTE=SiliconFlow_DeepSeek_Flash python3 archive/tools/scripts/theme_lib_v1_enrich_tags.py --limit 5
    python3 archive/tools/scripts/theme_lib_v1_enrich_tags.py --workers 16
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


def load_bridge_env() -> None:
    bridge_env = Path.home() / "Library/Application Support/FeishuCodexBridge/bridge/.env"
    if not bridge_env.exists():
        return
    if os.environ.get("DEEPSEEK_API_KEY"):
        return
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

LIB_ROOT = WORKSPACE / "archive/资料/历史题材库"
SAMPLES_DIR = LIB_ROOT / "样本/按媒介"
TAGS_FILE = LIB_ROOT / "TAGS.md"
LOGS_DIR = LIB_ROOT.parent.parent / "tools/scripts/历史题材库_数据/_logs"
TODAY = datetime.now().strftime("%Y-%m-%d")


# ========== 加载 L1/L2/L3 候选 ==========
def load_tags() -> tuple[set[str], set[str], set[str]]:
    """从 TAGS.md 解析出 L1(30)、L2(~100)、L3(~100) 候选"""
    text = TAGS_FILE.read_text(encoding="utf-8")

    # L1: §二 段中所有 `xxx` 标签
    l1_section = re.search(r"## 二、L1.*?(?=## 三、)", text, re.DOTALL)
    l1 = set(re.findall(r"`([^`]+)`", l1_section.group(0))) if l1_section else set()

    # L2: §三 段中所有 `xxx` 标签
    l2_section = re.search(r"## 三、L2.*?(?=## 四、)", text, re.DOTALL)
    l2 = set(re.findall(r"`([^`]+)`", l2_section.group(0))) if l2_section else set()

    # L3: §四 段中所有 `xxx` 标签
    l3_section = re.search(r"## 四、L3.*?(?=## 五、)", text, re.DOTALL)
    l3 = set(re.findall(r"`([^`]+)`", l3_section.group(0))) if l3_section else set()

    return l1, l2, l3


L1_TAGS, L2_TAGS_RAW, L3_TAGS = load_tags()
# L1 名字本身也是合法的 L2(跨大类选时常见,如《银魂》L1=喜剧 + L2=[机甲, 江湖])
L2_TAGS = L2_TAGS_RAW | L1_TAGS


# ========== 提示词 ==========
def build_system_prompt() -> str:
    l1_list = " / ".join(sorted(L1_TAGS))
    return f"""你是游戏题材分类专家,熟悉三层标签体系。

任务:给定一部作品的已有字段(work_name / year / environment / cultural_paradigm / narrative_core / core_conflict / material_hooks / n_main),输出 4 个新字段:

输出 JSON 格式(只输出 JSON,不加任何额外文字,不要 markdown 代码块):
{{
  "theme_primary": "<L1 大类,单选>",
  "theme_secondary": ["<L2 子题材>", "...", ...],
  "visual_tags": ["<L3 视觉标签>", "...", ...],
  "acquisition_score": 1-5
}}

判定规则:

【L1 主题大类(theme_primary)】严格从以下 30 个枚举选 1 个:
{l1_list}

选取原则:取作品最主要的题材轴(占核心叙事 50%+),其他题材进 L2。
例:进击的巨人 → "末日";权力的游戏 → "政治权谋";海贼王 → "冒险";老友记 → "都市";黑神话:悟空 → "神话"

【L2 子题材(theme_secondary)】多选 2-5 个,严格从下方候选选(不要造词):

末日类:丧尸 / 病毒爆发 / 核战后 / 自然灾难 / 小行星撞击 / 异种入侵 / 文明崩溃 / 资源枯竭 / 太空末日 / 生态崩坏 / AI 失控 / 瘟疫
灾难类:地震 / 海啸 / 火山 / 空难 / 海难 / 城市火灾 / 极端气候
求生类:荒岛求生 / 极地求生 / 丛林求生 / 沙漠求生 / 孤独求生 / 小队求生 / 城市废墟求生
战争类:二战 / 一战 / 越战 / 朝鲜战争 / 冷战 / 古代战争 / 中世纪战争 / 未来战争 / 内战 / 反恐战争 / 代理人战争 / 游击战
政治权谋类:古代宫斗 / 朝堂权谋 / 现代政坛 / 黑帮帝国 / 王朝兴衰 / 国际博弈 / 商战 / 公司政治 / 权力游戏 / 革命 / 军阀混战
校园类:青春恋爱 / 校园悬疑 / 社团活动 / 升学竞争 / 校园暴力 / 异能学院 / 体育部活 / 日常喜剧 / 毕业季 / 师生关系 / 转校
都市类:职场日常 / 恋爱日常 / 美食 / 文艺 / 怪谈都市 / 异能都市 / 黑帮都市 / 女性独立 / 都市单身
职场类:医疗 / 律政 / 警务 / 军旅 / IT 创业 / 金融 / 媒体 / 教师 / 咨询 / 广告 / 时尚
家庭类:多子家庭 / 重组家庭 / 单亲家庭 / 代际冲突 / 兄弟姐妹 / 夫妻关系
田园类:小镇生活 / 乡村田园 / 农场经营 / 渔村 / 山居
恋爱类:校园恋爱 / 职场恋爱 / 异世界恋爱 / 禁忌恋爱 / 网恋 / 异国恋 / 恋人重逢 / 三角关系 / 养成系 / BG / GL / BL
友情类:兄弟情 / 闺蜜情 / 战友情 / 师徒情 / 跨年龄友情 / 革命友谊
亲情类:父子 / 母女 / 兄弟姐妹 / 祖孙 / 父女 / 母子 / 养子养女 / 遗腹子
武侠类:江湖 / 武林大会 / 名门正派 / 邪派 / 复仇侠客 / 隐士 / 武林秘籍 / 朝廷与江湖
体育类:篮球 / 足球 / 棒球 / 网球 / 田径 / 游泳 / 电竞 / 围棋 / 象棋 / 赛车 / 滑雪 / 武术
冒险类:海上冒险 / 太空冒险 / 荒野探险 / 寻宝 / 地下迷宫 / 异域旅行 / 极地探险 / 深海探险
奇幻类:魔法 / 精灵兽人 / 龙 / 异世界穿越 / 异界召唤 / 史诗奇幻 / 黑暗奇幻 / 城市奇幻 / 童话奇幻
修仙类:凡人流 / 系统流 / 重生流 / 宗门流 / 散修流 / 仙侠 / 渡劫
神话类:中国神话 / 北欧神话 / 希腊神话 / 埃及神话 / 日本神话 / 印度神话 / 克苏鲁
科幻类:近未来 / 远未来 / 平行宇宙 / 时间旅行 / 克隆人 / 基因改造 / 脑机接口 / 量子 / 多元宇宙
赛博朋克类:义体改造 / 脑控 / 大企业统治 / 黑客 / 虚拟现实 / 霓虹都市
太空类:星际探索 / 星际战争 / 太空殖民 / 星际贸易 / 银河帝国 / 太空海盗 / 星舰
机甲类:驾驶式机甲 / 穿戴式动力服 / 巨型机甲 / 小型机甲 / 载具机甲
悬疑类:连环案 / 失踪 / 身份谜团 / 阴谋论 / 时间环 / 心理悬疑 / 家庭秘密 / 超自然悬疑
推理类:本格推理 / 社会派推理 / 法医推理 / 刑侦 / 黑色幽默推理 / 安乐椅侦探 / 历史推理
恐怖类:灵异 / 怪谈 / 心理恐怖 / 血腥恐怖 / 民俗恐怖 / 克苏鲁恐怖 / 生存恐怖 / 丧尸恐怖
犯罪类:黑帮 / 毒品 / 银行劫案 / 连环杀手 / 经济犯罪 / 网络犯罪 / 走私 / 贩卖
历史类:古代 / 近代 / 现代史 / 朝代更迭 / 历史人物 / 战乱年代 / 重大事件
传记类:政治家 / 企业家 / 艺术家 / 科学家 / 音乐人 / 运动员 / 作家 / 女性传记
喜剧类:讽刺喜剧 / 黑色喜剧 / 日常喜剧 / 荒诞喜剧 / 情景喜剧 / 罗曼喜剧 / 家庭喜剧
穿越转生类:穿越古代 / 穿越异世 / 转生异世 / 转生动物 / 转生物品 / 时间穿越 / 平行宇宙穿越 / 重生回到过去

【跨题材通用 L2】适用于任何 L1,LLM 可自由组合:
- 复仇 / 成长 / 逆袭 / 蜕变 / 救赎 / 寻找自我 / 身份认同
- 热血战斗 / 战斗 / 竞技 / 智斗 / 军事行动 / 特工任务 / 谍战 / 特殊行动
- 治愈 / 励志 / 悲剧 / 黑色幽默
- 蒸汽朋克 / 生化朋克 / 太空朋克 / 丝绸朋克
- AI 失控 / 时间轮回 / 平行宇宙 / 元宇宙 / 超能力 / 异能觉醒
- 音乐 / 舞蹈 / 美食 / 园艺 / 手作 / 美术
- 家庭羁绊 / 兄妹 / 母女 / 父子 / 养子养女 / 重组家庭
- 少年成长 / 少女成长 / 青春期烦恼 / 中年危机 / 老年生活
- 外星入侵 / 怪兽 / 吸血鬼 / 狼人 / 精灵 / 骑士
- 异世界 / 异世界穿越 / 转生 / 重生
- 阶级压迫 / 权力博弈 / 信仰冲突 / 理想 vs 现实 / 革命与反抗
- 宫廷权谋 / 后宫 / 古风甜宠
- 西部 / 海盗 / 星海冒险 / 极地探险
- 音乐战斗 / 料理战斗 / 职业竞技 / 电竞职业
- 阵营对抗 / 兵种相克

L2 选取原则:多选 2-5 个,主子题材在前,可跨 L1 大类选(如《银魂》L1=喜剧 + L2=[日常喜剧, 江湖, 异种入侵])。L1 名字本身也是合法 L2。

【L3 视觉标签(visual_tags)】多选 2-5 个,半开放。优先从下方候选选,不够用时可新增。

场景符号候选:废土 / 沙漠 / 森林 / 雪原 / 海洋 / 丛林 / 极地 / 山脉 / 溶洞 / 古堡 / 城堡 / 教堂 / 神社 / 寺庙 / 宫殿 / 废墟 / 迷宫 / 都市夜景 / 霓虹灯 / 摩天楼 / 贫民窟 / 老街巷 / 咖啡馆 / 地铁 / 公寓 / 校园 / 操场 / 教室 / 图书馆 / 宿舍 / 海港 / 船坞 / 海盗船 / 战舰 / 航母 / 潜艇 / 星舰内部 / 空间站 / 行星表面 / 古战场 / 阵地 / 堡垒 / 要塞 / 城墙 / 实验室 / 工厂 / 仓库 / 地下基地 / 军营
视觉符号候选:数字雨 / 代码界面 / 霓虹 / 全息投影 / 光剑 / 机甲 / 义体 / 魔法阵 / 召唤术 / 符咒 / 卷轴 / 法杖 / 龙 / 精灵 / 兽人 / 亡灵 / 丧尸 / 变异生物 / 异形 / 怪兽 / 武器对决 / 刀光剑影 / 枪林弹雨 / 爆炸场面 / 空战 / 飞剑 / 仙鹤 / 云雾缭绕 / 仙境 / 古风装扮 / 汉服 / 和服 / 武侠服饰 / 维多利亚风 / 蒸汽朋克 / 黑色西装 / 墨镜 / 白大褂 / 军装 / 警服
氛围风格候选:末日紧张 / 废土荒凉 / 异世神秘 / 奇幻瑰丽 / 黑暗压抑 / 阳光治愈 / 田园清新 / 校园青春 / 都市繁华 / 权谋阴谋 / 政治紧张 / 战场残酷 / 生存绝望 / 古风诗意 / 江湖侠义 / 仙侠飘逸 / 赛博压迫 / 霓虹冷光 / 近未来质感 / 太空孤寂 / 恋爱甜蜜 / 日常温馨 / 搞笑荒诞 / 家庭温情 / 悬疑诡异 / 推理冷静 / 恐怖压抑

L3 选取原则:同一作品的标签应在同一抽象层(都场景或都氛围,不混填);每个标签 ≤12 字。

【acquisition_score(1-5)】基于 IP 知名度 × 视觉钩子强度:
- 5:顶级 IP(全球破圈) + 视觉强(进击的巨人、海贼王、哈利波特)
- 4:本地市场高热度 IP + 视觉明显
- 3:中等知名度 + 有标准素材
- 2:小众 IP + 视觉需长解释
- 1:无 IP 价值 + 视觉薄弱
判断 IP 知名度时:看作品是否有全球/本地破圈、有无续作/改编、是否进入大众文化记忆。不依赖外部豆瓣/IMDb,以你的知识综合判断。

严格按 JSON 输出,无前后文字。"""


def build_user_prompt(work_name: str, year: str, media_type: str,
                      environment: str, cultural_paradigm: str, narrative_core: str,
                      core_conflict: str, material_hooks: list[str], n_main: str) -> str:
    return f"""请为以下作品输出三层标签 + 重判 acquisition_score,只输出 JSON:

work_name: {work_name}
year: {year}
media_type: {media_type}
environment: {environment}
cultural_paradigm: {cultural_paradigm}
narrative_core: {narrative_core}
core_conflict: {core_conflict}
material_hooks: {material_hooks}
n_main(已判定,作参考): {n_main}
"""


# ========== yaml 解析/写回 ==========
FRONTMATTER_RE = re.compile(r"^(---\n.*?\n---)(\n.*)?$", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict, str, str]:
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
            # 去掉行内注释
            value = m2.group(2)
            value = re.sub(r"\s+#.*$", "", value).strip()
            fields[m2.group(1)] = value
    return fields, fm_text, body


def needs_enrichment(fields: dict, force: bool = False) -> bool:
    if force:
        return True
    return fields.get("theme_primary", "TBD") in ("TBD", "", "null")


def parse_list_value(v: str) -> list[str]:
    if not v or v in ("[]", ""):
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
    pattern = rf"^({re.escape(field_name)}):\s*[^\n]*$"
    replacement = f"{field_name}: {new_value}"
    return re.sub(pattern, replacement, fm_text, count=1, flags=re.MULTILINE)


def strip_inline_comment(line: str) -> str:
    # 去掉 # 后的注释,保留行尾换行
    return re.sub(r"\s+#.*$", "", line)


# ========== LLM 调用 ==========
LOCK = threading.Lock()
STATS = {"ok": 0, "failed": 0, "skipped": 0, "by_media": {}, "new_l3_tags": set()}
SYSTEM_PROMPT = build_system_prompt()


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
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", raw, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass
        return None


def enrich_sample(sample_path: Path, log_file, force: bool = False) -> str:
    text = sample_path.read_text(encoding="utf-8")
    fields, fm_text, body = parse_frontmatter(text)

    if not fields:
        log(f"  [PARSE_ERR] {sample_path.name}: 无 frontmatter", log_file)
        STATS["failed"] += 1
        return "failed"

    if not needs_enrichment(fields, force):
        STATS["skipped"] += 1
        return "skipped"

    work_name = fields.get("work_name", "").strip('"').strip("'")
    year = fields.get("year_first", "?")
    media_type = fields.get("media_type", "?")
    environment = fields.get("environment", "").strip('"').strip("'")
    cultural_paradigm = fields.get("cultural_paradigm", "").strip('"').strip("'")
    narrative_core = fields.get("narrative_core", "").strip('"').strip("'")
    core_conflict = fields.get("core_conflict", "").strip('"').strip("'")
    material_hooks = parse_list_value(fields.get("material_hooks", "[]"))
    n_main = fields.get("n_main", "TBD")

    user_prompt = build_user_prompt(
        work_name, year, media_type,
        environment, cultural_paradigm, narrative_core,
        core_conflict, material_hooks, n_main,
    )

    try:
        raw = chat_text(
            user_prompt,
            system=SYSTEM_PROMPT,
            route="SiliconFlow_DeepSeek_Flash",
            max_tokens=400,
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
        log(f"  [LLM_EMPTY] {work_name}", log_file)
        STATS["failed"] += 1
        return "failed"

    parsed = parse_llm_json(raw)
    if not parsed:
        log(f"  [JSON_ERR] {work_name}: {raw[:120]}", log_file)
        STATS["failed"] += 1
        return "failed"

    # 字段校验
    theme_primary = parsed.get("theme_primary", "TBD")
    if theme_primary not in L1_TAGS:
        log(f"  [L1_INVALID] {work_name}: theme_primary='{theme_primary}' 不在 30 个枚举", log_file)
        STATS["failed"] += 1
        return "failed"

    theme_secondary = parsed.get("theme_secondary") or []
    if not (2 <= len(theme_secondary) <= 5):
        log(f"  [L2_LEN] {work_name}: theme_secondary 长度 {len(theme_secondary)}, 应 2-5", log_file)
        # 不算失败,自动截断或补足
        theme_secondary = theme_secondary[:5] if len(theme_secondary) > 5 else theme_secondary

    invalid_l2 = [t for t in theme_secondary if t not in L2_TAGS]
    if invalid_l2:
        log(f"  [L2_INVALID] {work_name}: 不在候选: {invalid_l2}", log_file)
        # 过滤无效
        theme_secondary = [t for t in theme_secondary if t in L2_TAGS]
        if len(theme_secondary) < 2:
            # 太少了直接报失败
            STATS["failed"] += 1
            return "failed"

    visual_tags = parsed.get("visual_tags") or []
    if not (2 <= len(visual_tags) <= 5):
        visual_tags = visual_tags[:5]

    # 长度截断 ≤12 字
    visual_tags = [t[:12] for t in visual_tags]

    # 收集新 L3 标签
    for t in visual_tags:
        if t not in L3_TAGS:
            with LOCK:
                STATS["new_l3_tags"].add(t)

    try:
        new_acq = int(parsed.get("acquisition_score", 3))
        new_acq = max(1, min(5, new_acq))
    except (ValueError, TypeError):
        new_acq = 3

    new_fm = fm_text
    new_fm = update_field(new_fm, "theme_primary", theme_primary)
    new_fm = update_field(new_fm, "theme_secondary", yaml_list(theme_secondary))
    new_fm = update_field(new_fm, "visual_tags", yaml_list(visual_tags))
    new_fm = update_field(new_fm, "acquisition_score", str(new_acq))
    new_fm = update_field(new_fm, "evidence_level", "B")
    new_fm = update_field(new_fm, "source", "SiliconFlow_DeepSeek_Flash + v0-migrate + tags")
    new_fm = update_field(new_fm, "source_run_id", f"{TODAY}-tags-enrich")
    new_fm = update_field(new_fm, "last_updated", TODAY)

    sample_path.write_text(new_fm + body, encoding="utf-8")
    STATS["ok"] += 1
    media_code = fields.get("media_type", "?")
    STATS["by_media"][media_code] = STATS["by_media"].get(media_code, 0) + 1
    return "ok"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--media", help="只跑某媒介")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print(f"[{datetime.now().strftime('%H:%M:%S')}] v1.1 三层标签打标开始")
    print(f"  L1 候选: {len(L1_TAGS)} 个")
    print(f"  L2 候选: {len(L2_TAGS)} 个")
    print(f"  L3 候选: {len(L3_TAGS)} 个")
    print()

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

    print(f"  待补样本: {len(candidates)}")
    print(f"  workers: {args.workers}")
    print()

    if args.dry_run:
        for fp in candidates[:10]:
            print(f"  {fp.name}")
        return 0

    if not candidates:
        print("[INFO] 无候选样本")
        return 0

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / f"enrich_tags_{TODAY}.log"

    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(f"\n=== run {datetime.now()} workers={args.workers} candidates={len(candidates)} ===\n")

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
                if done % 50 == 0:
                    log(f"进度 {done}/{len(candidates)} (ok={STATS['ok']}, failed={STATS['failed']})", log_file)

    print()
    print("=" * 60)
    print("=== 完成 ===")
    print(f"成功: {STATS['ok']}")
    print(f"失败: {STATS['failed']}")
    print(f"跳过: {STATS['skipped']}")
    if STATS['by_media']:
        print(f"按媒介: {dict(STATS['by_media'])}")
    if STATS['new_l3_tags']:
        print(f"\n新增 L3 标签 (共 {len(STATS['new_l3_tags'])} 个,可考虑加入 TAGS.md):")
        for t in sorted(STATS['new_l3_tags'])[:30]:
            print(f"  - {t}")
        if len(STATS['new_l3_tags']) > 30:
            print(f"  ... 还有 {len(STATS['new_l3_tags']) - 30} 个")
    print(f"\n日志: {log_path}")
    return 0 if STATS['failed'] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
