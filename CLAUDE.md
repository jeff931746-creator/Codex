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

用户目标优先于技术偏好；系统承载复杂度，可见交互保持简单；重复工作变自动化；规则的价值是减少决策，不是增加流程。

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

以 `archive/skills/skills/` 为准，读对应 `SKILL.md` 并按其工作流执行。

### 入口选择

先查这张表再选 Skill。命中第一行即停，不要同时触发多个入口。

| 场景 | 入口 | 不要做什么 |
|---|---|---|
| 对一款游戏做分析 / 机制拆解 / 竞品研究，或项目知识库内有游戏拆解需入库 | `游戏机制拆解` | 不要直接写分析绕过 Skill，机制库需要标准化结构 |
| 跨平台收集竞品 / 产品信息 | `产品收集` | 不要自定义字段后录入，schema 必须先确认 |
| 下载 Forevernine 指定来源素材 | `forevernine-material-downloader` | 不要手动逐个处理 |
| 评估买量素材组合 | `买量组合评估` | 不要跳过证据链给主观评分 |
| 写一份功能需求 GDD | `gdd-write` | 不要直接输出完整文档，应逐步确认每一步 |
| 审核 / Self-Review 一份 GDD | `gdd-review` | 不要内联审核，设计文档审核必须走 Skill |
| 判断当前任务流程强度 | `session-router` | 不要直接执行跳过路由判断 |
| compact 或 clear 前 | `session-compact` | 不要先压缩再补写记忆，顺序不能反 |
| 新会话续接已有任务 | `session-resume` | 不要从 MEMORY.md 手动推断状态 |
| 任务交付前收尾检查 | `neat-freak` | 不要只写交付摘要，门禁需要逐项确认 |

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
| Hook 触发表 | `.claude/rules/hook-table.md` |
| 子 agent 模型默认配置 | `.claude/rules/model-defaults.md` |

### 流程强度分级

| 任务强度 | 适用场景 | 流程要求 |
|---|---|---|
| `quick` | 单步问答、查一个事实、无文件改动的小判断 | 直接给结论；必要时用 1 句说明假设 |
| `standard` | 一般分析、局部文档修改、小范围代码或脚本调整 | 先给极简 `plan`，获批后执行 |
| `strict` | 新项目、跨文件改动、部署、会影响长期工作流的规则或 Skill | 必须完整 `plan`，说明目标、范围、风险、验证方式，获批后执行 |

硬规则：`strict` 任务不得跳过 `plan`。任务方向明显变化时重新 `plan`。调整规范时先改文档，再按新规范执行。详细阶段门禁和任务类型见 `.claude/rules/task-flow-matrix.md`，Agent 分工见 `.claude/rules/agent-delegation-policy.md`。

### 决策路由器

读密集 / 分析 / 验证类 → **subagent**；连续失败 / 方向偏移 → **rewind**；上下文 >60% → **clear**；>30% → **compact**；否则 **continue**。错误分级：逻辑层 → rewind；实现层 → 就地修复；理解层 → compact 后重新澄清。完整触发条件见 `plan-and-hook-model.md`。

### 记忆写入规则

- **强制写入**：重要任务结束时、形成长期约束时、compact / clear 前
- **即时写入**：发现已确认结论或关键约束时
- **禁止写入**：调试过程、失败尝试、中间输出、重复解释

### 任务收尾门禁

有文件 / 规则 / 记忆变更，或重要分析结束时，交付前运行 `neat-freak` Skill。

## Development Rules

- 代码或脚本改动后，必须跑验证（test / lint / smoke check）再交付。语法通过不等于验证完成。
- 不得注释掉失败代码来让运行通过。找根因或明确报告阻塞。
- Secrets、token、密码、私钥不得进入源文件、日志、提交或共享文档。
- 优先使用项目已有命令和本地约定。

## Git And Deployment

- Commit messages 必须使用中文，并概括本次提交包含的所有主要改动。
- 不自动运行 `git push`。只在用户明确要求时 push。
- 部署按项目自身文档的命令执行，不把 `git push` 当部署。

