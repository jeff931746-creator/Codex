# 国王带队守线RPG塔防：6张玩法概念图 Prompt 包

## 说明

- 这套图基于 [【国王带队守线RPG塔防】立项文档.md](/Users/mt/Documents/Codex/国王带队守线RPG塔防/【国王带队守线RPG塔防】立项文档.md) 的核心玩法设计整理。
- 画面方向围绕：
  - 国王带队守线
  - 前场短程打野
  - 三选一成长
  - 神器驱动 Build 跃迁
  - Boss 压门
- 用户说的是“竖屏16:9”，这里按移动端常见玩法图理解为 `竖屏 9:16`。
- 推荐生成顺序：`图1 -> 图2 -> 图3 -> 图4 -> 图5 -> 图6`
- 从图2开始，建议在 Gemini 中使用上一张图作为视觉参考，确保场景、机位和 UI 一致。

## 全局总控 Prompt

```text
Create a consistent 6-image gameplay concept series for a vertical mobile game called "Kingline TD", a king-led defense RPG tower defense game.

Global rules for every image in the series:
- vertical mobile game composition, 9:16 portrait layout
- same battlefield, same camera angle, same art style, same kingdom wall, same defense line, same lane direction, same UI framework across all 6 images
- enemies always come from the top and push toward the base at the bottom
- the bottom area always contains the kingdom wall, gate, main defense line, and the king's fallback zone
- the king is a visible controllable hero, not just a UI icon
- allied followers fight alongside the king and the defense line
- the images must clearly communicate "king leading the final defense", not generic hero action combat
- this is not a pure auto battler, not a generic tower defense menu screen, not a vampire-survivor-only battlefield
- premium mobile fantasy strategy game screenshot feeling
- clean mobile UI
- strong gameplay readability
- minimal text only
- each image should show one clear gameplay step in the progression chain
```

## 图1：最后防线建立

```text
Create image 1 of the gameplay concept series for "Kingline TD".

Use a vertical 9:16 mobile game screenshot composition.

This image must show the baseline state of the game:
the king and a small group of followers are defending the kingdom's last line against the first incoming monster wave.

Core composition:
- enemies and monsters pour from the top toward the kingdom gate at the bottom
- the king stands near the frontline, clearly visible as the controllable leader
- 2 to 4 allied followers fight near the king
- the kingdom wall, gate, and core defense line are clearly visible at the bottom
- one main lane with strong readability
- the battlefield should already suggest pressure, but not full chaos
- mobile gameplay UI should show health, skill frame, and minimal tactical indicators

Important visual goal:
the player must instantly understand "I am the king, I am leading a squad, and I must hold the last defense line."

Style goals:
- medieval fantasy with strong kingdom defense atmosphere
- premium mobile strategy game screenshot concept
- readable combat hierarchy
- dramatic but practical

Negative guidance:
no generic MOBA look
no endless battlefield without a base
no purely static tower defense view
no overcomplicated HUD
```

## 图2：前场打野抢高价值目标

```text
Create image 2 of the same gameplay concept series.

Use image 1 as the visual reference and keep the exact same battlefield, same camera angle, same wall position, same lane structure, same UI framework, and same art style.

This image must focus on one clear event:
the king leaves the safety of the defense line and pushes slightly forward to defeat a high-value neutral target or elite event monster.

Important visual goals:
- the king is visibly stepping out from the main defense line into the forward combat zone
- followers and the rear defense line are still visible, showing that the base is still under pressure
- the high-value target should look rare, dangerous, and worth the risk
- the image must communicate risk-versus-reward
- the forward event should feel like a short tactical sortie, not a totally separate map
- the kingdom gate and rear line must still remain visible at the bottom

The image must clearly communicate:
"the player can briefly leave the line to secure a high-value event and return stronger."

Style goals:
- premium mobile gameplay concept
- strong tension between greed and defense
- readable vertical battle staging

Negative guidance:
no open-world exploration feeling
no separate dungeon map
no scene reset
do not change the camera angle
```

## 图3：三选一成长后队伍明显变强

```text
Create image 3 of the same gameplay concept series.

Use image 2 as the visual reference and keep the exact same battlefield, same camera angle, same wall position, same lane layout, same UI hierarchy, and same art style.

This image must focus on one clear event:
after a three-choice upgrade selection, the king's squad becomes visibly stronger.

Important visual goals:
- show a clear before-and-after upgrade feeling
- the king and followers should now look stronger, more coordinated, or more specialized
- one obvious combat improvement should be visible, such as stronger projectiles, better frontline hold, or more effective follower attacks
- the defense line should look more stable than before
- a subtle three-choice or reward result UI can be implied, but the battlefield transformation is the real focus

The image must clearly communicate:
"a single upgrade choice can noticeably strengthen the whole squad and defense line."

Negative guidance:
no deckbuilding screen
no full-screen reward menu
no disconnected upgrade illustration
```

## 图4：神器让 Build 发生跃迁

```text
Create image 4 of the same gameplay concept series.

Use image 3 as the visual reference and keep the exact same battlefield, same camera angle, same wall, same lane structure, same UI hierarchy, and same art style.

This image must focus on one clear event:
the king acquires a powerful relic or artifact, and the entire build visibly evolves.

Important visual goals:
- the artifact should look rare, mythic, and gameplay-defining
- the king's combat style or aura should visibly change
- followers or the defense line should also be affected by the artifact
- the battlefield should show a strong leap in power, not just a small numeric increase
- this should feel like a "build-defining moment"

Possible visual examples:
- holy royal banner relic empowering all nearby followers
- cursed crown relic causing chain explosions
- sacred blade relic causing the king to cleave enemy waves
- summoning relic causing reinforcements to appear

The image must clearly communicate:
"the relic changes how this run plays."

Negative guidance:
no generic loot chest screen
no isolated item card art
no ordinary stat-up feeling
```

## 图5：Build成型后回防顶住Boss

```text
Create image 5 of the same gameplay concept series.

Use image 4 as the visual reference and keep the exact same battlefield, same camera angle, same kingdom wall, same lane layout, same UI framework, and same art style.

This image must focus on one clear event:
the king and the fully formed squad return to the defense line and use their built-up synergy to withstand a major boss wave.

Important visual goals:
- a major boss or siege monster is pushing from the top
- the king stands at the center of the defense effort
- followers are clearly contributing, not just decorative side units
- the artifact/build effect is still visible
- the kingdom wall and gate are under visible pressure
- the whole image should feel like a decisive "hold the line" moment

The image must clearly communicate:
"the earlier choices and risks now pay off in a dramatic defense showdown."

Negative guidance:
no separate boss arena
no loss of base identity
no switch to pure hero-action spectacle
```

## 图6：王国绝境反转与胜利定格

```text
Create image 6 of the same gameplay concept series.

Use image 5 as the visual reference and keep the exact same battlefield, same camera angle, same kingdom wall, same lane layout, same UI hierarchy, and same art style.

This image must focus on one clear event:
the king and squad survive the final pressure and achieve a dramatic turnaround victory at the last defense line.

Important visual goals:
- the battlefield should still show aftermath pressure, not a relaxed menu scene
- the king should feel like the true commander and hero of the defense
- surviving followers should still be visible around him
- the kingdom wall and defense line remain central to the composition
- the image should feel like a "we held the kingdom" climax
- victory should come from leadership, build, and defense synergy, not from random spectacle

The image must clearly communicate:
"the king-led defense build survived the final crisis."

Style goals:
- premium mobile strategy key gameplay visual
- strong emotional payoff
- cinematic but still readable like a mobile game screenshot

Negative guidance:
no detached victory splash screen
no pure cutscene framing
no loss of gameplay readability
```
