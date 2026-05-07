#!/usr/bin/env python3
"""
Daily game breakdown pipeline.
独立脚本（不经过 Claude Code），直接由系统 cron 调用。
可由 `python3 -u /tmp/daily_game_breakdown_standalone.py` 执行。
"""
import json
import os
import random
import re
import ssl
import urllib.request
from datetime import date, datetime
from pathlib import Path

import certifi

LIBRARY_ROOT = Path("/Users/mt/Documents/Codex/research/资料/机制库")
INDEX_FILE = LIBRARY_ROOT / "00_总索引.md"
STATE_FILE = Path("/tmp/daily_game_breakdown_state.json")
STATE_TTL_HOURS = 24

# ========== 候选池（Python 决定选题，不交给 GLM）==========
CANDIDATE_POOL = [
    "咸鱼之王", "寻道大千", "无尽冬日", "向僵尸开炮", "菇勇者传说",
    "这城有良田", "疯狂骑士团", "三国咸鱼王", "弹壳特攻队", "咸鱼之王侠义篇",
    "不朽家族", "寻一个江湖", "最强祖师", "一念逍遥", "小小蚁国",
    "口袋奇兵", "放置奇兵", "三国志战略版", "原始征途",
]

# ========== frontmatter 字段枚举（硬性校验）==========
ENUM_品类 = {"放置卡牌", "Roguelike构筑", "SLG", "塔防", "模拟经营",
             "修仙放置", "射击肉鸽", "MMO", "卡牌对战", "其他"}
ENUM_平台 = {"微信小游戏", "Steam", "App手游", "多平台"}
ENUM_变现 = {"IAP", "买断", "IAA", "IAP+IAA"}

# ========== API key ==========
api_key = os.environ.get("SILICONFLOW_API_KEY", "").strip()
if not api_key:
    raise RuntimeError("SILICONFLOW_API_KEY 未设置")

# ========== 已拆游戏列表 ==========
existing_games = sorted([
    p.name for p in LIBRARY_ROOT.iterdir()
    if p.is_dir() and not p.name.startswith(".") and not p.name.startswith("0") and not p.name.startswith("9")
])

# ========== 选题（state 优先 → 候选池轮询）==========
def load_state():
    if not STATE_FILE.exists():
        return None
    try:
        s = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        ts = datetime.fromisoformat(s["timestamp"])
        if (datetime.now() - ts).total_seconds() > STATE_TTL_HOURS * 3600:
            return None
        return s
    except Exception:
        return None

def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")

def clear_state():
    if STATE_FILE.exists():
        STATE_FILE.unlink()

state = load_state()
resuming = state is not None

if resuming:
    game_name = state["game_name"]
    content1 = state["content1"]
    blocks1 = [(p, b) for p, b in state["blocks1"]]
    print(f"[resume] 检测到 24h 内的 Part 1 状态，恢复游戏：{game_name}，跳过 Part 1")
else:
    pool_remaining = [g for g in CANDIDATE_POOL if g not in existing_games]
    if not pool_remaining:
        print("候选池已耗尽。请补充候选池或删掉部分目录重拆。")
        raise SystemExit(0)
    # 取池中第一个未拆的（按池顺序确定性选择，用户可改池顺序控制下次选谁）
    game_name = pool_remaining[0]
    print(f"[select] 今日拆解：{game_name}（剩余 {len(pool_remaining)} 款未拆）")

# ========== system prompt ==========
COMMON_HEAD = """你是资深游戏策划，按机制库标准拆解一款**微信小游戏平台**的 IAP 爆款。

# 七条质量标准与具体判断清单

## 标准一：机制可重现（禁绝空位词）
**原则**：触发条件+具体结果+设计原因。**禁止词汇**：特定/某些/一定程度/满足条件后/较高/相当/大概/通常/往往/等等

✗ 反例："利息机制让经济体系变得更强" （感受总结，无具体触发和数值）
✓ 正例："每轮结束时，持有金币每满 5 块获得 1 块利息，最多 $5/轮。这让玩家主动选择存钱而非消费。"

**自查清单**：
- [ ] 所有触发条件明确（"满 X 时"而非"足够多时"）
- [ ] 所有结果可量化（"+15%"而非"+一定百分比"）
- [ ] 设计原因说清楚（为什么这个数值，不是别的数值）

---

## 标准二：专题问题可否证（命题格式）
**原则**：问题是**可被反驳的命题**，而非分类标题。能否读者读完后说"我不同意"或"我同意"？

✗ 反例："这个专题要回答 Joker 的设计"（这是标题，不是命题）
✓ 正例："为什么 Joker 是流派发动机，以及 5 槽限制如何把'强度堆叠'变成'强度取舍'"（这是可验证的主张）

**自查清单**：
- [ ] 开头不是"XX 的设计"，而是"XX 为什么..."或"XX 如何..."
- [ ] 问题包含两个部分：现象描述 + 解释原因
- [ ] 读者能说"同意"或"不同意"

---

## 标准三：功能分类有识别边界
**原则**：如果分了类，每类都要有明确的"什么时候属于这类"。类别间的边界清晰。

✗ 反例：分了"核心玩法"和"延伸玩法"，但不说怎么判断哪个是核心、哪个是延伸
✓ 正例："核心玩法 = 每局都必须做的，延伸玩法 = 可选参与的。例：[具体例子]"

**自查清单**：
- [ ] 每个分类都有判别标准（"怎样才属于这一类"）
- [ ] 类别间无重叠（同一个系统不同时属于两类）
- [ ] 用具体例子说明边界

---

## 标准四：结论 If-Then 要有决定性
**原则**：If 必须是**决定性变量**（If 不存在，Then 就不成立），且要**包含机制特征**（不能普遍成立）。

✗ 反例："If 游戏有经济循环，Then 玩家会重复参与"（太宽，任何游戏都有经济循环；而且 If 不是决定性的，其他因素也影响重复参与）
✓ 正例："If 经济产出与消耗 1:1 平衡，Then 玩家不会感到通胀压力"（包含本类特征；If 取反 Then 必破）

**自查清单**：
- [ ] If 包含本游戏品类的机制关键词（放置/SLG/IAP/轮回 等）
- [ ] If 取反后，Then 肯定不成立（强命题）
- [ ] 不能换个游戏品类还 100% 成立

---

## 标准五：模块必须说清不负责什么
**原则**：模块说"负责什么"容易，说"不负责什么"才能明确边界。否则这个模块会无限膨胀。

✗ 反例：02_模块拆解讲完了战斗，结束。没有说"经济平衡不在此讨论"。读者不知道战斗和经济是否分开了。
✓ 正例："本模块负责战斗**结算规则**（谁赢谁输）。**不负责**战斗的动画、音效，也不负责战前的阵容构筑（那是 03_流派设计）。"

**自查清单**：
- [ ] 明确列出"不负责什么"
- [ ] 边界说得清楚（相邻模块间有无重叠）

---

## 标准六：交叉引用有方向和原因
**原则**：不能说"详见 XX 模块"就完事。必须说**为什么相关**，以及**依赖 XX 的哪个具体概念**。

✗ 反例："详见 04_经济循环了解更多"（为什么要看？哪部分相关？）
✓ 正例："这里的数值基于 04_经济循环 的'金币产出速度'，产出越快则战斗奖励权重越低。"

**自查清单**：
- [ ] 每条交叉引用都说"为什么相关"
- [ ] 说明"依赖的具体概念"（不能含糊）

---

## 标准七：模块覆盖对齐总档
**原则**：总档的"系统总览表格"列出的每个系统，都必须有对应的拆解文件。否则知识库有盲区。

✗ 反例：总档说有"8 个核心系统"，但只拆解了 6 个，另外 2 个没有文件
✓ 正例：总档列出的系统与文件夹逐一对应，无遗漏

**自查清单**：
- [ ] 总档的系统表格与实际产出文件逐一对应
- [ ] 没有"提过但未拆解"的系统

# 数值溯源（硬性，脚本会校验）
- 有明确来源（官方公告/财报/公开爆料/社区实测）→ `25%[已验证(来源类别)]`，括号里写来源类别
- 无明确来源或基于同品类对标推断 → `25%[推测]`
- **禁止**不带标签的裸数值
- **禁止**不带括号来源的 `[已验证]`（即写成 `25%[已验证]` 却没有括号 → 视为不合格）

# 每个专题文件结构
专题名称 / 这个专题要回答什么 / 总体判断 / 拆解正文 / 这个模块不负责什么 / 关键判断 / 可迁移结论（If-Then）/ 相关专题。≥ 800 中文字。

# 输出格式
每个文件块 `<<<FILE: 相对路径>>>` 起、`<<<END>>>` 止，相对路径相对于 `{游戏名}/`。不要用 ``` 包裹整体响应。
"""

PART1_TEMPLATE = COMMON_HEAD + """
# 本次任务（第 1/2 批）
今日拆解游戏：**{GAME}**。这是候选池指派的，不要更换游戏。如果你对该游戏不熟，尽力按同品类合理推断并用 `[推测]` 标注所有数值。

本批产出 **00_总档 + 02_模块拆解(≥2 文件) + 按本游戏品类声明的可选专题**。

## 参考示例（Few-shot Learning）

以下是来自《小丑牌》高质量拆解的实际范例，展示执行层、路线层、底层公式、产品化结论的标准格式和具体性水准。**参考这些范例的具体、可重现、边界清晰的表达方式，应用到新游戏的拆解中。**

### 范例 1：执行层拆解的具体性要求

**结算公式与关键约束（来自小丑牌·扑克牌执行层）**

得分 = (参与结算的牌面值之和 + 牌型基础筹码) × (牌型基础倍率 + 加成倍率)

关键：**只有构成牌型的牌才参与筹码结算**。出一对 5，手里还有 3 张其他牌 → 只有两张 5 的牌面值计入筹码；出同花顺 → 五张牌全部参与结算。这个机制直接决定了如何选择强化目标。

**牌面值与花色（执行层的隐性变量）**

| 牌面 | 筹码值 | 说明 |
| --- | --- | --- |
| 2–10 | 面值本身 | 基础线性 |
| J / Q / K | 10 | 大牌筹码值不高，但在特定牌型里构成条件 |
| A | 11 | 皇家同花顺必需 |

四种花色本身没有数值差异，但花色是大量 Joker 的触发条件。这意味着**牌库的花色分布是隐性构筑变量**——不是一张牌的个体问题，而是整副牌的花色比例问题。

### 范例 2：路线层的判断标准与取舍

**Joker 的功能分类（来自小丑牌·Joker 设计拆解）**

- **路线件（方向性 Joker）**：拿到后会明显改变后续决策方向。强制押注特定牌型、花色或出牌模式。
- **触发件（条件性 Joker）**：在特定条件满足时额外结算一次或多次。条件越苛刻，倍率潜力越高。
- **乘区件（x倍率 Joker）**：提供乘法倍率（×2、×3 等）而非加法倍率。是后期分数爆炸的核心件。
- **经济件（资源性 Joker）**：不直接提供战斗收益，而是加速经济或资源获取。

**好 Joker 的判断标准**：
1. 改变后续决策（拿到后，商店里看什么、买什么会跟着变）
2. 排斥另一类玩法（对某条路线有强加成，对其他路线是浪费，制造取舍）
3. 多系统联动（至少和执行层及一种消耗牌联动）
4. 有增长空间（随牌库成熟或牌数减少，价值会提升）

### 范例 3：底层设计公式的强命题（带反面测试）

**结论 1：乘区声明定调**

If 构筑组件具有排他性的触发条件与极高的乘区收益，Then 玩家会在极早的循环节点确立流派方向并产生强烈的定向搜寻动力。

*反面测试*：把 If 取反后，Then 是否仍成立？**不成立**（If 是决定性变量，强命题✓）

**结论 2：容量上限转化决策**

If 核心构筑件存在严苛的容量上限，Then 组件替换将取代组件堆叠成为中后期的核心决策。

*反面测试*：把 If 取反后，Then 是否仍成立？**不成立**（若无容量限制，玩家就无脑堆叠，不需做取舍）

### 范例 4：产品化结论的完整结构

**结论：利息杠杆重塑商店消费节奏（来自小丑牌·产品化结论）**

If 经济系统设置利息上限为 5 元[推测]（每 1 元生 1 利息），Then 玩家在商店阶段会有超过 50%[推测]的概率选择跳过购买以攒钱，从而主动延迟满足并调控成型节奏。

*适用前提*：资源获取相对稳定、商店刷新成本低于留存收益的构筑游戏，玩家对数学期望敏感且具备长线规划能力。
*反例游戏*：《炉石传说》（卡牌对战），因为其法力水晶每回合全额重置，经济系统服务于当回合的节奏，不存在跨回合的储蓄策略。
*太宽测试*：若替换为「卡牌对战」类型，结论不成立。

---

## 00_总档.md 必须以 YAML frontmatter 开头（字段取值必须在枚举内）：

```
---
品类: [放置卡牌, 挂机]                  # 多值数组，取自：{ENUM_CAT}
平台: 微信小游戏                          # 单值，取自：{ENUM_PLAT}
变现: IAP                                 # 单值，取自：{ENUM_MONET}
发行年份: 2023                            # 4 位数字
核心循环: 挂机产出→灵兽养成→推关→付费    # 一句话
研发商: 中清龙图                          # 字符串
拆解日期: {TODAY}                         # 自动填今天
数据时点: 2024Q4                          # 基于哪个时期的资料（版本/赛季/年份季度）
---
```

随后紧跟 `# {GAME} — 总档` 和正文，含：基本信息/一句话定义/核心结构/系统总览表格/模块覆盖检查。

## 总档必须显式声明本次产出的专题列表

在总档正文某段落里写一行（脚本会按此解析）：

    本次拆解产出专题: [00_总档, 02_模块拆解, 04_经济循环, 90_结论提炼, 03_流派设计, 06_商店与奖励]

列表顺序不限，但必须包含 4 个核心：`00_总档, 02_模块拆解, 04_经济循环, 90_结论提炼`，加至少 2 个可选（从 `01_系统结构, 03_流派设计, 05_关卡节奏, 06_商店与奖励, 07_Boss与检定` 中选）。

## 本批产出文件

1. `00_总档.md`（含上述 frontmatter + 专题声明行）
2. `02_模块拆解/{前缀}_{模块名}.md` × ≥2 — 文件名前缀**必须**用：`战斗_` / `养成_` / `构筑_` / `社交_`。例：`02_模块拆解/战斗_灵兽主协战回合.md`
3. 声明列表中属于 01/03 的专题文件（若声明了）
4. `04_经济循环/经济循环拆解.md`

本批**不要**输出 05/06/07/90 和索引补丁。

开头无需 `<<<GAME:...>>>`，直接从第一个文件块起。
""".replace("{ENUM_CAT}", " / ".join(sorted(ENUM_品类))) \
   .replace("{ENUM_PLAT}", " / ".join(sorted(ENUM_平台))) \
   .replace("{ENUM_MONET}", " / ".join(sorted(ENUM_变现))) \
   .replace("{TODAY}", date.today().isoformat())

PART2_TEMPLATE = COMMON_HEAD + """
# 本次任务（第 2/2 批）
延续上一批已选定的游戏（由 user 消息告知），产出剩余声明的专题文件。**只产出上一批未产出、但总档声明列表里的文件**。

## 参考示例（底层公式与产品化结论的写法）

以下来自《小丑牌·结论提炼》的范例，展示底层公式与产品化结论的完整结构。**本批重点是 90_结论提炼 两份文件，务必参照这些范例确保命题强度与格式完整性。**

### 底层公式范例（≥5 条，每条一句，无需论据堆砌）

**结论 1：乘区声明定调**

If 构筑组件具有排他性的触发条件与极高的乘区收益，Then 玩家会在极早的循环节点确立流派方向并产生强烈的定向搜寻动力。

*反面测试*：把 If 取反后，Then 是否仍成立？不成立

**结论 2：底盘重塑兑现偏科**

If 执行层的底盘分布可被低成本重塑，Then 构筑层的极端偏科路线才具备兑现可行性。

*反面测试*：把 If 取反后，Then 是否仍成立？不成立

### 产品化结论范例（每条必须包含4个子字段）

**结论：槽位硬限制驱动成型快感**

If 构筑组件槽位限制在 5 个[推测]且单局循环时长小于 30 分钟[推测] Then 玩家能在 3-5 天[推测]内快速掌握流派成型逻辑，并在取舍中产生强烈的重开欲望。

*适用前提*：买断制或无重度内购的 Roguelike 构筑游戏，局内成长远快于局外养成，用户追求单局内的脑力激荡而非长线数值积累。
*反例游戏*：《原神》（开放世界 RPG），因为其角色配队构筑是长线养成，槽位和装备是数值堆叠与付费抽卡的基础，若采用硬限制会直接切断商业化路径。
*太宽测试*：若替换为「开放世界」类型，结论不成立。

---

## 本批可能产出（按上一批总档声明的专题列表决定）
- `05_关卡节奏/关卡节奏拆解.md`（如声明）
- `06_商店与奖励/商店与奖励拆解.md`（如声明）
- `07_Boss与检定/Boss与挑战拆解.md`（如声明）
- `90_结论提炼/底层设计公式.md`（**必选**，见下）
- `90_结论提炼/产品化结论.md`（**必选**，见下）

## 两份结论文件的分工与硬约束

### 90_结论提炼/底层设计公式.md
**用途**：产出对任何同大类游戏都成立的底层设计命题。偏抽象、偏耐久、不允许编造具体数字。

**格式要求**：≥5 条 If-Then，每条一段话即可，无需论据堆砌。不要引用具体游戏名做佐证。不要出现具体分钟数、天数、百分比之类的"实证感"数字——需要具体数字时用「短/中/长」「低/中/高」这类相对量词。

**反面测试（每条必带）**：在每条结论后追加一行：

    *反面测试*：把 If 取反后，Then 是否仍成立？{成立/不成立}

含义：
- 自评「不成立」= If 是 Then 的决定性变量（强命题）
- 自评「成立」= If 只是 Then 的一条路径（充分不必要，弱命题）

**示例**：
- 强命题 ✓ `If 波次压力是可逆的（推进距离），Then 压力高峰期玩家仍有挽回动力。*反面测试*：If 压力不可逆，Then 玩家仍有挽回动力？{不成立}` — If 取反 Then 必破
- 弱命题（废话） ✗ `If 执行层易懂，Then 新手易上手。*反面测试*：If 执行层难懂，新手还易上手？{成立}` — 新手上手还受其他因素影响，这条 If 不是决定性的

**脚本校验**：`*反面测试*` 行数 ≥5；自评「成立」的条数 ≤ 2（允许少量充分不必要型命题，但超过 2 条说明整文件 If 选得太弱）。

### 90_结论提炼/产品化结论.md
**用途**：产出可直接落地到当前品类/变现形态/用户层的具体设计判断。允许带具体数字（必须 `[推测]` 标签），允许带反例游戏。

**格式要求**：≥5 条 If-Then，每条带"适用前提"和"反例游戏"两个子字段：

    **结论 N：{命题短名}**

    If ... Then ...

    *适用前提*：{什么条件下这条才成立，例：轻度移动端用户、F2P+IAP 变现、局内时长 < 15 分钟}
    *反例游戏*：{一个这条不适用的游戏，并说明为什么不适用；不能举同品类游戏当反例}
    *太宽测试*：若替换为 {单机 RPG / MOBA / 卡牌对战 任选一} 类型，结论{成立/不成立}

**硬约束**：
- ≥5 条 If-Then
- ≥5 条带 `*适用前提*`
- ≥5 条带 `*反例游戏*`（且反例必须跨品类，脚本会检查反例里不含本游戏品类关键词）
- ≥5 条带 `*太宽测试*`，其中自评为「不成立」的条数 ≥ 3（否则说明结论太宽，整文件不合格）
- 结论中的具体数字（≥1 位阿拉伯数字 + %/倍/分钟/天/次/连 等单位）必须带 `[推测]` 或 `[已验证(来源)]` 标签

### 为什么要两份
- 底层公式**命题正确率高但可操作性低**（"路线件比纯数值有构筑感"——对，但你要做什么？）
- 产品化结论**可操作性高但命题正确率低**（带具体数字和反例，易伪造）
- 两份互相纠偏：读底层公式建立方向感，读产品化结论拿落地判断，读者心里有谱哪份更可信

## 最末追加索引补丁块

<<<INDEX_PATCH>>>
| {游戏名} | {主目录相对路径} | {当前重点专题} |
<<<END>>>
"""

# ========== API 调用 ==========
import threading, time
def call_api(messages, max_tokens=16384):
    payload = {
        "model": "Pro/zai-org/GLM-5.1",
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.5,
    }
    req = urllib.request.Request(
        "https://api.siliconflow.cn/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    stop = threading.Event()
    def _heartbeat():
        t0 = time.time()
        while not stop.wait(15):
            print(f"[api] waiting... {int(time.time()-t0)}s", flush=True)
    hb = threading.Thread(target=_heartbeat, daemon=True)
    print(f"[api] request start (max_tokens={max_tokens})", flush=True)
    t0 = time.time()
    hb.start()
    try:
        with urllib.request.urlopen(req, timeout=420, context=ssl_context) as resp:
            content = json.loads(resp.read().decode("utf-8"))["choices"][0]["message"]["content"]
    finally:
        stop.set()
        hb.join(timeout=1)
    print(f"[api] done ({int(time.time()-t0)}s, {len(content)} chars)", flush=True)
    return content

# ========== Part 1 ==========
if not resuming:
    sys1 = PART1_TEMPLATE.replace("{GAME}", game_name)
    content1 = call_api([
        {"role": "system", "content": sys1},
        {"role": "user", "content": f"今天是 {date.today().isoformat()}。请按 Part 1 产出 {game_name} 的总档 + 02 模块拆解 + 声明的其他前半专题。"},
    ], max_tokens=24000)
    blocks1 = re.findall(r"<<<FILE:\s*(.+?)>>>\n(.*?)<<<END>>>", content1, re.DOTALL)
    if len(blocks1) < 3:
        raise RuntimeError(f"Part 1 文件块不足 3（实际 {len(blocks1)}）。原文：{content1[:800]}")
    save_state({
        "timestamp": datetime.now().isoformat(),
        "game_name": game_name,
        "content1": content1,
        "blocks1": blocks1,
    })
    print(f"[part1-ok] 产出 {len(blocks1)} 块，状态已保存")

# ========== 解析总档的专题声明 ==========
toc_body = next((body for path, body in blocks1 if "00_总档" in path), "")
if not toc_body:
    raise RuntimeError("Part 1 未产出 00_总档.md")

decl_m = re.search(r"本次拆解产出专题[:：]\s*\[([^\]]+)\]", toc_body)
if not decl_m:
    raise RuntimeError("00_总档.md 缺少『本次拆解产出专题: [...]』声明行")
declared = [s.strip() for s in decl_m.group(1).split(",") if s.strip()]
core_required = {"00_总档", "02_模块拆解", "04_经济循环", "90_结论提炼"}
declared_set = set(declared)
missing_core = core_required - declared_set
if missing_core:
    raise RuntimeError(f"专题声明缺失核心项：{missing_core}")
optional_valid = {"01_系统结构", "03_流派设计", "05_关卡节奏", "06_商店与奖励", "07_Boss与检定"}
declared_optional = declared_set & optional_valid
if len(declared_optional) < 2:
    raise RuntimeError(f"至少声明 2 个可选专题，实际仅 {len(declared_optional)}：{declared_optional}")

# ========== frontmatter 校验 ==========
fm_m = re.match(r"---\n(.*?)\n---", toc_body, re.DOTALL)
if not fm_m:
    raise RuntimeError("00_总档.md 缺少 YAML frontmatter")
fm_text = fm_m.group(1)

def parse_fm(text):
    d = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            v = [x.strip().strip('"').strip("'") for x in v[1:-1].split(",") if x.strip()]
        else:
            v = v.strip('"').strip("'")
        d[k] = v
    return d

fm = parse_fm(fm_text)
required_fields = ["品类", "平台", "变现", "发行年份", "核心循环", "研发商", "拆解日期", "数据时点"]
for f in required_fields:
    if f not in fm:
        raise RuntimeError(f"frontmatter 缺字段：{f}")

cats = fm["品类"] if isinstance(fm["品类"], list) else [fm["品类"]]
bad_cats = [c for c in cats if c not in ENUM_品类]
if bad_cats:
    raise RuntimeError(f"frontmatter 品类取值不在枚举内：{bad_cats}（允许：{sorted(ENUM_品类)}）")
if fm["平台"] not in ENUM_平台:
    raise RuntimeError(f"frontmatter 平台取值非法：{fm['平台']}（允许：{sorted(ENUM_平台)}）")
if fm["变现"] not in ENUM_变现:
    raise RuntimeError(f"frontmatter 变现取值非法：{fm['变现']}（允许：{sorted(ENUM_变现)}）")
if not re.fullmatch(r"\d{4}", str(fm["发行年份"])):
    raise RuntimeError(f"frontmatter 发行年份必须是 4 位数字：{fm['发行年份']}")

# ========== Part 2 ==========
part2_needed = sorted(declared_set - {"00_总档", "02_模块拆解", "01_系统结构", "03_流派设计", "04_经济循环"})
part2_hint = "、".join(part2_needed)

content2 = call_api([
    {"role": "system", "content": PART2_TEMPLATE},
    {"role": "user", "content": (
        f"上一批已完成的游戏：{game_name}。\n"
        f"上一批已产出的文件：{', '.join(p for p,_ in blocks1)}。\n"
        f"总档声明的专题列表：{declared}。\n"
        f"本批必须产出的专题（已去除上一批产物）：{part2_needed}。\n"
        f"请延续同一游戏，只产出这些专题对应的文件，末尾追加 <<<INDEX_PATCH>>>。"
    )},
], max_tokens=24000)

blocks2 = re.findall(r"<<<FILE:\s*(.+?)>>>\n(.*?)<<<END>>>", content2, re.DOTALL)
expected_part2 = len(part2_needed) + (1 if "90_结论提炼" in part2_needed else 0)
if len(blocks2) < expected_part2:
    raise RuntimeError(f"Part 2 文件块不足（预期 {expected_part2}，实际 {len(blocks2)}）。原文：{content2[:800]}")

file_blocks = blocks1 + blocks2

# ========== 综合校验 ==========
joined_paths = " ".join(p for p, _ in file_blocks)
for topic in declared_set:
    marker = "00_总档.md" if topic == "00_总档" else topic
    if marker not in joined_paths:
        raise RuntimeError(f"声明了 {topic} 但无对应文件")

PREFIX_ALLOWED = ("战斗_", "养成_", "构筑_", "社交_")
mod_files = [p for p, _ in file_blocks if p.startswith("02_模块拆解/")]
if len(mod_files) < 2:
    raise RuntimeError(f"02_模块拆解/ 至少 2 文件，实际 {len(mod_files)}")
for p in mod_files:
    fname = p.split("/", 1)[1]
    if not fname.startswith(PREFIX_ALLOWED):
        raise RuntimeError(f"02_模块拆解/ 文件名必须以 {PREFIX_ALLOWED} 之一开头：{p}")

# ========== 反向检查：所有产出文件是否都被声明 ==========
actual_topics = set()
topic_mapping = {
    "00_总档": "00_总档",
    "02_模块拆解": "02_模块拆解",
    "01_系统结构": "01_系统结构",
    "03_流派设计": "03_流派设计",
    "04_经济循环": "04_经济循环",
    "05_关卡节奏": "05_关卡节奏",
    "06_商店与奖励": "06_商店与奖励",
    "07_Boss与检定": "07_Boss与检定",
    "90_结论提炼": "90_结论提炼",
}
for path, _ in file_blocks:
    for topic_code, topic_name in topic_mapping.items():
        if topic_code in path:
            actual_topics.add(topic_code)
            break
undeclared = actual_topics - declared_set
if undeclared:
    raise RuntimeError(f"产出了未声明的文件：{undeclared}，请补充到总档『本次拆解产出专题』声明列表")

# ========== 总档系统表格对齐检查 ==========
# 从总档提取"系统总览"表格中列出的系统
toc_table_match = re.search(r"## 系统总览[^\n]*\n(.*?)(?=\n##|\Z)", toc_body, re.DOTALL)
if toc_table_match:
    toc_table = toc_table_match.group(1)
    # 从 Markdown 表格中提取第一列（系统名称）
    toc_systems = []
    for line in toc_table.splitlines():
        if "|" in line and not line.strip().startswith("|---") and not line.strip().startswith("|:-"):
            cols = [c.strip() for c in line.split("|")]
            if len(cols) >= 2 and cols[1]:  # 跳过空行和表头分隔符
                sys_name = cols[1]
                if sys_name not in ["系统", "系统名"]:  # 跳过表头
                    toc_systems.append(sys_name)

    # 检查是否所有系统都有对应的拆解文件
    missing_decomps = []
    for sys_name in toc_systems:
        # 检查是否在文件路径中提到了这个系统
        sys_found = any(sys_name in path for path, _ in file_blocks)
        if not sys_found:
            missing_decomps.append(sys_name)

    if missing_decomps:
        print(f"[警告] 总档声明的系统缺少拆解文件：{missing_decomps}（可能是表格格式问题，已记录但不阻止执行）")

# ========== 两份结论文件校验 ==========
gongshi_body = next((body for path, body in file_blocks if "底层设计公式" in path), "")
chanpin_body = next((body for path, body in file_blocks if "产品化结论" in path), "")
if not gongshi_body:
    raise RuntimeError("缺少 90_结论提炼/底层设计公式.md")
if not chanpin_body:
    raise RuntimeError("缺少 90_结论提炼/产品化结论.md")

_IF_RE = r"(?:^|\n)\s*(?:\d+[\.、)]|[-*])\s*\*?\*?If\b|(?:^|\n)\s*(?:##+)\s*结论\s*\d+|(?:^|\n)\s*If\s"

def _extract_verdicts(text, marker):
    out = []
    for line in text.splitlines():
        if marker in line:
            cleaned = line.replace("是否仍成立", "").replace("仍成立", "")
            hits = re.findall(r"(不成立|成立)", cleaned)
            if hits:
                out.append(hits[-1])
    return out

gs_if = len(re.findall(_IF_RE, gongshi_body))
if gs_if < 5:
    raise RuntimeError(f"底层设计公式.md If-Then 不足 5 条（识别 {gs_if}）")
gs_fm = _extract_verdicts(gongshi_body, "*反面测试*")
if len(gs_fm) < 5:
    raise RuntimeError(f"底层设计公式.md 反面测试行不足 5（识别 {len(gs_fm)}）")
gs_cheng = [x for x in gs_fm if x == "成立"]
if len(gs_cheng) > 2:
    raise RuntimeError(f"底层设计公式.md 有 {len(gs_cheng)} 条反面测试自评为「成立」（允许 ≤2 条充分不必要型命题，超过说明 If 选得太弱）")

gs_bad_numbers = re.findall(r"(?<![\w\[])\d+(?:\.\d+)?\s*(?:%|分钟|小时|天|次)", gongshi_body)
if len(gs_bad_numbers) > 2:
    raise RuntimeError(f"底层设计公式.md 含过多具体数字（{len(gs_bad_numbers)} 个：{gs_bad_numbers[:5]}...）。底层公式应用相对量词，不编造具体数字")

cp_if = len(re.findall(_IF_RE, chanpin_body))
if cp_if < 5:
    raise RuntimeError(f"产品化结论.md If-Then 不足 5 条（识别 {cp_if}）")
cp_prem = len(re.findall(r"\*适用前提\*", chanpin_body))
if cp_prem < 5:
    raise RuntimeError(f"产品化结论.md 适用前提行不足 5（识别 {cp_prem}）")
cp_counter = len(re.findall(r"\*反例游戏\*", chanpin_body))
if cp_counter < 5:
    raise RuntimeError(f"产品化结论.md 反例游戏行不足 5（识别 {cp_counter}）")
cp_tk = _extract_verdicts(chanpin_body, "*太宽测试*")
if len(cp_tk) < 5:
    raise RuntimeError(f"产品化结论.md 太宽测试行不足 5（识别 {len(cp_tk)}）")
cp_tk_fail = [x for x in cp_tk if x == "不成立"]
if len(cp_tk_fail) < 3:
    raise RuntimeError(f"产品化结论.md 太宽测试自评「不成立」仅 {len(cp_tk_fail)} 条（要求 ≥3，否则结论太宽）")

for cat in cats:
    if cat == "其他":
        continue
    bad_counter = re.findall(rf"\*反例游戏\*[^\n]*{re.escape(cat)}", chanpin_body)
    if bad_counter:
        raise RuntimeError(f"产品化结论.md 反例游戏疑似同品类（品类={cat}）：{bad_counter[:2]}")

def _check_tags(text: str):
    numbers = re.findall(r"(?<![\w\[])\d+(?:\.\d+)?\s*(?:%|倍|级|回合|秒|分钟|小时|天|次|连|星|个|条|格)", text)
    verified_with_source = re.findall(r"\[已验证\([^)]+\)\]", text)
    verified_bare = re.findall(r"\[已验证\](?!\()", text)
    speculated = re.findall(r"\[推测\]", text)
    return len(numbers), len(verified_with_source), len(verified_bare), len(speculated)

for path, body in file_blocks:
    if not path.endswith(".md") or "00_总档" in path:
        continue
    total, vws, vb, sp = _check_tags(body)
    if vb > 0:
        raise RuntimeError(f"{path}: 发现 {vb} 个裸 [已验证]（无括号来源），视为不合格")
    if total >= 5 and (vws + sp) / max(total, 1) < 0.6:
        raise RuntimeError(
            f"{path}: 数值溯源覆盖不足（数字 {total}，带标签 {vws+sp}，要求 ≥60%）"
        )

# ========== 目录不覆盖检查 ==========
game_dir = LIBRARY_ROOT / game_name
if game_dir.exists():
    raise RuntimeError(f"游戏目录已存在，拒绝覆盖：{game_dir}")

# ========== 写盘 ==========
written = []
for rel_path, body in file_blocks:
    rel_path = rel_path.strip()
    if ".." in rel_path or rel_path.startswith("/"):
        raise RuntimeError(f"非法相对路径：{rel_path}")
    target = game_dir / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body.strip() + "\n", encoding="utf-8")
    written.append(str(target))

# ========== 索引补丁 ==========
patch_m = re.search(r"<<<INDEX_PATCH>>>\n(.*?)<<<END>>>", content2, re.DOTALL)
if patch_m and INDEX_FILE.exists():
    patch_line = patch_m.group(1).strip()
    cols = [c.strip() for c in patch_line.strip("|").split("|")]
    if len(cols) >= 3:
        gc = cols[0]
        if not (gc.startswith("《") and gc.endswith("》")):
            gc = f"《{gc}》"
        dc = f"`research/资料/机制库/{game_name}/`"
        fc = cols[2]
        patch_line = f"| {gc} | {dc} | {fc} |"

    index_text = INDEX_FILE.read_text(encoding="utf-8")
    lines = index_text.splitlines()
    in_table = False
    last_row_idx = -1
    for i, line in enumerate(lines):
        if line.strip() == "## 游戏索引":
            in_table = True
            continue
        if in_table:
            if line.startswith("## "):
                break
            if line.startswith("|") and "---" not in line and "游戏" not in line[:10]:
                last_row_idx = i
    if last_row_idx == -1:
        raise RuntimeError("总索引未找到游戏索引表格的插入点")
    lines.insert(last_row_idx + 1, patch_line)
    INDEX_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

# ========== 原始响应归档 ==========
raw_dir = game_dir / "_raw"
raw_dir.mkdir(exist_ok=True)
stamp = date.today().isoformat()
(raw_dir / f"{stamp}_glm_part1.txt").write_text(content1, encoding="utf-8")
(raw_dir / f"{stamp}_glm_part2.txt").write_text(content2, encoding="utf-8")

# ========== 刷新多视图（扫所有游戏的 frontmatter，聚合）==========
def extract_fm(game_dir_path: Path):
    toc = game_dir_path / "00_总档.md"
    if not toc.exists():
        return None
    text = toc.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return None
    try:
        return parse_fm(m.group(1))
    except Exception:
        return None

all_games = []
for p in LIBRARY_ROOT.iterdir():
    if not p.is_dir() or p.name.startswith(".") or p.name.startswith("0") or p.name.startswith("9") or p.name.startswith("_"):
        continue
    meta = extract_fm(p)
    all_games.append((p.name, meta))

def group_by(items, key_fn):
    g = {}
    for name, meta in items:
        if not meta:
            continue
        keys = key_fn(meta)
        if not isinstance(keys, list):
            keys = [keys]
        for k in keys:
            g.setdefault(str(k), []).append(name)
    return {k: sorted(set(v)) for k, v in sorted(g.items())}

by_cat = group_by(all_games, lambda m: m.get("品类", "未分类"))
by_plat = group_by(all_games, lambda m: m.get("平台", "未分类"))
by_monet = group_by(all_games, lambda m: m.get("变现", "未分类"))
by_year = group_by(all_games, lambda m: m.get("发行年份", "未知"))
no_fm = sorted([n for n, m in all_games if not m])

def render_group(title, g):
    lines = [f"### {title}"]
    if not g:
        lines.append("- （暂无数据）")
    else:
        for k in sorted(g.keys()):
            names = "、".join(f"《{n}》" for n in g[k])
            lines.append(f"- **{k}**：{names}")
    return "\n".join(lines)

views_block = ["<!-- views:auto-generated -->",
               "## 多视图（脚本自动刷新，勿手改）",
               f"_上次刷新：{datetime.now().isoformat(timespec='seconds')}_", ""]
views_block.append(render_group("按品类视图", by_cat))
views_block.append("")
views_block.append(render_group("按平台视图", by_plat))
views_block.append("")
views_block.append(render_group("按变现视图", by_monet))
views_block.append("")
views_block.append(render_group("按发行年份视图", by_year))
if no_fm:
    views_block.append("")
    views_block.append("### 待回补 frontmatter 的游戏")
    for n in no_fm:
        views_block.append(f"- 《{n}》")
views_block.append("<!-- views:end -->")
views_text = "\n".join(views_block)

index_text = INDEX_FILE.read_text(encoding="utf-8")
if "<!-- views:auto-generated -->" in index_text and "<!-- views:end -->" in index_text:
    new_text = re.sub(
        r"<!-- views:auto-generated -->.*?<!-- views:end -->",
        views_text.replace("\\", "\\\\"),
        index_text,
        flags=re.DOTALL,
    )
else:
    new_text = index_text.rstrip() + "\n\n" + views_text + "\n"
INDEX_FILE.write_text(new_text, encoding="utf-8")

# ========== 清理 state ==========
clear_state()

print(f"\n[done] 游戏：{game_name}")
print(f"写入文件数：{len(written)}")
for w in written:
    print(f"  - {w}")
print(f"已刷新 00_总索引.md 的多视图段落（{len(all_games)} 款游戏）")
