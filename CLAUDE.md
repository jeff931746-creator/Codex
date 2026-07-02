# CLAUDE.md - Claude entry pointer

This file is a Claude runtime entry pointer. It intentionally does not define project workflow rules.

Claude must first read `.agents/AI-ONBOARDING.md`, then use the agent-neutral project rule sources:

1. `.agents/AI-ONBOARDING.md`
2. `.agents/AI-ENTRYPOINTS.md`

`.agents/AI-ENTRYPOINTS.md` lists the concrete active source files, hook sources, adapters, public state locations, and file safety guard.

Runtime-specific hook configuration, if needed, should point to the hook or adapter source listed there. It is not the source of truth for project rules.

Claude must not write project memory, rules, task state, checkpoints, or handoff notes to runtime-private state directories. Use the project-visible state locations listed in `.agents/AI-ENTRYPOINTS.md`.
