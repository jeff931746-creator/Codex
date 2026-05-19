# Workspace Rules

This workspace is for workflow-related assets only.
These rules apply repo-wide unless a deeper folder explicitly narrows them.

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
- Prefer placing execution work in the existing `workspace/` folders: `workspace/projects/`, `workspace/playground/`, and `workspace/tmp/`.
- Put reusable materials, methods, mechanism studies, and structured external data under `archive/`.
- Treat `reference/` as the stable rule and template layer; do not modify it without explicit user permission.
- Do not create or write new workflow assets under `research/`; it is ignored local/deprecated space, not a canonical knowledge base.

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

## Claude Rule Boundary

`.claude/` and `/Users/mt/.claude/` are Claude-owned rule, hook, worktree, and memory sources.

Codex may:

- read relevant `.claude` rules and memory when required by this workspace protocol
- summarize those rules into the current task context
- follow compatible rules during execution

Codex must not:

- create, edit, move, delete, format, sync, or indirectly mutate files under `.claude/` or `/Users/mt/.claude/`
- update Claude hooks, Claude settings, Claude worktrees, or Claude memory directly
- treat `.claude` as a writable Codex state store

Claude may continue to own and modify those paths. If Codex needs a rule or memory change that belongs to Claude, it must propose the change in conversation; it must not create a parallel Codex-side rule source.

Before Codex runs a shell command or script intended to create, edit, move, delete, format, or sync files, pass the known target paths through:

```bash
bash /Users/mt/Documents/Codex/tools/codex-guard/check-paths.sh <path> [...]
```

For `apply_patch`, Codex must inspect the patch targets directly and must not include protected `.claude` paths.

## Skills

Reusable task workflows are defined as Skills in `/Users/mt/Documents/Codex/archive/skills/skills/`. Before starting any task that matches a Skill's description, read the corresponding `SKILL.md` and follow its workflow exactly.

Legacy references to `/Users/mt/Documents/Codex/tools/repos/codex-skills-repo/` or `/Users/mt/Documents/Codex/tools/codex-skills-repo/` are stale. Do not rely on those paths unless they are restored in the working tree.

Available Skills:

- `游戏机制拆解` — 对一款游戏做系统性机制拆解并入机制库
- `产品收集` — 跨平台收集产品信息并做结构化录入
- `prompt-save-workflow` — 保存和组织 prompt 产物到本地目录
- `forevernine-material-downloader` — 下载指定来源的素材资料
- `session-router` — 按 `quick` / `standard` / `strict` 判断流程强度，再决定是否 plan、继续执行、委托或上下文控制
- `session-compact` — 压缩当前会话状态并写入记忆库，compact 或 clear 前必须运行
- `neat-freak` — 任务结束前的轻量收尾门禁，对齐改动、文档、规则、记忆和交付摘要

## Claude Rule Consumption Protocol

Claude is the only author of workflow rules for this workspace. Codex must treat Claude-owned rules as authoritative read-only sources, not copy or redefine them in `AGENTS.md`.

Before Codex performs any non-trivial task, and before the first mutating tool call in a turn, Codex must read the relevant Claude rule and memory sources:

- `/Users/mt/.claude/projects/-Users-mt-Documents-Codex/memory/MEMORY.md`
- `/Users/mt/Documents/Codex/.claude/rules/workflow-chain.md`
- `/Users/mt/Documents/Codex/.claude/rules/task-flow-matrix.md`
- `/Users/mt/Documents/Codex/.claude/rules/agent-delegation-policy.md`

Codex must then execute the task according to those Claude-defined flow gates, task types, routing rules, memory rules, and closeout expectations where compatible with Codex system and developer instructions. If a Claude rule conflicts with higher-priority Codex runtime rules, Codex must follow the higher-priority rule and explicitly report the deviation.

Codex-specific files may define only adapters and guards, such as:

- read-only protection for `.claude/`
- checks that Claude rule intake happened before mutation
- Codex tool compatibility notes
- non-Claude storage locations for temporary hook state

Codex must not create a parallel workflow source of truth in `AGENTS.md`, Codex Skills, or workspace docs. Any durable workflow rule change belongs to Claude and must be proposed to the user or authored by Claude in `.claude/`.

Codex must not run Claude checkpoint scripts that write under `.claude/`. When Claude closeout requires such a checkpoint, Codex should run the compatible review/check steps, skip the `.claude` write, and report that boundary.

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
- `neat-freak`：重要任务交付前，运行此 skill 做轻量收尾检查

## Game Breakdown Rules

Any time you complete a game analysis or mechanism breakdown — whether for a project knowledge base (e.g. `向僵尸开炮知识库/`) or as a standalone task — you **must also** run the `游戏机制拆解` Skill and write the results into:

```
/Users/mt/Documents/Codex/archive/资料/机制库/{游戏名}/
```

The project knowledge base and the 机制库 serve different purposes and are not interchangeable:

- Project knowledge base: raw analysis, execution decisions, project-specific context
- 机制库: structured breakdown following quality standards, transferable conclusions

Completing only one of the two is not considered done. Both must be written before the task is closed.
