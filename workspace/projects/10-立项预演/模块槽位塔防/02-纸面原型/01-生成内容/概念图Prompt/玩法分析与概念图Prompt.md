# 模块槽位塔防：聊天整理

## 1. 方向结论

`模块槽位塔防` 的核心不是“背包换皮”，而是把背包里的空间管理，压缩成 `少量固定槽位 + 明确模块联动`。

一句话定义：

玩家不再管理一整包道具，而是在有限槽位里装配核心模块，让防线按不同流派运转。

这个方向的价值在于：

- 比背包塔防更简单
- 比单位合成塔防更清楚
- 比 `向日葵` 更容易拉开前台交互差异
- 保留 `Build`、`联动`、`关键替换` 的爽点

## 2. 为什么它能和向日葵拉开差距

`向日葵` 这一路的前台感知更像：

- 单位上场
- 合成升星
- 阵地排布
- 同类单位成长

`模块槽位塔防` 应该让用户感知成：

- 核心系统装配
- 防线引擎改装
- 插件联动
- 少量关键替换

要点是：

- 不是“合单位”
- 不是“格子背包”
- 不是“俄罗斯方块式物品管理”
- 而是“用 4-6 个固定槽位改造整条防线”

## 3. 核心玩法

核心循环：

1. 怪潮压线
2. 防线自动作战
3. 掉落模块或升级机会
4. 在固定槽位里装配/替换模块
5. 激活联动
6. 用成型 Build 处理精英和 Boss

单局建议：

- `5-8 分钟`
- 每次掉落都要有价值
- 模块数量少，但替换决策关键

## 4. 槽位结构建议

推荐先做 `4 槽`：

- `核心槽`
- `输出槽`
- `功能槽`
- `召唤槽`

也可以扩到 `5-6 槽`，但不建议一开始太多。

## 5. 模块示例

- `火核`：主伤害带灼烧与爆炸
- `连锁线圈`：攻击在敌群间弹射
- `冰结晶`：地面形成减速/冻结区
- `兵营信标`：召唤士兵顶线

正确方向不是只加面板，而是：

模块装上去后，战场表现立刻变了。

## 6. 联动示例

- `火核 + 连锁线圈`：连锁灼烧
- `冰结晶 + 主炮`：高频减速点杀
- `兵营信标 + 增压类模块`：士兵刷新更快
- `火核 + 召唤类模块`：召唤单位附带燃烧攻击

## 7. 战斗画面应长什么样

战斗画面必须让用户一眼看出：

- 上方出怪
- 中间交战
- 下方基地和主防线
- 右侧是 `4 个固定硬件槽位`
- 槽位通过 `能量线/电缆` 连到防线核心

最重要的认知是：

这不是“4 个技能按钮”，而是“4 个正在驱动整条防线的模块”。

## 8. 对当前生成图的判断

已生成的竖屏图方向基本正确，优点是：

- 竖屏真机感成立
- 怪潮压线清楚
- 火、电、冰、召唤四种效果一眼能懂
- 基地、防线、Boss 压力成立

但当前图更像：

`普通守线塔防 + 右侧技能按钮`

而不像：

`模块槽位塔防`

关键问题：

- 右侧更像技能卡/装备列表，不像固定模块槽位
- 模块和防线核心没有明确“物理连接感”
- 看起来像“4 个技能同时生效”，不像“整条防线被模块驱动”
- 画面中心更像主炮，而不是整条防线系统

## 9. 概念图系列结构

这套图应该做成 `玩法链条系列图`，不是一张总览图。

推荐 `6 张图`：

1. `基础防线`
2. `掉落模块`
3. `安装第一个模块`
4. `第二模块触发联动`
5. `Build 成型`
6. `Boss 波检验`

系列图全局规则：

- 同一场景
- 同一机位
- 同一 UI 框架
- 每一张只变化一个关键状态

## 10. Gemini 总控提示词

```text
Create a consistent multi-image gameplay concept series for a vertical mobile game called “module-slot tower defense”.

Important global rules for every image in the series:
- use the exact same battlefield, same camera angle, same vertical composition, same art style, same defense line layout, same module panel layout
- enemies always come from the top and move toward the base at the bottom
- the base at the bottom includes a main cannon, city wall, reactor core, side defense nodes, and a summoning beacon
- on the right side there is always the same fixed module panel with exactly 4 embedded module slots
- the module slots must look like permanent machine slots connected by glowing energy cables into the defense system
- this is not a backpack game, not a merge plant game, not a sunflower-style game
- this is not a skill button menu, the slots are physical system modules
- premium mobile strategy game concept art
- real game screenshot feeling
- highly readable gameplay
- dark sci-fi fantasy style
- minimal text only
- each image should show one clear step in the gameplay chain
```

## 11. Gemini：掉落模块提示词

这张图最容易失败，所以这里保留最终修正版本。

```text
Create image 2 of the same gameplay concept series.

Use the previous image as a visual reference and keep the exact same battlefield, same camera angle, same defense line, same module panel, same UI layout, and same art style.

This image must focus on ONE main event:
an elite enemy has just been killed, and a large glowing module loot drops onto the battlefield.

Very important composition rules:
- the dropped module must be the visual focus of the image
- place the module drop near the center of the lane, clearly visible
- the module drop should be large, glowing, high-value, and obviously collectible
- show a defeated elite enemy or explosion mark near the drop so it is clear where it came from
- add a strong loot-beam, glow ring, or holographic highlight around the dropped module
- the dropped module should look like a physical machine component or energy cartridge, not a coin, not a gem, not a card
- the right-side module panel must still have 4 empty fixed slots
- the defense line is still fighting enemy waves, but the loot drop is the main focus

The image must clearly communicate:
“an important battle module has dropped and can now be installed.”

Style goals:
- premium mobile game screenshot concept
- strong readability
- dark sci-fi fantasy
- minimal text only
- cinematic but practical
- real game screenshot feeling

Negative guidance:
no backpack inventory
no card drop
no random gem loot
no tiny item
no hidden module
no vague reward
no skill button menu
do not change the camera angle
do not redesign the interface
```

## 12. Gemini：安装后真机图提示词

```text
Generate a vertical mobile game gameplay concept image for a “module-slot tower defense” game.

The image must look like a real mobile game battle screenshot, but with a very clear modular defense system.

Core composition:
- enemy waves and elite monsters pour from the top toward a base at the bottom
- one main defense lane
- the base is protected by a full defense system: a main cannon, city wall, reactor core, side support turrets, and a summoning beacon
- on the right side there are exactly 4 fixed hardware module slots, built into a visible module panel
- each module is inserted like a cartridge into a slot
- glowing energy cables connect the module slots directly into the reactor core and defense system
- the slots must look like permanent system slots, NOT like skill buttons or cards

Installed modules:
- Fire Core
- Chain Coil
- Ice Crystal
- Barracks Beacon

The battlefield must clearly show that these modules are modifying the entire defense line:
- burning explosions across enemy groups
- chain lightning jumping between monsters
- frozen and slowed enemies in ice zones
- summoned soldiers fighting in front of the wall
- support turrets and defense nodes visibly reacting to the installed modules
- the whole defense line feels powered and transformed by the module setup

Important visual goal:
this should feel like “a defense system being reconfigured by modules”, not “a normal tower defense with 4 active skills”

Style goals:
- premium mobile strategy game concept art
- highly readable gameplay
- dark sci-fi fantasy
- strong combat pressure
- polished mobile UI
- cinematic but practical
- real game screenshot feeling
- minimal text only
- clean hierarchy
- commercial quality

Negative guidance:
no backpack inventory
no tetris bag
no merge plants
no sunflower style
no skill button menu
no card list feeling
no abstract infographic
no engineering blueprint
no isolated single cannon focus
```

## 13. 不再保留的无关内容

以下内容已从本次整理中主动剔除：

- 之前关于 `War3 RPG塔防` 的大段市场路线讨论
- `向僵尸开炮 / 梦境护卫队 / 皇室式守塔` 的长线立项争论
- 与本次“模块槽位塔防概念图”无直接关系的商业化模型细节
- 无关的图像生成往返试错描述

本文件只保留：

- 模块槽位塔防本体
- 与向日葵的核心差异
- 概念图该怎么画
- 可直接复制的 Gemini 生成词
