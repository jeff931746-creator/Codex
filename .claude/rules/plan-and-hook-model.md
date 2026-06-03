# Plan And Hook Model

运行时控制模型：从强制 plan 审批到执行、委派和状态控制动作。

配套文件：[`task-flow-matrix.md`](task-flow-matrix.md) · [`agent-delegation-policy.md`](agent-delegation-policy.md) · [`hook-table.md`](hook-table.md)

## Core Definitions

### Main Agent

主 agent 拥有：请求理解、任务分解、本地执行 vs 委派决策、plan 审批门禁执行、结果整合与最终交付。不应把中间探索步骤堆入共享上下文。主 agent 是用户审批的唯一渠道。

### Subagent

子 agent 是有边界工作的执行隔离单元。

使用时机：读 ≥ 3 个文件但不编辑、产生大量中间输出、执行审核/验证/文档起草、工作可隔离后返回简短结论。

合约：主 agent 发出精确问题 → 子 agent 在隔离上下文中执行 → 只返回结论，不返回过程。子 agent 可辅助 plan，但不拥有任务级正式 plan。

### Plan

`plan` 是每个新任务的强制第一步，防止直接跳入执行。

每次新任务必须：1) 概述预期方式；2) 点名可能改动的文件/系统/行为；3) 说明非显然的权衡或风险；4) 等待用户批准后再执行。

每个 `doc-change` 和 `implementation` plan 必须包含 gate 执行序列小节：

```
## 执行 gate 序列
1. target-inspection — [读什么]
2. edit — [写什么]
3. self-review — subagent（设计文档强制）
4. validation — [检查什么]
5. delivery
```

无此小节的 plan 视为不合格，应拒绝并要求重写。任务方向实质变化后，必须重新 `plan`。

### Hook

hook 是条件—动作触发器：`if condition -> perform action`。在本工作区中是控制逻辑，不是平台运行时。可操作的触发表见 [`hook-table.md`](hook-table.md)。

## Default Operating Model

1. 理解请求
2. 提交 `plan`，选择任务流类型
3. 等待批准
4. 按批准的 plan 逐 gate 执行
5. 边界工作委派给子 agent
6. 让 hook 在触发条件满足时强制执行压缩、委派、rewind 或审核行为

系统偏好：不跳过对齐步骤；不跳过任务分类；不跳过未完成的 gate；小任务 plan 保持简短；不向主上下文堆入探索噪声；不在无审批 gate 的情况下执行大范围改动。

## Trigger-Word Routing

以下词语出现时，默认分类为 `knowledge-asset` + `strict`：

- `标准` / `规范` / `流程` / `体系` / `框架` / `方法论` / `沉淀` / `长期管理` / `长期演进`
- `库`：仅限知识资产类短语：`知识库` / `机制库` / `题材库` / `方法论库` / `人群库` / `竞品库` / `买量组合库` / `复盘库` / `建立 XX 库` / `维护 XX 库`

**不触发**：`代码库` / `依赖库` / `库函数` / `标准库`；用户明确说"不需要长期维护"的单次收集。

行为：主 agent 必须先跑 `governance-design` gate 再写任何产物；降级到 `doc-change` 仅在用户明确说"一次性、无需长期治理"时允许；若触发词出现但最终分类为 `doc-change`，plan 必须说明为何不适用长期治理。

根本原因：典型失败是用户说"建立 X 标准/库/流程"，agent 直接跳到模板设计而不先扫现有资产和定义数据所有权。触发词路由让这个跳跃结构上不可能发生。

## Plan-Stage Scan Requirement For `knowledge-asset`

`knowledge-asset` plan 必须显式列出：
- 已搜索的同类现有资产（路径列表，即使为空）
- 已读取的 README 和规则文件（路径 + 内容摘要）
- 已检查的自动化脚本入口（路径列表）

缺少这三项的 plan 视为不合格，用户应拒绝并要求重写。

## Mandatory Stage Gates

- 下一个 gate 在当前 gate 完成前不得开始
- gate 阻断时，停在当前 gate，解决阻塞、`rewind` 或重新 `plan`
- 子 agent 继承有范围的任务类型和当前 gate；不得跳过 gate
- 任务状态始终显示：任务类型 · 当前 gate · 已完成 gate · 下一 gate

## When To Trigger Subagent

优先使用子 agent：读 ≥ 3 个文件但不编辑、产生大量中间分析、主线程只需简短答案、验证/评分/起草可并行完成。

子 agent 分配必须包含：精确问题、相关文件路径、输出约束（≤300 tokens 摘要 / bullet findings / JSON）、有范围的任务类型 + 当前 gate。

套娃禁止：主 agent 已有结论再委派子 agent 确认，零可靠性。委派前强制自检：「我对这个问题有结论了吗？」有 → 本地完成；无 → 给子 agent 开放问题。
