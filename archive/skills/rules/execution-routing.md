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

Typical hook mappings:

- context `>60%` and same task continues -> `compact`
- context `>80%` or too many failed branches -> `clear`
- repeated failure or goal drift -> `rewind`
- read-heavy, noisy, or verification work -> `subagent`
- new task or major scope change -> `plan`
- shared-asset change after `plan` approval -> local validation + Git review before rollout

Reference:

- [`../references/plan-and-hook-model.md`](/Users/mt/Documents/Codex/tools/codex-skills-repo/references/plan-and-hook-model.md)
- [`../references/task-flow-matrix.md`](/Users/mt/Documents/Codex/tools/codex-skills-repo/references/task-flow-matrix.md)
