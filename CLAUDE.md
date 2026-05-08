# Workspace Rules

This workspace is for workflow-related assets only.

## Collaboration Defaults

- Default to Chinese for discussion; keep code, commands, filenames, and identifiers in English unless the local project uses another convention.
- Lead with the conclusion, then give reasons. Avoid long background setup unless the task requires it.
- Explain technical decisions in terms of `why` and user impact, not only implementation details.
- Do not flatter, over-agree, or label ideas as good by default. If a direction is weak, say so directly and offer the better path.
- When requirements are vague, choose the most reasonable path first and name the assumption. Ask a question only when guessing would create real risk.
- Do not ask for confirmation just to be polite. Ask only when the action is high-impact, destructive, irreversible, or outside the agreed scope.

## Operating Principles

- User experience outranks technical preference. This applies to GUI, CLI, conversational flows, Skills, docs, and system feedback.
- Design for the user's goal, not for feature inventory. Add only the controls, outputs, or automation that help the user finish the job.
- Let the system carry complexity: automate repeated work, infer safe defaults, and keep the visible interaction simple.
- Use progressive disclosure: show the essential result first, then expose details when they are useful.
- Feedback should guide the next action. Prefer "what happened + what I am doing / what you can do next" over raw error reporting.
- Repeated work should become automation. If a task has been done three times, consider whether it should become a script, Skill, template, or workflow.
- Rules exist to reduce repeated decisions and protect quality; they are not the goal. When process cost is clearly higher than task value, use the smallest process that still preserves safety and traceability.

## Scope

- Keep only files, scripts, notes, research, prompts, and tools that directly support the active workflow.
- Prefer placing work in the existing top-level folders: `workspace/projects/`, `workspace/playground/`, and `workspace/tmp/`.
- `reference/` is the core knowledge base — AI must not modify files here without explicit user permission.
- `archive/` holds accumulated methods and tools. `reference/` holds stable standards and research.

## Software And Runtime Policy

- Do not install software into this workspace by default.
- Do not add local runtimes, SDKs, package manager globals, app installers, or downloaded binary bundles under this workspace unless the user explicitly approves them as workflow-critical.
- If a task can be completed with existing system tools or already-available dependencies, prefer that path.
- If new software appears necessary, stop and ask before installing, downloading, or vendoring it into the workspace.

## Cleanup Expectations

- Treat `tmp/` as scratch space for temporary artifacts.
- Remove temporary installers, caches, extracted runtimes, and other non-workflow files after use unless the user explicitly asks to keep them.
- Avoid leaving behind large support files that are not part of the existing workflow.

## Tooling Exceptions

- Reusable scripts or tool repos live in `archive/tools/` when they directly support this workflow.
- Keep tooling minimal and purpose-built; avoid general environment setup inside this workspace.

## Skills

Reusable task workflows are defined as Skills in `/Users/mt/Documents/Codex/archive/skills/skills/`. Before starting any task that matches a Skill's description, read the corresponding `SKILL.md` and follow its workflow exactly.

Available Skills:

- `游戏机制拆解` — 对一款游戏做系统性机制拆解并入机制库
- `产品收集` — 跨平台收集产品信息并做结构化录入
- `prompt-save-workflow` — 保存和组织 prompt 产物到本地目录
- `forevernine-material-downloader` — 下载指定来源的素材资料
- `session-router` — 按 `quick` / `standard` / `strict` 判断流程强度，再决定是否 plan、继续执行、委托或上下文控制
- `session-compact` — 压缩当前会话状态并写入记忆库，compact 或 clear 前必须运行
- `session-resume` — 新会话开始时恢复指定任务的上下文，让对话从正确状态继续
- `neat-freak` — 任务结束前的轻量收尾门禁，对齐改动、文档、规则、记忆和交付摘要

## Session Management Protocol

### 会话开始

每次会话开始时，读取 `/Users/mt/.claude/projects/-Users-mt-Documents-Codex/memory/MEMORY.md`，加载与当前任务相关的记忆。如果是续接已有任务，读完 MEMORY.md 后立即运行 `session-resume {任务名}`。

### 资料导航

| 需要什么 | 去哪里找 |
|---|---|
| 任务当前状态 | `memory/task_{任务名}.md` → 运行 `session-resume` |
| 活跃任务列表 | `/Users/mt/.claude/projects/-Users-mt-Documents-Codex/memory/MEMORY.md` |
| 可用 Skills | `archive/skills/skills/` |
| 自动 Hooks | `.claude/hooks/`（git commit 中文检查、危险命令拦截、Stop 状态播报） |
| 任务流程矩阵 | `archive/skills/references/task-flow-matrix.md` |
| Agent 委派规则 | `archive/skills/references/agent-delegation-policy.md` |
| 记忆文件 | `/Users/mt/.claude/projects/-Users-mt-Documents-Codex/memory/` |
| 工作流链路规则 | `.claude/rules/workflow-chain.md` |
| 部门标准 | `reference/部门标准/` |

### 流程强度分级

先判断任务强度，再选择流程重量。默认使用能保证质量的最小流程。

| 任务强度 | 适用场景 | 流程要求 |
|---|---|---|
| `quick` | 单步问答、查一个事实、轻量说明、无文件改动的小判断 | 可以直接给结论；必要时用 1 句说明假设 |
| `standard` | 一般分析、局部文档修改、小范围代码或脚本调整 | 先给极简 `plan`，获批后执行 |
| `strict` | 新项目、新目录结构、跨文件改动、部署、自动化、会影响长期工作流的规则或 Skill | 必须完整 `plan`，说明目标、范围、风险、验证方式，获批后执行 |

硬规则：

- `strict` 任务不得跳过 `plan`。
- 如果任务方向发生明显变化，重新进入 `plan`。
- 如果用户明确说“直接做 / 继续 / 修掉 / 跑一下”，且任务不是高风险，可以把 `plan` 压缩为一句执行说明后继续。
- 需要调整既有规范时，先改文档，再按新规范执行；不要先实践、后补规则。

### 约束先行

新项目、新目录、长期工具、复用脚本、知识库结构和跨团队工作流，开始前必须先有规则：

- 新项目先写项目级 `CLAUDE.md` 或等效规则文件。
- 新目录先说明结构约定：什么放哪、怎么命名、何时清理。
- 已有规范的项目，严格遵守更深层目录中的 `CLAUDE.md` / `AGENTS.md` / README 约定。
- 小任务不为了形式创建规则文件；只在会重复、会扩展、会被他人或未来自己复用时固化规则。

### 阶段门禁

`standard` 和 `strict` 任务按阶段推进；`quick` 任务可只保留轻量状态判断。

通用记录：

- 每个任务都要记录 `任务类型`
- 每个任务都要记录 `当前门禁`
- 每个任务都要记录 `已完成门禁`
- 每个任务都要记录 `下一门禁`

规则：

- 当前阶段未完成前，不得进入后续阶段。
- 如果当前阶段被阻塞，停留在当前阶段解决，或 `rewind` / 重新 `plan`。
- 不允许通过口头假设把“未完成”当成“已完成”。

任务流程矩阵见：

- [`archive/skills/references/task-flow-matrix.md`](/Users/mt/Documents/Codex/archive/skills/references/task-flow-matrix.md)

### 任务管理

`standard` 和 `strict` 任务进入执行前，必须先归类到一个流程类型：

- `analysis`：分析 / 研究 / 结论生成
- `doc-change`：文档 / 规则 / 模板修改
- `implementation`：实现 / 执行 / 产物生成
- `review`：审查 / 校对 / 验证 / 打分
- `collection`：资料收集 / 结构化录入 / 批量整理

默认要求：

- 需要阶段化推进的任务，未分类不进入执行
- 任务类型变了，重新 `plan`
- 同一线程里多个任务并行时，每个任务单独维护自己的流程状态

### 主 Agent 与子 Agent 分工

硬规则：

- 正式 `plan` 只能由主 agent 向用户提交
- `任务类型`、`当前门禁`、`门禁切换`、`最终交付` 只能由主 agent 确认
- 子 agent 只能在被分配的作用域内工作，不能自行把任务推进到下一门禁
- 当分析会明显拉长主线程上下文时，主 agent 必须优先委派子 agent

详细分工规则见：

- [`archive/skills/references/agent-delegation-policy.md`](/Users/mt/Documents/Codex/archive/skills/references/agent-delegation-policy.md)

### 决策路由器

`standard` 和 `strict` 任务在 `plan` 获批后，每次重大步骤前，对照以下规则（按从上到下顺序匹配，命中第一条规则即执行对应动作）：

| 条件 | 动作 |
|---|---|
| 游戏分析 / 立项推演 / 竞品对比类任务 | **subagent** |
| 需要读 ≥ 3 个文件但不修改它们 | **subagent** |
| 任务产生大量中间输出，主上下文只需结论 | **subagent** |
| 验证 / 校对 / 文档生成类任务 | **subagent** |
| 同一问题连续失败 ≥ 3 次 | **rewind** |
| 任务方向根本性偏移（变成了新目标） | **rewind** |
| 上下文 >80% 满，或累积 ≥ 3 个失败分支 | **clear** |
| 同任务继续，上下文 >60% 满 | **compact** |
| 以上均不符合 | **continue** |

**错误分级**（决定是 rewind 还是就地修复）：
- 逻辑层（方向错了）→ rewind
- 实现层（代码写错了）→ 就地修复
- 理解层（需求没搞清楚）→ compact 后重新澄清

### 各动作执行方式

**rewind**：停止当前线程，不在失败分支上继续堆叠。找到最后已知正确状态，从那里重新出发。

**compact**：先运行 `session-compact` skill 写入记忆，再继续。

**clear**：先运行 `session-compact` skill 保存完整状态，再清空，从记忆摘要重建。

**plan**：`standard` / `strict` 任务的正式起点。先给出执行方案，说明预计改动范围与风险，等用户审核后再执行。`quick` 任务可以直接回答或用一句话说明假设。

**subagent**：委托时指定：精确问题 + 相关文件路径 + 输出格式（摘要 ≤ 300 token）。只把结论带回主上下文，不带过程。子任务也必须遵守自己的阶段门禁。

### 记忆写入规则

**强制写入时机**：重要任务结束时、形成长期约束时、compact / clear 前。

**即时写入时机**：发现已确认结论或关键约束时。

**禁止写入**：调试过程、失败尝试、中间输出、重复解释。

### 任务收尾门禁

重要任务交付前运行 `neat-freak` Skill 做轻量收尾检查。

触发场景：

- 文档、规则、代码、脚本、Skill、目录结构或记忆发生变更。
- 重要分析 / 研究任务结束，并形成长期结论。
- 任务产出了可交付文件、测试 / 评估产物或后续会复用的工作流。

检查内容：

- 回看本轮实际改动，区分用户原有改动和本轮改动。
- 判断 README、`AGENTS.md` / `CLAUDE.md`、Skill、catalog 或记忆是否需要同步。
- 检查 `.DS_Store`、缓存、临时下载、测试 / 评估产物混放等待清理项。
- 最终回复给出简短变更摘要、验证结果和待处理项。

边界：

- `neat-freak` 是收尾质量门禁，不是全仓库清理命令。
- 不自动删除用户未确认的文件。
- 不替代任务本身的测试、lint、build、smoke check，也不替代 `session-compact`。

## Development Rules

- After code or script changes, run the relevant validation when feasible: test, lint, build, smoke check, or a focused command that proves the change works.
- Do not comment out failing code just to make the run pass. Find the root cause or clearly report the blocker.
- Secrets, tokens, passwords, and private keys must not enter source files, logs, commits, or shared docs.
- Prefer existing project commands and local conventions over inventing new tooling.

## Git And Deployment

- Commit messages must be written in Chinese and must summarize all meaningful changes included in the commit, not only the main intent.
- Do not run `git push` automatically. Use push only when the user asks, typically for cross-device sync.
- Deployment follows the project's own documented command. Do not treat `git push` as deployment unless the project explicitly says so.

### 可用 Skills

- `session-router`：不确定走哪条路时，运行此 skill 做路由决策
- `session-compact`：compress 或 clear 前，运行此 skill 保存状态
- `session-resume`：续接已有任务时，运行此 skill 恢复任务上下文
- `neat-freak`：重要任务交付前，运行此 skill 做轻量收尾检查

---

## Game Breakdown Rules

Any time you complete a game analysis or mechanism breakdown — whether for a project knowledge base (e.g. `向僵尸开炮知识库/`) or as a standalone task — you **must also** run the `游戏机制拆解` Skill and write the results into:

```
/Users/mt/Documents/Codex/reference/资料/机制库/{游戏名}/
```

The project knowledge base and the 机制库 serve different purposes and are not interchangeable:

- Project knowledge base: raw analysis, execution decisions, project-specific context
- 机制库: structured breakdown following quality standards, transferable conclusions

Completing only one of the two is not considered done. Both must be written before the task is closed.
