# Task Flow Matrix

This document defines the shared task types and their mandatory gate order.

## Global Rules

These rules apply to every task flow:

- every new task should first be classified by flow intensity: `quick`, `standard`, or `strict`
- `quick` tasks can be answered or executed directly when they are low-risk and do not need staged work
- `standard` and `strict` tasks must be assigned a `task type`
- `standard` and `strict` tasks must start with `plan`
- a gate must be marked complete before the next gate begins
- if a gate is blocked, stay in that gate, `rewind`, or re-enter `plan`
- if the task changes type, stop and choose a new flow through `plan`
- subagents inherit a scoped task type and gate; they do not get to skip gates

## Shared Task Record

Every active task should track:

- `flow intensity`
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

### `knowledge-asset`

Use for:

- standards (`标准` / `规范`)
- libraries / knowledge bases (`库`)
- methodologies (`方法论`)
- long-term workflows (`流程` / `体系` / `框架`)
- any artifact meant to evolve and be reused across sessions

This flow exists because `doc-change` does not force the agent to reason about main data, lifecycle, and integration before writing. Misclassifying a long-term asset as `doc-change` is the canonical failure this flow prevents.

Gate order:

1. `intake`
2. `plan`
3. `governance-design`
4. `target-inspection`
5. `edit`
6. `validation`
7. `delivery`

Completion standard:

- `governance-design` is complete only when all 5 governance fields below resolve to concrete paths or lists, not yes/no or abstract principles
- `target-inspection` is complete only when the existing assets named in `governance-design` field 4 have actually been read
- `edit` is complete only when the scoped change is applied
- `validation` is complete only when references in memory, README, and related rules are checked for consistency

#### Governance Design Checklist

The `governance-design` gate must produce these 5 fields. Each answer must be a file path, file list, or directory path. Yes/no answers, abstract principles, or "should consider..." phrasing fail this gate.

| # | Field | Acceptance form |
|---|---|---|
| 1 | Long-term reuse impact | List affected paths under `archive/`, `reference/`, `archive/skills/`, `archive/tools/`. If none, declare `无,产物只落 workspace/` |
| 2 | Rules / directory structure / Skills / automation scripts touched | List specific paths (`.claude/rules/*.md`, `SKILL.md`, `*.py`, directory paths). If none, declare so explicitly |
| 3 | Memory / archive / reference writes | Name target directory(s) and trigger timing: `write immediately` / `write on task completion` / `no write`. If write, name the target file path |
| 4 | Existing same-kind assets scanned | List paths already read (e.g. `archive/资料/买量组合库/README.md`, `reference/部门标准/立项/`). Empty list means this gate is not complete |
| 5 | Main data ownership | Name the single source of truth file path. Describe how derived files refresh when main data changes |

Any field that cannot point to a path or list fails this gate. Do not advance to `target-inspection` until all 5 fields are concrete.

## Scope Change Rule

When the task changes materially, do not keep pushing through the old flow.

Instead:

1. stop
2. re-enter `plan`
3. decide whether the same task type still applies
4. if not, switch to the new flow and restart at the correct gate

### Misclassification Rewind Rule

Classification errors must rewind to the classification gate. Do not patch the current execution gate to make the artifact look compliant.

Triggers (any one):

- the user flags that the abstract task level was identified incorrectly
- the produced artifact is missing any of: main data ownership, lifecycle, integration relations
- the task actually produces long-term assets but is running under `doc-change` or `implementation`

When triggered:

1. stop the current gate immediately
2. any artifact already produced is downgraded to `draft` and does not count toward gate completion
3. return to `intake`, re-classify, re-`plan`
4. do not continue patching the current gate to retro-fit governance fields onto an artifact that was built without them
