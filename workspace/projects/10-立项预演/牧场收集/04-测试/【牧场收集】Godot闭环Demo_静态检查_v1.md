# 【牧场收集】Godot闭环演示_静态检查_v1

## 检查目标

验证 Godot 演示的文件结构、场景引用、脚本引用和配置边界是否符合闭环演示计划。

## 检查项

- Godot 项目入口：`03-实现/Godot/project.godot`
- 主场景：`03-实现/Godot/scenes/Main.tscn`
- 战斗场景：`03-实现/Godot/scenes/Battle.tscn`
- 全局状态：`03-实现/Godot/autoload/GameState.gd`
- 主界面逻辑：`03-实现/Godot/scripts/Main.gd`
- 战斗逻辑：`03-实现/Godot/scripts/Battle.gd`
- 外置配置：`03-实现/Godot/configs/demo_data.json`
- 实现说明：`03-实现/Godot/docs/implementation_notes.md`

## 自动检查结果

当前已安装 Godot 4.6.2，并通过：

- `godot --headless --path ... --quit`，无界面加载检查
- `godot --path ... --scene res://scenes/Main.tscn --quit-after 2`

## 待执行玩法走查

新版演示已从调试型主界面改为强制阶段闭环，需要在 Godot 编辑器中继续手动试玩检查：

1. 开局 5 秒内只看到一个明确主按钮：`防守草地牧门`。
2. 第一场胜利后回到主界面，显示 `叶犬碎片 0/5 -> 5/5`。
3. 主按钮变为 `孵化叶犬`，点击后显示伙伴加入、`战力 2 -> 5`。
4. 果园围栏以独立阶段显示解锁。
5. 第二场战斗中叶犬有独立位置、名字和绿色辅助攻击。
6. 第二场结束后进入 `free_loop`，才出现自由刷区入口。
