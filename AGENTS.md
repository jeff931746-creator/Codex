# AGENTS.md — Codex 入口（纯指针）

本文件**不定义任何工作流规则**，只把 Codex 指向唯一真相源。
规则全部由 Claude 在 `CLAUDE.md` 和 `.claude/rules/` 维护，本文件刻意不复制其内容，以免两份漂移。

> 历史教训：本文件曾内联复制规则，半个月后与 `CLAUDE.md` 实质漂移（Skills 清单过期、流程分级缺失），导致 Codex 按过期规则行事。现已改为纯指针。**不要再往本文件里粘贴规则正文。**

---

## 一、权威规则源（执行任何非平凡任务前必读）

在本仓库工作时，Codex 必须先读以下文件，并按其中定义的任务流、gate 门禁、路由规则、记忆规则、收尾要求执行（与 Codex 自身 system/developer 指令兼容的范围内）：

1. `/Users/mt/.claude/projects/-Users-mt-Documents-Codex/memory/MEMORY.md` — 记忆索引
2. `/Users/mt/Documents/Codex/CLAUDE.md` — 项目主入口（入口选择表、流程强度分级、决策路由器）
3. `/Users/mt/Documents/Codex/.claude/rules/task-flow.md` — 任务流类型、gate 顺序、委派规则、Hook 触发表
4. 按任务需要，继续读 `.claude/rules/quality-gates.md`（LLM 事实性处理 + Git 卫生）、`.claude/rules/workflow-chain.md`（工作流层级）、`.claude/references/`（API 调用规则、工作流详细参考）

若 Claude 规则与更高优先级的 Codex 运行时规则冲突，遵守更高优先级规则，并显式报告偏差。

## 二、高风险治理类任务：Codex 不主导

以下任务对流程遵守度要求高，**Codex 不得自行主导执行**。发现任务属于此类时，停下并告知用户"这类应由 Claude 驱动"：

- `knowledge-asset` 类：建立/修改标准、规范、库、方法论、长期流程、体系、框架
- 需求 GDD 写作与审核（走 `gdd-write` / `gdd-review`）
- 立项流程各阶段（六闸门评审、纸面原型等）
- 任何对 `.claude/rules/`、`CLAUDE.md`、Skills 的规则性改动

Codex 可承接：执行类、写代码/脚本、有明确边界的局部产出、收集与归一等 bounded work。

## 三、Codex 专属护栏：`.claude/` 只读

`.claude/` 和 `/Users/mt/.claude/` 是 Claude 拥有的规则、hook、worktree、记忆源。

Codex **可以**读这些文件、把规则摘要进当前任务上下文、按兼容规则执行。

Codex **不得**创建、编辑、移动、删除、格式化、同步或间接改动 `.claude/` 与 `/Users/mt/.claude/` 下任何文件；不得把 `.claude` 当作 Codex 的可写状态存储；不得创建与 Claude 平行的 Codex 侧规则源。若需要规则或记忆变更，在对话中向用户提出，由 Claude 来改。

在执行任何会创建/编辑/移动/删除/格式化/同步文件的 shell 命令或脚本前，先用护栏校验目标路径：

```bash
bash /Users/mt/Documents/Codex/tools/codex-guard/check-paths.sh <path> [...]
```

对 `apply_patch`，Codex 须直接检查 patch 目标，不得包含受保护的 `.claude` 路径。

Codex 不得运行会写入 `.claude/` 的 Claude checkpoint 脚本；遇到此类收尾步骤时，跑兼容的 review/check，跳过 `.claude` 写入，并报告该边界。
