# 模块槽位塔防：6张玩法图二次修图 Prompt

## 使用方式

- 这份文件用于“第一轮图已经生成，但还不够准”的情况。
- 每张图都默认建立在“保持上一版画面不变，只修正关键识别点”的原则上。
- 用法建议：
  - 把当前图上传给 Gemini
  - 复制对应编号的修图 prompt
  - 重点只修一两个问题，不要一次改太多

## 通用修图前缀

```text
Use the provided image as the direct visual reference.
Do not redesign the whole scene.
Keep the same battlefield, same camera angle, same vertical composition, same defense line, same base layout, same right-side module panel, and same overall art style.
Only refine the specific gameplay readability issues listed below.
This must still look like a premium mobile game screenshot concept.
```

## 图1：基础防线 二次修图

```text
Use the provided image as the direct visual reference.
Keep the same battlefield, same camera angle, same vertical composition, same base layout, same right-side module panel, and same art style.

Refine this image so it reads more clearly as the baseline state of a module-slot tower defense system.

Important fixes:
- make the 4 fixed module slots on the right look more like permanent hardware sockets, not skill buttons
- make the energy cables more visible, clearly running from the slots into the defense core
- keep all 4 slots empty or inactive
- reduce any feeling of a card list or action-button menu
- strengthen the read of top enemy spawn, middle battle line, and bottom base
- the battlefield should feel like a modular defense system waiting to be configured

Do not add new modules.
Do not redesign the UI.
Do not change the camera angle.
```

## 图2：掉落模块 二次修图

```text
Use the provided image as the direct visual reference.
Keep the same battlefield, same camera angle, same defense line, same module panel, same UI layout, and same art style.

Refine this image so the dropped module becomes the unmistakable visual focus.

Important fixes:
- enlarge the dropped module so it feels rare and high-value
- place the dropped module clearly near the center of the lane
- add a stronger loot beam, glow ring, or holographic highlight
- make the dropped object look like a physical machine component or energy cartridge
- show the elite enemy defeat source more clearly near the drop
- keep the 4 module slots on the right empty
- reduce background combat noise so the loot event reads instantly

Do not turn the drop into a coin, gem, card, or generic reward icon.
Do not change the interface framing.
```

## 图3：安装第一个模块 二次修图

```text
Use the provided image as the direct visual reference.
Keep the same battlefield, same camera angle, same defense line, same base structure, same right-side module panel, and same art style.

Refine this image so it more clearly communicates that installing one module changes the whole defense system.

Important fixes:
- make exactly 1 module slot visibly occupied by a cartridge-like module
- strengthen the glowing energy cable running from that installed module into the reactor core
- make the defense line reaction more immediate and readable
- show one dominant combat change such as stronger cannon fire or a clearly visible burning explosion effect
- keep the other 3 module slots empty or inactive
- reduce any feeling that the right-side panel is a skill menu

Do not add a second installed module.
Do not redesign the battlefield.
```

## 图4：第二模块触发联动 二次修图

```text
Use the provided image as the direct visual reference.
Keep the same battlefield, same camera angle, same base layout, same module panel, same UI hierarchy, and same art style.

Refine this image so it clearly communicates synergy between two installed modules.

Important fixes:
- make exactly 2 of the 4 hardware slots visibly occupied
- both installed modules must feel physically connected into the same defense system
- strengthen the energy cables and reactor response
- make the combat effects read as linked synergy, such as chain-burning or lightning-linked fire damage
- avoid showing two unrelated isolated effects
- make the whole defense line feel more upgraded and engineered than image 3

Do not make the image about one single cannon.
Do not change the scene framing.
```

## 图5：Build 成型 二次修图

```text
Use the provided image as the direct visual reference.
Keep the same battlefield, same camera angle, same defense line, same module panel, same UI layout, and same art style.

Refine this image so the completed build reads clearly at a glance.

Important fixes:
- show all 4 module slots installed and active
- make each module effect readable in a different zone of the battlefield
- clearly show burning, chain lightning, freezing control, and summoned frontline units
- make support turrets and defense nodes visibly react to the modules
- strengthen the feeling that the entire defense line is powered by the module system
- reduce any impression of "4 active skills" and emphasize "1 reconfigured defense engine"

Do not redesign the module panel.
Do not lose battlefield readability in visual noise.
```

## 图6：Boss 波检验 二次修图

```text
Use the provided image as the direct visual reference.
Keep the same battlefield, same camera angle, same module panel, same defense system layout, same UI framework, and same art style.

Refine this image so it clearly reads as the boss-wave stress test of the completed modular build.

Important fixes:
- make the boss enemy larger and more clearly the current threat
- keep all 4 slots visibly active and connected to the defense core
- make the battlefield pressure feel intense but still readable
- show all module effects working together against the boss wave
- make the base defense feel like it is barely holding but not collapsing
- preserve the same scene and same system identity from the previous images

Do not turn this into a separate boss arena.
Do not change the camera angle.
Do not hide the right-side module panel.
```
