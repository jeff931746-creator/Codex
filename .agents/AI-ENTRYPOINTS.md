# AI Entrypoints

This file contains the concrete onboarding targets for the current workspace.

Change this file when paths, source lists, hooks, adapters, or public state locations change. Keep `.agents/AI-ONBOARDING.md` focused on rules.

## Active Workspace

Agents work only in the current checkout root: the directory containing `PROJECT.md` and `.agents/AI-ENTRYPOINTS.md`. Resolve it from the entry file location, never from a personal absolute path.

This workspace is independent. Do not read from or write to any external workspace unless the user explicitly names that target and asks to port, sync, compare, or migrate specific work.

## Required Admission Sequence

Before any non-trivial task, read and follow these sources in order:

1. `.agents/AI-ONBOARDING.md` - mandatory onboarding rules
2. `.agents/AI-ENTRYPOINTS.md` - concrete workspace entrypoints and paths
3. `PROJECT.md` - workspace scope, entry routing, session protocol, and flow intensity
4. `.agents/memory/MEMORY.md` - shared project memory index, when the task may depend on prior context
5. `.agents/rules/task-flow.md` - task types, gates, plan requirements, delegation, and hook triggers
6. `.agents/rules/quality-gates.md` - factuality, review discipline, and Git hygiene
7. `.agents/rules/workflow-chain.md` - reference/archive/workspace layers and capability lookup

Open only linked memory files needed for the current task.

## Active Rule And Memory Sources

| Purpose | Source |
|---|---|
| Mandatory AI admission rules | `.agents/AI-ONBOARDING.md` |
| Concrete workspace entrypoints and paths | `.agents/AI-ENTRYPOINTS.md` |
| Workspace entry, scope, routing, session protocol | `PROJECT.md` |
| Shared project memory | `.agents/memory/MEMORY.md` |
| Task flow, gates, plan requirements, delegation | `.agents/rules/task-flow.md` |
| Factuality, review discipline, Git hygiene | `.agents/rules/quality-gates.md` |
| Workflow layers and capability lookup | `.agents/rules/workflow-chain.md` |
| Department standards | `reference/部门标准/` |
| Planning decision authority | `reference/部门标准/策划/策划决策权规则.md` |
| Delivery writing standard | `reference/部门标准/通用/交付型文档写作标准.md` |
| Runtime hook logic and adapter examples | `.agents/hooks/`, `.agents/adapters/` |

Runtime entry files such as `AGENTS.md`, `CODEX.md`, and `CLAUDE.md` are thin pointers. Do not treat them as rule sources.

Required multi-agent authorization for project workflow gates is defined in `.agents/AI-ONBOARDING.md`.

## Runtime Entry Files

Use one of these project entries when configuring an AI runtime:

1. `AGENTS.md`
2. `.agents/AI-ONBOARDING.md`
3. `.agents/AI-ENTRYPOINTS.md`
4. Runtime-specific thin pointers such as `CODEX.md` or `CLAUDE.md`

Runtime-specific pointers must redirect here instead of copying or redefining workflow logic.

## Hook And Adapter Sources

Shared hook source:

`./.agents/hooks.json`

Context-pressure hook state:

`workspace/tmp/agent-checkpoints/<runtime>/context-pressure.json`

This is a workflow handoff brake for high context usage. It does not interrupt the current task. It requires a compact handoff before starting the next task when context remains above the threshold, but it does not make any runtime or desktop app auto-compact.

Runtime adapter examples:

- `.agents/adapters/codex-hooks.json`
- `.agents/adapters/claude-hooks.json`
- `.agents/adapters/README.md`

Hook support gives physical blocking. Without hook support, `.agents/AI-ONBOARDING.md` and this file remain mandatory, but enforcement is procedural.

## Public Project State Locations

Use these public project locations for project-visible state:

- `.agents/memory/`
- `.agents/rules/`
- `workspace/tmp/agent-checkpoints/<runtime>/`

Runtime-private directories may contain runtime internals only, never project source-of-truth state.

Private runtime paths include:

- `.claude/`
- `.codex/`
- `.cursor/`
- `.gemini/`
- `.continue/`
- `.aider/`
- `~/.claude/`
- `~/.codex/`
- any equivalent runtime-private directory

## File Safety Guard

Before any shell command or script that creates, edits, moves, deletes, formats, or syncs files, run this guard when target paths are known:

```text
python tools/workspace-guard/check_paths.py <path> [...]
```

For patch-based edits, inspect patch targets directly and ensure they are inside `the current checkout root`.

## Windows And Relocation

Run commands from the checkout root with Python 3.10+ (`python -X utf8`). The guard derives its root from its own file and allows only that checkout plus OS temporary directories. `AGENT_WORKSPACE` is an internal adapter override, not permission to access another project.

Checked-in hook JSON files use checkout-relative commands. Generate absolute local commands with `python tools/windows/bootstrap.py --runtime codex` (or `claude`) before connecting runtime hooks. Regenerate after moving the checkout or changing Python. Generated files live under `workspace/tmp/runtime-config/`, not runtime-private state. See `docs/windows.md` for native Windows entrypoints and remaining platform-specific tools.
