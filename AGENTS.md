# AGENTS.md - agent entry pointer

This file intentionally does not define workflow rules.

Any AI agent working in this project must first read `.agents/AI-ONBOARDING.md`, then read `.agents/AI-ENTRYPOINTS.md` for the concrete active source list.

## Active Workspace

The active workspace is listed in `.agents/AI-ENTRYPOINTS.md`.

## Active Rule Sources

Before any non-trivial task in this workspace, read and follow:

1. `.agents/AI-ONBOARDING.md` - mandatory admission contract for any AI runtime
2. `.agents/AI-ENTRYPOINTS.md` - concrete active source list, paths, hooks, adapters, and public state locations

The active rule and memory sources are listed in `.agents/AI-ENTRYPOINTS.md`. Runtime entry files such as `CODEX.md` and `CLAUDE.md` are thin pointers, not rule sources.

## Runtime Private State

Any AI runtime may keep its own internal logs, caches, transcripts, or local continuation state in its private runtime directory.

No AI runtime may store project source-of-truth rules, shared memory, task state, checkpoints, or handoff notes in a runtime-private directory.

Use the project-visible state locations listed in `.agents/AI-ENTRYPOINTS.md`.

## File Safety

Before any shell command or script that creates, edits, moves, deletes, formats, or syncs files, run the path guard when the target path is known:

See `.agents/AI-ENTRYPOINTS.md` for the current guard command.

For `apply_patch`, inspect patch targets directly and ensure they are inside the intended workspace.
