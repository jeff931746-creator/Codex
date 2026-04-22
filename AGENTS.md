# Workspace Rules

This workspace is for workflow-related assets only.
These rules apply repo-wide unless a deeper folder explicitly narrows them.

## Scope

- Keep only files, scripts, notes, research, prompts, and tools that directly support the active workflow.
- Prefer placing work in the existing top-level folders: `projects/`, `research/`, `tools/`, `playground/`, and `tmp/`.

## Software And Runtime Policy

- Do not install software into this workspace by default.
- Do not add local runtimes, SDKs, package manager globals, app installers, or downloaded binary bundles under this workspace unless the user explicitly approves them as workflow-critical.
- If a task can be completed with existing system tools or already-available dependencies, prefer that path.
- If new software appears necessary, stop and ask before installing, downloading, or vendoring it into the workspace.

## Cleanup Expectations

- Treat `tmp/` as scratch space for temporary artifacts.
- Remove temporary installers, caches, extracted runtimes, and other non-workflow files after use unless the user explicitly asks to keep them.
- Avoid leaving behind large support files that are not part of the ongoing workflow.

## Tooling Exceptions

- Reusable scripts or tool repos may live in `tools/` when they directly support this workflow.
- Keep tooling minimal and purpose-built; avoid general environment setup inside this workspace.

## Skills

Reusable task workflows are defined as Skills in `/Users/mt/Documents/Codex/tools/codex-skills-repo/skills/`. Before starting any task that matches a Skill's description, read the corresponding `SKILL.md` and follow its workflow exactly.

Available Skills:

- `游戏机制拆解` — 对一款游戏做系统性机制拆解并入机制库
- `产品收集` — 跨平台收集产品信息并做结构化录入
- `prompt-save-workflow` — 保存和组织 prompt 产物到本地目录
- `forevernine-material-downloader` — 下载指定来源的素材资料
- `session-router` — 所有新任务先经过 plan，再判断继续执行、委托或上下文控制
- `session-compact` — 压缩当前会话状态并写入记忆库，compact 或 clear 前必须运行

## Session Management Protocol

### 会话开始

每次会话开始时，读取 `/Users/mt/.claude/projects/-Users-mt-Documents-Codex/memory/MEMORY.md`，加载与当前任务相关的记忆。

### 强制 Plan Gate

所有新任务在执行前都必须先经过 `plan`。

规则：

- 先给出简短方案，不直接开干
- 方案至少说明目标、预计动作、涉及文件或范围、潜在风险
- 等用户审核后，才进入执行阶段
- 如果任务方向发生明显变化，重新进入 `plan`

即使任务很小，也要先给一个极简 `plan`；只是小任务的 `plan` 可以压缩成 1 到 3 句。

### 强制阶段门禁

所有任务都必须按阶段推进。

规则：

- 先确定任务类型，再选择对应流程
- 当前阶段未完成前，不得进入后续阶段
- 如果当前阶段被阻塞，停留在当前阶段解决，或 `rewind` / 重新 `plan`
- 不允许通过口头假设把“未完成”当成“已完成”

通用要求：

- 每个任务都要记录 `任务类型`
- 每个任务都要记录 `当前门禁`
- 每个任务都要记录 `已完成门禁`
- 每个任务都要记录 `下一门禁`

任务流程矩阵见：

- [`tools/codex-skills-repo/references/task-flow-matrix.md`](/Users/mt/Documents/Codex/tools/codex-skills-repo/references/task-flow-matrix.md)

### 任务管理

新任务进入执行前，必须先归类到一个流程类型：

- `analysis`：分析 / 研究 / 结论生成
- `doc-change`：文档 / 规则 / 模板修改
- `implementation`：实现 / 执行 / 产物生成
- `review`：审查 / 校对 / 验证 / 打分
- `collection`：资料收集 / 结构化录入 / 批量整理

默认要求：

- 未分类，不进入执行
- 任务类型变了，重新 `plan`
- 同一线程里多个任务并行时，每个任务单独维护自己的流程状态

### 主 Agent 与子 Agent 分工

硬规则：

- 正式 `plan` 只能由主 agent 向用户提交
- `任务类型`、`当前门禁`、`门禁切换`、`最终交付` 只能由主 agent 确认
- 子 agent 只能在被分配的作用域内工作，不能自行把任务推进到下一门禁
- 当分析会明显拉长主线程上下文时，主 agent 必须优先委派子 agent

详细分工规则见：

- [`tools/codex-skills-repo/references/agent-delegation-policy.md`](/Users/mt/Documents/Codex/tools/codex-skills-repo/references/agent-delegation-policy.md)

### 决策路由器

`plan` 获批后，每次重大步骤前，对照以下规则（首条命中即执行）：

| 条件 | 动作 |
|---|---|
| 同一问题连续失败 ≥ 3 次 | **rewind** |
| 任务方向根本性偏移（变成了新目标） | **rewind** |
| 上下文 >80% 满，或累积 ≥ 3 个失败分支 | **clear** |
| 同任务继续，上下文 >60% 满 | **compact** |
| 需要读 ≥ 3 个文件但不修改它们 | **subagent** |
| 任务产生大量中间输出，主上下文只需结论 | **subagent** |
| 验证 / 校对 / 文档生成类任务 | **subagent** |
| 以上均不符合 | **continue** |

**错误分级**（决定是 rewind 还是就地修复）：
- 逻辑层（方向错了）→ rewind
- 实现层（代码写错了）→ 就地修复
- 理解层（需求没搞清楚）→ compact 后重新澄清

### 各动作执行方式

**rewind**：停止当前线程，不在失败分支上继续堆叠。找到最后已知正确状态，从那里重新出发。

**compact**：先运行 `session-compact` skill 写入记忆，再继续。

**clear**：先运行 `session-compact` skill 保存完整状态，再清空，从记忆摘要重建。

**plan**：所有新任务的强制第一步。先给出执行方案，说明预计改动范围与风险，等用户审核后再执行。

**subagent**：委托时指定：精确问题 + 相关文件路径 + 输出格式（摘要 ≤ 300 token）。只把结论带回主上下文，不带过程。子任务也必须遵守自己的阶段门禁。

### 记忆写入规则

**强制写入时机**：任务结束时、compact / clear 前。

**即时写入时机**：发现已确认结论或关键约束时。

**禁止写入**：调试过程、失败尝试、中间输出、重复解释。

### 可用 Skills

- `session-router`：不确定走哪条路时，运行此 skill 做路由决策
- `session-compact`：compress 或 clear 前，运行此 skill 保存状态

## Game Breakdown Rules

Any time you complete a game analysis or mechanism breakdown — whether for a project knowledge base (e.g. `向僵尸开炮知识库/`) or as a standalone task — you **must also** run the `游戏机制拆解` Skill and write the results into:

```
/Users/mt/Documents/Codex/research/资料/机制库/{游戏名}/
```

The project knowledge base and the 机制库 serve different purposes and are not interchangeable:

- Project knowledge base: raw analysis, execution decisions, project-specific context
- 机制库: structured breakdown following quality standards, transferable conclusions

Completing only one of the two is not considered done. Both must be written before the task is closed.
