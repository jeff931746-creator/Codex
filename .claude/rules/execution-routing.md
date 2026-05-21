# Execution Routing

Use this rule when deciding how to move after the mandatory `plan` step.

- every new task starts with `plan`, even when the task is small
- classify the task before execution: `analysis`, `doc-change`, `implementation`, `review`, or `collection`
- select the matching flow before doing any execution work
- do not enter the next gate until the current gate is marked complete
- keep trivial-task plans short rather than skipping them
- `continue` only after the current `plan` has been approved
- `subagent` when the task is read-heavy, noisy, review-oriented, or only needs a concise conclusion in the main context.
- `hook` means `condition -> action`; use it to enforce routing and safety behavior rather than as a separate runtime layer.

Hook trigger table is maintained in `plan-and-hook-model.md` (authoritative). Do not duplicate here.

Reference:

- [`./plan-and-hook-model.md`](/Users/mt/Documents/Codex/.claude/rules/plan-and-hook-model.md)
- [`./task-flow-matrix.md`](/Users/mt/Documents/Codex/.claude/rules/task-flow-matrix.md)
