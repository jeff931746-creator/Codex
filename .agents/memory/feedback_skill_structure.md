---
name: Skill 结构与打包规范
description: 创建、评估、测试、打包 Codex Skill 时必须遵守的目录边界和产物放置规则
type: feedback
---

Codex Skill 的标准目录结构：

- `<skill-name>/SKILL.md`：必需，skill 的核心描述和使用说明。
- `<skill-name>/scripts/`：可选，skill 运行时需要的脚本。
- `<skill-name>/references/`：可选，skill 依赖的参考资料，如风格指南、示例。
- `<skill-name>/evals/`：可选，评估报告按日期命名。
- `<skill-name>/tests/`：可选，测试产物按日期分组。

操作规范：

- 新建 skill 时，在根目录创建 `<skill-name>/`，写好 `SKILL.md`；如有脚本，放入 `scripts/`。
- 跑评估时，报告输出到 `<skill-name>/evals/`，文件名带日期；不要把评估报告放到根目录或其他 skill 文件夹。
- 跑测试时，测试产物输出到 `<skill-name>/tests/YYYY-MM-DD[-备注]/`；临时快速验证先放 `_sandbox/`，确认有用后再移动到对应 skill 的 `tests/`。
- 打包 `.skill` 文件时，输出到 `builds/`；包内包含 `SKILL.md`、`scripts/`、`references/`，不包含 `evals/` 和 `tests/`。
- 打包后用 `unzip -l` 验证内容完整，且没有混入 `evals/` 或 `tests/`。
- 清理时，`_sandbox/` 用完可删，`tests/` 里超过一个月的旧测试产物可以清理，`builds/` 只保留最新版 `.skill` 文件。

**Why:**
用户提供了 skill 文件夹结构与操作规范截图，并要求“学习一下”。

**How to apply:**
后续创建、修改、评估、测试、打包 skill 时，先按这套目录边界规划产物位置，避免把评估、测试、临时文件混入可分发的 `.skill` 包。
