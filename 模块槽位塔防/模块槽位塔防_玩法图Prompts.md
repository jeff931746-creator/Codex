# 模块槽位塔防：6张玩法可视化图片 Prompt 包

## 使用建议

- 先生成 `图1 基础防线`，作为后续所有图片的视觉参考。
- 从 `图2` 开始，建议在 Gemini 中使用“参考上一张图片”的方式继续生成，保证场景、镜头、UI、模块槽位保持一致。
- 每张图都保持：
  - 同一竖屏战场
  - 同一镜头机位
  - 同一右侧 4 槽模块面板
  - 同一主基地与防线结构

## 全局总控 Prompt

```text
Create a consistent multi-image gameplay concept series for a vertical mobile game called "module-slot tower defense".

Important global rules for every image in the series:
- use the exact same battlefield, same camera angle, same vertical composition, same art style, same defense line layout, same module panel layout
- lock the screen layout across the full series: enemy spawn zone at the top, battle lane in the center, base zone at the bottom, fixed 4-slot module panel on the right
- do not move the battlefield horizon, do not change the lane width, do not move the base position, do not move the module panel position
- treat image 1 as the master layout reference for all later images
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

## 图1：基础防线

```text
Create image 1 of a consistent gameplay concept series for a vertical mobile game called "module-slot tower defense".

Use the same battlefield, same camera angle, same vertical composition, same art style, and same fixed UI framework that will be reused across the entire series.

This image must show the baseline battle state before any major module build is formed.

Core composition:
- enemies pour from the top toward the base at the bottom
- one main defense lane with a clear central battle line
- the base includes a main cannon, city wall, reactor core, side defense nodes, and a summoning beacon
- the right side shows a fixed hardware module panel with exactly 4 embedded module slots
- all 4 module slots are currently empty or inactive
- glowing energy cables connect the module slots into the defense system, but the system is only lightly powered

Gameplay readability goals:
- clearly show top enemy spawn, middle battle, bottom base defense
- make the fixed module panel very visible
- communicate that this is a modular defense system waiting to be configured
- the battlefield should feel pressured but still under control

Style goals:
- premium mobile strategy game concept art
- dark sci-fi fantasy
- real game screenshot feeling
- cinematic but practical
- polished mobile UI
- minimal text only

Negative guidance:
no backpack inventory
no skill button menu
no merge plant feeling
no card list
no overdesigned HUD
```

## 图2：掉落模块

```text
Create image 2 of the same gameplay concept series.

Use image 1 as a visual reference and keep the exact same battlefield, same camera angle, same defense line, same module panel, same UI layout, and same art style.

This image must focus on one main event:
an elite enemy has just been killed, and a large glowing module loot drops onto the battlefield.

Very important composition rules:
- preserve the exact same screen layout as image 1, with no camera shift and no scene rearrangement
- keep the lane centerline, base position, defense system silhouette, and right-side module panel in exactly the same place as image 1
- the dropped module must be the visual focus of the image
- place the module drop near the center of the lane, clearly visible
- the module drop should be large, glowing, high-value, and obviously collectible
- show a defeated elite enemy or explosion mark near the drop so it is clear where it came from
- add a strong loot beam, glow ring, or holographic highlight around the dropped module
- the dropped module should look like a physical machine component or energy cartridge, not a coin, not a gem, not a card
- the right-side module panel must still have 4 empty fixed slots
- the defense line is still fighting enemy waves, but the loot drop is the main focus

The image must clearly communicate:
"an important battle module has dropped and can now be installed."

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
do not alter the scene layout from image 1
do not move the base or module panel
```

## 图3：安装第一个模块

```text
Create image 3 of the same gameplay concept series.

Use image 2 as the visual reference and keep the exact same battlefield, same camera angle, same defense line, same base structure, same right-side module panel, and same art style.

This image must focus on one clear event:
the first module has just been installed into one of the fixed hardware slots.

Important visual goals:
- preserve the exact same screen layout as image 1 and image 2
- one module slot on the right is now visibly occupied by a powerful module cartridge
- glowing energy cables now pulse from that installed module into the reactor core and main defense line
- the battlefield reaction should be immediate and obvious
- show one clear combat change such as stronger cannon fire, burning explosions, or energized defense nodes
- the other 3 module slots remain empty or inactive

The image must clearly communicate:
"installing one module changes the whole defense system."

Style goals:
- premium mobile strategy game concept art
- highly readable gameplay
- dark sci-fi fantasy
- real game screenshot feeling
- polished mobile UI
- minimal text only

Negative guidance:
no skill button menu
no floating action bar feeling
no backpack management
no card collection screen
```

## 图4：第二模块触发联动

```text
Create image 4 of the same gameplay concept series.

Use image 3 as the visual reference and keep the exact same battlefield, same camera angle, same base layout, same module panel, same UI hierarchy, and same art style.

This image must focus on one clear event:
a second module is now installed, and the interaction between modules visibly changes the battle.

Installed modules:
- Fire Core
- Chain Coil

Visual goals:
- preserve the exact same screen layout as images 1 to 3, with no UI or camera drift
- exactly 2 of the 4 hardware slots are now occupied
- both installed modules should feel connected into the same defense system
- energy cables should glow more strongly than before
- the battlefield should clearly show chain burning or lightning-linked explosions across multiple enemies
- communicate synergy, not just two independent effects
- the defense line now feels more engineered and more upgraded

The image must clearly communicate:
"module combinations create a stronger build through synergy."

Style goals:
- premium mobile gameplay concept
- dark sci-fi fantasy
- strong combat clarity
- real game screenshot feeling
- minimal text only

Negative guidance:
no isolated single turret focus
no abstract infographic
no random visual clutter
no redesign of scene framing
```

## 图5：Build 成型

```text
Generate image 5 of the same gameplay concept series for a "module-slot tower defense" game.

Use the previous image as a visual reference and keep the exact same battlefield, same camera angle, same defense line, same module panel, same UI layout, and same art style.

This image shows a completed modular build in full operation.

Installed modules:
- Fire Core
- Chain Coil
- Ice Crystal
- Barracks Beacon

The battlefield must clearly show that these modules are modifying the entire defense line:
- preserve the exact same screen layout as images 1 to 4
- burning explosions across enemy groups
- chain lightning jumping between monsters
- frozen and slowed enemies in ice zones
- summoned soldiers fighting in front of the wall
- support turrets and defense nodes visibly reacting to the installed modules
- the whole defense line feels powered and transformed by the module setup

Important visual goal:
this should feel like "a defense system being reconfigured by modules", not "a normal tower defense with 4 active skills"

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

## 图6：Boss 波检验

```text
Create image 6 of the same gameplay concept series.

Use image 5 as the visual reference and keep the exact same battlefield, same camera angle, same module panel, same defense system layout, same UI framework, and same art style.

This image must focus on the final validation moment:
the completed module build is being tested by a boss wave.

Boss battle requirements:
- preserve the exact same screen layout as images 1 to 5
- a large boss enemy pushes from the top toward the base
- the battlefield is under intense pressure
- the fully installed 4-slot module system is clearly visible on the right
- all four slots look active, powered, and physically connected into the defense core
- the base defense system is responding at full intensity
- show burning, chain lightning, freezing control, and summoned frontline units all working together
- the fight should feel dangerous, but the build is holding

The image must clearly communicate:
"the modular build has matured and is now being stress-tested against a boss wave."

Style goals:
- premium mobile strategy game screenshot concept
- dramatic but readable
- dark sci-fi fantasy
- commercial quality
- polished UI
- real game screenshot feeling
- minimal text only

Negative guidance:
no generic boss arena
no scene reset
no camera angle change
no loss of module panel clarity
no skill-button interpretation
```
