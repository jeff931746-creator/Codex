# 玩法承接 v1.1 矩阵验证报告(1455 真实爆款)

**日期**:2026-05-14
**样本数**:1455
**模型**:DeepSeek V4 Pro(`LLM_PROVIDER=deepseek`)

## 一、v1.1 验证指标

| 指标 | 数值 | 阈值 | 状态 |
|---|---|---|---|
| 主簇置信度 high 率 | 66.0% | >70% 通过 | ⚠️ |
| 主簇置信度 low 率 | 0.2% | <10% 通过 | ✅ |
| 无簇可归率 | 0.0% | <10% 通过 | ✅ |

## 二、9 个 CC 主簇归类分布

| CC | 样本数 | 占比 |
|---|---|---|
| CC1 | 215 | 14.8% |
| CC2 | 458 | 31.5% |
| CC3 | 102 | 7.0% |
| CC5 | 204 | 14.0% |
| CC6 | 241 | 16.6% |
| CC7 | 8 | 0.5% |
| CC8 | 65 | 4.5% |
| CC9 | 44 | 3.0% |
| CC10 | 116 | 8.0% |
| 无合适承接 | 0 | 0.0% |

## 三、置信度分布

| 置信度 | 样本数 | 占比 |
|---|---|---|
| high | 961 | 66.0% |
| medium | 491 | 33.7% |
| low | 3 | 0.2% |

## 四、R/G/LT 维度分布

### R 反馈结构

| R | 样本数 |
|---|---|
| R1 | 724 |
| R2 | 220 |
| R3 | 346 |
| R4 | 560 |
| R5 | 207 |

### G 成长结构

| G | 样本数 |
|---|---|
| G0 | 78 |
| G1 | 193 |
| G2 | 930 |
| G3 | 619 |
| G4 | 427 |
| G5 | 107 |

### LT 时间结构

| LT | 样本数 |
|---|---|
| LT1 | 964 |
| LT2 | 233 |
| LT3 | 639 |
| LT4 | 55 |

## 五、按平台 CC 分布(前 5)

| 平台 | 主要 CC 分布 |
|---|---|
| Steam | CC2(351)、CC5(150)、CC6(114)、CC1(100)、CC10(43) |
| 微信小游戏 | CC6(127)、CC1(115)、CC2(107)、CC3(87)、CC10(73) |

## 六、按年份 CC 分布(前 5)

| 年份 | 主要 CC 分布 |
|---|---|
| 2015 | CC6(34)、CC2(12)、CC10(3)、CC5(2)、CC8(1) |
| 2016 | CC2(23)、CC5(16)、CC6(15)、CC1(7)、CC9(6) |
| 2017 | CC2(43)、CC1(34)、CC6(21)、CC10(12)、CC5(9) |
| 2018 | CC2(44)、CC5(22)、CC6(19)、CC1(19)、CC10(10) |
| 2019 | CC2(22)、CC6(17)、CC1(15)、CC5(14)、CC10(9) |
| 2020 | CC2(31)、CC6(16)、CC5(14)、CC10(11)、CC3(11) |
| 2021 | CC2(42)、CC6(24)、CC3(18)、CC10(15)、CC1(14) |
| 2022 | CC1(14)、CC5(9)、CC6(8)、CC3(6)、CC2(5) |
| 2023 | CC2(41)、CC6(18)、CC1(15)、CC5(15)、CC10(7) |
| 2024 | CC2(51)、CC5(21)、CC6(20)、CC3(11)、CC1(9) |
| 2025 | CC2(73)、CC1(33)、CC5(28)、CC6(10)、CC3(8) |
| 2026 | CC2(71)、CC1(46)、CC5(40)、CC6(39)、CC10(33) |

## 七、Low 置信度样本(必须人工复核)

- **351. 《浩劫前夕》** [2023/Steam] | 主 CC2 | 排除 CC1 因为宣发承诺PVE生存挑战；排除 CC5 因为搜刮建造是生存手段而非系统经营。注：产品未兑现承诺，按宣发意图归类
- **360. 《红霞岛》** [2023/Steam] | 主 CC2 | 排除 CC1 因为主打合作PVE而非竞技对抗；排除 CC9 为主簇因为合作是手段，核心仍是射击克服敌人挑战。注：产品未达预期，按宣发意图归类
- **373. 《飙酷车神：极乐狂欢》** [2023/Steam] | 主 CC4 | 排除 CC1 因为核心是载具收集与展示，竞速对抗为副；排除 CC2 因为挑战感弱于收集驱动

## 八、所有样本归类全表

| ID | 年份 | 平台 | 样本 | 主CC | 副CC | R | G | LT | 置信度 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 2026 | Steam | 1000xRESIST Spirit | CC6 | CC8 | R4、R5 | G4 | LT1 | high |
| 2 | 2026 | Steam | Abiotic Factor (1. | CC5 | CC9 | R3 | G2、G3 | LT3 | medium |
| 3 | 2026 | Steam | Age of Mythology:  | CC1 | CC5 | R3、R1 | G2 | LT1、LT3 | medium |
| 4 | 2026 | Steam | Anger Foot (1.0) | CC2 | — | R1 | G2 | LT1 | high |
| 5 | 2026 | Steam | Animal Well DLC | CC6 | CC9 | R4 | G4 | LT1、LT3 | medium |
| 6 | 2026 | Steam | Ark 2 | CC5 | CC9、CC4 | R3、R2 | G3、G2 | LT3 | medium |
| 7 | 2026 | Steam | Avowed | CC2 | CC6 | R1 | G2、G3 | LT1、LT3 | medium |
| 8 | 2026 | Steam | Balatro DLC | CC6 | CC3 | R3、R2 | G4、G1 | LT1、LT2 | high |
| 9 | 2026 | Steam | Black Myth: Wukong | CC2 | CC6 | R1 | G2、G3 | LT1、LT3 | high |
| 10 | 2026 | Steam | Blasphemous 3 | CC2 | — | R1 | G2 | LT1 | high |
| 11 | 2026 | Steam | Blue Protocol (PC) | CC2 | CC4、CC9 | R1、R2 | G2、G3 | LT3 | medium |
| 12 | 2026 | Steam | Chrono Odyssey | CC2 | CC9、CC4 | R1 | G2、G3 | LT3 | medium |
| 13 | 2026 | Steam | Cities: Skylines 2 | CC5 | — | R3 | G2 | LT3 | high |
| 14 | 2026 | Steam | Civilization VII | CC5 | CC1 | R3 | G2、G4 | LT3 | high |
| 15 | 2026 | Steam | Clockwork Revoluti | CC6 | CC5 | R3、R4 | G4、G2 | LT1、LT3 | medium |
| 16 | 2026 | Steam | Crimson Desert | CC2 | CC4 | R1 | G2、G3 | LT1、LT3 | high |
| 17 | 2026 | Steam | Crow Country Seque | CC2 | CC6 | R4 | G2、G4 | LT1 | medium |
| 18 | 2026 | Steam | Dark and Darker (1 | CC1 | CC2、CC3 | R1 | G3、G2 | LT1、LT2 | medium |
| 19 | 2026 | Steam | Dead Island 2 DLC | CC10 | CC3、CC4 | R1、R2 | G3、G1 | LT1、LT2 | medium |
| 20 | 2026 | Steam | Deadlock (1.0) | CC1 | CC6 | R1 | G2 | LT1、LT3 | high |
| 21 | 2026 | Steam | Death Stranding 2 | CC5 | CC9、CC4 | R3、R4 | G3、G4 | LT3、LT4 | medium |
| 22 | 2026 | Steam | Den of Wolves | CC1 | CC9 | R1 | G2、G3 | LT1、LT2 | high |
| 23 | 2026 | Steam | Diablo IV Expansio | CC2 | CC3、CC4 | R1、R2 | G1、G3 | LT2、LT3 | medium |
| 24 | 2026 | Steam | Dragon's Dogma 2 D | CC2 | CC4 | R1 | G2、G3 | LT1、LT3 | high |
| 25 | 2026 | Steam | Dune: Awakening | CC9 | CC5、CC1 | R3、R1 | G3、G2 | LT3 | medium |
| 26 | 2026 | Steam | Dwarf Fortress DLC | CC5 | CC6 | R3 | G4、G2 | LT3、LT4 | medium |
| 27 | 2026 | Steam | Dying Light 2 DLC  | CC2 | CC10 | R1 | G2、G3 | LT1、LT3 | high |
| 28 | 2026 | Steam | Dyson Sphere Progr | CC5 | CC3 | R3、R2 | G3、G2 | LT3、LT4 | high |
| 29 | 2026 | Steam | EA Sports FC 26 | CC1 | CC4 | R1 | G2、G3 | LT1、LT3 | high |
| 30 | 2026 | Steam | Earthblade | CC2 | — | R1、R4 | G2、G4 | LT1 | high |
| 31 | 2026 | Steam | Ender Lilies 2 | CC2 | CC4 | R1 | G2、G3 | LT1、LT2 | high |
| 32 | 2026 | Steam | Enshrouded DLC | CC5 | CC2、CC4 | R3、R4 | G3、G2 | LT3、LT4 | medium |
| 33 | 2026 | Steam | Fable | CC8 | CC2 | R5、R1 | G5、G4 | LT3 | medium |
| 34 | 2026 | Steam | Factorio DLC | CC5 | CC6 | R3 | G2、G4 | LT3、LT4 | high |
| 35 | 2026 | Steam | Football Manager 2 | CC5 | CC1 | R3、R2 | G4、G2 | LT3 | medium |
| 36 | 2026 | Steam | Forza Horizon 6 | CC10 | CC1、CC4 | R1、R5 | G2、G3 | LT1、LT4 | medium |
| 37 | 2026 | Steam | Frostpunk 2 DLC | CC5 | CC6 | R3、R4 | G4、G2 | LT3 | high |
| 38 | 2026 | Steam | Ghost of Yotei | CC2 | — | R1 | G2、G3 | LT1、LT3 | high |
| 39 | 2026 | Steam | Ghostrunner 2 DLC | CC2 | — | R1 | G2 | LT1 | high |
| 40 | 2026 | Steam | Grand Theft Auto V | CC10 | CC1、CC5 | R3、R1、R5 | G2、G3 | LT4、LT1 | medium |
| 41 | 2026 | Steam | Grime 2 | CC2 | CC4 | R1 | G2、G3 | LT1、LT3 | high |
| 42 | 2026 | Steam | Hades II (1.0) | CC2 | CC4 | R1、R3 | G2、G3、G4 | LT1、LT3 | high |
| 43 | 2026 | Steam | Hell is Us | CC2 | — | R1、R4 | G2、G4 | LT1、LT3 | high |
| 44 | 2026 | Steam | Hollow Knight: Sil | CC2 | CC7 | R1、R4 | G2、G3、G4 | LT1、LT3 | high |
| 45 | 2026 | Steam | Hollowbody | CC2 | — | R4、R5 | G2、G4 | LT1 | medium |
| 46 | 2026 | Steam | Homeworld 3 DLC | CC5 | CC9 | R3、R4 | G2、G4 | LT1、LT3 | medium |
| 47 | 2026 | Steam | Judas | CC2 | CC6 | R1、R5 | G2、G4 | LT1、LT3 | medium |
| 48 | 2026 | Steam | Last Epoch Expansi | CC2 | CC4、CC7 | R1、R2 | G2、G3 | LT1、LT3 | high |
| 49 | 2026 | Steam | Lethal Company (1. | CC10 | CC9 | R1、R5 | G0、G2 | LT1、LT2 | high |
| 50 | 2026 | Steam | Little Nightmares  | CC2 | CC9 | R4、R5 | G2、G4 | LT1 | medium |
| 51 | 2026 | Steam | Manor Lords (1.0) | CC5 | CC9 | R3、R4 | G2、G3、G4 | LT3 | high |
| 52 | 2026 | Steam | Marathon | CC1 | CC3 | R1 | G2、G3 | LT1、LT3 | high |
| 53 | 2026 | Steam | Marvel's Spider-Ma | CC2 | CC10 | R1、R5 | G2、G3 | LT1、LT3 | high |
| 54 | 2026 | Steam | Mechabellum (1.0) | CC6 | CC1 | R3、R4 | G2、G4 | LT1、LT2 | high |
| 55 | 2026 | Steam | Metaphor: ReFantaz | CC2 | CC6、CC7 | R1、R3 | G2、G4 | LT1、LT3 | medium |
| 56 | 2026 | Steam | Mewgenics | CC5 | CC4、CC6 | R3 | G2、G3、G4 | LT3 | medium |
| 57 | 2026 | Steam | Monster Hunter Wil | CC2 | CC4、CC9 | R1 | G2、G3 | LT1、LT3 | high |
| 58 | 2026 | Steam | Mortal Kombat 2 | CC1 | CC10 | R1 | G2 | LT1 | high |
| 59 | 2026 | Steam | NBA 2K26 | CC1 | CC5 | R1、R4 | G2、G3 | LT1、LT3 | high |
| 60 | 2026 | Steam | Neon White 2 | CC1 | CC6 | R1、R4 | G2、G4 | LT1、LT2 | high |
| 61 | 2026 | Steam | Nightingale (1.0) | CC5 | CC4 | R3 | G3、G2 | LT3 | high |
| 62 | 2026 | Steam | Nine Sols 2 | CC2 | — | R1 | G2 | LT1 | high |
| 63 | 2026 | Steam | Once Human (1.0) | CC5 | CC4 | R3 | G3、G2 | LT3 | high |
| 64 | 2026 | Steam | Pacific Drive 2 | CC5 | CC4 | R3 | G3、G2 | LT2 | medium |
| 65 | 2026 | Steam | Path of Exile 2 (1 | CC2 | CC4、CC7 | R1、R3 | G2、G3 | LT3 | high |
| 66 | 2026 | Steam | Pax Dei (1.0) | CC9 | CC5 | R3 | G3、G5 | LT3 | high |
| 67 | 2026 | Steam | Perfect Dark | CC2 | — | R1、R4 | G2 | LT1 | high |
| 68 | 2026 | Steam | Phasmophobia (1.0) | CC6 | CC9 | R4 | G4 | LT1 | high |
| 69 | 2026 | Steam | Project Mugen | CC2 | CC7、CC4 | R1 | G2、G3 | LT3 | medium |
| 70 | 2026 | Steam | Project Zomboid (1 | CC5 | CC6 | R3 | G4、G2 | LT3 | high |
| 71 | 2026 | Steam | Reanimal | CC10 | CC9 | R5 | G5 | LT1 | medium |
| 72 | 2026 | Steam | RimWorld DLC | CC5 | CC7 | R3 | G2、G4 | LT3 | high |
| 73 | 2026 | Steam | Rise of the Ronin  | CC2 | CC8 | R1 | G2 | LT1 | high |
| 74 | 2026 | Steam | Routine | CC2 | — | R4 | G2 | LT1 | medium |
| 75 | 2026 | Steam | Satisfactory (1.0) | CC5 | CC7 | R3 | G2、G3 | LT3 | high |
| 76 | 2026 | Steam | Sea of Stars 2 | CC2 | — | R1、R4 | G2 | LT1 | high |
| 77 | 2026 | Steam | Selaco (1.0) | CC2 | — | R1 | G2 | LT1 | high |
| 78 | 2026 | Steam | Sifu DLC | CC2 | — | R1 | G2 | LT1 | high |
| 79 | 2026 | Steam | Silent Hill 2 Rema | CC6 | CC10 | R4、R5 | G4 | LT1 | high |
| 80 | 2026 | Steam | Slay the Spire 2 | CC6 | CC7 | R3 | G4、G2 | LT1、LT2 | high |
| 81 | 2026 | Steam | Slitterhead | CC2 | — | R1 | G2 | LT1 | high |
| 82 | 2026 | Steam | Spectre Divide | CC1 | — | R1 | G2 | LT1 | high |
| 83 | 2026 | Steam | State of Decay 3 | CC5 | CC4 | R3、R4 | G3、G2 | LT3 | high |
| 84 | 2026 | Steam | Stellar Blade (PC) | CC2 | — | R1 | G2 | LT1 | high |
| 85 | 2026 | Steam | Stormgate | CC1 | CC9 | R3、R1 | G2 | LT1、LT3 | medium |
| 86 | 2026 | Steam | Tekken 9 | CC1 | — | R1 | G2 | LT1 | high |
| 87 | 2026 | Steam | Tevi Sequel | CC2 | — | R1 | G2 | LT1 | high |
| 88 | 2026 | Steam | The Finals Season  | CC1 | — | R1、R3 | G2 | LT1 | high |
| 89 | 2026 | Steam | The Last of Us Par | CC2 | CC8 | R1、R5 | G4、G3 | LT1 | high |
| 90 | 2026 | Steam | The Outer Worlds 2 | CC2 | CC8 | R1、R5 | G4、G3 | LT1 | high |
| 91 | 2026 | Steam | The Wolf Among Us  | CC6 | CC8 | R5、R4 | G4 | LT1 | high |
| 92 | 2026 | Steam | Total War: Star Wa | CC5 | CC9 | R3、R1 | G2、G3 | LT3 | high |
| 93 | 2026 | Steam | Vampire: The Masqu | CC2 | CC8 | R1、R5 | G4、G2 | LT1 | high |
| 94 | 2026 | Steam | Warframe 1999 | CC2 | CC4 | R1、R2 | G3、G2 | LT3 | high |
| 95 | 2026 | Steam | Where the Water Ta | CC8 | CC4 | R5 | G4 | LT1 | high |
| 96 | 2026 | Steam | Wreckfest 2 | CC10 | — | R1 | G0 | LT1 | high |
| 97 | 2026 | Steam | Zero Space | CC1 | CC9 | R3、R1 | G2 | LT1、LT3 | medium |
| 98 | 2025 | Steam | S&box | CC5 | CC7 | R3、R4 | G2、G4 | LT4 | high |
| 99 | 2025 | Steam | Unrecord | CC2 | CC7 | R1、R4 | G2 | LT1 | high |
| 100 | 2025 | Steam | 七日世界 大型更新 | CC5 | CC4、CC9 | R3、R4 | G3、G2 | LT3 | high |
| 101 | 2025 | Steam | 三角洲行动 | CC1 | CC3 | R1 | G2、G3 | LT1、LT3 | high |
| 102 | 2025 | Steam | 上古卷轴4：湮灭重制版 | CC2 | CC4 | R1、R5 | G2、G3、G4 | LT3 | high |
| 103 | 2025 | Steam | 严阵以待 大型更新 | CC2 | CC9 | R1、R4 | G2 | LT1 | medium |
| 104 | 2025 | Steam | 光与影：33号远征队 | CC2 | CC6 | R4 | G2、G4 | LT1、LT3 | medium |
| 105 | 2025 | Steam | 光明破坏者 | CC2 | CC6 | R1、R3 | G2、G3 | LT1、LT2 | medium |
| 106 | 2025 | Steam | 冰汽时代2 大型更新 | CC5 | CC2 | R3、R4 | G2、G4 | LT3 | high |
| 107 | 2025 | Steam | 刺客信条：影 | CC2 | CC4 | R1、R4 | G2、G3 | LT3 | high |
| 108 | 2025 | Steam | 动物井 DLC | CC6 | CC4 | R4 | G4 | LT1 | high |
| 109 | 2025 | Steam | 午夜之南 | CC2 | — | R1、R4 | G2 | LT1 | high |
| 110 | 2025 | Steam | 博德之门3 MOD更新 | CC2 | CC6、CC4 | R4、R5 | G2、G4 | LT3 | medium |
| 111 | 2025 | Steam | 原神 Steam版 | CC2 | CC4、CC8 | R1、R5 | G2、G3、G5 | LT3 | medium |
| 112 | 2025 | Steam | 双点博物馆 | CC5 | CC4 | R3、R4 | G2、G3 | LT3 | high |
| 113 | 2025 | Steam | 发条革命 | CC2 | CC6 | R1、R4 | G2、G4 | LT3 | medium |
| 114 | 2025 | Steam | 合金装备Δ：食蛇者 | CC2 | CC6 | R1、R4 | G2、G4 | LT1 | high |
| 115 | 2025 | Steam | 吸血鬼幸存者 DLC | CC3 | CC6 | R2、R3 | G1、G2 | LT1、LT2 | high |
| 116 | 2025 | Steam | 命运2 新章节 | CC2 | CC3、CC4 | R1、R2 | G1、G3 | LT1、LT3 | medium |
| 117 | 2025 | Steam | 咩咩启示录 DLC | CC5 | CC2 | R1、R3 | G2、G3 | LT3 | medium |
| 118 | 2025 | Steam | 哈迪斯2 | CC2 | CC6、CC5 | R1、R3 | G2、G4 | LT1、LT2 | medium |
| 119 | 2025 | Steam | 夜莺1.0 | CC5 | CC2 | R3、R4 | G2、G3 | LT3 | high |
| 120 | 2025 | Steam | 天国：拯救2 | CC2 | CC5 | R1、R4 | G2、G3 | LT3 | high |
| 121 | 2025 | Steam | 天外世界2 | CC2 | CC4 | R1、R4 | G2、G3 | LT1、LT3 | high |
| 122 | 2025 | Steam | 失落之魂 | CC2 | — | R1 | G2 | LT1 | high |
| 123 | 2025 | Steam | 夺宝奇兵：古老之圈 | CC6 | CC4 | R4 | G4 | LT1 | high |
| 124 | 2025 | Steam | 如龙8外传：夏威夷海盗 | CC2 | CC4 | R1 | G2、G3 | LT1、LT3 | high |
| 125 | 2025 | Steam | 完美黑暗 | CC2 | — | R1、R4 | G2 | LT1 | high |
| 126 | 2025 | Steam | 宣誓 | CC2 | CC4 | R1、R4 | G2、G3 | LT1、LT3 | high |
| 127 | 2025 | Steam | 小人物大世界1.0 | CC5 | — | R3 | G2、G3 | LT3 | high |
| 128 | 2025 | Steam | 小小梦魇3 | CC6 | — | R4 | G4 | LT1 | high |
| 129 | 2025 | Steam | 小马岛2 | CC6 | — | R4 | G4 | LT1 | high |
| 130 | 2025 | Steam | 尘白禁区 大型更新 | CC2 | CC4、CC8 | R1 | G2、G3 | LT1、LT3 | medium |
| 131 | 2025 | Steam | 崩坏：星穹铁道 Steam版 | CC2 | CC4、CC8 | R2、R4 | G1、G2、G3 | LT1、LT3 | medium |
| 132 | 2025 | Steam | 帝国神话1.0 | CC5 | CC9 | R1、R3 | G2、G3 | LT3 | medium |
| 133 | 2025 | Steam | 幸福工厂1.0 | CC5 | — | R3 | G2、G3 | LT3 | high |
| 134 | 2025 | Steam | 幻兽帕鲁 DLC | CC5 | CC4、CC8 | R3 | G2、G3 | LT3 | high |
| 135 | 2025 | Steam | 庄园领主 大型更新 | CC5 | — | R3 | G2、G3 | LT3 | high |
| 136 | 2025 | Steam | 异星工厂：太空时代 | CC5 | — | R3 | G2、G3 | LT3 | high |
| 137 | 2025 | Steam | 异环 | CC2 | CC4、CC8 | R1、R4 | G2、G3 | LT1、LT3 | high |
| 138 | 2025 | Steam | 心灵杀手2 DLC | CC2 | — | R1、R4、R5 | G2、G4 | LT1 | high |
| 139 | 2025 | Steam | 忍者龙剑传：怒之羁绊 | CC2 | — | R1 | G2 | LT1 | high |
| 140 | 2025 | Steam | 忍：复仇之刃 | CC2 | — | R1 | G2 | LT1 | high |
| 141 | 2025 | Steam | 怪物猎人：荒野 | CC2 | CC4 | R1 | G2、G3 | LT1、LT3 | high |
| 142 | 2025 | Steam | 恐怖黎明2 | CC2 | CC4 | R1、R2 | G1、G3 | LT3 | high |
| 143 | 2025 | Steam | 战锤40K：星际战士2 | CC2 | — | R1 | G2、G3 | LT1、LT3 | high |
| 144 | 2025 | Steam | 戴森球计划 大型更新 | CC5 | — | R3 | G2、G4 | LT3 | high |
| 145 | 2025 | Steam | 文明7 | CC5 | — | R3、R4 | G2、G4 | LT3 | high |
| 146 | 2025 | Steam | 方舟2 | CC5 | CC4 | R3、R4 | G2、G3 | LT3 | high |
| 147 | 2025 | Steam | 无主之地4 | CC2 | CC4 | R1 | G1、G3 | LT1、LT3 | high |
| 148 | 2025 | Steam | 无限暖暖 | CC7 | CC4 | R4、R5 | G3、G5 | LT2、LT3 | medium |
| 149 | 2025 | Steam | 时空英豪2 | CC2 | — | R1、R4 | G2、G3 | LT1、LT3 | high |
| 150 | 2025 | Steam | 明日方舟：终末地 | CC5 | CC4 | R3、R4 | G2、G3 | LT3 | high |
| 151 | 2025 | Steam | 明末：渊虚之羽 | CC2 | — | R1 | G2、G3 | LT1、LT3 | high |
| 152 | 2025 | Steam | 星际战甲1999 | CC2 | CC4 | R1 | G1、G3 | LT3 | high |
| 153 | 2025 | Steam | 暗区突围：无限 | CC1 | CC4 | R1 | G3 | LT1、LT3 | high |
| 154 | 2025 | Steam | 暗黑地牢2 DLC | CC2 | — | R1、R4 | G2、G4 | LT1、LT2 | high |
| 155 | 2025 | Steam | 杀戮空间3 | CC2 | — | R1 | G2、G3 | LT1 | medium |
| 156 | 2025 | Steam | 杀手：血钱复出 | CC6 | — | R4 | G2、G4 | LT1 | high |
| 157 | 2025 | Steam | 森林之子1.0 | CC5 | — | R3、R4 | G2、G3 | LT3 | high |
| 158 | 2025 | Steam | 死亡搁浅2 | CC5 | CC8 | R4、R5 | G2、G5 | LT3 | medium |
| 159 | 2025 | Steam | 毁灭战士：黑暗时代 | CC2 | — | R1 | G2、G3 | LT1、LT3 | high |
| 160 | 2025 | Steam | 永劫无间2 | CC1 | — | R1 | G2、G3 | LT1、LT3 | high |
| 161 | 2025 | Steam | 泰坦之旅2 | CC2 | CC4 | R1 | G2、G3 | LT1、LT3 | high |
| 162 | 2025 | Steam | 流放之路2 | CC2 | CC4 | R1 | G2、G3 | LT1、LT3 | high |
| 163 | 2025 | Steam | 浪人崛起PC版 | CC2 | — | R1 | G2、G3 | LT1、LT3 | high |
| 164 | 2025 | Steam | 渎神2 DLC | CC2 | — | R1、R4 | G2 | LT1 | high |
| 165 | 2025 | Steam | 渔帆暗影2 | CC2 | CC4 | R4、R5 | G3、G4 | LT2、LT3 | medium |
| 166 | 2025 | Steam | 漫威争锋 | CC1 | — | R1 | G2 | LT1 | high |
| 167 | 2025 | Steam | 漫威蜘蛛侠2 PC版 | CC2 | — | R1、R5 | G2、G3 | LT1、LT3 | high |
| 168 | 2025 | Steam | 潜行者2 大型更新 | CC2 | CC4 | R1、R4 | G3、G4 | LT2、LT3 | medium |
| 169 | 2025 | Steam | 燃灯者 | CC2 | — | R1 | G2、G3 | LT1、LT3 | high |
| 170 | 2025 | Steam | 燕云十六声 | CC2 | CC4 | R1 | G2、G3 | LT1、LT3 | high |
| 171 | 2025 | Steam | 猎杀：对决 大型更新 | CC1 | CC4 | R1、R4 | G2、G3 | LT1、LT2 | high |
| 172 | 2025 | Steam | 白夜极光 PC版 | CC6 | CC4 | R4 | G2、G4 | LT1、LT2 | medium |
| 173 | 2025 | Steam | 百英雄传 DLC | CC2 | CC4 | R4 | G2、G3 | LT1、LT3 | high |
| 174 | 2025 | Steam | 神之亵渎2 DLC | CC2 | — | R1、R4 | G2 | LT1 | high |
| 175 | 2025 | Steam | 神之浩劫2 | CC1 | — | R1 | G2 | LT1 | high |
| 176 | 2025 | Steam | 神话时代：重述版 | CC1 | — | R1、R3 | G2、G4 | LT1 | medium |
| 177 | 2025 | Steam | 神鬼寓言 | CC2 | CC4 | R1、R5 | G2、G3、G5 | LT1、LT3 | medium |
| 178 | 2025 | Steam | 空洞骑士：丝之歌 | CC2 | — | R1、R4 | G2 | LT1 | high |
| 179 | 2025 | Steam | 第一后裔 大型更新 | CC2 | CC4 | R1 | G2、G3 | LT1、LT3 | high |
| 180 | 2025 | Steam | 绝区零 Steam版 | CC2 | CC4 | R1 | G2、G3 | LT1、LT2 | high |
| 181 | 2025 | Steam | 绝地潜兵2 大型DLC | CC1 | CC9 | R1 | G2、G3 | LT1、LT3 | high |
| 182 | 2025 | Steam | 罪恶装备：奋战 DLC | CC1 | — | R1 | G2 | LT1 | high |
| 183 | 2025 | Steam | 羊蹄山之魂 | CC2 | CC4 | R1 | G2、G3 | LT1、LT3 | high |
| 184 | 2025 | Steam | 腐朽之都3 | CC5 | CC9 | R3、R4 | G2、G3 | LT3 | medium |
| 185 | 2025 | Steam | 蓝色星原：旅谣 | CC8 | CC4 | R5 | G5、G3 | LT3、LT4 | high |
| 186 | 2025 | Steam | 街头霸王6 DLC | CC1 | — | R1 | G2 | LT1 | high |
| 187 | 2025 | Steam | 解限机 | CC1 | CC4 | R1 | G2、G3 | LT1、LT3 | high |
| 188 | 2025 | Steam | 边缘世界 DLC | CC5 | — | R3 | G2、G3 | LT3 | high |
| 189 | 2025 | Steam | 远星物语 | CC6 | — | R4 | G2、G4 | LT1 | high |
| 190 | 2025 | Steam | 逆水寒手游PC版 | CC3 | CC4、CC7 | R2、R5 | G1、G3 | LT3 | medium |
| 191 | 2025 | Steam | 铁拳8 DLC | CC1 | — | R1 | G2 | LT1 | high |
| 192 | 2025 | Steam | 铁锈风云 | CC5 | CC1 | R1、R3 | G2、G3 | LT1、LT3 | medium |
| 193 | 2025 | Steam | 零之领域 | CC1 | CC9 | R1 | G2、G3 | LT1、LT3 | medium |
| 194 | 2025 | Steam | 雾锁王国1.0 | CC2 | CC5 | R1、R4 | G2、G3 | LT3 | medium |
| 195 | 2025 | Steam | 非生物因素1.0 | CC5 | — | R3、R4 | G2、G3 | LT3 | high |
| 196 | 2025 | Steam | 风暴之城 DLC | CC5 | CC6 | R3、R4 | G2、G4 | LT1、LT2 | medium |
| 197 | 2025 | Steam | 风暴之门 | CC1 | CC5 | R1、R3 | G2 | LT1 | medium |
| 198 | 2025 | Steam | 风起云涌 | CC2 | CC9 | R1 | G2、G3 | LT1 | medium |
| 199 | 2025 | Steam | 鸣潮 Steam版 | CC2 | CC4、CC3 | R1、R2 | G1、G2、G3 | LT1、LT3 | medium |
| 200 | 2025 | Steam | 黑神话：悟空 DLC | CC2 | CC4 | R1 | G2、G3 | LT1、LT3 | high |
| 201 | 2025 | Steam | 龙之信条2 DLC | CC2 | CC4 | R1、R4 | G2、G3 | LT1、LT3 | high |
| 202 | 2024 | Steam | F1 24 | CC2 | — | R1、R4 | G2 | LT1、LT3 | high |
| 203 | 2024 | Steam | NBA 2K25 | CC1 | — | R1、R4 | G2、G3 | LT1、LT3 | high |
| 204 | 2024 | Steam | No More Room in He | CC2 | CC9 | R1、R4 | G2、G3 | LT1 | medium |
| 205 | 2024 | Steam | WRC 24 | CC2 | — | R1、R4 | G2 | LT1、LT3 | high |
| 206 | 2024 | Steam | 一千个抵抗 | CC6 | — | R4 | G4 | LT1 | high |
| 207 | 2024 | Steam | 七日世界 | CC5 | CC4、CC9 | R3、R4 | G2、G3 | LT3、LT4 | medium |
| 208 | 2024 | Steam | 乌鸦国 | CC5 | — | R3、R4 | G2、G3 | LT1、LT3 | high |
| 209 | 2024 | Steam | 众生之门 | CC2 | CC4 | R1、R4 | G2、G3 | LT1、LT3 | high |
| 210 | 2024 | Steam | 像素神话 | CC6 | — | R1、R3 | G2、G4 | LT1 | high |
| 211 | 2024 | Steam | 内容警告 | CC10 | CC9 | R1、R5 | G0 | LT1 | medium |
| 212 | 2024 | Steam | 冰汽时代2 | CC5 | — | R3、R4 | G2、G4 | LT3 | high |
| 213 | 2024 | Steam | 动物井 | CC6 | CC9 | R4 | G4 | LT1、LT3 | high |
| 214 | 2024 | Steam | 勇气之剑 | CC2 | — | R1 | G2 | LT1 | high |
| 215 | 2024 | Steam | 勇者斗恶龙怪物篇3 | CC3 | CC4 | R1、R2 | G1、G3 | LT1、LT3 | high |
| 216 | 2024 | Steam | 命运2：终焉之形 | CC2 | CC4、CC9 | R1、R4 | G2、G3 | LT1、LT3 | high |
| 217 | 2024 | Steam | 咒语浪人 | CC6 | — | R1、R3 | G2、G4 | LT1 | high |
| 218 | 2024 | Steam | 圣兽之王 | CC6 | — | R1、R3 | G2、G4 | LT1、LT3 | high |
| 219 | 2024 | Steam | 圣歌德嘉的晚钟 | CC6 | — | R4、R5 | G4 | LT1 | high |
| 220 | 2024 | Steam | 地心护核者1.0 | CC5 | CC4 | R3、R4 | G2、G3 | LT3、LT4 | high |
| 221 | 2024 | Steam | 地狱之刃2：塞娜的史诗 | CC2 | CC8 | R1、R5 | G2、G4 | LT1 | high |
| 222 | 2024 | Steam | 太平洋驾驶 | CC2 | CC4 | R2、R4 | G3、G2 | LT2、LT3 | medium |
| 223 | 2024 | Steam | 太阳避难所 | CC5 | CC4 | R3、R4 | G3、G2 | LT3 | medium |
| 224 | 2024 | Steam | 女神异闻录3 Reload | CC8 | CC2 | R1、R5 | G5、G2 | LT3 | high |
| 225 | 2024 | Steam | 如龙8 | CC2 | CC8 | R1、R5 | G2、G3 | LT3 | medium |
| 226 | 2024 | Steam | 寂静岭2 | CC6 | CC10 | R4、R5 | G4、G3 | LT1 | high |
| 227 | 2024 | Steam | 小丑牌 | CC6 | CC3 | R3、R4 | G4、G1 | LT1、LT2 | high |
| 228 | 2024 | Steam | 尘封大陆 | CC2 | CC4 | R1 | G2、G3 | LT1、LT3 | high |
| 229 | 2024 | Steam | 师父 DLC | CC2 | — | R1 | G2 | LT1 | high |
| 230 | 2024 | Steam | 帝国时代2：罗马归来 | CC1 | CC5 | R1、R3 | G2、G3 | LT1 | medium |
| 231 | 2024 | Steam | 帝国神话 | CC5 | CC9、CC4 | R1、R3 | G3、G2 | LT3 | medium |
| 232 | 2024 | Steam | 幻兽帕鲁 | CC5 | CC4、CC10 | R3、R2 | G3、G2 | LT3 | high |
| 233 | 2024 | Steam | 幻日夜羽 | CC8 | CC2 | R1、R5 | G5、G2 | LT3 | high |
| 234 | 2024 | Steam | 庄园领主 | CC5 | CC2 | R3、R4 | G2、G3 | LT3 | high |
| 235 | 2024 | Steam | 异星工厂2.0 | CC5 | — | R3 | G2、G3 | LT3 | high |
| 236 | 2024 | Steam | 恐鬼症1.0 | CC6 | CC10 | R4、R5 | G4、G2 | LT1 | high |
| 237 | 2024 | Steam | 恶意不息 | CC2 | CC4 | R1 | G2、G3 | LT1、LT3 | high |
| 238 | 2024 | Steam | 恶魔轮盘 | CC6 | CC10 | R4 | G4 | LT1 | high |
| 239 | 2024 | Steam | 拉力赛艺术 | CC2 | — | R1 | G2 | LT1 | high |
| 240 | 2024 | Steam | 星球大战：法外狂徒 | CC2 | CC8、CC4 | R1、R5 | G2、G5 | LT3 | medium |
| 241 | 2024 | Steam | 星际角斗场 | CC2 | CC4 | R1 | G2、G3 | LT1、LT2 | high |
| 242 | 2024 | Steam | 星露谷物语1.6 | CC5 | CC4、CC8 | R3、R4 | G3、G5 | LT3 | high |
| 243 | 2024 | Steam | 暗喻幻想 | CC2 | CC6 | R1、R4 | G2、G4 | LT3 | medium |
| 244 | 2024 | Steam | 暗黑破坏神4：憎恶之躯 | CC2 | CC3、CC4 | R1、R2 | G1、G3 | LT3 | medium |
| 245 | 2024 | Steam | 最终幻想14：黄金的遗产 | CC2 | CC9、CC4 | R1 | G2、G3、G5 | LT3 | medium |
| 246 | 2024 | Steam | 机车狂欢 | CC1 | — | R1 | G2、G3 | LT1 | high |
| 247 | 2024 | Steam | 死亡教堂 | CC2 | CC6 | R1 | G2、G4 | LT1、LT2 | medium |
| 248 | 2024 | Steam | 浪漫沙加2：七英雄的复仇 | CC2 | CC4 | R1、R4 | G2、G4 | LT3 | high |
| 249 | 2024 | Steam | 深岩银河：幸存者 | CC2 | CC6 | R1、R3 | G2、G3 | LT1、LT2 | medium |
| 250 | 2024 | Steam | 深空梦里人2 | CC6 | CC8 | R4、R5 | G4 | LT3 | high |
| 251 | 2024 | Steam | 潜水员戴夫 DLC | CC5 | CC4 | R3、R4 | G3 | LT2、LT3 | high |
| 252 | 2024 | Steam | 火山冒险 | CC2 | CC6 | R1、R4 | G2、G4 | LT1、LT3 | medium |
| 253 | 2024 | Steam | 火山女儿 | CC3 | CC8、CC4 | R2、R4 | G1、G5 | LT3 | medium |
| 254 | 2024 | Steam | 灵魂面甲 | CC5 | CC2、CC4 | R3、R4 | G2、G3 | LT3 | medium |
| 255 | 2024 | Steam | 燧石枪：黎明之围 | CC2 | — | R1 | G2、G3 | LT1、LT3 | high |
| 256 | 2024 | Steam | 狂野星球之旅 | CC5 | CC4、CC9 | R3、R4 | G3、G4 | LT1、LT3 | medium |
| 257 | 2024 | Steam | 猎杀：对决1896 | CC1 | CC2 | R1 | G2、G3 | LT1、LT2 | high |
| 258 | 2024 | Steam | 百英雄传 | CC2 | CC4 | R1、R4 | G2、G3 | LT3 | high |
| 259 | 2024 | Steam | 真女神转生5：复仇 | CC2 | CC6、CC4 | R1、R4 | G2、G4 | LT3 | medium |
| 260 | 2024 | Steam | 真知之岛 | CC6 | — | R4 | G4 | LT1 | high |
| 261 | 2024 | Steam | 碧海黑帆 | CC2 | CC4 | R1、R3 | G2、G3 | LT1、LT3 | medium |
| 262 | 2024 | Steam | 碧蓝幻想：Relink | CC2 | CC4 | R1 | G2、G3 | LT1、LT3 | high |
| 263 | 2024 | Steam | 祇：女神之道 | CC2 | — | R1、R3 | G2、G4 | LT1 | medium |
| 264 | 2024 | Steam | 第一后裔 | CC2 | CC4 | R1 | G2、G3 | LT1、LT3 | medium |
| 265 | 2024 | Steam | 纸境奇缘 | CC6 | — | R4 | G2、G4 | LT1 | medium |
| 266 | 2024 | Steam | 绝命游卡 | CC1 | CC4 | R1 | G2、G3 | LT1 | medium |
| 267 | 2024 | Steam | 绝地潜兵2 | CC9 | — | R1 | G2、G3 | LT1、LT3 | medium |
| 268 | 2024 | Steam | 绝境反击 | CC2 | — | R1、R3 | G2 | LT1 | high |
| 269 | 2024 | Steam | 绝境重启 | CC2 | — | R1 | G2 | LT1 | high |
| 270 | 2024 | Steam | 绝影战士 | CC2 | — | R1 | G2 | LT1 | high |
| 271 | 2024 | Steam | 羊肚菌 | CC6 | — | R4 | G4 | LT1 | high |
| 272 | 2024 | Steam | 肉鸽之魂 | CC2 | — | R1、R3 | G2 | LT1 | high |
| 273 | 2024 | Steam | 致命公司 | CC10 | CC4 | R5 | G0 | LT1 | medium |
| 274 | 2024 | Steam | 艾尔登法环：黄金树幽影 | CC2 | CC4 | R1 | G2、G3 | LT1、LT3 | high |
| 275 | 2024 | Steam | 艾诺提亚：失落之歌 | CC2 | — | R1 | G2、G3 | LT1 | high |
| 276 | 2024 | Steam | 节奏医生 | CC6 | — | R4 | G2、G4 | LT1 | medium |
| 277 | 2024 | Steam | 蟹蟹寻宝奇遇 | CC2 | CC4 | R1 | G2、G3 | LT1 | high |
| 278 | 2024 | Steam | 诺科 | CC6 | — | R4、R5 | G4 | LT1 | medium |
| 279 | 2024 | Steam | 辐射4次世代更新 | CC2 | CC4 | R1、R4 | G2、G3 | LT1、LT3 | medium |
| 280 | 2024 | Steam | 边缘世界：异常 | CC5 | — | R3 | G2、G4 | LT3、LT4 | medium |
| 281 | 2024 | Steam | 逆转裁判456 | CC6 | — | R4 | G4 | LT1 | high |
| 282 | 2024 | Steam | 铁拳8 | CC1 | — | R1 | G2 | LT1 | high |
| 283 | 2024 | Steam | 铃兰之剑 | CC2 | CC4 | R4 | G2、G3 | LT1、LT3 | medium |
| 284 | 2024 | Steam | 银河破裂者 | CC5 | — | R1、R3 | G2、G3 | LT2、LT3 | medium |
| 285 | 2024 | Steam | 风暴之城 | CC5 | — | R3、R4 | G2、G4 | LT1、LT2 | high |
| 286 | 2024 | Steam | 驱灵者：新伊甸的幽灵 | CC2 | CC8 | R1、R5 | G2、G5 | LT1、LT3 | medium |
| 287 | 2024 | Steam | 魔法餐作室 | CC5 | CC4 | R3、R4 | G2、G3 | LT2 | high |
| 288 | 2024 | Steam | 鸣潮 | CC2 | CC4、CC8 | R1 | G2、G3 | LT1、LT3 | medium |
| 289 | 2024 | Steam | 黑神话：悟空 | CC2 | — | R1 | G2、G3 | LT1、LT3 | high |
| 290 | 2024 | Steam | 龙之信条2 | CC2 | CC8 | R1、R3 | G2、G3 | LT1、LT3 | medium |
| 291 | 2024 | Steam | 龙珠Z：卡卡罗特 DLC6 | CC2 | CC8 | R1、R5 | G2、G5 | LT1 | medium |
| 292 | 2024 | Steam | 龙腾世纪4：影障守护者 | CC2 | CC8、CC9 | R1、R5 | G2、G5 | LT1、LT3 | medium |
| 293 | 2023 | Steam | EA Sports FC 24 | CC1 | CC4 | R1 | G2、G3 | LT1、LT3 | high |
| 294 | 2023 | Steam | F1 23 | CC1 | — | R1 | G2 | LT1、LT3 | high |
| 295 | 2023 | Steam | NBA 2K24 | CC1 | CC4 | R1 | G2、G3 | LT1、LT3 | high |
| 296 | 2023 | Steam | WWE 2K23 | CC1 | CC8 | R1、R5 | G2 | LT1 | medium |
| 297 | 2023 | Steam | 三位一体5 | CC6 | — | R4 | G2、G4 | LT1 | high |
| 298 | 2023 | Steam | 严酷考验 | CC2 | CC10 | R1、R5 | G2 | LT1 | medium |
| 299 | 2023 | Steam | 严阵以待 | CC9 | — | R1 | G2 | LT1 | high |
| 300 | 2023 | Steam | 人类 | CC6 | — | R4 | G4 | LT1 | high |
| 301 | 2023 | Steam | 使命召唤：现代战争3 | CC1 | — | R1 | G2 | LT1、LT3 | high |
| 302 | 2023 | Steam | 全面战争：法老 | CC5 | CC1 | R3 | G2、G3 | LT3 | medium |
| 303 | 2023 | Steam | 刺客信条：幻景 | CC2 | — | R1、R4 | G2、G3 | LT1、LT2 | high |
| 304 | 2023 | Steam | 匹诺曹的谎言 | CC2 | CC4 | R1 | G2、G3 | LT1、LT2 | high |
| 305 | 2023 | Steam | 博尔特枪 | CC2 | — | R1 | G2、G3 | LT1 | high |
| 306 | 2023 | Steam | 博德之门3 | CC6 | CC8、CC4 | R3、R5 | G2、G4 | LT3 | medium |
| 307 | 2023 | Steam | 卧龙：苍天陨落 | CC2 | — | R1 | G2、G3 | LT1、LT2 | high |
| 308 | 2023 | Steam | 原始袭变 | CC9 | CC2 | R1 | G2、G3 | LT1、LT2 | medium |
| 309 | 2023 | Steam | 原子之心 | CC2 | — | R1、R4 | G2、G3 | LT1、LT2 | high |
| 310 | 2023 | Steam | 反恐精英2 | CC1 | CC9 | R1 | G2 | LT1、LT3 | high |
| 311 | 2023 | Steam | 取景器 | CC6 | — | R4 | G4 | LT1 | high |
| 312 | 2023 | Steam | 命运2：光陨之秋 | CC2 | CC1、CC4 | R1、R2 | G2、G3 | LT1、LT3 | medium |
| 313 | 2023 | Steam | 地平线：西之绝境 | CC2 | CC4 | R1、R4 | G2、G3 | LT2、LT3 | high |
| 314 | 2023 | Steam | 坎巴拉太空计划2 | CC5 | CC6 | R3 | G2、G4 | LT3 | medium |
| 315 | 2023 | Steam | 埃尔帕索，别处 | CC2 | — | R1 | G2 | LT1 | high |
| 316 | 2023 | Steam | 城市天际线2 | CC5 | — | R3 | G2、G4 | LT3 | high |
| 317 | 2023 | Steam | 堕落之主 | CC2 | — | R1 | G2、G3 | LT1、LT2 | high |
| 318 | 2023 | Steam | 塔洛斯的法则2 | CC6 | — | R4、R5 | G4 | LT1、LT2 | high |
| 319 | 2023 | Steam | 大地之爱 | CC5 | CC10 | R3、R4 | G2、G3 | LT3 | medium |
| 320 | 2023 | Steam | 失忆症：地堡 | CC2 | CC6 | R1、R4 | G2、G4 | LT1 | medium |
| 321 | 2023 | Steam | 奇娅 | CC10 | CC4 | R4、R5 | G4 | LT1 | medium |
| 322 | 2023 | Steam | 女神异闻录3 携带版 | CC2 | CC8 | R2、R4 | G1、G5 | LT3 | medium |
| 323 | 2023 | Steam | 女神异闻录5 战略版 | CC6 | — | R4 | G2、G4 | LT1、LT2 | medium |
| 324 | 2023 | Steam | 如龙7外传 | CC2 | CC10 | R1、R5 | G2 | LT1 | medium |
| 325 | 2023 | Steam | 如龙：维新！极 | CC2 | — | R1 | G2 | LT1 | high |
| 326 | 2023 | Steam | 守望先锋2 | CC1 | CC9 | R1 | G2 | LT1、LT3 | high |
| 327 | 2023 | Steam | 完美音浪 | CC2 | — | R1 | G2 | LT1 | high |
| 328 | 2023 | Steam | 寻路者 | CC2 | CC4 | R1、R2 | G1、G3 | LT2、LT3 | medium |
| 329 | 2023 | Steam | 帝国时代4：苏丹崛起 | CC5 | CC1 | R3 | G2、G4 | LT1、LT3 | medium |
| 330 | 2023 | Steam | 幽灵行者2 | CC2 | — | R1 | G2 | LT1 | high |
| 331 | 2023 | Steam | 心灵杀手2 | CC6 | CC10 | R4、R5 | G4 | LT1 | medium |
| 332 | 2023 | Steam | 战律2 | CC6 | CC1 | R4 | G2、G4 | LT1、LT2 | medium |
| 333 | 2023 | Steam | 战锤40K：行商浪人 | CC6 | CC2 | R4 | G2、G4 | LT3 | medium |
| 334 | 2023 | Steam | 收获日3 | CC9 | CC2 | R1、R4 | G2、G3 | LT1、LT2 | medium |
| 335 | 2023 | Steam | 方舟：生存飞升 | CC5 | CC3、CC9 | R3 | G1、G3 | LT3、LT4 | medium |
| 336 | 2023 | Steam | 无敌号 | CC10 | — | R5 | G4 | LT1 | high |
| 337 | 2023 | Steam | 星之海 | CC2 | — | R1、R4 | G2 | LT1、LT3 | medium |
| 338 | 2023 | Steam | 星之海洋2：第二个故事R | CC2 | CC4 | R1、R2 | G1、G2、G3 | LT3 | medium |
| 339 | 2023 | Steam | 星空 | CC5 | CC2、CC4 | R3、R5 | G2、G3、G4 | LT3、LT4 | medium |
| 340 | 2023 | Steam | 星际迷航：复苏 | CC10 | — | R5 | G4 | LT1 | high |
| 341 | 2023 | Steam | 暗黑地牢2 | CC2 | CC4 | R1、R4 | G2、G3 | LT1、LT3 | high |
| 342 | 2023 | Steam | 暗黑破坏神4 | CC2 | CC3、CC4 | R1、R2 | G1、G3 | LT3 | high |
| 343 | 2023 | Steam | 月石岛 | CC8 | CC4、CC6 | R1、R4 | G2、G5 | LT2、LT3 | medium |
| 344 | 2023 | Steam | 机械战警：暴戾都市 | CC2 | — | R1、R4 | G2 | LT1 | high |
| 345 | 2023 | Steam | 极限竞速 | CC2 | CC4 | R1、R2 | G2、G3 | LT1、LT3 | medium |
| 346 | 2023 | Steam | 森林之子 | CC5 | CC2 | R1、R3 | G2、G3 | LT3 | high |
| 347 | 2023 | Steam | 歧路旅人2 | CC2 | CC4 | R1、R4 | G1、G2 | LT1、LT3 | high |
| 348 | 2023 | Steam | 死亡回归 | CC2 | — | R1 | G2 | LT1、LT2 | high |
| 349 | 2023 | Steam | 沙石镇时光 | CC5 | CC4、CC8 | R3、R4 | G2、G3 | LT3 | high |
| 350 | 2023 | Steam | 洛克人EXE合集 | CC6 | CC2 | R1、R4 | G2、G4 | LT1 | high |
| 351 | 2023 | Steam | 浩劫前夕 | CC2 | — | R1 | G3 | LT3 | low |
| 352 | 2023 | Steam | 渔帆暗礁 | CC2 | CC4、CC10 | R1、R4 | G2、G3 | LT1、LT3 | medium |
| 353 | 2023 | Steam | 潜水员戴夫 | CC5 | CC2、CC4 | R1、R3、R4 | G2、G3 | LT2、LT3 | high |
| 354 | 2023 | Steam | 狂野之心 | CC2 | CC5 | R1 | G2、G3 | LT1、LT3 | high |
| 355 | 2023 | Steam | 珊瑚岛 | CC5 | CC4、CC8 | R3、R4 | G2、G3 | LT3 | high |
| 356 | 2023 | Steam | 瑞奇与叮当：时空跳转 | CC2 | CC4 | R1、R4 | G2、G3 | LT1 | high |
| 357 | 2023 | Steam | 生化危机4重制版 | CC2 | — | R1、R4 | G2、G3 | LT1、LT2 | high |
| 358 | 2023 | Steam | 神之亵渎2 | CC2 | — | R1、R4 | G2 | LT1、LT2 | high |
| 359 | 2023 | Steam | 系统休克 | CC6 | CC2 | R1、R4 | G2、G4 | LT1 | high |
| 360 | 2023 | Steam | 红霞岛 | CC2 | CC9 | R1 | G2、G3 | LT1、LT3 | low |
| 361 | 2023 | Steam | 英雄传说：黎之轨迹2 | CC8 | CC2 | R5、R1 | G5、G2 | LT3 | medium |
| 362 | 2023 | Steam | 英雄连3 | CC1 | CC5 | R3、R1 | G2、G3 | LT1、LT3 | medium |
| 363 | 2023 | Steam | 茧 | CC6 | — | R4 | G4 | LT1 | high |
| 364 | 2023 | Steam | 莱莎的炼金工房3 | CC5 | CC4、CC8 | R3、R2 | G3、G2 | LT3 | medium |
| 365 | 2023 | Steam | 街头霸王6 | CC1 | — | R1 | G2 | LT1、LT3 | high |
| 366 | 2023 | Steam | 装甲核心6 | CC2 | CC6 | R1、R3 | G2、G3 | LT1、LT3 | medium |
| 367 | 2023 | Steam | 赛博朋克2077：往日之影 | CC8 | CC2 | R5、R1 | G5、G2 | LT3 | medium |
| 368 | 2023 | Steam | 足球经理2024 | CC5 | CC1 | R3、R2 | G2、G3 | LT3 | medium |
| 369 | 2023 | Steam | 遗迹2 | CC2 | CC6 | R1、R3 | G2、G3 | LT1、LT3 | medium |
| 370 | 2023 | Steam | 铁血联盟3 | CC5 | CC2 | R3、R1 | G2、G3 | LT3 | medium |
| 371 | 2023 | Steam | 阿凡达：潘多拉边境 | CC2 | CC4 | R1、R5 | G2、G3 | LT3 | medium |
| 372 | 2023 | Steam | 霍格沃茨之遗 | CC8 | CC2、CC4 | R5、R1 | G5、G2 | LT3 | high |
| 373 | 2023 | Steam | 飙酷车神：极乐狂欢 | CC4 | CC1 | R1、R2 | G3、G2 | LT3 | low |
| 374 | 2023 | Steam | 魔咒之地 | CC2 | CC4 | R1、R5 | G2、G3 | LT3 | medium |
| 375 | 2023 | Steam | 魔女之泉R | CC3 | CC8、CC4 | R2、R1 | G1、G5 | LT3 | medium |
| 376 | 2021 | Steam | 12 Minutes | CC6 | — | R4、R5 | G4 | LT1 | high |
| 377 | 2021 | Steam | Age of Empires IV | CC1 | CC5 | R3、R1 | G2、G3 | LT1、LT3 | medium |
| 378 | 2021 | Steam | Alex Kidd in Mirac | CC2 | — | R1、R4 | G2 | LT1 | high |
| 379 | 2021 | Steam | Art of Rally | CC2 | CC4 | R1 | G2、G3 | LT1、LT3 | medium |
| 380 | 2021 | Steam | Axiom Verge 2 | CC6 | CC2 | R4、R1 | G4、G2 | LT1、LT3 | medium |
| 381 | 2021 | Steam | Back 4 Blood | CC2 | CC6 | R1 | G2、G3 | LT1、LT3 | high |
| 382 | 2021 | Steam | Battlefield 2042 | CC1 | — | R1 | G2、G3 | LT1、LT3 | high |
| 383 | 2021 | Steam | Before Your Eyes | CC8 | — | R5 | G4 | LT1 | high |
| 384 | 2021 | Steam | Black Book | CC6 | CC2 | R4 | G2、G4 | LT1、LT2 | high |
| 385 | 2021 | Steam | Bonfire Peaks | CC6 | — | R4 | G4 | LT1 | high |
| 386 | 2021 | Steam | Boomerang X | CC2 | — | R1 | G2 | LT1 | high |
| 387 | 2021 | Steam | Bright Memory: Inf | CC2 | — | R1 | G2、G3 | LT1 | high |
| 388 | 2021 | Steam | Chernobylite | CC5 | CC2 | R3、R5 | G2、G3 | LT3 | medium |
| 389 | 2021 | Steam | Chicory: A Colorfu | CC10 | CC6 | R4、R5 | G4 | LT1 | medium |
| 390 | 2021 | Steam | Cris Tales | CC6 | CC2 | R4 | G2、G4 | LT1、LT2 | high |
| 391 | 2021 | Steam | Curse of the Dead  | CC2 | CC6 | R1 | G2、G3 | LT1、LT2 | high |
| 392 | 2021 | Steam | Death Stranding: D | CC5 | CC8 | R3、R5 | G2、G3 | LT3 | high |
| 393 | 2021 | Steam | Death Trash | CC2 | CC6 | R1、R5 | G2、G4 | LT1、LT2 | medium |
| 394 | 2021 | Steam | Death's Door | CC2 | — | R1 | G2、G3 | LT1 | high |
| 395 | 2021 | Steam | Disco Elysium: The | CC6 | CC8 | R5 | G4 | LT1 | high |
| 396 | 2021 | Steam | Doki Doki Literatu | CC8 | CC6 | R5 | G4、G5 | LT1 | high |
| 397 | 2021 | Steam | Dorfromantik | CC10 | CC5 | R3、R4 | G0 | LT1 | medium |
| 398 | 2021 | Steam | Dyson Sphere Progr | CC5 | CC3 | R3 | G2、G3 | LT3 | high |
| 399 | 2021 | Steam | Eastward | CC2 | CC6、CC8 | R4、R5 | G2、G4 | LT1 | medium |
| 400 | 2021 | Steam | Echo Generation | CC2 | CC6 | R4 | G2、G3 | LT1 | high |
| 401 | 2021 | Steam | Eldest Souls | CC2 | — | R1 | G2 | LT1 | high |
| 402 | 2021 | Steam | Everhood | CC2 | — | R1 | G2 | LT1 | high |
| 403 | 2021 | Steam | F1 2021 | CC2 | — | R1 | G2、G3 | LT1、LT3 | high |
| 404 | 2021 | Steam | Farming Simulator  | CC5 | CC4 | R3 | G3 | LT3 | high |
| 405 | 2021 | Steam | Fatal Frame: Maide | CC2 | — | R1、R5 | G2、G4 | LT1 | high |
| 406 | 2021 | Steam | Football Manager 2 | CC5 | — | R3 | G2、G4 | LT3 | high |
| 407 | 2021 | Steam | Forza Horizon 5 | CC2 | CC4、CC7 | R1 | G2、G3 | LT1、LT3 | medium |
| 408 | 2021 | Steam | Gamedec | CC6 | — | R4 | G4 | LT1 | high |
| 409 | 2021 | Steam | Genesis Noir | CC6 | — | R4、R5 | G4 | LT1 | high |
| 410 | 2021 | Steam | Grime | CC2 | — | R1 | G2、G3 | LT1 | high |
| 411 | 2021 | Steam | Guardians of the G | CC2 | CC8 | R1、R5 | G2、G5 | LT1 | medium |
| 412 | 2021 | Steam | Guilty Gear Strive | CC1 | — | R1 | G2 | LT1 | high |
| 413 | 2021 | Steam | Halo Infinite | CC1 | — | R1 | G2、G3 | LT1、LT3 | high |
| 414 | 2021 | Steam | Humankind | CC5 | — | R3 | G2、G4 | LT3 | high |
| 415 | 2021 | Steam | Inscryption | CC6 | CC4 | R3、R4 | G4 | LT1 | high |
| 416 | 2021 | Steam | It Takes Two | CC9 | CC8 | R4 | G2 | LT1 | high |
| 417 | 2021 | Steam | Jett: The Far Shor | CC10 | — | R5 | G4 | LT1 | medium |
| 418 | 2021 | Steam | Judgment | CC2 | CC6 | R1、R4 | G2、G4 | LT1 | medium |
| 419 | 2021 | Steam | KeyWe | CC9 | — | R4 | G2 | LT1 | high |
| 420 | 2021 | Steam | Lake | CC10 | — | R5 | G0 | LT1 | high |
| 421 | 2021 | Steam | Legend of Mana | CC5 | CC4 | R3、R4 | G2、G3 | LT3 | medium |
| 422 | 2021 | Steam | Lemnis Gate | CC1 | CC6 | R1、R4 | G2、G4 | LT1 | medium |
| 423 | 2021 | Steam | Life is Strange: T | CC8 | CC10 | R5 | G4、G5 | LT3 | high |
| 424 | 2021 | Steam | Loop Hero | CC5 | CC3、CC6 | R2、R3 | G1、G2、G3 | LT2 | medium |
| 425 | 2021 | Steam | Mass Effect Legend | CC8 | CC2、CC4 | R1、R5 | G2、G4、G5 | LT3 | high |
| 426 | 2021 | Steam | NEO: The World End | CC2 | CC6、CC4 | R1、R3 | G2、G3 | LT3 | medium |
| 427 | 2021 | Steam | Naraka: Bladepoint | CC1 | CC2 | R1 | G2 | LT1 | high |
| 428 | 2021 | Steam | New World | CC9 | CC3、CC5 | R1、R2 | G1、G2、G3 | LT3 | medium |
| 429 | 2021 | Steam | NieR Replicant | CC2 | CC8、CC4 | R1、R5 | G2、G4 | LT3 | medium |
| 430 | 2021 | Steam | Omori | CC2 | CC8、CC10 | R1、R5 | G2、G4 | LT3 | medium |
| 431 | 2021 | Steam | Outriders | CC3 | CC2 | R1、R2 | G1、G3 | LT3 | high |
| 432 | 2021 | Steam | Pathfinder: Wrath  | CC6 | CC2、CC5 | R3、R4 | G2、G4 | LT3 | medium |
| 433 | 2021 | Steam | Psychonauts 2 | CC2 | CC6、CC10 | R1、R4 | G2、G4 | LT3 | medium |
| 434 | 2021 | Steam | Quake Remaster | CC1 | CC2 | R1 | G2 | LT1 | high |
| 435 | 2021 | Steam | Raji: An Ancient E | CC2 | — | R1 | G2 | LT3 | high |
| 436 | 2021 | Steam | Resident Evil Vill | CC2 | CC8、CC4 | R1、R5 | G2、G3 | LT3 | high |
| 437 | 2021 | Steam | Sable | CC10 | CC4 | R5 | G4 | LT3 | medium |
| 438 | 2021 | Steam | Saturnalia | CC2 | CC6 | R4、R5 | G4 | LT1 | medium |
| 439 | 2021 | Steam | Scarlet Nexus | CC2 | CC8、CC4 | R1、R3 | G2、G4 | LT3 | medium |
| 440 | 2021 | Steam | Severed Steel | CC2 | — | R1 | G2 | LT1 | high |
| 441 | 2021 | Steam | Solar Ash | CC2 | — | R1 | G2 | LT1 | medium |
| 442 | 2021 | Steam | Solasta: Crown of  | CC2 | CC4 | R4 | G2、G3 | LT1、LT3 | medium |
| 443 | 2021 | Steam | Song of Farca | CC6 | — | R4 | G4 | LT1 | high |
| 444 | 2021 | Steam | Subnautica: Below  | CC2 | CC4 | R3 | G2、G3 | LT3 | medium |
| 445 | 2021 | Steam | Super Robot Wars 3 | CC2 | CC4 | R4 | G1、G3 | LT1、LT3 | medium |
| 446 | 2021 | Steam | TOEM | CC10 | CC4 | R4 | G4 | LT1 | medium |
| 447 | 2021 | Steam | Tale of Immortal | CC3 | CC4 | R2、R3 | G1、G2 | LT3 | high |
| 448 | 2021 | Steam | Tales of Arise | CC2 | — | R1 | G1、G2 | LT1、LT3 | medium |
| 449 | 2021 | Steam | The Artful Escape | CC10 | — | R5 | G4 | LT1 | high |
| 450 | 2021 | Steam | The Ascent | CC2 | CC4 | R1 | G1、G2 | LT1、LT3 | medium |
| 451 | 2021 | Steam | The Forgotten City | CC6 | — | R4 | G4 | LT1 | high |
| 452 | 2021 | Steam | The Great Ace Atto | CC6 | — | R4 | G4 | LT1 | high |
| 453 | 2021 | Steam | The Last Stand: Af | CC2 | CC4 | R1、R3 | G2、G3 | LT1、LT2 | medium |
| 454 | 2021 | Steam | The Procession to  | CC6 | — | R4 | G4 | LT1 | medium |
| 455 | 2021 | Steam | Timberborn | CC5 | — | R3 | G2、G3 | LT3 | high |
| 456 | 2021 | Steam | Tribes of Midgard | CC2 | CC9 | R1、R3 | G2、G3 | LT1、LT2 | medium |
| 457 | 2021 | Steam | Unpacking | CC10 | — | R4、R5 | G4 | LT1 | medium |
| 458 | 2021 | Steam | Valheim | CC2 | CC5、CC9 | R1、R3 | G2、G3 | LT3 | medium |
| 459 | 2021 | Steam | Voice of Cards: Th | CC2 | CC4 | R4 | G2、G4 | LT1、LT3 | medium |
| 460 | 2021 | Steam | White Shadows | CC2 | — | R1 | G2 | LT1 | medium |
| 461 | 2021 | Steam | Wildermyth | CC8 | CC4 | R5、R3 | G5、G2 | LT3 | medium |
| 462 | 2021 | Steam | Yakuza 6: The Song | CC2 | CC10 | R1、R5 | G2、G3 | LT2 | medium |
| 463 | 2020 | Steam | Among Us | CC1 | CC6 | R4、R5 | G0 | LT1 | high |
| 464 | 2020 | Steam | Black Mesa | CC2 | — | R1 | G2 | LT2 | high |
| 465 | 2020 | Steam | Bloodroots | CC2 | — | R1 | G2 | LT1 | medium |
| 466 | 2020 | Steam | Carrion | CC10 | CC2 | R1、R4 | G2 | LT2 | medium |
| 467 | 2020 | Steam | Cloudpunk | CC8 | — | R5 | G4 | LT2 | medium |
| 468 | 2020 | Steam | Command & Conquer  | CC1 | CC5 | R3、R1 | G2、G3 | LT1、LT3 | medium |
| 469 | 2020 | Steam | Crusader Kings III | CC5 | CC8 | R3、R5 | G4、G5 | LT3 | high |
| 470 | 2020 | Steam | Crysis Remastered | CC2 | — | R1 | G2 | LT2 | high |
| 471 | 2020 | Steam | Cyberpunk 2077 | CC2 | CC8、CC4 | R1、R5 | G2、G3 | LT3 | medium |
| 472 | 2020 | Steam | Deep Rock Galactic | CC9 | CC2 | R1、R3 | G2、G3 | LT1、LT3 | medium |
| 473 | 2020 | Steam | Desperados III | CC6 | CC2 | R4、R3 | G4、G2 | LT1 | high |
| 474 | 2020 | Steam | Destroy All Humans | CC10 | CC2 | R1 | G2 | LT2 | medium |
| 475 | 2020 | Steam | Doom Eternal | CC2 | — | R1 | G2 | LT1、LT2 | high |
| 476 | 2020 | Steam | F1 2020 | CC1 | CC2 | R1 | G2 | LT1、LT3 | medium |
| 477 | 2020 | Steam | Factorio | CC5 | — | R3 | G4、G2 | LT3 | high |
| 478 | 2020 | Steam | Fall Guys: Ultimat | CC10 | CC1 | R1、R4 | G0 | LT1 | medium |
| 479 | 2020 | Steam | Football Manager 2 | CC5 | CC1 | R3、R2 | G4、G3 | LT3 | medium |
| 480 | 2020 | Steam | Gears Tactics | CC2 | CC6 | R1、R4 | G2、G3 | LT2 | medium |
| 481 | 2020 | Steam | Genshin Impact | CC8 | CC2、CC4 | R1、R5 | G3、G5 | LT3、LT4 | high |
| 482 | 2020 | Steam | Ghostrunner | CC2 | — | R1 | G2 | LT1 | high |
| 483 | 2020 | Steam | Gloomhaven | CC6 | CC2 | R4 | G2、G4 | LT1、LT3 | high |
| 484 | 2020 | Steam | Godfall | CC3 | CC2 | R1、R2 | G1、G3 | LT1、LT3 | high |
| 485 | 2020 | Steam | Going Under | CC2 | CC10 | R1 | G3 | LT1 | medium |
| 486 | 2020 | Steam | Grounded | CC5 | CC2 | R3、R4 | G2、G3 | LT3 | high |
| 487 | 2020 | Steam | Hades | CC2 | CC6、CC8 | R1、R5 | G2、G4、G5 | LT1、LT2 | high |
| 488 | 2020 | Steam | Half-Life: Alyx | CC2 | CC6 | R1、R5 | G2、G4 | LT1 | high |
| 489 | 2020 | Steam | Immortals Fenyx Ri | CC2 | CC6、CC4 | R1、R4 | G2、G3 | LT1、LT3 | high |
| 490 | 2020 | Steam | Iron Harvest | CC5 | CC1 | R3 | G2 | LT1 | medium |
| 491 | 2020 | Steam | Mafia: Definitive  | CC2 | CC8 | R1、R5 | G4 | LT1 | high |
| 492 | 2020 | Steam | Marvel's Avengers | CC3 | CC2、CC4 | R1、R2 | G1、G3 | LT1、LT3 | high |
| 493 | 2020 | Steam | Microsoft Flight S | CC5 | CC4 | R3、R5 | G2、G4 | LT4 | high |
| 494 | 2020 | Steam | Mortal Shell | CC2 | CC6 | R1 | G2、G3 | LT1 | high |
| 495 | 2020 | Steam | Mount & Blade II:  | CC5 | CC1、CC9 | R1、R3 | G2、G3 | LT3 | high |
| 496 | 2020 | Steam | Moving Out | CC10 | CC9 | R4 | G0 | LT1 | high |
| 497 | 2020 | Steam | Muck | CC5 | CC2 | R3、R4 | G2、G3 | LT1、LT2 | high |
| 498 | 2020 | Steam | Neon Abyss | CC3 | CC6 | R1、R3 | G1、G3 | LT1、LT2 | medium |
| 499 | 2020 | Steam | Noita | CC6 | CC5 | R3 | G4、G2 | LT1 | high |
| 500 | 2020 | Steam | One Step From Eden | CC6 | CC2 | R1 | G2、G4 | LT1 | high |
| 501 | 2020 | Steam | Ori and the Will o | CC2 | — | R1 | G2 | LT1 | high |
| 502 | 2020 | Steam | Othercide | CC2 | — | R2、R4 | G2、G3 | LT2 | high |
| 503 | 2020 | Steam | Paradise Killer | CC6 | CC4 | R4 | G4 | LT1 | high |
| 504 | 2020 | Steam | Phasmophobia | CC6 | CC9、CC10 | R4、R5 | G4、G3 | LT1 | medium |
| 505 | 2020 | Steam | Resident Evil 3 | CC2 | — | R1、R4 | G2、G3 | LT1 | high |
| 506 | 2020 | Steam | Risk of Rain 2 | CC3 | CC2、CC4 | R1、R3 | G1、G3 | LT1 | medium |
| 507 | 2020 | Steam | Rogue Company | CC1 | CC9 | R1 | G2、G3 | LT1、LT3 | high |
| 508 | 2020 | Steam | Rust | CC1 | CC5、CC9 | R1、R3 | G3、G2 | LT3 | high |
| 509 | 2020 | Steam | Sakuna: Of Rice an | CC5 | CC2、CC3 | R1、R2 | G2、G1 | LT2 | medium |
| 510 | 2020 | Steam | Satisfactory | CC5 | — | R3 | G2、G3 | LT3 | high |
| 511 | 2020 | Steam | Skul: The Hero Sla | CC2 | CC3、CC6 | R1、R3 | G2、G3 | LT1 | medium |
| 512 | 2020 | Steam | SnowRunner | CC2 | CC5 | R1、R4 | G2、G3 | LT3 | medium |
| 513 | 2020 | Steam | Spellbreak | CC1 | CC6 | R1、R3 | G2 | LT1 | high |
| 514 | 2020 | Steam | Spelunky 2 | CC2 | CC6 | R1、R3 | G2、G4 | LT1 | medium |
| 515 | 2020 | Steam | Spiritfarer | CC8 | CC5、CC4 | R5、R2 | G5、G2 | LT2 | high |
| 516 | 2020 | Steam | Star Wars: Squadro | CC1 | CC2 | R1 | G2、G3 | LT1、LT3 | high |
| 517 | 2020 | Steam | Streets of Rage 4 | CC2 | CC10 | R1 | G2 | LT1 | high |
| 518 | 2020 | Steam | The Walking Dead:  | CC2 | CC10 | R1、R5 | G2、G3 | LT2 | high |
| 519 | 2020 | Steam | Trackmania | CC2 | CC1、CC7 | R1 | G2 | LT1、LT3 | medium |
| 520 | 2020 | Steam | Trials of Mana | CC2 | CC3、CC4 | R1、R2 | G1、G2、G3 | LT2 | medium |
| 521 | 2020 | Steam | Umurangi Generatio | CC6 | CC4 | R4 | G4 | LT1 | medium |
| 522 | 2020 | Steam | Wasteland 3 | CC2 | CC4 | R1、R4 | G2、G3 | LT2、LT3 | high |
| 523 | 2020 | Steam | Watch Dogs: Legion | CC2 | CC4 | R1、R4 | G2、G3 | LT2、LT3 | medium |
| 524 | 2020 | Steam | XCOM: Chimera Squa | CC2 | CC4 | R1、R4 | G2、G3 | LT2、LT3 | high |
| 525 | 2020 | Steam | Yakuza: Like a Dra | CC2 | CC4 | R1、R4 | G2、G3 | LT2、LT3 | high |
| 526 | 2019 | Steam | Apex 英雄 | CC1 | CC4 | R1 | G2 | LT1、LT3 | high |
| 527 | 2019 | Steam | Gato Roboto | CC2 | — | R1、R4 | G2 | LT1 | high |
| 528 | 2019 | Steam | Mordhau | CC1 | — | R1 | G2 | LT1 | high |
| 529 | 2019 | Steam | 三国志14 | CC5 | — | R3 | G2、G4 | LT3 | high |
| 530 | 2019 | Steam | 代码薇拉 | CC2 | — | R1 | G2 | LT1 | high |
| 531 | 2019 | Steam | 全面战争：三国 | CC5 | — | R1、R3 | G2、G4 | LT3 | high |
| 532 | 2019 | Steam | 只狼：影逝二度 | CC2 | — | R1 | G2 | LT1 | high |
| 533 | 2019 | Steam | 命运2：暗影要塞 | CC2 | CC4、CC9 | R1 | G2、G3 | LT3 | medium |
| 534 | 2019 | Steam | 圣歌 | CC2 | CC4 | R1 | G2、G3 | LT3 | high |
| 535 | 2019 | Steam | 地铁：离去 | CC2 | — | R1、R4 | G2、G3 | LT2 | high |
| 536 | 2019 | Steam | 夜勤人 | CC5 | CC4 | R1、R3 | G2、G3 | LT2 | medium |
| 537 | 2019 | Steam | 天外世界 | CC2 | CC4 | R1、R4 | G2、G3、G4 | LT2 | high |
| 538 | 2019 | Steam | 女巫布莱尔 | CC10 | — | R5 | G4 | LT1 | medium |
| 539 | 2019 | Steam | 威尔莫特的仓库 | CC5 | — | R3、R4 | G2 | LT1 | high |
| 540 | 2019 | Steam | 尘埃拉力赛2.0 | CC2 | — | R1 | G2 | LT1 | high |
| 541 | 2019 | Steam | 巴巴是你 | CC6 | — | R4 | G4 | LT1 | high |
| 542 | 2019 | Steam | 幸福工厂 | CC5 | CC4 | R3 | G2、G3 | LT3 | high |
| 543 | 2019 | Steam | 战争机器5 | CC2 | CC1 | R1 | G2、G3 | LT1、LT3 | medium |
| 544 | 2019 | Steam | 战地5 | CC1 | CC9 | R1 | G2、G3 | LT1、LT3 | high |
| 545 | 2019 | Steam | 捣蛋鹅 | CC10 | — | R4 | G0 | LT1 | high |
| 546 | 2019 | Steam | 控制 | CC2 | — | R1 | G2、G4 | LT1、LT2 | high |
| 547 | 2019 | Steam | 无主之地3 | CC3 | CC4 | R1、R2 | G1、G3 | LT1、LT3 | high |
| 548 | 2019 | Steam | 星球大战 绝地：陨落的武士团 | CC2 | — | R1 | G2 | LT1、LT2 | high |
| 549 | 2019 | Steam | 星际拓荒 | CC6 | — | R4、R5 | G4 | LT1 | high |
| 550 | 2019 | Steam | 杀戮尖塔 | CC6 | CC4 | R3、R4 | G2、G4 | LT1、LT2 | high |
| 551 | 2019 | Steam | 极乐迪斯科 | CC6 | CC8 | R5 | G4、G5 | LT1、LT2 | high |
| 552 | 2019 | Steam | 武士零 | CC2 | — | R1 | G2 | LT1 | high |
| 553 | 2019 | Steam | 死亡搁浅 | CC5 | CC9 | R3、R5 | G2、G3 | LT3 | medium |
| 554 | 2019 | Steam | 汤姆克兰西：全境封锁2 | CC3 | CC1、CC4 | R1、R2 | G1、G3 | LT1、LT3 | high |
| 555 | 2019 | Steam | 沉没之城 | CC6 | — | R4、R5 | G4 | LT1、LT2 | high |
| 556 | 2019 | Steam | 波西亚时光 | CC5 | CC4、CC8 | R2、R4 | G2、G3、G5 | LT3 | high |
| 557 | 2019 | Steam | 海岛大亨6 | CC5 | — | R3 | G2 | LT3 | high |
| 558 | 2019 | Steam | 炉石传说：酒馆战棋 | CC1 | CC6 | R3、R4 | G2、G4 | LT1 | high |
| 559 | 2019 | Steam | 狂怒2 | CC2 | — | R1 | G2 | LT1、LT2 | high |
| 560 | 2019 | Steam | 狂热运输2 | CC5 | — | R3 | G2 | LT3 | high |
| 561 | 2019 | Steam | 生化危机2：重制版 | CC2 | CC4 | R1、R4 | G2、G3 | LT1、LT2 | high |
| 562 | 2019 | Steam | 皇牌空战7：未知空域 | CC2 | — | R1 | G2、G3 | LT1、LT2 | high |
| 563 | 2019 | Steam | 纪元1800 | CC5 | — | R3 | G2、G3 | LT3 | high |
| 564 | 2019 | Steam | 绿色地狱 | CC2 | — | R2、R4 | G2、G3 | LT3 | high |
| 565 | 2019 | Steam | 缺氧 | CC5 | — | R3 | G2、G4 | LT3 | high |
| 566 | 2019 | Steam | 荒野大镖客：救赎2 | CC8 | CC4 | R5、R1 | G5、G3 | LT3 | medium |
| 567 | 2019 | Steam | 血污：夜之仪式 | CC2 | CC4 | R1、R4 | G2、G3 | LT1、LT3 | high |
| 568 | 2019 | Steam | 遗迹：灰烬重生 | CC2 | CC4 | R1、R3 | G2、G3 | LT1、LT3 | high |
| 569 | 2019 | Steam | 雨中冒险2 | CC2 | CC4 | R1、R3 | G2、G3 | LT1、LT2 | high |
| 570 | 2019 | Steam | 雷霆一击 | CC1 | — | R1 | G2 | LT1 | high |
| 571 | 2019 | Steam | 骰子地下城 | CC6 | — | R3、R4 | G4、G2 | LT1 | high |
| 572 | 2019 | Steam | 鬼泣5 | CC2 | — | R1 | G2 | LT1、LT2 | high |
| 573 | 2019 | Steam | 魔兽世界：经典旧世 | CC9 | CC2、CC4 | R1、R2 | G2、G3、G5 | LT3 | medium |
| 574 | 2018 | Steam | Amid Evil | CC2 | — | R1 | G2 | LT1 | high |
| 575 | 2018 | Steam | Artifact | CC6 | CC4 | R3 | G4、G2 | LT1、LT3 | medium |
| 576 | 2018 | Steam | Contractors | CC1 | — | R1 | G2 | LT1 | high |
| 577 | 2018 | Steam | Dusk | CC2 | — | R1 | G2 | LT1 | high |
| 578 | 2018 | Steam | Grip | CC1 | — | R1 | G2 | LT1 | high |
| 579 | 2018 | Steam | Kenshi | CC5 | — | R3 | G2、G3、G4 | LT3 | high |
| 580 | 2018 | Steam | Minit | CC6 | — | R4 | G4 | LT1 | high |
| 581 | 2018 | Steam | Realm Royale | CC1 | CC6 | R1 | G2、G3 | LT1 | medium |
| 582 | 2018 | Steam | Synthetik | CC2 | CC6 | R1 | G2、G3 | LT1、LT2 | medium |
| 583 | 2018 | Steam | 世界最终幻想 | CC2 | CC4 | R2、R4 | G3、G1 | LT2、LT3 | medium |
| 584 | 2018 | Steam | 二之国2：亡灵之国 | CC5 | CC2、CC4 | R1、R3 | G1、G3 | LT3 | medium |
| 585 | 2018 | Steam | 交叉代码 | CC6 | CC2 | R1、R4 | G2、G4 | LT1 | medium |
| 586 | 2018 | Steam | 伊苏8：达娜的安魂曲 | CC2 | — | R1 | G2、G3 | LT1、LT3 | high |
| 587 | 2018 | Steam | 侏罗纪世界：进化 | CC5 | CC4 | R3、R4 | G3、G1 | LT3 | high |
| 588 | 2018 | Steam | 信使 | CC2 | CC6 | R1、R4 | G2、G4 | LT1 | medium |
| 589 | 2018 | Steam | 全面战争传奇：不列颠尼亚王座 | CC5 | CC1 | R3、R1 | G2、G1 | LT3 | medium |
| 590 | 2018 | Steam | 冰城传奇4 | CC2 | CC6 | R1、R4 | G2、G3 | LT1、LT3 | medium |
| 591 | 2018 | Steam | 冰汽时代 | CC5 | — | R3、R4 | G2、G4 | LT3 | high |
| 592 | 2018 | Steam | 刺客信条：奥德赛 | CC2 | CC3、CC4 | R1、R2 | G1、G2、G3 | LT3 | medium |
| 593 | 2018 | Steam | 剑与魔法 | CC2 | — | R1 | G2 | LT1 | high |
| 594 | 2018 | Steam | 勇者斗恶龙11 | CC2 | CC4 | R1、R4 | G1、G3 | LT3 | high |
| 595 | 2018 | Steam | 北境之地 | CC5 | — | R3、R4 | G2、G1 | LT3 | high |
| 596 | 2018 | Steam | 双点医院 | CC5 | — | R3、R4 | G2、G1 | LT3 | high |
| 597 | 2018 | Steam | 叛乱：沙漠风暴 | CC1 | — | R1 | G2 | LT1 | high |
| 598 | 2018 | Steam | 古墓丽影：暗影 | CC2 | CC6 | R1、R4 | G2、G3 | LT1、LT3 | medium |
| 599 | 2018 | Steam | 吸血鬼 | CC2 | CC5 | R1、R2 | G1、G2 | LT3 | medium |
| 600 | 2018 | Steam | 哈迪斯 | CC2 | CC6、CC4 | R1、R3 | G2、G3、G4 | LT1、LT2 | medium |
| 601 | 2018 | Steam | 《堡垒之夜》 | CC1 | CC4 | R1 | G2、G3 | LT1、LT3 | high |
| 602 | 2018 | Steam | 《墨西哥英雄大混战2》 | CC2 | — | R1 | G2 | LT1 | high |
| 603 | 2018 | Steam | 《夜下降生》 | CC1 | — | R1 | G2 | LT1 | high |
| 604 | 2018 | Steam | 《天国：拯救》 | CC2 | — | R1 | G2、G3 | LT1、LT3 | high |
| 605 | 2018 | Steam | 《奇异人生2》 | CC8 | — | R5 | G4、G5 | LT1 | high |
| 606 | 2018 | Steam | 《奇异小队》 | CC2 | — | R1、R4 | G2、G3 | LT1 | medium |
| 607 | 2018 | Steam | 《奥伯拉·丁的回归》 | CC6 | — | R4 | G4 | LT1 | high |
| 608 | 2018 | Steam | 《如龙0》 | CC2 | CC4 | R1、R4 | G2、G3 | LT1、LT3 | medium |
| 609 | 2018 | Steam | 《孤岛惊魂5》 | CC2 | CC4 | R1、R4 | G2、G3 | LT1、LT3 | high |
| 610 | 2018 | Steam | 《守墓人》 | CC5 | CC4 | R3、R4 | G2、G3 | LT2、LT3 | high |
| 611 | 2018 | Steam | 《实况足球2019》 | CC1 | — | R1 | G2 | LT1、LT3 | high |
| 612 | 2018 | Steam | 《巫师之昆特牌》 | CC1 | CC4 | R4 | G2、G3、G4 | LT1、LT3 | high |
| 613 | 2018 | Steam | 《巫师之昆特牌：王权的陨落》 | CC2 | CC4 | R4、R5 | G2、G3、G4 | LT1、LT3 | high |
| 614 | 2018 | Steam | 《帝国时代：决定版》 | CC1 | — | R3 | G2、G3 | LT1、LT3 | medium |
| 615 | 2018 | Steam | 《幽匿协议》 | CC6 | — | R4 | G2、G4 | LT1 | high |
| 616 | 2018 | Steam | 《开拓者：拥王者》 | CC2 | CC4 | R3、R4 | G2、G3、G4 | LT1、LT3 | medium |
| 617 | 2018 | Steam | 《怪物猎人：世界》 | CC2 | CC4 | R1 | G2、G3 | LT1、LT3 | high |
| 618 | 2018 | Steam | 《战场女武神4》 | CC2 | — | R1、R4 | G2、G3 | LT1、LT3 | high |
| 619 | 2018 | Steam | 《战锤：末世鼠疫2》 | CC10 | CC4 | R1 | G2、G3 | LT1、LT3 | medium |
| 620 | 2018 | Steam | 《房产达人》 | CC10 | — | R4 | G3 | LT1、LT2 | high |
| 621 | 2018 | Steam | 撞车嘉年华 | CC10 | CC4 | R1、R3 | G3、G2 | LT1、LT2 | medium |
| 622 | 2018 | Steam | 旗帜的传说3 | CC2 | CC8 | R4、R5 | G2、G4 | LT1、LT3 | medium |
| 623 | 2018 | Steam | 最终幻想15 | CC2 | CC8、CC4 | R1、R5 | G2、G3、G5 | LT3、LT4 | medium |
| 624 | 2018 | Steam | 木筏生存 | CC5 | CC9、CC4 | R3、R2 | G3、G2 | LT3、LT4 | medium |
| 625 | 2018 | Steam | 机甲战士 | CC6 | CC2、CC4 | R1、R3 | G2、G3、G4 | LT1、LT3 | medium |
| 626 | 2018 | Steam | 杀手2 | CC6 | CC2 | R3、R4 | G4、G2 | LT1、LT2 | high |
| 627 | 2018 | Steam | 极限竞速：地平线4 | CC2 | CC4、CC7 | R1、R4 | G2、G3 | LT1、LT3 | medium |
| 628 | 2018 | Steam | 格莉斯 | CC10 | CC8 | R5、R4 | G2、G4 | LT1、LT3 | medium |
| 629 | 2018 | Steam | 森林 | CC5 | CC2、CC9 | R3、R1 | G3、G2 | LT3、LT4 | medium |
| 630 | 2018 | Steam | 模拟农场19 | CC5 | CC10、CC4 | R3、R2 | G3、G2 | LT3、LT4 | high |
| 631 | 2018 | Steam | 正当防卫4 | CC10 | CC2 | R1、R3 | G2、G3 | LT1、LT4 | medium |
| 632 | 2018 | Steam | 死亡细胞 | CC2 | CC6、CC4 | R1、R3 | G2、G3 | LT1、LT2 | high |
| 633 | 2018 | Steam | 毛线小精灵2 | CC8 | CC9、CC6 | R4、R5 | G5、G2 | LT1、LT3 | medium |
| 634 | 2018 | Steam | 永恒之柱2：死火 | CC2 | CC6、CC8 | R3、R4 | G2、G4、G3 | LT3、LT1 | medium |
| 635 | 2018 | Steam | 洛克人11 | CC2 | — | R1、R4 | G2 | LT1、LT2 | high |
| 636 | 2018 | Steam | 流放者柯南 | CC5 | CC2、CC9、CC4 | R3、R1 | G3、G2 | LT3、LT4 | medium |
| 637 | 2018 | Steam | 深岩银河 | CC9 | CC2、CC4 | R1、R3 | G2、G3 | LT1、LT3 | medium |
| 638 | 2018 | Steam | 深海迷航 | CC5 | CC2、CC4 | R3、R2 | G3、G2、G4 | LT3、LT4 | medium |
| 639 | 2018 | Steam | 火车山谷2 | CC6 | CC5 | R3、R4 | G4、G2 | LT1、LT2 | medium |
| 640 | 2018 | Steam | 灵魂能力6 | CC1 | CC7、CC4 | R1 | G2、G3 | LT1、LT2 | high |
| 641 | 2018 | Steam | 猎杀：对决 | CC1 | CC2 | R1 | G2、G3 | LT1 | high |
| 642 | 2018 | Steam | 甜甜圈县 | CC10 | — | R4 | G0 | LT1 | high |
| 643 | 2018 | Steam | 生存火星 | CC5 | — | R3 | G2、G3 | LT3 | high |
| 644 | 2018 | Steam | 盗贼之海 | CC9 | CC1、CC4 | R1、R3 | G3、G5 | LT1、LT3 | medium |
| 645 | 2018 | Steam | 绝地求生 | CC1 | CC3 | R1 | G2、G3 | LT1 | high |
| 646 | 2018 | Steam | 胡闹厨房2 | CC10 | CC9 | R4 | G2 | LT1 | medium |
| 647 | 2018 | Steam | 节奏光剑 | CC2 | CC10 | R1 | G2 | LT1 | medium |
| 648 | 2018 | Steam | 花园之间 | CC6 | — | R4 | G4 | LT1 | high |
| 649 | 2018 | Steam | 苍翼默示录：交叉组队战 | CC1 | CC4 | R1 | G2 | LT1 | high |
| 650 | 2018 | Steam | 蔚蓝 | CC2 | — | R1 | G2 | LT1 | high |
| 651 | 2018 | Steam | 血污：月之诅咒 | CC2 | CC4 | R1 | G2、G3 | LT1 | high |
| 652 | 2018 | Steam | 装机模拟器 | CC5 | CC6 | R3、R4 | G2、G4 | LT3 | medium |
| 653 | 2018 | Steam | 足球经理2019 | CC5 | CC6 | R3 | G2、G4 | LT3 | medium |
| 654 | 2018 | Steam | 辐射76 | CC3 | CC1、CC4 | R1、R2 | G1、G3 | LT3 | medium |
| 655 | 2018 | Steam | 边缘世界 | CC5 | CC6 | R3 | G2、G4 | LT3 | high |
| 656 | 2018 | Steam | 达尔文计划 | CC1 | CC2 | R1 | G2 | LT1 | high |
| 657 | 2018 | Steam | 过山车大亨 | CC5 | — | R3 | G2、G3 | LT3 | high |
| 658 | 2018 | Steam | 逃出生天 | CC9 | CC8 | R4 | G5 | LT1 | high |
| 659 | 2018 | Steam | 铁路帝国 | CC5 | — | R3 | G2、G3 | LT3 | high |
| 660 | 2018 | Steam | 陷阵之志 | CC6 | CC2 | R4 | G4 | LT1 | high |
| 661 | 2018 | Steam | 龙珠战士Z | CC1 | — | R1 | G2 | LT1 | high |
| 662 | 2017 | Steam | A Hat in Time | CC2 | CC4 | R4 | G2、G3 | LT1、LT2 | high |
| 663 | 2017 | Steam | Albion Online | CC9 | CC5 | R3 | G3、G2 | LT3 | medium |
| 664 | 2017 | Steam | Ark: Survival Evol | CC5 | CC9、CC4 | R3 | G3、G2 | LT3 | medium |
| 665 | 2017 | Steam | Assassin's Creed O | CC2 | CC4 | R1、R4 | G3、G2 | LT2、LT3 | high |
| 666 | 2017 | Steam | Battle Chasers: Ni | CC6 | CC2 | R4 | G4、G3 | LT2 | medium |
| 667 | 2017 | Steam | Battlerite | CC1 | — | R1 | G2 | LT1 | high |
| 668 | 2017 | Steam | Bayonetta | CC2 | — | R1 | G2 | LT1 | high |
| 669 | 2017 | Steam | Blackwake | CC9 | CC1 | R1 | G2 | LT1 | medium |
| 670 | 2017 | Steam | Call of Duty: WWII | CC1 | — | R1 | G2、G3 | LT1、LT2 | high |
| 671 | 2017 | Steam | Caveblazer | CC6 | CC2 | R3、R1 | G4、G2 | LT1 | medium |
| 672 | 2017 | Steam | Conan Exiles | CC5 | CC9、CC2 | R3 | G3、G2 | LT3 | medium |
| 673 | 2017 | Steam | Cuphead | CC2 | — | R1、R4 | G2 | LT1 | high |
| 674 | 2017 | Steam | Dead Cells | CC6 | CC2 | R3、R1 | G4、G2 | LT1、LT2 | medium |
| 675 | 2017 | Steam | Destiny 2 | CC2 | CC9、CC4 | R1、R4 | G3、G2 | LT3 | medium |
| 676 | 2017 | Steam | Dirt 4 | CC2 | — | R1 | G2 | LT1 | high |
| 677 | 2017 | Steam | Dishonored: Death  | CC6 | CC2 | R3、R4 | G4、G2 | LT1 | medium |
| 678 | 2017 | Steam | Divinity: Original | CC6 | CC5 | R3 | G4、G2 | LT2、LT3 | high |
| 679 | 2017 | Steam | Doki Doki Literatu | CC10 | CC8 | R5 | G4 | LT1 | medium |
| 680 | 2017 | Steam | Dreadnought | CC1 | — | R1 | G2 | LT1 | high |
| 681 | 2017 | Steam | Dungeons 3 | CC5 | CC2 | R3、R4 | G2、G3 | LT2、LT3 | medium |
| 682 | 2017 | Steam | ELEX | CC2 | CC3 | R1、R2 | G2、G3 | LT3 | medium |
| 683 | 2017 | Steam | Endless Space 2 | CC5 | CC9 | R3 | G2、G4 | LT3 | high |
| 684 | 2017 | Steam | Everspace | CC2 | CC6 | R1、R3 | G2、G3 | LT1、LT2 | medium |
| 685 | 2017 | Steam | F1 2017 | CC2 | CC5 | R1、R4 | G2、G3 | LT3 | medium |
| 686 | 2017 | Steam | Faeria | CC6 | CC1 | R3、R4 | G2、G4 | LT1 | medium |
| 687 | 2017 | Steam | Flinthook | CC2 | CC6 | R1 | G2 | LT1、LT2 | medium |
| 688 | 2017 | Steam | For Honor | CC1 | CC2 | R1 | G2 | LT1、LT3 | high |
| 689 | 2017 | Steam | Foxhole | CC9 | CC5 | R3、R4 | G2、G3 | LT3、LT4 | high |
| 690 | 2017 | Steam | Friday the 13th: T | CC10 | CC1 | R1、R5 | G0 | LT1 | medium |
| 691 | 2017 | Steam | Getting Over It wi | CC2 | CC10 | R1、R4 | G2 | LT1 | medium |
| 692 | 2017 | Steam | Ghost Recon Wildla | CC9 | CC2 | R1、R4 | G2、G3 | LT3 | medium |
| 693 | 2017 | Steam | Guilty Gear Xrd Re | CC1 | — | R1 | G2 | LT1 | high |
| 694 | 2017 | Steam | Gwent: The Witcher | CC1 | CC6 | R3、R4 | G2、G4 | LT1、LT3 | medium |
| 695 | 2017 | Steam | Halo Wars 2 | CC5 | CC1 | R3、R4 | G2 | LT1、LT3 | medium |
| 696 | 2017 | Steam | Hellblade: Senua's | CC2 | CC8 | R1、R5 | G4 | LT1 | medium |
| 697 | 2017 | Steam | Hollow Knight | CC2 | CC3 | R1、R4 | G2、G3 | LT3 | high |
| 698 | 2017 | Steam | Human: Fall Flat | CC10 | CC6 | R1、R4 | G2 | LT1 | high |
| 699 | 2017 | Steam | Idle Champions of  | CC3 | CC4 | R2 | G1、G3 | LT2、LT3 | high |
| 700 | 2017 | Steam | Injustice 2 | CC1 | CC3、CC4 | R1、R2 | G1、G2、G3 | LT1、LT3 | medium |
| 701 | 2017 | Steam | Just Dance 2018 | CC10 | CC1 | R1 | G2 | LT1 | high |
| 702 | 2017 | Steam | LawBreakers | CC1 | — | R1 | G2 | LT1 | high |
| 703 | 2017 | Steam | Little Nightmares | CC2 | CC10 | R4 | G4 | LT1 | medium |
| 704 | 2017 | Steam | Marvel vs. Capcom: | CC1 | CC6 | R1 | G2 | LT1 | high |
| 705 | 2017 | Steam | Mass Effect: Andro | CC2 | CC8、CC4 | R1、R5 | G2、G3、G5 | LT3 | medium |
| 706 | 2017 | Steam | Middle-earth: Shad | CC2 | CC5、CC3 | R1、R3 | G2、G3 | LT3 | medium |
| 707 | 2017 | Steam | Nex Machina | CC2 | — | R1 | G2 | LT1 | high |
| 708 | 2017 | Steam | Nidhogg 2 | CC1 | — | R1 | G2 | LT1 | high |
| 709 | 2017 | Steam | NieR: Automata | CC2 | CC6、CC8 | R1、R5 | G2、G4 | LT3 | medium |
| 710 | 2017 | Steam | Night in the Woods | CC8 | CC10 | R5 | G5、G4 | LT1 | high |
| 711 | 2017 | Steam | Northgard | CC5 | CC2 | R3 | G2、G3 | LT3 | high |
| 712 | 2017 | Steam | Okami HD | CC2 | CC6 | R1、R4 | G2、G4 | LT3 | medium |
| 713 | 2017 | Steam | Outlast 2 | CC10 | CC2 | R4 | G4 | LT1 | medium |
| 714 | 2017 | Steam | Oxygen Not Include | CC5 | CC6 | R3 | G2、G4 | LT3 | high |
| 715 | 2017 | Steam | Paladins | CC1 | CC6、CC3 | R1 | G2、G3 | LT1、LT3 | medium |
| 716 | 2017 | Steam | Path of Exile: The | CC2 | CC6、CC3 | R1、R2 | G2、G3 | LT3 | medium |
| 717 | 2017 | Steam | PlayerUnknown's Ba | CC1 | CC3 | R1 | G2、G3 | LT1 | high |
| 718 | 2017 | Steam | Project CARS 2 | CC2 | CC1 | R1 | G2 | LT1、LT3 | medium |
| 719 | 2017 | Steam | Pyre | CC2 | CC8、CC1 | R1、R5 | G2、G5 | LT1、LT3 | medium |
| 720 | 2017 | Steam | Quake Champions | CC1 | — | R1 | G2 | LT1 | high |
| 721 | 2017 | Steam | Ravenfield | CC1 | — | R1 | G2 | LT1 | medium |
| 722 | 2017 | Steam | Resident Evil 7: B | CC2 | — | R1、R4 | G2、G3 | LT1 | high |
| 723 | 2017 | Steam | RiME | CC6 | CC8 | R4、R5 | G4 | LT1 | medium |
| 724 | 2017 | Steam | Shovel Knight: Spe | CC2 | — | R1 | G2 | LT1 | high |
| 725 | 2017 | Steam | Slay the Spire | CC6 | CC4 | R3、R4 | G2、G4 | LT1、LT2 | high |
| 726 | 2017 | Steam | Snake Pass | CC6 | — | R4 | G2 | LT1 | high |
| 727 | 2017 | Steam | Sonic Forces | CC2 | CC4、CC7 | R1 | G2、G3 | LT1 | medium |
| 728 | 2017 | Steam | Sonic Mania | CC2 | — | R1 | G2 | LT1 | high |
| 729 | 2017 | Steam | South Park: The Fr | CC6 | CC8 | R4 | G2、G4 | LT1 | medium |
| 730 | 2017 | Steam | Star Wars Battlefr | CC1 | CC4 | R1 | G2、G3 | LT1、LT3 | high |
| 731 | 2017 | Steam | SteamWorld Dig 2 | CC2 | CC4 | R1、R4 | G2、G3 | LT1、LT2 | medium |
| 732 | 2017 | Steam | Steel Division: No | CC6 | CC9 | R3、R4 | G2、G4 | LT1 | medium |
| 733 | 2017 | Steam | Stick Fight: The G | CC10 | — | R1 | G0 | LT1 | high |
| 734 | 2017 | Steam | Sudden Strike 4 | CC6 | — | R4 | G2、G4 | LT1 | medium |
| 735 | 2017 | Steam | Tacoma | CC6 | CC8 | R5、R4 | G4 | LT1 | medium |
| 736 | 2017 | Steam | Tekken 7 | CC1 | — | R1 | G2 | LT1 | high |
| 737 | 2017 | Steam | The Binding of Isa | CC2 | CC4、CC6 | R1、R3 | G2、G3、G4 | LT1、LT2 | medium |
| 738 | 2017 | Steam | The Escapists 2 | CC6 | CC9 | R3、R4 | G2、G4 | LT1 | medium |
| 739 | 2017 | Steam | The Evil Within 2 | CC2 | — | R1、R4 | G2、G3 | LT1 | high |
| 740 | 2017 | Steam | The Long Dark | CC2 | — | R4 | G2、G3 | LT1 | high |
| 741 | 2017 | Steam | The Mummy Demaster | CC2 | — | R1 | G2、G3 | LT1 | high |
| 742 | 2017 | Steam | The Surge | CC2 | CC4 | R1 | G2、G3 | LT1、LT3 | high |
| 743 | 2017 | Steam | They Are Billions | CC5 | — | R3 | G2、G3 | LT1、LT3 | high |
| 744 | 2017 | Steam | Thimbleweed Park | CC6 | — | R4 | G4 | LT1 | high |
| 745 | 2017 | Steam | Torment: Tides of  | CC6 | CC8 | R5 | G4 | LT1 | medium |
| 746 | 2017 | Steam | Total War: Warhamm | CC5 | CC1 | R3、R1 | G2、G3 | LT1、LT3 | medium |
| 747 | 2017 | Steam | Vanquish | CC2 | — | R1 | G2 | LT1 | high |
| 748 | 2017 | Steam | Warframe: Plains o | CC2 | CC4 | R1、R2 | G2、G3 | LT1、LT3 | medium |
| 749 | 2017 | Steam | Warhammer 40,000:  | CC1 | CC5 | R3、R1 | G2 | LT1 | medium |
| 750 | 2017 | Steam | West of Loathing | CC6 | CC10 | R5、R4 | G4、G2 | LT1 | medium |
| 751 | 2017 | Steam | What Remains of Ed | CC8 | — | R5 | G4 | LT1 | high |
| 752 | 2017 | Steam | Yooka-Laylee | CC2 | CC4 | R1、R4 | G2、G3 | LT1 | high |
| 753 | 2017 | Steam | Yu-Gi-Oh! Duel Lin | CC1 | CC4、CC6 | R3、R4 | G2、G4、G3 | LT1、LT3 | high |
| 754 | 2016 | Steam | Abzû | CC10 | — | R5 | G0 | LT1 | high |
| 755 | 2016 | Steam | Astroneer | CC5 | CC10 | R3 | G2、G3 | LT3、LT4 | medium |
| 756 | 2016 | Steam | Attack on Titan | CC2 | — | R1 | G2 | LT1 | high |
| 757 | 2016 | Steam | Battlefield 1 | CC1 | CC9 | R1 | G2、G3 | LT1、LT3 | medium |
| 758 | 2016 | Steam | Battlefleet Gothic | CC5 | CC1 | R3 | G2、G3 | LT1、LT3 | medium |
| 759 | 2016 | Steam | Call of Duty: Infi | CC1 | CC2 | R1 | G2、G3 | LT1、LT3 | medium |
| 760 | 2016 | Steam | Civilization VI | CC5 | CC1 | R3 | G2、G4 | LT1、LT3 | high |
| 761 | 2016 | Steam | Clustertruck | CC2 | — | R1 | G2 | LT1 | high |
| 762 | 2016 | Steam | Dark Souls III | CC2 | CC4 | R1 | G2、G3 | LT1、LT3 | high |
| 763 | 2016 | Steam | Darkest Dungeon | CC2 | CC4 | R2、R4 | G2、G3 | LT3 | high |
| 764 | 2016 | Steam | Dead by Daylight | CC1 | — | R1 | G2、G3 | LT1、LT3 | high |
| 765 | 2016 | Steam | Deus Ex: Mankind D | CC6 | CC4 | R1、R4 | G2、G4 | LT1、LT3 | medium |
| 766 | 2016 | Steam | Dishonored 2 | CC6 | CC4 | R1、R4 | G2、G4 | LT1、LT3 | medium |
| 767 | 2016 | Steam | Doom | CC2 | — | R1 | G2、G3 | LT1 | high |
| 768 | 2016 | Steam | Dragon's Dogma | CC2 | CC4 | R1 | G2、G3 | LT1、LT3 | high |
| 769 | 2016 | Steam | Enter the Gungeon | CC2 | CC4 | R1、R3 | G2、G3 | LT1、LT2 | high |
| 770 | 2016 | Steam | Far Cry Primal | CC2 | CC4 | R1、R4 | G2、G3 | LT1、LT3 | high |
| 771 | 2016 | Steam | Firewatch | CC8 | — | R5 | G5 | LT1 | high |
| 772 | 2016 | Steam | Grim Dawn | CC2 | CC4 | R1、R2 | G2、G3 | LT3 | high |
| 773 | 2016 | Steam | Hearts of Iron IV | CC5 | — | R3 | G2、G4 | LT3 | high |
| 774 | 2016 | Steam | Hitman | CC6 | CC4 | R1、R4 | G2、G4 | LT1、LT2 | high |
| 775 | 2016 | Steam | Hyper Light Drifte | CC2 | CC4 | R1 | G2、G3 | LT1 | high |
| 776 | 2016 | Steam | Inside | CC6 | — | R4 | G4 | LT1 | high |
| 777 | 2016 | Steam | Job Simulator | CC10 | — | R5 | G0 | LT1 | high |
| 778 | 2016 | Steam | Killing Floor 2 | CC2 | — | R1 | G2、G3 | LT1、LT3 | high |
| 779 | 2016 | Steam | Kingdom: New Lands | CC5 | — | R3、R4 | G2、G4 | LT1、LT3 | high |
| 780 | 2016 | Steam | Layers of Fear | CC10 | — | R5 | G4 | LT1 | high |
| 781 | 2016 | Steam | Move or Die | CC10 | CC1 | R1 | G0 | LT1 | medium |
| 782 | 2016 | Steam | My Summer Car | CC5 | CC2 | R3 | G2、G3 | LT4 | medium |
| 783 | 2016 | Steam | No Man's Sky | CC5 | CC4 | R3、R2 | G3、G2 | LT3 | medium |
| 784 | 2016 | Steam | Offworld Trading C | CC6 | CC5 | R3 | G4、G2 | LT1 | medium |
| 785 | 2016 | Steam | Overcooked! | CC9 | CC10 | R1 | G2 | LT1 | medium |
| 786 | 2016 | Steam | Overwatch | CC1 | CC9 | R1 | G2 | LT1、LT3 | high |
| 787 | 2016 | Steam | Owlboy | CC2 | — | R1、R4 | G2 | LT1 | medium |
| 788 | 2016 | Steam | Planet Coaster | CC5 | CC7 | R3 | G2、G3 | LT3 | high |
| 789 | 2016 | Steam | Poly Bridge | CC6 | CC2 | R3、R4 | G4 | LT1 | medium |
| 790 | 2016 | Steam | Portal Knights | CC5 | CC2、CC4 | R1、R2 | G3、G2 | LT2、LT3 | medium |
| 791 | 2016 | Steam | Punch Club | CC5 | CC3 | R2 | G1、G2 | LT2 | medium |
| 792 | 2016 | Steam | Reigns | CC6 | CC8 | R4 | G4 | LT1 | medium |
| 793 | 2016 | Steam | RimWorld | CC5 | CC8、CC9 | R3 | G2、G3 | LT3 | high |
| 794 | 2016 | Steam | Rise of the Tomb R | CC2 | CC4 | R1、R4 | G2、G3 | LT1 | high |
| 795 | 2016 | Steam | Salt and Sanctuary | CC2 | — | R1 | G2、G3 | LT1 | high |
| 796 | 2016 | Steam | Scrap Mechanic | CC5 | CC6 | R3 | G2、G3 | LT3 | medium |
| 797 | 2016 | Steam | Shadow Tactics | CC6 | CC2 | R4 | G4、G2 | LT1 | medium |
| 798 | 2016 | Steam | Shenzen I/O | CC6 | CC5 | R3、R4 | G4 | LT1 | high |
| 799 | 2016 | Steam | Skyrim SE | CC2 | CC4、CC5 | R1、R2 | G2、G3 | LT3 | medium |
| 800 | 2016 | Steam | Starbound | CC5 | CC2、CC4 | R3、R2 | G3、G2 | LT3 | medium |
| 801 | 2016 | Steam | Stardew Valley | CC5 | CC8、CC4 | R2、R4 | G3、G5 | LT3 | high |
| 802 | 2016 | Steam | Stellaris | CC5 | CC6 | R3 | G2、G4 | LT3 | high |
| 803 | 2016 | Steam | Stephen's Sausage  | CC6 | — | R4 | G4 | LT1 | high |
| 804 | 2016 | Steam | Street Fighter V | CC1 | — | R1 | G2 | LT1、LT3 | high |
| 805 | 2016 | Steam | Superhot | CC6 | — | R1、R4 | G2、G4 | LT1 | medium |
| 806 | 2016 | Steam | Superhot VR | CC6 | — | R1、R4 | G2、G4 | LT1 | medium |
| 807 | 2016 | Steam | The Division | CC2 | CC1、CC4 | R1、R2 | G3、G2 | LT3 | medium |
| 808 | 2016 | Steam | The Witness | CC6 | — | R4 | G4 | LT1 | high |
| 809 | 2016 | Steam | Thumper | CC2 | — | R1 | G2 | LT1 | medium |
| 810 | 2016 | Steam | Titanfall 2 | CC2 | — | R1 | G2 | LT1 | high |
| 811 | 2016 | Steam | Total War: Warhamm | CC5 | CC2 | R3、R1 | G2、G3 | LT3 | high |
| 812 | 2016 | Steam | Tyranny | CC6 | CC8 | R5、R4 | G4、G5 | LT3 | medium |
| 813 | 2016 | Steam | Ultimate Chicken H | CC10 | CC1 | R4、R3 | G0 | LT1 | high |
| 814 | 2016 | Steam | Unravel | CC2 | CC8 | R4、R5 | G2、G4 | LT1 | medium |
| 815 | 2016 | Steam | Va-11 Hall-A | CC8 | CC6 | R5 | G5、G4 | LT1 | high |
| 816 | 2016 | Steam | Watch Dogs 2 | CC2 | CC6 | R1、R3 | G2、G3 | LT3 | medium |
| 817 | 2016 | Steam | XCOM 2 | CC2 | CC5、CC6 | R3、R4 | G2、G3、G4 | LT3 | medium |
| 818 | 2016 | Steam | Zero Escape | CC6 | CC8 | R4、R5 | G4 | LT1 | high |
| 819 | 2026 | 微信小游戏 | 2048 | CC6 | — | R4 | G4 | LT1 | high |
| 820 | 2026 | 微信小游戏 | QQ飞车 | CC1 | CC4 | R1 | G2、G3 | LT1、LT3 | high |
| 821 | 2026 | 微信小游戏 | 一念逍遥 | CC3 | — | R2 | G1 | LT2、LT3 | high |
| 822 | 2026 | 微信小游戏 | 三国志·战略版 | CC9 | CC5 | R3 | G2、G3 | LT3 | high |
| 823 | 2026 | 微信小游戏 | 三国杀 | CC6 | CC1 | R4 | G4 | LT1 | high |
| 824 | 2026 | 微信小游戏 | 不休的乌拉拉 | CC3 | CC9 | R2 | G1、G3 | LT2、LT3 | medium |
| 825 | 2026 | 微信小游戏 | 丛林大作战 | CC1 | — | R1 | G0 | LT1 | high |
| 826 | 2026 | 微信小游戏 | 九阴真经3D | CC1 | CC2 | R1 | G2、G3 | LT3 | medium |
| 827 | 2026 | 微信小游戏 | 乱世王者 | CC9 | CC5 | R3 | G2、G3 | LT3 | high |
| 828 | 2026 | 微信小游戏 | 云上城之歌 | CC2 | CC8、CC4 | R1、R2 | G2、G3 | LT2、LT3 | medium |
| 829 | 2026 | 微信小游戏 | 人生重开模拟器 | CC6 | CC3 | R3、R4 | G4 | LT1 | high |
| 830 | 2026 | 微信小游戏 | 仙剑奇侠传之挥剑问情 | CC2 | CC8、CC4 | R4、R5 | G2、G3 | LT2、LT3 | medium |
| 831 | 2026 | 微信小游戏 | 会说话的安吉拉 | CC8 | CC4 | R5 | G5 | LT4 | high |
| 832 | 2026 | 微信小游戏 | 会说话的汤姆猫 | CC8 | — | R5 | G5 | LT4 | high |
| 833 | 2026 | 微信小游戏 | 会说话的狗狗本 | CC8 | — | R5 | G5 | LT4 | high |
| 834 | 2026 | 微信小游戏 | 你画我猜 | CC10 | CC1 | R4 | G0 | LT1 | high |
| 835 | 2026 | 微信小游戏 | 侠义九州 | CC2 | — | R1 | G2 | LT1、LT3 | high |
| 836 | 2026 | 微信小游戏 | 侠客风云传 | CC6 | CC2、CC8 | R4、R5 | G4、G5 | LT3 | medium |
| 837 | 2026 | 微信小游戏 | 保卫萝卜 | CC6 | CC2 | R4 | G4、G2 | LT1、LT2 | high |
| 838 | 2026 | 微信小游戏 | 修仙模拟器 | CC3 | CC6 | R2、R3 | G1、G4 | LT3 | medium |
| 839 | 2026 | 微信小游戏 | 倒霉熊 | CC10 | — | R1 | G0 | LT1 | high |
| 840 | 2026 | 微信小游戏 | 元气骑士 | CC2 | CC6、CC9 | R1、R3 | G2、G3 | LT1、LT2 | medium |
| 841 | 2026 | 微信小游戏 | 光·遇 | CC8 | CC9、CC4 | R5 | G5 | LT4 | high |
| 842 | 2026 | 微信小游戏 | 全民大乐斗 | CC10 | CC1 | R1 | G2 | LT1 | medium |
| 843 | 2026 | 微信小游戏 | 全职觉醒 | CC2 | CC3 | R1 | G2、G3 | LT2、LT3 | high |
| 844 | 2026 | 微信小游戏 | 决战！平安京 | CC1 | — | R1 | G2 | LT1 | high |
| 845 | 2026 | 微信小游戏 | 几何冲刺 | CC2 | — | R1 | G2 | LT1 | high |
| 846 | 2026 | 微信小游戏 | 别踩白块儿 | CC2 | — | R1 | G2 | LT1 | high |
| 847 | 2026 | 微信小游戏 | 剑与远征：启程 | CC3 | CC4 | R2 | G1、G3 | LT2、LT3 | high |
| 848 | 2026 | 微信小游戏 | 剑网3指尖江湖 | CC2 | CC8 | R1 | G2、G3 | LT2、LT3 | medium |
| 849 | 2026 | 微信小游戏 | 割绳子 | CC6 | — | R4 | G4 | LT1 | high |
| 850 | 2026 | 微信小游戏 | 动物餐厅 | CC10 | CC4、CC8 | R2、R5 | G3、G5 | LT4 | high |
| 851 | 2026 | 微信小游戏 | 反应堆 | CC10 | — | R1 | G0 | LT1 | high |
| 852 | 2026 | 微信小游戏 | 变形金刚：地球之战 | CC1 | CC4、CC9 | R1 | G2、G3 | LT2、LT3 | medium |
| 853 | 2026 | 微信小游戏 | 古剑奇谭木语人 | CC3 | CC4、CC8 | R2 | G1、G3 | LT2、LT3 | high |
| 854 | 2026 | 微信小游戏 | 古镜记 | CC6 | — | R4、R5 | G4 | LT1 | high |
| 855 | 2026 | 微信小游戏 | 叫我万岁爷 | CC5 | CC3、CC4 | R2、R3 | G1、G3 | LT3 | high |
| 856 | 2026 | 微信小游戏 | 史莱姆与地下城 | CC2 | CC6 | R1、R3 | G2、G3 | LT1、LT2 | medium |
| 857 | 2026 | 微信小游戏 | 合成大西瓜 | CC10 | — | R4 | G0 | LT1 | high |
| 858 | 2026 | 微信小游戏 | 吞噬星空：黎明 | CC3 | CC4 | R2 | G1、G3 | LT2、LT3 | high |
| 859 | 2026 | 微信小游戏 | 咸鱼之王 | CC3 | CC4 | R2 | G1 | LT2、LT3 | high |
| 860 | 2026 | 微信小游戏 | 喜羊羊与灰太狼 | CC10 | — | R1 | G0 | LT1 | high |
| 861 | 2026 | 微信小游戏 | 围棋 | CC1 | — | R4 | G2、G4 | LT1 | high |
| 862 | 2026 | 微信小游戏 | 地下城堡2 | CC2 | CC4 | R2、R3 | G2、G3 | LT3 | high |
| 863 | 2026 | 微信小游戏 | 地铁跑酷 | CC2 | — | R1 | G2 | LT1、LT2 | medium |
| 864 | 2026 | 微信小游戏 | 塔防精灵 | CC6 | — | R3、R4 | G2、G4 | LT1、LT2 | medium |
| 865 | 2026 | 微信小游戏 | 墨迹大侠 | CC3 | — | R1、R2 | G1、G2 | LT1、LT2 | high |
| 866 | 2026 | 微信小游戏 | 大话西游 | CC9 | CC4 | R2、R5 | G1、G3、G5 | LT3 | high |
| 867 | 2026 | 微信小游戏 | 大钢琴 | CC2 | — | R1、R4 | G2 | LT1 | high |
| 868 | 2026 | 微信小游戏 | 天天炫斗 | CC2 | — | R1 | G1、G2、G3 | LT1、LT3 | high |
| 869 | 2026 | 微信小游戏 | 天天爱消除 | CC10 | — | R4 | G0 | LT1 | high |
| 870 | 2026 | 微信小游戏 | 天天过马路 | CC10 | — | R1 | G0 | LT1 | medium |
| 871 | 2026 | 微信小游戏 | 天天酷跑 | CC2 | — | R1 | G1、G2、G3 | LT1、LT2 | high |
| 872 | 2026 | 微信小游戏 | 天涯明月刀 | CC8 | CC4 | R1、R5 | G2、G3、G5 | LT3 | high |
| 873 | 2026 | 微信小游戏 | 天龙八部手游 | CC9 | CC4 | R2、R5 | G1、G3、G5 | LT3 | high |
| 874 | 2026 | 微信小游戏 | 太吾绘卷 | CC6 | — | R3 | G2、G4 | LT3 | high |
| 875 | 2026 | 微信小游戏 | 奇迹暖暖 | CC8 | CC4 | R4、R5 | G3、G5 | LT2、LT3 | high |
| 876 | 2026 | 微信小游戏 | 奥拉星 | CC8 | CC4 | R2、R5 | G1、G3、G5 | LT3 | high |
| 877 | 2026 | 微信小游戏 | 奥比岛：梦想国度 | CC8 | CC4 | R5 | G3、G5 | LT4 | high |
| 878 | 2026 | 微信小游戏 | 奥特曼系列 | CC2 | CC4 | R1 | G1、G2、G3 | LT1、LT3 | high |
| 879 | 2026 | 微信小游戏 | 女皇陛下 | CC8 | CC4 | R2、R5 | G3、G5 | LT3 | high |
| 880 | 2026 | 微信小游戏 | 孙美琪疑案 | CC6 | — | R4 | G4 | LT1 | high |
| 881 | 2026 | 微信小游戏 | 宫廷计 | CC8 | CC4、CC7 | R5、R4 | G5、G3 | LT3、LT2 | high |
| 882 | 2026 | 微信小游戏 | 宾果消消消 | CC10 | — | R4 | G0 | LT1 | high |
| 883 | 2026 | 微信小游戏 | 对对碰 | CC10 | — | R4 | G0 | LT1 | high |
| 884 | 2026 | 微信小游戏 | 寻道大千 | CC3 | CC4 | R2 | G1 | LT4、LT2 | high |
| 885 | 2026 | 微信小游戏 | 射雕 | CC2 | CC4、CC8 | R1、R5 | G2、G3 | LT3 | medium |
| 886 | 2026 | 微信小游戏 | 小小蚁国 | CC5 | CC9 | R3 | G2、G3 | LT3 | medium |
| 887 | 2026 | 微信小游戏 | 小黄人快跑 | CC10 | CC4 | R1、R4 | G0、G3 | LT1、LT2 | medium |
| 888 | 2026 | 微信小游戏 | 巨兽战场 | CC9 | CC4、CC5 | R3、R2 | G3、G2 | LT3 | medium |
| 889 | 2026 | 微信小游戏 | 幻之封神 | CC3 | CC4、CC8 | R2 | G1、G3 | LT4、LT2 | high |
| 890 | 2026 | 微信小游戏 | 开心农场 | CC5 | CC9、CC4 | R3、R2 | G3、G5 | LT3、LT2 | medium |
| 891 | 2026 | 微信小游戏 | 开心消消乐 | CC10 | — | R4 | G0、G2 | LT1、LT2 | high |
| 892 | 2026 | 微信小游戏 | 弹壳特攻队 | CC10 | CC3 | R1、R3 | G2、G1 | LT1、LT2 | medium |
| 893 | 2026 | 微信小游戏 | 征途 | CC1 | CC9、CC3 | R1、R2 | G1、G3 | LT3 | high |
| 894 | 2026 | 微信小游戏 | 御龙在天 | CC1 | CC9、CC3 | R1、R2 | G1、G3 | LT3 | high |
| 895 | 2026 | 微信小游戏 | 忍者必须死3 | CC2 | CC1 | R1 | G2 | LT1、LT2 | medium |
| 896 | 2026 | 微信小游戏 | 恋与制作人 | CC8 | CC4 | R5 | G5、G3 | LT3、LT2 | high |
| 897 | 2026 | 微信小游戏 | 恐怖奶奶 | CC2 | CC6 | R1、R4 | G2、G4 | LT1 | medium |
| 898 | 2026 | 微信小游戏 | 愤怒的小鸟2 | CC2 | CC6 | R1、R4 | G2、G4 | LT1 | medium |
| 899 | 2026 | 微信小游戏 | 我的世界 | CC5 | CC7、CC4 | R3 | G2、G3 | LT4 | high |
| 900 | 2026 | 微信小游戏 | 我的安吉拉 | CC8 | CC4、CC7 | R5、R2 | G5、G3 | LT4、LT2 | high |
| 901 | 2026 | 微信小游戏 | 我的汤姆猫 | CC8 | CC4 | R2、R5 | G5 | LT4 | high |
| 902 | 2026 | 微信小游戏 | 我飞刀玩得贼6 | CC1 | — | R1 | G0、G2 | LT1 | high |
| 903 | 2026 | 微信小游戏 | 战火与永恒 | CC9 | CC5 | R3、R1 | G3、G2 | LT3 | high |
| 904 | 2026 | 微信小游戏 | 战魂铭人 | CC2 | — | R1 | G2、G3 | LT1、LT2 | high |
| 905 | 2026 | 微信小游戏 | 打地鼠 | CC10 | — | R1 | G0 | LT1 | high |
| 906 | 2026 | 微信小游戏 | 找你妹 | CC6 | — | R4 | G0、G4 | LT1 | high |
| 907 | 2026 | 微信小游戏 | 找茬 | CC6 | — | R4 | G0、G4 | LT1 | high |
| 908 | 2026 | 微信小游戏 | 抓大鹅 | CC10 | CC4 | R4 | G0 | LT1 | medium |
| 909 | 2026 | 微信小游戏 | 捕鱼大作战 | CC1 | CC3 | R1、R2 | G1、G3 | LT1、LT2 | medium |
| 910 | 2026 | 微信小游戏 | 掌门下山 | CC3 | CC5 | R2 | G1、G3 | LT4 | high |
| 911 | 2026 | 微信小游戏 | 搬砖模拟器 | CC10 | — | R2、R5 | G1 | LT4 | high |
| 912 | 2026 | 微信小游戏 | 摩尔庄园 | CC8 | CC5、CC9 | R5、R3 | G5、G3 | LT4 | medium |
| 913 | 2026 | 微信小游戏 | 文字修仙 | CC3 | — | R2 | G1 | LT4 | high |
| 914 | 2026 | 微信小游戏 | 文字玩出花 | CC6 | — | R4 | G0、G4 | LT1 | high |
| 915 | 2026 | 微信小游戏 | 文明与征服 | CC9 | CC5 | R3、R1 | G3、G2 | LT3 | high |
| 916 | 2026 | 微信小游戏 | 斗破苍穹：斗帝之路 | CC3 | CC4、CC8 | R2、R1 | G1、G3 | LT3 | high |
| 917 | 2026 | 微信小游戏 | 斗罗大陆：魂师对决 | CC3 | CC4、CC6 | R2、R1 | G1、G2 | LT3 | high |
| 918 | 2026 | 微信小游戏 | 旅者之憩 | CC5 | — | R3 | G2、G3 | LT3 | high |
| 919 | 2026 | 微信小游戏 | 旅行青蛙 | CC8 | CC4 | R5 | G5 | LT4 | high |
| 920 | 2026 | 微信小游戏 | 无尽的拉格朗日 | CC9 | CC5 | R3、R1 | G3、G2 | LT3 | high |
| 921 | 2026 | 微信小游戏 | 明日之后 | CC9 | CC4 | R1、R3 | G3、G5 | LT3 | high |
| 922 | 2026 | 微信小游戏 | 暗黑修仙 | CC3 | CC4 | R2 | G1、G3 | LT2 | high |
| 923 | 2026 | 微信小游戏 | 曙光英雄 | CC1 | — | R1 | G2 | LT1 | high |
| 924 | 2026 | 微信小游戏 | 机械迷城 | CC6 | — | R4 | G4 | LT1 | high |
| 925 | 2026 | 微信小游戏 | 梦幻家园 | CC10 | CC4 | R4、R5 | G3、G5 | LT2 | medium |
| 926 | 2026 | 微信小游戏 | 梦幻花园 | CC10 | CC4 | R4、R5 | G3、G5 | LT2 | medium |
| 927 | 2026 | 微信小游戏 | 梦幻西游 | CC9 | CC4 | R2、R3 | G1、G3、G5 | LT3 | high |
| 928 | 2026 | 微信小游戏 | 梦想小镇 | CC5 | CC4 | R3 | G3 | LT3 | high |
| 929 | 2026 | 微信小游戏 | 植物大战僵尸2 | CC2 | CC4 | R1、R4 | G2、G3 | LT1、LT2 | high |
| 930 | 2026 | 微信小游戏 | 模拟城市：我是市长 | CC5 | CC4 | R3 | G3 | LT3 | high |
| 931 | 2026 | 微信小游戏 | 次神光之觉醒 | CC3 | CC4 | R2 | G1 | LT2 | high |
| 932 | 2026 | 微信小游戏 | 欢乐五子棋 | CC1 | — | R4 | G2、G4 | LT1 | high |
| 933 | 2026 | 微信小游戏 | 欢乐农场 | CC5 | CC4 | R3 | G3 | LT3 | high |
| 934 | 2026 | 微信小游戏 | 欢乐斗地主 | CC1 | — | R4 | G2、G4 | LT1 | high |
| 935 | 2026 | 微信小游戏 | 欢乐消消消 | CC10 | — | R4 | G0 | LT1 | high |
| 936 | 2026 | 微信小游戏 | 欢乐麻将 | CC1 | — | R4 | G2、G4 | LT1 | high |
| 937 | 2026 | 微信小游戏 | 水果忍者 | CC10 | — | R1 | G2 | LT1 | high |
| 938 | 2026 | 微信小游戏 | 汉字找茬王 | CC6 | — | R4 | G4 | LT1 | high |
| 939 | 2026 | 微信小游戏 | 江南百景图 | CC5 | CC4 | R3、R5 | G3 | LT3 | high |
| 940 | 2026 | 微信小游戏 | 汤姆猫跑酷 | CC10 | CC4 | R1 | G3 | LT1、LT2 | medium |
| 941 | 2026 | 微信小游戏 | 泡泡龙 | CC2 | — | R4 | G2 | LT1 | high |
| 942 | 2026 | 微信小游戏 | 泰拉瑞亚 | CC5 | CC4 | R3 | G2、G3 | LT3 | high |
| 943 | 2026 | 微信小游戏 | 洛克王国世界 | CC8 | CC4 | R2 | G1、G5 | LT3 | high |
| 944 | 2026 | 微信小游戏 | 洪荒文明 | CC9 | CC5 | R3 | G2、G3 | LT3 | medium |
| 945 | 2026 | 微信小游戏 | 流言侦探 | CC6 | — | R4 | G4 | LT1 | high |
| 946 | 2026 | 微信小游戏 | 海绵宝宝：蟹堡王 | CC5 | CC4 | R3 | G2、G3 | LT3 | high |
| 947 | 2026 | 微信小游戏 | 涂鸦上帝 | CC6 | — | R3 | G4 | LT1 | high |
| 948 | 2026 | 微信小游戏 | 消灭星星 | CC2 | — | R4 | G2 | LT1 | high |
| 949 | 2026 | 微信小游戏 | 深海水族馆 | CC10 | CC4 | R2 | G1 | LT4 | high |
| 950 | 2026 | 微信小游戏 | 游戏王：决斗链接 | CC1 | CC4、CC6 | R3 | G2、G4 | LT1、LT3 | high |
| 951 | 2026 | 微信小游戏 | 滚动的天空 | CC2 | — | R1 | G2 | LT1 | high |
| 952 | 2026 | 微信小游戏 | 热血传奇 | CC1 | CC3、CC9 | R1、R2 | G1、G3 | LT3 | high |
| 953 | 2026 | 微信小游戏 | 熊出没之熊大快跑 | CC2 | — | R1 | G2 | LT1 | high |
| 954 | 2026 | 微信小游戏 | 爆炒江湖 | CC5 | CC4 | R3 | G2、G3 | LT3 | high |
| 955 | 2026 | 微信小游戏 | 狼人杀 | CC1 | CC6 | R4 | G4 | LT1 | high |
| 956 | 2026 | 微信小游戏 | 猎梦宿舍 | CC5 | CC2 | R3 | G2、G3 | LT2 | medium |
| 957 | 2026 | 微信小游戏 | 猫和老鼠 | CC1 | — | R1 | G2 | LT1 | high |
| 958 | 2026 | 微信小游戏 | 王牌战士 | CC1 | — | R1 | G2 | LT1、LT3 | high |
| 959 | 2026 | 微信小游戏 | 球球大作战 | CC1 | — | R1 | G2 | LT1 | high |
| 960 | 2026 | 微信小游戏 | 画境长恨歌 | CC6 | — | R4 | G4 | LT1 | high |
| 961 | 2026 | 微信小游戏 | 画火柴人 | CC6 | — | R4 | G4 | LT1 | high |
| 962 | 2026 | 微信小游戏 | 疯狂骑士团 | CC3 | CC4 | R2 | G1、G3 | LT2、LT3 | high |
| 963 | 2026 | 微信小游戏 | 看谁能通关 | CC6 | CC7 | R4 | G4 | LT1 | high |
| 964 | 2026 | 微信小游戏 | 祖玛 | CC2 | — | R1、R4 | G2 | LT1 | high |
| 965 | 2026 | 微信小游戏 | 神之折纸 | CC6 | — | R4 | G4 | LT1 | high |
| 966 | 2026 | 微信小游戏 | 神庙逃亡 | CC2 | — | R1 | G2 | LT1 | high |
| 967 | 2026 | 微信小游戏 | 神武4 | CC9 | CC8、CC4 | R2、R5 | G1、G5 | LT3 | high |
| 968 | 2026 | 微信小游戏 | 神雕侠侣2 | CC8 | CC9、CC4 | R2、R5 | G1、G5 | LT3 | high |
| 969 | 2026 | 微信小游戏 | 穿越火线：枪战王者 | CC1 | — | R1 | G2、G3 | LT1、LT3 | high |
| 970 | 2026 | 微信小游戏 | 笑傲江湖 | CC8 | CC2、CC4 | R2、R5 | G1、G5 | LT3 | high |
| 971 | 2026 | 微信小游戏 | 第五人格 | CC1 | CC6 | R1 | G2、G4 | LT1、LT3 | high |
| 972 | 2026 | 微信小游戏 | 第五件遗留物 | CC8 | CC6 | R5 | G4 | LT1 | high |
| 973 | 2026 | 微信小游戏 | 红月战神 | CC3 | CC4 | R2 | G1、G3 | LT3 | high |
| 974 | 2026 | 微信小游戏 | 纪念碑谷2 | CC6 | CC7 | R4、R5 | G4 | LT1 | high |
| 975 | 2026 | 微信小游戏 | 纸人 | CC2 | CC6 | R4、R5 | G4 | LT1 | high |
| 976 | 2026 | 微信小游戏 | 纸嫁衣 | CC6 | CC2 | R4、R5 | G4 | LT1 | high |
| 977 | 2026 | 微信小游戏 | 终结战场 | CC1 | — | R1 | G2、G3 | LT1、LT3 | high |
| 978 | 2026 | 微信小游戏 | 缤纷彩带 | CC6 | — | R4 | G4 | LT1 | high |
| 979 | 2026 | 微信小游戏 | 羊了个羊 | CC6 | CC7 | R4 | G4 | LT1 | high |
| 980 | 2026 | 微信小游戏 | 脑洞大师 | CC6 | CC7 | R4 | G4 | LT1 | high |
| 981 | 2026 | 微信小游戏 | 脑点子 | CC6 | — | R4 | G4 | LT1 | high |
| 982 | 2026 | 微信小游戏 | 英雄杀 | CC1 | CC9 | R4 | G4 | LT1 | medium |
| 983 | 2026 | 微信小游戏 | 荒野乱斗 | CC1 | — | R1 | G2、G3 | LT1、LT3 | high |
| 984 | 2026 | 微信小游戏 | 荒野行动 | CC1 | CC4 | R1 | G2、G3 | LT1 | high |
| 985 | 2026 | 微信小游戏 | 谁是卧底 | CC1 | CC9 | R4 | G4 | LT1 | medium |
| 986 | 2026 | 微信小游戏 | 象棋 | CC1 | — | R4 | G2、G4 | LT1 | high |
| 987 | 2026 | 微信小游戏 | 赛尔号 | CC8 | CC2、CC4 | R2 | G1、G3、G5 | LT3 | medium |
| 988 | 2026 | 微信小游戏 | 跳一跳 | CC1 | — | R1 | G2 | LT1 | high |
| 989 | 2026 | 微信小游戏 | 跳舞的线 | CC10 | — | R1、R5 | G2 | LT1 | medium |
| 990 | 2026 | 微信小游戏 | 躺平发育 | CC5 | CC2 | R2、R3 | G1、G3 | LT1 | medium |
| 991 | 2026 | 微信小游戏 | 轩辕剑龙舞云山 | CC8 | CC2、CC4 | R2、R5 | G1、G3、G5 | LT3 | medium |
| 992 | 2026 | 微信小游戏 | 这城有良田 | CC5 | CC9 | R2、R3 | G1、G2、G3 | LT3 | high |
| 993 | 2026 | 微信小游戏 | 连连看 | CC10 | — | R4 | G2 | LT1 | medium |
| 994 | 2026 | 微信小游戏 | 迷你世界 | CC5 | CC7、CC9 | R3 | G2、G3 | LT4 | medium |
| 995 | 2026 | 微信小游戏 | 迷失立方体 | CC6 | — | R4 | G4 | LT1 | high |
| 996 | 2026 | 微信小游戏 | 迷雾大陆 | CC2 | CC3、CC4 | R1、R2 | G1、G3 | LT2、LT3 | medium |
| 997 | 2026 | 微信小游戏 | 逆水寒 | CC8 | CC2、CC7 | R1、R5 | G2、G3、G5 | LT3、LT4 | medium |
| 998 | 2026 | 微信小游戏 | 遇见逆水寒 | CC8 | CC4 | R5 | G5 | LT3 | high |
| 999 | 2026 | 微信小游戏 | 道天录 | CC3 | CC5、CC4 | R2、R3 | G1、G2、G3 | LT3 | medium |
| 1000 | 2026 | 微信小游戏 | 金铲铲之战 | CC1 | CC6 | R3、R4 | G2、G4 | LT1 | medium |
| 1001 | 2026 | 微信小游戏 | 闪耀暖暖 | CC7 | CC4、CC8 | R4、R5 | G3、G5 | LT2、LT3 | medium |
| 1002 | 2026 | 微信小游戏 | 问道 | CC3 | CC1、CC4 | R2 | G1、G3 | LT3 | high |
| 1003 | 2026 | 微信小游戏 | 阴阳师：百闻牌 | CC6 | CC1、CC4 | R3、R4 | G2、G4 | LT1、LT2 | high |
| 1004 | 2026 | 微信小游戏 | 隐形守护者 | CC8 | CC6 | R5 | G4 | LT1 | medium |
| 1005 | 2026 | 微信小游戏 | 非人学园 | CC1 | CC10 | R1 | G2 | LT1、LT2 | high |
| 1006 | 2026 | 微信小游戏 | 飞行棋大作战 | CC10 | CC1 | R4 | G0 | LT1 | medium |
| 1007 | 2026 | 微信小游戏 | 饥荒：新家园 | CC5 | CC2、CC4 | R3 | G2、G3 | LT3 | high |
| 1008 | 2026 | 微信小游戏 | 香肠派对 | CC1 | CC10 | R1 | G2、G3 | LT1、LT2 | high |
| 1009 | 2026 | 微信小游戏 | 鬼谷八荒 | CC3 | CC2、CC4 | R2、R3 | G1、G2 | LT3 | medium |
| 1010 | 2026 | 微信小游戏 | 鳄鱼小顽皮爱洗澡 | CC6 | — | R4 | G4 | LT1 | high |
| 1011 | 2026 | 微信小游戏 | 鹿鼎记 | CC8 | CC3 | R5 | G5、G1 | LT3 | medium |
| 1012 | 2026 | 微信小游戏 | 黄金矿工 | CC10 | CC3 | R2、R4 | G1 | LT1 | medium |
| 1013 | 2026 | 微信小游戏 | 黎明觉醒：生机 | CC5 | CC2、CC4 | R3 | G2、G3 | LT3 | high |
| 1014 | 2025 | 微信小游戏 | NBA 2K Online 2 | CC1 | CC4 | R1 | G2、G3 | LT1、LT3 | high |
| 1015 | 2025 | 微信小游戏 | 三国：谋定天下 | CC9 | CC5、CC1 | R3 | G2、G3 | LT3 | high |
| 1016 | 2025 | 微信小游戏 | 以闪亮之名 | CC7 | CC4、CC8 | R4、R5 | G3、G5 | LT2、LT3 | medium |
| 1017 | 2025 | 微信小游戏 | 元梦之星 | CC10 | CC1 | R1、R4 | G0、G3 | LT1 | medium |
| 1018 | 2025 | 微信小游戏 | 光与夜之恋 | CC8 | CC4 | R5 | G5 | LT3 | high |
| 1019 | 2025 | 微信小游戏 | 冒险大作战 | CC3 | CC4 | R2 | G1、G3 | LT2、LT3 | high |
| 1020 | 2025 | 微信小游戏 | 冒险岛：枫之传说 | CC2 | CC4、CC8 | R1、R2 | G1、G2、G3 | LT3 | medium |
| 1021 | 2025 | 微信小游戏 | 凡人修仙传：人界篇 | CC3 | CC4 | R2 | G1、G3 | LT2、LT3 | high |
| 1022 | 2025 | 微信小游戏 | 剑与远征 | CC3 | CC4 | R2 | G1、G3 | LT2、LT3 | high |
| 1023 | 2025 | 微信小游戏 | 劲舞团 | CC1 | CC7 | R1 | G2 | LT1 | high |
| 1024 | 2025 | 微信小游戏 | 原神（云游戏） | CC2 | CC4、CC8 | R1、R5 | G2、G3、G5 | LT3、LT4 | high |
| 1025 | 2025 | 微信小游戏 | 向僵尸开炮 | CC3 | CC6 | R1、R2 | G1、G2 | LT1、LT2 | medium |
| 1026 | 2025 | 微信小游戏 | 吞噬星空 | CC2 | CC4 | R1、R2 | G1、G2、G3 | LT2、LT3 | medium |
| 1027 | 2025 | 微信小游戏 | 和平精英（小程序版） | CC1 | — | R1 | G2、G3 | LT1、LT3 | high |
| 1028 | 2025 | 微信小游戏 | 四川麻将 | CC1 | — | R4 | G2、G4 | LT1 | high |
| 1029 | 2025 | 微信小游戏 | 塔瑞斯世界 | CC2 | CC9 | R1 | G2、G3 | LT1、LT3 | medium |
| 1030 | 2025 | 微信小游戏 | 大秦帝国之帝国崛起 | CC5 | CC1、CC9 | R3 | G2、G3、G4 | LT3 | high |
| 1031 | 2025 | 微信小游戏 | 完美世界：诸神之战 | CC2 | CC4 | R1、R2 | G1、G2、G3 | LT2、LT3 | medium |
| 1032 | 2025 | 微信小游戏 | 小鸡舰队 | CC3 | CC6 | R2、R3 | G1、G2 | LT1、LT2 | medium |
| 1033 | 2025 | 微信小游戏 | 幻兽爱合成 | CC5 | CC4 | R3、R4 | G2、G3 | LT2、LT3 | high |
| 1034 | 2025 | 微信小游戏 | 广东麻将 | CC1 | — | R4 | G2、G4 | LT1 | high |
| 1035 | 2025 | 微信小游戏 | 征途2（小程序版） | CC1 | CC9 | R1、R2 | G1、G3 | LT3 | high |
| 1036 | 2025 | 微信小游戏 | 拳皇97（小程序版） | CC1 | — | R1 | G2 | LT1 | high |
| 1037 | 2025 | 微信小游戏 | 挨饿荒野 | CC5 | — | R3、R4 | G2、G3、G4 | LT3、LT4 | high |
| 1038 | 2025 | 微信小游戏 | 斗牛 | CC1 | — | R4 | G2、G4 | LT1 | high |
| 1039 | 2025 | 微信小游戏 | 斗罗大陆：史莱克学院 | CC2 | CC4、CC8 | R1、R2 | G1、G2、G3 | LT2、LT3 | medium |
| 1040 | 2025 | 微信小游戏 | 新笑傲江湖 | CC2 | CC8、CC9 | R1、R5 | G2、G3、G5 | LT2、LT3 | medium |
| 1041 | 2025 | 微信小游戏 | 无尽对决 | CC1 | — | R1 | G2 | LT1、LT3 | high |
| 1042 | 2025 | 微信小游戏 | 明日之后（小程序版） | CC5 | CC4 | R3、R4 | G3、G2 | LT3 | high |
| 1043 | 2025 | 微信小游戏 | 星穹铁道（云游戏） | CC2 | CC4、CC8 | R2、R4 | G2、G3 | LT3 | high |
| 1044 | 2025 | 微信小游戏 | 植物大战僵尸 | CC2 | — | R4 | G2、G3 | LT1、LT2 | high |
| 1045 | 2025 | 微信小游戏 | 欢乐升级 | CC1 | — | R4 | G2 | LT1 | high |
| 1046 | 2025 | 微信小游戏 | 汉家江湖 | CC2 | CC4 | R4 | G2、G3 | LT3 | high |
| 1047 | 2025 | 微信小游戏 | 洪荒自动棋 | CC6 | CC3 | R3、R4 | G2、G4 | LT1、LT2 | medium |
| 1048 | 2025 | 微信小游戏 | 流浪超市 | CC3 | CC4、CC5 | R2、R3 | G1、G3 | LT2、LT3 | high |
| 1049 | 2025 | 微信小游戏 | 海贼王：热血航线 | CC2 | CC4、CC8 | R1、R4 | G2、G3 | LT3 | high |
| 1050 | 2025 | 微信小游戏 | 火影忍者（小程序版） | CC1 | CC4、CC8 | R1 | G2、G3 | LT1、LT3 | high |
| 1051 | 2025 | 微信小游戏 | 猎魂觉醒 | CC2 | CC4、CC9 | R1 | G2、G3 | LT3 | high |
| 1052 | 2025 | 微信小游戏 | 率土之滨 | CC9 | CC5 | R3、R4 | G2、G3 | LT3 | high |
| 1053 | 2025 | 微信小游戏 | 王者荣耀（极速版） | CC1 | — | R1 | G2 | LT1、LT3 | high |
| 1054 | 2025 | 微信小游戏 | 王铲铲的致富之路 | CC5 | CC3 | R4、R2 | G1、G3 | LT2、LT3 | high |
| 1055 | 2025 | 微信小游戏 | 生化危机（小程序版） | CC2 | — | R1、R4 | G2、G3 | LT1、LT2 | high |
| 1056 | 2025 | 微信小游戏 | 白荆回廊 | CC2 | CC4、CC6 | R1、R3 | G2、G3 | LT3 | medium |
| 1057 | 2025 | 微信小游戏 | 盗墓笔记 | CC6 | CC8 | R4 | G4、G2 | LT1、LT2 | high |
| 1058 | 2025 | 微信小游戏 | 穿越火线（小程序版） | CC1 | — | R1 | G2 | LT1、LT3 | high |
| 1059 | 2025 | 微信小游戏 | 第五人格（小程序版） | CC1 | — | R1、R4 | G2 | LT1、LT3 | high |
| 1060 | 2025 | 微信小游戏 | 红月 | CC1 | CC3 | R1 | G1、G2 | LT3 | medium |
| 1061 | 2025 | 微信小游戏 | 蛋仔派对 | CC10 | CC1 | R1 | G0 | LT1 | medium |
| 1062 | 2025 | 微信小游戏 | 街头篮球 | CC1 | — | R1 | G2 | LT1 | high |
| 1063 | 2025 | 微信小游戏 | 街头霸王（小程序版） | CC1 | — | R1 | G2 | LT1 | high |
| 1064 | 2025 | 微信小游戏 | 跑得快 | CC1 | CC6 | R4 | G4 | LT1 | medium |
| 1065 | 2025 | 微信小游戏 | 跑跑卡丁车 | CC1 | — | R1 | G2 | LT1 | high |
| 1066 | 2025 | 微信小游戏 | 逆战：未来 | CC2 | CC1 | R1 | G2、G3 | LT1、LT3 | medium |
| 1067 | 2025 | 微信小游戏 | 鬼吹灯之精绝古城 | CC2 | CC8 | R1、R4 | G2、G3 | LT2 | medium |
| 1068 | 2025 | 微信小游戏 | 魂斗罗：归来 | CC2 | — | R1 | G2、G3 | LT1、LT2 | high |
| 1069 | 2025 | 微信小游戏 | 黑暗笔录 | CC6 | CC8 | R4 | G4 | LT1 | high |
| 1070 | 2024 | 微信小游戏 | 三国吧兄弟 | CC3 | CC2 | R1、R2 | G1、G2 | LT1、LT2 | medium |
| 1071 | 2024 | 微信小游戏 | 仙剑奇侠传之新的开始 | CC8 | CC2、CC4 | R4、R5 | G1、G5 | LT3 | high |
| 1072 | 2024 | 微信小游戏 | 侠客梦 | CC3 | CC2 | R1、R2 | G1、G2 | LT1、LT2 | medium |
| 1073 | 2024 | 微信小游戏 | 保卫向日葵 | CC5 | CC2 | R3、R4 | G2、G4 | LT1、LT2 | medium |
| 1074 | 2024 | 微信小游戏 | 冲一冲专家 | CC10 | — | R1、R4 | G0 | LT1 | high |
| 1075 | 2024 | 微信小游戏 | 出发吧麦芬 | CC3 | CC4、CC9 | R2 | G1、G3 | LT3 | medium |
| 1076 | 2024 | 微信小游戏 | 叫我大掌柜 | CC5 | CC4 | R3、R2 | G1、G3 | LT3 | high |
| 1077 | 2024 | 微信小游戏 | 地下城与领主 | CC2 | CC3、CC4 | R1、R2 | G1、G3 | LT2、LT3 | medium |
| 1078 | 2024 | 微信小游戏 | 墨斗 | CC1 | — | R1 | G2 | LT1 | high |
| 1079 | 2024 | 微信小游戏 | 大侠立志传 | CC5 | CC2、CC4 | R3、R4 | G2、G4 | LT3 | medium |
| 1080 | 2024 | 微信小游戏 | 寻宝大冒险 | CC10 | CC4 | R2、R4 | G3 | LT1、LT2 | medium |
| 1081 | 2024 | 微信小游戏 | 小鸡舰队出击 | CC2 | CC4 | R1、R3 | G2、G3 | LT1、LT2 | high |
| 1082 | 2024 | 微信小游戏 | 我是大东家 | CC5 | — | R3、R4 | G2、G3 | LT3 | high |
| 1083 | 2024 | 微信小游戏 | 掌门江湖路 | CC3 | CC4 | R2、R4 | G1、G3 | LT2、LT3 | high |
| 1084 | 2024 | 微信小游戏 | 整蛊邻居 | CC6 | — | R4 | G4 | LT1 | high |
| 1085 | 2024 | 微信小游戏 | 无尽冬日 | CC9 | CC5 | R3、R4 | G2、G3 | LT3 | high |
| 1086 | 2024 | 微信小游戏 | 星际大作战 | CC3 | CC4 | R1、R2 | G1、G3 | LT2 | high |
| 1087 | 2024 | 微信小游戏 | 暗黑觉醒 | CC2 | — | R1、R3 | G2 | LT1、LT2 | high |
| 1088 | 2024 | 微信小游戏 | 欢乐坦克大战 | CC1 | — | R1 | G2 | LT1 | high |
| 1089 | 2024 | 微信小游戏 | 欢乐钓鱼大师 | CC10 | CC4 | R4、R5 | G3、G4 | LT1、LT2 | medium |
| 1090 | 2024 | 微信小游戏 | 洛克王国 | CC8 | CC4 | R2、R4 | G3、G5 | LT3 | high |
| 1091 | 2024 | 微信小游戏 | 洪荒觉醒 | CC3 | CC4 | R2 | G1 | LT2、LT3 | high |
| 1092 | 2024 | 微信小游戏 | 灌篮高手 | CC1 | — | R1 | G2 | LT1 | high |
| 1093 | 2024 | 微信小游戏 | 灵剑仙师 | CC3 | CC4 | R2 | G1 | LT2、LT3 | high |
| 1094 | 2024 | 微信小游戏 | 灵魂序章 | CC3 | CC4 | R2、R4 | G1、G3 | LT2、LT3 | high |
| 1095 | 2024 | 微信小游戏 | 烧脑瓶子 | CC6 | — | R4 | G4 | LT1 | high |
| 1096 | 2024 | 微信小游戏 | 百炼英雄 | CC2 | CC4 | R1、R3 | G2、G3 | LT1、LT2 | high |
| 1097 | 2024 | 微信小游戏 | 节奏大师 | CC2 | — | R1、R4 | G2 | LT1 | high |
| 1098 | 2024 | 微信小游戏 | 跃动小子 | CC3 | — | R2 | G1 | LT2、LT3 | high |
| 1099 | 2024 | 微信小游戏 | 霓虹深渊：无限 | CC6 | CC2 | R1、R3 | G2、G4 | LT1、LT2 | medium |
| 1100 | 2024 | 微信小游戏 | 飞吧龙骑士 | CC2 | — | R1、R3 | G2、G3 | LT1、LT2 | high |
| 1101 | 2024 | 微信小游戏 | 骑士冲啊 | CC2 | CC6 | R1 | G2 | LT1 | high |
| 1102 | 2024 | 微信小游戏 | 骑行去拉萨 | CC10 | CC4 | R2、R5 | G3 | LT2 | medium |
| 1103 | 2023 | 微信小游戏 | 五子棋 | CC1 | — | R4 | G2 | LT1 | high |
| 1104 | 2023 | 微信小游戏 | 停车大师 | CC2 | — | R4 | G2 | LT1 | high |
| 1105 | 2023 | 微信小游戏 | 全民打螺丝 | CC10 | — | R4 | G0 | LT1 | medium |
| 1106 | 2023 | 微信小游戏 | 六边形消消乐 | CC6 | — | R4 | G4 | LT1 | high |
| 1107 | 2023 | 微信小游戏 | 军棋 | CC1 | — | R4 | G4 | LT1 | high |
| 1108 | 2023 | 微信小游戏 | 割草的哈利 | CC2 | — | R1 | G2 | LT1 | high |
| 1109 | 2023 | 微信小游戏 | 功夫派 | CC2 | CC3 | R1、R2 | G1、G2 | LT2 | medium |
| 1110 | 2023 | 微信小游戏 | 大富翁 | CC1 | CC5 | R3 | G3 | LT1 | medium |
| 1111 | 2023 | 微信小游戏 | 奥比岛 | CC8 | CC4、CC7 | R5 | G5 | LT4 | high |
| 1112 | 2023 | 微信小游戏 | 小森生活 | CC10 | CC5 | R2、R5 | G3 | LT4 | medium |
| 1113 | 2023 | 微信小游戏 | 小花仙 | CC8 | CC4、CC7 | R5 | G5 | LT4 | high |
| 1114 | 2023 | 微信小游戏 | 我飞刀玩得真牛 | CC1 | — | R1 | G2 | LT1 | high |
| 1115 | 2023 | 微信小游戏 | 扫雷 | CC6 | — | R4 | G4 | LT1 | high |
| 1116 | 2023 | 微信小游戏 | 数独 | CC6 | — | R4 | G4 | LT1 | high |
| 1117 | 2023 | 微信小游戏 | 斗兽棋 | CC1 | — | R4 | G4 | LT1 | high |
| 1118 | 2023 | 微信小游戏 | 水排序 | CC6 | — | R4 | G4 | LT1 | high |
| 1119 | 2023 | 微信小游戏 | 物理弹球 | CC10 | — | R1、R3 | G0 | LT1 | medium |
| 1120 | 2023 | 微信小游戏 | 猫旅馆物语 | CC8 | CC4、CC5 | R2、R5 | G3、G5 | LT3 | high |
| 1121 | 2023 | 微信小游戏 | 玩梗找茬王 | CC6 | — | R4 | G4 | LT1 | high |
| 1122 | 2023 | 微信小游戏 | 皇室战争 | CC1 | CC4 | R1、R3 | G2、G3 | LT1、LT3 | high |
| 1123 | 2023 | 微信小游戏 | 纪念碑谷 | CC6 | — | R4 | G4 | LT1 | high |
| 1124 | 2023 | 微信小游戏 | 见缝插针 | CC2 | — | R1 | G2 | LT1 | medium |
| 1125 | 2023 | 微信小游戏 | 野兽领主：新世界 | CC5 | CC9 | R3 | G2、G3 | LT3 | medium |
| 1126 | 2023 | 微信小游戏 | 钢琴块 | CC2 | — | R1 | G2 | LT1 | high |
| 1127 | 2023 | 微信小游戏 | 飞行棋 | CC10 | CC1 | R4 | G0 | LT1 | medium |
| 1128 | 2022 | 微信小游戏 | 乌冬的旅店 | CC5 | CC10、CC4 | R3、R5 | G3、G2 | LT3 | high |
| 1129 | 2022 | 微信小游戏 | 全民枪神 | CC1 | — | R1 | G2、G3 | LT1、LT3 | high |
| 1130 | 2022 | 微信小游戏 | 剧本杀 | CC6 | CC8 | R5、R4 | G4 | LT1 | high |
| 1131 | 2022 | 微信小游戏 | 动物快跑 | CC2 | CC10 | R1 | G2 | LT1 | medium |
| 1132 | 2022 | 微信小游戏 | 原神 | CC2 | CC8、CC4 | R1、R5 | G2、G3、G5 | LT3、LT4 | high |
| 1133 | 2022 | 微信小游戏 | 召唤神龙 | CC3 | CC4 | R2 | G1 | LT1 | high |
| 1134 | 2022 | 微信小游戏 | 可口的披萨 | CC5 | CC2 | R4、R3 | G2、G3 | LT3 | high |
| 1135 | 2022 | 微信小游戏 | 和平精英 | CC1 | CC4 | R1 | G2、G3 | LT1、LT3 | high |
| 1136 | 2022 | 微信小游戏 | 天天象棋 | CC1 | CC6 | R4 | G2、G4 | LT1 | high |
| 1137 | 2022 | 微信小游戏 | 天天足球 | CC1 | CC10 | R1 | G2 | LT1 | medium |
| 1138 | 2022 | 微信小游戏 | 弹弹堂 | CC1 | CC4 | R1 | G2、G3 | LT1、LT3 | high |
| 1139 | 2022 | 微信小游戏 | 悦动音符 | CC2 | CC10 | R1 | G2 | LT1 | medium |
| 1140 | 2022 | 微信小游戏 | 愤怒的小鸟 | CC6 | CC2 | R4 | G4、G2 | LT1 | high |
| 1141 | 2022 | 微信小游戏 | 房东模拟器 | CC5 | — | R3、R4 | G3、G2 | LT3 | high |
| 1142 | 2022 | 微信小游戏 | 拳皇97 | CC1 | — | R1 | G2 | LT1 | high |
| 1143 | 2022 | 微信小游戏 | 摸鱼大作战 | CC10 | — | R1、R4 | G0 | LT1 | high |
| 1144 | 2022 | 微信小游戏 | 放置奇兵 | CC3 | CC4 | R2 | G1、G3 | LT3 | high |
| 1145 | 2022 | 微信小游戏 | 文字大冒险 | CC6 | — | R4、R5 | G4 | LT1 | medium |
| 1146 | 2022 | 微信小游戏 | 文字大玩家 | CC5 | — | R2、R4 | G1、G3 | LT3 | high |
| 1147 | 2022 | 微信小游戏 | 文字梗传 | CC6 | — | R4 | G4 | LT1 | high |
| 1148 | 2022 | 微信小游戏 | 文字生存者 | CC5 | — | R3、R4 | G2、G4 | LT3 | medium |
| 1149 | 2022 | 微信小游戏 | 斗罗大陆 | CC3 | CC4 | R2 | G1、G3 | LT3 | high |
| 1150 | 2022 | 微信小游戏 | 星途 | CC10 | — | R1、R4 | G0 | LT1 | high |
| 1151 | 2022 | 微信小游戏 | 暗区突围 | CC1 | CC4 | R1 | G3、G2 | LT1、LT3 | high |
| 1152 | 2022 | 微信小游戏 | 最强蜗牛 | CC3 | CC4 | R2、R5 | G1、G3 | LT3 | high |
| 1153 | 2022 | 微信小游戏 | 枪火重生 | CC2 | CC4 | R1、R3 | G2、G3 | LT1、LT2 | high |
| 1154 | 2022 | 微信小游戏 | 梦想城镇 | CC5 | — | R3、R4 | G3、G2 | LT3 | high |
| 1155 | 2022 | 微信小游戏 | 模拟城市 | CC5 | — | R3、R4 | G2、G3 | LT3 | high |
| 1156 | 2022 | 微信小游戏 | 欢乐六边形 | CC6 | — | R4 | G4、G2 | LT1 | high |
| 1157 | 2022 | 微信小游戏 | 流浪方舟 | CC6 | CC4 | R3、R1 | G4、G2 | LT1、LT2 | medium |
| 1158 | 2022 | 微信小游戏 | 海岛奇兵 | CC1 | CC9 | R1、R3 | G2、G3 | LT3 | high |
| 1159 | 2022 | 微信小游戏 | 消消乐 | CC10 | — | R4 | G0 | LT1 | high |
| 1160 | 2022 | 微信小游戏 | 深海水怪 | CC3 | — | R1、R2 | G1 | LT1、LT2 | high |
| 1161 | 2022 | 微信小游戏 | 火影忍者 | CC1 | CC4 | R1 | G2、G3 | LT1、LT3 | high |
| 1162 | 2022 | 微信小游戏 | 王者荣耀 | CC1 | — | R1 | G2、G3 | LT1、LT3 | high |
| 1163 | 2022 | 微信小游戏 | 穿越 | CC1 | — | R1 | G2、G3 | LT1、LT3 | high |
| 1164 | 2022 | 微信小游戏 | 篮球大师 | CC5 | CC4 | R3、R2 | G3、G2 | LT3 | medium |
| 1165 | 2022 | 微信小游戏 | 纸嫁衣2奘铃村 | CC6 | — | R4 | G4 | LT1 | high |
| 1166 | 2022 | 微信小游戏 | 英雄联盟手游 | CC1 | — | R1 | G2、G3 | LT1、LT3 | high |
| 1167 | 2022 | 微信小游戏 | 贪吃蛇大作战 | CC1 | — | R1 | G2 | LT1 | medium |
| 1168 | 2022 | 微信小游戏 | 车库倒车入库 | CC6 | — | R4 | G2 | LT1 | high |
| 1169 | 2022 | 微信小游戏 | 这就是江湖 | CC3 | CC4 | R2 | G1、G4 | LT3 | medium |
| 1170 | 2022 | 微信小游戏 | 部落冲突 | CC5 | CC9 | R3、R2 | G3、G2 | LT3 | medium |
| 1171 | 2022 | 微信小游戏 | 魂斗罗 | CC2 | — | R1 | G2 | LT1 | high |
| 1172 | 2022 | 微信小游戏 | 麻将来了 | CC1 | — | R4 | G2、G4 | LT1 | medium |
| 1173 | 2021 | 微信小游戏 | QQ农场 | CC5 | CC4、CC9 | R2、R3 | G3 | LT3 | medium |
| 1174 | 2021 | 微信小游戏 | 三国志幻想大陆 | CC3 | CC4、CC8 | R2 | G1、G3 | LT3 | medium |
| 1175 | 2021 | 微信小游戏 | 九天封神 | CC3 | CC4 | R2 | G1、G3 | LT3 | high |
| 1176 | 2021 | 微信小游戏 | 仙剑奇侠传 | CC2 | CC4、CC8 | R4、R5 | G2、G3 | LT3 | medium |
| 1177 | 2021 | 微信小游戏 | 传奇世界 | CC3 | CC1、CC9 | R2、R1 | G1、G3 | LT3 | medium |
| 1178 | 2021 | 微信小游戏 | 传奇霸业 | CC3 | CC1 | R2 | G1、G3 | LT3 | high |
| 1179 | 2021 | 微信小游戏 | 俄罗斯方块 | CC6 | — | R4 | G2 | LT1 | high |
| 1180 | 2021 | 微信小游戏 | 修仙掌门人 | CC5 | CC3、CC4 | R3、R2 | G3、G1 | LT3 | medium |
| 1181 | 2021 | 微信小游戏 | 全民枪战 | CC1 | — | R1 | G2 | LT1、LT3 | high |
| 1182 | 2021 | 微信小游戏 | 凡人修仙 | CC3 | CC4 | R2 | G1、G3 | LT2、LT3 | high |
| 1183 | 2021 | 微信小游戏 | 原始传奇 | CC3 | CC4 | R2 | G1、G3 | LT2、LT3 | high |
| 1184 | 2021 | 微信小游戏 | 大天使之剑 | CC3 | CC4 | R2 | G1、G3 | LT2、LT3 | high |
| 1185 | 2021 | 微信小游戏 | 天天狼人 | CC6 | CC9 | R4 | G4 | LT1 | medium |
| 1186 | 2021 | 微信小游戏 | 妄想山海 | CC5 | CC4、CC8 | R3 | G2、G3 | LT3、LT4 | medium |
| 1187 | 2021 | 微信小游戏 | 完美世界 | CC3 | CC4 | R2 | G1、G3 | LT2、LT3 | high |
| 1188 | 2021 | 微信小游戏 | 宾果消消乐 | CC10 | — | R4 | G0 | LT1 | high |
| 1189 | 2021 | 微信小游戏 | 密室逃脱 | CC6 | — | R4 | G4 | LT1 | high |
| 1190 | 2021 | 微信小游戏 | 弹球达人 | CC10 | — | R4 | G0 | LT1 | high |
| 1191 | 2021 | 微信小游戏 | 御剑情缘 | CC3 | CC8 | R2 | G1、G5 | LT2、LT3 | medium |
| 1192 | 2021 | 微信小游戏 | 想不想修真 | CC3 | — | R2 | G1 | LT2、LT3 | high |
| 1193 | 2021 | 微信小游戏 | 我功夫特牛 | CC2 | CC6 | R1、R3 | G2 | LT1、LT2 | medium |
| 1194 | 2021 | 微信小游戏 | 拼三张 | CC1 | — | R4 | G0 | LT1 | high |
| 1195 | 2021 | 微信小游戏 | 捕鱼达人 | CC10 | CC3 | R1、R2 | G1、G3 | LT1、LT2 | medium |
| 1196 | 2021 | 微信小游戏 | 放置江湖 | CC3 | CC4 | R2 | G1、G3 | LT2、LT3 | high |
| 1197 | 2021 | 微信小游戏 | 文字三国 | CC5 | — | R3 | G2、G3 | LT3 | high |
| 1198 | 2021 | 微信小游戏 | 斗破苍穹 | CC3 | CC4 | R2 | G1、G3 | LT2、LT3 | high |
| 1199 | 2021 | 微信小游戏 | 昭和杂货店物语 | CC8 | CC4、CC10 | R5 | G5、G3 | LT2、LT4 | high |
| 1200 | 2021 | 微信小游戏 | 校花模拟器 | CC8 | CC3 | R5、R2 | G5、G1 | LT2、LT3 | high |
| 1201 | 2021 | 微信小游戏 | 泡泡精灵 | CC10 | — | R4 | G0 | LT1 | high |
| 1202 | 2021 | 微信小游戏 | 消星星 | CC10 | — | R4 | G0 | LT1 | high |
| 1203 | 2021 | 微信小游戏 | 消灭病毒 | CC3 | — | R1、R2 | G1 | LT2 | high |
| 1204 | 2021 | 微信小游戏 | 火拼连连看 | CC10 | — | R4 | G0 | LT1 | high |
| 1205 | 2021 | 微信小游戏 | 炸金花 | CC1 | — | R4 | G0 | LT1 | high |
| 1206 | 2021 | 微信小游戏 | 猫咪公寓 | CC8 | CC4 | R5 | G5 | LT3 | high |
| 1207 | 2021 | 微信小游戏 | 画线救救火柴人 | CC6 | — | R4 | G4 | LT1 | high |
| 1208 | 2021 | 微信小游戏 | 疯狂猜成语 | CC6 | — | R4 | G4 | LT1 | high |
| 1209 | 2021 | 微信小游戏 | 疯狂猜歌 | CC6 | — | R4 | G4 | LT1 | high |
| 1210 | 2021 | 微信小游戏 | 神手 | CC10 | — | R1 | G2 | LT1 | medium |
| 1211 | 2021 | 微信小游戏 | 神脑洞 | CC6 | — | R4 | G4 | LT1 | high |
| 1212 | 2021 | 微信小游戏 | 穿越火线 | CC1 | — | R1 | G2、G3 | LT1、LT3 | high |
| 1213 | 2021 | 微信小游戏 | 网吧模拟器 | CC5 | — | R3 | G3 | LT3 | high |
| 1214 | 2021 | 微信小游戏 | 脑力大乱斗 | CC6 | — | R4 | G4 | LT1 | high |
| 1215 | 2021 | 微信小游戏 | 腾讯桌球 | CC1 | — | R1 | G2 | LT1 | high |
| 1216 | 2021 | 微信小游戏 | 英魂之刃 | CC1 | — | R1 | G2、G3 | LT1、LT3 | high |
| 1217 | 2021 | 微信小游戏 | 荣耀大天使 | CC3 | CC4 | R2 | G1、G3 | LT3 | high |
| 1218 | 2021 | 微信小游戏 | 蓝月传奇 | CC3 | — | R2 | G1、G3 | LT3 | high |
| 1219 | 2021 | 微信小游戏 | 诛仙 | CC3 | CC4 | R2 | G1、G3 | LT3 | high |
| 1220 | 2021 | 微信小游戏 | 逃离公司 | CC6 | — | R4 | G4 | LT1 | high |
| 1221 | 2021 | 微信小游戏 | 钢琴块2 | CC2 | — | R1 | G2 | LT1 | high |
| 1222 | 2021 | 微信小游戏 | 锄大地 | CC1 | CC6 | R4 | G4 | LT1 | medium |
| 1223 | 2021 | 微信小游戏 | 隐藏的我的游戏母亲 | CC6 | — | R4 | G4 | LT1 | high |
| 1224 | 2020 | 微信小游戏 | 人群冲撞 | CC1 | CC3 | R2 | G1 | LT1 | medium |
| 1225 | 2020 | 微信小游戏 | 切切切 | CC10 | — | R1 | G0 | LT1 | high |
| 1226 | 2020 | 微信小游戏 | 列王的纷争 | CC9 | CC5 | R3 | G3、G1 | LT3 | high |
| 1227 | 2020 | 微信小游戏 | 合并庄园 | CC5 | CC4、CC8 | R3 | G3 | LT3 | medium |
| 1228 | 2020 | 微信小游戏 | 合并龙 | CC5 | CC4 | R3 | G3 | LT3 | high |
| 1229 | 2020 | 微信小游戏 | 堆栈球 | CC10 | — | R1 | G0 | LT1 | high |
| 1230 | 2020 | 微信小游戏 | 帝国与谜题 | CC2 | CC6、CC3 | R4 | G3、G2 | LT3 | medium |
| 1231 | 2020 | 微信小游戏 | 快乐玻璃杯 | CC6 | — | R4 | G4 | LT1 | high |
| 1232 | 2020 | 微信小游戏 | 恋爱球球 | CC6 | CC8 | R4 | G4 | LT1 | medium |
| 1233 | 2020 | 微信小游戏 | 成语消消消 | CC6 | — | R4 | G4 | LT1 | high |
| 1234 | 2020 | 微信小游戏 | 手机壳DIY | CC7 | CC10 | R5 | G0 | LT1 | medium |
| 1235 | 2020 | 微信小游戏 | 扎染大师 | CC7 | CC10 | R5 | G0 | LT1 | medium |
| 1236 | 2020 | 微信小游戏 | 托尼老师 | CC10 | CC7 | R5 | G0 | LT1 | medium |
| 1237 | 2020 | 微信小游戏 | 拥挤城市 | CC1 | CC3 | R2 | G1 | LT1 | high |
| 1238 | 2020 | 微信小游戏 | 攻城掠地 | CC9 | CC5 | R3 | G3、G1 | LT3 | high |
| 1239 | 2020 | 微信小游戏 | 救援大师 | CC6 | — | R4 | G4 | LT1 | high |
| 1240 | 2020 | 微信小游戏 | 文字拼图 | CC6 | — | R4 | G4 | LT1 | high |
| 1241 | 2020 | 微信小游戏 | 斑点巨人 | CC3 | CC10 | R2 | G1 | LT1 | medium |
| 1242 | 2020 | 微信小游戏 | 最强的大脑 | CC6 | CC7 | R4 | G4 | LT1 | high |
| 1243 | 2020 | 微信小游戏 | 权力的游戏 | CC5 | CC9 | R3 | G2、G3 | LT3 | medium |
| 1244 | 2020 | 微信小游戏 | 桥上跑 | CC2 | CC4 | R1、R4 | G2 | LT1 | medium |
| 1245 | 2020 | 微信小游戏 | 欢乐球球 | CC10 | — | R1 | G0 | LT1 | medium |
| 1246 | 2020 | 微信小游戏 | 泡泡 | CC10 | — | R1、R5 | G0 | LT1 | high |
| 1247 | 2020 | 微信小游戏 | 热血合击 | CC3 | CC1、CC4 | R1、R2 | G1、G3 | LT3 | high |
| 1248 | 2020 | 微信小游戏 | 班主任模拟器 | CC6 | CC8 | R4 | G4 | LT1 | high |
| 1249 | 2020 | 微信小游戏 | 美甲 | CC10 | CC7 | R5 | G0 | LT1 | medium |
| 1250 | 2020 | 微信小游戏 | 胖子变瘦子 | CC3 | CC10 | R2 | G1 | LT1 | medium |
| 1251 | 2020 | 微信小游戏 | 脑力测试 | CC6 | CC7 | R4 | G4 | LT1 | high |
| 1252 | 2020 | 微信小游戏 | 脑洞找茬 | CC6 | CC8 | R4 | G4 | LT1 | high |
| 1253 | 2020 | 微信小游戏 | 螺旋跳跃 | CC2 | — | R1 | G2 | LT1 | medium |
| 1254 | 2020 | 微信小游戏 | 行尸走肉 | CC5 | CC2 | R3 | G2、G3 | LT3 | medium |
| 1255 | 2020 | 微信小游戏 | 解压玩具 | CC10 | — | R1、R5 | G0 | LT1 | high |
| 1256 | 2020 | 微信小游戏 | 计数大师 | CC3 | CC1 | R2 | G1 | LT1 | medium |
| 1257 | 2020 | 微信小游戏 | 金币大富翁 | CC3 | CC5 | R2 | G1 | LT3 | medium |
| 1258 | 2020 | 微信小游戏 | 铅笔冲刺 | CC2 | CC4 | R1 | G2 | LT1 | medium |
| 1259 | 2020 | 微信小游戏 | 阿瓦隆之王 | CC9 | CC5、CC1 | R3 | G2、G3 | LT3 | high |
| 1260 | 2020 | 微信小游戏 | 高人跑 | CC3 | CC10 | R2 | G1 | LT1 | medium |
| 1261 | 2020 | 微信小游戏 | 《高跟鞋》 | CC3 | CC4 | R2 | G1 | LT2 | high |
| 1262 | 2019 | 微信小游戏 | 《1010!》 | CC6 | — | R4 | G4 | LT1 | high |
| 1263 | 2019 | 微信小游戏 | 《保卫萝卜3》 | CC2 | CC4 | R4 | G2、G3 | LT1、LT2 | high |
| 1264 | 2019 | 微信小游戏 | 《全民奇迹MU》 | CC3 | CC4 | R1、R2 | G1、G3 | LT3 | high |
| 1265 | 2019 | 微信小游戏 | 《六边形拼图》 | CC6 | — | R4 | G4 | LT1 | high |
| 1266 | 2019 | 微信小游戏 | 《大家来找茬》 | CC6 | — | R4 | G4 | LT1 | high |
| 1267 | 2019 | 微信小游戏 | 《天天打怪兽》 | CC3 | CC4 | R2 | G1、G3 | LT2 | high |
| 1268 | 2019 | 微信小游戏 | 《天天斗地主》 | CC1 | — | R4 | G2、G4 | LT1 | high |
| 1269 | 2019 | 微信小游戏 | 《头脑王者》 | CC1 | — | R4 | G4 | LT1 | high |
| 1270 | 2019 | 微信小游戏 | 《少年三国志》 | CC3 | CC4 | R2 | G1、G3 | LT3 | high |
| 1271 | 2019 | 微信小游戏 | 《少年西游记》 | CC3 | CC4 | R2 | G1、G3 | LT3 | high |
| 1272 | 2019 | 微信小游戏 | 《屠龙破晓》 | CC3 | CC4 | R1、R2 | G1、G3 | LT3 | high |
| 1273 | 2019 | 微信小游戏 | 《弹一弹》 | CC10 | — | R4 | G0 | LT1 | medium |
| 1274 | 2019 | 微信小游戏 | 《悠梦》 | CC6 | — | R4 | G4 | LT1 | high |
| 1275 | 2019 | 微信小游戏 | 《成语接龙》 | CC6 | — | R4 | G4 | LT1 | high |
| 1276 | 2019 | 微信小游戏 | 《成语消消乐》 | CC6 | — | R4 | G4 | LT1 | high |
| 1277 | 2019 | 微信小游戏 | 《我切菜贼溜》 | CC10 | — | R1 | G0 | LT1 | high |
| 1278 | 2019 | 微信小游戏 | 《我削皮贼溜》 | CC10 | — | R1 | G0 | LT1 | high |
| 1279 | 2019 | 微信小游戏 | 《我叫MT4》 | CC3 | CC4、CC9 | R1、R2 | G1、G3 | LT3 | medium |
| 1280 | 2019 | 微信小游戏 | 《我在7年后等你》 | CC8 | — | R5 | G4、G5 | LT1 | high |
| 1281 | 2019 | 微信小游戏 | 我的大刀四十米 | CC1 | CC10 | R1 | G2 | LT1 | high |
| 1282 | 2019 | 微信小游戏 | 我走路贼6 | CC10 | — | R1 | G2 | LT1 | medium |
| 1283 | 2019 | 微信小游戏 | 挂机吧兄弟 | CC3 | CC4 | R2 | G1、G3 | LT2 | high |
| 1284 | 2019 | 微信小游戏 | 捣蛋猪 | CC6 | — | R3、R4 | G4 | LT1 | high |
| 1285 | 2019 | 微信小游戏 | 星途WeGoing | CC1 | — | R1 | G2 | LT1 | high |
| 1286 | 2019 | 微信小游戏 | 欢乐动物园 | CC5 | CC4 | R2、R3 | G1、G3 | LT2 | medium |
| 1287 | 2019 | 微信小游戏 | 欢乐大乱斗 | CC10 | — | R1 | G0 | LT1 | high |
| 1288 | 2019 | 微信小游戏 | 欢乐捕鱼 | CC10 | — | R1、R2 | G1 | LT1 | medium |
| 1289 | 2019 | 微信小游戏 | 欢乐球吃球 | CC1 | CC9 | R1 | G2 | LT1 | high |
| 1290 | 2019 | 微信小游戏 | 欢乐象棋 | CC1 | CC6 | R4 | G4 | LT1 | high |
| 1291 | 2019 | 微信小游戏 | 海盗来了 | CC5 | CC7、CC9 | R2、R3 | G1、G3 | LT2 | medium |
| 1292 | 2019 | 微信小游戏 | 涂色花园 | CC10 | — | R4 | G0 | LT1 | high |
| 1293 | 2019 | 微信小游戏 | 热血街篮 | CC1 | CC9 | R1 | G2 | LT1 | high |
| 1294 | 2019 | 微信小游戏 | 猜画小歌 | CC7 | CC6 | R4、R5 | G0 | LT1 | medium |
| 1295 | 2019 | 微信小游戏 | 猫咪后院 | CC8 | CC4 | R2、R5 | G3、G5 | LT2 | high |
| 1296 | 2019 | 微信小游戏 | 王者传奇 | CC1 | CC3、CC9 | R1、R2 | G1、G3 | LT3 | high |
| 1297 | 2019 | 微信小游戏 | 疯狂猜图 | CC6 | — | R4 | G4 | LT1 | high |
| 1298 | 2019 | 微信小游戏 | 空当接龙 | CC6 | — | R4 | G4 | LT1 | high |
| 1299 | 2019 | 微信小游戏 | 胡莱三国 | CC1 | CC6 | R4 | G2、G4 | LT1 | high |
| 1300 | 2019 | 微信小游戏 | 蜘蛛纸牌 | CC6 | — | R4 | G4 | LT1 | high |
| 1301 | 2019 | 微信小游戏 | 贪吃蛇在线 | CC1 | — | R1 | G2 | LT1 | high |
| 1302 | 2019 | 微信小游戏 | 跳跳球 | CC2 | — | R1 | G2 | LT1 | high |
| 1303 | 2019 | 微信小游戏 | 转转拼图 | CC6 | — | R4 | G4 | LT1 | high |
| 1304 | 2019 | 微信小游戏 | 黑暗料理王 | CC5 | CC4 | R3 | G3 | LT3 | medium |
| 1305 | 2018 | 微信小游戏 | 主题医院 | CC5 | — | R3 | G2 | LT3 | high |
| 1306 | 2018 | 微信小游戏 | 修仙录 | CC3 | — | R2 | G1 | LT4 | high |
| 1307 | 2018 | 微信小游戏 | 全民小镇 | CC5 | CC4、CC9 | R3 | G3 | LT3 | medium |
| 1308 | 2018 | 微信小游戏 | 几何大逃亡 | CC1 | — | R1 | G2 | LT1 | high |
| 1309 | 2018 | 微信小游戏 | 创业公司 | CC5 | — | R3 | G2 | LT3 | high |
| 1310 | 2018 | 微信小游戏 | 华容道 | CC6 | — | R4 | G4 | LT1 | high |
| 1311 | 2018 | 微信小游戏 | 商业大亨 | CC3 | CC5 | R2 | G1 | LT3 | medium |
| 1312 | 2018 | 微信小游戏 | 坦克大战 | CC2 | — | R1 | G2 | LT1 | high |
| 1313 | 2018 | 微信小游戏 | 填字游戏 | CC6 | — | R4 | G4 | LT1 | high |
| 1314 | 2018 | 微信小游戏 | 套圈圈 | CC2 | — | R1 | G2 | LT1 | high |
| 1315 | 2018 | 微信小游戏 | 射击 | CC2 | — | R1 | G2 | LT1 | high |
| 1316 | 2018 | 微信小游戏 | 弹弓 | CC2 | — | R1 | G2 | LT1 | high |
| 1317 | 2018 | 微信小游戏 | 弹球王者 | CC3 | — | R2 | G1 | LT1 | medium |
| 1318 | 2018 | 微信小游戏 | 成语猜猜看 | CC6 | — | R4 | G4 | LT1 | high |
| 1319 | 2018 | 微信小游戏 | 打字游戏 | CC2 | — | R1 | G2 | LT1 | high |
| 1320 | 2018 | 微信小游戏 | 打砖块 | CC2 | — | R1 | G2 | LT1 | high |
| 1321 | 2018 | 微信小游戏 | 打飞机 | CC2 | — | R1 | G2 | LT1 | high |
| 1322 | 2018 | 微信小游戏 | 抓娃娃 | CC10 | CC4 | R4 | G0 | LT1 | medium |
| 1323 | 2018 | 微信小游戏 | 损友圈 | CC1 | CC9 | R4 | G3 | LT2 | high |
| 1324 | 2018 | 微信小游戏 | 接水管 | CC6 | — | R4 | G4 | LT1 | high |
| 1325 | 2018 | 微信小游戏 | 推箱子 | CC6 | — | R4 | G4 | LT1 | high |
| 1326 | 2018 | 微信小游戏 | 方块弹珠 | CC10 | — | R1、R4 | G0 | LT1 | medium |
| 1327 | 2018 | 微信小游戏 | 最强弹一弹 | CC10 | — | R1、R4 | G0 | LT1 | medium |
| 1328 | 2018 | 微信小游戏 | 最强飞刀手 | CC2 | — | R1 | G2 | LT1 | high |
| 1329 | 2018 | 微信小游戏 | 武侠Q传 | CC3 | CC4、CC8 | R2 | G1、G3 | LT3 | high |
| 1330 | 2018 | 微信小游戏 | 汉字听写 | CC6 | CC7 | R4 | G4 | LT1 | medium |
| 1331 | 2018 | 微信小游戏 | 点击英雄 | CC3 | — | R2 | G1 | LT2 | high |
| 1332 | 2018 | 微信小游戏 | 爱消除 | CC1 | CC10 | R4 | G2 | LT1、LT2 | high |
| 1333 | 2018 | 微信小游戏 | 猜歌名 | CC6 | CC7 | R4 | G4 | LT1 | medium |
| 1334 | 2018 | 微信小游戏 | 翻滚球球 | CC2 | — | R1 | G2 | LT1 | high |
| 1335 | 2018 | 微信小游戏 | 脑筋急转弯 | CC6 | CC10 | R4 | G4 | LT1 | high |
| 1336 | 2018 | 微信小游戏 | 诗词大会 | CC7 | CC6 | R4 | G4 | LT1 | high |
| 1337 | 2018 | 微信小游戏 | 谜语 | CC6 | — | R4 | G4 | LT1 | high |
| 1338 | 2018 | 微信小游戏 | 贪玩蓝月 | CC3 | CC1 | R1、R2 | G1、G3 | LT3 | high |
| 1339 | 2018 | 微信小游戏 | 跑酷 | CC2 | — | R1 | G2 | LT1 | high |
| 1340 | 2018 | 微信小游戏 | 跳跃 | CC2 | — | R1 | G2 | LT1 | high |
| 1341 | 2018 | 微信小游戏 | 《躲避》 | CC2 | — | R1 | G2 | LT1 | high |
| 1342 | 2018 | 微信小游戏 | 《飞机大战》 | CC2 | — | R1、R2 | G1、G2 | LT1 | medium |
| 1343 | 2018 | 微信小游戏 | 《麻将》 | CC1 | CC6 | R4 | G4 | LT1 | high |
| 1344 | 2017 | 微信小游戏 | 《两人麻将》 | CC1 | CC6 | R4 | G4 | LT1 | high |
| 1345 | 2017 | 微信小游戏 | 《乒乓球》 | CC1 | — | R1 | G2 | LT1 | high |
| 1346 | 2017 | 微信小游戏 | 《保皇》 | CC9 | CC1、CC6 | R4 | G4 | LT1 | medium |
| 1347 | 2017 | 微信小游戏 | 《全民打枪》 | CC10 | — | R1 | G0 | LT1 | medium |
| 1348 | 2017 | 微信小游戏 | 《全民飞机大战》 | CC2 | CC3 | R1、R2 | G1、G2 | LT1 | medium |
| 1349 | 2017 | 微信小游戏 | 《冲顶大会》 | CC1 | CC6 | R4 | G4 | LT1 | high |
| 1350 | 2017 | 微信小游戏 | 《千炮捕鱼》 | CC3 | — | R1、R2 | G1 | LT1 | high |
| 1351 | 2017 | 微信小游戏 | 《单机斗地主》 | CC2 | CC6 | R4 | G4 | LT1 | medium |
| 1352 | 2017 | 微信小游戏 | 《双扣》 | CC1 | CC6 | R4 | G4 | LT1 | high |
| 1353 | 2017 | 微信小游戏 | 《吃豆人》 | CC2 | — | R1 | G2 | LT1 | high |
| 1354 | 2017 | 微信小游戏 | 《四国军棋》 | CC9 | CC1、CC6 | R4 | G4 | LT1 | high |
| 1355 | 2017 | 微信小游戏 | 《围住神经猫》 | CC6 | — | R4 | G4 | LT1 | high |
| 1356 | 2017 | 微信小游戏 | 《坦克风云》 | CC3 | CC2 | R1、R2 | G1、G3 | LT1、LT2 | medium |
| 1357 | 2017 | 微信小游戏 | 《完美建楼》 | CC2 | — | R4 | G2 | LT1 | high |
| 1358 | 2017 | 微信小游戏 | 《小美斗地主》 | CC8 | CC2、CC6 | R4、R5 | G4、G5 | LT1 | medium |
| 1359 | 2017 | 微信小游戏 | 《开心水族箱》 | CC8 | CC4、CC5 | R2、R5 | G3、G5 | LT4 | high |
| 1360 | 2017 | 微信小游戏 | 《弹球大师》 | CC10 | — | R4 | G0 | LT1 | high |
| 1361 | 2017 | 微信小游戏 | 强手棋 | CC1 | CC5 | R3 | G3 | LT1 | medium |
| 1362 | 2017 | 微信小游戏 | 德州扑克 | CC1 | CC6 | R4 | G2 | LT1 | high |
| 1363 | 2017 | 微信小游戏 | 扎金花 | CC1 | — | R4 | G2 | LT1 | high |
| 1364 | 2017 | 微信小游戏 | 旋转跳跃 | CC2 | — | R1 | G2 | LT1 | high |
| 1365 | 2017 | 微信小游戏 | 星星消除 | CC10 | — | R4 | G0 | LT1 | high |
| 1366 | 2017 | 微信小游戏 | 最强飞刀 | CC10 | — | R1 | G2 | LT1 | medium |
| 1367 | 2017 | 微信小游戏 | 欢乐大作战 | CC1 | — | R1 | G2 | LT1 | high |
| 1368 | 2017 | 微信小游戏 | 欢乐德州 | CC1 | CC6 | R4 | G2 | LT1 | high |
| 1369 | 2017 | 微信小游戏 | 欢乐泡泡龙 | CC10 | — | R4 | G2 | LT1 | medium |
| 1370 | 2017 | 微信小游戏 | 疯狂打怪兽 | CC3 | — | R2 | G1 | LT2 | high |
| 1371 | 2017 | 微信小游戏 | 百人牛牛 | CC1 | — | R4 | G2 | LT1 | high |
| 1372 | 2017 | 微信小游戏 | 看图猜词 | CC6 | — | R4 | G4 | LT1 | high |
| 1373 | 2017 | 微信小游戏 | 知识超人 | CC6 | — | R4 | G4 | LT1 | high |
| 1374 | 2017 | 微信小游戏 | 纸牌接龙 | CC6 | — | R4 | G4 | LT1 | high |
| 1375 | 2017 | 微信小游戏 | 经典斗地主 | CC1 | CC6 | R4 | G2 | LT1 | high |
| 1376 | 2017 | 微信小游戏 | 翻转棋 | CC1 | CC6 | R4 | G4 | LT1 | medium |
| 1377 | 2017 | 微信小游戏 | 葵花斗地主 | CC1 | CC6 | R4 | G2 | LT1 | high |
| 1378 | 2017 | 微信小游戏 | 血战麻将 | CC1 | CC6 | R4 | G2 | LT1 | high |
| 1379 | 2017 | 微信小游戏 | 街机捕鱼 | CC3 | — | R1 | G1 | LT1 | medium |
| 1380 | 2017 | 微信小游戏 | 见缝插圆 | CC10 | — | R4 | G2 | LT1 | high |
| 1381 | 2017 | 微信小游戏 | 贪吃蛇 | CC2 | — | R1 | G2 | LT1 | high |
| 1382 | 2017 | 微信小游戏 | 贪婪洞窟 | CC2 | CC4 | R2、R3 | G3 | LT2 | high |
| 1383 | 2017 | 微信小游戏 | 跳棋 | CC1 | — | R4 | G2 | LT1 | high |
| 1384 | 2017 | 微信小游戏 | 黄金矿工2 | CC2 | CC4 | R1、R2 | G2、G3 | LT1、LT2 | medium |
| 1385 | 2017 | 微信小游戏 | 黑白棋 | CC1 | — | R4 | G2 | LT1 | high |
| 1386 | 2016 | 微信小游戏 | Fate/Grand Order | CC8 | CC4 | R5 | G5 | LT3 | high |
| 1387 | 2016 | 微信小游戏 | Pokemon GO | CC4 | CC9 | R1、R5 | G3 | LT3 | medium |
| 1388 | 2016 | 微信小游戏 | 传奇世界H5 | CC3 | CC1 | R2 | G1 | LT3 | high |
| 1389 | 2016 | 微信小游戏 | 倩女幽魂 | CC9 | CC8 | R1、R5 | G3、G5 | LT3 | high |
| 1390 | 2016 | 微信小游戏 | 决战沙城 | CC3 | CC1 | R2 | G1 | LT3 | high |
| 1391 | 2016 | 微信小游戏 | 剑侠情缘 | CC9 | CC8 | R1、R5 | G3、G5 | LT3 | high |
| 1392 | 2016 | 微信小游戏 | 大天使之剑H5 | CC3 | — | R2 | G1 | LT3 | high |
| 1393 | 2016 | 微信小游戏 | 大话西游手游 | CC9 | CC8 | R1、R5 | G3、G5 | LT3 | high |
| 1394 | 2016 | 微信小游戏 | 崩坏3 | CC2 | CC4、CC8 | R1 | G2、G3 | LT2、LT3 | high |
| 1395 | 2016 | 微信小游戏 | 影之刃2 | CC2 | — | R1 | G2 | LT1、LT2 | high |
| 1396 | 2016 | 微信小游戏 | 征途手机版 | CC9 | CC1 | R1 | G1、G3 | LT3 | high |
| 1397 | 2016 | 微信小游戏 | 愚公移山 | CC3 | — | R2 | G1 | LT2 | high |
| 1398 | 2016 | 微信小游戏 | 梦幻西游手游 | CC9 | CC8 | R1、R5 | G3、G5 | LT3 | high |
| 1399 | 2016 | 微信小游戏 | 炉石传说 | CC1 | CC4、CC6 | R3、R4 | G2、G4 | LT1、LT3 | high |
| 1400 | 2016 | 微信小游戏 | 热血传奇手机版 | CC1 | CC9 | R1 | G1、G3 | LT3 | high |
| 1401 | 2016 | 微信小游戏 | 阴阳师 | CC8 | CC4、CC2 | R2、R5 | G3、G5 | LT3 | high |
| 1402 | 2015 | 微信小游戏 | 一个都不能死 | CC2 | — | R1 | G2 | LT1 | high |
| 1403 | 2015 | 微信小游戏 | 七巧板 | CC6 | — | R4 | G4 | LT1 | high |
| 1404 | 2015 | 微信小游戏 | 体育 | CC2 | — | R1 | G2 | LT1 | high |
| 1405 | 2015 | 微信小游戏 | 俗语 | CC6 | — | R4 | G4 | LT1 | high |
| 1406 | 2015 | 微信小游戏 | 停车场 | CC6 | — | R4 | G4 | LT1 | high |
| 1407 | 2015 | 微信小游戏 | 养成 | CC8 | CC3 | R2、R5 | G5、G1 | LT2 | high |
| 1408 | 2015 | 微信小游戏 | 冒险 | CC2 | CC6 | R1、R4 | G2、G4 | LT1 | medium |
| 1409 | 2015 | 微信小游戏 | 动漫 | CC6 | CC7 | R4 | G4 | LT1 | high |
| 1410 | 2015 | 微信小游戏 | 化学 | CC6 | — | R4 | G4 | LT1 | high |
| 1411 | 2015 | 微信小游戏 | 历史 | CC6 | — | R4 | G4 | LT1 | high |
| 1412 | 2015 | 微信小游戏 | 合体 | CC3 | CC6 | R2、R3 | G1、G4 | LT1 | medium |
| 1413 | 2015 | 微信小游戏 | 名言 | CC6 | — | R4 | G4 | LT1 | high |
| 1414 | 2015 | 微信小游戏 | 哲学 | CC6 | — | R4 | G4 | LT1 | high |
| 1415 | 2015 | 微信小游戏 | 地理 | CC6 | — | R4 | G4 | LT1 | high |
| 1416 | 2015 | 微信小游戏 | 塔防 | CC2 | CC6 | R3、R4 | G2、G4 | LT1 | medium |
| 1417 | 2015 | 微信小游戏 | 填字 | CC6 | — | R4 | G4 | LT1 | high |
| 1418 | 2015 | 微信小游戏 | 宗教 | CC6 | — | R4 | G4 | LT1 | high |
| 1419 | 2015 | 微信小游戏 | 战争 | CC2 | CC6 | R3、R4 | G2、G4 | LT1 | medium |
| 1420 | 2015 | 微信小游戏 | 打企鹅 | CC10 | — | R1 | G0 | LT1 | high |
| 1421 | 2015 | 微信小游戏 | 拼图 | CC6 | — | R4 | G4 | LT1 | high |
| 1422 | 2015 | 微信小游戏 | 摩托车 | CC2 | — | R1 | G2 | LT1 | high |
| 1423 | 2015 | 微信小游戏 | 政治 | CC6 | — | R4 | G4 | LT1 | high |
| 1424 | 2015 | 微信小游戏 | 数学 | CC6 | — | R4 | G4 | LT1 | high |
| 1425 | 2015 | 微信小游戏 | 明星 | CC6 | — | R4 | G4 | LT1 | high |
| 1426 | 2015 | 微信小游戏 | 模拟 | CC5 | CC4 | R3 | G2、G3 | LT3 | high |
| 1427 | 2015 | 微信小游戏 | 歇后语 | CC6 | — | R4 | G4 | LT1 | high |
| 1428 | 2015 | 微信小游戏 | 歌词 | CC6 | — | R4 | G4 | LT1 | high |
| 1429 | 2015 | 微信小游戏 | 法律 | CC6 | — | R4 | G4 | LT1 | high |
| 1430 | 2015 | 微信小游戏 | 测测你的前世今生 | CC7 | — | R5 | G0 | LT1 | high |
| 1431 | 2015 | 微信小游戏 | 涂鸦跳跃 | CC2 | — | R1 | G2 | LT1 | high |
| 1432 | 2015 | 微信小游戏 | 物理 | CC6 | — | R4 | G4 | LT1 | high |
| 1433 | 2015 | 微信小游戏 | 猜谜 | CC6 | — | R4 | G4 | LT1 | high |
| 1434 | 2015 | 微信小游戏 | 生物 | CC6 | — | R4 | G4 | LT1 | high |
| 1435 | 2015 | 微信小游戏 | 电影 | CC6 | — | R4 | G4 | LT1 | high |
| 1436 | 2015 | 微信小游戏 | 电视剧 | CC6 | — | R4 | G4 | LT1 | high |
| 1437 | 2015 | 微信小游戏 | 疯狂打企鹅 | CC10 | — | R1 | G0 | LT1 | high |
| 1438 | 2015 | 微信小游戏 | 看你有多色 | CC2 | — | R1 | G2 | LT1 | high |
| 1439 | 2015 | 微信小游戏 | 神经猫的朋友圈 | CC10 | — | R5 | G0 | LT1 | high |
| 1440 | 2015 | 微信小游戏 | 积木 | CC2 | — | R1 | G2 | LT1 | high |
| 1441 | 2015 | 微信小游戏 | 策略 | CC6 | — | R4 | G2、G4 | LT1 | medium |
| 1442 | 2015 | 微信小游戏 | 经济 | CC6 | — | R4 | G4 | LT1 | medium |
| 1443 | 2015 | 微信小游戏 | 经营 | CC5 | CC3 | R2、R3 | G1、G3 | LT3 | high |
| 1444 | 2015 | 微信小游戏 | 舞蹈 | CC6 | — | R4 | G4 | LT1 | medium |
| 1445 | 2015 | 微信小游戏 | 艺术 | CC6 | — | R4 | G4 | LT1 | medium |
| 1446 | 2015 | 微信小游戏 | 英语 | CC6 | — | R4 | G4 | LT1 | medium |
| 1447 | 2015 | 微信小游戏 | 角色扮演 | CC2 | CC3、CC4 | R1、R2 | G1、G2、G3 | LT3 | high |
| 1448 | 2015 | 微信小游戏 | 解谜 | CC6 | — | R4 | G2、G4 | LT1 | high |
| 1449 | 2015 | 微信小游戏 | 诗词 | CC6 | — | R4 | G4 | LT1 | medium |
| 1450 | 2015 | 微信小游戏 | 语文 | CC6 | — | R4 | G4 | LT1 | medium |
| 1451 | 2015 | 微信小游戏 | 谚语 | CC6 | — | R4 | G4 | LT1 | medium |
| 1452 | 2015 | 微信小游戏 | 赛车 | CC2 | — | R1 | G2 | LT1 | medium |
| 1453 | 2015 | 微信小游戏 | 音乐 | CC6 | — | R4 | G4 | LT1 | medium |
| 1454 | 2015 | 微信小游戏 | 飞行 | CC2 | — | R1 | G2 | LT1 | high |
| 1455 | 2015 | 微信小游戏 | 魔方 | CC6 | — | R4 | G2、G4 | LT1 | high |

## 九、自动判定

**结论**:⚠️ v1.1 基本可用,但置信度分布需优化