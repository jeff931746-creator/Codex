# Workspace Rules

This workspace is for workflow-related assets only.

## Collaboration Defaults

- Default to Chinese for discussion; keep code, commands, filenames, and identifiers in English unless the local project uses another convention.
- Lead with the conclusion, then give reasons.
- Explain technical decisions in terms of `why` and user impact, not only implementation details.
- Do not flatter or over-agree. If a direction is weak, say so directly and offer the better path.
- When requirements are vague, choose the most reasonable path first and name the assumption.
- Do not ask for confirmation just to be polite. Ask only when the action is high-impact, destructive, irreversible, or outside the agreed scope.

## Operating Principles

- User experience outranks technical preference.
- Design for the user's goal, not for feature inventory.
- Let the system carry complexity: automate repeated work, infer safe defaults, keep visible interaction simple.
- Use progressive disclosure: essential result first, details when useful.
- Feedback should guide the next action: "what happened + what to do next" over raw error reporting.
- Repeated work should become automation.
- Rules exist to reduce repeated decisions; use the smallest process that still preserves safety.

## Scope

- Keep only files, scripts, notes, research, prompts, and tools that directly support the active workflow.
- Prefer: `workspace/projects/`, `workspace/playground/`, `workspace/tmp/`.
- `reference/` is the core knowledge base — AI must not modify files here without explicit user permission.
- `archive/` holds accumulated methods and tools. `reference/` holds stable standards and research.

## Software And Runtime Policy

- Do not install software into this workspace by default.
- If a task can be completed with existing system tools, prefer that path.
- If new software appears necessary, stop and ask before installing.

## Cleanup

- `tmp/` is scratch space. Remove temporary artifacts after use.
- Reusable scripts or tool repos live in `archive/tools/`.

## Skills

Reusable task workflows are defined as Skills in `/Users/mt/Documents/Codex/archive/skills/skills/`. Before starting any task that matches a Skill's description, read the corresponding `SKILL.md` and follow its workflow exactly.

Available Skills:

- `游戏机制拆解` — 对一款游戏做系统性机制拆解并入机制库
- `产品收集` — 跨平台收集产品信息并做结构化录入
- `forevernine-material-downloader` — 下载指定来源的素材资料
- `买量组合评估` — 评估买量素材组合的蓝海度、可玩性与 IAP 变现潜力
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
| 自动 Hooks | `.claude/hooks/` |
| 任务流程矩阵 | `.claude/rules/task-flow-matrix.md` |
| Agent 委派规则 | `.claude/rules/agent-delegation-policy.md` |
| 记忆文件 | `/Users/mt/.claude/projects/-Users-mt-Documents-Codex/memory/` |
| 工作流链路规则 | `.claude/rules/workflow-chain.md` |
| Git 卫生规则 | `.claude/rules/git-hygiene.md` |
| API 调用规则 | `.claude/rules/api-client-architecture.md` |
| LLM 事实性信息处理 | `.claude/rules/llm-fact-checking.md` |
| 部门标准 | `reference/部门标准/` |

### 流程强度分级

| 任务强度 | 适用场景 | 流程要求 |
|---|---|---|
| `quick` | 单步问答、查一个事实、无文件改动的小判断 | 直接给结论；必要时用 1 句说明假设 |
| `standard` | 一般分析、局部文档修改、小范围代码或脚本调整 | 先给极简 `plan`，获批后执行 |
| `strict` | 新项目、跨文件改动、部署、会影响长期工作流的规则或 Skill | 必须完整 `plan`，说明目标、范围、风险、验证方式，获批后执行 |

硬规则：`strict` 任务不得跳过 `plan`。任务方向明显变化时重新 `plan`。调整规范时先改文档，再按新规范执行。详细阶段门禁和任务类型见 `.claude/rules/task-flow-matrix.md`，Agent 分工见 `.claude/rules/agent-delegation-policy.md`。

### 决策路由器

`plan` 获批后，每次重大步骤前按顺序匹配（命中第一条即执行）：

| 条件 | 动作 |
|---|---|
| 游戏分析 / 立项推演 / 竞品对比类任务 | **subagent** |
| 需要读 ≥ 3 个文件但不修改它们 | **subagent** |
| 任务产生大量中间输出，主上下文只需结论 | **subagent** |
| 验证 / 校对 / 文档生成类任务 | **subagent** |
| 同一问题连续失败 ≥ 3 次 | **rewind** |
| 任务方向根本性偏移 | **rewind** |
| 上下文 >60% 满，或累积 ≥ 3 个失败分支 | **clear** |
| 同任务继续，上下文 >30% 满 | **compact** |
| 以上均不符合 | **continue** |

错误分级：逻辑层（方向错了）→ rewind；实现层（代码写错了）→ 就地修复；理解层（需求没搞清楚）→ compact 后重新澄清。

### 记忆写入规则

- **强制写入**：重要任务结束时、形成长期约束时、compact / clear 前
- **即时写入**：发现已确认结论或关键约束时
- **禁止写入**：调试过程、失败尝试、中间输出、重复解释

### 框架沉淀硬规则

主对话中达成下列任一类共识时，**必须在继续下一步工作前**沉淀到 `reference/` 或 `archive/方法论`：

- 新的概念框架（公分母、第一性维度、基础结构）
- 第一性推演结论（从底层重新论证后的维度定义、易混判据）
- 跨任务复用的判据 / 方法
- 用户多次反复纠正后形成的定义
- 新建的层次结构 / 接口规则

| 类型 | 位置 |
|---|---|
| 标准 / 规则 / 字段定义 | `reference/部门标准/` |
| 方法论 / 推导过程 / 判据集 | `archive/方法论/` |

❌ 禁止：先做事、事后再沉淀。框架必须先于数据存在。用户问"沉淀了吗"才补写意味着系统失职。

### 三位一体框架引用规则

引用 `reference/部门标准/立项/三位一体框架/` 下任何标准时：

- **必须从 `current/` 读取**：`reference/部门标准/立项/三位一体框架/current/{标准名}.md`
- **禁止裸路径**（升级后路径失效）
- **`history/` 仅作历史追溯**，不在业务流程或 Skill 中引用

修订时：复制到 `history/{标准名}/v{X}_{日期}.md` → 覆盖 `current/` → 更新 yaml 元数据 → 更新 README 索引。

### 任务收尾门禁

文档 / 规则 / 代码 / Skill / 记忆有变更，或重要分析结束，交付前运行 `neat-freak` Skill。边界：不是全仓库清理命令，不替代测试 / `session-compact`。

## Development Rules

- 代码或脚本改动后，必须跑验证（test / lint / smoke check）再交付。语法通过不等于验证完成。
- 不得注释掉失败代码来让运行通过。找根因或明确报告阻塞。
- Secrets、token、密码、私钥不得进入源文件、日志、提交或共享文档。
- 优先使用项目已有命令和本地约定。

## Git And Deployment

- Commit messages 必须使用中文，并概括本次提交包含的所有主要改动。
- 不自动运行 `git push`。只在用户明确要求时 push。
- 部署按项目自身文档的命令执行，不把 `git push` 当部署。

---

## Game Breakdown Rules

Any time you complete a game analysis or mechanism breakdown — whether for a project knowledge base (e.g. `向僵尸开炮知识库/`) or as a standalone task — you **must also** run the `游戏机制拆解` Skill and write the results into:

```
/Users/mt/Documents/Codex/archive/资料/机制库/{游戏名}/
```

The project knowledge base and the 机制库 serve different purposes and are not interchangeable. Completing only one of the two is not considered done.
