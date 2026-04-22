# Task Flow Matrix

This document defines the shared task types and their mandatory gate order.

## Global Rules

These rules apply to every task flow:

- every new task must be assigned a `task type`
- every new task must start with `plan`
- a gate must be marked complete before the next gate begins
- if a gate is blocked, stay in that gate, `rewind`, or re-enter `plan`
- if the task changes type, stop and choose a new flow through `plan`
- subagents inherit a scoped task type and gate; they do not get to skip gates

## Shared Task Record

Every active task should track:

- `task type`
- `current gate`
- `completed gates`
- `next gate`
- `blocked on`

## Flow Types

### `analysis`

Use for:

- research
- comparison
- synthesis
- theory building
- decision support

Gate order:

1. `intake`
2. `plan`
3. `evidence`
4. `synthesis`
5. `review`
6. `delivery`

Completion standard:

- `evidence` is complete only when the conclusion has enough supporting material
- `synthesis` is complete only when the answer is organized and decision-ready
- `review` is complete only when weak claims and missing evidence are called out

### `doc-change`

Use for:

- rule edits
- README updates
- template changes
- workflow documentation changes

Gate order:

1. `intake`
2. `plan`
3. `target-inspection`
4. `edit`
5. `self-review`
6. `validation`
7. `delivery`

Completion standard:

- `target-inspection` is complete only when the affected files and current wording are known
- `edit` is complete only when the intended text changes are applied
- `self-review` is complete only when wording conflicts and scope drift are checked
- `validation` is complete only when local checks for the affected assets have run, when available

### `implementation`

Use for:

- code changes
- script changes
- content generation that produces working artifacts
- execution-heavy production work

Gate order:

1. `intake`
2. `plan`
3. `context-inspection`
4. `implementation`
5. `validation`
6. `review`
7. `delivery`

Completion standard:

- `context-inspection` is complete only when the relevant files and constraints are understood
- `implementation` is complete only when the scoped change is applied
- `validation` is complete only when tests, smoke checks, or equivalent verification run where feasible
- `review` is complete only when major risks, regressions, and missing checks are surfaced

### `review`

Use for:

- code review
- document review
- QA pass
- scoring
- verification-only work

Gate order:

1. `intake`
2. `plan`
3. `target-inspection`
4. `findings`
5. `cross-check`
6. `delivery`

Completion standard:

- `target-inspection` is complete only when the thing being reviewed is fully identified
- `findings` is complete only when concrete issues or a no-findings result is produced
- `cross-check` is complete only when findings are tied back to evidence

### `collection`

Use for:

- product collection
- structured imports
- batch normalization
- schema-driven gathering work

Gate order:

1. `intake`
2. `plan`
3. `schema-check`
4. `collection`
5. `normalization`
6. `validation`
7. `delivery`

Completion standard:

- `schema-check` is complete only when the target fields and format are fixed
- `collection` is complete only when the source data is gathered
- `normalization` is complete only when the data is mapped into the target structure
- `validation` is complete only when obvious gaps, duplicates, and format errors are checked

## Scope Change Rule

When the task changes materially, do not keep pushing through the old flow.

Instead:

1. stop
2. re-enter `plan`
3. decide whether the same task type still applies
4. if not, switch to the new flow and restart at the correct gate
