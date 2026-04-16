# Godot 实现骨架

这里是新 demo 使用 Godot 时的默认实现目录参考。

```text
Godot/
  project.godot
  scenes/
  scripts/
  autoload/
  assets/
  configs/
  ui/
  docs/
```

## 目录说明

- `project.godot`：项目配置入口。
- `scenes/`：所有场景文件。
- `scripts/`：所有 GDScript 脚本。
- `autoload/`：全局单例与事件总线。
- `assets/`：图片、音频、字体、特效等资源。
- `configs/`：数值、节奏、卡包、关卡等配置。
- `ui/`：界面场景和 HUD。
- `docs/`：实现说明、输入映射、导出说明、节点约定。

## 推荐约定

- 一个核心玩法至少对应一个独立场景或脚本边界。
- 配置优先外置，避免把节奏、波次、卡牌和商店价格写死在脚本里。
- 用 `autoload` 管全局状态，但不要把所有逻辑都堆进去。
- 场景树和节点命名尽量固定，避免后续引用路径不稳定。

## 启动顺序

1. 建 `project.godot`
2. 建主场景
3. 建输入映射
4. 建全局单例
5. 再拆战斗、UI、商店、配置
