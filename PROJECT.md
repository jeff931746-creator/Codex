# Project Agent Rules

This workspace is an independent workflow workspace.

The active workflow rules are agent-neutral. They apply to any AI agent working in this project, including Codex, Claude, or another assistant.

## Scope

- Keep only files, scripts, notes, research, prompts, and tools that directly support the active workflow.
- Prefer: `workspace/projects/`, `workspace/playground/`, `workspace/tmp/`.
- `workspace/tmp/` is scratch; remove artifacts after use when appropriate.
- Reusable scripts live in `archive/tools/`.
- `reference/` is the core knowledge base; do not modify files there without explicit user permission.
- `archive/` holds accumulated methods and tools.
- `reference/` holds stable standards and research.
- Do not use any external workspace as an implicit dependency. Read from or write to one only when the user explicitly names that target and asks to port, sync, compare, or migrate specific work.
- Use the local workspace guard before file-changing shell commands when the target path is known: `bash /Users/mt/Documents/Codex-codex-work/tools/workspace-guard/check-paths.sh <path> [...]`.

## Active Rule Sources

Use `.agents/AI-ENTRYPOINTS.md` as the concrete index for active rule sources, memory sources, paths, hook sources, adapter examples, and public state locations.

Runtime entry files such as `CODEX.md` and `CLAUDE.md` are thin pointers. Do not treat them as rule sources.

## Skills

Use `archive/skills/skills/` as the project-local skill source when applicable. Read the corresponding `SKILL.md` and follow its workflow, while also following the current runtime's skill instructions.

### Entry Selection

Check this table before selecting a project-local skill. Stop at the first matching row; do not trigger multiple entries at once.

| Scenario | Entry | Do not |
|---|---|---|
| Analyze a game, break down mechanics, research competitors, or add game breakdowns to project knowledge | `游戏机制拆解` | Do not bypass the skill with free-form analysis |
| Collect competitor or product information across platforms | `产品收集` | Do not invent fields before confirming schema |
| Download Forevernine source materials | `forevernine-material-downloader` | Do not process items manually one by one |
| Evaluate ad-buying material combinations | `买量组合评估` | Do not skip evidence chains and give subjective scores |
| Write a feature GDD | `gdd-write` | Do not output the full document directly; confirm step by step |
| Review or self-review a GDD, feature design document, system design, gameplay/design proposal, or "case/案子" for a game feature | `gdd-review` | Do not perform informal inline review; do not let system-planning, numeric, or project-initiation standards replace the GDD standard |
| Determine task flow intensity | `.agents/rules/task-flow.md` | Do not execute complex tasks without routing |
| Before compact or clear | `.agents/memory/` plus current runtime memory protocol | Do not compress before preserving important constraints |
| Resume an existing task | `.agents/memory/` plus current runtime memory protocol | Do not infer state only from another runtime's private memory |
| Final delivery check | `.agents/rules/quality-gates.md` | Do not provide only a summary when gates must be checked |

## Session Management Protocol

### Session Start

At the start of a non-trivial task:

1. Read `.agents/AI-ONBOARDING.md`.
2. Read `.agents/AI-ENTRYPOINTS.md`.
3. Follow the required admission sequence listed in `.agents/AI-ENTRYPOINTS.md`.
4. Use the current runtime's memory instructions for runtime-level continuation when required.
5. Do not read or write another runtime's private memory as active project memory.
6. If continuing an existing task, identify the current task state from public project memory, current-runtime memory, user context, or workspace files.

### Flow Intensity

| Intensity | Use When | Requirement |
|---|---|---|
| `quick` | Single-step answer, one fact, small judgment with no file edits | Give the conclusion directly; state assumptions briefly if needed |
| `standard` | General analysis, local document edits, small code/script changes | Give a minimal plan or work note before execution |
| `strict` | New project, cross-file change, deployment, or changes affecting long-term workflow/rules/skills | Provide a full plan with goal, scope, risk, and validation; wait for user approval |

Hard rules:

- `strict` tasks must not skip planning.
- Re-plan when task direction changes materially.
- When changing standards, first define the new standard, then execute according to it.
- High-risk governance work remains a draft until the user confirms it as authoritative.

### Decision Router

- Read-heavy, analysis-heavy, or verification-heavy work -> delegate or parallelize when possible.
- Repeated failure or direction drift -> rewind to the correct gate and re-plan.
- Context pressure -> compact using the current runtime's memory protocol.
- Logic-layer error -> rewind.
- Implementation-layer error -> fix in place after understanding the cause.
- Understanding-layer error -> clarify or compact and restate assumptions.

### Memory Write Rules

`.agents/memory/` is the durable project memory source. Runtime memory is a local continuation mechanism, not the project source of truth.

- Write durable project memory only when explicitly asked by the user, or when project rules require a public handoff before compact/clear/resume.
- Important completed tasks, long-term constraints, compact/clear handoffs, and confirmed task state should be preserved in `.agents/memory/` when they must survive across runtimes.
- Follow the current runtime's memory instructions for runtime-local continuation when needed.
- Do not store debugging noise, failed attempts, intermediate scratch output, or repeated explanations as durable memory.
- Preserve important constraints in the final response when they affect future work.
- Do not write another runtime's private memory files.
- Do not write project rules, project memory, task state, checkpoints, or handoff notes to `.claude/`, `.codex/`, `/Users/mt/.claude/`, `/Users/mt/.codex/`, or any equivalent runtime-private state directory. Runtime-private locations may contain runtime internals only, never project source-of-truth state.
