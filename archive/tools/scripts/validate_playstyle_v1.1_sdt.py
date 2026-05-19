#!/usr/bin/env python3
"""
玩法承接 v1.1 矩阵验证脚本(SDT 三需求版 A/P/F/N)

公分母:玩法承接 = 玩家行为契约
  A (Action):    反复行为
  P (Pressure):  成本/压力
  F (Feedback):  成功反馈
  N (Need):      基本心理需求(Self-Determination Theory,3 个)

模型:DeepSeek V4 Pro(LLM_PROVIDER=deepseek)
输出:archive/资料/玩法承接库/_draft/validation_report_v1.1_sdt_{date}.md
"""

import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
for _parent in _THIS_FILE.parents:
    if (_parent / "archive" / "tools" / "lib").is_dir():
        sys.path.insert(0, str(_parent))
        break

from archive.tools.lib.llm_client import chat_text
from archive.tools.lib.llm_common import RetryPolicy

OUTPUT_DIR = Path("/Users/mt/Documents/Codex/archive/资料/玩法承接库/_draft")
RAW_DIR = OUTPUT_DIR / "_raw" / "v1.1_sdt"
TODAY = datetime.now().strftime("%Y-%m-%d")
RANKING_DIR = Path("/Users/mt/Documents/Codex/archive/资料/竞品库/爆款年度榜")


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def call_llm(prompt, max_tokens=18000, retries=4):
    return chat_text(
        prompt,
        max_tokens=max_tokens,
        temperature=0.2,
        timeout=360,
        retry_policy=RetryPolicy(
            retries=retries,
            base_delay=3,
            long_retry_after_attempt=3,
            long_delay_range=(300, 600),
        ),
        logger=lambda msg: log(f"  {msg}"),
        return_empty_on_error=True,
    )


def call_llm_cached(prompt, label, max_tokens=18000):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_DIR / f"{TODAY}_{label}.txt"
    if raw_path.exists() and raw_path.stat().st_size > 100:
        log(f"  [{label}] 使用缓存")
        return raw_path.read_text(encoding="utf-8")
    raw = call_llm(prompt, max_tokens)
    if raw:
        raw_path.write_text(raw, encoding="utf-8")
    return raw


def extract_samples_from_md(file_path, year, section):
    samples = []
    text = file_path.read_text(encoding="utf-8")
    seen = set()
    for line in text.split("\n"):
        line = line.strip()
        if not line.startswith("|") or "---" in line:
            continue
        if line.startswith("| 游戏名"):
            continue
        cells = [c.strip() for c in line.split("|") if c.strip()]
        if len(cells) < 3:
            continue
        name, tag, feature = cells[0], cells[1], cells[2]
        if not name or name in seen:
            continue
        seen.add(name)
        samples.append({
            "year": year,
            "section": section,
            "name": name,
            "tag": tag,
            "feature": feature,
        })
    return samples


def load_all_samples():
    seen = {}
    platforms = ["Steam", "微信小游戏", "手游", "任天堂"]
    for platform in platforms:
        platform_dir = RANKING_DIR / platform
        if not platform_dir.exists():
            log(f"  ⚠️ {platform_dir} 不存在")
            continue
        for year in range(2015, 2027):
            fp = platform_dir / f"{year}.md"
            if not fp.exists():
                continue
            year_samples = extract_samples_from_md(fp, year, platform)
            log(f"  {platform}/{year}: {len(year_samples)} 个")
            for s in year_samples:
                if s["name"] not in seen or seen[s["name"]]["year"] < s["year"]:
                    seen[s["name"]] = s
    samples = list(seen.values())
    samples.sort(key=lambda x: (x["section"], -x["year"], x["name"]))
    for i, s in enumerate(samples, 1):
        s["id"] = i
    return samples


V11_RULES = """
# 玩法承接 v1.1 行为契约归类规则(SDT 三需求版,必须严格遵守)

## 公分母

玩法承接 = 玩家行为契约 = A × P × F × N

每个游戏必须用以下 4 个维度描述:
- A (Action):     玩家每天/每局/每节点反复做什么
- P (Pressure):   玩家付出什么 + 承受什么(成本 + 压力)
- F (Feedback):   成功时给玩家什么反馈
- N (Need):       这个反馈满足什么基本心理需求(SDT 三需求)

## A 反复行为(7 个)

| 编号 | A 类型 | 描述 |
|---|---|---|
| A1 | 对抗真人 | 与真人 PVP 胜负、比拼、博弈 |
| A2 | 克服 PVE 内容 | 打 BOSS、推关卡、刷怪 |
| A3 | 投入累积 | 登录、领奖、看战力涨、刷资源(强调"看见数字") |
| A4 | 调整系统 | 设计布局、排序、优化流程、调参 |
| A5 | 探索/试错 | 抽卡组、走未知路线、试规则、解谜 |
| A6 | 见证内容 | 看剧情、看角色、看演出(操作低,主动接收) |
| A7 | 协同执行 | 和真人协调任务、分工执行(非对抗) |

允许多选(一个游戏可同时有多个 A),但必须标 1 个主 A。

## P 成本与压力(成本 5 + 压力 6)

P-成本(玩家必须投入什么):
- P-Rxn: 反应力(操作手感、即时判断)
- P-Time: 时间(单局时长 / 长期在线)
- P-Cog: 认知(钻研规则、查攻略、推演)
- P-Soc: 社交(必须有真人队友/对手/熟人局)
- P-$: 金钱(高 ARPU 才能解锁完整体验)

P-压力(玩家承受什么):
- Pr-Lose: 失败压力(失败惩罚强)
- Pr-Cmp: 比较压力(与真人/排名比较)
- Pr-Rnd: 随机压力(不可控运气因素)
- Pr-Sct: 稀缺压力(资源/时间/角色不够)
- Pr-Spd: 时间限制压力(版本压迫、活动限时)
- Pr-Low: 低压力(基本无压力,自我节奏)

允许多选,但 Pr-Low 与其他压力互斥(同时只能有一个压力主轴)。

## F 成功反馈(6 个)

| 编号 | F 类型 | 反馈本质 |
|---|---|---|
| F1 | 击杀反馈 | 即时打击、爆装、命中(秒级反馈) |
| F2 | 数值膨胀 | 数字慢慢涨,看见就有满足 |
| F3 | 系统涌现 | 多元素跑出意外好结果 |
| F4 | 闭环达成 | 关卡通过、谜题解开、套装齐 |
| F5 | 情感见证 | 剧情进展、角色亲密 |
| F6 | 社交认可 | 排名提升、被点赞、被认同 |

允许多选,但必须标 1 个主 F。

## N 基本心理需求(SDT 三需求,来自 Deci & Ryan)

### N-Comp 胜任感(Competence)

定义:玩家通过游戏验证"我能做到 / 我能掌握"

覆盖范围:
- 操作变强(打击、连招、走位、反应)
- 认知能力被验证(解谜、构筑、推演)
- 系统掌控(自动化、流程优化、规则掌握)
- 数值膨胀(养成数字稳定上涨、战力提升)
- 通关达成(关卡过、副本过、谜题解)
- PVP 上分(排位、比拼、击败对手)

关键特征:有目标 + 有反馈 + 玩家能力被验证

典型:黑神话:悟空(操作胜任)、咸鱼之王(数值胜任)、杀戮尖塔(认知胜任)、Factorio(系统胜任)、王者荣耀(竞技胜任)

### N-Auto 自主性(Autonomy)

定义:玩家获得"我自己决定"的自由感

覆盖范围:
- 无目标体验(没有强制目标,玩什么自己定)
- 自由探索(开放世界探索,主动发现)
- 自定义建造(沙盒、装修、捏脸捏角色)
- 无压力消磨(放置、挂机、休闲消除)
- 低压派对(轻量社交,无强对抗压力)

关键特征:玩家自定节奏 + 自定目标 + 低强制压力(Pr-Low 主导)

典型:Minecraft 创造模式、模拟人生、动物森友会、蛋仔派对(派对模式)、消消乐(无强目标版)

### N-Rel 归属感(Relatedness)

定义:玩家通过游戏获得"我和谁有连接"

覆盖范围:
- 虚拟关系(与 NPC、宠物、可攻略角色、剧情角色的情感纽带)
- 真人关系(队友、公会、熟人局、PVP 对手关系本身)
- 组织归属(SLG 联盟、MMO 公会、固定开黑队)

关键特征:与对象的关系是主驱动,不是工具
(注意:王者荣耀里队友是"赢比赛的工具" → N-Comp;MMO 公会里队友是"归属对象" → N-Rel)

典型:乙女游戏(虚拟亲密)、原神角色向玩家(虚拟亲密)、SLG 联盟战(真人组织)、MMO 公会(真人组织)、宠物游戏(虚拟陪伴)

### 主副规则

每个游戏必须标:
- n_main: N-Comp / N-Auto / N-Rel 之一(必填,1 个主 N)
- n_others: 0-2 个副 N(选填,允许跨需求)

## rel_object 副字段(N-Rel 关系对象类型)

当 n_main = N-Rel 时,必须标 rel_object:
- "virtual": 关系对象是虚拟角色/NPC/宠物
- "real": 关系对象是真人
- "mixed": 虚拟与真人两者并存

当 n_main != N-Rel 时,rel_object 留空(写 null)。

## 核心判断流程

### Step 1: 找出"反复行为 A"

问:玩家每天/每局/每节点绕不开什么?
- 反复对抗真人 → A1
- 反复打怪推图 → A2
- 反复登录领奖、看数字涨 → A3
- 反复调整布局/优化 → A4
- 反复试错/探索 → A5
- 反复看剧情/演出 → A6
- 反复和队友协同任务 → A7

### Step 2: 找出"成本与压力 P"

- 操作手感重要吗?→ P-Rxn
- 需要长时间投入吗?→ P-Time
- 需要思考钻研吗?→ P-Cog
- 必须有真人队友/对手吗?→ P-Soc
- 高付费才能进核心体验吗?→ P-$
- 失败惩罚强吗?→ Pr-Lose
- 跟别人比较吗?→ Pr-Cmp
- 运气主导吗?→ Pr-Rnd
- 资源/时间稀缺吗?→ Pr-Sct
- 限时压迫吗?→ Pr-Spd
- 基本无压力吗?→ Pr-Low

### Step 3: 找出"成功反馈 F"

成功瞬间玩家看到的反馈类型 → F1-F6

### Step 4: 推出"基本心理需求 N"(SDT 三需求)

问 3 个核心问题:
- 这游戏有强目标 + 失败/比较压力,玩家投入是为了证明"我能行/我变强" → N-Comp
- 这游戏 Pr-Low 主导 + 没有强目标,玩家自定节奏 → N-Auto
- 这游戏的主驱动是和某个对象(虚拟角色/真人)的关系 → N-Rel

### Step 5: 输出置信度

- high:A/P/F/N 一致,核心反复行为清晰,N 与 F/P 强相关
- medium:A 清晰但 N 在两个候选间略有摇摆
- low:A 不清晰,或 N 在多个候选间摇摆

## 易混判据(boundary)

### B-A:N-Comp vs N-Auto(最高频易混)

- 有目标 + 失败/比较/稀缺压力 → N-Comp
- 无强目标 + Pr-Low 主导 → N-Auto
- 关键判据:玩家退出时本能感受
  - "下次能更强 / 能解锁更多" → N-Comp
  - "玩爽了 / 可以收工" → N-Auto

### B-B:N-Comp vs N-Rel

- F1/F2/F3/F4 主反馈(打击/数值/系统/闭环) → N-Comp
- F5(情感见证) / F6(社交认可)主反馈 → N-Rel
- 关键判据:玩家投入的目的
  - 投入为了"我变强" → N-Comp
  - 投入为了"和角色/队友的关系" → N-Rel

### B-C:N-Auto vs N-Rel(罕见但需区分)

关键判据:动力源
- 无压力但独自玩 → N-Auto
- 无压力但和别人玩 → N-Rel(rel_object 必须标注)

### 其他 boundary

| 易混对 | 判据 |
|---|---|
| A1 vs A7 | 高光是赢对手 → A1;高光是和队友完成任务 → A7 |
| A2 vs A3 | 关键是"克服设计"(BOSS/关卡) → A2;关键是"看见数字涨" → A3 |
| A3 vs A4 | 看着系统涨(被动) → A3;主动调系统(优化) → A4 |
| A4 vs A5 | 在已知系统里优化 → A4;在未知里试错 → A5 |
| A5 vs A6 | 主动选择/试错 → A5;被动接收 → A6 |
| Pr-Low vs 其他 | 基本无压力 → Pr-Low,不与其他压力并存 |
| Pr-Cmp vs Pr-Lose | 主要因输给真人有压力 → Pr-Cmp;主要因失败惩罚 → Pr-Lose |

## 输出规则

每个样本必须:
- a_main: A1-A7 主反复行为(必填,1 个)
- a_others: 其他 A(选填,数组)
- p_cost: P-Rxn/P-Time/P-Cog/P-Soc/P-$ 中的多选(数组,至少 1 个)
- p_pressure: Pr-Lose/Pr-Cmp/Pr-Rnd/Pr-Sct/Pr-Spd/Pr-Low 中的多选(数组,至少 1 个)
- f_main: F1-F6 主反馈(必填,1 个)
- f_others: 其他 F(选填,数组)
- n_main: N-Comp/N-Auto/N-Rel 主心理需求(必填,1 个)
- n_others: 副心理需求(0-2 个,数组,允许跨需求)
- rel_object: virtual/real/mixed(n_main=N-Rel 必填,其他留 null)
- t_main: T1-T6 主任务态(必填,1 个)
- t_others: 其他可承接任务态(选填,数组,0-2 个)
- confidence: high/medium/low
- boundary_excluded: 显式排除的最相邻 N 的理由

## T 任务态(必填,用户当下处理什么心理任务)

T 是任务态,不是基本需求。N 是地基,T 是用户在某段时间具体处理的问题。
**一个 N 可承接多个 T**,玩家选择该玩法是为了处理某个 T。

| 编号 | T 任务态 | 用户在处理什么 | 主要由哪些 N 承接 |
|---|---|---|---|
| T1 | 状态调节 | 缓解无聊、压力、疲惫、紧张,处理负面状态 | N-Auto(无目标转移)/ N-Comp(快速胜任爽感)/ N-Rel(治愈陪伴) |
| T2 | 价值/能力确认 | 确认"我变强、我有价值、我没掉队" | N-Comp |
| T3 | 对象亲密 | 和角色/宠物/虚拟对象建立情感连接 | N-Rel(rel_object=virtual) |
| T4 | 群体位置 | 在组织/队伍/关系网里有位置 | N-Rel(rel_object=real / mixed) |
| T5 | 规则理解 | 理解、破解、看懂复杂规则 | N-Comp |
| T6 | 秩序掌控 | 把系统、世界、资源变得可控 | N-Comp 或 N-Auto |

### T 任务态判断流程

问 2 个问题确定 T:
1. **用户长期留下来是在处理什么任务?**(主导任务态)
   - 缓解状态 → T1
   - 确认自我价值 → T2
   - 和虚拟对象建立关系 → T3
   - 在真人群体中找位置 → T4
   - 理解复杂规则 → T5
   - 让世界变得有序可控 → T6

2. **这个玩法还能承接哪些其他任务态?**(t_others,0-2 个)
   - 例:动作 RPG 主 T2(确认变强),但也承接 T1(打怪释放压力)
   - 例:SLG 主 T4(在联盟有位置),但也承接 T6(经营自己的城市)

### T 和 N 的关系(必须看懂)

- T 是任务态,N 是底层需求,**两者解耦**
- 同一个 N 可服务多个 T,同一个 T 可由多个 N 承接
- 例:割草泄压(咸鱼之王、向僵尸开炮)
  - N = N-Comp(快速胜任反馈是核心)
  - T = T1(用户在处理"缓解压力/疲惫")
  - 不是 N-Auto!不要因为"放松"就归 N-Auto

### T 易混判据

| 易混对 | 判据 |
|---|---|
| T1 vs T2 | 缓解负面状态(我感觉不好,要好起来) → T1;追求正向价值(我要变更强) → T2 |
| T2 vs T5 | 确认"我能行/我变强" → T2;确认"我看懂了/我理解了" → T5 |
| T2 vs T6 | 确认"我个体变强"(向内) → T2;确认"我让世界按我规则运转"(向外) → T6 |
| T3 vs T4 | 关系对象是虚拟角色 → T3;关系对象是真人组织 → T4 |
| T5 vs T6 | 理解规则后退场(我懂了) → T5;持续维护系统运转(我让它转起来) → T6 |
| T1 vs T6 | 处理负面状态(短期) → T1;长期建立可控秩序 → T6 |
"""


def build_prompt(samples_batch, batch_idx, total_batches):
    samples_str = "\n".join(
        f"{s['id']}. 【{s['year']}/{s['section']}】《{s['name']}》— 类型:{s['tag']};特色:{s['feature']}"
        for s in samples_batch
    )
    return f"""你是资深游戏玩法分析师。请用以下 v1.1 玩法承接行为契约规则(SDT 三需求版)对真实爆款样本做归类。
这是第 {batch_idx}/{total_batches} 批,共 {len(samples_batch)} 个样本。

{V11_RULES}

# 待验证样本({len(samples_batch)} 个)

{samples_str}

# 输出格式(JSON 数组,{len(samples_batch)} 个)

```json
[
  {{
    "id": 1,
    "name": "样本名",
    "a_main": "A2",
    "a_others": ["A5"],
    "p_cost": ["P-Rxn", "P-Time"],
    "p_pressure": ["Pr-Lose"],
    "f_main": "F1",
    "f_others": ["F4"],
    "n_main": "N-Comp",
    "n_others": [],
    "rel_object": null,
    "t_main": "T2",
    "t_others": ["T1"],
    "confidence": "high",
    "boundary_excluded": "排除 N-Auto 因为有失败压力;排除 N-Rel 因为剧情服务于能力验证;T 选 T2 因为核心是确认能力,T1 作为附带状态调节"
  }}
]
```

【硬约束】
- 每个样本必须有 a_main / f_main / n_main / t_main(都是单选)
- n_main 只能是 N-Comp / N-Auto / N-Rel 三选一
- t_main 只能是 T1 / T2 / T3 / T4 / T5 / T6 六选一
- t_others 最多 2 个
- p_cost / p_pressure 必填,至少 1 个
- rel_object:n_main=N-Rel 时必填 virtual/real/mixed,其他必须为 null
- confidence 是 3 个枚举之一
- 必须显式回答 boundary_excluded(与最相邻 N 的差异理由)
- 不能用品类/题材直接推 N,必须从 A/P/F 推
- Pr-Low 与其他 P-压力 互斥

只返回 JSON 数组,不要其他文字或代码块标记。"""


def parse_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text.strip())


def write_report(all_results, all_samples):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / f"validation_report_v1.1_sdt_{TODAY}.md"

    sample_by_id = {s["id"]: s for s in all_samples}
    n_count = {}
    a_count = {}
    f_count = {}
    t_count = {}
    nt_matrix = {}  # N-T 交叉矩阵
    confidence_count = {"high": 0, "medium": 0, "low": 0}
    p_cost_count = {}
    p_pressure_count = {}
    rel_object_count = {"virtual": 0, "real": 0, "mixed": 0, "null": 0}

    section_n = {}
    no_cluster = 0

    for r in all_results:
        n = r.get("n_main", "未知")
        a = r.get("a_main", "未知")
        f = r.get("f_main", "未知")
        t = r.get("t_main", "未知")

        if n not in ("N-Comp", "N-Auto", "N-Rel"):
            no_cluster += 1

        n_count[n] = n_count.get(n, 0) + 1
        a_count[a] = a_count.get(a, 0) + 1
        f_count[f] = f_count.get(f, 0) + 1
        t_count[t] = t_count.get(t, 0) + 1
        nt_matrix.setdefault(n, {})
        nt_matrix[n][t] = nt_matrix[n].get(t, 0) + 1

        conf = r.get("confidence", "unknown")
        if conf in confidence_count:
            confidence_count[conf] += 1

        for c in r.get("p_cost", []):
            p_cost_count[c] = p_cost_count.get(c, 0) + 1
        for p in r.get("p_pressure", []):
            p_pressure_count[p] = p_pressure_count.get(p, 0) + 1

        if n == "N-Rel":
            ro = r.get("rel_object")
            if ro in ("virtual", "real", "mixed"):
                rel_object_count[ro] += 1
            else:
                rel_object_count["null"] += 1

        s = sample_by_id.get(r["id"], {})
        section = s.get("section", "未知")
        section_n.setdefault(section, {})
        section_n[section][n] = section_n[section].get(n, 0) + 1

    total = len(all_results)
    high_rate = confidence_count["high"] / total * 100 if total else 0
    low_rate = confidence_count["low"] / total * 100 if total else 0
    no_cluster_rate = no_cluster / total * 100 if total else 0

    lines = [
        f"# 玩法承接 v1.1 行为契约验证报告(SDT 三需求版,{total} 真实爆款)",
        f"",
        f"**日期**:{TODAY}",
        f"**样本数**:{total}",
        f"**模型**:DeepSeek V4 Pro",
        f"**框架**:玩法承接 = A(反复行为) × P(成本/压力) × F(成功反馈) × N(SDT 三需求)",
        f"",
        f"## 一、验证指标",
        f"",
        f"| 指标 | 数值 | 阈值 | 状态 |",
        f"|---|---|---|---|",
        f"| 主 N 置信度 high 率 | {high_rate:.1f}% | >70% 通过 | {'✅' if high_rate > 70 else '⚠️'} |",
        f"| 主 N 置信度 low 率 | {low_rate:.1f}% | <10% 通过 | {'✅' if low_rate < 10 else '⚠️'} |",
        f"| 无 N 可归率 | {no_cluster_rate:.1f}% | <10% 通过 | {'✅' if no_cluster_rate < 10 else '⚠️'} |",
        f"",
        f"## 二、N 基本心理需求分布(SDT 三需求)",
        f"",
        f"| N | 定义 | 样本数 | 占比 |",
        f"|---|---|---|---|",
    ]
    n_label = {
        "N-Comp": "胜任感(Competence)",
        "N-Auto": "自主性(Autonomy)",
        "N-Rel": "归属感(Relatedness)",
    }
    for nk in ["N-Comp", "N-Auto", "N-Rel"]:
        c = n_count.get(nk, 0)
        pct = c / total * 100 if total else 0
        lines.append(f"| {nk} | {n_label.get(nk, '—')} | {c} | {pct:.1f}% |")

    t_label = {
        "T1": "状态调节",
        "T2": "价值/能力确认",
        "T3": "对象亲密",
        "T4": "群体位置",
        "T5": "规则理解",
        "T6": "秩序掌控",
    }
    lines += [
        f"",
        f"## 三、T 任务态分布",
        f"",
        f"| T | 定义 | 样本数 | 占比 |",
        f"|---|---|---|---|",
    ]
    for tk in ["T1", "T2", "T3", "T4", "T5", "T6"]:
        c = t_count.get(tk, 0)
        pct = c / total * 100 if total else 0
        lines.append(f"| {tk} | {t_label.get(tk, '—')} | {c} | {pct:.1f}% |")

    lines += [
        f"",
        f"## 四、N × T 交叉矩阵(行 N,列 T)",
        f"",
        f"|  | T1 状态调节 | T2 价值确认 | T3 对象亲密 | T4 群体位置 | T5 规则理解 | T6 秩序掌控 | 合计 |",
        f"|---|---|---|---|---|---|---|---|",
    ]
    for nk in ["N-Comp", "N-Auto", "N-Rel"]:
        row_total = sum(nt_matrix.get(nk, {}).values())
        cells = [f"| {nk}"]
        for tk in ["T1", "T2", "T3", "T4", "T5", "T6"]:
            cells.append(str(nt_matrix.get(nk, {}).get(tk, 0)))
        cells.append(str(row_total))
        lines.append(" | ".join(cells) + " |")

    rel_total = sum(rel_object_count.values())
    lines += [
        f"",
        f"## 五、N-Rel 内部 rel_object 分布",
        f"",
        f"| rel_object | 含义 | 样本数 | 占 N-Rel 比 |",
        f"|---|---|---|---|",
        f"| virtual | 关系对象是虚拟角色/NPC/宠物 | {rel_object_count['virtual']} | {rel_object_count['virtual']/rel_total*100 if rel_total else 0:.1f}% |",
        f"| real | 关系对象是真人 | {rel_object_count['real']} | {rel_object_count['real']/rel_total*100 if rel_total else 0:.1f}% |",
        f"| mixed | 虚拟+真人并存 | {rel_object_count['mixed']} | {rel_object_count['mixed']/rel_total*100 if rel_total else 0:.1f}% |",
        f"| (缺失) | n_main=N-Rel 但未标 rel_object | {rel_object_count['null']} | {rel_object_count['null']/rel_total*100 if rel_total else 0:.1f}% |",
    ]

    lines += [
        f"",
        f"## 六、A 反复行为分布",
        f"",
        f"| A | 样本数 | 占比 |",
        f"|---|---|---|",
    ]
    a_label = {
        "A1": "对抗真人",
        "A2": "克服 PVE 内容",
        "A3": "投入累积",
        "A4": "调整系统",
        "A5": "探索/试错",
        "A6": "见证内容",
        "A7": "协同执行",
    }
    for ak in ["A1", "A2", "A3", "A4", "A5", "A6", "A7"]:
        c = a_count.get(ak, 0)
        pct = c / total * 100 if total else 0
        lines.append(f"| {ak} {a_label.get(ak, '')} | {c} | {pct:.1f}% |")

    lines += [
        f"",
        f"## 七、F 主反馈分布",
        f"",
        f"| F | 样本数 |",
        f"|---|---|",
    ]
    f_label = {
        "F1": "击杀反馈",
        "F2": "数值膨胀",
        "F3": "系统涌现",
        "F4": "闭环达成",
        "F5": "情感见证",
        "F6": "社交认可",
    }
    for fk in ["F1", "F2", "F3", "F4", "F5", "F6"]:
        c = f_count.get(fk, 0)
        lines.append(f"| {fk} {f_label.get(fk, '')} | {c} |")

    lines += [
        f"",
        f"## 八、P-成本分布",
        f"",
        f"| P-成本 | 样本数 |",
        f"|---|---|",
    ]
    for pk in ["P-Rxn", "P-Time", "P-Cog", "P-Soc", "P-$"]:
        lines.append(f"| {pk} | {p_cost_count.get(pk, 0)} |")

    lines += [
        f"",
        f"## 九、P-压力分布",
        f"",
        f"| P-压力 | 样本数 |",
        f"|---|---|",
    ]
    for pk in ["Pr-Lose", "Pr-Cmp", "Pr-Rnd", "Pr-Sct", "Pr-Spd", "Pr-Low"]:
        lines.append(f"| {pk} | {p_pressure_count.get(pk, 0)} |")

    lines += [
        f"",
        f"## 十、置信度分布",
        f"",
        f"| 置信度 | 样本数 | 占比 |",
        f"|---|---|---|",
        f"| high | {confidence_count['high']} | {confidence_count['high']/total*100:.1f}% |",
        f"| medium | {confidence_count['medium']} | {confidence_count['medium']/total*100:.1f}% |",
        f"| low | {confidence_count['low']} | {confidence_count['low']/total*100:.1f}% |",
        f"",
        f"## 十一、按平台 N 分布",
        f"",
        f"| 平台 | N 分布 |",
        f"|---|---|",
    ]
    for sec, nmap in sorted(section_n.items()):
        dist = sorted(nmap.items(), key=lambda x: -x[1])
        lines.append(f"| {sec} | " + "、".join(f"{n}({c})" for n, c in dist) + " |")

    lines += [
        f"",
        f"## 十二、Low 置信度样本",
        f"",
    ]
    low_samples = [r for r in all_results if r.get("confidence") == "low"]
    if low_samples:
        for r in low_samples:
            s = sample_by_id.get(r["id"], {})
            lines.append(
                f"- **{r['id']}. 《{r['name']}》** [{s.get('year','—')}/{s.get('section','—')}] | A={r.get('a_main')} N={r.get('n_main')} | {r.get('boundary_excluded','—')}"
            )
    else:
        lines.append("无")

    lines += [
        f"",
        f"## 十三、所有样本归类全表",
        f"",
        f"| ID | 年份 | 平台 | 样本 | A主 | F主 | N主 | N副 | T主 | T副 | rel_object | 置信度 |",
        f"|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in all_results:
        s = sample_by_id.get(r["id"], {})
        n_other = "、".join(r.get("n_others", [])) or "—"
        t_other = "、".join(r.get("t_others", [])) or "—"
        ro = r.get("rel_object") or "—"
        lines.append(
            f"| {r['id']} | {s.get('year','—')} | {s.get('section','—')} | {r['name'][:18]} | {r.get('a_main','—')} | {r.get('f_main','—')} | {r.get('n_main','—')} | {n_other} | {r.get('t_main','—')} | {t_other} | {ro} | {r.get('confidence','—')} |"
        )

    lines += [f"", f"## 十四、自动判定", f""]
    if high_rate > 70 and low_rate < 10:
        verdict = "✅ v1.1 SDT 三需求框架验证通过"
    elif high_rate > 50:
        verdict = "⚠️ v1.1 SDT 基本可用,boundary 需进一步优化"
    else:
        verdict = "❌ v1.1 SDT 需调整"
    lines.append(f"**结论**:{verdict}")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    log(f"  ✓ 写出报告:{report_path}")
    return report_path, high_rate, low_rate, no_cluster_rate


def main():
    log("=" * 60)
    log("玩法承接 v1.1 行为契约验证(SDT 三需求版 A/P/F/N)")
    log("=" * 60)
    provider = os.environ.get("LLM_PROVIDER", "未设置")
    log(f"LLM_PROVIDER:{provider}")
    log(f"DEEPSEEK_MODEL:{os.environ.get('DEEPSEEK_MODEL', '默认')}")

    log("\n[1/3] 加载样本...")
    samples = load_all_samples()
    log(f"  去重后:{len(samples)} 个")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    BATCH_SIZE = 20
    batches = [samples[i:i + BATCH_SIZE] for i in range(0, len(samples), BATCH_SIZE)]
    log(f"\n[2/3] 分 {len(batches)} 批,每批最多 {BATCH_SIZE} 个")

    all_results = []
    for i, batch in enumerate(batches, 1):
        log(f"\n  批次 {i}/{len(batches)}({len(batch)} 样本)")
        prompt = build_prompt(batch, i, len(batches))
        raw = call_llm_cached(prompt, f"sdt_batch{i:03d}", max_tokens=12000)
        if not raw:
            log(f"  ❌ 批次 {i} 空响应")
            continue
        try:
            results = parse_json(raw)
            log(f"  解析 {len(results)} 个结果")
            all_results.extend(results)
        except Exception as e:
            log(f"  ❌ 批次 {i} 解析失败:{e}")
            log(f"  前 300:{raw[:300]}")

        if i < len(batches):
            time.sleep(3)

    log(f"\n[3/3] 总解析 {len(all_results)}/{len(samples)}")
    if not all_results:
        log("❌ 无结果")
        return

    report, high, low, no_cluster = write_report(all_results, samples)
    log("\n" + "=" * 60)
    log(f"✅ v1.1 SDT 三需求验证完成!")
    log(f"   样本数:{len(all_results)}")
    log(f"   高置信度:{high:.1f}%")
    log(f"   低置信度:{low:.1f}%")
    log(f"   无 N 可归:{no_cluster:.1f}%")
    log(f"   报告:{report}")
    log("=" * 60)


if __name__ == "__main__":
    main()
