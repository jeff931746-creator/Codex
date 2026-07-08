#!/usr/bin/env python3
"""
人群簇 v0.2 矩阵反向验证脚本
用 50 个跨媒介样本验证 12 强簇候选是否覆盖完整、归类是否稳定。

输出：
- _raw/{date}_validation_response.txt 原始响应
- 验证报告.md 含归类分布、冲突清单、调整建议
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
for _parent in _THIS_FILE.parents:
    if (_parent / "archive" / "tools" / "lib").is_dir():
        sys.path.insert(0, str(_parent))
        break

from archive.tools.lib.llm_common import RetryPolicy
from archive.tools.lib.llm_client import chat_text

OUTPUT_DIR = Path("/Users/mt/Documents/Codex/archive/资料/人群簇库/_draft")
RAW_DIR = OUTPUT_DIR / "_raw"
TODAY = datetime.now().strftime("%Y-%m-%d")

LLM_ROUTE = "SiliconFlow_GLM"

def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def call_llm(prompt: str, max_tokens: int = 12000, retries: int = 3) -> str:
    return chat_text(
        prompt,
        route=LLM_ROUTE,
        max_tokens=max_tokens,
        temperature=0.2,
        timeout=300,
        retry_policy=RetryPolicy(retries=retries, base_delay=3),
        logger=lambda msg: log(f"  {msg}"),
        return_empty_on_error=True,
    )

def call_llm_cached(prompt: str, label: str, max_tokens: int = 12000) -> str:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_DIR / f"{TODAY}_{label}.txt"
    if raw_path.exists() and raw_path.stat().st_size > 100:
        log(f"  [{label}] 使用缓存")
        return raw_path.read_text(encoding="utf-8")
    raw = call_llm(prompt, max_tokens)
    if raw:
        raw_path.write_text(raw, encoding="utf-8")
    return raw

# ========== 50 个跨媒介验证样本 ==========
SAMPLES = [
    # === 国内重度手游 12 个 ===
    {"id": 1, "name": "三国志战略版", "type": "国内重度手游", "note": "SLG 联盟战、土地、武将"},
    {"id": 2, "name": "率土之滨", "type": "国内重度手游", "note": "SLG 鼻祖、武将羁绊"},
    {"id": 3, "name": "Whiteout Survival 无尽冬日", "type": "国内重度手游", "note": "末日 SLG 海外榜首"},
    {"id": 4, "name": "原神", "type": "国内重度手游", "note": "二次元开放世界抽卡"},
    {"id": 5, "name": "崩坏：星穹铁道", "type": "国内重度手游", "note": "二次元回合制抽卡"},
    {"id": 6, "name": "明日方舟", "type": "国内重度手游", "note": "二次元塔防抽卡"},
    {"id": 7, "name": "梦幻西游手游", "type": "国内重度手游", "note": "经典 MMO 老用户、商人玩法"},
    {"id": 8, "name": "阴阳师", "type": "国内重度手游", "note": "二次元卡牌抽卡"},
    {"id": 9, "name": "和平精英", "type": "国内重度手游", "note": "FPS 大逃杀社交"},
    {"id": 10, "name": "王者荣耀", "type": "国内重度手游", "note": "MOBA 国民竞技"},
    {"id": 11, "name": "口袋奇兵", "type": "国内重度手游", "note": "海外 SLG + 合成创新"},
    {"id": 12, "name": "一念逍遥", "type": "国内重度手游", "note": "修仙放置"},
    # === 国内中轻度手游 8 个 ===
    {"id": 13, "name": "向僵尸开炮", "type": "国内中轻度手游", "note": "射击肉鸽爆款"},
    {"id": 14, "name": "咸鱼之王", "type": "国内中轻度手游", "note": "搞怪放置下沉爆款"},
    {"id": 15, "name": "保卫向日葵 / Plants vs Zombies", "type": "国内中轻度手游", "note": "经典塔防"},
    {"id": 16, "name": "开心消消乐", "type": "国内中轻度手游", "note": "三消休闲国民级"},
    {"id": 17, "name": "羊了个羊", "type": "国内中轻度手游", "note": "短期病毒级解压"},
    {"id": 18, "name": "宾果消消消", "type": "国内中轻度手游", "note": "高 ARPU 三消买量爆款"},
    {"id": 19, "name": "动物餐厅", "type": "国内中轻度手游", "note": "治愈经营独立"},
    {"id": 20, "name": "菇勇者传说", "type": "国内中轻度手游", "note": "Roguelike 出海爆款"},
    # === Steam/主机游戏 8 个 ===
    {"id": 21, "name": "杀戮尖塔 Slay the Spire", "type": "Steam单机", "note": "牌组构筑 Roguelike 鼻祖"},
    {"id": 22, "name": "吸血鬼幸存者", "type": "Steam单机", "note": "极简肉鸽爆款"},
    {"id": 23, "name": "星露谷物语", "type": "Steam单机", "note": "治愈经营长留作品"},
    {"id": 24, "name": "Factorio 异星工厂", "type": "Steam单机", "note": "自动化工厂硬核"},
    {"id": 25, "name": "黑神话：悟空", "type": "主机/Steam", "note": "动作 ARPG 国民现象"},
    {"id": 26, "name": "纪念碑谷", "type": "移动/主机", "note": "艺术向解谜"},
    {"id": 27, "name": "动物森友会", "type": "主机", "note": "Switch 治愈社交"},
    {"id": 28, "name": "黑暗之魂 / 艾尔登法环", "type": "主机/Steam", "note": "魂系硬核动作"},
    # === 短剧 6 个 ===
    {"id": 29, "name": "战神/兵王类短剧（如《无双》）", "type": "短剧", "note": "强还乡团兵王扮猪吃虎"},
    {"id": 30, "name": "赘婿/上门女婿类短剧", "type": "短剧", "note": "低位逆袭打脸狗血"},
    {"id": 31, "name": "霸总/总裁追妻类短剧", "type": "短剧", "note": "女频霸总情感投射"},
    {"id": 32, "name": "复仇/打脸甜宠类短剧", "type": "短剧", "note": "女主复仇/打脸渣男"},
    {"id": 33, "name": "重生/穿越中老年短剧", "type": "短剧", "note": "中老年现实补偿"},
    {"id": 34, "name": "悬疑反转/翻车类短剧", "type": "短剧", "note": "结尾反转烧脑"},
    # === 长篇网文/出版小说 6 个 ===
    {"id": 35, "name": "起点战神/玄幻爽文（如《斗罗大陆》）", "type": "网文", "note": "男频爽文长线"},
    {"id": 36, "name": "起点修仙/修真长篇", "type": "网文", "note": "凡人流境界感"},
    {"id": 37, "name": "晋江女频言情/古言", "type": "网文", "note": "女频情感细腻"},
    {"id": 38, "name": "推理悬疑小说（东野圭吾类）", "type": "出版小说", "note": "推理解谜认知向"},
    {"id": 39, "name": "番茄都市/赘婿快餐文", "type": "网文", "note": "下沉市场超快爽文"},
    {"id": 40, "name": "克苏鲁/科幻硬核小说", "type": "出版小说", "note": "认知扩展硬核"},
    # === 影视/动漫 6 个 ===
    {"id": 41, "name": "甄嬛传 / 知否", "type": "国产电视剧", "note": "宫斗权谋大众化"},
    {"id": 42, "name": "进击的巨人", "type": "日漫", "note": "热血+权谋+世界观"},
    {"id": 43, "name": "孤独的美食家", "type": "日剧", "note": "日常治愈陪伴"},
    {"id": 44, "name": "权力的游戏", "type": "美剧", "note": "权谋史诗"},
    {"id": 45, "name": "黑镜 / 怪奇物语", "type": "美剧", "note": "科幻反思认知"},
    {"id": 46, "name": "我的恶魔(Korean lover)/恋综类", "type": "韩剧/综艺", "note": "亲密情感代入"},
    # === 综艺/直播/社区 4 个 ===
    {"id": 47, "name": "斗地主/欢乐麻将（边界样本）", "type": "棋牌", "note": "习惯型社交消费"},
    {"id": 48, "name": "户外探险/野外生存直播", "type": "直播", "note": "替代探险体验"},
    {"id": 49, "name": "小红书穿搭/家居博主", "type": "社区内容", "note": "审美身份表达"},
    {"id": 50, "name": "B站知识区/财经科普", "type": "社区内容", "note": "认知获取"},
]

# ========== 12 强簇定义 ==========
CLUSTERS_DEF = """
| 簇 ID | 主任务 | 主承接偏好 | 核心收益 | 典型表现 |
|---|---|---|---|---|
| C01 | 情绪调节 | 强刺激覆盖 | — | 爽文/割草/爆装 |
| C02 | 情绪调节 | 情感共鸣 | — | 治愈/陪伴向内容 |
| C03 | 情绪调节 | 低负荷转移 | — | 消除/放置/短视频 |
| C04 | 自我确认 | 强刺激覆盖 | — | PVE 逆袭/战神向 |
| C05 | 自我确认 | 系统模拟 | 竞争排名 | PVP战神/榜单 |
| C06 | 自我确认 | 系统模拟 | 秩序优化 | 经济流派炫耀 |
| C07 | 亲密连接 | 情感共鸣 | — | 乙女/恋爱/角色养成 |
| C08 | 协作归属 | 情感共鸣 | — | MMO团魂/公会剧情 |
| C09 | 协作归属 | 系统模拟 | 协作分工 | SLG联盟/MMO公会 |
| C10 | 认知扩展 | 系统模拟 | 规则解码 | 解谜/构筑/策略 |
| C11 | 控制感重建 | 系统模拟 | 秩序优化 | 模拟经营/建造 |
| C12 | 控制感重建 | 系统模拟 | 竞争排名 | SLG重氪霸主 |

【作用域 boundary 判据，区分易混簇】
- 满足感来自"我这个个体更强/更稀有" → 自我确认（C04/C05/C06）
- 满足感来自"我让一套系统/组织/世界按我的规则运转" → 控制感重建（C11/C12）
- 例如：传奇战神→C05；SLG霸服→C12；晒阵容/晒流派→C06；模拟经营井然有序→C11
"""

def build_prompt():
    samples_str = "\n".join(
        f"{s['id']}. 【{s['type']}】《{s['name']}》— {s['note']}"
        for s in SAMPLES
    )

    return f"""你是资深用户研究专家。请用以下"12 强簇候选"对 50 个跨媒介样本做归类验证。

# 12 强簇候选（v0.2）

{CLUSTERS_DEF}

# 一级任务（6 个，互斥）

1. 情绪调节：处理负面状态（焦虑/压抑/疲惫/无聊）
2. 自我确认：确认我是谁、我有价值、我没掉队
3. 亲密连接：获得情感连接、被看见、被需要、虚拟亲密
4. 协作归属：在团体中有位置、有任务、被依赖（工具性协作）
5. 认知扩展：理解世界、解码规则、满足好奇
6. 控制感重建：在不可控的生活中重建一个可控小世界

# 主承接偏好（4 个）

- 强刺激覆盖：爽文、爆装、割草、搞笑、恐怖
- 情感共鸣：治愈、恋爱、剧情、陪伴、代入
- 低负荷转移：消除、放置、美食、日常、轻收集
- 系统模拟：SLG、经营、建造、解谜、策略优化（内部再分竞争排名/协作分工/秩序优化/规则解码）

# 验证规则

1. 每个样本必须选 1 个**主簇**（C01-C12，或标"无合适簇"）
2. 如有显著副任务，标 1-2 个**副簇**
3. **冲突标记**：归类是否勉强、规则是否被打破，必须诚实标注
4. **不能拼凑**：若 12 簇都不合适，必须标"无合适簇"并说明缺什么维度
5. 棋牌/二次元抽卡/女性向悬疑古风等边界样本，按 boundary 判据归类后说明依据

# 待验证样本（50 个）

{samples_str}

# 输出格式（JSON 数组，50 个）

```json
[
  {{
    "id": 1,
    "name": "三国志战略版",
    "audience_desc": "核心受众一句话描述（30字内）",
    "main_task": "协作归属",
    "main_carrier": "系统模拟",
    "system_yield": "协作分工",
    "main_cluster": "C09",
    "secondary_clusters": ["C12"],
    "fit_quality": "good/marginal/poor/none",
    "conflict_note": "归类时是否勉强、与哪个簇冲突、为什么（30字内，无冲突填'无'）",
    "missing_dim": "若 main_cluster=无合适簇，缺什么维度"
  }},
  ...
]
```

【硬约束】
- 50 个样本全部必须有 main_cluster（C01-C12 或"无合适簇"）
- fit_quality 是 4 个枚举，不能模糊
- conflict_note 不允许写"无问题"等套话，要么"无"要么具体说明

只返回 JSON 数组，不要其他文字或代码块标记。"""

def parse_json(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text.strip())

def write_report(results: list):
    """生成验证报告"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / f"validation_report_{TODAY}.md"

    # 统计
    cluster_count = {}
    fit_count = {"good": 0, "marginal": 0, "poor": 0, "none": 0}
    no_cluster_samples = []
    poor_samples = []
    secondary_count = 0
    conflicts = []

    for r in results:
        cluster = r.get("main_cluster", "未知")
        cluster_count[cluster] = cluster_count.get(cluster, 0) + 1

        fit = r.get("fit_quality", "unknown")
        if fit in fit_count:
            fit_count[fit] += 1

        if cluster == "无合适簇":
            no_cluster_samples.append(r)
        if fit == "poor":
            poor_samples.append(r)

        sec = r.get("secondary_clusters", [])
        if sec and len(sec) > 0:
            secondary_count += 1

        cn = r.get("conflict_note", "")
        if cn and cn != "无" and len(cn) > 3:
            conflicts.append(r)

    total = len(results)
    success_rate = (fit_count["good"] + fit_count["marginal"]) / total * 100 if total else 0
    secondary_rate = secondary_count / total * 100 if total else 0
    no_cluster_rate = fit_count["none"] / total * 100 if total else 0

    # 写报告
    lines = [
        f"# 人群簇 v0.2 矩阵反向验证报告",
        f"",
        f"**验证日期**：{TODAY}",
        f"**样本数**：{total}",
        f"**模型**：{LLM_ROUTE}",
        f"",
        f"## 一、关键指标",
        f"",
        f"| 指标 | 数值 | 判据 |",
        f"|---|---|---|",
        f"| 归类成功率（good+marginal） | {success_rate:.1f}% | ≥85% 通过 / 70-85% 补判据 / <70% 调整矩阵 |",
        f"| 复合归类率（含副簇） | {secondary_rate:.1f}% | >30% 考虑合簇 |",
        f"| 无簇可归率 | {no_cluster_rate:.1f}% | >10% 矩阵漏维度 |",
        f"",
        f"## 二、12 簇归类分布",
        f"",
        f"| 簇 ID | 样本数 | 占比 |",
        f"|---|---|---|",
    ]
    for cid in ["C01","C02","C03","C04","C05","C06","C07","C08","C09","C10","C11","C12","无合适簇"]:
        count = cluster_count.get(cid, 0)
        pct = count / total * 100 if total else 0
        lines.append(f"| {cid} | {count} | {pct:.1f}% |")

    lines += [
        f"",
        f"## 三、归类质量分布",
        f"",
        f"| 质量 | 样本数 | 含义 |",
        f"|---|---|---|",
        f"| good | {fit_count['good']} | 完美匹配 |",
        f"| marginal | {fit_count['marginal']} | 基本匹配，少量勉强 |",
        f"| poor | {fit_count['poor']} | 勉强归入，明显不合 |",
        f"| none | {fit_count['none']} | 无合适簇 |",
        f"",
        f"## 四、无合适簇样本（高优先级）",
        f"",
    ]
    if no_cluster_samples:
        for r in no_cluster_samples:
            lines.append(f"### {r['id']}. 《{r['name']}》")
            lines.append(f"- audience_desc：{r.get('audience_desc', '')}")
            lines.append(f"- missing_dim：{r.get('missing_dim', '')}")
            lines.append(f"- conflict_note：{r.get('conflict_note', '')}")
            lines.append(f"")
    else:
        lines.append("无")
        lines.append("")

    lines += [
        f"## 五、Poor 质量样本（次高优先级）",
        f"",
    ]
    if poor_samples:
        for r in poor_samples:
            lines.append(f"### {r['id']}. 《{r['name']}》")
            lines.append(f"- main_cluster：{r.get('main_cluster')}")
            lines.append(f"- conflict_note：{r.get('conflict_note', '')}")
            lines.append(f"")
    else:
        lines.append("无")
        lines.append("")

    lines += [
        f"## 六、冲突清单（含 conflict_note 的样本）",
        f"",
        f"| ID | 样本 | 主簇 | 副簇 | 质量 | 冲突说明 |",
        f"|---|---|---|---|---|---|",
    ]
    for r in conflicts:
        sec = "、".join(r.get("secondary_clusters", [])) or "—"
        lines.append(
            f"| {r['id']} | {r['name'][:20]} | {r['main_cluster']} | {sec} | {r['fit_quality']} | {r['conflict_note']} |"
        )

    lines += [
        f"",
        f"## 七、所有样本归类全表",
        f"",
        f"| ID | 类型 | 样本 | 主任务 | 承接 | 系统收益 | 主簇 | 副簇 | 质量 |",
        f"|---|---|---|---|---|---|---|---|---|",
    ]
    for i, r in enumerate(results):
        sample = SAMPLES[i] if i < len(SAMPLES) else {}
        sec = "、".join(r.get("secondary_clusters", [])) or "—"
        lines.append(
            f"| {r['id']} | {sample.get('type','—')} | {r['name'][:18]} | {r.get('main_task','—')} | "
            f"{r.get('main_carrier','—')} | {r.get('system_yield','—')} | {r['main_cluster']} | {sec} | {r['fit_quality']} |"
        )

    lines += [
        f"",
        f"## 八、自动判定",
        f"",
    ]
    if success_rate >= 85 and secondary_rate <= 30 and no_cluster_rate <= 10:
        verdict = "✅ 矩阵通过验证，可进入命名阶段"
    elif success_rate >= 70:
        verdict = "⚠️ 矩阵基本可用，需要补判据或处理边界样本"
    else:
        verdict = "❌ 矩阵需要调整，回到 v0.3"

    lines.append(f"**结论**：{verdict}")
    lines.append("")
    lines.append(f"## 九、建议下一步")
    lines.append("")
    if cluster_count.get("无合适簇", 0) > 0:
        lines.append(f"- 关注 {cluster_count['无合适簇']} 个无合适簇样本，判断是否需要新增维度")
    if fit_count["poor"] > 3:
        lines.append(f"- 关注 {fit_count['poor']} 个 poor 样本，可能需要拆簇或加判据")
    if secondary_rate > 30:
        lines.append(f"- 复合率 {secondary_rate:.1f}% 偏高，考虑簇合并")

    # 簇覆盖度
    empty_clusters = [c for c in ["C01","C02","C03","C04","C05","C06","C07","C08","C09","C10","C11","C12"]
                      if cluster_count.get(c, 0) == 0]
    if empty_clusters:
        lines.append(f"- 空簇（无样本归入）：{', '.join(empty_clusters)}——可能是矩阵冗余或样本不够")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    log(f"  ✓ 写出报告：{report_path}")
    return report_path, success_rate, no_cluster_rate, secondary_rate

def main():
    log("=" * 60)
    log("人群簇 v0.2 矩阵反向验证")
    log("=" * 60)
    log(f"模型：{LLM_ROUTE}")
    log(f"样本数：{len(SAMPLES)}")
    log(f"输出：{OUTPUT_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    log("\n[1/3] 构造 prompt...")
    prompt = build_prompt()
    log(f"  prompt 长度：{len(prompt)} 字符")

    log("\n[2/3] 调用 LLM 归类...")
    raw = call_llm_cached(prompt, "validation_50samples", max_tokens=12000)
    if not raw:
        log("❌ LLM 空响应")
        return
    log(f"  原始响应：{len(raw)} 字符")

    log("\n[3/3] 解析并生成报告...")
    try:
        results = parse_json(raw)
        if not isinstance(results, list):
            log("❌ 返回非数组")
            return
        log(f"  解析到 {len(results)} 个归类结果")

        if len(results) != len(SAMPLES):
            log(f"  ⚠️ 样本数不匹配：期望 {len(SAMPLES)}，得到 {len(results)}")

        report_path, success, no_cluster, secondary = write_report(results)

        log("\n" + "=" * 60)
        log(f"✅ 验证完成！")
        log(f"   归类成功率：{success:.1f}%")
        log(f"   无簇可归率：{no_cluster:.1f}%")
        log(f"   复合归类率：{secondary:.1f}%")
        log(f"   报告：{report_path}")
        log("=" * 60)

    except Exception as e:
        log(f"❌ 解析失败：{e}")
        log(f"原始响应前500字：\n{raw[:500]}")

if __name__ == "__main__":
    main()
