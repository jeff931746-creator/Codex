# 玩法承接 v1.1 行为契约验证报告(SDT 三需求版,1455 真实爆款)

**日期**:2026-05-15
**样本数**:1455
**模型**:DeepSeek V4 Pro
**框架**:玩法承接 = A(反复行为) × P(成本/压力) × F(成功反馈) × N(SDT 三需求)

## 一、验证指标

| 指标 | 数值 | 阈值 | 状态 |
|---|---|---|---|
| 主 N 置信度 high 率 | 82.9% | >70% 通过 | ✅ |
| 主 N 置信度 low 率 | 0.0% | <10% 通过 | ✅ |
| 无 N 可归率 | 0.0% | <10% 通过 | ✅ |

## 二、N 基本心理需求分布(SDT 三需求)

| N | 定义 | 样本数 | 占比 |
|---|---|---|---|
| N-Comp | 胜任感(Competence) | 1089 | 74.8% |
| N-Auto | 自主性(Autonomy) | 231 | 15.9% |
| N-Rel | 归属感(Relatedness) | 135 | 9.3% |

## 三、T 任务态分布

| T | 定义 | 样本数 | 占比 |
|---|---|---|---|
| T1 | 状态调节 | 169 | 11.6% |
| T2 | 价值/能力确认 | 695 | 47.8% |
| T3 | 对象亲密 | 65 | 4.5% |
| T4 | 群体位置 | 71 | 4.9% |
| T5 | 规则理解 | 252 | 17.3% |
| T6 | 秩序掌控 | 203 | 14.0% |

## 四、N × T 交叉矩阵(行 N,列 T)

|  | T1 状态调节 | T2 价值确认 | T3 对象亲密 | T4 群体位置 | T5 规则理解 | T6 秩序掌控 | 合计 |
|---|---|---|---|---|---|---|---|
| N-Comp | 36 | 695 | 0 | 0 | 226 | 132 | 1089 |
| N-Auto | 133 | 0 | 1 | 0 | 26 | 71 | 231 |
| N-Rel | 0 | 0 | 64 | 71 | 0 | 0 | 135 |

## 五、N-Rel 内部 rel_object 分布

| rel_object | 含义 | 样本数 | 占 N-Rel 比 |
|---|---|---|---|
| virtual | 关系对象是虚拟角色/NPC/宠物 | 60 | 44.4% |
| real | 关系对象是真人 | 61 | 45.2% |
| mixed | 虚拟+真人并存 | 14 | 10.4% |
| (缺失) | n_main=N-Rel 但未标 rel_object | 0 | 0.0% |

## 六、A 反复行为分布

| A | 样本数 | 占比 |
|---|---|---|
| A1 对抗真人 | 245 | 16.8% |
| A2 克服 PVE 内容 | 427 | 29.3% |
| A3 投入累积 | 127 | 8.7% |
| A4 调整系统 | 263 | 18.1% |
| A5 探索/试错 | 293 | 20.1% |
| A6 见证内容 | 55 | 3.8% |
| A7 协同执行 | 45 | 3.1% |

## 七、F 主反馈分布

| F | 样本数 |
|---|---|
| F1 击杀反馈 | 440 |
| F2 数值膨胀 | 149 |
| F3 系统涌现 | 176 |
| F4 闭环达成 | 494 |
| F5 情感见证 | 103 |
| F6 社交认可 | 93 |

## 八、P-成本分布

| P-成本 | 样本数 |
|---|---|
| P-Rxn | 656 |
| P-Time | 947 |
| P-Cog | 868 |
| P-Soc | 261 |
| P-$ | 79 |

## 九、P-压力分布

| P-压力 | 样本数 |
|---|---|
| Pr-Lose | 802 |
| Pr-Cmp | 354 |
| Pr-Rnd | 184 |
| Pr-Sct | 312 |
| Pr-Spd | 59 |
| Pr-Low | 349 |

## 十、置信度分布

| 置信度 | 样本数 | 占比 |
|---|---|---|
| high | 1206 | 82.9% |
| medium | 249 | 17.1% |
| low | 0 | 0.0% |

## 十一、按平台 N 分布

| 平台 | N 分布 |
|---|---|
| Steam | N-Comp(642)、N-Auto(121)、N-Rel(55) |
| 微信小游戏 | N-Comp(447)、N-Auto(110)、N-Rel(80) |

## 十二、Low 置信度样本

无

## 十三、所有样本归类全表

| ID | 年份 | 平台 | 样本 | A主 | F主 | N主 | N副 | T主 | T副 | rel_object | 置信度 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2026 | Steam | 1000xRESIST Spirit | A6 | F5 | N-Rel | N-Comp | T3 | T5 | virtual | medium |
| 2 | 2026 | Steam | Abiotic Factor (1. | A4 | F3 | N-Comp | N-Rel | T6 | T4 | — | high |
| 3 | 2026 | Steam | Age of Mythology:  | A4 | F3 | N-Comp | — | T5 | T2 | — | high |
| 4 | 2026 | Steam | Anger Foot (1.0) | A2 | F1 | N-Comp | — | T1 | T2 | — | high |
| 5 | 2026 | Steam | Animal Well DLC | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 6 | 2026 | Steam | Ark 2 | A4 | F3 | N-Comp | N-Rel | T6 | T4 | — | high |
| 7 | 2026 | Steam | Avowed | A5 | F3 | N-Comp | — | T5 | T2 | — | high |
| 8 | 2026 | Steam | Balatro DLC | A5 | F3 | N-Comp | — | T5 | T1 | — | high |
| 9 | 2026 | Steam | Black Myth: Wukong | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 10 | 2026 | Steam | Blasphemous 3 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 11 | 2026 | Steam | Blue Protocol (PC) | A2 | F1 | N-Comp | N-Rel | T2 | T4 | — | medium |
| 12 | 2026 | Steam | Chrono Odyssey | A2 | F1 | N-Comp | N-Rel | T2 | T4 | — | high |
| 13 | 2026 | Steam | Cities: Skylines 2 | A4 | F3 | N-Auto | N-Comp | T6 | T1 | — | high |
| 14 | 2026 | Steam | Civilization VII | A4 | F3 | N-Comp | — | T5 | T2 | — | high |
| 15 | 2026 | Steam | Clockwork Revoluti | A5 | F3 | N-Comp | N-Auto | T5 | T6 | — | medium |
| 16 | 2026 | Steam | Crimson Desert | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 17 | 2026 | Steam | Crow Country Seque | A5 | F4 | N-Comp | — | T5 | T1 | — | high |
| 18 | 2026 | Steam | Dark and Darker (1 | A1 | F1 | N-Comp | N-Rel | T2 | T4 | — | high |
| 19 | 2026 | Steam | Dead Island 2 DLC | A2 | F1 | N-Comp | N-Auto | T1 | T2 | — | medium |
| 20 | 2026 | Steam | Deadlock (1.0) | A1 | F1 | N-Comp | — | T2 | T5 | — | high |
| 21 | 2026 | Steam | Death Stranding 2 | A7 | F4 | N-Auto | N-Rel | T6 | T1 | — | high |
| 22 | 2026 | Steam | Den of Wolves | A7 | F1 | N-Comp | N-Rel | T2 | T4 | — | high |
| 23 | 2026 | Steam | Diablo IV Expansio | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 24 | 2026 | Steam | Dragon's Dogma 2 D | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 25 | 2026 | Steam | Dune: Awakening | A1 | F6 | N-Rel | N-Comp | T4 | T2 | real | high |
| 26 | 2026 | Steam | Dwarf Fortress DLC | A4 | F3 | N-Auto | N-Comp | T6 | T5 | — | high |
| 27 | 2026 | Steam | Dying Light 2 DLC  | A5 | F1 | N-Comp | — | T2 | T1 | — | high |
| 28 | 2026 | Steam | Dyson Sphere Progr | A4 | F3 | N-Auto | N-Comp | T6 | T5 | — | high |
| 29 | 2026 | Steam | EA Sports FC 26 | A1 | F1 | N-Comp | N-Rel | T2 | T4 | — | high |
| 30 | 2026 | Steam | Earthblade | A5 | F4 | N-Comp | — | T2 | T5 | — | high |
| 31 | 2026 | Steam | Ender Lilies 2 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 32 | 2026 | Steam | Enshrouded DLC | A4 | F3 | N-Comp | N-Auto | T6 | T2 | — | medium |
| 33 | 2026 | Steam | Fable | A6 | F5 | N-Auto | N-Rel | T3 | T1 | — | medium |
| 34 | 2026 | Steam | Factorio DLC | A4 | F3 | N-Auto | N-Comp | T6 | T5 | — | high |
| 35 | 2026 | Steam | Football Manager 2 | A4 | F3 | N-Auto | N-Comp | T6 | T5 | — | high |
| 36 | 2026 | Steam | Forza Horizon 6 | A5 | F1 | N-Auto | N-Comp | T1 | T2 | — | high |
| 37 | 2026 | Steam | Frostpunk 2 DLC | A4 | F4 | N-Comp | — | T6 | T5 | — | high |
| 38 | 2026 | Steam | Ghost of Yotei | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 39 | 2026 | Steam | Ghostrunner 2 DLC | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 40 | 2026 | Steam | Grand Theft Auto V | A5 | F3 | N-Auto | N-Comp | T1 | T6 | — | high |
| 41 | 2026 | Steam | Grime 2 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 42 | 2026 | Steam | Hades II (1.0) | A2 | F3 | N-Comp | N-Rel | T2 | T3 | — | high |
| 43 | 2026 | Steam | Hell is Us | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 44 | 2026 | Steam | Hollow Knight: Sil | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 45 | 2026 | Steam | Hollowbody | A5 | F4 | N-Comp | — | T5 | T1 | — | high |
| 46 | 2026 | Steam | Homeworld 3 DLC | A4 | F3 | N-Comp | — | T6 | T5 | — | high |
| 47 | 2026 | Steam | Judas | A2 | F4 | N-Comp | N-Rel | T2 | T3 | — | medium |
| 48 | 2026 | Steam | Last Epoch Expansi | A5 | F3 | N-Comp | — | T5 | T2 | — | high |
| 49 | 2026 | Steam | Lethal Company (1. | A7 | F6 | N-Rel | N-Comp | T4 | T1 | real | high |
| 50 | 2026 | Steam | Little Nightmares  | A7 | F4 | N-Rel | N-Comp | T4 | T5 | real | high |
| 51 | 2026 | Steam | Manor Lords (1.0) | A4 | F3 | N-Comp | — | T6 | T5 | — | high |
| 52 | 2026 | Steam | Marathon | A1 | F1 | N-Comp | N-Rel | T2 | T4 | — | high |
| 53 | 2026 | Steam | Marvel's Spider-Ma | A2 | F1 | N-Comp | N-Auto | T1 | T2 | — | medium |
| 54 | 2026 | Steam | Mechabellum (1.0) | A4 | F3 | N-Comp | — | T5 | T2 | — | high |
| 55 | 2026 | Steam | Metaphor: ReFantaz | A5 | F3 | N-Comp | N-Rel | T5 | T3 | — | high |
| 56 | 2026 | Steam | Mewgenics | A5 | F3 | N-Comp | N-Rel | T5 | T3 | — | medium |
| 57 | 2026 | Steam | Monster Hunter Wil | A2 | F1 | N-Comp | N-Rel | T2 | T4 | — | high |
| 58 | 2026 | Steam | Mortal Kombat 2 | A1 | F1 | N-Comp | — | T1 | T2 | — | high |
| 59 | 2026 | Steam | NBA 2K26 | A1 | F1 | N-Comp | N-Rel | T2 | T4 | — | high |
| 60 | 2026 | Steam | Neon White 2 | A5 | F4 | N-Comp | — | T2 | T5 | — | high |
| 61 | 2026 | Steam | Nightingale (1.0) | A4 | F3 | N-Comp | N-Auto | T6 | T5 | — | high |
| 62 | 2026 | Steam | Nine Sols 2 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 63 | 2026 | Steam | Once Human (1.0) | A4 | F3 | N-Comp | N-Rel | T6 | T4 | — | high |
| 64 | 2026 | Steam | Pacific Drive 2 | A4 | F4 | N-Comp | — | T6 | T1 | — | high |
| 65 | 2026 | Steam | Path of Exile 2 (1 | A5 | F3 | N-Comp | N-Rel | T5 | T2、T4 | — | high |
| 66 | 2026 | Steam | Pax Dei (1.0) | A7 | F6 | N-Rel | N-Comp | T4 | T6 | real | high |
| 67 | 2026 | Steam | Perfect Dark | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 68 | 2026 | Steam | Phasmophobia (1.0) | A7 | F4 | N-Rel | N-Comp | T4 | T5 | real | high |
| 69 | 2026 | Steam | Project Mugen | A5 | F5 | N-Auto | N-Comp | T1 | T2 | — | medium |
| 70 | 2026 | Steam | Project Zomboid (1 | A4 | F3 | N-Comp | — | T5 | T6 | — | high |
| 71 | 2026 | Steam | Reanimal | A7 | F6 | N-Rel | N-Comp | T4 | T1 | real | high |
| 72 | 2026 | Steam | RimWorld DLC | A4 | F3 | N-Auto | N-Comp | T6 | T1 | — | medium |
| 73 | 2026 | Steam | Rise of the Ronin  | A2 | F1 | N-Comp | N-Rel | T2 | T3 | — | high |
| 74 | 2026 | Steam | Routine | A5 | F4 | N-Comp | — | T5 | T1 | — | high |
| 75 | 2026 | Steam | Satisfactory (1.0) | A4 | F3 | N-Auto | N-Comp | T6 | T5 | — | medium |
| 76 | 2026 | Steam | Sea of Stars 2 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 77 | 2026 | Steam | Selaco (1.0) | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 78 | 2026 | Steam | Sifu DLC | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 79 | 2026 | Steam | Silent Hill 2 Rema | A5 | F4 | N-Comp | N-Rel | T5 | T1、T3 | — | high |
| 80 | 2026 | Steam | Slay the Spire 2 | A5 | F3 | N-Comp | — | T5 | T2 | — | high |
| 81 | 2026 | Steam | Slitterhead | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 82 | 2026 | Steam | Spectre Divide | A1 | F6 | N-Comp | — | T2 | T5 | — | high |
| 83 | 2026 | Steam | State of Decay 3 | A3 | F4 | N-Comp | — | T6 | T2 | — | high |
| 84 | 2026 | Steam | Stellar Blade (PC) | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 85 | 2026 | Steam | Stormgate | A1 | F6 | N-Comp | — | T2 | T5 | — | high |
| 86 | 2026 | Steam | Tekken 9 | A1 | F1 | N-Comp | — | T2 | T5 | — | high |
| 87 | 2026 | Steam | Tevi Sequel | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 88 | 2026 | Steam | The Finals Season  | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 89 | 2026 | Steam | The Last of Us Par | A2 | F5 | N-Rel | N-Comp | T3 | T2 | virtual | high |
| 90 | 2026 | Steam | The Outer Worlds 2 | A6 | F5 | N-Auto | N-Comp | T1 | T5 | — | medium |
| 91 | 2026 | Steam | The Wolf Among Us  | A6 | F5 | N-Auto | N-Comp | T1 | T5 | — | medium |
| 92 | 2026 | Steam | Total War: Star Wa | A4 | F4 | N-Comp | — | T6 | T2 | — | high |
| 93 | 2026 | Steam | Vampire: The Masqu | A6 | F5 | N-Auto | N-Comp | T1 | T5 | — | medium |
| 94 | 2026 | Steam | Warframe 1999 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 95 | 2026 | Steam | Where the Water Ta | A6 | F5 | N-Auto | — | T1 | — | — | high |
| 96 | 2026 | Steam | Wreckfest 2 | A1 | F1 | N-Comp | — | T1 | T2 | — | high |
| 97 | 2026 | Steam | Zero Space | A4 | F4 | N-Comp | — | T2 | T5 | — | high |
| 98 | 2025 | Steam | S&box | A4 | F3 | N-Auto | N-Comp | T6 | T1 | — | high |
| 99 | 2025 | Steam | Unrecord | A2 | F4 | N-Comp | — | T2 | T5 | — | high |
| 100 | 2025 | Steam | 七日世界 大型更新 | A3 | F4 | N-Comp | — | T6 | T2 | — | high |
| 101 | 2025 | Steam | 三角洲行动 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 102 | 2025 | Steam | 上古卷轴4：湮灭重制版 | A5 | F4 | N-Auto | N-Comp | T1 | T6 | — | high |
| 103 | 2025 | Steam | 严阵以待 大型更新 | A7 | F4 | N-Comp | — | T2 | T5 | — | high |
| 104 | 2025 | Steam | 光与影：33号远征队 | A2 | F4 | N-Comp | N-Rel | T2 | T5 | — | high |
| 105 | 2025 | Steam | 光明破坏者 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 106 | 2025 | Steam | 冰汽时代2 大型更新 | A4 | F4 | N-Comp | — | T6 | T5 | — | high |
| 107 | 2025 | Steam | 刺客信条：影 | A2 | F4 | N-Auto | N-Comp | T1 | T6 | — | high |
| 108 | 2025 | Steam | 动物井 DLC | A5 | F4 | N-Auto | N-Comp | T5 | T1 | — | high |
| 109 | 2025 | Steam | 午夜之南 | A2 | F4 | N-Comp | — | T2 | T1 | — | high |
| 110 | 2025 | Steam | 博德之门3 MOD更新 | A2 | F4 | N-Comp | N-Rel | T2 | T5 | — | high |
| 111 | 2025 | Steam | 原神 Steam版 | A2 | F2 | N-Comp | N-Rel | T2 | T3 | — | high |
| 112 | 2025 | Steam | 双点博物馆 | A4 | F3 | N-Auto | N-Comp | T6 | T1 | — | high |
| 113 | 2025 | Steam | 发条革命 | A2 | F4 | N-Comp | — | T2 | T5 | — | high |
| 114 | 2025 | Steam | 合金装备Δ：食蛇者 | A2 | F4 | N-Comp | — | T2 | T5 | — | high |
| 115 | 2025 | Steam | 吸血鬼幸存者 DLC | A2 | F1 | N-Comp | — | T1 | T2 | — | high |
| 116 | 2025 | Steam | 命运2 新章节 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 117 | 2025 | Steam | 咩咩启示录 DLC | A2 | F4 | N-Comp | N-Auto | T2 | T6 | — | high |
| 118 | 2025 | Steam | 哈迪斯2 | A2 | F1 | N-Comp | N-Rel | T2 | T1 | — | high |
| 119 | 2025 | Steam | 夜莺1.0 | A4 | F4 | N-Comp | N-Auto | T6 | T2 | — | high |
| 120 | 2025 | Steam | 天国：拯救2 | A2 | F4 | N-Comp | — | T2 | T5 | — | high |
| 121 | 2025 | Steam | 天外世界2 | A2 | F4 | N-Comp | N-Auto | T2 | T5 | — | high |
| 122 | 2025 | Steam | 失落之魂 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 123 | 2025 | Steam | 夺宝奇兵：古老之圈 | A5 | F4 | N-Comp | N-Auto | T5 | T2 | — | high |
| 124 | 2025 | Steam | 如龙8外传：夏威夷海盗 | A2 | F1 | N-Comp | N-Rel | T2 | T1 | — | high |
| 125 | 2025 | Steam | 完美黑暗 | A2 | F4 | N-Comp | — | T2 | T5 | — | high |
| 126 | 2025 | Steam | 宣誓 | A2 | F4 | N-Comp | N-Auto | T2 | T5 | — | high |
| 127 | 2025 | Steam | 小人物大世界1.0 | A4 | F4 | N-Comp | N-Auto | T6 | T2 | — | high |
| 128 | 2025 | Steam | 小小梦魇3 | A5 | F4 | N-Comp | N-Rel | T5 | T4 | — | medium |
| 129 | 2025 | Steam | 小马岛2 | A5 | F4 | N-Comp | — | T5 | — | — | high |
| 130 | 2025 | Steam | 尘白禁区 大型更新 | A2 | F1 | N-Comp | N-Rel | T2 | T1 | — | high |
| 131 | 2025 | Steam | 崩坏：星穹铁道 Steam版 | A2 | F4 | N-Comp | N-Rel | T2 | T5 | — | high |
| 132 | 2025 | Steam | 帝国神话1.0 | A4 | F4 | N-Comp | N-Rel | T6 | T4 | — | high |
| 133 | 2025 | Steam | 幸福工厂1.0 | A4 | F3 | N-Auto | N-Comp | T6 | T5 | — | high |
| 134 | 2025 | Steam | 幻兽帕鲁 DLC | A4 | F3 | N-Comp | N-Auto | T6 | T2 | — | high |
| 135 | 2025 | Steam | 庄园领主 大型更新 | A4 | F3 | N-Comp | N-Auto | T6 | T2 | — | high |
| 136 | 2025 | Steam | 异星工厂：太空时代 | A4 | F3 | N-Auto | N-Comp | T6 | T5 | — | high |
| 137 | 2025 | Steam | 异环 | A2 | F4 | N-Comp | N-Auto | T2 | T5 | — | high |
| 138 | 2025 | Steam | 心灵杀手2 DLC | A2 | F4 | N-Comp | — | T2 | T5 | — | high |
| 139 | 2025 | Steam | 忍者龙剑传：怒之羁绊 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 140 | 2025 | Steam | 忍：复仇之刃 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 141 | 2025 | Steam | 怪物猎人：荒野 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 142 | 2025 | Steam | 恐怖黎明2 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 143 | 2025 | Steam | 战锤40K：星际战士2 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 144 | 2025 | Steam | 戴森球计划 大型更新 | A4 | F3 | N-Auto | N-Comp | T6 | T5 | — | high |
| 145 | 2025 | Steam | 文明7 | A4 | F3 | N-Comp | N-Auto | T6 | T5 | — | high |
| 146 | 2025 | Steam | 方舟2 | A2 | F4 | N-Comp | N-Auto | T2 | T6 | — | high |
| 147 | 2025 | Steam | 无主之地4 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 148 | 2025 | Steam | 无限暖暖 | A5 | F5 | N-Auto | N-Rel | T1 | T3 | — | medium |
| 149 | 2025 | Steam | 时空英豪2 | A5 | F4 | N-Comp | — | T2 | T5 | — | high |
| 150 | 2025 | Steam | 明日方舟：终末地 | A4 | F3 | N-Comp | N-Rel | T6 | T5、T3 | — | medium |
| 151 | 2025 | Steam | 明末：渊虚之羽 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 152 | 2025 | Steam | 星际战甲1999 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 153 | 2025 | Steam | 暗区突围：无限 | A1 | F4 | N-Comp | — | T2 | T1 | — | high |
| 154 | 2025 | Steam | 暗黑地牢2 DLC | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 155 | 2025 | Steam | 杀戮空间3 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 156 | 2025 | Steam | 杀手：血钱复出 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 157 | 2025 | Steam | 森林之子1.0 | A4 | F4 | N-Comp | N-Auto | T6 | T2 | — | high |
| 158 | 2025 | Steam | 死亡搁浅2 | A7 | F4 | N-Rel | N-Auto | T4 | T6、T1 | mixed | medium |
| 159 | 2025 | Steam | 毁灭战士：黑暗时代 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 160 | 2025 | Steam | 永劫无间2 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 161 | 2025 | Steam | 泰坦之旅2 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 162 | 2025 | Steam | 流放之路2 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 163 | 2025 | Steam | 浪人崛起PC版 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 164 | 2025 | Steam | 渎神2 DLC | A2 | F4 | N-Comp | — | T2 | T5 | — | high |
| 165 | 2025 | Steam | 渔帆暗影2 | A5 | F4 | N-Comp | N-Auto | T6 | T1 | — | medium |
| 166 | 2025 | Steam | 漫威争锋 | A1 | F1 | N-Comp | — | T2 | T4 | — | high |
| 167 | 2025 | Steam | 漫威蜘蛛侠2 PC版 | A2 | F1 | N-Auto | N-Comp | T1 | T2 | — | medium |
| 168 | 2025 | Steam | 潜行者2 大型更新 | A5 | F4 | N-Comp | — | T6 | T2 | — | high |
| 169 | 2025 | Steam | 燃灯者 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 170 | 2025 | Steam | 燕云十六声 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 171 | 2025 | Steam | 猎杀：对决 大型更新 | A1 | F4 | N-Comp | — | T2 | T4 | — | high |
| 172 | 2025 | Steam | 白夜极光 PC版 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 173 | 2025 | Steam | 百英雄传 DLC | A2 | F4 | N-Comp | — | T2 | T5 | — | high |
| 174 | 2025 | Steam | 神之亵渎2 DLC | A2 | F4 | N-Comp | — | T2 | T5 | — | high |
| 175 | 2025 | Steam | 神之浩劫2 | A1 | F1 | N-Comp | — | T2 | T4 | — | high |
| 176 | 2025 | Steam | 神话时代：重述版 | A1 | F1 | N-Comp | — | T2 | T5、T6 | — | high |
| 177 | 2025 | Steam | 神鬼寓言 | A5 | F5 | N-Auto | N-Comp | T1 | T2 | — | medium |
| 178 | 2025 | Steam | 空洞骑士：丝之歌 | A2 | F4 | N-Comp | — | T2 | T5 | — | high |
| 179 | 2025 | Steam | 第一后裔 大型更新 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 180 | 2025 | Steam | 绝区零 Steam版 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 181 | 2025 | Steam | 绝地潜兵2 大型DLC | A7 | F1 | N-Comp | N-Rel | T2 | T4 | — | high |
| 182 | 2025 | Steam | 罪恶装备：奋战 DLC | A1 | F1 | N-Comp | — | T2 | T5 | — | high |
| 183 | 2025 | Steam | 羊蹄山之魂 | A2 | F1 | N-Comp | N-Auto | T2 | T1 | — | high |
| 184 | 2025 | Steam | 腐朽之都3 | A4 | F4 | N-Comp | N-Auto | T6 | T2 | — | medium |
| 185 | 2025 | Steam | 蓝色星原：旅谣 | A5 | F5 | N-Auto | N-Rel | T1 | T3 | — | medium |
| 186 | 2025 | Steam | 街头霸王6 DLC | A1 | F1 | N-Comp | — | T2 | T5 | — | high |
| 187 | 2025 | Steam | 解限机 | A1 | F1 | N-Comp | — | T2 | T5 | — | high |
| 188 | 2025 | Steam | 边缘世界 DLC | A4 | F3 | N-Comp | N-Auto | T6 | T5 | — | high |
| 189 | 2025 | Steam | 远星物语 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 190 | 2025 | Steam | 逆水寒手游PC版 | A3 | F6 | N-Rel | N-Comp | T4 | T2、T3 | mixed | high |
| 191 | 2025 | Steam | 铁拳8 DLC | A1 | F1 | N-Comp | — | T2 | T5 | — | high |
| 192 | 2025 | Steam | 铁锈风云 | A4 | F1 | N-Comp | — | T6 | T2 | — | high |
| 193 | 2025 | Steam | 零之领域 | A1 | F1 | N-Comp | N-Rel | T2 | T4 | — | high |
| 194 | 2025 | Steam | 雾锁王国1.0 | A2 | F1 | N-Comp | N-Auto | T2 | T6 | — | high |
| 195 | 2025 | Steam | 非生物因素1.0 | A5 | F4 | N-Comp | — | T6 | T5 | — | high |
| 196 | 2025 | Steam | 风暴之城 DLC | A4 | F3 | N-Comp | — | T6 | T5 | — | high |
| 197 | 2025 | Steam | 风暴之门 | A4 | F1 | N-Comp | — | T2 | T6 | — | high |
| 198 | 2025 | Steam | 风起云涌 | A7 | F1 | N-Comp | N-Rel | T2 | T4 | — | high |
| 199 | 2025 | Steam | 鸣潮 Steam版 | A2 | F1 | N-Comp | N-Rel | T2 | T1、T3 | — | high |
| 200 | 2025 | Steam | 黑神话：悟空 DLC | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 201 | 2025 | Steam | 龙之信条2 DLC | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 202 | 2024 | Steam | F1 24 | A4 | F4 | N-Comp | — | T2 | T5 | — | high |
| 203 | 2024 | Steam | NBA 2K25 | A1 | F6 | N-Comp | — | T2 | T4 | — | high |
| 204 | 2024 | Steam | No More Room in He | A7 | F4 | N-Comp | N-Rel | T2 | T4 | — | medium |
| 205 | 2024 | Steam | WRC 24 | A4 | F4 | N-Comp | — | T2 | T5 | — | high |
| 206 | 2024 | Steam | 一千个抵抗 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 207 | 2024 | Steam | 七日世界 | A3 | F2 | N-Comp | N-Rel | T6 | T4 | — | medium |
| 208 | 2024 | Steam | 乌鸦国 | A4 | F4 | N-Comp | — | T6 | T5 | — | high |
| 209 | 2024 | Steam | 众生之门 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 210 | 2024 | Steam | 像素神话 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 211 | 2024 | Steam | 内容警告 | A7 | F6 | N-Rel | N-Comp | T4 | T1 | real | high |
| 212 | 2024 | Steam | 冰汽时代2 | A4 | F4 | N-Comp | — | T6 | T5 | — | high |
| 213 | 2024 | Steam | 动物井 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 214 | 2024 | Steam | 勇气之剑 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 215 | 2024 | Steam | 勇者斗恶龙怪物篇3 | A3 | F2 | N-Comp | — | T2 | T5 | — | high |
| 216 | 2024 | Steam | 命运2：终焉之形 | A2 | F1 | N-Comp | N-Rel | T2 | T4 | — | high |
| 217 | 2024 | Steam | 咒语浪人 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 218 | 2024 | Steam | 圣兽之王 | A4 | F4 | N-Comp | — | T5 | T2 | — | high |
| 219 | 2024 | Steam | 圣歌德嘉的晚钟 | A5 | F5 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 220 | 2024 | Steam | 地心护核者1.0 | A4 | F4 | N-Comp | N-Auto | T6 | T1 | — | medium |
| 221 | 2024 | Steam | 地狱之刃2：塞娜的史诗 | A2 | F4 | N-Comp | N-Rel | T2 | T3 | — | high |
| 222 | 2024 | Steam | 太平洋驾驶 | A2 | F4 | N-Comp | — | T2 | T6 | — | high |
| 223 | 2024 | Steam | 太阳避难所 | A4 | F4 | N-Comp | — | T6 | T2 | — | high |
| 224 | 2024 | Steam | 女神异闻录3 Reload | A2 | F5 | N-Rel | N-Comp | T3 | T2 | virtual | high |
| 225 | 2024 | Steam | 如龙8 | A2 | F1 | N-Comp | N-Rel | T2 | T1、T3 | — | high |
| 226 | 2024 | Steam | 寂静岭2 | A5 | F4 | N-Comp | N-Rel | T5 | T1、T3 | — | high |
| 227 | 2024 | Steam | 小丑牌 | A5 | F3 | N-Comp | — | T5 | T2 | — | high |
| 228 | 2024 | Steam | 尘封大陆 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 229 | 2024 | Steam | 师父 DLC | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 230 | 2024 | Steam | 帝国时代2：罗马归来 | A1 | F4 | N-Comp | — | T2 | T5 | — | high |
| 231 | 2024 | Steam | 帝国神话 | A4 | F4 | N-Comp | N-Rel | T6 | T4、T2 | — | high |
| 232 | 2024 | Steam | 幻兽帕鲁 | A4 | F3 | N-Comp | N-Auto | T6 | T2、T1 | — | high |
| 233 | 2024 | Steam | 幻日夜羽 | A2 | F1 | N-Comp | N-Rel | T2 | T3 | — | high |
| 234 | 2024 | Steam | 庄园领主 | A4 | F3 | N-Comp | — | T6 | T2 | — | high |
| 235 | 2024 | Steam | 异星工厂2.0 | A4 | F3 | N-Comp | N-Auto | T6 | T5 | — | high |
| 236 | 2024 | Steam | 恐鬼症1.0 | A5 | F4 | N-Comp | N-Rel | T5 | T1、T4 | — | high |
| 237 | 2024 | Steam | 恶意不息 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 238 | 2024 | Steam | 恶魔轮盘 | A1 | F4 | N-Comp | — | T5 | T2 | — | high |
| 239 | 2024 | Steam | 拉力赛艺术 | A2 | F4 | N-Comp | — | T2 | T1 | — | high |
| 240 | 2024 | Steam | 星球大战：法外狂徒 | A5 | F4 | N-Comp | N-Rel | T2 | T3 | — | high |
| 241 | 2024 | Steam | 星际角斗场 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 242 | 2024 | Steam | 星露谷物语1.6 | A4 | F2 | N-Auto | N-Comp | T6 | T1 | — | high |
| 243 | 2024 | Steam | 暗喻幻想 | A2 | F4 | N-Comp | — | T5 | T2 | — | high |
| 244 | 2024 | Steam | 暗黑破坏神4：憎恶之躯 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 245 | 2024 | Steam | 最终幻想14：黄金的遗产 | A7 | F4 | N-Comp | N-Rel | T2 | T4 | — | high |
| 246 | 2024 | Steam | 机车狂欢 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 247 | 2024 | Steam | 死亡教堂 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 248 | 2024 | Steam | 浪漫沙加2：七英雄的复仇 | A2 | F4 | N-Comp | — | T5 | T2 | — | high |
| 249 | 2024 | Steam | 深岩银河：幸存者 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 250 | 2024 | Steam | 深空梦里人2 | A5 | F5 | N-Comp | N-Rel | T5 | T3 | — | medium |
| 251 | 2024 | Steam | 潜水员戴夫 DLC | A3 | F2 | N-Auto | N-Comp | T6 | T1 | — | high |
| 252 | 2024 | Steam | 火山冒险 | A2 | F4 | N-Comp | — | T2 | T5 | — | high |
| 253 | 2024 | Steam | 火山女儿 | A3 | F2 | N-Comp | N-Rel | T2 | T3 | — | medium |
| 254 | 2024 | Steam | 灵魂面甲 | A4 | F4 | N-Comp | N-Auto | T6 | T2 | — | medium |
| 255 | 2024 | Steam | 燧石枪：黎明之围 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 256 | 2024 | Steam | 狂野星球之旅 | A5 | F4 | N-Auto | N-Rel | T1 | T4 | — | medium |
| 257 | 2024 | Steam | 猎杀：对决1896 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 258 | 2024 | Steam | 百英雄传 | A2 | F4 | N-Comp | — | T5 | T2 | — | high |
| 259 | 2024 | Steam | 真女神转生5：复仇 | A2 | F4 | N-Comp | — | T5 | T2 | — | high |
| 260 | 2024 | Steam | 真知之岛 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 261 | 2024 | Steam | 碧海黑帆 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 262 | 2024 | Steam | 碧蓝幻想：Relink | A2 | F1 | N-Comp | N-Rel | T2 | T4 | — | high |
| 263 | 2024 | Steam | 祇：女神之道 | A4 | F4 | N-Comp | — | T6 | T2 | — | high |
| 264 | 2024 | Steam | 第一后裔 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 265 | 2024 | Steam | 纸境奇缘 | A2 | F4 | N-Comp | — | T5 | T2 | — | high |
| 266 | 2024 | Steam | 绝命游卡 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 267 | 2024 | Steam | 绝地潜兵2 | A7 | F1 | N-Comp | N-Rel | T2 | T4 | — | high |
| 268 | 2024 | Steam | 绝境反击 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 269 | 2024 | Steam | 绝境重启 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 270 | 2024 | Steam | 绝影战士 | A2 | F1 | N-Comp | — | T2 | — | — | high |
| 271 | 2024 | Steam | 羊肚菌 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 272 | 2024 | Steam | 肉鸽之魂 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 273 | 2024 | Steam | 致命公司 | A7 | F4 | N-Rel | N-Comp | T4 | T1 | real | high |
| 274 | 2024 | Steam | 艾尔登法环：黄金树幽影 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 275 | 2024 | Steam | 艾诺提亚：失落之歌 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 276 | 2024 | Steam | 节奏医生 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 277 | 2024 | Steam | 蟹蟹寻宝奇遇 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 278 | 2024 | Steam | 诺科 | A6 | F5 | N-Auto | N-Comp | T1 | T5 | — | medium |
| 279 | 2024 | Steam | 辐射4次世代更新 | A5 | F4 | N-Auto | N-Comp | T1 | T6 | — | high |
| 280 | 2024 | Steam | 边缘世界：异常 | A4 | F4 | N-Comp | — | T6 | T5 | — | high |
| 281 | 2024 | Steam | 逆转裁判456 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 282 | 2024 | Steam | 铁拳8 | A1 | F1 | N-Comp | — | T2 | T5 | — | high |
| 283 | 2024 | Steam | 铃兰之剑 | A2 | F4 | N-Comp | — | T2 | T5 | — | high |
| 284 | 2024 | Steam | 银河破裂者 | A4 | F4 | N-Comp | — | T6 | T2 | — | high |
| 285 | 2024 | Steam | 风暴之城 | A4 | F4 | N-Comp | — | T6 | T5 | — | high |
| 286 | 2024 | Steam | 驱灵者：新伊甸的幽灵 | A2 | F4 | N-Comp | N-Rel | T2 | T3 | — | medium |
| 287 | 2024 | Steam | 魔法餐作室 | A4 | F3 | N-Comp | N-Auto | T6 | T1 | — | medium |
| 288 | 2024 | Steam | 鸣潮 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 289 | 2024 | Steam | 黑神话：悟空 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 290 | 2024 | Steam | 龙之信条2 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 291 | 2024 | Steam | 龙珠Z：卡卡罗特 DLC6 | A2 | F1 | N-Comp | N-Rel | T2 | T3 | — | medium |
| 292 | 2024 | Steam | 龙腾世纪4：影障守护者 | A2 | F4 | N-Comp | N-Rel | T2 | T3 | — | medium |
| 293 | 2023 | Steam | EA Sports FC 24 | A1 | F1 | N-Comp | — | T2 | T4 | — | high |
| 294 | 2023 | Steam | F1 23 | A1 | F1 | N-Comp | — | T2 | T5 | — | high |
| 295 | 2023 | Steam | NBA 2K24 | A1 | F1 | N-Comp | — | T2 | T4 | — | high |
| 296 | 2023 | Steam | WWE 2K23 | A1 | F1 | N-Comp | — | T2 | T3 | — | high |
| 297 | 2023 | Steam | 三位一体5 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 298 | 2023 | Steam | 严酷考验 | A2 | F4 | N-Comp | — | T2 | T1 | — | high |
| 299 | 2023 | Steam | 严阵以待 | A7 | F4 | N-Comp | N-Rel | T2 | T4 | — | medium |
| 300 | 2023 | Steam | 人类 | A5 | F4 | N-Comp | — | T5 | T6 | — | high |
| 301 | 2023 | Steam | 使命召唤：现代战争3 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 302 | 2023 | Steam | 全面战争：法老 | A4 | F4 | N-Comp | N-Auto | T6 | T5 | — | high |
| 303 | 2023 | Steam | 刺客信条：幻景 | A2 | F4 | N-Comp | — | T2 | T5 | — | high |
| 304 | 2023 | Steam | 匹诺曹的谎言 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 305 | 2023 | Steam | 博尔特枪 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 306 | 2023 | Steam | 博德之门3 | A5 | F4 | N-Comp | N-Rel | T5 | T3 | — | high |
| 307 | 2023 | Steam | 卧龙：苍天陨落 | A2 | F1 | N-Comp | — | T2 | — | — | high |
| 308 | 2023 | Steam | 原始袭变 | A7 | F1 | N-Comp | — | T2 | T1 | — | high |
| 309 | 2023 | Steam | 原子之心 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 310 | 2023 | Steam | 反恐精英2 | A1 | F1 | N-Comp | — | T2 | — | — | high |
| 311 | 2023 | Steam | 取景器 | A5 | F4 | N-Auto | N-Comp | T5 | T1 | — | high |
| 312 | 2023 | Steam | 命运2：光陨之秋 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 313 | 2023 | Steam | 地平线：西之绝境 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 314 | 2023 | Steam | 坎巴拉太空计划2 | A5 | F3 | N-Comp | N-Auto | T5 | T6 | — | high |
| 315 | 2023 | Steam | 埃尔帕索，别处 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 316 | 2023 | Steam | 城市天际线2 | A4 | F3 | N-Auto | N-Comp | T6 | T1 | — | high |
| 317 | 2023 | Steam | 堕落之主 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 318 | 2023 | Steam | 塔洛斯的法则2 | A5 | F4 | N-Auto | N-Comp | T5 | T1 | — | high |
| 319 | 2023 | Steam | 大地之爱 | A4 | F3 | N-Auto | N-Comp | T6 | T1 | — | high |
| 320 | 2023 | Steam | 失忆症：地堡 | A5 | F4 | N-Comp | — | T5 | T1 | — | high |
| 321 | 2023 | Steam | 奇娅 | A5 | F4 | N-Auto | — | T1 | T6 | — | high |
| 322 | 2023 | Steam | 女神异闻录3 携带版 | A2 | F4 | N-Comp | N-Rel | T2 | T3 | — | high |
| 323 | 2023 | Steam | 女神异闻录5 战略版 | A4 | F4 | N-Comp | — | T5 | T2 | — | high |
| 324 | 2023 | Steam | 如龙7外传 | A2 | F1 | N-Comp | N-Rel | T2 | T1 | — | high |
| 325 | 2023 | Steam | 如龙：维新！极 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 326 | 2023 | Steam | 守望先锋2 | A1 | F1 | N-Comp | N-Rel | T2 | T4 | — | high |
| 327 | 2023 | Steam | 完美音浪 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 328 | 2023 | Steam | 寻路者 | A2 | F2 | N-Comp | — | T2 | T1 | — | high |
| 329 | 2023 | Steam | 帝国时代4：苏丹崛起 | A4 | F4 | N-Comp | — | T6 | T5 | — | high |
| 330 | 2023 | Steam | 幽灵行者2 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 331 | 2023 | Steam | 心灵杀手2 | A6 | F5 | N-Rel | N-Auto | T3 | T5 | virtual | high |
| 332 | 2023 | Steam | 战律2 | A4 | F4 | N-Comp | N-Auto | T5 | T6 | — | high |
| 333 | 2023 | Steam | 战锤40K：行商浪人 | A5 | F4 | N-Comp | N-Rel | T5 | T2 | — | high |
| 334 | 2023 | Steam | 收获日3 | A7 | F4 | N-Comp | N-Rel | T2 | T4 | — | high |
| 335 | 2023 | Steam | 方舟：生存飞升 | A3 | F2 | N-Comp | N-Rel | T6 | T2 | — | high |
| 336 | 2023 | Steam | 无敌号 | A6 | F5 | N-Rel | N-Auto | T3 | T1 | virtual | high |
| 337 | 2023 | Steam | 星之海 | A2 | F4 | N-Comp | N-Rel | T2 | T3 | — | high |
| 338 | 2023 | Steam | 星之海洋2：第二个故事R | A2 | F1 | N-Comp | N-Rel | T2 | T3 | — | high |
| 339 | 2023 | Steam | 星空 | A5 | F4 | N-Auto | N-Comp、N-Rel | T6 | T1、T3 | — | medium |
| 340 | 2023 | Steam | 星际迷航：复苏 | A6 | F5 | N-Rel | N-Auto | T3 | T1 | virtual | high |
| 341 | 2023 | Steam | 暗黑地牢2 | A2 | F4 | N-Comp | — | T5 | T2 | — | high |
| 342 | 2023 | Steam | 暗黑破坏神4 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 343 | 2023 | Steam | 月石岛 | A5 | F3 | N-Auto | N-Comp | T1 | T5 | — | medium |
| 344 | 2023 | Steam | 机械战警：暴戾都市 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 345 | 2023 | Steam | 极限竞速 | A4 | F4 | N-Comp | — | T2 | T5 | — | high |
| 346 | 2023 | Steam | 森林之子 | A4 | F3 | N-Auto | N-Comp | T6 | T1 | — | medium |
| 347 | 2023 | Steam | 歧路旅人2 | A2 | F4 | N-Comp | N-Rel | T2 | T3 | — | high |
| 348 | 2023 | Steam | 死亡回归 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 349 | 2023 | Steam | 沙石镇时光 | A4 | F3 | N-Auto | N-Rel | T6 | T3 | — | high |
| 350 | 2023 | Steam | 洛克人EXE合集 | A5 | F3 | N-Comp | — | T5 | T2 | — | high |
| 351 | 2023 | Steam | 浩劫前夕 | A2 | F1 | N-Comp | — | T2 | T1 | — | medium |
| 352 | 2023 | Steam | 渔帆暗礁 | A5 | F3 | N-Auto | N-Comp | T1 | T6 | — | high |
| 353 | 2023 | Steam | 潜水员戴夫 | A4 | F3 | N-Auto | N-Comp | T6 | T1 | — | high |
| 354 | 2023 | Steam | 狂野之心 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 355 | 2023 | Steam | 珊瑚岛 | A4 | F3 | N-Auto | N-Rel | T6 | T3 | — | high |
| 356 | 2023 | Steam | 瑞奇与叮当：时空跳转 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 357 | 2023 | Steam | 生化危机4重制版 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 358 | 2023 | Steam | 神之亵渎2 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 359 | 2023 | Steam | 系统休克 | A2 | F4 | N-Comp | — | T5 | T2 | — | high |
| 360 | 2023 | Steam | 红霞岛 | A2 | F1 | N-Comp | — | T2 | T4 | — | medium |
| 361 | 2023 | Steam | 英雄传说：黎之轨迹2 | A6 | F5 | N-Rel | N-Comp | T3 | T1 | virtual | high |
| 362 | 2023 | Steam | 英雄连3 | A1 | F4 | N-Comp | — | T2 | T5 | — | high |
| 363 | 2023 | Steam | 茧 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | high |
| 364 | 2023 | Steam | 莱莎的炼金工房3 | A4 | F3 | N-Auto | N-Rel、N-Comp | T6 | T3、T1 | — | medium |
| 365 | 2023 | Steam | 街头霸王6 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 366 | 2023 | Steam | 装甲核心6 | A4 | F4 | N-Comp | — | T2 | T5、T6 | — | high |
| 367 | 2023 | Steam | 赛博朋克2077：往日之影 | A6 | F5 | N-Rel | N-Comp | T3 | T1、T2 | virtual | high |
| 368 | 2023 | Steam | 足球经理2024 | A4 | F3 | N-Auto | N-Comp | T6 | T5 | — | medium |
| 369 | 2023 | Steam | 遗迹2 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 370 | 2023 | Steam | 铁血联盟3 | A4 | F4 | N-Comp | — | T5 | T6、T2 | — | high |
| 371 | 2023 | Steam | 阿凡达：潘多拉边境 | A5 | F5 | N-Auto | N-Rel | T1 | T3 | — | medium |
| 372 | 2023 | Steam | 霍格沃茨之遗 | A5 | F5 | N-Auto | N-Rel、N-Comp | T1 | T3、T2 | — | medium |
| 373 | 2023 | Steam | 飙酷车神：极乐狂欢 | A5 | F2 | N-Auto | N-Comp | T1 | T2 | — | high |
| 374 | 2023 | Steam | 魔咒之地 | A5 | F1 | N-Auto | N-Comp | T1 | T2 | — | medium |
| 375 | 2023 | Steam | 魔女之泉R | A3 | F2 | N-Auto | N-Rel、N-Comp | T1 | T3 | — | medium |
| 376 | 2021 | Steam | 12 Minutes | A5 | F4 | N-Comp | — | T5 | T1 | — | high |
| 377 | 2021 | Steam | Age of Empires IV | A1 | F4 | N-Comp | — | T2 | T5、T6 | — | high |
| 378 | 2021 | Steam | Alex Kidd in Mirac | A2 | F4 | N-Comp | — | T2 | T1 | — | high |
| 379 | 2021 | Steam | Art of Rally | A4 | F2 | N-Auto | N-Comp | T1 | T6 | — | medium |
| 380 | 2021 | Steam | Axiom Verge 2 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | high |
| 381 | 2021 | Steam | Back 4 Blood | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 382 | 2021 | Steam | Battlefield 2042 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 383 | 2021 | Steam | Before Your Eyes | A6 | F5 | N-Rel | N-Auto | T3 | T1 | virtual | high |
| 384 | 2021 | Steam | Black Book | A5 | F4 | N-Comp | N-Rel | T5 | T3 | — | medium |
| 385 | 2021 | Steam | Bonfire Peaks | A4 | F4 | N-Comp | N-Auto | T5 | T6 | — | high |
| 386 | 2021 | Steam | Boomerang X | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 387 | 2021 | Steam | Bright Memory: Inf | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 388 | 2021 | Steam | Chernobylite | A3 | F4 | N-Comp | — | T6 | T2 | — | high |
| 389 | 2021 | Steam | Chicory: A Colorfu | A5 | F4 | N-Auto | N-Comp | T1 | T5 | — | medium |
| 390 | 2021 | Steam | Cris Tales | A2 | F4 | N-Comp | — | T5 | T2 | — | high |
| 391 | 2021 | Steam | Curse of the Dead  | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 392 | 2021 | Steam | Death Stranding: D | A4 | F4 | N-Auto | N-Rel | T6 | T3 | — | medium |
| 393 | 2021 | Steam | Death Trash | A5 | F5 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 394 | 2021 | Steam | Death's Door | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 395 | 2021 | Steam | Disco Elysium: The | A5 | F5 | N-Auto | N-Comp | T5 | T1 | — | medium |
| 396 | 2021 | Steam | Doki Doki Literatu | A6 | F5 | N-Rel | N-Auto | T3 | T1 | virtual | high |
| 397 | 2021 | Steam | Dorfromantik | A4 | F3 | N-Auto | N-Comp | T6 | T1 | — | high |
| 398 | 2021 | Steam | Dyson Sphere Progr | A4 | F3 | N-Comp | N-Auto | T6 | T5 | — | high |
| 399 | 2021 | Steam | Eastward | A5 | F4 | N-Auto | N-Comp | T1 | T5 | — | medium |
| 400 | 2021 | Steam | Echo Generation | A2 | F4 | N-Comp | — | T2 | T5 | — | high |
| 401 | 2021 | Steam | Eldest Souls | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 402 | 2021 | Steam | Everhood | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 403 | 2021 | Steam | F1 2021 | A4 | F4 | N-Comp | — | T2 | T5 | — | high |
| 404 | 2021 | Steam | Farming Simulator  | A4 | F3 | N-Auto | N-Comp | T6 | T1 | — | high |
| 405 | 2021 | Steam | Fatal Frame: Maide | A2 | F1 | N-Comp | N-Rel | T2 | T1 | — | medium |
| 406 | 2021 | Steam | Football Manager 2 | A4 | F3 | N-Comp | — | T5 | T2、T6 | — | high |
| 407 | 2021 | Steam | Forza Horizon 5 | A4 | F1 | N-Auto | N-Comp | T1 | T6 | — | high |
| 408 | 2021 | Steam | Gamedec | A5 | F4 | N-Auto | N-Comp | T5 | T1 | — | medium |
| 409 | 2021 | Steam | Genesis Noir | A5 | F4 | N-Auto | — | T5 | T1 | — | high |
| 410 | 2021 | Steam | Grime | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 411 | 2021 | Steam | Guardians of the G | A2 | F1 | N-Comp | N-Rel | T2 | T3 | — | medium |
| 412 | 2021 | Steam | Guilty Gear Strive | A1 | F1 | N-Comp | — | T2 | T4 | — | high |
| 413 | 2021 | Steam | Halo Infinite | A1 | F1 | N-Comp | — | T2 | T4 | — | high |
| 414 | 2021 | Steam | Humankind | A4 | F3 | N-Comp | — | T6 | T5、T2 | — | high |
| 415 | 2021 | Steam | Inscryption | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 416 | 2021 | Steam | It Takes Two | A7 | F4 | N-Rel | N-Comp | T4 | T3、T1 | real | high |
| 417 | 2021 | Steam | Jett: The Far Shor | A5 | F5 | N-Auto | — | T1 | T6 | — | high |
| 418 | 2021 | Steam | Judgment | A5 | F4 | N-Comp | N-Rel | T5 | T2、T3 | — | medium |
| 419 | 2021 | Steam | KeyWe | A7 | F4 | N-Rel | N-Comp | T4 | T1 | real | high |
| 420 | 2021 | Steam | Lake | A6 | F5 | N-Auto | N-Rel | T1 | T3 | — | high |
| 421 | 2021 | Steam | Legend of Mana | A5 | F4 | N-Auto | N-Comp | T6 | T5 | — | medium |
| 422 | 2021 | Steam | Lemnis Gate | A1 | F4 | N-Comp | — | T5 | T2 | — | high |
| 423 | 2021 | Steam | Life is Strange: T | A6 | F5 | N-Rel | N-Auto | T3 | T1 | virtual | high |
| 424 | 2021 | Steam | Loop Hero | A4 | F3 | N-Comp | — | T6 | T5 | — | high |
| 425 | 2021 | Steam | Mass Effect Legend | A6 | F5 | N-Rel | N-Comp | T3 | T2 | virtual | high |
| 426 | 2021 | Steam | NEO: The World End | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 427 | 2021 | Steam | Naraka: Bladepoint | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 428 | 2021 | Steam | New World | A3 | F2 | N-Comp | N-Rel | T2 | T4 | — | medium |
| 429 | 2021 | Steam | NieR Replicant | A2 | F5 | N-Rel | N-Comp | T3 | T2 | virtual | high |
| 430 | 2021 | Steam | Omori | A6 | F5 | N-Rel | N-Comp | T3 | T1 | virtual | high |
| 431 | 2021 | Steam | Outriders | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 432 | 2021 | Steam | Pathfinder: Wrath  | A5 | F4 | N-Comp | N-Rel | T5 | T2、T3 | — | medium |
| 433 | 2021 | Steam | Psychonauts 2 | A5 | F4 | N-Auto | N-Comp | T5 | T1 | — | medium |
| 434 | 2021 | Steam | Quake Remaster | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 435 | 2021 | Steam | Raji: An Ancient E | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 436 | 2021 | Steam | Resident Evil Vill | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 437 | 2021 | Steam | Sable | A5 | F4 | N-Auto | — | T1 | T6 | — | high |
| 438 | 2021 | Steam | Saturnalia | A5 | F4 | N-Comp | — | T5 | T1 | — | high |
| 439 | 2021 | Steam | Scarlet Nexus | A2 | F1 | N-Comp | N-Rel | T2 | T3 | — | medium |
| 440 | 2021 | Steam | Severed Steel | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 441 | 2021 | Steam | Solar Ash | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 442 | 2021 | Steam | Solasta: Crown of  | A2 | F4 | N-Comp | — | T5 | T2 | — | high |
| 443 | 2021 | Steam | Song of Farca | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 444 | 2021 | Steam | Subnautica: Below  | A5 | F4 | N-Comp | N-Auto | T6 | T1 | — | high |
| 445 | 2021 | Steam | Super Robot Wars 3 | A2 | F4 | N-Comp | N-Rel | T2 | T3 | — | high |
| 446 | 2021 | Steam | TOEM | A5 | F4 | N-Auto | N-Comp | T1 | T6 | — | high |
| 447 | 2021 | Steam | Tale of Immortal | A5 | F3 | N-Comp | — | T2 | T5 | — | high |
| 448 | 2021 | Steam | Tales of Arise | A2 | F1 | N-Comp | N-Rel | T2 | T3 | — | high |
| 449 | 2021 | Steam | The Artful Escape | A6 | F5 | N-Auto | N-Rel | T1 | T3 | — | medium |
| 450 | 2021 | Steam | The Ascent | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 451 | 2021 | Steam | The Forgotten City | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 452 | 2021 | Steam | The Great Ace Atto | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 453 | 2021 | Steam | The Last Stand: Af | A5 | F4 | N-Comp | — | T6 | T2 | — | high |
| 454 | 2021 | Steam | The Procession to  | A5 | F4 | N-Auto | N-Comp | T1 | T5 | — | medium |
| 455 | 2021 | Steam | Timberborn | A4 | F3 | N-Comp | N-Auto | T6 | T1 | — | high |
| 456 | 2021 | Steam | Tribes of Midgard | A7 | F4 | N-Comp | N-Rel | T2 | T4 | — | high |
| 457 | 2021 | Steam | Unpacking | A4 | F4 | N-Auto | N-Comp | T6 | T1 | — | high |
| 458 | 2021 | Steam | Valheim | A7 | F4 | N-Comp | N-Rel、N-Auto | T2 | T4、T6 | — | high |
| 459 | 2021 | Steam | Voice of Cards: Th | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 460 | 2021 | Steam | White Shadows | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 461 | 2021 | Steam | Wildermyth | A2 | F5 | N-Rel | N-Comp | T3 | T2 | virtual | medium |
| 462 | 2021 | Steam | Yakuza 6: The Song | A2 | F1 | N-Comp | N-Rel | T2 | T1、T3 | — | high |
| 463 | 2020 | Steam | Among Us | A1 | F6 | N-Comp | N-Rel | T2 | T4 | — | high |
| 464 | 2020 | Steam | Black Mesa | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 465 | 2020 | Steam | Bloodroots | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 466 | 2020 | Steam | Carrion | A5 | F1 | N-Comp | N-Auto | T2 | T1 | — | medium |
| 467 | 2020 | Steam | Cloudpunk | A6 | F5 | N-Auto | N-Rel | T1 | T3 | — | medium |
| 468 | 2020 | Steam | Command & Conquer  | A4 | F4 | N-Comp | — | T2 | T5 | — | high |
| 469 | 2020 | Steam | Crusader Kings III | A4 | F3 | N-Comp | N-Rel | T6 | T5、T3 | — | high |
| 470 | 2020 | Steam | Crysis Remastered | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 471 | 2020 | Steam | Cyberpunk 2077 | A2 | F1 | N-Comp | N-Rel | T2 | T3、T1 | — | high |
| 472 | 2020 | Steam | Deep Rock Galactic | A7 | F4 | N-Comp | N-Rel | T2 | T4 | — | medium |
| 473 | 2020 | Steam | Desperados III | A4 | F4 | N-Comp | — | T5 | T2 | — | high |
| 474 | 2020 | Steam | Destroy All Humans | A2 | F1 | N-Auto | N-Comp | T1 | T2 | — | medium |
| 475 | 2020 | Steam | Doom Eternal | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 476 | 2020 | Steam | F1 2020 | A4 | F4 | N-Comp | — | T2 | T5 | — | high |
| 477 | 2020 | Steam | Factorio | A4 | F3 | N-Comp | N-Auto | T6 | T5 | — | high |
| 478 | 2020 | Steam | Fall Guys: Ultimat | A1 | F6 | N-Comp | N-Auto | T2 | T1 | — | medium |
| 479 | 2020 | Steam | Football Manager 2 | A4 | F3 | N-Comp | — | T6 | T2 | — | high |
| 480 | 2020 | Steam | Gears Tactics | A4 | F4 | N-Comp | — | T2 | T5 | — | high |
| 481 | 2020 | Steam | Genshin Impact | A2 | F5 | N-Rel | N-Comp | T3 | T2、T1 | mixed | high |
| 482 | 2020 | Steam | Ghostrunner | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 483 | 2020 | Steam | Gloomhaven | A5 | F4 | N-Comp | N-Rel | T5 | T2、T4 | — | high |
| 484 | 2020 | Steam | Godfall | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 485 | 2020 | Steam | Going Under | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 486 | 2020 | Steam | Grounded | A4 | F4 | N-Comp | N-Auto | T6 | T2、T1 | — | medium |
| 487 | 2020 | Steam | Hades | A5 | F4 | N-Comp | N-Rel | T2 | T5、T3 | — | high |
| 488 | 2020 | Steam | Half-Life: Alyx | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 489 | 2020 | Steam | Immortals Fenyx Ri | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 490 | 2020 | Steam | Iron Harvest | A1 | F4 | N-Comp | — | T2 | T5 | — | high |
| 491 | 2020 | Steam | Mafia: Definitive  | A6 | F5 | N-Rel | — | T3 | T1 | virtual | high |
| 492 | 2020 | Steam | Marvel's Avengers | A2 | F2 | N-Comp | — | T2 | T1 | — | high |
| 493 | 2020 | Steam | Microsoft Flight S | A4 | F4 | N-Auto | N-Comp | T6 | T1、T5 | — | high |
| 494 | 2020 | Steam | Mortal Shell | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 495 | 2020 | Steam | Mount & Blade II:  | A1 | F4 | N-Comp | N-Rel | T6 | T2、T4 | — | high |
| 496 | 2020 | Steam | Moving Out | A7 | F6 | N-Rel | N-Auto | T4 | T1 | real | high |
| 497 | 2020 | Steam | Muck | A4 | F4 | N-Comp | — | T2 | T6 | — | high |
| 498 | 2020 | Steam | Neon Abyss | A5 | F1 | N-Comp | — | T2 | T1 | — | high |
| 499 | 2020 | Steam | Noita | A5 | F3 | N-Comp | — | T5 | T2 | — | high |
| 500 | 2020 | Steam | One Step From Eden | A5 | F4 | N-Comp | — | T2 | T5 | — | high |
| 501 | 2020 | Steam | Ori and the Will o | A2 | F4 | N-Comp | — | T2 | T1 | — | high |
| 502 | 2020 | Steam | Othercide | A2 | F4 | N-Comp | — | T5 | T2 | — | high |
| 503 | 2020 | Steam | Paradise Killer | A5 | F4 | N-Auto | N-Comp | T5 | T1 | — | medium |
| 504 | 2020 | Steam | Phasmophobia | A7 | F4 | N-Rel | N-Comp | T4 | T5 | real | high |
| 505 | 2020 | Steam | Resident Evil 3 | A2 | F4 | N-Comp | — | T2 | T1 | — | high |
| 506 | 2020 | Steam | Risk of Rain 2 | A2 | F3 | N-Comp | — | T2 | T5 | — | high |
| 507 | 2020 | Steam | Rogue Company | A1 | F1 | N-Comp | N-Rel | T2 | T4 | — | high |
| 508 | 2020 | Steam | Rust | A1 | F6 | N-Rel | N-Comp | T4 | T2、T6 | real | high |
| 509 | 2020 | Steam | Sakuna: Of Rice an | A4 | F3 | N-Auto | N-Comp | T6 | T2 | — | medium |
| 510 | 2020 | Steam | Satisfactory | A4 | F3 | N-Auto | N-Comp | T6 | T5 | — | high |
| 511 | 2020 | Steam | Skul: The Hero Sla | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 512 | 2020 | Steam | SnowRunner | A4 | F4 | N-Comp | N-Auto | T6 | T5 | — | medium |
| 513 | 2020 | Steam | Spellbreak | A1 | F1 | N-Comp | — | T2 | T5 | — | high |
| 514 | 2020 | Steam | Spelunky 2 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 515 | 2020 | Steam | Spiritfarer | A6 | F5 | N-Rel | N-Auto | T3 | T1 | virtual | high |
| 516 | 2020 | Steam | Star Wars: Squadro | A1 | F1 | N-Comp | N-Rel | T2 | T4 | — | high |
| 517 | 2020 | Steam | Streets of Rage 4 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 518 | 2020 | Steam | The Walking Dead:  | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 519 | 2020 | Steam | Trackmania | A4 | F4 | N-Comp | — | T2 | T5 | — | high |
| 520 | 2020 | Steam | Trials of Mana | A2 | F2 | N-Auto | N-Comp | T1 | T2 | — | medium |
| 521 | 2020 | Steam | Umurangi Generatio | A4 | F4 | N-Auto | — | T1 | T6 | — | high |
| 522 | 2020 | Steam | Wasteland 3 | A2 | F4 | N-Comp | — | T2 | T5 | — | high |
| 523 | 2020 | Steam | Watch Dogs: Legion | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 524 | 2020 | Steam | XCOM: Chimera Squa | A2 | F4 | N-Comp | — | T2 | T5 | — | high |
| 525 | 2020 | Steam | Yakuza: Like a Dra | A2 | F4 | N-Comp | N-Rel | T2 | T3 | — | high |
| 526 | 2019 | Steam | Apex 英雄 | A1 | F1 | N-Comp | — | T2 | T4 | — | high |
| 527 | 2019 | Steam | Gato Roboto | A2 | F4 | N-Comp | — | T2 | T5 | — | high |
| 528 | 2019 | Steam | Mordhau | A1 | F1 | N-Comp | — | T2 | T5 | — | high |
| 529 | 2019 | Steam | 三国志14 | A4 | F3 | N-Comp | — | T6 | T5 | — | high |
| 530 | 2019 | Steam | 代码薇拉 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 531 | 2019 | Steam | 全面战争：三国 | A4 | F3 | N-Comp | — | T6 | T2 | — | high |
| 532 | 2019 | Steam | 只狼：影逝二度 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 533 | 2019 | Steam | 命运2：暗影要塞 | A2 | F1 | N-Comp | — | T2 | T4 | — | high |
| 534 | 2019 | Steam | 圣歌 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 535 | 2019 | Steam | 地铁：离去 | A2 | F4 | N-Comp | — | T2 | T5 | — | high |
| 536 | 2019 | Steam | 夜勤人 | A2 | F4 | N-Comp | — | T2 | T6 | — | high |
| 537 | 2019 | Steam | 天外世界 | A5 | F5 | N-Comp | N-Rel | T5 | T3 | — | medium |
| 538 | 2019 | Steam | 女巫布莱尔 | A5 | F4 | N-Comp | — | T2 | T1 | — | high |
| 539 | 2019 | Steam | 威尔莫特的仓库 | A4 | F3 | N-Comp | N-Rel | T6 | T4 | — | medium |
| 540 | 2019 | Steam | 尘埃拉力赛2.0 | A2 | F4 | N-Comp | — | T2 | T5 | — | high |
| 541 | 2019 | Steam | 巴巴是你 | A5 | F4 | N-Comp | — | T5 | — | — | high |
| 542 | 2019 | Steam | 幸福工厂 | A4 | F3 | N-Comp | N-Auto | T6 | T1 | — | high |
| 543 | 2019 | Steam | 战争机器5 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 544 | 2019 | Steam | 战地5 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 545 | 2019 | Steam | 捣蛋鹅 | A5 | F4 | N-Auto | — | T1 | T3 | — | high |
| 546 | 2019 | Steam | 控制 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 547 | 2019 | Steam | 无主之地3 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 548 | 2019 | Steam | 星球大战 绝地：陨落的武士团 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 549 | 2019 | Steam | 星际拓荒 | A5 | F4 | N-Comp | — | T5 | T1 | — | high |
| 550 | 2019 | Steam | 杀戮尖塔 | A5 | F3 | N-Comp | — | T5 | T2 | — | high |
| 551 | 2019 | Steam | 极乐迪斯科 | A6 | F5 | N-Auto | N-Rel | T1 | T5 | — | medium |
| 552 | 2019 | Steam | 武士零 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 553 | 2019 | Steam | 死亡搁浅 | A4 | F4 | N-Comp | N-Rel | T6 | T4 | — | medium |
| 554 | 2019 | Steam | 汤姆克兰西：全境封锁2 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 555 | 2019 | Steam | 沉没之城 | A5 | F4 | N-Comp | — | T5 | T1 | — | high |
| 556 | 2019 | Steam | 波西亚时光 | A4 | F4 | N-Auto | N-Rel | T1 | T3、T6 | — | high |
| 557 | 2019 | Steam | 海岛大亨6 | A4 | F3 | N-Comp | N-Auto | T6 | T1 | — | high |
| 558 | 2019 | Steam | 炉石传说：酒馆战棋 | A1 | F3 | N-Comp | — | T2 | T5 | — | high |
| 559 | 2019 | Steam | 狂怒2 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 560 | 2019 | Steam | 狂热运输2 | A4 | F3 | N-Comp | N-Auto | T6 | T1 | — | high |
| 561 | 2019 | Steam | 生化危机2：重制版 | A2 | F4 | N-Comp | — | T2 | T5 | — | high |
| 562 | 2019 | Steam | 皇牌空战7：未知空域 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 563 | 2019 | Steam | 纪元1800 | A4 | F3 | N-Comp | N-Auto | T6 | T5 | — | high |
| 564 | 2019 | Steam | 绿色地狱 | A2 | F4 | N-Comp | — | T2 | T5 | — | high |
| 565 | 2019 | Steam | 缺氧 | A4 | F3 | N-Comp | — | T6 | T5 | — | high |
| 566 | 2019 | Steam | 荒野大镖客：救赎2 | A6 | F5 | N-Rel | N-Auto | T3 | T1 | virtual | high |
| 567 | 2019 | Steam | 血污：夜之仪式 | A2 | F4 | N-Comp | — | T2 | T5 | — | high |
| 568 | 2019 | Steam | 遗迹：灰烬重生 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 569 | 2019 | Steam | 雨中冒险2 | A2 | F3 | N-Comp | — | T2 | T5 | — | high |
| 570 | 2019 | Steam | 雷霆一击 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 571 | 2019 | Steam | 骰子地下城 | A5 | F3 | N-Comp | — | T5 | T2 | — | high |
| 572 | 2019 | Steam | 鬼泣5 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 573 | 2019 | Steam | 魔兽世界：经典旧世 | A2 | F4 | N-Comp | N-Rel | T2 | T4 | — | high |
| 574 | 2018 | Steam | Amid Evil | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 575 | 2018 | Steam | Artifact | A1 | F3 | N-Comp | — | T5 | T2 | — | high |
| 576 | 2018 | Steam | Contractors | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 577 | 2018 | Steam | Dusk | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 578 | 2018 | Steam | Grip | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 579 | 2018 | Steam | Kenshi | A4 | F3 | N-Auto | N-Comp | T6 | T1 | — | high |
| 580 | 2018 | Steam | Minit | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 581 | 2018 | Steam | Realm Royale | A1 | F1 | N-Comp | — | T2 | T5 | — | high |
| 582 | 2018 | Steam | Synthetik | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 583 | 2018 | Steam | 世界最终幻想 | A3 | F2 | N-Comp | N-Rel | T2 | T3 | — | medium |
| 584 | 2018 | Steam | 二之国2：亡灵之国 | A2 | F4 | N-Comp | N-Auto | T2 | T6、T3 | — | medium |
| 585 | 2018 | Steam | 交叉代码 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 586 | 2018 | Steam | 伊苏8：达娜的安魂曲 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 587 | 2018 | Steam | 侏罗纪世界：进化 | A4 | F3 | N-Comp | N-Auto | T6 | T1 | — | medium |
| 588 | 2018 | Steam | 信使 | A2 | F4 | N-Comp | — | T2 | T5 | — | high |
| 589 | 2018 | Steam | 全面战争传奇：不列颠尼亚王座 | A4 | F4 | N-Comp | — | T6 | T2 | — | high |
| 590 | 2018 | Steam | 冰城传奇4 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 591 | 2018 | Steam | 冰汽时代 | A4 | F3 | N-Comp | — | T6 | T5 | — | high |
| 592 | 2018 | Steam | 刺客信条：奥德赛 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 593 | 2018 | Steam | 剑与魔法 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 594 | 2018 | Steam | 勇者斗恶龙11 | A2 | F4 | N-Comp | N-Rel | T2 | T3 | — | medium |
| 595 | 2018 | Steam | 北境之地 | A4 | F3 | N-Comp | — | T6 | T2 | — | high |
| 596 | 2018 | Steam | 双点医院 | A4 | F3 | N-Comp | N-Auto | T6 | T1 | — | medium |
| 597 | 2018 | Steam | 叛乱：沙漠风暴 | A1 | F1 | N-Comp | — | T2 | T4 | — | high |
| 598 | 2018 | Steam | 古墓丽影：暗影 | A5 | F4 | N-Comp | — | T2 | T5 | — | high |
| 599 | 2018 | Steam | 吸血鬼 | A2 | F1 | N-Comp | — | T2 | T6 | — | high |
| 600 | 2018 | Steam | 哈迪斯 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 601 | 2018 | Steam | 堡垒之夜 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 602 | 2018 | Steam | 墨西哥英雄大混战2 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 603 | 2018 | Steam | 夜下降生 | A1 | F1 | N-Comp | — | T2 | T5 | — | high |
| 604 | 2018 | Steam | 天国：拯救 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 605 | 2018 | Steam | 奇异人生2 | A6 | F5 | N-Rel | N-Auto | T3 | T1 | virtual | high |
| 606 | 2018 | Steam | 奇异小队 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 607 | 2018 | Steam | 奥伯拉·丁的回归 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | high |
| 608 | 2018 | Steam | 如龙0 | A2 | F1 | N-Comp | N-Rel | T2 | T3 | — | medium |
| 609 | 2018 | Steam | 孤岛惊魂5 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 610 | 2018 | Steam | 守墓人 | A4 | F3 | N-Comp | N-Auto | T6 | T1 | — | medium |
| 611 | 2018 | Steam | 实况足球2019 | A1 | F1 | N-Comp | — | T2 | T5 | — | high |
| 612 | 2018 | Steam | 巫师之昆特牌 | A1 | F3 | N-Comp | — | T2 | T5 | — | high |
| 613 | 2018 | Steam | 巫师之昆特牌：王权的陨落 | A5 | F4 | N-Comp | N-Rel | T5 | T3 | — | medium |
| 614 | 2018 | Steam | 帝国时代：决定版 | A4 | F3 | N-Comp | — | T6 | T2 | — | high |
| 615 | 2018 | Steam | 幽匿协议 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 616 | 2018 | Steam | 开拓者：拥王者 | A4 | F3 | N-Comp | N-Rel | T6 | T5、T3 | — | medium |
| 617 | 2018 | Steam | 怪物猎人：世界 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 618 | 2018 | Steam | 战场女武神4 | A4 | F4 | N-Comp | — | T5 | T2 | — | high |
| 619 | 2018 | Steam | 战锤：末世鼠疫2 | A2 | F1 | N-Comp | — | T1 | T2 | — | high |
| 620 | 2018 | Steam | 房产达人 | A4 | F3 | N-Auto | N-Comp | T6 | T1 | — | high |
| 621 | 2018 | Steam | 撞车嘉年华 | A1 | F1 | N-Comp | N-Auto | T1 | T2 | — | high |
| 622 | 2018 | Steam | 旗帜的传说3 | A2 | F5 | N-Rel | N-Comp | T3 | T5 | virtual | high |
| 623 | 2018 | Steam | 最终幻想15 | A2 | F5 | N-Rel | N-Comp | T3 | T2 | virtual | high |
| 624 | 2018 | Steam | 木筏生存 | A3 | F2 | N-Auto | N-Rel | T6 | T1、T4 | — | medium |
| 625 | 2018 | Steam | 机甲战士 | A4 | F4 | N-Comp | — | T5 | T2 | — | high |
| 626 | 2018 | Steam | 杀手2 | A5 | F4 | N-Comp | N-Auto | T5 | T6 | — | high |
| 627 | 2018 | Steam | 极限竞速：地平线4 | A3 | F2 | N-Auto | N-Comp | T1 | T2 | — | medium |
| 628 | 2018 | Steam | 格莉斯 | A5 | F5 | N-Auto | N-Rel | T1 | T3 | — | high |
| 629 | 2018 | Steam | 森林 | A3 | F4 | N-Comp | N-Rel | T2 | T4、T1 | — | high |
| 630 | 2018 | Steam | 模拟农场19 | A4 | F2 | N-Auto | N-Comp | T6 | T1 | — | high |
| 631 | 2018 | Steam | 正当防卫4 | A2 | F1 | N-Auto | N-Comp | T1 | T2 | — | high |
| 632 | 2018 | Steam | 死亡细胞 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 633 | 2018 | Steam | 毛线小精灵2 | A7 | F5 | N-Rel | N-Auto | T4 | T3 | real | high |
| 634 | 2018 | Steam | 永恒之柱2：死火 | A4 | F4 | N-Comp | N-Rel | T5 | T2、T3 | — | high |
| 635 | 2018 | Steam | 洛克人11 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 636 | 2018 | Steam | 流放者柯南 | A3 | F2 | N-Comp | N-Rel | T2 | T4、T6 | — | high |
| 637 | 2018 | Steam | 深岩银河 | A7 | F4 | N-Comp | N-Rel | T2 | T4、T1 | — | medium |
| 638 | 2018 | Steam | 深海迷航 | A5 | F4 | N-Auto | N-Comp | T6 | T1 | — | high |
| 639 | 2018 | Steam | 火车山谷2 | A4 | F4 | N-Auto | N-Comp | T6 | T5 | — | high |
| 640 | 2018 | Steam | 灵魂能力6 | A1 | F1 | N-Comp | N-Rel | T2 | T1、T4 | — | high |
| 641 | 2018 | Steam | 猎杀：对决 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 642 | 2018 | Steam | 甜甜圈县 | A4 | F2 | N-Auto | — | T1 | — | — | high |
| 643 | 2018 | Steam | 生存火星 | A4 | F4 | N-Comp | N-Auto | T6 | T5 | — | high |
| 644 | 2018 | Steam | 盗贼之海 | A7 | F4 | N-Rel | N-Comp | T4 | T1 | real | high |
| 645 | 2018 | Steam | 绝地求生 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 646 | 2018 | Steam | 胡闹厨房2 | A7 | F4 | N-Rel | N-Comp | T4 | T1 | real | high |
| 647 | 2018 | Steam | 节奏光剑 | A2 | F1 | N-Comp | N-Auto | T1 | T2 | — | medium |
| 648 | 2018 | Steam | 花园之间 | A5 | F4 | N-Auto | — | T1 | T5 | — | high |
| 649 | 2018 | Steam | 苍翼默示录：交叉组队战 | A1 | F1 | N-Comp | — | T2 | T5 | — | high |
| 650 | 2018 | Steam | 蔚蓝 | A2 | F4 | N-Comp | — | T2 | T1 | — | high |
| 651 | 2018 | Steam | 血污：月之诅咒 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 652 | 2018 | Steam | 装机模拟器 | A4 | F4 | N-Auto | N-Comp | T6 | T5 | — | medium |
| 653 | 2018 | Steam | 足球经理2019 | A4 | F3 | N-Comp | — | T6 | T5 | — | high |
| 654 | 2018 | Steam | 辐射76 | A3 | F2 | N-Comp | N-Rel | T2 | T4 | — | medium |
| 655 | 2018 | Steam | 边缘世界 | A4 | F3 | N-Comp | N-Auto | T6 | T5 | — | high |
| 656 | 2018 | Steam | 达尔文计划 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 657 | 2018 | Steam | 过山车大亨 | A4 | F3 | N-Auto | N-Comp | T6 | T1 | — | medium |
| 658 | 2018 | Steam | 逃出生天 | A7 | F5 | N-Rel | — | T4 | T3 | real | high |
| 659 | 2018 | Steam | 铁路帝国 | A4 | F3 | N-Comp | — | T6 | T5 | — | high |
| 660 | 2018 | Steam | 陷阵之志 | A4 | F4 | N-Comp | — | T5 | T2 | — | high |
| 661 | 2018 | Steam | 龙珠战士Z | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 662 | 2017 | Steam | A Hat in Time | A5 | F4 | N-Auto | N-Comp | T1 | T5 | — | high |
| 663 | 2017 | Steam | Albion Online | A3 | F2 | N-Comp | N-Rel | T2 | T4 | — | medium |
| 664 | 2017 | Steam | Ark: Survival Evol | A3 | F2 | N-Comp | N-Auto | T6 | T2 | — | high |
| 665 | 2017 | Steam | Assassin's Creed O | A2 | F4 | N-Auto | N-Comp | T1 | T2 | — | medium |
| 666 | 2017 | Steam | Battle Chasers: Ni | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 667 | 2017 | Steam | Battlerite | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 668 | 2017 | Steam | Bayonetta | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 669 | 2017 | Steam | Blackwake | A7 | F6 | N-Rel | N-Comp | T4 | T2 | real | high |
| 670 | 2017 | Steam | Call of Duty: WWII | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 671 | 2017 | Steam | Caveblazer | A5 | F3 | N-Comp | — | T5 | T2 | — | high |
| 672 | 2017 | Steam | Conan Exiles | A3 | F2 | N-Comp | N-Auto | T6 | T2 | — | high |
| 673 | 2017 | Steam | Cuphead | A2 | F4 | N-Comp | — | T2 | T1 | — | high |
| 674 | 2017 | Steam | Dead Cells | A5 | F3 | N-Comp | — | T5 | T2 | — | high |
| 675 | 2017 | Steam | Destiny 2 | A2 | F1 | N-Comp | N-Rel | T2 | T4 | — | medium |
| 676 | 2017 | Steam | Dirt 4 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 677 | 2017 | Steam | Dishonored: Death  | A5 | F3 | N-Auto | N-Comp | T6 | T5 | — | medium |
| 678 | 2017 | Steam | Divinity: Original | A5 | F3 | N-Comp | N-Auto | T5 | T6 | — | high |
| 679 | 2017 | Steam | Doki Doki Literatu | A6 | F5 | N-Rel | — | T3 | T5 | virtual | high |
| 680 | 2017 | Steam | Dreadnought | A1 | F1 | N-Comp | — | T2 | T5 | — | high |
| 681 | 2017 | Steam | Dungeons 3 | A4 | F3 | N-Comp | — | T6 | T5 | — | high |
| 682 | 2017 | Steam | ELEX | A5 | F4 | N-Comp | N-Auto | T2 | T1 | — | medium |
| 683 | 2017 | Steam | Endless Space 2 | A4 | F3 | N-Comp | — | T6 | T5 | — | high |
| 684 | 2017 | Steam | Everspace | A5 | F1 | N-Comp | — | T2 | T5 | — | high |
| 685 | 2017 | Steam | F1 2017 | A1 | F4 | N-Comp | — | T2 | T6 | — | high |
| 686 | 2017 | Steam | Faeria | A1 | F3 | N-Comp | — | T5 | T2 | — | high |
| 687 | 2017 | Steam | Flinthook | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 688 | 2017 | Steam | For Honor | A1 | F1 | N-Comp | — | T2 | T5 | — | high |
| 689 | 2017 | Steam | Foxhole | A7 | F6 | N-Rel | N-Comp | T4 | T6 | real | high |
| 690 | 2017 | Steam | Friday the 13th: T | A1 | F6 | N-Rel | N-Comp | T4 | T1 | real | high |
| 691 | 2017 | Steam | Getting Over It wi | A2 | F4 | N-Comp | — | T2 | T1 | — | high |
| 692 | 2017 | Steam | Ghost Recon Wildla | A7 | F4 | N-Comp | N-Rel | T2 | T4 | — | medium |
| 693 | 2017 | Steam | Guilty Gear Xrd Re | A1 | F1 | N-Comp | — | T2 | T5 | — | high |
| 694 | 2017 | Steam | Gwent: The Witcher | A1 | F3 | N-Comp | — | T5 | T2 | — | high |
| 695 | 2017 | Steam | Halo Wars 2 | A1 | F3 | N-Comp | — | T2 | T6 | — | high |
| 696 | 2017 | Steam | Hellblade: Senua's | A6 | F5 | N-Rel | N-Comp | T3 | T1 | virtual | high |
| 697 | 2017 | Steam | Hollow Knight | A5 | F4 | N-Comp | N-Auto | T2 | T5 | — | high |
| 698 | 2017 | Steam | Human: Fall Flat | A5 | F4 | N-Auto | N-Rel | T1 | T4 | — | medium |
| 699 | 2017 | Steam | Idle Champions of  | A3 | F2 | N-Comp | — | T2 | T6 | — | high |
| 700 | 2017 | Steam | Injustice 2 | A1 | F1 | N-Comp | — | T2 | T6 | — | high |
| 701 | 2017 | Steam | Just Dance 2018 | A7 | F6 | N-Rel | N-Auto | T4 | T1 | real | high |
| 702 | 2017 | Steam | LawBreakers | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 703 | 2017 | Steam | Little Nightmares | A2 | F4 | N-Comp | — | T2 | T5 | — | high |
| 704 | 2017 | Steam | Marvel vs. Capcom: | A1 | F1 | N-Comp | — | T2 | T5 | — | high |
| 705 | 2017 | Steam | Mass Effect: Andro | A2 | F5 | N-Rel | N-Comp | T3 | T2 | virtual | medium |
| 706 | 2017 | Steam | Middle-earth: Shad | A2 | F3 | N-Comp | — | T6 | T2 | — | high |
| 707 | 2017 | Steam | Nex Machina | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 708 | 2017 | Steam | Nidhogg 2 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 709 | 2017 | Steam | NieR: Automata | A2 | F5 | N-Rel | N-Comp | T3 | T2、T5 | virtual | medium |
| 710 | 2017 | Steam | Night in the Woods | A6 | F5 | N-Rel | N-Auto | T3 | T1 | virtual | high |
| 711 | 2017 | Steam | Northgard | A4 | F3 | N-Comp | — | T6 | T5 | — | high |
| 712 | 2017 | Steam | Okami HD | A2 | F4 | N-Comp | N-Rel | T2 | T5、T3 | — | medium |
| 713 | 2017 | Steam | Outlast 2 | A2 | F4 | N-Comp | — | T2 | T1 | — | high |
| 714 | 2017 | Steam | Oxygen Not Include | A4 | F3 | N-Comp | — | T6 | T5 | — | high |
| 715 | 2017 | Steam | Paladins | A1 | F1 | N-Comp | — | T2 | T5 | — | high |
| 716 | 2017 | Steam | Path of Exile: The | A5 | F3 | N-Comp | — | T5 | T2、T6 | — | high |
| 717 | 2017 | Steam | PlayerUnknown's Ba | A1 | F1 | N-Comp | N-Rel | T2 | T4 | — | high |
| 718 | 2017 | Steam | Project CARS 2 | A1 | F1 | N-Comp | — | T2 | T5 | — | high |
| 719 | 2017 | Steam | Pyre | A1 | F4 | N-Comp | N-Rel | T2 | T3 | — | medium |
| 720 | 2017 | Steam | Quake Champions | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 721 | 2017 | Steam | Ravenfield | A2 | F1 | N-Comp | N-Auto | T1 | T2 | — | medium |
| 722 | 2017 | Steam | Resident Evil 7: B | A5 | F4 | N-Comp | — | T2 | T5 | — | high |
| 723 | 2017 | Steam | RiME | A5 | F4 | N-Auto | N-Rel | T1 | T3 | — | medium |
| 724 | 2017 | Steam | Shovel Knight: Spe | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 725 | 2017 | Steam | Slay the Spire | A5 | F3 | N-Comp | — | T5 | T2 | — | high |
| 726 | 2017 | Steam | Snake Pass | A5 | F4 | N-Auto | N-Comp | T6 | T5 | — | medium |
| 727 | 2017 | Steam | Sonic Forces | A2 | F1 | N-Comp | N-Auto | T2 | T6 | — | medium |
| 728 | 2017 | Steam | Sonic Mania | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 729 | 2017 | Steam | South Park: The Fr | A4 | F4 | N-Comp | N-Rel | T5 | T2、T3 | — | medium |
| 730 | 2017 | Steam | Star Wars Battlefr | A1 | F1 | N-Comp | N-Rel | T2 | T4、T1 | — | high |
| 731 | 2017 | Steam | SteamWorld Dig 2 | A3 | F2 | N-Comp | — | T2 | T6 | — | high |
| 732 | 2017 | Steam | Steel Division: No | A4 | F3 | N-Comp | — | T5 | T2 | — | high |
| 733 | 2017 | Steam | Stick Fight: The G | A1 | F1 | N-Comp | N-Auto | T1 | T2 | — | medium |
| 734 | 2017 | Steam | Sudden Strike 4 | A4 | F4 | N-Comp | — | T5 | T6 | — | high |
| 735 | 2017 | Steam | Tacoma | A5 | F5 | N-Rel | N-Auto | T3 | T5 | virtual | medium |
| 736 | 2017 | Steam | Tekken 7 | A1 | F1 | N-Comp | — | T2 | T5 | — | high |
| 737 | 2017 | Steam | The Binding of Isa | A5 | F3 | N-Comp | — | T5 | T2 | — | high |
| 738 | 2017 | Steam | The Escapists 2 | A4 | F4 | N-Comp | N-Rel | T5 | T4、T6 | — | medium |
| 739 | 2017 | Steam | The Evil Within 2 | A2 | F1 | N-Comp | — | T2 | T5、T1 | — | high |
| 740 | 2017 | Steam | The Long Dark | A4 | F4 | N-Comp | — | T6 | T2、T5 | — | high |
| 741 | 2017 | Steam | The Mummy Demaster | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 742 | 2017 | Steam | The Surge | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 743 | 2017 | Steam | They Are Billions | A4 | F4 | N-Comp | — | T6 | T5 | — | high |
| 744 | 2017 | Steam | Thimbleweed Park | A5 | F4 | N-Auto | N-Comp | T5 | T1 | — | medium |
| 745 | 2017 | Steam | Torment: Tides of  | A6 | F5 | N-Auto | N-Rel | T5 | T3 | — | medium |
| 746 | 2017 | Steam | Total War: Warhamm | A4 | F3 | N-Comp | — | T6 | T2 | — | high |
| 747 | 2017 | Steam | Vanquish | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 748 | 2017 | Steam | Warframe: Plains o | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 749 | 2017 | Steam | Warhammer 40,000:  | A1 | F4 | N-Comp | — | T2 | T5 | — | high |
| 750 | 2017 | Steam | West of Loathing | A5 | F5 | N-Auto | N-Comp | T1 | T5 | — | medium |
| 751 | 2017 | Steam | What Remains of Ed | A6 | F5 | N-Auto | N-Rel | T1 | T3 | — | medium |
| 752 | 2017 | Steam | Yooka-Laylee | A5 | F4 | N-Auto | N-Comp | T1 | T2 | — | medium |
| 753 | 2017 | Steam | Yu-Gi-Oh! Duel Lin | A1 | F4 | N-Comp | — | T2 | T5 | — | high |
| 754 | 2016 | Steam | Abzû | A6 | F5 | N-Auto | — | T1 | — | — | high |
| 755 | 2016 | Steam | Astroneer | A4 | F3 | N-Auto | N-Rel | T6 | T1 | — | medium |
| 756 | 2016 | Steam | Attack on Titan | A2 | F1 | N-Comp | N-Rel | T2 | T3 | — | high |
| 757 | 2016 | Steam | Battlefield 1 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 758 | 2016 | Steam | Battlefleet Gothic | A1 | F4 | N-Comp | — | T2 | T5 | — | high |
| 759 | 2016 | Steam | Call of Duty: Infi | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 760 | 2016 | Steam | Civilization VI | A4 | F3 | N-Comp | — | T6 | T2、T5 | — | high |
| 761 | 2016 | Steam | Clustertruck | A2 | F4 | N-Comp | — | T2 | T1 | — | high |
| 762 | 2016 | Steam | Dark Souls III | A2 | F4 | N-Comp | — | T2 | T5 | — | high |
| 763 | 2016 | Steam | Darkest Dungeon | A4 | F4 | N-Comp | — | T5 | T6 | — | high |
| 764 | 2016 | Steam | Dead by Daylight | A1 | F6 | N-Comp | N-Rel | T2 | T4 | — | high |
| 765 | 2016 | Steam | Deus Ex: Mankind D | A5 | F4 | N-Comp | N-Auto | T5 | T2 | — | high |
| 766 | 2016 | Steam | Dishonored 2 | A5 | F4 | N-Comp | N-Auto | T5 | T2 | — | high |
| 767 | 2016 | Steam | Doom | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 768 | 2016 | Steam | Dragon's Dogma | A2 | F1 | N-Comp | N-Rel | T2 | T3 | — | high |
| 769 | 2016 | Steam | Enter the Gungeon | A2 | F4 | N-Comp | — | T2 | T5 | — | high |
| 770 | 2016 | Steam | Far Cry Primal | A2 | F4 | N-Comp | N-Rel | T2 | T3 | — | high |
| 771 | 2016 | Steam | Firewatch | A6 | F5 | N-Rel | N-Auto | T3 | T1 | virtual | high |
| 772 | 2016 | Steam | Grim Dawn | A3 | F2 | N-Comp | — | T2 | T6 | — | high |
| 773 | 2016 | Steam | Hearts of Iron IV | A4 | F3 | N-Comp | N-Auto | T6 | T5 | — | high |
| 774 | 2016 | Steam | Hitman | A5 | F4 | N-Comp | N-Auto | T5 | T2 | — | high |
| 775 | 2016 | Steam | Hyper Light Drifte | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 776 | 2016 | Steam | Inside | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 777 | 2016 | Steam | Job Simulator | A5 | F3 | N-Auto | — | T1 | — | — | high |
| 778 | 2016 | Steam | Killing Floor 2 | A2 | F1 | N-Comp | N-Rel | T2 | T1、T4 | — | high |
| 779 | 2016 | Steam | Kingdom: New Lands | A4 | F4 | N-Comp | — | T6 | T5 | — | high |
| 780 | 2016 | Steam | Layers of Fear | A6 | F5 | N-Rel | N-Auto | T3 | T1 | virtual | high |
| 781 | 2016 | Steam | Move or Die | A1 | F6 | N-Comp | N-Rel | T1 | T4 | — | high |
| 782 | 2016 | Steam | My Summer Car | A4 | F4 | N-Auto | N-Comp | T6 | T5 | — | high |
| 783 | 2016 | Steam | No Man's Sky | A5 | F3 | N-Auto | N-Comp | T1 | T6 | — | high |
| 784 | 2016 | Steam | Offworld Trading C | A4 | F3 | N-Comp | — | T5 | T2 | — | high |
| 785 | 2016 | Steam | Overcooked! | A7 | F4 | N-Comp | N-Rel | T1 | T4 | — | high |
| 786 | 2016 | Steam | Overwatch | A1 | F1 | N-Comp | N-Rel | T2 | T4 | — | high |
| 787 | 2016 | Steam | Owlboy | A2 | F4 | N-Comp | N-Rel | T2 | T3 | — | high |
| 788 | 2016 | Steam | Planet Coaster | A4 | F3 | N-Auto | N-Comp | T6 | T1 | — | high |
| 789 | 2016 | Steam | Poly Bridge | A5 | F3 | N-Auto | N-Comp | T5 | T6 | — | high |
| 790 | 2016 | Steam | Portal Knights | A3 | F2 | N-Auto | N-Comp | T1 | T6 | — | high |
| 791 | 2016 | Steam | Punch Club | A4 | F2 | N-Comp | — | T6 | T2 | — | high |
| 792 | 2016 | Steam | Reigns | A5 | F4 | N-Comp | N-Rel | T5 | T3 | — | high |
| 793 | 2016 | Steam | RimWorld | A4 | F3 | N-Comp | N-Rel | T6 | T5 | — | high |
| 794 | 2016 | Steam | Rise of the Tomb R | A2 | F4 | N-Comp | N-Rel | T2 | T3 | — | high |
| 795 | 2016 | Steam | Salt and Sanctuary | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 796 | 2016 | Steam | Scrap Mechanic | A4 | F3 | N-Auto | N-Comp | T6 | T5 | — | high |
| 797 | 2016 | Steam | Shadow Tactics | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 798 | 2016 | Steam | Shenzen I/O | A4 | F3 | N-Auto | N-Comp | T5 | T6 | — | high |
| 799 | 2016 | Steam | Skyrim SE | A5 | F3 | N-Auto | N-Comp、N-Rel | T1 | T6、T3 | — | high |
| 800 | 2016 | Steam | Starbound | A5 | F3 | N-Auto | N-Comp | T1 | T6 | — | high |
| 801 | 2016 | Steam | Stardew Valley | A3 | F2 | N-Auto | N-Rel | T6 | T1、T3 | — | high |
| 802 | 2016 | Steam | Stellaris | A4 | F3 | N-Comp | — | T6 | T5 | — | high |
| 803 | 2016 | Steam | Stephen's Sausage  | A5 | F4 | N-Comp | — | T5 | — | — | high |
| 804 | 2016 | Steam | Street Fighter V | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 805 | 2016 | Steam | Superhot | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 806 | 2016 | Steam | Superhot VR | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 807 | 2016 | Steam | The Division | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 808 | 2016 | Steam | The Witness | A5 | F4 | N-Comp | — | T5 | — | — | high |
| 809 | 2016 | Steam | Thumper | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 810 | 2016 | Steam | Titanfall 2 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 811 | 2016 | Steam | Total War: Warhamm | A4 | F3 | N-Comp | — | T6 | T2 | — | high |
| 812 | 2016 | Steam | Tyranny | A6 | F5 | N-Comp | N-Rel | T5 | T3 | — | medium |
| 813 | 2016 | Steam | Ultimate Chicken H | A1 | F6 | N-Rel | N-Comp | T4 | T1 | real | high |
| 814 | 2016 | Steam | Unravel | A5 | F5 | N-Auto | N-Rel | T1 | T3 | — | medium |
| 815 | 2016 | Steam | Va-11 Hall-A | A6 | F5 | N-Rel | N-Auto | T3 | T1 | virtual | high |
| 816 | 2016 | Steam | Watch Dogs 2 | A5 | F3 | N-Auto | N-Comp | T6 | T1 | — | medium |
| 817 | 2016 | Steam | XCOM 2 | A4 | F4 | N-Comp | — | T5 | T6 | — | high |
| 818 | 2016 | Steam | Zero Escape | A5 | F4 | N-Comp | — | T5 | — | — | high |
| 819 | 2026 | 微信小游戏 | 2048 | A4 | F2 | N-Comp | — | T5 | T6 | — | high |
| 820 | 2026 | 微信小游戏 | QQ飞车 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 821 | 2026 | 微信小游戏 | 一念逍遥 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 822 | 2026 | 微信小游戏 | 三国志·战略版 | A1 | F6 | N-Rel | N-Comp | T4 | T6 | real | high |
| 823 | 2026 | 微信小游戏 | 三国杀 | A1 | F6 | N-Comp | N-Rel | T5 | T4 | — | medium |
| 824 | 2026 | 微信小游戏 | 不休的乌拉拉 | A3 | F2 | N-Comp | N-Rel | T2 | T4 | — | medium |
| 825 | 2026 | 微信小游戏 | 丛林大作战 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 826 | 2026 | 微信小游戏 | 九阴真经3D | A1 | F1 | N-Comp | N-Rel | T2 | T1 | — | high |
| 827 | 2026 | 微信小游戏 | 乱世王者 | A1 | F6 | N-Rel | N-Comp | T4 | T6 | real | high |
| 828 | 2026 | 微信小游戏 | 云上城之歌 | A2 | F4 | N-Comp | N-Rel | T2 | T3 | — | medium |
| 829 | 2026 | 微信小游戏 | 人生重开模拟器 | A5 | F3 | N-Auto | — | T1 | T5 | — | high |
| 830 | 2026 | 微信小游戏 | 仙剑奇侠传之挥剑问情 | A6 | F5 | N-Rel | N-Comp | T3 | T2 | virtual | high |
| 831 | 2026 | 微信小游戏 | 会说话的安吉拉 | A3 | F5 | N-Rel | N-Auto | T3 | T1 | virtual | high |
| 832 | 2026 | 微信小游戏 | 会说话的汤姆猫 | A3 | F5 | N-Rel | N-Auto | T3 | T1 | virtual | high |
| 833 | 2026 | 微信小游戏 | 会说话的狗狗本 | A3 | F5 | N-Rel | N-Auto | T3 | T1 | virtual | high |
| 834 | 2026 | 微信小游戏 | 你画我猜 | A7 | F6 | N-Rel | N-Auto | T4 | T1 | real | high |
| 835 | 2026 | 微信小游戏 | 侠义九州 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 836 | 2026 | 微信小游戏 | 侠客风云传 | A5 | F5 | N-Auto | N-Comp、N-Rel | T1 | T5、T3 | — | medium |
| 837 | 2026 | 微信小游戏 | 保卫萝卜 | A4 | F4 | N-Comp | — | T6 | T5 | — | high |
| 838 | 2026 | 微信小游戏 | 修仙模拟器 | A5 | F3 | N-Auto | N-Comp | T1 | T5 | — | high |
| 839 | 2026 | 微信小游戏 | 倒霉熊 | A2 | F1 | N-Auto | — | T1 | — | — | high |
| 840 | 2026 | 微信小游戏 | 元气骑士 | A5 | F3 | N-Comp | N-Rel | T5 | T2、T4 | — | high |
| 841 | 2026 | 微信小游戏 | 光·遇 | A7 | F6 | N-Rel | N-Auto | T4 | T1 | real | high |
| 842 | 2026 | 微信小游戏 | 全民大乐斗 | A1 | F6 | N-Rel | N-Comp | T4 | T1 | real | high |
| 843 | 2026 | 微信小游戏 | 全职觉醒 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 844 | 2026 | 微信小游戏 | 决战！平安京 | A1 | F1 | N-Comp | — | T2 | T5 | — | high |
| 845 | 2026 | 微信小游戏 | 几何冲刺 | A2 | F4 | N-Comp | — | T2 | T1 | — | high |
| 846 | 2026 | 微信小游戏 | 别踩白块儿 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 847 | 2026 | 微信小游戏 | 剑与远征：启程 | A3 | F2 | N-Comp | — | T2 | T6 | — | high |
| 848 | 2026 | 微信小游戏 | 剑网3指尖江湖 | A2 | F1 | N-Comp | N-Rel | T2 | T3 | — | medium |
| 849 | 2026 | 微信小游戏 | 割绳子 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 850 | 2026 | 微信小游戏 | 动物餐厅 | A3 | F2 | N-Auto | N-Rel | T1 | T3 | — | high |
| 851 | 2026 | 微信小游戏 | 反应堆 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 852 | 2026 | 微信小游戏 | 变形金刚：地球之战 | A1 | F6 | N-Comp | N-Rel | T2 | T5 | — | medium |
| 853 | 2026 | 微信小游戏 | 古剑奇谭木语人 | A3 | F2 | N-Comp | N-Rel | T2 | T3 | — | medium |
| 854 | 2026 | 微信小游戏 | 古镜记 | A5 | F4 | N-Comp | — | T5 | T1 | — | high |
| 855 | 2026 | 微信小游戏 | 叫我万岁爷 | A4 | F2 | N-Comp | — | T6 | T2 | — | high |
| 856 | 2026 | 微信小游戏 | 史莱姆与地下城 | A5 | F3 | N-Comp | — | T5 | T2 | — | high |
| 857 | 2026 | 微信小游戏 | 合成大西瓜 | A4 | F3 | N-Auto | N-Comp | T1 | T5 | — | medium |
| 858 | 2026 | 微信小游戏 | 吞噬星空：黎明 | A3 | F2 | N-Comp | N-Rel | T2 | T3 | — | medium |
| 859 | 2026 | 微信小游戏 | 咸鱼之王 | A3 | F2 | N-Comp | — | T1 | T2 | — | high |
| 860 | 2026 | 微信小游戏 | 喜羊羊与灰太狼 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 861 | 2026 | 微信小游戏 | 《围棋》 | A1 | F4 | N-Comp | — | T2 | T5 | — | high |
| 862 | 2026 | 微信小游戏 | 《地下城堡2》 | A2 | F4 | N-Comp | — | T5 | T2、T6 | — | high |
| 863 | 2026 | 微信小游戏 | 《地铁跑酷》 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 864 | 2026 | 微信小游戏 | 《塔防精灵》 | A4 | F3 | N-Comp | — | T5 | T2、T6 | — | high |
| 865 | 2026 | 微信小游戏 | 《墨迹大侠》 | A2 | F1 | N-Comp | — | T1 | T2 | — | high |
| 866 | 2026 | 微信小游戏 | 《大话西游》 | A2 | F6 | N-Rel | N-Comp | T4 | T2、T1 | real | high |
| 867 | 2026 | 微信小游戏 | 《大钢琴》 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 868 | 2026 | 微信小游戏 | 《天天炫斗》 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 869 | 2026 | 微信小游戏 | 《天天爱消除》 | A4 | F4 | N-Auto | N-Comp | T1 | T6 | — | high |
| 870 | 2026 | 微信小游戏 | 《天天过马路》 | A2 | F4 | N-Comp | — | T2 | T1 | — | high |
| 871 | 2026 | 微信小游戏 | 《天天酷跑》 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 872 | 2026 | 微信小游戏 | 《天涯明月刀》 | A6 | F5 | N-Rel | N-Comp、N-Auto | T3 | T2、T4 | mixed | high |
| 873 | 2026 | 微信小游戏 | 《天龙八部手游》 | A2 | F6 | N-Rel | N-Comp | T4 | T2、T3 | real | high |
| 874 | 2026 | 微信小游戏 | 《太吾绘卷》 | A5 | F3 | N-Comp | N-Auto | T5 | T6、T2 | — | high |
| 875 | 2026 | 微信小游戏 | 《奇迹暖暖》 | A4 | F5 | N-Rel | N-Comp、N-Auto | T3 | T2、T1 | virtual | high |
| 876 | 2026 | 微信小游戏 | 《奥拉星》 | A3 | F2 | N-Rel | N-Comp | T3 | T2、T5 | virtual | high |
| 877 | 2026 | 微信小游戏 | 《奥比岛：梦想国度》 | A4 | F6 | N-Rel | N-Auto | T4 | T3、T1 | mixed | high |
| 878 | 2026 | 微信小游戏 | 《奥特曼系列》 | A2 | F1 | N-Comp | N-Rel | T2 | T1、T3 | — | high |
| 879 | 2026 | 微信小游戏 | 《女皇陛下》 | A4 | F5 | N-Rel | N-Comp、N-Auto | T3 | T6、T2 | virtual | high |
| 880 | 2026 | 微信小游戏 | 《孙美琪疑案》 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 881 | 2026 | 微信小游戏 | 宫廷计 | A6 | F5 | N-Rel | N-Comp | T3 | T2 | virtual | high |
| 882 | 2026 | 微信小游戏 | 宾果消消消 | A4 | F4 | N-Auto | N-Comp | T1 | T5 | — | high |
| 883 | 2026 | 微信小游戏 | 对对碰 | A4 | F4 | N-Auto | N-Comp | T1 | T5 | — | high |
| 884 | 2026 | 微信小游戏 | 寻道大千 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 885 | 2026 | 微信小游戏 | 射雕 | A5 | F5 | N-Auto | N-Comp、N-Rel | T1 | T3、T5 | — | medium |
| 886 | 2026 | 微信小游戏 | 小小蚁国 | A4 | F6 | N-Rel | N-Comp | T4 | T6、T2 | real | high |
| 887 | 2026 | 微信小游戏 | 小黄人快跑 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 888 | 2026 | 微信小游戏 | 巨兽战场 | A1 | F6 | N-Rel | N-Comp | T4 | T6、T2 | real | high |
| 889 | 2026 | 微信小游戏 | 幻之封神 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 890 | 2026 | 微信小游戏 | 开心农场 | A4 | F6 | N-Rel | N-Comp、N-Auto | T4 | T6、T1 | real | high |
| 891 | 2026 | 微信小游戏 | 开心消消乐 | A4 | F4 | N-Auto | N-Comp | T1 | T5 | — | high |
| 892 | 2026 | 微信小游戏 | 弹壳特攻队 | A2 | F1 | N-Comp | — | T1 | T2 | — | high |
| 893 | 2026 | 微信小游戏 | 征途 | A1 | F6 | N-Rel | N-Comp | T4 | T2 | real | high |
| 894 | 2026 | 微信小游戏 | 御龙在天 | A1 | F6 | N-Rel | N-Comp | T4 | T2 | real | high |
| 895 | 2026 | 微信小游戏 | 忍者必须死3 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 896 | 2026 | 微信小游戏 | 恋与制作人 | A6 | F5 | N-Rel | — | T3 | T1 | virtual | high |
| 897 | 2026 | 微信小游戏 | 恐怖奶奶 | A5 | F4 | N-Comp | — | T5 | T1 | — | high |
| 898 | 2026 | 微信小游戏 | 愤怒的小鸟2 | A4 | F4 | N-Auto | N-Comp | T1 | T5 | — | high |
| 899 | 2026 | 微信小游戏 | 我的世界 | A4 | F3 | N-Auto | N-Comp、N-Rel | T6 | T1、T5 | — | high |
| 900 | 2026 | 微信小游戏 | 我的安吉拉 | A6 | F5 | N-Rel | N-Auto | T3 | T1 | virtual | high |
| 901 | 2026 | 微信小游戏 | 我的汤姆猫 | A3 | F5 | N-Rel | N-Auto | T3 | T1 | virtual | high |
| 902 | 2026 | 微信小游戏 | 我飞刀玩得贼6 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 903 | 2026 | 微信小游戏 | 战火与永恒 | A4 | F6 | N-Rel | N-Comp | T4 | T6 | real | high |
| 904 | 2026 | 微信小游戏 | 战魂铭人 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 905 | 2026 | 微信小游戏 | 打地鼠 | A2 | F1 | N-Auto | N-Comp | T1 | — | — | medium |
| 906 | 2026 | 微信小游戏 | 找你妹 | A5 | F4 | N-Comp | — | T5 | T1 | — | medium |
| 907 | 2026 | 微信小游戏 | 找茬 | A5 | F4 | N-Comp | — | T5 | T1 | — | medium |
| 908 | 2026 | 微信小游戏 | 抓大鹅 | A4 | F4 | N-Comp | — | T5 | T6 | — | high |
| 909 | 2026 | 微信小游戏 | 捕鱼大作战 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 910 | 2026 | 微信小游戏 | 掌门下山 | A3 | F2 | N-Comp | N-Auto | T2 | T6 | — | medium |
| 911 | 2026 | 微信小游戏 | 搬砖模拟器 | A3 | F2 | N-Auto | — | T1 | — | — | high |
| 912 | 2026 | 微信小游戏 | 摩尔庄园 | A4 | F6 | N-Rel | N-Auto | T4 | T3、T6 | mixed | high |
| 913 | 2026 | 微信小游戏 | 文字修仙 | A3 | F2 | N-Auto | N-Comp | T1 | T2 | — | medium |
| 914 | 2026 | 微信小游戏 | 文字玩出花 | A5 | F4 | N-Comp | — | T5 | T1 | — | high |
| 915 | 2026 | 微信小游戏 | 文明与征服 | A4 | F6 | N-Rel | N-Comp | T4 | T6 | real | high |
| 916 | 2026 | 微信小游戏 | 斗破苍穹：斗帝之路 | A3 | F2 | N-Comp | N-Rel | T2 | T3 | — | medium |
| 917 | 2026 | 微信小游戏 | 斗罗大陆：魂师对决 | A4 | F3 | N-Comp | N-Rel | T5 | T2 | — | medium |
| 918 | 2026 | 微信小游戏 | 旅者之憩 | A4 | F3 | N-Auto | N-Comp | T6 | T1 | — | high |
| 919 | 2026 | 微信小游戏 | 旅行青蛙 | A3 | F5 | N-Rel | N-Auto | T3 | T1 | virtual | high |
| 920 | 2026 | 微信小游戏 | 无尽的拉格朗日 | A4 | F6 | N-Rel | N-Comp | T4 | T6 | real | high |
| 921 | 2026 | 微信小游戏 | 明日之后 | A7 | F6 | N-Rel | N-Comp | T4 | T6 | real | high |
| 922 | 2026 | 微信小游戏 | 暗黑修仙 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 923 | 2026 | 微信小游戏 | 曙光英雄 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 924 | 2026 | 微信小游戏 | 机械迷城 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 925 | 2026 | 微信小游戏 | 梦幻家园 | A4 | F4 | N-Auto | N-Rel | T1 | T6、T3 | — | high |
| 926 | 2026 | 微信小游戏 | 梦幻花园 | A4 | F4 | N-Auto | N-Rel | T1 | T6、T3 | — | high |
| 927 | 2026 | 微信小游戏 | 梦幻西游 | A7 | F6 | N-Rel | N-Comp | T4 | T2 | real | high |
| 928 | 2026 | 微信小游戏 | 梦想小镇 | A4 | F3 | N-Auto | N-Comp | T6 | T1 | — | high |
| 929 | 2026 | 微信小游戏 | 植物大战僵尸2 | A4 | F4 | N-Comp | — | T5 | T2 | — | high |
| 930 | 2026 | 微信小游戏 | 模拟城市：我是市长 | A4 | F3 | N-Auto | N-Comp | T6 | T1 | — | high |
| 931 | 2026 | 微信小游戏 | 次神光之觉醒 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 932 | 2026 | 微信小游戏 | 欢乐五子棋 | A1 | F4 | N-Comp | N-Rel | T2 | T5 | — | high |
| 933 | 2026 | 微信小游戏 | 欢乐农场 | A4 | F2 | N-Auto | — | T1 | T6 | — | high |
| 934 | 2026 | 微信小游戏 | 欢乐斗地主 | A1 | F4 | N-Comp | N-Rel | T2 | T1 | — | high |
| 935 | 2026 | 微信小游戏 | 欢乐消消消 | A5 | F4 | N-Auto | N-Comp | T1 | T5 | — | high |
| 936 | 2026 | 微信小游戏 | 欢乐麻将 | A1 | F4 | N-Comp | N-Rel | T2 | T1 | — | high |
| 937 | 2026 | 微信小游戏 | 水果忍者 | A2 | F1 | N-Auto | N-Comp | T1 | — | — | high |
| 938 | 2026 | 微信小游戏 | 汉字找茬王 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 939 | 2026 | 微信小游戏 | 江南百景图 | A4 | F3 | N-Auto | N-Rel | T6 | T1、T3 | — | high |
| 940 | 2026 | 微信小游戏 | 汤姆猫跑酷 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 941 | 2026 | 微信小游戏 | 《泡泡龙》 | A4 | F4 | N-Auto | N-Comp | T1 | T5 | — | high |
| 942 | 2026 | 微信小游戏 | 《泰拉瑞亚》 | A5 | F3 | N-Auto | N-Comp | T6 | T5、T1 | — | high |
| 943 | 2026 | 微信小游戏 | 《洛克王国世界》 | A2 | F2 | N-Rel | N-Comp | T3 | T2 | virtual | high |
| 944 | 2026 | 微信小游戏 | 《洪荒文明》 | A4 | F6 | N-Rel | N-Comp | T4 | T6、T2 | real | high |
| 945 | 2026 | 微信小游戏 | 《流言侦探》 | A6 | F5 | N-Auto | N-Comp | T1 | T5 | — | medium |
| 946 | 2026 | 微信小游戏 | 《海绵宝宝：蟹堡王》 | A4 | F2 | N-Comp | N-Auto | T6 | T1 | — | high |
| 947 | 2026 | 微信小游戏 | 《涂鸦上帝》 | A5 | F3 | N-Auto | N-Comp | T5 | T1 | — | high |
| 948 | 2026 | 微信小游戏 | 《消灭星星》 | A4 | F4 | N-Auto | N-Comp | T1 | T5 | — | high |
| 949 | 2026 | 微信小游戏 | 《深海水族馆》 | A3 | F2 | N-Auto | N-Rel | T1 | T3 | — | high |
| 950 | 2026 | 微信小游戏 | 《游戏王：决斗链接》 | A1 | F3 | N-Comp | N-Rel | T2 | T5、T4 | — | high |
| 951 | 2026 | 微信小游戏 | 《滚动的天空》 | A2 | F4 | N-Comp | — | T2 | T1 | — | high |
| 952 | 2026 | 微信小游戏 | 《热血传奇》 | A1 | F1 | N-Rel | N-Comp | T4 | T2 | real | high |
| 953 | 2026 | 微信小游戏 | 《熊出没之熊大快跑》 | A2 | F4 | N-Comp | — | T2 | T1 | — | high |
| 954 | 2026 | 微信小游戏 | 《爆炒江湖》 | A4 | F2 | N-Comp | N-Auto | T6 | T1 | — | high |
| 955 | 2026 | 微信小游戏 | 《狼人杀》 | A1 | F6 | N-Rel | N-Comp | T4 | T5 | real | high |
| 956 | 2026 | 微信小游戏 | 《猎梦宿舍》 | A4 | F4 | N-Comp | — | T6 | T2 | — | high |
| 957 | 2026 | 微信小游戏 | 《猫和老鼠》 | A1 | F1 | N-Comp | N-Rel | T2 | T1、T4 | — | high |
| 958 | 2026 | 微信小游戏 | 《王牌战士》 | A1 | F1 | N-Comp | N-Rel | T2 | T4 | — | high |
| 959 | 2026 | 微信小游戏 | 《球球大作战》 | A1 | F2 | N-Comp | N-Rel | T2 | T4 | — | high |
| 960 | 2026 | 微信小游戏 | 《画境长恨歌》 | A5 | F5 | N-Auto | N-Comp | T5 | T1 | — | high |
| 961 | 2026 | 微信小游戏 | 画火柴人 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 962 | 2026 | 微信小游戏 | 疯狂骑士团 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 963 | 2026 | 微信小游戏 | 看谁能通关 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 964 | 2026 | 微信小游戏 | 祖玛 | A4 | F1 | N-Comp | — | T2 | T1 | — | high |
| 965 | 2026 | 微信小游戏 | 神之折纸 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 966 | 2026 | 微信小游戏 | 神庙逃亡 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 967 | 2026 | 微信小游戏 | 神武4 | A7 | F6 | N-Rel | N-Comp | T4 | T2 | real | high |
| 968 | 2026 | 微信小游戏 | 神雕侠侣2 | A6 | F5 | N-Rel | N-Comp | T3 | T4 | mixed | high |
| 969 | 2026 | 微信小游戏 | 穿越火线：枪战王者 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 970 | 2026 | 微信小游戏 | 笑傲江湖 | A6 | F5 | N-Rel | N-Comp | T3 | T2 | virtual | high |
| 971 | 2026 | 微信小游戏 | 第五人格 | A1 | F1 | N-Comp | N-Rel | T2 | T5 | — | high |
| 972 | 2026 | 微信小游戏 | 第五件遗留物 | A6 | F5 | N-Rel | N-Comp | T3 | T5 | virtual | high |
| 973 | 2026 | 微信小游戏 | 红月战神 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 974 | 2026 | 微信小游戏 | 纪念碑谷2 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 975 | 2026 | 微信小游戏 | 纸人 | A5 | F5 | N-Comp | N-Rel | T5 | T3 | — | medium |
| 976 | 2026 | 微信小游戏 | 纸嫁衣 | A5 | F5 | N-Comp | N-Rel | T5 | T3 | — | medium |
| 977 | 2026 | 微信小游戏 | 终结战场 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 978 | 2026 | 微信小游戏 | 缤纷彩带 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 979 | 2026 | 微信小游戏 | 羊了个羊 | A5 | F4 | N-Comp | — | T2 | T5 | — | high |
| 980 | 2026 | 微信小游戏 | 脑洞大师 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 981 | 2026 | 微信小游戏 | 脑点子 | A5 | F4 | N-Auto | N-Comp | T5 | T1 | — | high |
| 982 | 2026 | 微信小游戏 | 英雄杀 | A1 | F6 | N-Comp | N-Rel | T2 | T4 | — | high |
| 983 | 2026 | 微信小游戏 | 荒野乱斗 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 984 | 2026 | 微信小游戏 | 荒野行动 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 985 | 2026 | 微信小游戏 | 谁是卧底 | A1 | F6 | N-Rel | N-Comp | T4 | T5 | real | high |
| 986 | 2026 | 微信小游戏 | 象棋 | A1 | F4 | N-Comp | — | T2 | T5 | — | high |
| 987 | 2026 | 微信小游戏 | 赛尔号 | A3 | F2 | N-Comp | N-Rel | T2 | T3 | — | high |
| 988 | 2026 | 微信小游戏 | 跳一跳 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 989 | 2026 | 微信小游戏 | 跳舞的线 | A2 | F4 | N-Comp | N-Auto | T2 | T1 | — | medium |
| 990 | 2026 | 微信小游戏 | 躺平发育 | A4 | F3 | N-Comp | — | T6 | T2 | — | high |
| 991 | 2026 | 微信小游戏 | 轩辕剑龙舞云山 | A2 | F5 | N-Rel | N-Comp | T3 | T2 | virtual | high |
| 992 | 2026 | 微信小游戏 | 这城有良田 | A4 | F3 | N-Comp | N-Auto | T6 | T2 | — | high |
| 993 | 2026 | 微信小游戏 | 连连看 | A5 | F4 | N-Comp | — | T2 | T1 | — | high |
| 994 | 2026 | 微信小游戏 | 迷你世界 | A4 | F3 | N-Auto | N-Rel | T6 | T4 | — | high |
| 995 | 2026 | 微信小游戏 | 迷失立方体 | A5 | F4 | N-Auto | N-Comp | T5 | T1 | — | high |
| 996 | 2026 | 微信小游戏 | 迷雾大陆 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 997 | 2026 | 微信小游戏 | 逆水寒 | A6 | F5 | N-Rel | N-Comp | T3 | T4、T2 | mixed | high |
| 998 | 2026 | 微信小游戏 | 遇见逆水寒 | A6 | F5 | N-Rel | — | T3 | — | virtual | high |
| 999 | 2026 | 微信小游戏 | 道天录 | A4 | F3 | N-Comp | — | T6 | T2 | — | high |
| 1000 | 2026 | 微信小游戏 | 金铲铲之战 | A4 | F3 | N-Comp | — | T2 | T5 | — | high |
| 1001 | 2026 | 微信小游戏 | 闪耀暖暖 | A5 | F4 | N-Comp | N-Rel | T2 | T3 | — | high |
| 1002 | 2026 | 微信小游戏 | 问道 | A2 | F2 | N-Comp | N-Rel | T2 | T4 | — | high |
| 1003 | 2026 | 微信小游戏 | 阴阳师：百闻牌 | A1 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1004 | 2026 | 微信小游戏 | 隐形守护者 | A6 | F5 | N-Rel | N-Comp | T3 | T5 | virtual | high |
| 1005 | 2026 | 微信小游戏 | 非人学园 | A1 | F1 | N-Comp | N-Rel | T2 | T1 | — | high |
| 1006 | 2026 | 微信小游戏 | 飞行棋大作战 | A1 | F6 | N-Rel | N-Comp | T4 | T1 | real | medium |
| 1007 | 2026 | 微信小游戏 | 饥荒：新家园 | A2 | F4 | N-Comp | N-Auto | T6 | T2 | — | high |
| 1008 | 2026 | 微信小游戏 | 香肠派对 | A1 | F1 | N-Comp | N-Rel | T2 | T1 | — | high |
| 1009 | 2026 | 微信小游戏 | 鬼谷八荒 | A2 | F2 | N-Comp | N-Auto | T2 | T5 | — | high |
| 1010 | 2026 | 微信小游戏 | 鳄鱼小顽皮爱洗澡 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 1011 | 2026 | 微信小游戏 | 鹿鼎记 | A6 | F5 | N-Rel | N-Auto | T3 | T1 | virtual | high |
| 1012 | 2026 | 微信小游戏 | 黄金矿工 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1013 | 2026 | 微信小游戏 | 黎明觉醒：生机 | A2 | F4 | N-Comp | N-Auto | T6 | T2 | — | high |
| 1014 | 2025 | 微信小游戏 | NBA 2K Online 2 | A1 | F1 | N-Comp | N-Rel | T2 | T4 | — | high |
| 1015 | 2025 | 微信小游戏 | 三国：谋定天下 | A1 | F6 | N-Rel | N-Comp | T4 | T6 | real | high |
| 1016 | 2025 | 微信小游戏 | 以闪亮之名 | A5 | F4 | N-Comp | N-Rel | T2 | T3 | — | high |
| 1017 | 2025 | 微信小游戏 | 元梦之星 | A1 | F6 | N-Rel | N-Comp | T4 | T1 | real | medium |
| 1018 | 2025 | 微信小游戏 | 光与夜之恋 | A6 | F5 | N-Rel | — | T3 | — | virtual | high |
| 1019 | 2025 | 微信小游戏 | 冒险大作战 | A3 | F2 | N-Comp | N-Auto | T2 | T1 | — | medium |
| 1020 | 2025 | 微信小游戏 | 冒险岛：枫之传说 | A2 | F1 | N-Comp | N-Rel | T2 | T1 | — | high |
| 1021 | 2025 | 微信小游戏 | 凡人修仙传：人界篇 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1022 | 2025 | 微信小游戏 | 剑与远征 | A3 | F2 | N-Comp | — | T2 | T5 | — | high |
| 1023 | 2025 | 微信小游戏 | 劲舞团 | A1 | F6 | N-Comp | N-Rel | T2 | T4 | — | high |
| 1024 | 2025 | 微信小游戏 | 原神（云游戏） | A5 | F4 | N-Comp | N-Rel | T2 | T3 | — | high |
| 1025 | 2025 | 微信小游戏 | 向僵尸开炮 | A2 | F1 | N-Comp | — | T1 | T5 | — | high |
| 1026 | 2025 | 微信小游戏 | 吞噬星空 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1027 | 2025 | 微信小游戏 | 和平精英（小程序版） | A1 | F1 | N-Comp | N-Rel | T2 | T4 | — | high |
| 1028 | 2025 | 微信小游戏 | 四川麻将 | A1 | F4 | N-Comp | N-Rel | T2 | T4 | — | high |
| 1029 | 2025 | 微信小游戏 | 塔瑞斯世界 | A2 | F4 | N-Comp | N-Rel | T2 | T4 | — | high |
| 1030 | 2025 | 微信小游戏 | 大秦帝国之帝国崛起 | A1 | F6 | N-Rel | N-Comp | T4 | T6 | real | high |
| 1031 | 2025 | 微信小游戏 | 完美世界：诸神之战 | A2 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1032 | 2025 | 微信小游戏 | 小鸡舰队 | A2 | F1 | N-Comp | — | T1 | T5 | — | high |
| 1033 | 2025 | 微信小游戏 | 幻兽爱合成 | A4 | F3 | N-Comp | N-Auto | T6 | T1 | — | medium |
| 1034 | 2025 | 微信小游戏 | 广东麻将 | A1 | F4 | N-Comp | N-Rel | T2 | T4 | — | high |
| 1035 | 2025 | 微信小游戏 | 征途2（小程序版） | A1 | F6 | N-Rel | N-Comp | T4 | T2 | real | high |
| 1036 | 2025 | 微信小游戏 | 拳皇97（小程序版） | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1037 | 2025 | 微信小游戏 | 挨饿荒野 | A5 | F4 | N-Comp | N-Auto | T6 | T1 | — | medium |
| 1038 | 2025 | 微信小游戏 | 斗牛 | A1 | F4 | N-Comp | N-Rel | T2 | T4 | — | high |
| 1039 | 2025 | 微信小游戏 | 斗罗大陆：史莱克学院 | A3 | F2 | N-Comp | N-Rel | T2 | T3 | — | high |
| 1040 | 2025 | 微信小游戏 | 新笑傲江湖 | A2 | F2 | N-Comp | N-Rel | T2 | T3、T4 | — | high |
| 1041 | 2025 | 微信小游戏 | 无尽对决 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1042 | 2025 | 微信小游戏 | 明日之后（小程序版） | A3 | F2 | N-Comp | — | T6 | T2 | — | high |
| 1043 | 2025 | 微信小游戏 | 星穹铁道（云游戏） | A2 | F1 | N-Comp | N-Rel | T2 | T3、T5 | — | high |
| 1044 | 2025 | 微信小游戏 | 植物大战僵尸 | A4 | F4 | N-Comp | — | T5 | T6 | — | high |
| 1045 | 2025 | 微信小游戏 | 欢乐升级 | A1 | F4 | N-Comp | — | T2 | T5 | — | high |
| 1046 | 2025 | 微信小游戏 | 汉家江湖 | A2 | F1 | N-Comp | N-Rel | T2 | T5、T3 | — | high |
| 1047 | 2025 | 微信小游戏 | 洪荒自动棋 | A5 | F3 | N-Comp | — | T5 | T2 | — | high |
| 1048 | 2025 | 微信小游戏 | 流浪超市 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1049 | 2025 | 微信小游戏 | 海贼王：热血航线 | A2 | F1 | N-Comp | N-Rel | T2 | T3 | — | high |
| 1050 | 2025 | 微信小游戏 | 火影忍者（小程序版） | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1051 | 2025 | 微信小游戏 | 猎魂觉醒 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1052 | 2025 | 微信小游戏 | 率土之滨 | A1 | F6 | N-Rel | N-Comp | T4 | T6、T2 | real | high |
| 1053 | 2025 | 微信小游戏 | 王者荣耀（极速版） | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1054 | 2025 | 微信小游戏 | 王铲铲的致富之路 | A3 | F2 | N-Comp | — | T6 | T1 | — | high |
| 1055 | 2025 | 微信小游戏 | 生化危机（小程序版） | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1056 | 2025 | 微信小游戏 | 白荆回廊 | A2 | F1 | N-Comp | — | T5 | T2 | — | high |
| 1057 | 2025 | 微信小游戏 | 盗墓笔记 | A5 | F4 | N-Comp | N-Rel | T5 | T3 | — | high |
| 1058 | 2025 | 微信小游戏 | 穿越火线（小程序版） | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1059 | 2025 | 微信小游戏 | 第五人格（小程序版） | A1 | F4 | N-Comp | — | T2 | T5 | — | high |
| 1060 | 2025 | 微信小游戏 | 红月 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1061 | 2025 | 微信小游戏 | 《蛋仔派对》— 类型:操控闪避+对抗 | A1 | F6 | N-Comp | N-Rel | T2 | T4 | — | high |
| 1062 | 2025 | 微信小游戏 | 《街头篮球》— 类型:对抗竞技+操控 | A1 | F1 | N-Comp | — | T2 | — | — | high |
| 1063 | 2025 | 微信小游戏 | 《街头霸王（小程序版）》— 类型:对 | A1 | F1 | N-Comp | — | T2 | T5 | — | high |
| 1064 | 2025 | 微信小游戏 | 《跑得快》— 类型:构建组合+出牌决 | A1 | F4 | N-Comp | — | T2 | T5 | — | high |
| 1065 | 2025 | 微信小游戏 | 《跑跑卡丁车》— 类型:操控载具+竞 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1066 | 2025 | 微信小游戏 | 《逆战：未来》— 类型:射击对抗+构 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 1067 | 2025 | 微信小游戏 | 《鬼吹灯之精绝古城》— 类型:探索空 | A2 | F4 | N-Comp | — | T2 | T5 | — | high |
| 1068 | 2025 | 微信小游戏 | 《魂斗罗：归来》— 类型:射击闪避+ | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1069 | 2025 | 微信小游戏 | 《黑暗笔录》— 类型:探索空间+解谜 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 1070 | 2024 | 微信小游戏 | 《三国吧兄弟》— 类型:割草闪避+构 | A2 | F1 | N-Comp | — | T1 | T2 | — | high |
| 1071 | 2024 | 微信小游戏 | 《仙剑奇侠传之新的开始》— 类型:构 | A2 | F4 | N-Comp | N-Rel | T2 | T3 | — | medium |
| 1072 | 2024 | 微信小游戏 | 《侠客梦》— 类型:割草闪避+构建技 | A2 | F1 | N-Comp | — | T1 | T2 | — | high |
| 1073 | 2024 | 微信小游戏 | 《保卫向日葵》— 类型:布局规划+即 | A4 | F4 | N-Comp | — | T6 | T5 | — | high |
| 1074 | 2024 | 微信小游戏 | 《冲一冲专家》— 类型:操控闪避+节 | A2 | F4 | N-Comp | — | T1 | T2 | — | high |
| 1075 | 2024 | 微信小游戏 | 《出发吧麦芬》— 类型:放置收集+构 | A3 | F2 | N-Comp | N-Rel | T2 | T4 | — | medium |
| 1076 | 2024 | 微信小游戏 | 《叫我大掌柜》— 类型:布局规划+优 | A4 | F2 | N-Comp | N-Auto | T6 | T2 | — | medium |
| 1077 | 2024 | 微信小游戏 | 《地下城与领主》— 类型:构建技能+ | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1078 | 2024 | 微信小游戏 | 《墨斗》— 类型:操控战斗+预判闪避 | A1 | F1 | N-Comp | — | T2 | T5 | — | high |
| 1079 | 2024 | 微信小游戏 | 《大侠立志传》— 类型:探索发现+构 | A5 | F4 | N-Auto | N-Comp | T6 | T5 | — | medium |
| 1080 | 2024 | 微信小游戏 | 《寻宝大冒险》— 类型:收集资源+概 | A3 | F2 | N-Comp | N-Auto | T1 | T2 | — | medium |
| 1081 | 2024 | 微信小游戏 | 小鸡舰队出击 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1082 | 2024 | 微信小游戏 | 我是大东家 | A4 | F2 | N-Comp | N-Auto | T6 | T2 | — | high |
| 1083 | 2024 | 微信小游戏 | 掌门江湖路 | A3 | F2 | N-Comp | — | T2 | T6 | — | high |
| 1084 | 2024 | 微信小游戏 | 整蛊邻居 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 1085 | 2024 | 微信小游戏 | 无尽冬日 | A1 | F6 | N-Rel | N-Comp | T4 | T6 | real | high |
| 1086 | 2024 | 微信小游戏 | 星际大作战 | A2 | F1 | N-Comp | N-Auto | T1 | T2 | — | medium |
| 1087 | 2024 | 微信小游戏 | 暗黑觉醒 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1088 | 2024 | 微信小游戏 | 欢乐坦克大战 | A1 | F1 | N-Comp | N-Rel | T2 | T1 | — | high |
| 1089 | 2024 | 微信小游戏 | 欢乐钓鱼大师 | A3 | F2 | N-Comp | N-Auto | T1 | T2 | — | medium |
| 1090 | 2024 | 微信小游戏 | 洛克王国 | A3 | F2 | N-Comp | N-Rel | T2 | T3 | — | medium |
| 1091 | 2024 | 微信小游戏 | 洪荒觉醒 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1092 | 2024 | 微信小游戏 | 灌篮高手 | A1 | F1 | N-Comp | N-Rel | T2 | T4 | — | high |
| 1093 | 2024 | 微信小游戏 | 灵剑仙师 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1094 | 2024 | 微信小游戏 | 灵魂序章 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1095 | 2024 | 微信小游戏 | 烧脑瓶子 | A4 | F4 | N-Comp | N-Auto | T5 | T1 | — | high |
| 1096 | 2024 | 微信小游戏 | 百炼英雄 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1097 | 2024 | 微信小游戏 | 节奏大师 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1098 | 2024 | 微信小游戏 | 跃动小子 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1099 | 2024 | 微信小游戏 | 霓虹深渊：无限 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 1100 | 2024 | 微信小游戏 | 飞吧龙骑士 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1101 | 2024 | 微信小游戏 | 骑士冲啊 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1102 | 2024 | 微信小游戏 | 骑行去拉萨 | A3 | F2 | N-Auto | — | T1 | — | — | high |
| 1103 | 2023 | 微信小游戏 | 五子棋 | A1 | F4 | N-Comp | — | T2 | T5 | — | high |
| 1104 | 2023 | 微信小游戏 | 停车大师 | A4 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1105 | 2023 | 微信小游戏 | 全民打螺丝 | A4 | F4 | N-Auto | — | T1 | T6 | — | high |
| 1106 | 2023 | 微信小游戏 | 六边形消消乐 | A4 | F4 | N-Auto | — | T1 | T5 | — | high |
| 1107 | 2023 | 微信小游戏 | 军棋 | A1 | F4 | N-Comp | — | T2 | T5 | — | high |
| 1108 | 2023 | 微信小游戏 | 割草的哈利 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1109 | 2023 | 微信小游戏 | 功夫派 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1110 | 2023 | 微信小游戏 | 大富翁 | A1 | F6 | N-Comp | N-Rel | T2 | T4 | — | medium |
| 1111 | 2023 | 微信小游戏 | 奥比岛 | A4 | F5 | N-Rel | N-Auto | T4 | T3、T1 | mixed | high |
| 1112 | 2023 | 微信小游戏 | 小森生活 | A3 | F2 | N-Auto | — | T1 | T6 | — | high |
| 1113 | 2023 | 微信小游戏 | 小花仙 | A3 | F5 | N-Rel | N-Auto | T3 | T1 | virtual | high |
| 1114 | 2023 | 微信小游戏 | 我飞刀玩得真牛 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1115 | 2023 | 微信小游戏 | 扫雷 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1116 | 2023 | 微信小游戏 | 数独 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1117 | 2023 | 微信小游戏 | 斗兽棋 | A1 | F4 | N-Comp | — | T2 | T5 | — | high |
| 1118 | 2023 | 微信小游戏 | 水排序 | A4 | F4 | N-Auto | — | T1 | T6 | — | high |
| 1119 | 2023 | 微信小游戏 | 物理弹球 | A4 | F1 | N-Auto | — | T1 | — | — | high |
| 1120 | 2023 | 微信小游戏 | 猫旅馆物语 | A3 | F5 | N-Rel | N-Auto | T3 | T1 | virtual | high |
| 1121 | 2023 | 微信小游戏 | 玩梗找茬王 | A5 | F4 | N-Auto | — | T1 | T5 | — | high |
| 1122 | 2023 | 微信小游戏 | 皇室战争 | A1 | F1 | N-Comp | — | T2 | T5 | — | high |
| 1123 | 2023 | 微信小游戏 | 纪念碑谷 | A5 | F4 | N-Auto | — | T5 | T1 | — | high |
| 1124 | 2023 | 微信小游戏 | 见缝插针 | A2 | F4 | N-Comp | — | T2 | T1 | — | high |
| 1125 | 2023 | 微信小游戏 | 野兽领主：新世界 | A4 | F2 | N-Comp | N-Rel | T6 | T4 | — | high |
| 1126 | 2023 | 微信小游戏 | 钢琴块 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1127 | 2023 | 微信小游戏 | 飞行棋 | A1 | F6 | N-Rel | N-Comp | T4 | T1 | real | high |
| 1128 | 2022 | 微信小游戏 | 乌冬的旅店 | A4 | F3 | N-Auto | — | T6 | T1 | — | high |
| 1129 | 2022 | 微信小游戏 | 全民枪神 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1130 | 2022 | 微信小游戏 | 剧本杀 | A5 | F5 | N-Rel | N-Auto | T4 | T5 | mixed | high |
| 1131 | 2022 | 微信小游戏 | 动物快跑 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1132 | 2022 | 微信小游戏 | 原神 | A2 | F5 | N-Rel | N-Comp | T3 | T2 | virtual | high |
| 1133 | 2022 | 微信小游戏 | 召唤神龙 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1134 | 2022 | 微信小游戏 | 可口的披萨 | A4 | F4 | N-Comp | — | T6 | T2 | — | high |
| 1135 | 2022 | 微信小游戏 | 和平精英 | A1 | F1 | N-Comp | N-Rel | T2 | T4 | — | high |
| 1136 | 2022 | 微信小游戏 | 天天象棋 | A1 | F4 | N-Comp | — | T2 | T5 | — | high |
| 1137 | 2022 | 微信小游戏 | 天天足球 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1138 | 2022 | 微信小游戏 | 弹弹堂 | A1 | F1 | N-Comp | — | T2 | T5 | — | high |
| 1139 | 2022 | 微信小游戏 | 悦动音符 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1140 | 2022 | 微信小游戏 | 愤怒的小鸟 | A5 | F4 | N-Auto | — | T5 | T1 | — | high |
| 1141 | 2022 | 微信小游戏 | 房东模拟器 | A4 | F2 | N-Auto | N-Comp | T6 | T1 | — | high |
| 1142 | 2022 | 微信小游戏 | 拳皇97 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1143 | 2022 | 微信小游戏 | 摸鱼大作战 | A2 | F1 | N-Auto | N-Comp | T1 | — | — | medium |
| 1144 | 2022 | 微信小游戏 | 放置奇兵 | A3 | F2 | N-Comp | — | T2 | T5 | — | high |
| 1145 | 2022 | 微信小游戏 | 文字大冒险 | A6 | F5 | N-Auto | N-Comp | T1 | T5 | — | medium |
| 1146 | 2022 | 微信小游戏 | 文字大玩家 | A3 | F2 | N-Auto | N-Comp | T6 | T1 | — | high |
| 1147 | 2022 | 微信小游戏 | 文字梗传 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | high |
| 1148 | 2022 | 微信小游戏 | 文字生存者 | A5 | F4 | N-Comp | N-Auto | T5 | T6 | — | high |
| 1149 | 2022 | 微信小游戏 | 斗罗大陆 | A2 | F2 | N-Comp | N-Rel | T2 | T3 | — | high |
| 1150 | 2022 | 微信小游戏 | 星途 | A2 | F4 | N-Auto | N-Comp | T1 | — | — | high |
| 1151 | 2022 | 微信小游戏 | 暗区突围 | A1 | F1 | N-Comp | N-Rel | T2 | T4 | — | high |
| 1152 | 2022 | 微信小游戏 | 最强蜗牛 | A3 | F2 | N-Auto | N-Comp | T1 | T6 | — | high |
| 1153 | 2022 | 微信小游戏 | 枪火重生 | A2 | F1 | N-Comp | N-Rel | T2 | T5 | — | high |
| 1154 | 2022 | 微信小游戏 | 梦想城镇 | A4 | F3 | N-Auto | N-Comp | T6 | T1 | — | high |
| 1155 | 2022 | 微信小游戏 | 模拟城市 | A4 | F3 | N-Auto | N-Comp | T6 | T1 | — | high |
| 1156 | 2022 | 微信小游戏 | 欢乐六边形 | A4 | F4 | N-Comp | N-Auto | T5 | T1 | — | high |
| 1157 | 2022 | 微信小游戏 | 流浪方舟 | A1 | F3 | N-Comp | — | T2 | T5 | — | high |
| 1158 | 2022 | 微信小游戏 | 海岛奇兵 | A1 | F6 | N-Comp | N-Rel | T2 | T4 | — | high |
| 1159 | 2022 | 微信小游戏 | 消消乐 | A4 | F4 | N-Auto | N-Comp | T1 | T5 | — | medium |
| 1160 | 2022 | 微信小游戏 | 深海水怪 | A2 | F2 | N-Auto | N-Comp | T1 | T6 | — | high |
| 1161 | 2022 | 微信小游戏 | 火影忍者 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1162 | 2022 | 微信小游戏 | 王者荣耀 | A1 | F6 | N-Comp | — | T2 | T4 | — | high |
| 1163 | 2022 | 微信小游戏 | 穿越 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1164 | 2022 | 微信小游戏 | 篮球大师 | A4 | F2 | N-Comp | N-Auto | T6 | T2 | — | medium |
| 1165 | 2022 | 微信小游戏 | 纸嫁衣2奘铃村 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 1166 | 2022 | 微信小游戏 | 英雄联盟手游 | A1 | F6 | N-Comp | — | T2 | T4 | — | high |
| 1167 | 2022 | 微信小游戏 | 贪吃蛇大作战 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1168 | 2022 | 微信小游戏 | 车库倒车入库 | A4 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1169 | 2022 | 微信小游戏 | 这就是江湖 | A5 | F2 | N-Auto | N-Comp | T1 | T5 | — | medium |
| 1170 | 2022 | 微信小游戏 | 部落冲突 | A4 | F3 | N-Comp | N-Rel | T6 | T4、T2 | — | high |
| 1171 | 2022 | 微信小游戏 | 魂斗罗 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1172 | 2022 | 微信小游戏 | 麻将来了 | A1 | F4 | N-Comp | N-Rel | T2 | T4、T1 | — | medium |
| 1173 | 2021 | 微信小游戏 | QQ农场 | A3 | F2 | N-Comp | N-Rel | T6 | T4、T1 | — | medium |
| 1174 | 2021 | 微信小游戏 | 三国志幻想大陆 | A3 | F2 | N-Comp | N-Rel | T2 | T3 | — | medium |
| 1175 | 2021 | 微信小游戏 | 九天封神 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1176 | 2021 | 微信小游戏 | 仙剑奇侠传 | A2 | F4 | N-Comp | N-Rel | T2 | T3、T5 | — | medium |
| 1177 | 2021 | 微信小游戏 | 传奇世界 | A3 | F2 | N-Comp | N-Rel | T2 | T4、T1 | — | high |
| 1178 | 2021 | 微信小游戏 | 传奇霸业 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1179 | 2021 | 微信小游戏 | 俄罗斯方块 | A4 | F4 | N-Comp | — | T2 | T1 | — | high |
| 1180 | 2021 | 微信小游戏 | 修仙掌门人 | A4 | F2 | N-Comp | N-Auto | T6 | T2、T1 | — | medium |
| 1181 | 2021 | 微信小游戏 | 全民枪战 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1182 | 2021 | 微信小游戏 | 凡人修仙 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1183 | 2021 | 微信小游戏 | 原始传奇 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1184 | 2021 | 微信小游戏 | 大天使之剑 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1185 | 2021 | 微信小游戏 | 天天狼人 | A1 | F6 | N-Comp | N-Rel | T2 | T4 | — | medium |
| 1186 | 2021 | 微信小游戏 | 妄想山海 | A5 | F3 | N-Comp | N-Auto | T6 | T5 | — | medium |
| 1187 | 2021 | 微信小游戏 | 完美世界 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1188 | 2021 | 微信小游戏 | 宾果消消乐 | A4 | F4 | N-Auto | N-Comp | T1 | T5 | — | medium |
| 1189 | 2021 | 微信小游戏 | 密室逃脱 | A5 | F4 | N-Comp | — | T5 | — | — | high |
| 1190 | 2021 | 微信小游戏 | 弹球达人 | A4 | F3 | N-Auto | N-Comp | T1 | T5 | — | medium |
| 1191 | 2021 | 微信小游戏 | 御剑情缘 | A3 | F2 | N-Comp | N-Rel | T2 | T3 | — | medium |
| 1192 | 2021 | 微信小游戏 | 想不想修真 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1193 | 2021 | 微信小游戏 | 我功夫特牛 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1194 | 2021 | 微信小游戏 | 拼三张 | A1 | F6 | N-Comp | N-Rel | T2 | T4 | — | medium |
| 1195 | 2021 | 微信小游戏 | 捕鱼达人 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1196 | 2021 | 微信小游戏 | 放置江湖 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1197 | 2021 | 微信小游戏 | 文字三国 | A4 | F3 | N-Comp | — | T6 | T5 | — | high |
| 1198 | 2021 | 微信小游戏 | 斗破苍穹 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1199 | 2021 | 微信小游戏 | 昭和杂货店物语 | A3 | F5 | N-Rel | N-Auto | T3 | T1 | virtual | high |
| 1200 | 2021 | 微信小游戏 | 校花模拟器 | A3 | F5 | N-Rel | N-Comp | T3 | T2 | virtual | medium |
| 1201 | 2021 | 微信小游戏 | 泡泡精灵 | A2 | F4 | N-Auto | N-Comp | T1 | T5 | — | medium |
| 1202 | 2021 | 微信小游戏 | 消星星 | A2 | F4 | N-Auto | N-Comp | T1 | — | — | high |
| 1203 | 2021 | 微信小游戏 | 消灭病毒 | A2 | F1 | N-Comp | — | T1 | T2 | — | high |
| 1204 | 2021 | 微信小游戏 | 火拼连连看 | A2 | F4 | N-Comp | — | T2 | T1 | — | high |
| 1205 | 2021 | 微信小游戏 | 炸金花 | A1 | F6 | N-Comp | N-Rel | T2 | T4 | — | medium |
| 1206 | 2021 | 微信小游戏 | 猫咪公寓 | A3 | F5 | N-Rel | N-Auto | T3 | T1 | virtual | high |
| 1207 | 2021 | 微信小游戏 | 画线救救火柴人 | A5 | F4 | N-Comp | — | T5 | T1 | — | high |
| 1208 | 2021 | 微信小游戏 | 疯狂猜成语 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1209 | 2021 | 微信小游戏 | 疯狂猜歌 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1210 | 2021 | 微信小游戏 | 神手 | A2 | F1 | N-Comp | — | T1 | T2 | — | high |
| 1211 | 2021 | 微信小游戏 | 神脑洞 | A5 | F4 | N-Comp | — | T5 | T1 | — | high |
| 1212 | 2021 | 微信小游戏 | 穿越火线 | A1 | F1 | N-Comp | N-Rel | T2 | T1 | — | high |
| 1213 | 2021 | 微信小游戏 | 网吧模拟器 | A4 | F2 | N-Auto | N-Comp | T6 | T1 | — | medium |
| 1214 | 2021 | 微信小游戏 | 脑力大乱斗 | A5 | F4 | N-Comp | — | T5 | T1 | — | high |
| 1215 | 2021 | 微信小游戏 | 腾讯桌球 | A1 | F4 | N-Comp | — | T2 | T5 | — | high |
| 1216 | 2021 | 微信小游戏 | 英魂之刃 | A1 | F1 | N-Comp | N-Rel | T2 | T4 | — | high |
| 1217 | 2021 | 微信小游戏 | 荣耀大天使 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1218 | 2021 | 微信小游戏 | 蓝月传奇 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1219 | 2021 | 微信小游戏 | 诛仙 | A3 | F2 | N-Comp | N-Rel | T2 | T3 | — | medium |
| 1220 | 2021 | 微信小游戏 | 逃离公司 | A5 | F4 | N-Comp | — | T5 | T1 | — | high |
| 1221 | 2021 | 微信小游戏 | 钢琴块2 | A2 | F4 | N-Comp | — | T2 | T1 | — | high |
| 1222 | 2021 | 微信小游戏 | 锄大地 | A1 | F6 | N-Comp | N-Rel | T2 | T4 | — | high |
| 1223 | 2021 | 微信小游戏 | 隐藏的我的游戏母亲 | A5 | F4 | N-Auto | N-Comp | T5 | T1 | — | high |
| 1224 | 2020 | 微信小游戏 | 人群冲撞 | A1 | F6 | N-Comp | — | T2 | T1 | — | high |
| 1225 | 2020 | 微信小游戏 | 切切切 | A2 | F1 | N-Auto | N-Comp | T1 | — | — | high |
| 1226 | 2020 | 微信小游戏 | 列王的纷争 | A1 | F6 | N-Rel | N-Comp | T4 | T2、T6 | real | high |
| 1227 | 2020 | 微信小游戏 | 合并庄园 | A4 | F3 | N-Auto | N-Rel | T6 | T3、T1 | — | medium |
| 1228 | 2020 | 微信小游戏 | 合并龙 | A4 | F3 | N-Auto | N-Comp | T6 | T5、T1 | — | high |
| 1229 | 2020 | 微信小游戏 | 堆栈球 | A2 | F1 | N-Auto | N-Comp | T1 | — | — | high |
| 1230 | 2020 | 微信小游戏 | 帝国与谜题 | A2 | F4 | N-Comp | — | T2 | T5 | — | high |
| 1231 | 2020 | 微信小游戏 | 快乐玻璃杯 | A5 | F4 | N-Auto | N-Comp | T5 | T1 | — | high |
| 1232 | 2020 | 微信小游戏 | 恋爱球球 | A5 | F4 | N-Auto | N-Rel | T5 | T3、T1 | — | medium |
| 1233 | 2020 | 微信小游戏 | 成语消消消 | A5 | F4 | N-Auto | N-Comp | T5 | T1 | — | high |
| 1234 | 2020 | 微信小游戏 | 手机壳DIY | A4 | F3 | N-Auto | — | T6 | T1 | — | high |
| 1235 | 2020 | 微信小游戏 | 扎染大师 | A4 | F3 | N-Auto | — | T6 | T1 | — | high |
| 1236 | 2020 | 微信小游戏 | 托尼老师 | A4 | F3 | N-Auto | — | T6 | T1 | — | high |
| 1237 | 2020 | 微信小游戏 | 拥挤城市 | A1 | F6 | N-Comp | — | T2 | T1 | — | high |
| 1238 | 2020 | 微信小游戏 | 攻城掠地 | A1 | F6 | N-Rel | N-Comp | T4 | T2、T6 | real | high |
| 1239 | 2020 | 微信小游戏 | 救援大师 | A5 | F4 | N-Auto | N-Comp | T5 | T1 | — | high |
| 1240 | 2020 | 微信小游戏 | 文字拼图 | A5 | F4 | N-Auto | N-Comp | T5 | T1 | — | high |
| 1241 | 2020 | 微信小游戏 | 斑点巨人 | A3 | F2 | N-Auto | N-Comp | T1 | T2 | — | high |
| 1242 | 2020 | 微信小游戏 | 最强的大脑 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1243 | 2020 | 微信小游戏 | 权力的游戏 | A1 | F6 | N-Comp | N-Rel | T2 | T4 | — | medium |
| 1244 | 2020 | 微信小游戏 | 桥上跑 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1245 | 2020 | 微信小游戏 | 欢乐球球 | A2 | F1 | N-Comp | — | T1 | T2 | — | high |
| 1246 | 2020 | 微信小游戏 | 泡泡 | A6 | F1 | N-Auto | — | T1 | — | — | high |
| 1247 | 2020 | 微信小游戏 | 热血合击 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1248 | 2020 | 微信小游戏 | 班主任模拟器 | A5 | F4 | N-Auto | N-Comp | T1 | T5 | — | medium |
| 1249 | 2020 | 微信小游戏 | 美甲 | A4 | F3 | N-Auto | — | T1 | T6 | — | high |
| 1250 | 2020 | 微信小游戏 | 胖子变瘦子 | A5 | F2 | N-Auto | — | T1 | — | — | high |
| 1251 | 2020 | 微信小游戏 | 脑力测试 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1252 | 2020 | 微信小游戏 | 脑洞找茬 | A5 | F4 | N-Auto | N-Comp | T1 | T5 | — | medium |
| 1253 | 2020 | 微信小游戏 | 螺旋跳跃 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1254 | 2020 | 微信小游戏 | 行尸走肉 | A4 | F4 | N-Comp | — | T6 | T2 | — | high |
| 1255 | 2020 | 微信小游戏 | 解压玩具 | A6 | F1 | N-Auto | — | T1 | — | — | high |
| 1256 | 2020 | 微信小游戏 | 计数大师 | A1 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1257 | 2020 | 微信小游戏 | 金币大富翁 | A3 | F2 | N-Auto | N-Comp | T1 | T6 | — | high |
| 1258 | 2020 | 微信小游戏 | 铅笔冲刺 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1259 | 2020 | 微信小游戏 | 阿瓦隆之王 | A1 | F6 | N-Rel | N-Comp | T4 | T2、T6 | real | high |
| 1260 | 2020 | 微信小游戏 | 高人跑 | A5 | F2 | N-Auto | — | T1 | — | — | high |
| 1261 | 2020 | 微信小游戏 | 《高跟鞋》 | A3 | F2 | N-Auto | — | T1 | — | — | high |
| 1262 | 2019 | 微信小游戏 | 《1010!》 | A4 | F4 | N-Auto | N-Comp | T6 | T1 | — | medium |
| 1263 | 2019 | 微信小游戏 | 《保卫萝卜3》 | A4 | F4 | N-Comp | — | T5 | T6 | — | high |
| 1264 | 2019 | 微信小游戏 | 《全民奇迹MU》 | A3 | F2 | N-Comp | — | T2 | — | — | high |
| 1265 | 2019 | 微信小游戏 | 《六边形拼图》 | A4 | F4 | N-Auto | N-Comp | T6 | T1 | — | medium |
| 1266 | 2019 | 微信小游戏 | 《大家来找茬》 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1267 | 2019 | 微信小游戏 | 《天天打怪兽》 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1268 | 2019 | 微信小游戏 | 《天天斗地主》 | A1 | F6 | N-Comp | N-Rel | T2 | T4 | — | medium |
| 1269 | 2019 | 微信小游戏 | 《头脑王者》 | A1 | F6 | N-Comp | — | T2 | T5 | — | high |
| 1270 | 2019 | 微信小游戏 | 《少年三国志》 | A3 | F2 | N-Comp | — | T2 | T5 | — | high |
| 1271 | 2019 | 微信小游戏 | 《少年西游记》 | A3 | F2 | N-Comp | — | T2 | T5 | — | high |
| 1272 | 2019 | 微信小游戏 | 《屠龙破晓》 | A3 | F2 | N-Comp | — | T2 | — | — | high |
| 1273 | 2019 | 微信小游戏 | 《弹一弹》 | A4 | F3 | N-Auto | N-Comp | T1 | T6 | — | medium |
| 1274 | 2019 | 微信小游戏 | 《悠梦》 | A5 | F4 | N-Auto | N-Comp | T5 | T1 | — | medium |
| 1275 | 2019 | 微信小游戏 | 《成语接龙》 | A5 | F4 | N-Auto | N-Comp | T5 | T1 | — | medium |
| 1276 | 2019 | 微信小游戏 | 《成语消消乐》 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1277 | 2019 | 微信小游戏 | 《我切菜贼溜》 | A2 | F1 | N-Comp | — | T1 | T2 | — | high |
| 1278 | 2019 | 微信小游戏 | 《我削皮贼溜》 | A2 | F1 | N-Comp | — | T1 | T2 | — | high |
| 1279 | 2019 | 微信小游戏 | 《我叫MT4》 | A3 | F2 | N-Comp | N-Rel | T2 | T4 | — | medium |
| 1280 | 2019 | 微信小游戏 | 《我在7年后等你》 | A6 | F5 | N-Rel | N-Auto | T3 | T1 | virtual | high |
| 1281 | 2019 | 微信小游戏 | 我的大刀四十米 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1282 | 2019 | 微信小游戏 | 我走路贼6 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1283 | 2019 | 微信小游戏 | 挂机吧兄弟 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1284 | 2019 | 微信小游戏 | 捣蛋猪 | A5 | F4 | N-Comp | — | T5 | T6 | — | high |
| 1285 | 2019 | 微信小游戏 | 星途WeGoing | A1 | F6 | N-Comp | — | T2 | T1 | — | high |
| 1286 | 2019 | 微信小游戏 | 欢乐动物园 | A3 | F2 | N-Comp | N-Auto | T6 | T1 | — | medium |
| 1287 | 2019 | 微信小游戏 | 欢乐大乱斗 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1288 | 2019 | 微信小游戏 | 欢乐捕鱼 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1289 | 2019 | 微信小游戏 | 欢乐球吃球 | A1 | F1 | N-Comp | — | T2 | T4 | — | high |
| 1290 | 2019 | 微信小游戏 | 欢乐象棋 | A1 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1291 | 2019 | 微信小游戏 | 海盗来了 | A3 | F2 | N-Comp | N-Rel | T2 | T4 | — | medium |
| 1292 | 2019 | 微信小游戏 | 涂色花园 | A4 | F4 | N-Auto | — | T1 | T6 | — | high |
| 1293 | 2019 | 微信小游戏 | 热血街篮 | A1 | F1 | N-Comp | — | T2 | T4 | — | high |
| 1294 | 2019 | 微信小游戏 | 猜画小歌 | A5 | F6 | N-Comp | N-Rel | T5 | T4 | — | medium |
| 1295 | 2019 | 微信小游戏 | 猫咪后院 | A3 | F5 | N-Rel | N-Auto | T3 | T1 | virtual | high |
| 1296 | 2019 | 微信小游戏 | 王者传奇 | A3 | F2 | N-Comp | N-Rel | T2 | T4 | — | medium |
| 1297 | 2019 | 微信小游戏 | 疯狂猜图 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1298 | 2019 | 微信小游戏 | 空当接龙 | A4 | F4 | N-Comp | — | T5 | T6 | — | high |
| 1299 | 2019 | 微信小游戏 | 胡莱三国 | A1 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1300 | 2019 | 微信小游戏 | 蜘蛛纸牌 | A4 | F4 | N-Comp | — | T5 | T6 | — | high |
| 1301 | 2019 | 微信小游戏 | 贪吃蛇在线 | A1 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1302 | 2019 | 微信小游戏 | 跳跳球 | A2 | F4 | N-Comp | — | T2 | T1 | — | high |
| 1303 | 2019 | 微信小游戏 | 转转拼图 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1304 | 2019 | 微信小游戏 | 黑暗料理王 | A4 | F3 | N-Comp | N-Auto | T6 | T1、T5 | — | medium |
| 1305 | 2018 | 微信小游戏 | 主题医院 | A4 | F3 | N-Comp | — | T6 | T5 | — | high |
| 1306 | 2018 | 微信小游戏 | 修仙录 | A3 | F2 | N-Comp | N-Auto | T2 | T1 | — | medium |
| 1307 | 2018 | 微信小游戏 | 全民小镇 | A4 | F3 | N-Auto | N-Rel | T1 | T4、T6 | — | medium |
| 1308 | 2018 | 微信小游戏 | 几何大逃亡 | A1 | F4 | N-Comp | — | T2 | T1 | — | high |
| 1309 | 2018 | 微信小游戏 | 创业公司 | A4 | F3 | N-Comp | — | T6 | T2 | — | high |
| 1310 | 2018 | 微信小游戏 | 华容道 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1311 | 2018 | 微信小游戏 | 商业大亨 | A4 | F2 | N-Comp | — | T6 | T2 | — | high |
| 1312 | 2018 | 微信小游戏 | 坦克大战 | A2 | F1 | N-Comp | — | T2 | T5 | — | high |
| 1313 | 2018 | 微信小游戏 | 填字游戏 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1314 | 2018 | 微信小游戏 | 套圈圈 | A2 | F4 | N-Comp | — | T2 | T1 | — | high |
| 1315 | 2018 | 微信小游戏 | 射击 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1316 | 2018 | 微信小游戏 | 弹弓 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1317 | 2018 | 微信小游戏 | 弹球王者 | A5 | F3 | N-Comp | — | T2 | T1 | — | high |
| 1318 | 2018 | 微信小游戏 | 成语猜猜看 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1319 | 2018 | 微信小游戏 | 打字游戏 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1320 | 2018 | 微信小游戏 | 打砖块 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1321 | 2018 | 微信小游戏 | 打飞机 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1322 | 2018 | 微信小游戏 | 抓娃娃 | A5 | F4 | N-Comp | — | T1 | T5 | — | medium |
| 1323 | 2018 | 微信小游戏 | 损友圈 | A1 | F6 | N-Rel | N-Comp | T4 | T1 | real | high |
| 1324 | 2018 | 微信小游戏 | 接水管 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 1325 | 2018 | 微信小游戏 | 推箱子 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | high |
| 1326 | 2018 | 微信小游戏 | 方块弹珠 | A5 | F1 | N-Comp | — | T1 | T5 | — | medium |
| 1327 | 2018 | 微信小游戏 | 最强弹一弹 | A5 | F1 | N-Comp | — | T1 | T5 | — | high |
| 1328 | 2018 | 微信小游戏 | 最强飞刀手 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1329 | 2018 | 微信小游戏 | 武侠Q传 | A3 | F2 | N-Comp | N-Rel | T2 | T3 | — | medium |
| 1330 | 2018 | 微信小游戏 | 汉字听写 | A5 | F4 | N-Comp | N-Auto | T5 | T2 | — | high |
| 1331 | 2018 | 微信小游戏 | 点击英雄 | A3 | F2 | N-Comp | N-Auto | T1 | T2 | — | medium |
| 1332 | 2018 | 微信小游戏 | 爱消除 | A1 | F6 | N-Rel | N-Comp | T4 | T1 | real | high |
| 1333 | 2018 | 微信小游戏 | 猜歌名 | A5 | F4 | N-Comp | N-Rel | T5 | T3 | — | medium |
| 1334 | 2018 | 微信小游戏 | 翻滚球球 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1335 | 2018 | 微信小游戏 | 脑筋急转弯 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | high |
| 1336 | 2018 | 微信小游戏 | 诗词大会 | A5 | F6 | N-Comp | N-Rel | T2 | T4 | — | medium |
| 1337 | 2018 | 微信小游戏 | 谜语 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | high |
| 1338 | 2018 | 微信小游戏 | 贪玩蓝月 | A2 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1339 | 2018 | 微信小游戏 | 跑酷 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1340 | 2018 | 微信小游戏 | 跳跃 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1341 | 2018 | 微信小游戏 | 《躲避》 | A2 | F4 | N-Comp | — | T2 | T1 | — | high |
| 1342 | 2018 | 微信小游戏 | 《飞机大战》 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1343 | 2018 | 微信小游戏 | 《麻将》 | A1 | F4 | N-Comp | N-Rel | T2 | T4 | — | high |
| 1344 | 2017 | 微信小游戏 | 《两人麻将》 | A1 | F4 | N-Comp | — | T2 | T1 | — | high |
| 1345 | 2017 | 微信小游戏 | 《乒乓球》 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1346 | 2017 | 微信小游戏 | 《保皇》 | A1 | F4 | N-Comp | N-Rel | T2 | T4 | — | high |
| 1347 | 2017 | 微信小游戏 | 《全民打枪》 | A2 | F1 | N-Comp | N-Auto | T1 | T2 | — | medium |
| 1348 | 2017 | 微信小游戏 | 《全民飞机大战》 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1349 | 2017 | 微信小游戏 | 《冲顶大会》 | A1 | F6 | N-Comp | N-Rel | T2 | T4 | — | high |
| 1350 | 2017 | 微信小游戏 | 《千炮捕鱼》 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1351 | 2017 | 微信小游戏 | 《单机斗地主》 | A2 | F4 | N-Comp | N-Auto | T1 | T2 | — | medium |
| 1352 | 2017 | 微信小游戏 | 《双扣》 | A1 | F4 | N-Comp | N-Rel | T2 | T4 | — | high |
| 1353 | 2017 | 微信小游戏 | 《吃豆人》 | A2 | F4 | N-Comp | — | T2 | T1 | — | high |
| 1354 | 2017 | 微信小游戏 | 《四国军棋》 | A1 | F4 | N-Comp | N-Rel | T2 | T4 | — | high |
| 1355 | 2017 | 微信小游戏 | 《围住神经猫》 | A5 | F4 | N-Comp | — | T2 | T5 | — | high |
| 1356 | 2017 | 微信小游戏 | 《坦克风云》 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1357 | 2017 | 微信小游戏 | 《完美建楼》 | A4 | F4 | N-Comp | — | T2 | T1 | — | high |
| 1358 | 2017 | 微信小游戏 | 《小美斗地主》 | A2 | F4 | N-Comp | N-Rel | T2 | T3 | — | medium |
| 1359 | 2017 | 微信小游戏 | 《开心水族箱》 | A3 | F2 | N-Auto | N-Rel | T1 | T3 | — | high |
| 1360 | 2017 | 微信小游戏 | 《弹球大师》 | A4 | F4 | N-Comp | N-Auto | T1 | T2 | — | medium |
| 1361 | 2017 | 微信小游戏 | 强手棋 | A1 | F6 | N-Comp | N-Rel | T2 | T4 | — | high |
| 1362 | 2017 | 微信小游戏 | 德州扑克 | A1 | F6 | N-Comp | N-Rel | T2 | T5 | — | high |
| 1363 | 2017 | 微信小游戏 | 扎金花 | A1 | F6 | N-Comp | N-Rel | T2 | T5 | — | high |
| 1364 | 2017 | 微信小游戏 | 旋转跳跃 | A2 | F4 | N-Comp | — | T2 | T1 | — | high |
| 1365 | 2017 | 微信小游戏 | 星星消除 | A4 | F4 | N-Auto | N-Comp | T1 | T6 | — | high |
| 1366 | 2017 | 微信小游戏 | 最强飞刀 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1367 | 2017 | 微信小游戏 | 欢乐大作战 | A1 | F1 | N-Comp | N-Rel | T2 | T4 | — | high |
| 1368 | 2017 | 微信小游戏 | 欢乐德州 | A1 | F6 | N-Comp | N-Rel | T2 | T5 | — | high |
| 1369 | 2017 | 微信小游戏 | 欢乐泡泡龙 | A4 | F4 | N-Comp | — | T2 | T1 | — | high |
| 1370 | 2017 | 微信小游戏 | 疯狂打怪兽 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1371 | 2017 | 微信小游戏 | 百人牛牛 | A1 | F6 | N-Comp | N-Rel | T2 | T4 | — | high |
| 1372 | 2017 | 微信小游戏 | 看图猜词 | A5 | F4 | N-Comp | — | T5 | T1 | — | high |
| 1373 | 2017 | 微信小游戏 | 知识超人 | A5 | F4 | N-Comp | — | T2 | T5 | — | high |
| 1374 | 2017 | 微信小游戏 | 纸牌接龙 | A4 | F4 | N-Auto | N-Comp | T1 | T6 | — | high |
| 1375 | 2017 | 微信小游戏 | 经典斗地主 | A1 | F6 | N-Comp | N-Rel | T2 | T5 | — | high |
| 1376 | 2017 | 微信小游戏 | 翻转棋 | A1 | F4 | N-Comp | N-Rel | T2 | T5 | — | high |
| 1377 | 2017 | 微信小游戏 | 葵花斗地主 | A1 | F6 | N-Comp | N-Rel | T2 | T5 | — | high |
| 1378 | 2017 | 微信小游戏 | 血战麻将 | A1 | F6 | N-Comp | N-Rel | T2 | T5 | — | high |
| 1379 | 2017 | 微信小游戏 | 街机捕鱼 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1380 | 2017 | 微信小游戏 | 见缝插圆 | A4 | F4 | N-Auto | N-Comp | T1 | T6 | — | high |
| 1381 | 2017 | 微信小游戏 | 贪吃蛇 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1382 | 2017 | 微信小游戏 | 贪婪洞窟 | A2 | F2 | N-Comp | — | T2 | T5 | — | high |
| 1383 | 2017 | 微信小游戏 | 跳棋 | A1 | F4 | N-Comp | N-Rel | T2 | T4 | — | high |
| 1384 | 2017 | 微信小游戏 | 黄金矿工2 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1385 | 2017 | 微信小游戏 | 黑白棋 | A1 | F4 | N-Comp | N-Rel | T2 | T4 | — | high |
| 1386 | 2016 | 微信小游戏 | Fate/Grand Order | A6 | F5 | N-Rel | N-Comp | T3 | T2 | virtual | high |
| 1387 | 2016 | 微信小游戏 | Pokemon GO | A5 | F4 | N-Auto | N-Rel、N-Comp | T1 | T4、T2 | — | medium |
| 1388 | 2016 | 微信小游戏 | 传奇世界H5 | A3 | F2 | N-Comp | N-Rel | T2 | T4 | — | high |
| 1389 | 2016 | 微信小游戏 | 倩女幽魂 | A7 | F6 | N-Rel | N-Comp | T4 | T3、T2 | mixed | high |
| 1390 | 2016 | 微信小游戏 | 决战沙城 | A3 | F2 | N-Comp | N-Rel | T2 | T4 | — | high |
| 1391 | 2016 | 微信小游戏 | 剑侠情缘 | A7 | F6 | N-Rel | N-Comp | T4 | T3、T2 | mixed | high |
| 1392 | 2016 | 微信小游戏 | 大天使之剑H5 | A3 | F2 | N-Comp | — | T2 | T1 | — | high |
| 1393 | 2016 | 微信小游戏 | 大话西游手游 | A7 | F6 | N-Rel | N-Comp | T4 | T3、T2 | mixed | high |
| 1394 | 2016 | 微信小游戏 | 崩坏3 | A2 | F1 | N-Comp | N-Rel | T2 | T3 | — | high |
| 1395 | 2016 | 微信小游戏 | 影之刃2 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1396 | 2016 | 微信小游戏 | 征途手机版 | A1 | F6 | N-Rel | N-Comp | T4 | T2 | real | high |
| 1397 | 2016 | 微信小游戏 | 愚公移山 | A3 | F2 | N-Auto | N-Comp | T1 | T2 | — | high |
| 1398 | 2016 | 微信小游戏 | 梦幻西游手游 | A7 | F6 | N-Rel | N-Comp | T4 | T2、T3 | mixed | high |
| 1399 | 2016 | 微信小游戏 | 炉石传说 | A1 | F4 | N-Comp | — | T2 | T5 | — | high |
| 1400 | 2016 | 微信小游戏 | 热血传奇手机版 | A1 | F6 | N-Rel | N-Comp | T4 | T2 | real | high |
| 1401 | 2016 | 微信小游戏 | 阴阳师 | A3 | F2 | N-Comp | N-Rel | T2 | T3 | — | high |
| 1402 | 2015 | 微信小游戏 | 一个都不能死 | A2 | F4 | N-Comp | — | T2 | T1 | — | high |
| 1403 | 2015 | 微信小游戏 | 七巧板 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 1404 | 2015 | 微信小游戏 | 体育 | A1 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1405 | 2015 | 微信小游戏 | 俗语 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 1406 | 2015 | 微信小游戏 | 停车场 | A4 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 1407 | 2015 | 微信小游戏 | 养成 | A3 | F5 | N-Rel | N-Auto | T3 | T1 | virtual | high |
| 1408 | 2015 | 微信小游戏 | 冒险 | A2 | F4 | N-Comp | — | T2 | T5 | — | high |
| 1409 | 2015 | 微信小游戏 | 动漫 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 1410 | 2015 | 微信小游戏 | 化学 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 1411 | 2015 | 微信小游戏 | 历史 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 1412 | 2015 | 微信小游戏 | 合体 | A4 | F2 | N-Comp | N-Auto | T6 | T1 | — | medium |
| 1413 | 2015 | 微信小游戏 | 名言 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 1414 | 2015 | 微信小游戏 | 哲学 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 1415 | 2015 | 微信小游戏 | 地理 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 1416 | 2015 | 微信小游戏 | 塔防 | A4 | F3 | N-Comp | — | T6 | T5 | — | high |
| 1417 | 2015 | 微信小游戏 | 填字 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 1418 | 2015 | 微信小游戏 | 宗教 | A5 | F4 | N-Comp | N-Auto | T5 | T1 | — | medium |
| 1419 | 2015 | 微信小游戏 | 战争 | A4 | F3 | N-Comp | — | T6 | T5 | — | high |
| 1420 | 2015 | 微信小游戏 | 打企鹅 | A2 | F1 | N-Auto | N-Comp | T1 | — | — | medium |
| 1421 | 2015 | 微信小游戏 | 拼图 | A5 | F4 | N-Auto | N-Comp | T1 | T5 | — | high |
| 1422 | 2015 | 微信小游戏 | 摩托车 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1423 | 2015 | 微信小游戏 | 政治 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1424 | 2015 | 微信小游戏 | 数学 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1425 | 2015 | 微信小游戏 | 明星 | A5 | F4 | N-Auto | N-Comp | T1 | T5 | — | high |
| 1426 | 2015 | 微信小游戏 | 模拟 | A4 | F2 | N-Auto | N-Comp | T6 | T1 | — | high |
| 1427 | 2015 | 微信小游戏 | 歇后语 | A5 | F4 | N-Auto | N-Comp | T1 | T5 | — | high |
| 1428 | 2015 | 微信小游戏 | 歌词 | A5 | F4 | N-Auto | N-Comp | T1 | T5 | — | high |
| 1429 | 2015 | 微信小游戏 | 法律 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1430 | 2015 | 微信小游戏 | 测测你的前世今生 | A3 | F6 | N-Rel | N-Auto | T4 | T1 | real | high |
| 1431 | 2015 | 微信小游戏 | 涂鸦跳跃 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1432 | 2015 | 微信小游戏 | 物理 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1433 | 2015 | 微信小游戏 | 猜谜 | A5 | F4 | N-Auto | N-Comp | T1 | T5 | — | high |
| 1434 | 2015 | 微信小游戏 | 生物 | A5 | F4 | N-Auto | N-Comp | T1 | T5 | — | high |
| 1435 | 2015 | 微信小游戏 | 电影 | A5 | F4 | N-Auto | N-Comp | T1 | T5 | — | high |
| 1436 | 2015 | 微信小游戏 | 电视剧 | A5 | F4 | N-Auto | N-Comp | T1 | T5 | — | high |
| 1437 | 2015 | 微信小游戏 | 疯狂打企鹅 | A2 | F1 | N-Auto | N-Comp | T1 | — | — | high |
| 1438 | 2015 | 微信小游戏 | 看你有多色 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1439 | 2015 | 微信小游戏 | 神经猫的朋友圈 | A6 | F5 | N-Rel | N-Auto | T4 | T1 | real | high |
| 1440 | 2015 | 微信小游戏 | 积木 | A4 | F4 | N-Comp | — | T2 | T6 | — | high |
| 1441 | 2015 | 微信小游戏 | 策略 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1442 | 2015 | 微信小游戏 | 经济 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1443 | 2015 | 微信小游戏 | 经营 | A3 | F2 | N-Comp | N-Auto | T6 | T2 | — | medium |
| 1444 | 2015 | 微信小游戏 | 舞蹈 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1445 | 2015 | 微信小游戏 | 艺术 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1446 | 2015 | 微信小游戏 | 英语 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1447 | 2015 | 微信小游戏 | 角色扮演 | A2 | F1 | N-Comp | N-Rel | T2 | T1、T3 | — | medium |
| 1448 | 2015 | 微信小游戏 | 解谜 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1449 | 2015 | 微信小游戏 | 诗词 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1450 | 2015 | 微信小游戏 | 语文 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1451 | 2015 | 微信小游戏 | 谚语 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1452 | 2015 | 微信小游戏 | 赛车 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1453 | 2015 | 微信小游戏 | 音乐 | A5 | F4 | N-Comp | — | T5 | T2 | — | high |
| 1454 | 2015 | 微信小游戏 | 飞行 | A2 | F1 | N-Comp | — | T2 | T1 | — | high |
| 1455 | 2015 | 微信小游戏 | 魔方 | A5 | F4 | N-Auto | N-Comp | T6 | T5 | — | medium |

## 十四、自动判定

**结论**:✅ v1.1 SDT 三需求框架验证通过