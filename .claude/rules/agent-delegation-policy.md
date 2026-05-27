# Agent Delegation Policy

This document defines the detailed ownership split between the main agent and subagents.

Use it together with:

- [`plan-and-hook-model.md`](/Users/mt/Documents/Codex/.claude/rules/plan-and-hook-model.md)
- [`task-flow-matrix.md`](/Users/mt/Documents/Codex/.claude/rules/task-flow-matrix.md)

## Core Principle

The main agent owns task control.

Subagents own bounded work only.

In short:

- main agent controls `plan`, flow, gates, and final delivery
- subagents perform scoped analysis, execution, verification, or review

## Hard Ownership Rules

### Main Agent Owns

- task-level formal `plan`
- task classification
- current gate and next gate decisions
- whether a gate is complete
- whether the task must `rewind`, `compact`, `clear`, or re-`plan`
- user-facing approval requests
- final integrated answer
- final decision to switch from one flow type to another

### Subagent Owns

- a bounded scoped question
- a bounded scoped write or read task
- evidence gathering
- isolated review or verification
- isolated comparison, extraction, normalization, or scoring
- a local subtask summary

### Subagent Must Not Own

- the task-level formal `plan`
- gate transition approval
- the final declaration that the whole task is complete
- scope changes for the parent task
- direct replacement of the main agent's user-facing conclusion
- review criteria definition — a subagent performing a `findings` gate must never define its own review dimensions; the applicable standard must be located by the main agent and passed explicitly in the prompt

Subagents may propose a local sub-plan, but it is only advisory until the main agent adopts it.

## Review Delegation Requirements

These rules apply whenever the main agent delegates a `findings` gate to a subagent.

Before writing the subagent prompt, the main agent must:

1. Complete `standard-check`: locate the applicable standard in `reference/部门标准/` (check both the current worktree path and the main repo path `/Users/mt/Documents/Codex/reference/`)
2. Confirm the standard with the user or proceed only if the standard is unambiguous
3. Include the standard content or its exact file path in the subagent prompt
4. Instruct the subagent explicitly to apply the provided standard — not to define its own criteria

A subagent prompt for `findings` that does not include a confirmed standard is invalid. The main agent must not send it.

If no standard exists:

- The main agent must stop at `standard-check` gate
- Report the gap to the user: "需要 [X] 能力的审核标准，当前 `reference/部门标准/` 下暂无，是否建立？"
- Do not proceed to `target-inspection` or `findings` until the user provides explicit direction

## Mandatory Delegation Triggers

The main agent should delegate when any of the following is true:

- three or more files need to be read without editing
- two or more templates, samples, or competing structures need comparison
- the step will generate long intermediate reasoning that the main thread does not need to keep
- the step is verification, review, scoring, or consistency checking
- the step can be parallelized into independent bounded questions
- the step is repetitive extraction, collection, normalization, or schema mapping
- the main thread already has enough context to synthesize, but not enough room to also keep all exploration detail
- the current gate is one where evidence, inspection, or cross-checking is the main work

## 委派约束

与 Mandatory Delegation Triggers 配套：前者说"何时必须委派"，后者说"委派时的禁止行为"。

### 套娃禁止

委托前先问：**我对这个问题有结论了吗？**

- 有结论 → 本地完成，不委托
- 无结论 → 给子 agent 开放问题，prompt 里不预埋方向、不列"重点检查 X"

"主 agent 有结论 + 委托子 agent 验证" = 套娃，无条件禁止。

### 设计文档审核

**主 agent 本轮写过或改过的设计文档**，审核必须走子 agent。

豁免：clear 后 / 全新 session 且本轮未参与写作或修改（无先验上下文，与子 agent 起点相同）。

## Main Agent Should Usually Stay Local When

- presenting the formal `plan`
- asking for user approval
- deciding task type
- deciding whether a gate is complete
- synthesizing already-collected evidence into a final answer
- closing the current flow and opening a new flow
- making a small local fix whose context cost is trivial

## Gate-Level Delegation Guidance

### `analysis`

Recommended owner by gate:

1. `intake` -> main agent
2. `plan` -> main agent
3. `evidence` -> subagent preferred; mandatory if the step is read-heavy or multi-source
4. `synthesis` -> main agent
5. `review` -> subagent preferred
6. `delivery` -> main agent

### `doc-change`

Recommended owner by gate:

1. `intake` -> main agent
2. `plan` -> main agent
3. `target-inspection` -> subagent preferred; mandatory if many files or standards must be inspected
4. `edit` -> main agent by default, or worker subagent if the write scope is clearly bounded
5. `self-review` -> subagent preferred
6. `validation` -> subagent or local deterministic checks
7. `delivery` -> main agent

### `implementation`

Recommended owner by gate:

1. `intake` -> main agent
2. `plan` -> main agent
3. `context-inspection` -> subagent preferred
4. `implementation` -> main agent or worker subagent with clear ownership
5. `validation` -> subagent or local deterministic checks
6. `review` -> subagent preferred
7. `delivery` -> main agent

### `review`

Recommended owner by gate:

1. `intake` -> main agent
2. `plan` -> main agent
3. `target-inspection` -> subagent preferred
4. `findings` -> reviewer subagent preferred
5. `cross-check` -> subagent or main agent, depending on conflict complexity
6. `delivery` -> main agent

### `collection`

Recommended owner by gate:

1. `intake` -> main agent
2. `plan` -> main agent
3. `schema-check` -> main agent
4. `collection` -> subagent preferred
5. `normalization` -> subagent preferred
6. `validation` -> subagent preferred
7. `delivery` -> main agent

## Context Budget Rules

The main thread should keep only:

- task type
- current gate
- completed gates
- next gate
- approved plan
- confirmed conclusions
- user-visible risks and options

The main thread should avoid keeping:

- long exploratory notes
- raw file-by-file reading logs
- repeated speculative branches
- large comparison tables unless the final answer truly needs them
- verbose subagent work process

If a step would create that kind of noise, delegate it.

## Subagent Output Contract

Every subagent task should specify:

- the exact question
- the relevant files or scope
- the task type
- the current gate
- the desired output format
- the maximum summary length, unless structured output is better

### Standard-First Rule for review and doc-change

When the subagent task type is `review` or `doc-change`, the prompt must include an explicit instruction to read the relevant standard files before executing. Specifically:

- the prompt must name the standard paths to read: both the worktree path and the main repo path (`/Users/mt/Documents/Codex/reference/部门标准/`)
- the subagent must read and confirm the standard before applying any evaluation criteria
- self-defined evaluation dimensions are not allowed unless the subagent has confirmed no relevant standard exists in either location
- if no standard exists, the subagent must state this explicitly and halt, not substitute a self-defined framework

Preferred return formats:

- summary <= 300 tokens
- bullet findings
- compact table
- structured JSON when post-processing matters

The subagent should return conclusions, not a full diary of its process.

## Formal Plan Rule

The task-level formal `plan` must come from the main agent.

This means:

- the main agent may consult subagents before writing the plan
- the main agent may include subagent findings in the plan
- the user should approve the main agent's plan, not a subagent's raw output

If a subagent proposes a better route, the main agent should restate it as the official plan before execution continues.

## Gate Transition Rule

Only the main agent can declare:

- `current gate complete`
- `move to next gate`
- `task type changed`
- `re-enter plan`

A subagent can report that its scoped work is complete, but that is not the same as approving the parent task's next gate.

## Conflict And Retry Handling

If a subagent result is insufficient:

1. keep the parent task in the same gate
2. either re-delegate with a narrower question or resolve locally
3. do not advance the gate until the missing requirement is satisfied

If multiple subagents disagree:

1. do not let either result become the final answer directly
2. the main agent compares the evidence
3. if needed, run a focused follow-up delegation
4. the main agent then publishes the integrated result

## Recommended Short Rule

Use this wording when you need the policy in one paragraph:

`Main agent owns the formal plan, task type, gate transitions, and final delivery. Subagents handle bounded heavy work such as evidence gathering, comparison, review, and verification. Delegate when analysis would create noise or context bloat; keep synthesis, approval, and final gate decisions in the main agent.`
