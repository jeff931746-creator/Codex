# Agent-Neutral Memory

This directory is the project-level memory source for `/Users/mt/Documents/Codex-codex-work`.

## Authority

- `.agents/memory/` is the shared project memory location.
- `MEMORY.md` and linked files are migrated source records. Preserve their original wording and logic unless the user explicitly asks to edit a memory entry.
- `PROJECT.md` and `.agents/rules/` define current operating rules. Memory can explain history, decisions, and task state, but it does not override current rules.
- Runtime-specific memory stores are caches or execution aids only; they are not the project source of truth.
- No runtime may write project memory, rules, task state, checkpoints, or handoff notes into its private runtime directory. Use this directory for durable shared memory.

## Use

Before non-trivial work, inspect `.agents/memory/MEMORY.md` for relevant entries, then open only the linked files needed for the task.

When preserving state through compact, clear, resume, or handoff, write to the current runtime's required mechanism if necessary, but keep durable project memory here when the user asks for memory to be updated or when project rules require a public handoff.

## Migration Note

This directory was migrated from a runtime-specific memory store on 2026-06-30.

Migration policy:

- Preserve memory entry bodies as source records.
- Do not mechanically rewrite old paths, runtime names, or historical implementation details inside memory bodies.
- Put public-management rules in this README, `PROJECT.md`, and `.agents/rules/`.
- If an old index line conflicts with current project rules, prefer current project rules and update the index only after explicit review.

## Hygiene

- Keep `MEMORY.md` as an index, not a dumping ground.
- Move completed or stale task states into `archived/`.
- Do not store debugging noise, failed attempts, scratch output, secrets, or repeated explanations.
- If a memory entry becomes a rule, move the rule to `.agents/rules/` and leave only a pointer here.
