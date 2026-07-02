# AI Onboarding Contract

This is the mandatory onboarding contract for any AI agent working in this workspace.

It applies before task execution, tool use, file edits, memory writes, or handoff work.

## Rule Layer Boundary

This file defines mandatory onboarding rules only.

Concrete workspace paths, required source files, public state locations, runtime adapter files, and guard commands live in `.agents/AI-ENTRYPOINTS.md`.

When those concrete details change, update `.agents/AI-ENTRYPOINTS.md` instead of rewriting this rule contract.

## Required Admission Rules

Before any non-trivial task, every AI agent must:

1. Read `.agents/AI-ENTRYPOINTS.md`.
2. Confirm the active workspace named by `.agents/AI-ENTRYPOINTS.md`.
3. Treat the active workspace as independent from any external workspace unless the user explicitly asks to port, sync, compare, or migrate specific work.
4. Read the active rule and memory sources listed in `.agents/AI-ENTRYPOINTS.md`.
5. Select the task flow intensity from the listed task-flow source.
6. Apply the listed file safety guard before file-changing shell commands when target paths are known.
7. Keep project-visible state in the listed public project locations, not runtime-private directories.

## Mandatory Rule Sources

Use the active rule and memory sources listed in `.agents/AI-ENTRYPOINTS.md`.

Runtime entry files are entry pointers. They do not override the active rule and memory sources.

## Runtime Adapter Requirement

When a runtime supports project entry files, point it to one of the entry files listed in `.agents/AI-ENTRYPOINTS.md`.

When a runtime supports hooks, guards, policies, or tool interception, configure it to use the hook source or closest adapter listed in `.agents/AI-ENTRYPOINTS.md`.

When a runtime does not support hooks, this onboarding contract and the active rule sources remain mandatory. In that case the runtime must enforce the same constraints through its prompt, session rules, or manual preflight checks.

## State Isolation Requirement

Runtime-private directories may contain only runtime internals such as logs, transcripts, caches, or local continuation data.

No AI agent may write project source-of-truth rules, shared memory, task state, checkpoints, or handoff notes to runtime-private paths.

Use the public project locations listed in `.agents/AI-ENTRYPOINTS.md` instead.

## File Safety Requirement

Before any shell command or script that creates, edits, moves, deletes, formats, or syncs files, run the listed local path guard when target paths are known.

For patch-based edits, inspect the patch targets and ensure every target is inside the active workspace.

## If Rules Conflict

Use this authority order:

1. Explicit latest user instruction in the current conversation.
2. This onboarding contract.
3. The workspace entry source listed in `.agents/AI-ENTRYPOINTS.md`.
4. The rule sources listed in `.agents/AI-ENTRYPOINTS.md`.
5. The shared memory source and linked memory files listed in `.agents/AI-ENTRYPOINTS.md`.
6. Runtime entry pointers and adapters.

Historical memory and reference material should remain faithful to the original wording unless the user explicitly asks to edit that record.
